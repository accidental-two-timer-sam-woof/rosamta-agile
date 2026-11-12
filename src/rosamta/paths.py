"""Where rosamta keeps its own files, and platform helpers."""

import contextlib
import os
import stat
import sys
from pathlib import Path

from rosamta.errors import ConfigError, RosamtaError


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


class NotAFolderError(RosamtaError):
    """A file sits where a folder should be. Windows reports this as a missing file instead."""


def _cannot_read(path: Path, err: OSError) -> RosamtaError:
    return RosamtaError(f"cannot read {display(path)} ({err.strerror or err}); "
                        "make it readable and its folder readable and searchable", path)


def _not_a_folder(path: Path) -> NotAFolderError:
    blocker = path.parent
    try:
        blocker = next(p for p in [*reversed(path.parents), path] if p.is_file())
    except (StopIteration, OSError):
        pass
    return NotAFolderError(f"cannot read {display(path)}: {display(blocker)} is a file, not a folder; "
                           "replace it with a folder", blocker)


@contextlib.contextmanager
def _open_regular_file(path: Path):
    """Open without blocking and check what was opened, so a FIFO can never hang rosamta (S19).

    A missing file raises FileNotFoundError, and a file where one of its folders should be NotAFolderError.
    Every other problem becomes a rosamta error naming the file (S22).
    """
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
    except FileNotFoundError:
        raise
    except NotADirectoryError:
        raise _not_a_folder(path) from None
    except OSError as err:
        raise _cannot_read(path, err) from None
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise RosamtaError(f"{display(path)} is not a regular file; replace it with a file", path)
        yield fd
    except OSError as err:
        raise _cannot_read(path, err) from None
    finally:
        os.close(fd)


def list_folder(folder: Path) -> list[Path]:
    """The folder's entries, sorted. A missing folder raises FileNotFoundError, a file in its place NotAFolderError.

    Path.glob skips a folder it cannot list without a word, so a locked folder would look empty (S22).
    """
    try:
        return sorted(folder.iterdir())
    except FileNotFoundError:
        raise
    except NotADirectoryError:
        raise _not_a_folder(folder) from None
    except OSError as err:
        raise RosamtaError(f"cannot read {display(folder)} ({err.strerror or err}); "
                           "make it readable and searchable, and its parent folders searchable", folder) from None


def read_bytes(path: Path) -> bytes:
    with _open_regular_file(path) as fd, open(fd, "rb", closefd=False) as file:
        return file.read()


def read_text(path: Path) -> str:
    try:
        with _open_regular_file(path) as fd, open(fd, encoding="utf-8", closefd=False) as file:
            return file.read()
    except UnicodeDecodeError:
        raise ConfigError(f"{display(path)}: not UTF-8 text; save it with UTF-8 encoding", path) from None
