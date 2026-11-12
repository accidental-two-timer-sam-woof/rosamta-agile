"""Modules: shared settings, one TOML file per module in `modules/` (S01)."""

import fnmatch
import tomllib
from pathlib import Path

from rosamta import paths
from rosamta.errors import ConfigError


def load_modules(config: Path) -> dict[str, dict]:
    folder = config / "modules"
    try:
        entries = paths.list_folder(folder)
    except (FileNotFoundError, NotADirectoryError):
        raise ConfigError(f"{folder}: modules folder not found; create it with one .toml file per module", folder) from None
    modules = {}
    for path in entries:
        if not fnmatch.fnmatch(path.name, "*.toml"):
            continue
        try:
            modules[path.stem] = tomllib.loads(paths.read_text(path))
        except tomllib.TOMLDecodeError as err:
            raise ConfigError(f"{path}: {err}", path) from None
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
