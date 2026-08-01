from __future__ import annotations
# Bundled under Software Project; implement-feature protocol identifiers remain stable.

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "verify-ready"


class VerifyReadyScenarios(unittest.TestCase):
    def git(self, checkout: Path, *arguments: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(checkout), *arguments],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    def fixture(self) -> dict[str, str]:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        repo = root / "repo"
        managed = root / "managed"
        subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True)
        self.git(repo, "config", "user.name", "Test User")
        self.git(repo, "config", "user.email", "test@example.com")
        (repo / "app.txt").write_text("base\n", encoding="utf-8")
        self.git(repo, "add", ".")
        self.git(repo, "commit", "-m", "base")
        base_sha = self.git(repo, "rev-parse", "HEAD")
        self.git(repo, "worktree", "add", "-b", "feature/health", str(managed))
        (managed / "app.txt").write_text("delivered\n", encoding="utf-8")
        self.git(managed, "add", ".")
        self.git(managed, "commit", "-m", "deliver health")
        return {
            "managed": str(managed),
            "base_sha": base_sha,
            "head_sha": self.git(managed, "rev-parse", "HEAD"),
        }

    def invoke_review_candidate(
        self,
        fixture: dict[str, str],
        *,
        branch: str = "feature/health",
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                str(TOOL),
                "--json",
                "review-candidate",
                "--checkout",
                fixture["managed"],
                "--branch",
                branch,
                "--base-sha",
                fixture["base_sha"],
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_cli_surface(self) -> None:
        version = subprocess.run([str(TOOL), "--version"], capture_output=True, text=True, check=True)
        doctor = subprocess.run([str(TOOL), "--json", "doctor"], capture_output=True, text=True, check=True)
        help_result = subprocess.run([str(TOOL), "--help"], capture_output=True, text=True, check=True)
        self.assertEqual(version.stdout.strip(), "1.0.0")
        self.assertTrue(json.loads(doctor.stdout)["ok"])
        self.assertIn("review-candidate", help_result.stdout)
        self.assertNotIn("local-branch", help_result.stdout)

    def test_review_candidate_returns_git_resolved_full_shas(self) -> None:
        fixture = self.fixture()
        result = self.invoke_review_candidate(fixture)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["data"]["head_sha"], fixture["head_sha"])
        self.assertEqual(payload["data"]["base_sha"], fixture["base_sha"])
        self.assertEqual(payload["data"]["branch"], "feature/health")
        self.assertTrue(payload["data"]["clean"])
        self.assertTrue(payload["data"]["ancestry_verified"])

    def test_review_candidate_rejects_branch_mismatch(self) -> None:
        result = self.invoke_review_candidate(self.fixture(), branch="feature/other")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["error"]["code"], "review-branch-mismatch")


if __name__ == "__main__":
    unittest.main()
