"""Command line interface.

Results go to standard output, errors and warnings to standard error (S22).
rosamta never reads from standard input, so scripts can never hang (S19).
"""

import argparse
import difflib
import json
import sys
from pathlib import Path

from rosamta import applier, local, manifest, paths, preflight
from rosamta.errors import EXIT_FAILED, EXIT_OK, EXIT_PARTIAL, ConfigError, RosamtaError, UsageError
from rosamta.module import get_value, load_modules
from rosamta.planner import KEEP, REMOVE, SKIP, UNCHANGED, WRITE, build_plan
from rosamta.query import query
from rosamta.templates import find_template

LABELS = {WRITE: "written", UNCHANGED: "unchanged", SKIP: "skipped", REMOVE: "removed", KEEP: "kept"}


def _config_folder(arg: Path | None) -> Path:
    if arg is not None:
        return arg
    settings = local.load()
    if settings.config_folder:
        return Path(settings.config_folder)
    return Path(".")


def _item(change) -> dict:
    return {"output": change.output, "path": str(change.path), "action": change.action, "reason": change.reason}


def _diff(change) -> str:
    return "".join(difflib.unified_diff(
        change.old_content().splitlines(keepends=True),
        (change.content or "").splitlines(keepends=True),
        fromfile=f"{paths.display(change.path)} (on disk)",
        tofile=f"{paths.display(change.path)} ({change.output}, generated)",
    ))


class Reporter:
    def __init__(self, as_json: bool):
        self.as_json = as_json
        self.data: dict = {"items": [], "messages": [], "warnings": []}

    def line(self, text: str = "") -> None:
        if self.as_json:
            self.data["messages"].append(text)
        else:
            print(text)

    def warn(self, text: str) -> None:
        self.data["warnings"].append(text)
        print(f"warning: {text}", file=sys.stderr)

    def finish(self, code: int) -> int:
        if self.as_json:
            self.data["exit_code"] = code
            print(json.dumps(self.data, indent=2))
        return code


def cmd_preview(config: Path, out: Reporter, overwrite: list[str]) -> int:
    plan = build_plan(config, overwrite)
    for message in plan.messages:
        out.line(message)
    changes = [c for c in plan.changes if c.action != UNCHANGED]
    out.data["items"] = [_item(c) for c in plan.changes]
    if not changes:
        out.line("Nothing to apply.")
        return EXIT_OK
    for change in changes:
        if change.action == WRITE:
            if out.as_json:
                out.data.setdefault("diffs", {})[change.output] = _diff(change)
            else:
                print(_diff(change), end="")
                if change.reason:
                    print(f"  ({change.reason})")
        elif change.action == REMOVE:
            out.line(f"will remove {paths.display(change.path)} ({change.reason})")
        else:
            out.line(f"will skip {paths.display(change.path)}: {change.reason}")
            if change.action == SKIP and change.content is not None and not out.as_json:
                print(_diff(change), end="")
    return EXIT_OK


def cmd_apply(config: Path, out: Reporter, overwrite: list[str]) -> int:
    plan = build_plan(config, overwrite)
    for message in plan.messages:
        out.line(message)
    problems, warnings = preflight.check(plan)
    for warning in warnings:
        out.warn(warning)
    if problems:
        for _, problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        out.data["error"] = {"code": EXIT_FAILED, "file": str(problems[0][0]),
                             "message": "preflight failed; nothing was written",
                             "problems": [problem for _, problem in problems]}
        return EXIT_FAILED
    if not plan.settings.host_id_saved:
        # Save the Host ID the plan used, so a later hostname change cannot pick other profiles (S07).
        local.save(plan.settings)
        out.line(f"this machine's Host ID is {plan.settings.host_id} (saved in {paths.display(local.settings_file())})")
    for note in applier.apply(plan):
        out.line(note)
    out.data["items"] = [_item(c) for c in plan.changes]
    for change in plan.changes:
        reason = f"  ({change.reason})" if change.reason else ""
        out.line(f"{LABELS[change.action]:<10} {change.output:<14} {paths.display(change.path)}{reason}")
    return EXIT_PARTIAL if plan.skipped else EXIT_OK


