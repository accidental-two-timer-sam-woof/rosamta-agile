"""S07 Profiles by OS and Host ID, S08 Profiles by tag."""

from unittest import mock

from helpers import RosamtaCase


class ProfileTest(RosamtaCase):
    def setUp(self):
        super().setUp()
        self.write("profiles.toml", """
[default]
outputs = ["bash"]

[[profile]]
name = "work"
host_ids = ["work-laptop"]
outputs = ["zsh"]

[[profile]]
name = "mac-only"
os = ["macos"]
outputs = ["fish"]

[[profile]]
name = "desktop"
tags = ["gui"]
outputs = ["alacritty"]
""")

    def local(self, host_id, *tags):
        path = self.home / ".config" / "rosamta" / "local.toml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'host_id = "{host_id}"\ntags = [' + ", ".join(f'"{t}"' for t in tags) + "]\n")

    def enabled(self):
        _, out, _ = self.run_cli("--json", "preview")
        import json
        return {item["output"] for item in json.loads(out)["items"]}

    def test_first_apply_saves_the_host_id(self):
        with mock.patch("socket.gethostname", return_value="work-laptop.local"):
            code, out, _ = self.run_cli("apply")
        self.assertEqual(code, 0)
        self.assertIn("Host ID is work-laptop", out)
        with mock.patch("socket.gethostname", return_value="work-laptop-2.local"):
            code, out, _ = self.run_cli("apply")
        self.assertEqual(code, 0)
        self.assertNotIn("removed", out)
        self.assertTrue(self.target(".config/rosamta/shellrc.zsh").is_file())
        self.assertIn('host_id = "work-laptop"', (self.home / ".config/rosamta/local.toml").read_text())

    def test_apply_saves_a_missing_host_id_and_keeps_tags(self):
        path = self.home / ".config/rosamta/local.toml"
        path.parent.mkdir(parents=True)
        path.write_text('tags = ["gui"]\n')
        with mock.patch("socket.gethostname", return_value="work-laptop.local"):
            self.run_cli("apply")
        self.assertIn('host_id = "work-laptop"', path.read_text())
        self.assertIn('tags = ["gui"]', path.read_text())

    def test_apply_saves_the_host_id_it_planned_with(self):
        names = iter(["work-laptop.local"])
        with mock.patch("socket.gethostname", side_effect=lambda: next(names, "renamed.local")):
            self.run_cli("apply")
        self.assertIn('host_id = "work-laptop"', (self.home / ".config/rosamta/local.toml").read_text())

    def test_preview_does_not_save_the_host_id(self):
        self.run_cli("preview")
        self.assertFalse((self.home / ".config/rosamta/local.toml").exists())

    def test_host_id_enables_its_outputs(self):
        self.local("work-laptop")
        self.assertIn("zsh", self.enabled())

    def test_os_profile_does_not_match_other_os(self):
        from unittest import mock
        self.local("other")
        with mock.patch("rosamta.paths.current_os", return_value="linux"):
            self.assertNotIn("fish", self.enabled())

    def test_no_match_uses_default_and_says_so(self):
        from unittest import mock
        self.local("other")
        with mock.patch("rosamta.paths.current_os", return_value="linux"):
            _, out, _ = self.run_cli("preview")
            self.assertEqual(self.enabled(), {"bash"})
        self.assertIn("no profile matched", out)

    def test_tags_come_from_local_settings(self):
        self.local("other", "gui")
        self.assertIn("alacritty", self.enabled())

    def test_other_tag_does_not_match(self):
        self.local("other", "server")
        self.assertNotIn("alacritty", self.enabled())

    def test_union_of_matching_profiles(self):
        self.local("work-laptop", "gui")
        enabled = self.enabled()
        self.assertTrue({"bash", "zsh", "alacritty"} <= enabled)
