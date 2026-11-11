"""Checks that run before anything is written (S10)."""

import os
import shutil
from pathlib import Path

from rosamta.planner import REMOVE, WRITE, Plan
from rosamta.state import StateRecord


def _writable(path: Path) -> bool:
    folder = path.parent
    while not folder.exists():
        folder = folder.parent
    return folder.is_dir() and os.access(folder, os.W_OK | os.X_OK)


def check(plan: Plan) -> tuple[list[tuple[Path, str]], list[str]]:
    """Return (problems, warnings). Any problem stops apply before it writes.

    Each problem is (path of the output that cannot be written, message).
    """
    problems, warnings = [], []
    for change in plan.changes:
        if change.action in (WRITE, REMOVE) and not _writable(change.path):
            problems.append((change.path, f"{change.output}: cannot write to {change.path.parent}"))
        for program in change.requires:
            if shutil.which(program) is None:
                warnings.append(f"{change.output}: needs {program}, which is not installed (rosamta will not install it)")
    # Apply records what it wrote at the end; check now so it never writes outputs it cannot record.
    # An existing state.json is rewritten in place, so only a new one needs a writable folder.
    state_file = StateRecord.file()
    if state_file.exists():
        if not os.access(state_file, os.W_OK):
            problems.append((state_file, f"state record: cannot write to {state_file}"))
    elif not _writable(state_file):
        problems.append((state_file, f"state record: cannot write to {state_file.parent}"))
    return problems, warnings
