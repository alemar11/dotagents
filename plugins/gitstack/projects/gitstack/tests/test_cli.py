from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gitstack import cli
from gitstack.common import GitStackError, Result, normalize_remote, resolve_repo
from gitstack.publish import _find_open_pr, open_pr, preflight, template


class CliContractTests(unittest.TestCase):
    def invoke(self, args: list[str]) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli.main(args)
        return code, output.getvalue()

    def test_version(self) -> None:
        code, output = self.invoke(["--version"])
        self.assertEqual(code, 0)
        self.assertEqual(output.strip(), "4.1.1")

    def test_json_doctor_shape(self) -> None:
        code, output = self.invoke(["--json", "doctor"])
        payload = json.loads(output)
        self.assertIn(code, {0, 1})
        self.assertEqual(payload["version"], "4.1.1")
        self.assertFalse(payload["checks"]["connector"]["cli_access"])

    def test_json_argument_error(self) -> None:
        code, output = self.invoke(["--json", "repo", "resolve", "--repo", "bad"])
        payload = json.loads(output)
        self.assertEqual(code, 64)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "invalid_arguments")

    def test_repo_resolve_json(self) -> None:
        code, output = self.invoke(["repo", "resolve", "--repo", "owner/repo", "--json"])
        payload = json.loads(output)
        self.assertEqual(code, 0)
        self.assertEqual(payload["data"]["repo"], "owner/repo")

    def test_normalize_remote(self) -> None:
        self.assertEqual(normalize_remote("git@github.com:owner/repo.git"), "owner/repo")
        self.assertEqual(normalize_remote("https://github.com/owner/repo.git"), "owner/repo")

    def test_template_reads_utf8_body_file(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as handle:
            handle.write("Body ✓")
            handle.flush()
            self.assertEqual(template("Title", handle.name)["body"], "Body ✓")

    def test_publish_refuses_default_branch(self) -> None:
        state = {"repo": "owner/repo", "root": "/tmp/repo", "branch": "main", "default_branch": "main", "on_default_branch": True, "upstream": None, "dirty": False, "status": [], "existing_pull_request": None}
        with mock.patch("gitstack.publish.preflight", return_value=state):
            with self.assertRaises(GitStackError) as raised:
                open_pr(repo=None, title="Title", body_file="body.md", draft=True, base=None, dry_run=True)
        self.assertEqual(raised.exception.code, "unsafe_branch")

    def test_publish_dry_run(self) -> None:
        state = {"repo": "owner/repo", "root": "/tmp/repo", "branch": "feature", "default_branch": "main", "on_default_branch": False, "upstream": "origin/feature", "dirty": False, "status": [], "existing_pull_request": None}
        with mock.patch("gitstack.publish.preflight", return_value=state):
            result = open_pr(repo=None, title="Title", body_file="body.md", draft=True, base="main", dry_run=True)
        self.assertEqual(result["status"], "dry-run")
        self.assertIn("--draft", result["command"])

    def test_preflight_keeps_matching_explicit_repo_checkout(self) -> None:
        def fake_checked(command, cwd=None):
            if command[:3] == ["git", "rev-parse", "--show-toplevel"]:
                return Result(0, "/tmp/repo\n", "")
            if command[:4] == ["git", "remote", "get-url", "origin"]:
                return Result(0, "git@github.com:owner/repo.git\n", "")
            if command[:3] == ["gh", "auth", "status"]:
                return Result(0, "", "")
            if command[:3] == ["git", "branch", "--show-current"]:
                return Result(0, "feature\n", "")
            if command[:3] == ["git", "status", "--short"]:
                return Result(0, "## feature...origin/feature\n", "")
            if command[:3] == ["gh", "repo", "view"]:
                return Result(0, "main\n", "")
            if command[:3] == ["git", "rev-list", "--left-right"]:
                return Result(0, "0 0\n", "")
            if command[:3] == ["gh", "pr", "list"]:
                return Result(0, "[]\n", "")
            raise AssertionError(command)

        def fake_run(command, cwd=None):
            if command[-1] == "branch.feature.remote":
                return Result(0, "origin\n", "")
            if command[-1] == "branch.feature.merge":
                return Result(0, "refs/heads/feature\n", "")
            raise AssertionError(command)

        with mock.patch("gitstack.publish.checked", side_effect=fake_checked), \
             mock.patch("gitstack.publish.run", side_effect=fake_run):
            state = preflight("owner/repo")
        self.assertEqual(state["root"], "/tmp/repo")
        self.assertEqual(state["upstream"], "origin/feature")
        self.assertTrue(state["upstream_valid"])

    def test_preflight_rejects_explicit_repo_origin_mismatch(self) -> None:
        with mock.patch(
            "gitstack.publish.checked",
            side_effect=[
                Result(0, "/tmp/repo\n", ""),
                Result(0, "git@github.com:owner/other.git\n", ""),
            ],
        ):
            with self.assertRaises(GitStackError) as raised:
                preflight("owner/repo")
        self.assertEqual(raised.exception.code, "repo_mismatch")

    def test_preflight_rejects_detached_head(self) -> None:
        with mock.patch(
            "gitstack.publish.checked",
            side_effect=[
                Result(0, "/tmp/repo\n", ""),
                Result(0, "git@github.com:owner/repo.git\n", ""),
                Result(0, "", ""),
                Result(0, "\n", ""),
            ],
        ):
            with self.assertRaises(GitStackError) as raised:
                preflight()
        self.assertEqual(raised.exception.code, "unsafe_branch")

    def test_preflight_rejects_wrong_upstream(self) -> None:
        checked_results = [
            Result(0, "/tmp/repo\n", ""),
            Result(0, "git@github.com:owner/repo.git\n", ""),
            Result(0, "", ""),
            Result(0, "feature\n", ""),
            Result(0, "## feature...fork/feature\n", ""),
            Result(0, "main\n", ""),
        ]
        run_results = [
            Result(0, "fork\n", ""),
            Result(0, "refs/heads/feature\n", ""),
        ]
        with mock.patch("gitstack.publish.checked", side_effect=checked_results), \
             mock.patch("gitstack.publish.run", side_effect=run_results):
            with self.assertRaises(GitStackError) as raised:
                preflight()
        self.assertEqual(raised.exception.code, "upstream_mismatch")

    def test_preflight_allows_missing_upstream_before_first_push(self) -> None:
        checked_results = [
            Result(0, "/tmp/repo\n", ""),
            Result(0, "git@github.com:owner/repo.git\n", ""),
            Result(0, "", ""),
            Result(0, "feature\n", ""),
            Result(0, "## feature\n", ""),
            Result(0, "main\n", ""),
            Result(0, "[]\n", ""),
        ]
        with mock.patch("gitstack.publish.checked", side_effect=checked_results), \
             mock.patch("gitstack.publish.run", return_value=Result(1, "", "no upstream")):
            state = preflight()
        self.assertIsNone(state["upstream"])
        self.assertTrue(state["needs_push"])

    def test_preflight_rejects_partial_upstream_configuration(self) -> None:
        checked_results = [
            Result(0, "/tmp/repo\n", ""),
            Result(0, "git@github.com:owner/repo.git\n", ""),
            Result(0, "", ""),
            Result(0, "feature\n", ""),
            Result(0, "## feature\n", ""),
            Result(0, "main\n", ""),
        ]
        run_results = [Result(0, "origin\n", ""), Result(1, "", "missing")]
        with mock.patch("gitstack.publish.checked", side_effect=checked_results), \
             mock.patch("gitstack.publish.run", side_effect=run_results):
            with self.assertRaises(GitStackError) as raised:
                preflight()
        self.assertEqual(raised.exception.code, "upstream_mismatch")

    def test_preflight_marks_ahead_branch_for_push(self) -> None:
        checked_results = [
            Result(0, "/tmp/repo\n", ""),
            Result(0, "git@github.com:owner/repo.git\n", ""),
            Result(0, "", ""),
            Result(0, "feature\n", ""),
            Result(0, "## feature...origin/feature [ahead 2]\n", ""),
            Result(0, "main\n", ""),
            Result(0, "2 0\n", ""),
            Result(0, "[]\n", ""),
        ]
        run_results = [
            Result(0, "origin\n", ""),
            Result(0, "refs/heads/feature\n", ""),
        ]
        with mock.patch("gitstack.publish.checked", side_effect=checked_results), \
             mock.patch("gitstack.publish.run", side_effect=run_results):
            state = preflight()
        self.assertEqual(state["ahead"], 2)
        self.assertTrue(state["needs_push"])

    def test_publish_open_rejects_unpushed_branch(self) -> None:
        state = {
            "repo": "owner/repo", "root": "/tmp/repo", "branch": "feature",
            "default_branch": "main", "on_default_branch": False,
            "upstream": None, "upstream_valid": True, "needs_push": True,
            "dirty": False, "status": [], "existing_pull_request": None,
        }
        with mock.patch("gitstack.publish.preflight", return_value=state):
            with self.assertRaises(GitStackError) as raised:
                open_pr(repo=None, title="Title", body_file="body.md", draft=True, base=None, dry_run=True)
        self.assertEqual(raised.exception.code, "branch_not_pushed")

    def test_open_pr_lookup_requires_verified_head_identity(self) -> None:
        payload = json.dumps([
            {
                "number": 7, "url": "https://github.com/owner/repo/pull/7",
                "title": "PR", "state": "OPEN", "isDraft": True,
                "headRefName": "feature",
                "headRepositoryOwner": {"login": "other"},
                "headRepository": {"name": "repo"},
            }
        ])
        with mock.patch("gitstack.publish.checked", return_value=Result(0, payload, "")):
            with self.assertRaises(GitStackError) as raised:
                _find_open_pr("owner/repo", "feature", Path("/tmp/repo"))
        self.assertEqual(raised.exception.code, "pull_request_mismatch")

    def test_open_pr_lookup_rejects_ambiguous_matches(self) -> None:
        payload = json.dumps([{"number": 1}, {"number": 2}])
        with mock.patch("gitstack.publish.checked", return_value=Result(0, payload, "")):
            with self.assertRaises(GitStackError) as raised:
                _find_open_pr("owner/repo", "feature", Path("/tmp/repo"))
        self.assertEqual(raised.exception.code, "ambiguous_pull_request")


if __name__ == "__main__":
    unittest.main()
