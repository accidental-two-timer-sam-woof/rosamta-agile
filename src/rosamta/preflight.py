"""Checks that run before anything is written (S10)."""

import os
import shutil
from pathlib import Path

from rosamta.planner import REMOVE, WRITE, Plan


def _writable(path: Path) -> bool:
    folder = path.parent
    while not folder.exists():
        folder = folder.parent
    return folder.is_dir() and os.access(folder, os.W_OK)


def check(plan: Plan) -> tuple[list[str], list[str]]:
    """Return (problems, warnings). Any problem stops apply before it writes."""
    problems, warnings = [], []
    for change in plan.changes:
        if change.action in (WRITE, REMOVE) and not _writable(change.path):
            problems.append(f"{change.output}: cannot write to {change.path.parent}")
        for program in change.requires:
            if shutil.which(program) is None:
                warnings.append(f"{change.output}: needs {program}, which is not installed (rosamta will not install it)")
    return problems, warnings
