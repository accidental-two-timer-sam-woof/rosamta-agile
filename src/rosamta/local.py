"""This machine's own settings, kept outside the shared config folder (S08, S18).

~/.config/rosamta/local.toml:

    host_id = "work-laptop"
    tags = ["gui"]
    config_folder = "/Users/me/dotfiles"
"""

import os
import socket
import stat
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from rosamta import paths
from rosamta.errors import ConfigError, RosamtaError


@dataclass
class LocalSettings:
    host_id: str
    tags: list[str] = field(default_factory=list)
    config_folder: str | None = None
    host_id_saved: bool = False


def settings_file() -> Path:
    return paths.config_dir() / "local.toml"


def default_host_id() -> str:
    """A Host ID is chosen once from the hostname and then stays fixed (S07 change request)."""
    name = socket.gethostname().split(".")[0].lower()
    return name or "host"


def load() -> LocalSettings:
    path = settings_file()
    try:
        # Check the file that was opened, not the path: reading a FIFO would block, and rosamta must never hang (S19).
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise RosamtaError(f"{paths.display(path)} is not a regular file; replace it with a file, "
                                   "or set XDG_CONFIG_HOME to another folder", path)
            with open(fd, encoding="utf-8", closefd=False) as file:
                text = file.read()
        finally:
            os.close(fd)
    except FileNotFoundError:
        return LocalSettings(default_host_id())
    except UnicodeDecodeError:
        raise ConfigError(f"{paths.display(path)}: not UTF-8 text; save it with UTF-8 encoding", path) from None
    except OSError as err:
        raise RosamtaError(f"cannot read {paths.display(path)} ({err.strerror or err}); make it readable and "
                           f"{paths.display(path.parent)} readable and searchable, "
                           "or set XDG_CONFIG_HOME to another folder", path) from None
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as err:
        raise ConfigError(f"{path}: {err}", path) from None
    saved = data.get("host_id")
    return LocalSettings(saved or default_host_id(),
                         list(data.get("tags", [])), data.get("config_folder"), bool(saved))


def _quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def save(settings: LocalSettings) -> None:
    path = settings_file()
    lines = [f"host_id = {_quote(settings.host_id)}",
             "tags = [" + ", ".join(_quote(t) for t in settings.tags) + "]"]
    if settings.config_folder:
        lines.append(f"config_folder = {_quote(settings.config_folder)}")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as err:
        raise RosamtaError(f"cannot write {paths.display(path)} ({err.strerror or err}); make "
                           f"{paths.display(path.parent)} writable, or set XDG_CONFIG_HOME to a writable folder",
                           path) from None
