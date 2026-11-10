"""What rosamta last wrote, so it can tell when a user edited a file (S13, S15).

Only a hash of each file is stored, never its content, because outputs may contain secrets.
"""

import hashlib
import json
from pathlib import Path

from rosamta import paths


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
        if path.is_file():
            return cls(json.loads(path.read_text(encoding="utf-8")).get("written", {}))
        return cls()

    def save(self) -> None:
        path = self.file()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"written": self.entries}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def wrote(self, path: Path) -> bool:
        return str(path) in self.entries

    def is_drifted(self, path: Path) -> bool:
        """True when rosamta wrote this file and it changed since."""
        if not self.wrote(path) or not path.is_file():
            return False
        return digest(path.read_bytes()) != self.entries[str(path)]
