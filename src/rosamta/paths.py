"""Where rosamta keeps its own files, and platform helpers."""

import os
import sys
from pathlib import Path


def home() -> Path:
    return Path.home()


def current_os() -> str:
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("win"):
        return "windows"
    return "linux"


def config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME")
    return (Path(base) if base else home() / ".config") / "rosamta"


def state_dir() -> Path:
    base = os.environ.get("XDG_STATE_HOME")
    return (Path(base) if base else home() / ".local" / "state") / "rosamta"


def expand(path: str) -> Path:
    if path.startswith("~/") or path == "~":
        return home() / path[2:]
    return Path(path)


def is_inside_home(path: Path) -> bool:
    try:
        path.resolve().relative_to(home().resolve())
        return True
    except ValueError:
        return False


def display(path: Path) -> str:
    try:
        return "~/" + str(path.relative_to(home()))
    except ValueError:
        return str(path)
