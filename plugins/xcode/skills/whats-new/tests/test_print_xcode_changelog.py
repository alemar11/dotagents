from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "print_xcode_changelog.py"
)
SPEC = importlib.util.spec_from_file_location("print_xcode_changelog", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
changelog = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = changelog
SPEC.loader.exec_module(changelog)


INDEX_MARKDOWN = """
[Xcode 27 Beta 6 Release Notes](/documentation/Xcode-Release-Notes/xcode-27-release-notes)
[Xcode 26.6 Release Notes](/documentation/Xcode-Release-Notes/xcode-26_6-release-notes)
[Xcode 26.5 Release Notes](/documentation/Xcode-Release-Notes/xcode-26_5-release-notes)
"""


class XcodeChangelogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.entries = changelog.parse_index_entries(INDEX_MARKDOWN)

    def test_numbered_beta_entry_is_preserved(self) -> None:
        beta = self.entries[0]

        self.assertEqual(beta.release_channel, changelog.BETA_CHANNEL)
        self.assertEqual(beta.version, "27")
        self.assertEqual(beta.beta_iteration, 6)

    def test_unversioned_beta_request_matches_current_beta(self) -> None:
        result = changelog.match_release_entry(
            self.entries, changelog.parse_target("27 beta")
        )

        self.assertEqual(result.entry.title, "Xcode 27 Beta 6 Release Notes")

    def test_numbered_beta_request_does_not_substitute_another_beta(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "No Xcode beta release notes"):
            changelog.match_release_entry(
                self.entries, changelog.parse_target("27 beta 5")
            )

    def test_numbered_beta_request_does_not_substitute_another_point_release(self) -> None:
        point_release_entries = changelog.parse_index_entries(
            "[Xcode 27.1 Beta 6 Release Notes]"
            "(/documentation/Xcode-Release-Notes/xcode-27_1-release-notes)"
        )

        with self.assertRaisesRegex(RuntimeError, "No Xcode beta release notes"):
            changelog.match_release_entry(
                point_release_entries, changelog.parse_target("27.0 beta 6")
            )

    def test_missing_beta_does_not_substitute_a_stable_release(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "No Xcode beta release notes"):
            changelog.match_release_entry(
                self.entries, changelog.parse_target("26.5 beta")
            )

    def test_missing_stable_does_not_substitute_a_beta_release(self) -> None:
        result = changelog.match_release_entry(
            self.entries, changelog.parse_target("27")
        )

        self.assertEqual(result.entry.title, "Xcode 26.6 Release Notes")
        self.assertIsNotNone(result.fallback_message)

    def test_active_lookup_requires_an_installed_xcode_version(self) -> None:
        info = changelog.XcodeInfo(
            version=None,
            build_version=None,
            developer_dir="/Library/Developer/CommandLineTools",
            app_path=None,
            resolution_errors=("xcodebuild failed",),
        )

        with self.assertRaisesRegex(
            RuntimeError, "Unable to resolve the active Xcode version"
        ):
            changelog.resolve_target(info, None)

    def test_active_beta_path_preserves_the_beta_channel(self) -> None:
        info = changelog.XcodeInfo(
            version="27.0",
            build_version="18A123",
            developer_dir="/Applications/Xcode-beta.app/Contents/Developer",
            app_path="/Applications/Xcode-beta.app",
            resolution_errors=(),
        )

        target = changelog.resolve_target(info, None)
        result = changelog.match_release_entry(self.entries, target)

        self.assertEqual(target.release_channel, changelog.BETA_CHANNEL)
        self.assertEqual(result.entry.title, "Xcode 27 Beta 6 Release Notes")

    def test_active_stable_build_suffix_remains_stable(self) -> None:
        info = changelog.XcodeInfo(
            version="16.0",
            build_version="16A242d",
            developer_dir="/Applications/Xcode.app/Contents/Developer",
            app_path="/Applications/Xcode.app",
            resolution_errors=(),
        )

        self.assertEqual(
            changelog.resolve_target(info, None).release_channel,
            changelog.STABLE_CHANNEL,
        )

    def test_default_supplements_installed_notes_with_stable_and_beta(self) -> None:
        installed = next(entry for entry in self.entries if entry.version == "26.5")

        supplementary = changelog.choose_supplementary_entries(
            self.entries, installed
        )

        self.assertEqual(
            [entry.title for entry in supplementary],
            ["Xcode 26.6 Release Notes", "Xcode 27 Beta 6 Release Notes"],
        )


if __name__ == "__main__":
    unittest.main()
