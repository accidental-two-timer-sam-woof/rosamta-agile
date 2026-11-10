"""S07 Profiles by OS and Host ID, S08 Profiles by tag."""

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
