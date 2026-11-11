"""Write the plan to disk, all or nothing (S11, S12, S15, S23)."""

import os
import shutil
import time
from pathlib import Path

from rosamta import paths
from rosamta.errors import RosamtaError
from rosamta.planner import REMOVE, UNCHANGED, WRITE, Plan
from rosamta.state import StateRecord, digest


class ApplyFailed(RosamtaError):
    """A write failed. Every file changed so far was restored."""


def _write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".rosamta-tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def _backup(path: Path, stamp: str) -> Path:
    target = paths.state_dir() / "backups" / stamp / path.relative_to(paths.home())
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    return target


def apply(plan: Plan) -> list[str]:
    """Apply the plan. Returns notes such as backup locations. Raises ApplyFailed after rolling back."""
    state = StateRecord.load()
    journal: list[tuple[Path, bytes | None]] = []   # (path, content before we touched it)
    notes = []
    stamp = time.strftime("%Y%m%d-%H%M%S")
    try:
        for change in plan.changes:
            if change.action == WRITE:
                before = change.path.read_bytes() if change.path.is_file() else None
                if change.take_over and before is not None:
                    notes.append(f"backed up {paths.display(change.path)} to {paths.display(_backup(change.path, stamp))}")
                journal.append((change.path, before))
                _write_atomic(change.path, change.content.encode("utf-8"))
            elif change.action == REMOVE:
                journal.append((change.path, change.path.read_bytes()))
                change.path.unlink()
    except OSError as err:
        for path, before in reversed(journal):
            if before is None:
                path.unlink(missing_ok=True)
            else:
                _write_atomic(path, before)
        raise ApplyFailed(f"{err}; rolled back {len(journal)} file(s)", file=change.path) from None

    for change in plan.changes:
        if change.action in (WRITE, UNCHANGED):
            state.entries[str(change.path)] = digest(change.path.read_bytes())
        elif change.action == REMOVE:
            state.entries.pop(str(change.path), None)
    state.save()
    return notes
