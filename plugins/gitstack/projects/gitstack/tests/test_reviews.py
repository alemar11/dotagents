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
    def automated_review_api(self, *, reviews=None, inline=None, comments=None, reactions=None):
        payloads = {
            "pulls/12/reviews": reviews or [],
            "pulls/12/comments": inline or [],
            "issues/12/comments": comments or [],
            "issues/comments/99/reactions": reactions or [],
        }

        def read(endpoint: str):
            for suffix, payload in payloads.items():
                if endpoint.endswith(suffix):
                    return payload
            self.fail(f"Unexpected endpoint: {endpoint}")

        return read

    def test_version(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(["--version"])
        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), "2.0.0")

    def test_json_doctor_shape(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.main(["--json", "doctor"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["version"], "2.0.0")
        self.assertIn("git", payload["checks"])
        self.assertIn("gh", payload["checks"])

    def test_positive_int(self) -> None:
        self.assertEqual(cli.positive_int("12", "pr"), 12)
        with self.assertRaises(cli.ReviewError):
            cli.positive_int("0", "pr")

    def test_duration_seconds(self) -> None:
        self.assertEqual(cli.duration_seconds("15m", "timeout"), 900)
        self.assertEqual(cli.duration_seconds("30s", "interval"), 30)
        with self.assertRaises(cli.ReviewError):
            cli.duration_seconds("0s", "timeout")

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
        self.assertEqual(payload["version"], "2.0.0")
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
        self.assertEqual(payload["version"], "2.0.0")
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

    def test_check_codex_reports_findings_for_expected_head(self) -> None:
        head = "a" * 40
        review = {"id": 7, "user": {"login": "chatgpt-codex-connector[bot]"}, "commit_id": head, "submitted_at": "2026-07-11T12:02:00Z"}
        finding = {"id": 8, "user": {"login": "chatgpt-codex-connector[bot]"}, "commit_id": head}
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(reviews=[review], inline=[finding]),
        ):
            payload = cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(payload["review_state"], "findings")
        self.assertEqual(payload["review"]["findings"], 1)

    def test_check_codex_reports_acknowledged_request(self) -> None:
        head = "b" * 40
        request = {"id": 99, "body": f"@codex review {head[:8]}", "created_at": "2026-07-11T12:01:00Z"}
        eyes = [{"content": "eyes", "user": {"login": "chatgpt-codex-connector[bot]"}}]
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(comments=[request], reactions=eyes),
        ):
            payload = cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(payload["review_state"], "acknowledged")
        self.assertTrue(payload["request"]["acknowledged"])

    def test_check_codex_emits_canonical_not_requested_state(self) -> None:
        head = "c" * 40
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(),
        ):
            payload = cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(payload["review_state"], "not-requested")
        self.assertNotIn("not_requested", json.dumps(payload))

    def test_check_codex_rejects_stale_review(self) -> None:
        head = "c" * 40
        old_head = "d" * 40
        old_review = {"id": 7, "user": {"login": "chatgpt-codex-connector[bot]"}, "commit_id": old_head}
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(reviews=[old_review]),
        ):
            payload = cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(payload["review_state"], "stale")

    def test_check_never_marks_a_non_current_head_clean(self) -> None:
        current_head = "e" * 40
        expected_head = "f" * 40
        old_review = {"id": 7, "user": {"login": "chatgpt-codex-connector[bot]"}, "commit_id": expected_head}
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": current_head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(reviews=[old_review]),
        ):
            payload = cli.check_automated_review("owner/repo", 12, "codex", expected_head)

        self.assertEqual(payload["review_state"], "stale")
        self.assertFalse(payload["head_is_current"])

    def test_check_rejects_ambiguous_head_prefix(self) -> None:
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": "a" * 40}}):
            with self.assertRaises(cli.ReviewError) as raised:
                cli.check_automated_review("owner/repo", 12, "codex", "a")

        self.assertEqual(raised.exception.code, "invalid_arguments")

    def test_plain_review_request_is_not_bound_to_a_head(self) -> None:
        head = "b" * 40
        request = {"id": 99, "body": "@codex review", "created_at": "2026-07-11T12:01:00Z"}
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(comments=[request]),
        ):
            payload = cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(payload["review_state"], "stale")

    def test_review_request_rejects_different_sha_with_same_prefix(self) -> None:
        head = "abcdef0" + "1" * 33
        other_head = "abcdef0" + "2" * 33
        request = {"body": f"@codex review {other_head}"}

        self.assertFalse(cli.review_request_matches(request, "codex", head))

    def test_review_request_accepts_bounded_sha_prefix_after_command(self) -> None:
        head = "abcdef0" + "1" * 33
        request = {"body": "@codex review\nPlease check updated head abcdef01."}

        self.assertTrue(cli.review_request_matches(request, "codex", head))

    def test_wait_times_out_pending_review(self) -> None:
        pending = {"review_state": "pending", "repo": "owner/repo", "pr": 12}
        with mock.patch.object(cli, "check_automated_review", return_value=pending), mock.patch.object(
            cli.time, "monotonic", side_effect=[0.0, 0.0, 2.0]
        ), mock.patch.object(cli.time, "sleep"):
            payload, exit_code = cli.wait_for_automated_review("owner/repo", 12, "codex", None, 1, 1, 1)

        self.assertEqual(exit_code, 124)
        self.assertTrue(payload["timed_out"])

    def test_check_maps_api_failures_to_exit_four(self) -> None:
        stdout = io.StringIO()
        failure = cli.ReviewError("API unavailable")
        with mock.patch.object(cli, "check_automated_review", side_effect=failure), contextlib.redirect_stdout(stdout):
            code = cli.main(
                ["--json", "check", "--provider", "codex", "--repo", "owner/repo", "--pr", "12"]
            )

        self.assertEqual(code, 4)
        self.assertEqual(json.loads(stdout.getvalue())["error"]["code"], "api_error")


if __name__ == "__main__":
    unittest.main()
