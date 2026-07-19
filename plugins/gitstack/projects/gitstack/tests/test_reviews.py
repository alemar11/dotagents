from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gitstack import reviews as cli
from gitstack.common import GitStackError, Result
from gitstack.provider_text import ProviderText

class ReviewsContractTests(unittest.TestCase):
    HOSTILE = "`ticks` $(command) ${HOME} $PATH 'single' \"double\"\n-leading\nUnicode ✓ 🚀"

    def provider_body(self) -> ProviderText:
        return ProviderText("body", self.HOSTILE.encode("utf-8"), self.HOSTILE)

    def frozen_clock(self):
        patcher = mock.patch.object(cli, "datetime")
        clock = patcher.start()
        self.addCleanup(patcher.stop)
        clock.now.return_value = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        return clock

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
        self.assertEqual(stdout.getvalue().strip(), "5.0.0")

    def test_json_doctor_shape(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.main(["--json", "doctor"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["version"], "5.0.0")
        self.assertIn("git", payload["checks"])
        self.assertIn("gh", payload["checks"])

    def test_review_owner_documents_terminal_state_and_shared_operations(self) -> None:
        plugin_root = Path(__file__).resolve().parents[3]
        options = (plugin_root / "references" / "options.md").read_text(
            encoding="utf-8"
        )
        review_contract = (
            plugin_root
            / "skills"
            / "github-review-threads"
            / "references"
            / "script-summary.md"
        ).read_text(encoding="utf-8")
        for state in (
            "not-requested",
            "acknowledged",
            "pending",
            "clean",
            "findings",
            "stale",
            "error",
        ):
            with self.subTest(state=state):
                self.assertIn(f"`{state}`", review_contract)
        self.assertIn(
            "`inspect`, `check`, `wait`, `request`, `comment`, `edit-comment`, `submit-review`, `reply`, `resolve`",
            options,
        )

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
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as handle:
            handle.write("`ticks` $(command) $HOME 'quotes' \"double\"\nUnicode ✓")
            handle.flush()
            stdout = io.StringIO()
            with mock.patch.object(cli, "_verify_pr_target", return_value={"number": 12}), \
                 mock.patch.object(cli, "require_worktree", return_value=None), \
                 contextlib.redirect_stdout(stdout):
                code = cli.main(
                    [
                        "--json", "comment", "--repo", "owner/repo", "--pr", "12",
                        "--body-file", handle.name, "--dry-run",
                    ]
                )
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["version"], "5.0.0")
        self.assertEqual(payload["command"], ["comment"])
        self.assertEqual(payload["data"]["repo"], "owner/repo")
        self.assertEqual(payload["data"]["pr"], 12)
        self.assertEqual(payload["data"]["action"]["status"], "dry-run")
        rendered = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn("ticks", rendered)
        self.assertNotIn("command", rendered.replace('"command": ["comment"]', ""))

    def test_address_is_read_only(self) -> None:
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
        stdout = io.StringIO()
        with mock.patch.object(cli, "collect_entries", return_value=[entry]), contextlib.redirect_stdout(stdout):
            code = cli.main(["--json", "address", "--repo", "owner/repo", "--pr", "12"])
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["version"], "5.0.0")
        self.assertNotIn("actions", payload["data"])

    def test_reply_dry_run_is_one_target_and_file_backed(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as handle:
            handle.write("Fixed `x` and $(not-run).")
            handle.flush()
            stdout = io.StringIO()
            parent = {"id": 123456, "pull_request_url": "https://api.github.com/repos/owner/repo/pulls/12"}
            with mock.patch.object(cli, "_api_object", return_value=parent), \
                 mock.patch.object(cli, "require_worktree", return_value=None), \
                 contextlib.redirect_stdout(stdout):
                code = cli.main([
                    "--json", "reply", "--repo", "owner/repo", "--pr", "12",
                    "--comment-id", "123456", "--body-file", handle.name, "--dry-run",
                ])
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        action = payload["data"]["action"]
        self.assertEqual(action["target"]["parent_id"], 123456)
        self.assertEqual(action["transport"]["endpoint"], "repos/owner/repo/pulls/12/comments/123456/replies")
        self.assertNotIn("not-run", json.dumps(payload))

    def test_inline_provider_text_flags_are_rejected(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        hostile = "`unsafe` $(command) $HOME"
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = cli.main([
                "--json", "comment", "--repo", "owner/repo", "--pr", "12", "--body", hostile,
            ])
        self.assertEqual(code, 64)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["error"]["code"], "invalid_arguments")
        self.assertNotIn(hostile, stdout.getvalue() + stderr.getvalue())

    def test_malformed_comment_response_recovers_from_one_unique_read_back(self) -> None:
        self.frozen_clock()
        body = self.provider_body()
        item = {
            "id": 41, "html_url": "https://github.com/owner/repo/issues/12#issuecomment-41",
            "issue_url": "https://api.github.com/repos/owner/repo/issues/12",
            "user": {"login": "agent"}, "body": body.text,
            "created_at": "2026-07-20T12:00:00Z",
        }
        unprovable_responses = (
            "not-json",
            "[]",
            json.dumps({"body": body.text}),
            json.dumps({**item, "user": "agent"}),
            json.dumps({**item, "issue_url": "https://api.github.com/repos/owner/other/issues/12"}),
            json.dumps({**item, "body": "different"}),
            json.dumps({**item, "body": "\ud800"}),
        )
        for response in unprovable_responses:
            with self.subTest(response=response[:20]), \
                 mock.patch.object(cli, "_verify_pr_target", return_value={"number": 12}), \
                 mock.patch.object(cli, "require_worktree", return_value=None), \
                 mock.patch.object(cli, "_viewer_login", return_value="agent"), \
                 mock.patch.object(cli, "api_request", return_value=Result(0, response, "")) as mutation, \
                 mock.patch.object(cli, "gh_api_paginated_list", return_value=[item]) as read_back:
                action = cli.post_conversation_comment("owner/repo", 12, body, False, None)

            self.assertEqual(action["status"], "recovered")
            self.assertEqual(action["id"], 41)
            mutation.assert_called_once()
            read_back.assert_called_once()

    def test_malformed_comment_response_with_missing_read_back_is_ambiguous_and_redacted(self) -> None:
        self.frozen_clock()
        body = self.provider_body()
        with mock.patch.object(cli, "_verify_pr_target", return_value={"number": 12}), \
             mock.patch.object(cli, "require_worktree", return_value=None), \
             mock.patch.object(cli, "_viewer_login", return_value="agent"), \
             mock.patch.object(cli, "api_request", return_value=Result(0, "not-json", "")), \
             mock.patch.object(cli, "gh_api_paginated_list", return_value=[]) as read_back, \
             self.assertRaises(cli.ReviewError) as raised:
            cli.post_conversation_comment("owner/repo", 12, body, False, None)

        self.assertEqual(raised.exception.code, "provider_write_ambiguous")
        self.assertEqual(raised.exception.details["response"]["code"], "provider_response_invalid")
        self.assertNotIn(body.text, json.dumps(raised.exception.details, ensure_ascii=False))
        read_back.assert_called_once()

    def test_recovered_comment_preserves_identity_when_worktree_post_check_fails(self) -> None:
        self.frozen_clock()
        body = self.provider_body()
        item = {
            "id": 42, "html_url": "https://github.com/owner/repo/issues/12#issuecomment-42",
            "issue_url": "https://api.github.com/repos/owner/repo/issues/12",
            "user": {"login": "agent"}, "body": body.text,
            "created_at": "2026-07-20T12:00:00Z",
        }
        before = {"fingerprint": "a" * 64}
        drift = GitStackError(
            "The provider mutation completed, but the Git worktree fingerprint changed.",
            code="provider_write_partial_success", exit_code=65,
        )
        with mock.patch.object(cli, "_verify_pr_target", return_value={"number": 12}), \
             mock.patch.object(cli, "require_worktree", return_value=before), \
             mock.patch.object(cli, "_viewer_login", return_value="agent"), \
             mock.patch.object(cli, "api_request", return_value=Result(0, "not-json", "")), \
             mock.patch.object(cli, "gh_api_paginated_list", return_value=[item]), \
             mock.patch.object(cli, "verify_worktree_unchanged", side_effect=drift), \
             self.assertRaises(cli.ReviewError) as raised:
            cli.post_conversation_comment("owner/repo", 12, body, False, before["fingerprint"])

        self.assertEqual(raised.exception.code, "provider_write_partial_success")
        self.assertEqual(raised.exception.details["action"]["status"], "recovered")
        self.assertEqual(raised.exception.details["action"]["id"], 42)
        self.assertNotIn(body.text, json.dumps(raised.exception.details, ensure_ascii=False))

    def test_malformed_reply_response_recovers_and_duplicate_read_back_is_ambiguous(self) -> None:
        self.frozen_clock()
        body = self.provider_body()
        parent = {"id": 55, "pull_request_url": "https://api.github.com/repos/owner/repo/pulls/12"}
        item = {
            "id": 56, "html_url": "https://github.com/owner/repo/pull/12#discussion_r56",
            "pull_request_url": "https://api.github.com/repos/owner/repo/pulls/12",
            "in_reply_to_id": 55, "user": {"login": "agent"}, "body": body.text,
            "created_at": "2026-07-20T12:00:00Z",
        }
        common = [
            mock.patch.object(cli, "_api_object", return_value=parent),
            mock.patch.object(cli, "require_worktree", return_value=None),
            mock.patch.object(cli, "_viewer_login", return_value="agent"),
            mock.patch.object(cli, "api_request", return_value=Result(0, "[]", "")),
        ]
        with common[0], common[1], common[2], common[3], \
             mock.patch.object(cli, "gh_api_paginated_list", return_value=[item]) as read_back:
            action = cli.reply_to_review_comment("owner/repo", 12, 55, body, False, None)
        self.assertEqual(action["status"], "recovered")
        read_back.assert_called_once()

        with mock.patch.object(cli, "_api_object", return_value=parent), \
             mock.patch.object(cli, "require_worktree", return_value=None), \
             mock.patch.object(cli, "_viewer_login", return_value="agent"), \
             mock.patch.object(cli, "api_request", return_value=Result(0, "[]", "")), \
             mock.patch.object(cli, "gh_api_paginated_list", return_value=[item, item]) as duplicate, \
             self.assertRaises(cli.ReviewError) as raised:
            cli.reply_to_review_comment("owner/repo", 12, 55, body, False, None)
        self.assertEqual(raised.exception.code, "provider_write_ambiguous")
        duplicate.assert_called_once()

    def test_malformed_edit_response_recovers_and_mismatched_read_back_is_ambiguous(self) -> None:
        body = self.provider_body()
        current = {
            "id": 61, "html_url": "https://github.com/owner/repo/issues/12#issuecomment-61",
            "issue_url": "https://api.github.com/repos/owner/repo/issues/12",
            "user": {"login": "agent"}, "body": "old",
        }
        updated = {**current, "body": body.text}
        with mock.patch.object(cli, "_api_object", side_effect=[current, updated]) as read_object, \
             mock.patch.object(cli, "require_worktree", return_value=None), \
             mock.patch.object(cli, "_viewer_login", return_value="agent"), \
             mock.patch.object(cli, "api_request", return_value=Result(0, "not-json", "")):
            action = cli.edit_comment("owner/repo", 12, 61, "conversation", body, False, None)
        self.assertEqual(action["status"], "recovered")
        self.assertEqual(read_object.call_count, 2)

        mismatched = {**updated, "id": 62}
        with mock.patch.object(cli, "_api_object", side_effect=[current, mismatched]) as read_object, \
             mock.patch.object(cli, "require_worktree", return_value=None), \
             mock.patch.object(cli, "_viewer_login", return_value="agent"), \
             mock.patch.object(cli, "api_request", return_value=Result(0, "not-json", "")), \
             self.assertRaises(cli.ReviewError) as raised:
            cli.edit_comment("owner/repo", 12, 61, "conversation", body, False, None)
        self.assertEqual(raised.exception.code, "provider_write_ambiguous")
        self.assertNotIn(body.text, json.dumps(raised.exception.details, ensure_ascii=False))
        self.assertEqual(read_object.call_count, 2)

    def test_malformed_review_response_recovers_and_duplicate_read_back_is_ambiguous(self) -> None:
        self.frozen_clock()
        body = self.provider_body()
        head = "a" * 40
        review = {
            "id": 71, "html_url": "https://github.com/owner/repo/pull/12#pullrequestreview-71",
            "pull_request_url": "https://api.github.com/repos/owner/repo/pulls/12",
            "user": {"login": "agent"}, "state": "APPROVED", "body": body.text,
            "commit_id": head, "submitted_at": "2026-07-20T12:00:00Z",
        }
        with mock.patch.object(cli, "_verify_pr_target", return_value={"number": 12, "head": {"sha": head}}), \
             mock.patch.object(cli, "require_worktree", return_value=None), \
             mock.patch.object(cli, "_viewer_login", return_value="agent"), \
             mock.patch.object(cli, "api_request", return_value=Result(0, "not-json", "")), \
             mock.patch.object(cli, "gh_api_paginated_list", return_value=[review]) as read_back:
            action = cli.submit_review("owner/repo", 12, "approve", body, False, None)
        self.assertEqual(action["status"], "recovered")
        read_back.assert_called_once()

        with mock.patch.object(cli, "_verify_pr_target", return_value={"number": 12, "head": {"sha": head}}), \
             mock.patch.object(cli, "require_worktree", return_value=None), \
             mock.patch.object(cli, "_viewer_login", return_value="agent"), \
             mock.patch.object(cli, "api_request", return_value=Result(0, "not-json", "")), \
             mock.patch.object(cli, "gh_api_paginated_list", return_value=[review, review]) as duplicate, \
             self.assertRaises(cli.ReviewError) as raised:
            cli.submit_review("owner/repo", 12, "approve", body, False, None)
        self.assertEqual(raised.exception.code, "provider_write_ambiguous")
        duplicate.assert_called_once()

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

    def test_check_codex_detects_terminal_clean_conversation_comment(self) -> None:
        head = "f5dc037d8d3978df85a6e59f68ebad38e75953b0"
        request = {
            "id": 99,
            "body": f"@codex review {head[:8]}",
            "created_at": "2026-07-15T13:00:00Z",
        }
        result = {
            "id": 100,
            "user": {"login": "chatgpt-codex-connector[bot]"},
            "body": (
                "Codex Review: Didn't find any major issues. Keep it up!\n\n"
                "**Reviewed commit:** `f5dc037d8d`"
            ),
            "created_at": "2026-07-15T13:12:20Z",
        }
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(comments=[request, result]),
        ):
            payload = cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(payload["review_state"], "clean")
        self.assertEqual(payload["evidence"]["kind"], "provider-comment")
        self.assertEqual(payload["evidence"]["object_id"], 100)
        self.assertEqual(payload["terminal_comment"]["reviewed_head"], "f5dc037d8d")
        self.assertRegex(payload["observation_fingerprint"], r"^[0-9a-f]{64}$")

    def test_check_codex_detects_terminal_findings_conversation_comment(self) -> None:
        head = "a" * 40
        request = {
            "id": 99,
            "body": f"@codex review {head[:8]}",
            "created_at": "2026-07-15T13:00:00Z",
        }
        result = {
            "id": 100,
            "user": {"login": "chatgpt-codex-connector[bot]"},
            "body": f"Codex Review: Found issues to address.\n\n**Reviewed commit:** `{head[:10]}`",
            "created_at": "2026-07-15T13:01:00Z",
        }
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(comments=[request, result]),
        ):
            payload = cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(payload["review_state"], "findings")
        self.assertEqual(payload["evidence"]["kind"], "provider-comment")

    def test_check_codex_detects_terminal_error_conversation_comment(self) -> None:
        head = "a" * 40
        request = {
            "id": 99,
            "body": f"@codex review {head[:8]}",
            "created_at": "2026-07-15T13:00:00Z",
        }
        result = {
            "id": 100,
            "user": {"login": "chatgpt-codex-connector[bot]"},
            "body": f"Codex Review: Review failed because the service encountered an error.\n\n**Reviewed commit:** `{head[:10]}`",
            "created_at": "2026-07-15T13:01:00Z",
        }
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(comments=[request, result]),
        ):
            payload = cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(payload["review_state"], "error")
        self.assertEqual(payload["evidence"]["kind"], "provider-comment")

    def test_check_codex_ignores_authenticated_nonterminal_status_comment(self) -> None:
        head = "a" * 40
        request = {
            "id": 99,
            "body": f"@codex review {head[:8]}",
            "created_at": "2026-07-15T13:00:00Z",
        }
        status = {
            "id": 100,
            "user": {"login": "chatgpt-codex-connector[bot]"},
            "body": f"Codex Review: Review is still in progress.\n\n**Reviewed commit:** `{head[:10]}`",
            "created_at": "2026-07-15T13:01:00Z",
        }
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(comments=[request, status]),
        ):
            payload = cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(payload["review_state"], "pending")
        self.assertEqual(payload["terminal_comment"]["count"], 0)

    def test_check_codex_rejects_terminal_result_after_overlapping_same_head_requests(self) -> None:
        head = "a" * 40
        first_request = {
            "id": 98,
            "body": f"@codex review {head[:8]}",
            "created_at": "2026-07-15T13:00:00Z",
        }
        second_request = {
            "id": 99,
            "body": f"@codex review {head[:8]}",
            "created_at": "2026-07-15T13:01:00Z",
        }
        result = {
            "id": 100,
            "user": {"login": "chatgpt-codex-connector[bot]"},
            "body": f"Codex Review: No findings.\n\n**Reviewed commit:** `{head[:10]}`",
            "created_at": "2026-07-15T13:02:00Z",
        }
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(
                comments=[first_request, second_request, result]
            ),
        ):
            with self.assertRaises(cli.ReviewError) as raised:
                cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(raised.exception.code, "ambiguous_review_evidence")

    def test_check_codex_allows_sequential_completed_same_head_requests(self) -> None:
        head = "a" * 40
        first_request = {
            "id": 97,
            "body": f"@codex review {head[:8]}",
            "created_at": "2026-07-15T13:00:00Z",
        }
        first_result = {
            "id": 98,
            "user": {"login": "chatgpt-codex-connector[bot]"},
            "body": f"Codex Review: No findings.\n\n**Reviewed commit:** `{head[:10]}`",
            "created_at": "2026-07-15T13:00:30Z",
        }
        second_request = {
            "id": 99,
            "body": f"@codex review {head[:8]}",
            "created_at": "2026-07-15T13:01:00Z",
        }
        second_result = {
            "id": 100,
            "user": {"login": "chatgpt-codex-connector[bot]"},
            "body": f"Codex Review: No findings.\n\n**Reviewed commit:** `{head[:10]}`",
            "created_at": "2026-07-15T13:02:00Z",
        }
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(
                comments=[
                    first_request,
                    first_result,
                    second_request,
                    second_result,
                ]
            ),
        ):
            payload = cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(payload["review_state"], "clean")
        self.assertEqual(payload["terminal_comment"]["count"], 1)
        self.assertEqual(payload["terminal_comment"]["latest_id"], 100)

    def test_check_codex_keeps_new_request_pending_after_older_formal_review(self) -> None:
        head = "a" * 40
        old_review = {
            "id": 97,
            "user": {"login": "chatgpt-codex-connector[bot]"},
            "commit_id": head,
            "submitted_at": "2026-07-15T13:00:30Z",
        }
        new_request = {
            "id": 99,
            "body": f"@codex review {head[:8]}",
            "created_at": "2026-07-15T13:01:00Z",
        }
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(
                reviews=[old_review],
                comments=[new_request],
            ),
        ):
            payload = cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(payload["review_state"], "pending")
        self.assertEqual(payload["review"]["count"], 0)
        self.assertEqual(payload["review"]["latest_id"], None)

    def test_check_codex_ignores_terminal_comment_before_latest_request(self) -> None:
        head = "a" * 40
        result = {
            "id": 98,
            "user": {"login": "chatgpt-codex-connector[bot]"},
            "body": f"Codex Review: No findings.\n\n**Reviewed commit:** `{head[:10]}`",
            "created_at": "2026-07-15T12:59:00Z",
        }
        request = {
            "id": 99,
            "body": f"@codex review {head[:8]}",
            "created_at": "2026-07-15T13:00:00Z",
        }
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(comments=[result, request]),
        ):
            payload = cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(payload["review_state"], "pending")
        self.assertEqual(payload["terminal_comment"]["count"], 0)

    def test_check_codex_ignores_spoofed_terminal_comment(self) -> None:
        head = "a" * 40
        request = {
            "id": 99,
            "body": f"@codex review {head[:8]}",
            "created_at": "2026-07-15T13:00:00Z",
        }
        spoof = {
            "id": 100,
            "user": {"login": "human-reviewer"},
            "body": f"Codex Review: No findings.\n\n**Reviewed commit:** `{head[:10]}`",
            "created_at": "2026-07-15T13:01:00Z",
        }
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(comments=[request, spoof]),
        ):
            payload = cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(payload["review_state"], "pending")

    def test_check_codex_rejects_conflicting_terminal_evidence(self) -> None:
        head = "a" * 40
        request = {
            "id": 99,
            "body": f"@codex review {head[:8]}",
            "created_at": "2026-07-15T13:00:00Z",
        }
        review = {
            "id": 7,
            "user": {"login": "chatgpt-codex-connector[bot]"},
            "commit_id": head,
            "submitted_at": "2026-07-15T13:01:00Z",
        }
        result = {
            "id": 100,
            "user": {"login": "chatgpt-codex-connector[bot]"},
            "body": f"Codex Review: Found issues to address.\n\n**Reviewed commit:** `{head[:10]}`",
            "created_at": "2026-07-15T13:02:00Z",
        }
        with mock.patch.object(cli, "gh_json", return_value={"head": {"sha": head}}), mock.patch.object(
            cli,
            "gh_api_paginated_list",
            side_effect=self.automated_review_api(reviews=[review], comments=[request, result]),
        ):
            with self.assertRaises(cli.ReviewError) as raised:
                cli.check_automated_review("owner/repo", 12, "codex", head)

        self.assertEqual(raised.exception.code, "ambiguous_review_evidence")

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

    def test_wait_counts_only_changed_observations_as_transitions(self) -> None:
        pending = {
            "review_state": "pending",
            "repo": "owner/repo",
            "pr": 12,
            "observation_fingerprint": "a" * 64,
        }
        clean = {
            "review_state": "clean",
            "repo": "owner/repo",
            "pr": 12,
            "observation_fingerprint": "b" * 64,
        }
        with mock.patch.object(
            cli,
            "check_automated_review",
            side_effect=[pending, pending, clean],
        ), mock.patch.object(
            cli.time,
            "monotonic",
            side_effect=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ), mock.patch.object(cli.time, "sleep") as sleep:
            payload, exit_code = cli.wait_for_automated_review(
                "owner/repo", 12, "codex", None, 10, 1, 2
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["attempts"], 3)
        self.assertEqual(payload["state_transitions"], 2)
        self.assertEqual(payload["unchanged_attempts"], 1)
        self.assertEqual(sleep.call_count, 2)

    def test_wait_stops_immediately_on_terminal_provider_error(self) -> None:
        error = {
            "review_state": "error",
            "repo": "owner/repo",
            "pr": 12,
            "observation_fingerprint": "a" * 64,
        }
        with mock.patch.object(
            cli,
            "check_automated_review",
            return_value=error,
        ), mock.patch.object(
            cli.time,
            "monotonic",
            side_effect=[0.0, 0.0],
        ), mock.patch.object(cli.time, "sleep") as sleep:
            payload, exit_code = cli.wait_for_automated_review(
                "owner/repo", 12, "codex", None, 10, 1, 2
            )

        self.assertEqual(exit_code, 4)
        self.assertEqual(payload["attempts"], 1)
        sleep.assert_not_called()

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
