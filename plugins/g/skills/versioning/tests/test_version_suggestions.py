from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "version-suggestions"


class VersionSuggestionsTests(unittest.TestCase):
    def run_cli(self, *args: str) -> dict[str, object]:
        command = [str(SCRIPT), "--json", *args]
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
        return json.loads(completed.stdout)

    def test_version_is_reported(self) -> None:
        completed = subprocess.run([str(SCRIPT), "--version"], check=True, capture_output=True, text=True)
        self.assertEqual(completed.stdout.strip(), "1.0.0")

    def test_main_suggests_patch_minor_and_major_from_rc(self) -> None:
        result = self.run_cli(
            "--mode",
            "main",
            "--tag",
            "v2.3.1-rc.2",
        )
        self.assertEqual(result["latest_tag"], "v2.3.1-rc.2")
        self.assertEqual(
            [suggestion["tag"] for suggestion in result["suggestions"]],
            ["v2.3.2-rc.1", "v2.4.0-rc.1", "v3.0.0-rc.1"],
        )
        self.assertEqual(result["tag_application"], "explicit-confirmation-required")

    def test_main_bootstraps_when_no_tags_exist(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tags_file = Path(directory) / "tags.txt"
            tags_file.write_text("", encoding="utf-8")
            result = self.run_cli("--mode", "main", "--tags-file", str(tags_file))

        self.assertIsNone(result["latest_tag"])
        self.assertEqual(result["initial_version"], "v0.1.0")
        self.assertEqual(result["suggestions"][0]["status"], "bootstrap-required")
        self.assertEqual(result["suggestions"][0]["tag"], "v0.1.0-rc.1")

    def test_main_uses_explicit_initial_version_without_tags(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tags_file = Path(directory) / "tags.txt"
            tags_file.write_text("", encoding="utf-8")
            result = self.run_cli(
                "--mode",
                "main",
                "--initial-version",
                "2.3.0",
                "--tags-file",
                str(tags_file),
            )

        self.assertEqual(result["initial_version"], "v2.3.0")
        self.assertEqual(result["initial_version_source"], "explicit")
        self.assertEqual(result["suggestions"][0]["tag"], "v2.3.0-rc.1")

    def test_legacy_tag_is_read_but_new_suggestion_has_v(self) -> None:
        result = self.run_cli("--mode", "main", "--tag", "2.3.0")
        self.assertEqual(result["latest_tag"], "2.3.0")
        self.assertEqual(result["suggestions"][0]["tag"], "v2.3.1-rc.1")

    def test_release_suggests_next_rc_and_final(self) -> None:
        result = self.run_cli(
            "--mode",
            "release",
            "--line",
            "release/v2.4.0",
            "--tag",
            "v2.4.0-rc.1",
            "--tag",
            "v2.4.0-rc.2",
        )
        self.assertFalse(result["finalized"])
        self.assertEqual(
            [suggestion["tag"] for suggestion in result["suggestions"]],
            ["v2.4.0-rc.3", "v2.4.0"],
        )

    def test_release_suggests_first_rc_and_final_without_tags(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tags_file = Path(directory) / "tags.txt"
            tags_file.write_text("", encoding="utf-8")
            result = self.run_cli(
                "--mode",
                "release",
                "--line",
                "release/v2.4.0",
                "--tags-file",
                str(tags_file),
            )

        self.assertFalse(result["finalized"])
        self.assertEqual(
            [suggestion["tag"] for suggestion in result["suggestions"]],
            ["v2.4.0-rc.1", "v2.4.0"],
        )

    def test_finalized_release_blocks_both_operations(self) -> None:
        result = self.run_cli(
            "--mode",
            "release",
            "--line",
            "release/v2.4.0",
            "--tag",
            "v2.4.0-rc.2",
            "--tag",
            "v2.4.0",
        )
        self.assertTrue(result["finalized"])
        self.assertEqual(
            [suggestion["status"] for suggestion in result["suggestions"]],
            ["blocked-finalized", "blocked-finalized"],
        )
        self.assertEqual([suggestion["tag"] for suggestion in result["suggestions"]], [None, None])

    def test_leading_zero_rc_is_rejected_when_no_valid_tag_exists(self) -> None:
        completed = subprocess.run(
            [str(SCRIPT), "--mode", "main", "--tag", "v2.4.0-rc.01"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("no SemVer tags found", completed.stderr)

    def test_migration_plans_a_canonical_alias_at_the_source_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            self.git(repo, "init")
            self.git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "--allow-empty", "-m", "initial")
            self.git(repo, "tag", "2.3.0")

            result = self.run_cli("--mode", "migration", "--repo", str(repo))

            self.assertEqual(result["migrations"][0]["source_tag"], "2.3.0")
            self.assertEqual(result["migrations"][0]["target_tag"], "v2.3.0")
            self.assertEqual(result["migrations"][0]["status"], "migration-available")
            self.assertEqual(len(result["migrations"][0]["source_commit"]), 40)

    def test_migration_is_empty_when_no_tags_exist(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            self.git(repo, "init")

            result = self.run_cli("--mode", "migration", "--repo", str(repo))

            self.assertEqual(result["status"], "nothing-to-migrate")
            self.assertEqual(result["migrations"], [])

    def test_migration_accepts_an_existing_alias_only_at_the_same_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            self.git(repo, "init")
            self.git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "--allow-empty", "-m", "initial")
            self.git(repo, "tag", "2.3.0")
            self.git(repo, "tag", "v2.3.0")

            result = self.run_cli("--mode", "migration", "--repo", str(repo))

            self.assertEqual(result["migrations"][0]["status"], "already-present")
            self.assertEqual(
                result["migrations"][0]["source_commit"],
                result["migrations"][0]["target_commit"],
            )

    def test_migration_blocks_an_alias_at_a_different_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            self.git(repo, "init")
            self.git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "--allow-empty", "-m", "initial")
            self.git(repo, "tag", "2.3.0")
            self.git(repo, "commit", "--allow-empty", "-m", "second")
            self.git(repo, "tag", "v2.3.0")

            result = self.run_cli("--mode", "migration", "--repo", str(repo))

            self.assertEqual(result["migrations"][0]["status"], "target-conflict")

    @staticmethod
    def git(repo: Path, *args: str) -> None:
        subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
