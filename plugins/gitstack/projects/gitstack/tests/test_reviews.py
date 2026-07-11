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
from gitstack import reviews as cli

class ReviewsContractTests(unittest.TestCase):
    def test_version(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(["--version"])
        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), "1.0.1")

    def test_json_doctor_shape(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.main(["--json", "doctor"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["version"], "1.0.1")
        self.assertIn("git", payload["checks"])
        self.assertIn("gh", payload["checks"])

    def test_positive_int(self) -> None:
        self.assertEqual(cli.positive_int("12", "pr"), 12)
        with self.assertRaises(cli.ReviewError):
            cli.positive_int("0", "pr")

    def test_comment_dry_run_json_shape(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(
                [
                    "--json",
                    "comment",
                    "--repo",
                    "owner/repo",
                    "--pr",
                    "12",
                    "--body",
                    "@codex please review this PR.",
                    "--dry-run",
                ]
            )
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["version"], "1.0.1")
        self.assertEqual(payload["command"], ["comment"])
        self.assertEqual(payload["data"]["repo"], "owner/repo")
        self.assertEqual(payload["data"]["pr"], 12)
        self.assertEqual(payload["data"]["action"]["status"], "dry-run")
        self.assertEqual(payload["data"]["action"]["type"], "conversation_comment")

    def test_read_body_from_file(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as handle:
            handle.write("hello from file")
            handle.flush()
            self.assertEqual(cli.read_body(None, handle.name), "hello from file")

    def test_read_body_rejects_ambiguous_input(self) -> None:
        with self.assertRaises(cli.ReviewError):
            cli.read_body("body", "message.md")

    def test_read_body_rejects_invalid_utf8(self) -> None:
        with tempfile.NamedTemporaryFile("wb") as handle:
            handle.write(b"\xff")
            handle.flush()
            with self.assertRaises(cli.ReviewError) as raised:
                cli.read_body(None, handle.name, option_prefix="reply-body")

        self.assertEqual(raised.exception.code, "invalid_arguments")

    def test_address_reads_reply_body_from_file(self) -> None:
        entry = {
            "index": 1,
            "type": "review_comment",
            "comment_id": 123456,
            "author": "reviewer",
            "updated": "2026-07-10T00:00:00Z",
            "body": "Please clarify this.",
            "body_preview": "Please clarify this.",
            "path": "src/example.py",
            "line": 12,
            "start_line": 12,
            "is_resolved": False,
            "is_outdated": False,
        }
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as handle:
            handle.write("Addressed in the latest revision.")
            handle.flush()
            stdout = io.StringIO()
            with mock.patch.object(cli, "collect_entries", return_value=[entry]):
                with contextlib.redirect_stdout(stdout):
                    code = cli.main(
                        [
                            "--json",
                            "address",
                            "--repo",
                            "owner/repo",
                            "--pr",
                            "12",
                            "--comment-ids",
                            "123456",
                            "--reply-body-file",
                            handle.name,
                            "--dry-run",
                        ]
                    )

        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["version"], "1.0.1")
        self.assertEqual(payload["data"]["actions"][0]["status"], "dry-run")

    def test_review_reply_uses_pr_scoped_endpoint(self) -> None:
        entry = {"type": "review_comment", "comment_id": 123456}
        result = mock.Mock(returncode=0, stdout="", stderr="")

        with mock.patch.object(cli, "run_gh", return_value=result) as run_gh:
            actions = cli.post_replies("owner/repo", 12, [entry], "Fixed.", False)

        run_gh.assert_called_once_with(
            [
                "api",
                "-X",
                "POST",
                "repos/owner/repo/pulls/12/comments/123456/replies",
                "-H",
                "Accept: application/vnd.github+json",
                "-f",
                "body=Fixed.",
            ]
        )
        self.assertEqual(actions[0]["status"], "replied")

    def test_review_reply_preserves_api_failure(self) -> None:
        entry = {"type": "review_comment", "comment_id": 123456}
        result = mock.Mock(returncode=1, stdout="", stderr="HTTP 404")

        with mock.patch.object(cli, "run_gh", return_value=result):
            actions = cli.post_replies("owner/repo", 12, [entry], "Fixed.", False)

        self.assertEqual(actions[0]["status"], "error")
        self.assertEqual(actions[0]["message"], "HTTP 404")

    def test_address_rejects_inline_and_file_reply_bodies_together(self) -> None:
        entry = {
            "index": 1,
            "type": "review_comment",
            "comment_id": 123456,
        }
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as handle:
            handle.write("file body")
            handle.flush()
            stdout = io.StringIO()
            with mock.patch.object(cli, "collect_entries", return_value=[entry]):
                with contextlib.redirect_stdout(stdout):
                    code = cli.main(
                        [
                            "--json",
                            "address",
                            "--repo",
                            "owner/repo",
                            "--pr",
                            "12",
                            "--comment-ids",
                            "123456",
                            "--reply-body",
                            "inline body",
                            "--reply-body-file",
                            handle.name,
                            "--dry-run",
                        ]
                    )

        self.assertEqual(code, 64)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["error"]["code"], "invalid_arguments")


if __name__ == "__main__":
    unittest.main()
