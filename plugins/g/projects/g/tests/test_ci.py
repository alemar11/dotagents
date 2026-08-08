from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from g import ci as cli

class CiInspectContractTests(unittest.TestCase):
    def test_version(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(["--version"])
        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), "2.5.1")

    def test_json_doctor_shape(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.main(["--json", "doctor"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["version"], "2.5.1")
        self.assertIn("git", payload["checks"])
        self.assertIn("gh", payload["checks"])

    def test_invalid_repo_reference(self) -> None:
        with self.assertRaises(cli.InspectionError):
            cli.validate_repo_reference("not-valid")

    def test_json_error_shape(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(["--json", "--repo", "bad", "--allow-non-project"])
        self.assertEqual(code, 64)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["version"], "2.5.1")
        self.assertEqual(payload["command"], ["inspect"])
        self.assertIn("message", payload["error"])

    def test_permissions_preflight_reads_actions_and_workflow_settings(self) -> None:
        gh_results = [
            cli.GhResult(0, "", ""),
            cli.GhResult(0, json.dumps({"enabled": True}), ""),
            cli.GhResult(
                0,
                json.dumps(
                    {
                        "default_workflow_permissions": "read",
                        "can_approve_pull_request_reviews": True,
                    }
                ),
                "",
            ),
        ]
        stdout = io.StringIO()
        with (
            mock.patch.object(cli, "which", return_value="/opt/homebrew/bin/gh"),
            mock.patch.object(cli, "run_gh_command", side_effect=gh_results) as run_gh,
            contextlib.redirect_stdout(stdout),
        ):
            code = cli.main(
                [
                    "--json",
                    "permissions",
                    "--repo",
                    "owner/repo",
                    "--allow-non-project",
                ]
            )

        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], ["permissions"])
        data = payload["data"]
        self.assertTrue(data["actions_enabled"])
        self.assertTrue(data["can_approve_pull_request_reviews"])
        self.assertEqual(data["pull_requests_write"]["repository_gate"], "enabled")
        self.assertEqual(data["pull_requests_write"]["effective"], "not-verifiable-before-workflow-run")
        self.assertEqual(data["workflow_authoring"]["status"], "ready")
        self.assertIsNone(data["workflow_authoring"]["warning"])
        self.assertEqual(
            run_gh.call_args_list[1].args[0][:2],
            ["api", "repos/owner/repo/actions/permissions"],
        )
        self.assertEqual(
            run_gh.call_args_list[2].args[0][:2],
            ["api", "repos/owner/repo/actions/permissions/workflow"],
        )

    def test_permissions_preflight_reports_api_denial_without_mutating(self) -> None:
        gh_results = [
            cli.GhResult(0, "", ""),
            cli.GhResult(403, "", "HTTP 403: requires Administration read permission"),
        ]
        stdout = io.StringIO()
        with (
            mock.patch.object(cli, "which", return_value="/opt/homebrew/bin/gh"),
            mock.patch.object(cli, "run_gh_command", side_effect=gh_results),
            contextlib.redirect_stdout(stdout),
        ):
            code = cli.main(
                [
                    "--json",
                    "permissions",
                    "--repo",
                    "owner/repo",
                    "--allow-non-project",
                ]
            )

        self.assertEqual(code, 1)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["command"], ["permissions"])
        self.assertIn("Administration read permission", payload["error"]["message"])

    def test_permissions_preflight_warns_but_does_not_block_workflow_authoring(self) -> None:
        gh_results = [
            cli.GhResult(0, "", ""),
            cli.GhResult(0, json.dumps({"enabled": True}), ""),
            cli.GhResult(
                0,
                json.dumps(
                    {
                        "default_workflow_permissions": "read",
                        "can_approve_pull_request_reviews": False,
                    }
                ),
                "",
            ),
        ]
        with (
            mock.patch.object(cli, "which", return_value="/opt/homebrew/bin/gh"),
            mock.patch.object(cli, "run_gh_command", side_effect=gh_results),
        ):
            payload = cli.inspect_actions_permissions(repo="owner/repo", repo_root=None)

        self.assertEqual(payload["pull_requests_write"]["repository_gate"], "blocked")
        self.assertEqual(payload["workflow_authoring"]["status"], "allowed-with-warning")
        self.assertIn("will not work", payload["workflow_authoring"]["warning"])


if __name__ == "__main__":
    unittest.main()
