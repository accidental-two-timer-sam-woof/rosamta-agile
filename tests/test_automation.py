"""S18 Init, S19 No prompts, S20 Exit codes, S21 JSON, S22 Actionable errors."""

import contextlib
import io
import json
import os
import subprocess
import sys
import unittest
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

    def test_init_stops_when_preflight_finds_a_problem(self):
        blocked = self.target(".config/alacritty")
        blocked.mkdir(parents=True)
        blocked.chmod(0o500)
        self.addCleanup(blocked.chmod, 0o700)
        if os.access(blocked, os.W_OK):
            self.skipTest("running as a user who can write anywhere")
        code, _, err = self.init("--tag", "gui")
        self.assertEqual(code, 1)
        self.assertIn("cannot write", err)
        self.assertIn(str(blocked), err)
        self.assertFalse(self.target(".config/rosamta/shellrc.bash").exists())
        self.assertFalse(self.target(".local/state/rosamta").exists())

    @unittest.skipIf(os.name == "nt" or os.geteuid() == 0, "needs POSIX permissions and a non-root user")
    def test_unwritable_settings_folder_is_a_short_error(self):
        folder = self.home / ".config/rosamta"
        folder.mkdir(parents=True)
        folder.chmod(0o500)
        self.addCleanup(folder.chmod, 0o700)
        self.edit("manifest.toml", "~/.config/rosamta/shellrc", "~/rosamta-shellrc")
        for name, run in (("init", self.init), ("apply", lambda: self.run_cli("apply"))):
            with self.subTest(name):
                code, _, err = run()
                self.assertEqual(code, 1)
                self.assertIn("cannot write ~/.config/rosamta/local.toml", err)
                self.assertIn("writable", err)
                self.assertEqual([p for p in self.home.rglob("*") if p.is_file()], [])

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

    def test_json_error_has_code_file_and_message(self):
        self.write("modules/theme.toml", "broken = \n")
        code, out, _ = self.run_cli("--json", "apply")
        data = json.loads(out)
        self.assertEqual(code, 3)
        self.assertEqual(data["error"]["code"], 3)
        self.assertEqual(data["error"]["file"], str(self.config / "modules" / "theme.toml"))
        self.assertIn("theme.toml", data["error"]["message"])

    def test_json_error_names_the_file_to_fix(self):
        # A built-in template cannot be edited, so the error names the module; a user's template names itself.
        self.edit("modules/font.toml", "size = 13\n", "")
        _, out, _ = self.run_cli("--json", "render", "alacritty")
        self.assertEqual(json.loads(out)["error"]["file"], str(self.config / "modules" / "font.toml"))
        self.write("templates/alacritty.tmpl", "x={{ font.weight }}\n")
        _, out, _ = self.run_cli("--json", "render", "alacritty")
        self.assertEqual(json.loads(out)["error"]["file"], str(self.config / "templates" / "alacritty.tmpl"))
        _, out, _ = self.run_cli("--json", "query", "no-such-name")
        self.assertIsNone(json.loads(out)["error"]["file"])

    @unittest.skipIf(os.name == "nt" or os.geteuid() == 0, "needs POSIX permissions and a non-root user")
    def test_unreadable_settings_is_a_json_error(self):
        folder = self.home / ".config/rosamta"
        folder.mkdir(parents=True)
        settings = folder / "local.toml"
        settings.write_text('host_id = "test-host"\ntags = []\n')
        for name, target, mode, restore in (("file", settings, 0o000, 0o600), ("folder", folder, 0o600, 0o700)):
            with self.subTest(name):
                target.chmod(mode)
                try:
                    code, out, _ = self.run_cli("--json", "preview")
                finally:
                    target.chmod(restore)
                self.assertEqual(code, 1)
                message = json.loads(out)["error"]["message"]
                self.assertIn("cannot read ~/.config/rosamta/local.toml", message)
                self.assertIn("searchable", message)

    @unittest.skipIf(not hasattr(os, "mkfifo"), "needs named pipes")
    def test_settings_that_are_not_a_file_are_rejected_without_hanging(self):
        settings = self.home / ".config/rosamta/local.toml"
        settings.parent.mkdir(parents=True)
        for name, make, remove in (("fifo", os.mkfifo, os.unlink), ("folder", os.mkdir, os.rmdir)):
            with self.subTest(name):
                make(settings)
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "rosamta", "--config", str(self.config), "preview"],
                        stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10,
                        env={"PYTHONPATH": str(SRC), "HOME": str(self.home), "PATH": "/usr/bin:/bin"})
                finally:
                    remove(settings)
                self.assertEqual(result.returncode, 1)
                self.assertIn("not a regular file", result.stderr)

    def run_main(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_json_usage_error_is_one_document_with_exit_3(self):
        for args in (["--json", "bogus"], ["--json", "get"]):
            with self.subTest(args=args):
                code, out, err = self.run_main(*args)
                self.assertEqual(code, 3)
                self.assertEqual(json.loads(out)["error"]["code"], 3)
                self.assertIn("usage:", err)

    def test_usage_error_without_json_exits_3(self):
        code, out, err = self.run_main("get")
        self.assertEqual(code, 3)
        self.assertEqual(out, "")
        self.assertIn("required: key", err)

    def test_errors_go_to_stderr_results_to_stdout(self):
        self.write("templates/alacritty.tmpl", "x={{ font.weight }}\n")
        code, out, err = self.run_cli("render", "alacritty")
        self.assertEqual(out, "")
        self.assertIn("modules/font.toml", err)
