"""S01 Shared values in a module."""

from helpers import RosamtaCase


class ModuleTest(RosamtaCase):
    def test_one_value_reaches_every_output_that_uses_it(self):
        self.set_tags("gui")
        self.edit("modules/theme.toml", "#1e1e2e", "#000000")
        code, out, _ = self.run_cli("render", "alacritty")
        self.assertEqual(code, 0)
        self.assertIn('background = "#000000"', out)

    def test_syntax_error_names_file_and_line_writes_nothing_exits_3(self):
        self.write("modules/theme.toml", "[colors]\nbackground = \n")
        code, out, err = self.run_cli("apply")
        self.assertEqual(code, 3)
        self.assertIn("theme.toml", err)
        self.assertIn("line 2", err)
        self.assertEqual(list(self.home.rglob("*.bash")), [])
