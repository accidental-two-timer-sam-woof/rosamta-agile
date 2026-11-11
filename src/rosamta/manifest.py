"""The manifest declares every output: its template, target path per OS, and options (S05, S06)."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from rosamta import local, paths
from rosamta.errors import ConfigError
from rosamta.state import StateRecord

OS_NAMES = ("macos", "linux", "windows")


@dataclass
class Output:
    name: str
    template: str
    targets: dict[str, str]          # OS name -> path
    take_over: bool = False          # may replace a file rosamta did not write (S23)
    requires: list[str] = field(default_factory=list)  # programs this output needs (S10)

    def target_for(self, os_name: str) -> Path | None:
        target = self.targets.get(os_name)
        return paths.expand(target) if target else None


def load_manifest(config: Path) -> list[Output]:
    path = config / "manifest.toml"
    if not path.is_file():
        raise ConfigError(f"{path}: manifest not found")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as err:
        raise ConfigError(f"{path}: {err}") from None
    outputs = []
    seen = set()
    for index, entry in enumerate(data.get("output", []), start=1):
        missing = [k for k in ("name", "template", "target") if k not in entry]
        if missing:
            raise ConfigError(f"{path}: output {index} is missing {', '.join(missing)}")
        if entry["name"] in seen:
            raise ConfigError(f"{path}: output name {entry['name']} is used twice")
        seen.add(entry["name"])
        target = entry["target"]
        if isinstance(target, str):
            targets = {os_name: target for os_name in OS_NAMES}
        elif isinstance(target, dict):
            unknown = set(target) - set(OS_NAMES)
            if unknown:
                raise ConfigError(f"{path}: output {entry['name']} has unknown OS {', '.join(sorted(unknown))}")
            targets = dict(target)
        else:
            raise ConfigError(f"{path}: output {entry['name']} target must be a path or a table per OS")
        outputs.append(Output(entry["name"], entry["template"], targets,
                              bool(entry.get("take_over", False)), list(entry.get("requires", []))))
    return outputs


def validate(outputs: list[Output], os_name: str) -> None:
    """Reject targets outside home, targets on rosamta's own files, and two outputs writing the same file (S06)."""
    owners: dict[Path, str] = {}
    own_files = {local.settings_file().resolve(), StateRecord.file().resolve()}
    for output in outputs:
        target = output.target_for(os_name)
        if target is None:
            continue
        if not paths.is_inside_home(target):
            raise ConfigError(f"output {output.name}: target {target} is outside the home directory")
        key = target.resolve()
        if key in own_files:
            raise ConfigError(f"output {output.name}: target {paths.display(target)} is one of rosamta's own files")
        if key in owners:
            raise ConfigError(f"outputs {owners[key]} and {output.name} both write {paths.display(target)}")
        owners[key] = output.name
