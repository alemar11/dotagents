from __future__ import annotations

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

    def write_tracker(self, path: Path, *, state: str, checked: bool) -> None:
        marker = "x" if checked else " "
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(
                [
                    "---",
                    f"workflow_state: {state}",
                    "---",
                    "",
                    "# Deliver health",
                    "",
                    "## Acceptance Criteria",
                    "",
                    f"- [{marker}] Health is visible",
                    "",
                    "## Validation",
                    "",
                    "- Run tests",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def fixture(self, *, state: str = "ready-for-agent", checked: bool = True) -> dict[str, str]:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        original = root / "repo"
        managed = root / "managed"
        subprocess.run(["git", "init", "-b", "main", str(original)], check=True, capture_output=True)
        self.git(original, "config", "user.name", "Test User")
        self.git(original, "config", "user.email", "test@example.com")
        spec = original / "planning/features/health/SPEC.md"
        issues = [
            original / "planning/features/health/issues/01-health.md",
            original / "planning/features/health/issues/02-route-check.md",
        ]
        self.write_tracker(spec, state="ready-for-agent", checked=False)
        for issue in issues:
            self.write_tracker(issue, state="ready-for-agent", checked=False)
        (original / "app.txt").write_text("base\n", encoding="utf-8")
        self.git(original, "add", ".")
        self.git(original, "commit", "-m", "base")
        base_sha = self.git(original, "rev-parse", "HEAD")
        self.git(original, "worktree", "add", "-b", "feature/health", str(managed))

        managed_spec = managed / "planning/features/health/SPEC.md"
        self.write_tracker(managed_spec, state="ready-for-agent", checked=checked)
        for name in ["01-health.md", "02-route-check.md"]:
            active_issue = managed / "planning/features/health/issues" / name
            done_issue = managed / "planning/features/health/issues/done" / name
            done_issue.parent.mkdir(parents=True, exist_ok=True)
            active_issue.rename(done_issue)
            self.write_tracker(done_issue, state=state, checked=checked)
        (managed / "app.txt").write_text("delivered\n", encoding="utf-8")
        self.git(managed, "add", ".")
        self.git(managed, "commit", "-m", "deliver health")
        return {
            "original": str(original),
            "managed": str(managed),
            "base_sha": base_sha,
            "head_sha": self.git(managed, "rev-parse", "HEAD"),
        }

    def invoke(self, fixture: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                str(TOOL),
                "--json",
                "local-branch",
                "--checkout",
                fixture["managed"],
                "--original-checkout",
                fixture["original"],
                "--base-branch",
                "main",
                "--base-sha",
                fixture["base_sha"],
                "--branch",
                "feature/health",
                "--head-sha",
                fixture["head_sha"],
                "--spec-path",
                "planning/features/health/SPEC.md",
                "--issue",
                "planning/features/health/issues/done/01-health.md=ready-for-agent",
                "--issue",
                "planning/features/health/issues/done/02-route-check.md=ready-for-agent",
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
        self.assertIn("local-branch", help_result.stdout)

    def test_local_branch_returns_one_terminal_snapshot(self) -> None:
        result = self.invoke(self.fixture())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["branch"], "feature/health")
        self.assertEqual(payload["data"]["spec_criteria_checked"], 1)
        self.assertEqual(len(payload["data"]["issues"]), 2)
        self.assertEqual(payload["data"]["issues"][0]["workflow_state"], "ready-for-agent")
        self.assertTrue(all(issue["criteria_checked"] == 1 for issue in payload["data"]["issues"]))
        self.assertTrue(payload["data"]["clean"])

    def test_local_branch_rejects_done_as_a_workflow_state(self) -> None:
        result = self.invoke(self.fixture(state="done"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["error"]["code"], "workflow-state-mismatch")

    def test_local_branch_rejects_unchecked_terminal_criteria(self) -> None:
        result = self.invoke(self.fixture(checked=False))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["error"]["code"], "unchecked-acceptance-criteria")


if __name__ == "__main__":
    unittest.main()
