"""Modules: shared settings, one TOML file per module in `modules/` (S01)."""

import tomllib
from pathlib import Path

from rosamta.errors import ConfigError


def load_modules(config: Path) -> dict[str, dict]:
    folder = config / "modules"
    if not folder.is_dir():
        raise ConfigError(f"{folder}: modules folder not found")
    modules = {}
    for path in sorted(folder.glob("*.toml")):
        try:
            modules[path.stem] = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as err:
            raise ConfigError(f"{path}: {err}") from None
    return modules


def get_value(modules: dict[str, dict], key: str):
    """Look up a dotted key such as `theme.colors.background`."""
    parts = key.split(".")
    value = modules
    for depth, part in enumerate(parts):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(".".join(parts[: depth + 1]))
        value = value[part]
    return value
