"""S09 Preview, S10 Preflight, S11 Apply, S12 Rollback, S23 Back up existing files."""

import os
from pathlib import Path
from unittest import mock

from helpers import RosamtaCase


class PreviewTest(RosamtaCase):
    def test_preview_shows_diff_and_writes_nothing(self):
        code, out, _ = self.run_cli("preview")
        self.assertEqual(code, 0)
        self.assertIn("+alias ll=", out)
        self.assertEqual([p for p in self.home.rglob("*") if p.is_file()], [])

    def test_nothing_to_apply_exits_0(self):
        self.run_cli("apply")
        code, out, _ = self.run_cli("preview")
        self.assertEqual(code, 0)
        self.assertIn("Nothing to apply.", out)


class ApplyTest(RosamtaCase):
    def test_apply_writes_regular_files_and_summarises(self):
        code, out, _ = self.run_cli("apply")
        self.assertEqual(code, 0)
        bash = self.target(".config/rosamta/shellrc.bash")
        self.assertTrue(bash.is_file() and not bash.is_symlink())
        self.assertIn("written", out)

    def test_identical_file_is_not_rewritten(self):
        self.run_cli("apply")
        bash = self.target(".config/rosamta/shellrc.bash")
        before = bash.stat().st_mtime_ns
        code, out, _ = self.run_cli("apply")
        self.assertEqual(bash.stat().st_mtime_ns, before)
        self.assertIn("unchanged", out)

    def test_preflight_stops_before_writing(self):
        blocked = self.target(".config")
        blocked.mkdir()
        blocked.chmod(0o500)
        self.addCleanup(blocked.chmod, 0o700)
        if os.access(blocked, os.W_OK):
            self.skipTest("running as a user who can write anywhere")
        code, _, err = self.run_cli("apply")
        self.assertEqual(code, 1)
        self.assertIn("cannot write", err)
        self.assertIn(str(blocked), err)
        self.assertFalse(self.target(".local/state/rosamta").exists())

    def test_missing_program_is_a_warning_not_an_install(self):
        self.write("manifest.toml", '[[output]]\nname = "bash"\ntemplate = "bash"\n'
                   'target = "~/x.bash"\nrequires = ["definitely-not-installed-tool"]\n')
        self.write("profiles.toml", '[default]\noutputs = ["bash"]\n')
        code, _, err = self.run_cli("apply")
        self.assertEqual(code, 0)
        self.assertIn("bash: needs definitely-not-installed-tool", err)
        self.assertTrue(self.target("x.bash").exists())


class RollbackTest(RosamtaCase):
    def test_failed_write_restores_everything_and_exits_1(self):
        bash = self.target(".config/rosamta/shellrc.bash")
        bash.parent.mkdir(parents=True)
        self.run_cli("apply")
        self.edit("modules/shellrc.toml", '"nvim"', '"vim"')
        original = bash.read_text()

        real_replace = os.replace
        calls = []

        def failing_replace(src, dst):
            calls.append(dst)
            if len(calls) == 2:
                raise OSError("disk full")
            return real_replace(src, dst)

        with mock.patch("rosamta.applier.os.replace", side_effect=failing_replace):
            code, _, err = self.run_cli("apply")
        self.assertEqual(code, 1)
        self.assertIn("rolled back", err)
        self.assertEqual(bash.read_text(), original)

    def test_rollback_removes_new_files(self):
        real_replace = os.replace
        calls = []

        def failing_replace(src, dst):
            calls.append(dst)
            if len(calls) == 2:
                Path(src).unlink()
                raise OSError("disk full")
            return real_replace(src, dst)

        with mock.patch("rosamta.applier.os.replace", side_effect=failing_replace):
            code, _, _ = self.run_cli("apply")
        self.assertEqual(code, 1)
        self.assertFalse(self.target(".config/rosamta/shellrc.bash").exists())


class TakeOverTest(RosamtaCase):
    def setUp(self):
        super().setUp()
        self.set_tags("gui")
        self.existing = self.target(".config/alacritty/alacritty.toml")
        self.existing.parent.mkdir(parents=True)
        self.existing.write_text("# my own config\n")

    def test_allowed_take_over_backs_up_first(self):
        code, out, _ = self.run_cli("apply")
        self.assertEqual(code, 0)
        self.assertIn("backed up", out)
        backups = list((self.home / ".local/state/rosamta/backups").rglob("alacritty.toml"))
        self.assertEqual(backups[0].read_text(), "# my own config\n")
        self.assertIn("[colors.primary]", self.existing.read_text())

    def test_not_allowed_take_over_skips_and_exits_2(self):
        self.edit("manifest.toml", "take_over = true", "take_over = false")
        code, out, _ = self.run_cli("apply")
        self.assertEqual(code, 2)
        self.assertIn("does not allow taking it over", out)
        self.assertEqual(self.existing.read_text(), "# my own config\n")
