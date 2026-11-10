"""S02 Built-in templates, S03 override a template, S04 template for a new program."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from helpers import RosamtaCase


class BuiltInTemplateTest(RosamtaCase):
    def check_syntax(self, shell: str):
        if shutil.which(shell) is None:
            self.skipTest(f"{shell} is not installed")
        code, out, _ = self.run_cli("render", shell)
        self.assertEqual(code, 0)
        with tempfile.NamedTemporaryFile("w", suffix="." + shell, delete=False) as f:
            f.write(out)
        result = subprocess.run([shell, "-n", f.name], capture_output=True, text=True)
        Path(f.name).unlink()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_bash_output_is_valid_syntax(self):
        self.check_syntax("bash")

    def test_zsh_output_is_valid_syntax(self):
        self.check_syntax("zsh")

    def test_fish_output_is_valid_syntax(self):
        self.check_syntax("fish")

    def test_one_shellrc_module_feeds_every_shell(self):
        for shell in ("bash", "zsh", "fish"):
            _, out, _ = self.run_cli("render", shell)
            self.assertIn("nvim", out, shell)
            self.assertIn("ls -la", out, shell)

    def test_alacritty_gets_colors_and_font(self):
        code, out, _ = self.run_cli("render", "alacritty")
        self.assertEqual(code, 0)
        self.assertIn('family = "JetBrains Mono"', out)
        self.assertIn("size = 13", out)

    def test_missing_value_names_template_and_key(self):
        self.write("modules/font.toml", 'family = "JetBrains Mono"\n')
        code, out, err = self.run_cli("render", "alacritty")
        self.assertEqual(code, 3)
        self.assertIn("template alacritty", err)
        self.assertIn("font.size", err)
        self.assertEqual(out, "")


class UserTemplateTest(RosamtaCase):
    def test_user_file_overrides_built_in(self):
        self.write("templates/alacritty.tmpl", "bg={{ theme.colors.background }}\n")
        _, out, _ = self.run_cli("render", "alacritty")
        self.assertEqual(out, "bg=#1e1e2e\n")

    def test_deleting_override_falls_back_to_built_in(self):
        self.write("templates/alacritty.tmpl", "bg={{ theme.colors.background }}\n")
        (self.config / "templates" / "alacritty.tmpl").unlink()
        _, out, _ = self.run_cli("render", "alacritty")
        self.assertIn("[colors.primary]", out)

    def test_error_names_user_file_and_line(self):
        self.write("templates/alacritty.tmpl", "ok\nbg={{ theme.colors.nope }}\n")
        code, _, err = self.run_cli("render", "alacritty")
        self.assertEqual(code, 3)
        self.assertIn("alacritty.tmpl", err)
        self.assertIn("line 2", err)

    def test_template_for_a_new_program_follows_module_values(self):
        self.write("templates/tmux.tmpl", "set -g status-bg '{{ theme.colors.background }}'\n")
        self.write("manifest.toml", (self.config / "manifest.toml").read_text()
                   + '\n[[output]]\nname = "tmux"\ntemplate = "tmux"\ntarget = "~/.tmux.conf"\n')
        _, out, _ = self.run_cli("render", "tmux")
        self.assertIn("#1e1e2e", out)
        self.edit("modules/theme.toml", "#1e1e2e", "#111111")
        _, out, _ = self.run_cli("render", "tmux")
        self.assertIn("#111111", out)
