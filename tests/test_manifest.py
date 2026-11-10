"""S05 Target paths per operating system, S06 Manifest validation."""

from unittest import mock

from helpers import RosamtaCase


class ManifestTest(RosamtaCase):
    def test_uses_the_path_for_the_current_os(self):
        self.write("manifest.toml", '[[output]]\nname = "bash"\ntemplate = "bash"\n'
                   'target = { linux = "~/linux.bash", macos = "~/mac.bash" }\n')
        self.write("profiles.toml", '[default]\noutputs = ["bash"]\n')
        with mock.patch("rosamta.paths.current_os", return_value="linux"):
            self.run_cli("apply")
        self.assertTrue(self.target("linux.bash").exists())
        self.assertFalse(self.target("mac.bash").exists())

    def test_output_without_path_for_this_os_is_skipped_and_reported(self):
        self.write("manifest.toml", '[[output]]\nname = "bash"\ntemplate = "bash"\n'
                   'target = { macos = "~/mac.bash" }\n')
        self.write("profiles.toml", '[default]\noutputs = ["bash"]\n')
        with mock.patch("rosamta.paths.current_os", return_value="linux"):
            code, out, _ = self.run_cli("apply")
        self.assertEqual(code, 0)
        self.assertIn("bash: not available on linux", out)

    def test_target_outside_home_is_rejected(self):
        self.write("manifest.toml", '[[output]]\nname = "bash"\ntemplate = "bash"\ntarget = "/etc/bash.bashrc"\n')
        code, _, err = self.run_cli("apply")
        self.assertEqual(code, 3)
        self.assertIn("outside the home directory", err)

    def test_two_outputs_with_the_same_target_are_rejected(self):
        self.write("manifest.toml", '[[output]]\nname = "a"\ntemplate = "bash"\ntarget = "~/same"\n'
                   '[[output]]\nname = "b"\ntemplate = "zsh"\ntarget = "~/same"\n')
        code, _, err = self.run_cli("apply")
        self.assertEqual(code, 3)
        self.assertIn("a and b", err)
        self.assertFalse(self.target("same").exists())
