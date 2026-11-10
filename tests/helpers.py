import contextlib
import io
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from rosamta.cli import main

EXAMPLE = Path(__file__).resolve().parent.parent / "example"


class RosamtaCase(unittest.TestCase):
    """Each test gets its own fake home directory and its own copy of the example config."""

    def setUp(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, True)
        self.home = root / "home"
        self.home.mkdir()
        env = {"HOME": str(self.home), "USERPROFILE": str(self.home)}
        for var in ("XDG_CONFIG_HOME", "XDG_STATE_HOME"):
            env[var] = ""
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
        for var in ("XDG_CONFIG_HOME", "XDG_STATE_HOME"):
            os.environ.pop(var, None)
        self.config = root / "config"
        shutil.copytree(EXAMPLE, self.config)

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["--config", str(self.config), *args])
        return code, out.getvalue(), err.getvalue()

    def edit(self, relative: str, old: str, new: str) -> None:
        path = self.config / relative
        path.write_text(path.read_text().replace(old, new))

    def write(self, relative: str, text: str) -> None:
        path = self.config / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def target(self, relative: str) -> Path:
        return self.home / relative

    def set_tags(self, *tags: str) -> None:
        local = self.home / ".config" / "rosamta" / "local.toml"
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_text('host_id = "test-host"\ntags = [' + ", ".join(f'"{t}"' for t in tags) + "]\n")
