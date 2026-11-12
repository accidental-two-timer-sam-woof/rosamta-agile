"""S18 Init, S19 No prompts, S20 Exit codes, S21 JSON, S22 Actionable errors."""

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from helpers import EXAMPLE, RosamtaCase
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

    def test_json_option_is_not_abbreviated(self):
        code, out, err = self.run_main("--js", "render", "alacritty")
        self.assertEqual(code, 3)
        self.assertEqual(out, "")
        self.assertIn("--js", err)

    def test_json_after_double_dash_is_a_value_not_the_option(self):
        code, out, _ = self.run_main("--config", str(self.config), "get", "--", "--json")
        self.assertEqual(code, 3)
        self.assertEqual(out, "")

    def test_errors_go_to_stderr_results_to_stdout(self):
        self.write("templates/alacritty.tmpl", "x={{ font.weight }}\n")
        code, out, err = self.run_cli("render", "alacritty")
        self.assertEqual(out, "")
        self.assertIn("modules/font.toml", err)


POSIX_USER = unittest.skipIf(os.name == "nt" or os.geteuid() == 0, "needs POSIX permissions and a non-root user")


class ActionableErrorTest(RosamtaCase):
    """S22: every error says what failed, where, and what to change, with no traceback."""

    def file_in(self, place, relative):
        return (self.config if place == "config" else self.home) / relative

    @POSIX_USER
    def test_unreadable_files_name_the_file(self):
        for place, relative in (("config", "manifest.toml"), ("config", "modules/theme.toml"),
                                ("config", "profiles.toml"), ("config", "templates/bash.tmpl"),
                                ("home", ".local/state/rosamta/state.json"), ("home", ".config/rosamta/shellrc.bash")):
            with self.subTest(relative):
                path = self.file_in(place, relative)
                if not path.exists():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("{}\n" if path.suffix == ".json" else "x\n")
                path.chmod(0)
                try:
                    code, _, err = self.run_cli("preview")
                finally:
                    path.chmod(0o600)
                self.assertEqual(code, 1)
                shown = f"~/{Path(relative)}" if place == "home" else str(path)
                self.assertIn(f"cannot read {shown}", err)
                self.assertIn("readable", err)

    def test_text_that_is_not_utf8_is_a_config_error(self):
        for place, relative in (("config", "manifest.toml"), ("config", "modules/theme.toml"),
                                ("home", ".config/rosamta/local.toml")):
            with self.subTest(relative):
                path = self.file_in(place, relative)
                path.parent.mkdir(parents=True, exist_ok=True)
                before = path.read_bytes() if path.exists() else None
                path.write_bytes(b"\xff")
                try:
                    code, _, err = self.run_cli("preview")
                finally:
                    if before is None:
                        path.unlink()
                    else:
                        path.write_bytes(before)
                self.assertEqual(code, 3)
                self.assertIn("not UTF-8 text; save it with UTF-8 encoding", err)

    def test_damaged_state_record_says_how_to_recover(self):
        state = self.home / ".local/state/rosamta/state.json"
        state.parent.mkdir(parents=True)
        for data in (b"{nope", b"[1]", b'{"written": 1}', b"\xff"):
            with self.subTest(data):
                state.write_bytes(data)
                code, _, err = self.run_cli("preview")
                self.assertEqual(code, 1)
                self.assertIn("state.json is damaged; delete it to start over", err)

    @POSIX_USER
    def test_unsearchable_templates_folder_is_an_error_not_the_built_in(self):
        self.write("templates/bash.tmpl", "MY BASH\n")
        folder = self.config / "templates"
        folder.chmod(0o600)
        self.addCleanup(folder.chmod, 0o700)
        code, out, err = self.run_cli("render", "bash")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn(f"cannot read {folder / 'bash.tmpl'}", err)

    @POSIX_USER
    def test_unreadable_modules_folder_is_an_error_not_an_empty_folder(self):
        folder = self.config / "modules"
        self.addCleanup(folder.chmod, 0o700)
        # 000 and 300 cannot be listed; 600 can be listed, but its files cannot be opened.
        for mode in (0o000, 0o300, 0o600):
            for args in (("render", "bash"), ("get", "theme.colors.background")):
                with self.subTest(mode=oct(mode), args=args):
                    folder.chmod(mode)
                    code, out, err = self.run_cli(*args)
                    self.assertEqual(code, 1)
                    self.assertEqual(out, "")
                    self.assertIn(f"cannot read {folder}", err)
                    self.assertIn("readable and searchable", err)

    @POSIX_USER
    def test_init_names_a_config_folder_it_cannot_read(self):
        self.config.chmod(0o000)
        self.addCleanup(self.config.chmod, 0o700)
        code, _, err = self.run_cli("init", str(self.config))
        self.assertEqual(code, 1)
        self.assertIn(f"cannot read {self.config.resolve() / 'manifest.toml'}", err)

    def test_init_on_a_file_is_not_a_config_folder(self):
        code, _, err = self.run_cli("init", str(self.config / "manifest.toml"))
        self.assertEqual(code, 3)
        self.assertIn("not a rosamta config folder (no manifest.toml)", err)

    @unittest.skipIf(not hasattr(os, "mkfifo"), "needs named pipes")
    def test_config_files_that_are_not_regular_files_do_not_hang(self):
        for relative in ("manifest.toml", "templates/bash.tmpl"):
            with self.subTest(relative):
                path = self.config / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                before = path.read_bytes() if path.exists() else None
                path.unlink(missing_ok=True)
                os.mkfifo(path)
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "rosamta", "--config", str(self.config), "preview"],
                        stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10,
                        env={"PYTHONPATH": str(SRC), "HOME": str(self.home), "PATH": "/usr/bin:/bin"})
                finally:
                    path.unlink()
                    if before is not None:
                        path.write_bytes(before)
                self.assertEqual(result.returncode, 1)
                self.assertIn(f"{path} is not a regular file", result.stderr)

    def test_preview_shows_a_diff_for_a_file_that_is_not_utf8(self):
        self.set_tags("gui")
        existing = self.target(".config/alacritty/alacritty.toml")
        existing.parent.mkdir(parents=True)
        existing.write_bytes(b"\xff\xfe old\n")
        code, out, _ = self.run_cli("preview")
        self.assertEqual(code, 0)
        self.assertIn("alacritty.toml (on disk)", out)

    @POSIX_USER
    def test_existing_state_record_in_a_read_only_folder_is_still_updated(self):
        self.assertEqual(self.run_cli("apply")[0], 0)
        folder = self.home / ".local/state/rosamta"
        folder.chmod(0o500)
        self.addCleanup(folder.chmod, 0o700)
        self.edit("modules/shellrc.toml", "[env]", '[env]\nROSAMTA_TEST = "1"')
        code, out, err = self.run_cli("apply")
        self.assertEqual(code, 0, err)
        self.assertIn("written    bash", out)

    @POSIX_USER
    def test_read_only_state_record_stops_apply_before_writing(self):
        state = self.home / ".local/state/rosamta/state.json"
        state.parent.mkdir(parents=True)
        state.write_text("{}\n")
        state.chmod(0o400)
        self.addCleanup(state.chmod, 0o600)
        code, _, err = self.run_cli("apply")
        self.assertEqual(code, 1)
        self.assertIn(f"state record: cannot write to {state}", err)
        self.assertFalse(self.target(".config/rosamta/shellrc.bash").exists())

    @POSIX_USER
    def test_unreadable_old_output_is_left_alone(self):
        self.run_cli("apply")
        old = self.target(".config/rosamta/shellrc.zsh")
        self.edit("profiles.toml", '"bash", "zsh"', '"bash"')
        old.chmod(0)
        self.addCleanup(old.chmod, 0o600)
        code, out, _ = self.run_cli("apply")
        self.assertEqual(code, 2)
        self.assertIn("rosamta cannot read it, so it is left alone", out)
        self.assertTrue(old.exists())

    @POSIX_USER
    def test_unwritable_state_folder_stops_apply_before_writing(self):
        folder = self.home / ".local/state/rosamta"
        folder.mkdir(parents=True)
        folder.chmod(0o500)
        self.addCleanup(folder.chmod, 0o700)
        code, _, err = self.run_cli("apply")
        self.assertEqual(code, 1)
        self.assertIn(f"state record: cannot write to {folder}", err)
        self.assertFalse(self.target(".config/rosamta/shellrc.bash").exists())

    def test_config_errors_say_what_to_change(self):
        cases = (
            ("unknown OS", lambda: self.edit("manifest.toml", "macos =", "mac ="), ("preview",),
             "unknown OS mac; use macos, linux, windows"),
            ("unknown output", lambda: self.edit("profiles.toml", '"zsh"]', '"zshh"]'), ("preview",),
             "add it to manifest.toml or remove it from the profile"),
            ("unknown query name", lambda: None, ("query", "nope"),
             "modules: font, shellrc, theme; outputs: bash, zsh, fish, alacritty"),
            ("no modules folder", lambda: shutil.rmtree(self.config / "modules"), ("preview",),
             "create it with one .toml file per module"),
            ("no manifest", lambda: (self.config / "manifest.toml").unlink(), ("preview",),
             "pass --config <folder>, or run rosamta init <folder>"),
            ("get, missing key", lambda: None, ("get", "theme.nope.deeper"),
             "key not found: theme.nope; set it in modules/theme.toml"),
            ("get, missing module", lambda: None, ("get", "nope.x"),
             "key not found: nope.x; there is no module nope (modules: font, shellrc, theme)"),
            ("render, unknown output", lambda: None, ("render", "nope"),
             "output nope: not in the manifest; outputs: bash, zsh, fish, alacritty"),
        )
        for name, change, args, hint in cases:
            with self.subTest(name):
                shutil.rmtree(self.config)
                shutil.copytree(EXAMPLE, self.config)
                change()
                code, _, err = self.run_cli(*args)
                self.assertEqual(code, 3)
                self.assertIn(hint, err)
