"""S13 Drift, S14 Overwrite a drifted file, S15 Clean up, S16/S17 Query."""

from pathlib import Path

from helpers import RosamtaCase


class DriftTest(RosamtaCase):
    def setUp(self):
        super().setUp()
        self.run_cli("apply")
        self.zsh = self.target(".config/rosamta/shellrc.zsh")
        self.bash = self.target(".config/rosamta/shellrc.bash")

    def test_hand_edit_is_kept_and_reported_others_still_apply(self):
        self.zsh.write_text(self.zsh.read_text() + "alias mine='echo mine'\n")
        self.edit("modules/shellrc.toml", '"nvim"', '"vim"')
        code, out, _ = self.run_cli("apply")
        self.assertEqual(code, 2)
        self.assertIn("alias mine", self.zsh.read_text())
        self.assertIn("drift", out)
        self.assertIn("EDITOR=vim", self.bash.read_text())

    def test_unedited_output_is_not_drifted(self):
        self.edit("modules/shellrc.toml", '"nvim"', '"vim"')
        code, out, _ = self.run_cli("apply")
        self.assertEqual(code, 0)
        self.assertNotIn("drift", out)

    def test_preview_shows_the_diff_of_a_drifted_file(self):
        generated = self.zsh.read_text()
        self.zsh.write_text("# edited\n")
        code, out, _ = self.run_cli("preview")
        self.assertEqual(code, 0)
        self.assertIn("-# edited", out)
        for line in generated.splitlines():
            self.assertIn(f"+{line}", out)

    def test_overwrite_replaces_a_drifted_file(self):
        generated = self.zsh.read_text()
        self.zsh.write_text("# edited\n")
        code, _, _ = self.run_cli("apply", "--overwrite", "zsh")
        self.assertEqual(code, 0)
        self.assertEqual(self.zsh.read_text(), generated)
        code, out, _ = self.run_cli("apply")
        self.assertEqual(code, 0)
        self.assertNotIn("drift", out)


class CleanupTest(RosamtaCase):
    def setUp(self):
        super().setUp()
        self.run_cli("apply")
        self.zsh = self.target(".config/rosamta/shellrc.zsh")
        self.edit("profiles.toml", 'outputs = ["bash", "zsh"]', 'outputs = ["bash"]')

    def test_unchanged_old_output_is_removed_and_previewed(self):
        _, out, _ = self.run_cli("preview")
        self.assertIn("will remove", out)
        code, out, _ = self.run_cli("apply")
        self.assertEqual(code, 0)
        self.assertFalse(self.zsh.exists())
        self.assertIn("removed", out)

    def test_edited_old_output_is_kept(self):
        self.zsh.write_text("# mine\n")
        code, out, _ = self.run_cli("apply")
        self.assertTrue(self.zsh.exists())
        self.assertIn("kept", out)

    def test_files_rosamta_never_wrote_are_untouched(self):
        other = self.target(".config/rosamta/notes.txt")
        other.write_text("hi")
        self.run_cli("apply")
        self.assertEqual(other.read_text(), "hi")


class QueryTest(RosamtaCase):
    def test_module_lists_outputs_with_their_target_paths(self):
        code, out, _ = self.run_cli("query", "shellrc")
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), [f"{name}\t~/{Path(relative)}" for name, relative in (
            ("bash", ".config/rosamta/shellrc.bash"),
            ("zsh", ".config/rosamta/shellrc.zsh"),
            ("fish", ".config/fish/conf.d/rosamta.fish"),
        )])

    def test_output_lists_modules(self):
        _, out, _ = self.run_cli("query", "alacritty")
        self.assertEqual(out.split(), ["font", "theme"])

    def test_unknown_name_exits_non_zero(self):
        code, _, err = self.run_cli("query", "nope")
        self.assertNotEqual(code, 0)
        self.assertIn("not a module or an output", err)
