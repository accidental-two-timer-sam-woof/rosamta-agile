"""S18 Init, S19 No prompts, S20 Exit codes, S21 JSON, S22 Actionable errors."""

import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

from helpers import RosamtaCase
from rosamta.cli import main

SRC = Path(__file__).resolve().parent.parent / "src"


class InitTest(RosamtaCase):
    def init(self, *extra):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["init", str(self.config), *extra])
        return code, out.getvalue(), err.getvalue()

    def test_init_records_folder_and_applies(self):
        code, out, _ = self.init("--tag", "gui")
        self.assertEqual(code, 0)
        self.assertIn("Host ID", out)
        local = (self.home / ".config/rosamta/local.toml").read_text()
        self.assertIn(str(self.config.resolve()), local)
        self.assertIn('"gui"', local)
        self.assertTrue(self.target(".config/rosamta/shellrc.bash").exists())

    def test_second_init_keeps_local_settings(self):
        self.init("--tag", "gui")
        code, _, _ = self.init()
        self.assertEqual(code, 0)
        self.assertIn('"gui"', (self.home / ".config/rosamta/local.toml").read_text())

    def test_host_id_stays_fixed_when_hostname_changes(self):
        with mock.patch("socket.gethostname", return_value="my-laptop.local"):
            self.init()
        with mock.patch("socket.gethostname", return_value="my-laptop-2.local"):
            code, _, _ = self.init()
        self.assertEqual(code, 0)
        self.assertIn('host_id = "my-laptop"', (self.home / ".config/rosamta/local.toml").read_text())

    def test_init_rejects_a_folder_without_manifest(self):
        (self.config / "manifest.toml").unlink()
        code, _, err = self.init()
        self.assertEqual(code, 3)
        self.assertIn("no manifest.toml", err)


class AutomationTest(RosamtaCase):
    def test_never_reads_stdin(self):
        result = subprocess.run([sys.executable, "-m", "rosamta", "--config", str(self.config), "apply"],
                                stdin=subprocess.PIPE, capture_output=True, text=True, timeout=30,
                                env={"PYTHONPATH": str(SRC), "HOME": str(self.home), "PATH": "/usr/bin:/bin"})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_json_apply_is_one_document(self):
        code, out, _ = self.run_cli("--json", "apply")
        data = json.loads(out)
        self.assertEqual(data["exit_code"], code)
        self.assertTrue(all("path" in i and "action" in i for i in data["items"]))
        self.assertNotIn("\x1b[", out)

    def test_json_error_has_code_and_message(self):
        self.write("modules/theme.toml", "broken = \n")
        code, out, _ = self.run_cli("--json", "apply")
        data = json.loads(out)
        self.assertEqual(code, 3)
        self.assertEqual(data["error"]["code"], 3)
        self.assertIn("theme.toml", data["error"]["message"])

    def test_errors_go_to_stderr_results_to_stdout(self):
        self.write("templates/alacritty.tmpl", "x={{ font.weight }}\n")
        code, out, err = self.run_cli("render", "alacritty")
        self.assertEqual(out, "")
        self.assertIn("modules/font.toml", err)
