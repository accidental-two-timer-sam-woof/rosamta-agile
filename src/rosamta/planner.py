"""Build the plan: what apply would do with every output on this machine (S07, S09, S13, S15, S23)."""

from dataclasses import dataclass, field
from pathlib import Path

from rosamta import local, manifest, paths, profiles
from rosamta.module import load_modules
from rosamta.state import StateRecord, digest
from rosamta.templates import find_template

WRITE, UNCHANGED, SKIP, REMOVE, KEEP = "write", "unchanged", "skip", "remove", "keep"


@dataclass
class Change:
    output: str
    path: Path
    action: str
    reason: str = ""
    content: str | None = None
    take_over: bool = False      # back up the existing file first (S23)
    requires: list[str] = field(default_factory=list)
    enabled_by: list[str] = field(default_factory=list)

    def old_content(self) -> str:
        return self.path.read_text(encoding="utf-8") if self.path.is_file() else ""


@dataclass
class Plan:
    changes: list[Change]
    messages: list[str]
    settings: local.LocalSettings

    @property
    def skipped(self) -> bool:
        return any(c.action in (SKIP, KEEP) for c in self.changes)


def build_plan(config: Path, overwrite: list[str] | None = None) -> Plan:
    overwrite = overwrite or []
    settings = local.load()
    machine = profiles.Machine(paths.current_os(), settings.host_id, settings.tags)
    modules = load_modules(config)
    outputs = manifest.load_manifest(config)
    manifest.validate(outputs, machine.os, config / "manifest.toml")
    selection = profiles.select_outputs(config, machine, [o.name for o in outputs])
    state = StateRecord.load()

    messages = []
    if not selection.matched:
        messages.append("no profile matched this machine; using the default profile only")
    changes = []
    planned_paths = set()
    for output in outputs:
        if output.name not in selection.enabled:
            continue
        target = output.target_for(machine.os)
        if target is None:
            messages.append(f"{output.name}: not available on {machine.os}")
            continue
        planned_paths.add(str(target))
        content = find_template(config, output.template).render(modules)
        change = Change(output.name, target, WRITE, content=content, requires=output.requires,
                        enabled_by=selection.enabled[output.name])
        if target.is_file():
            current = target.read_bytes()
            if current == content.encode("utf-8"):
                change.action = UNCHANGED
            elif state.is_drifted(target):
                if output.name in overwrite:
                    change.reason = "drifted, overwritten on request"
                else:
                    change.action, change.reason = SKIP, "edited by hand since the last apply (drift)"
            elif not state.wrote(target):
                if output.take_over:
                    change.take_over, change.reason = True, "existing file is backed up first"
                else:
                    change.action, change.reason = SKIP, "file exists and the manifest does not allow taking it over"
        changes.append(change)

    for path_text, written_hash in state.entries.items():
        if path_text in planned_paths:
            continue
        path = Path(path_text)
        if not path.is_file():
            continue
        if digest(path.read_bytes()) == written_hash:
            changes.append(Change("(old output)", path, REMOVE, "no longer enabled"))
        else:
            changes.append(Change("(old output)", path, KEEP, "no longer enabled, but edited by hand"))
    return Plan(changes, messages, settings)