def cmd_init(folder: Path, tags: list[str], out: Reporter) -> int:
    folder = folder.resolve()
    try:
        # Open it rather than ask is_file(): that hides a folder rosamta cannot search (S22).
        paths.read_bytes(folder / "manifest.toml")
    except (FileNotFoundError, paths.NotAFolderError):
        raise ConfigError(f"{folder}: not a rosamta config folder (no manifest.toml)", folder / "manifest.toml") from None
    settings = local.load()
    first_time = not settings.host_id_saved
    settings.config_folder = str(folder)
    settings.tags = sorted(set(settings.tags) | set(tags))
    local.save(settings)
    if first_time:
        out.line(f"this machine's Host ID is {settings.host_id} (saved in {paths.display(local.settings_file())})")
    return cmd_apply(folder, out, [])


class _Parser(argparse.ArgumentParser):
    """Turns a wrong command line into a rosamta error, so --json still prints one document (S21)."""

    def __init__(self, *args, **kwargs):
        # No abbreviations, in the commands too: "--js" must not silently mean "--json" (S21).
        super().__init__(*args, allow_abbrev=False, **kwargs)

    def error(self, message: str):
        self.print_usage(sys.stderr)
        raise UsageError(f"{self.prog}: {message}")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = _Parser(prog="rosamta", description="One module, many dotfiles.")
    parser.add_argument("--config", type=Path, help="config folder (default: the one saved by init, else the current folder)")
    parser.add_argument("--json", action="store_true", help="print results as one JSON document (S21)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("get", help="print one module value, e.g. theme.colors.background").add_argument("key")
    commands.add_parser("render", help="print one generated output").add_argument("output")
    for name, text in (("preview", "show what apply would change, without writing"),
                       ("apply", "write every enabled output")):
        sub = commands.add_parser(name, help=text)
        sub.add_argument("--overwrite", action="append", default=[], metavar="OUTPUT",
                         help="replace this output even if it was edited by hand (S14)")
    commands.add_parser("query", help="which outputs use a module, or which modules feed an output").add_argument("name")
    init = commands.add_parser("init", help="set up this machine with a config folder, then apply")
    init.add_argument("folder", type=Path)
    init.add_argument("--tag", action="append", default=[], help="add a tag to this machine")
    # S21 is written as "rosamta apply --json", so --json also works after the command.
    # SUPPRESS keeps a command from resetting "rosamta --json apply" to False.
    for sub in commands.choices.values():
        sub.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                         help="print results as one JSON document (S21)")
    # Before parsing, guess JSON mode the way the parser will: "--json" as an option, not after "--".
    options = argv[:argv.index("--")] if "--" in argv else argv
    out = Reporter("--json" in options)
    try:
        args = parser.parse_args(argv)
        out.as_json = args.json
        if args.command == "init":
            return out.finish(cmd_init(args.folder, args.tag, out))
        config = _config_folder(args.config)
        if args.command == "get":
            modules = load_modules(config)
            try:
                out.line(str(get_value(modules, args.key)))
            except KeyError as err:
                module = args.key.split(".")[0]
                if module in modules:
                    raise ConfigError(f"key not found: {err.args[0]}; set it in modules/{module}.toml",
                                      config / "modules" / f"{module}.toml") from None
                raise ConfigError(f"key not found: {args.key}; there is no module {module} "
                                  f"(modules: {', '.join(sorted(modules)) or 'none'})", config / "modules") from None
            return out.finish(EXIT_OK)
        if args.command == "render":
            outputs = {o.name: o for o in manifest.load_manifest(config)}
            if args.output not in outputs:
                raise ConfigError(f"output {args.output}: not in the manifest; outputs: {', '.join(outputs) or 'none'}",
                                  config / "manifest.toml")
            text = find_template(config, outputs[args.output].template).render(load_modules(config))
            if args.json:
                out.data["content"] = text
            else:
                print(text, end="")
            return out.finish(EXIT_OK)
        if args.command == "query":
            for line in query(config, args.name):
                out.line(line)
            return out.finish(EXIT_OK)
        if args.command == "preview":
            return out.finish(cmd_preview(config, out, args.overwrite))
        return out.finish(cmd_apply(config, out, args.overwrite))
    except RosamtaError as err:
        print(f"error: {err}", file=sys.stderr)
        out.data["error"] = {"code": err.exit_code, "file": err.file, "message": str(err)}
        return out.finish(err.exit_code)


if __name__ == "__main__":
    sys.exit(main())
