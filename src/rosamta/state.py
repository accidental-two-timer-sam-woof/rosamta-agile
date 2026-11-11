"""What rosamta last wrote, so it can tell when a user edited a file (S13, S15).

Only a hash of each file is stored, never its content, because outputs may contain secrets.
"""

import hashlib
import json
from pathlib import Path

from rosamta import paths
from rosamta.errors import RosamtaError


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class StateRecord:
    def __init__(self, entries: dict[str, str] | None = None):
        self.entries = entries or {}   # absolute path -> sha256 of what rosamta wrote

    @staticmethod
    def file() -> Path:
        return paths.state_dir() / "state.json"

    @classmethod
    def load(cls) -> "StateRecord":
        path = cls.file()
        try:
            data = paths.read_bytes(path)
        except FileNotFoundError:
            return cls()
        try:
            written = json.loads(data).get("written", {})
        except (ValueError, AttributeError):
            written = None
        if not isinstance(written, dict):
            raise RosamtaError(f"{paths.display(path)} is damaged; delete it to start over "
                               "(rosamta then treats existing outputs as files it did not write)", path)
        return cls(written)

    def save(self) -> None:
        path = self.file()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"written": self.entries}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        except OSError as err:
            raise RosamtaError(f"cannot record what rosamta wrote in {paths.display(path)} ({err.strerror or err}); "
                               f"make it and {paths.display(path.parent)} writable, then run rosamta apply again",
                               path) from None

    def wrote(self, path: Path) -> bool:
        return str(path) in self.entries

    def is_drifted(self, path: Path) -> bool:
        """True when rosamta wrote this file and it changed since."""
        if not self.wrote(path):
            return False
        try:
            return digest(paths.read_bytes(path)) != self.entries[str(path)]
        except FileNotFoundError:
            return False
