"""This machine's own settings, kept outside the shared config folder (S08, S18).

~/.config/rosamta/local.toml:

    host_id = "work-laptop"
    tags = ["gui"]
    config_folder = "/Users/me/dotfiles"
"""

import socket
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from rosamta import paths
from rosamta.errors import ConfigError


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
    if not path.is_file():
        return LocalSettings(default_host_id())
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as err:
        raise ConfigError(f"{path}: {err}") from None
    saved = data.get("host_id")
    return LocalSettings(saved or default_host_id(),
                         list(data.get("tags", [])), data.get("config_folder"), bool(saved))


def _quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def save(settings: LocalSettings) -> None:
    path = settings_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"host_id = {_quote(settings.host_id)}",
             "tags = [" + ", ".join(_quote(t) for t in settings.tags) + "]"]
    if settings.config_folder:
        lines.append(f"config_folder = {_quote(settings.config_folder)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
