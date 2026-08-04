from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from g import cli
from g.common import Result
from g.delivery_status import DELIVERY_QUERY, _classify, _read_pull_request, _read_rules, inspect_delivery_status


HEAD = "a" * 40


def pull_request(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "number": 77,
        "url": "https://github.com/owner/repo/pull/77",
        "state": "OPEN",
        "isDraft": False,
        "baseRefName": "main",
        "headRefName": "feature",
        "headRefOid": HEAD,
        "mergeable": "MERGEABLE",
        "mergeStateStatus": "CLEAN",
        "reviewDecision": None,
        "statusCheckRollup": {"state": "SUCCESS", "contexts": []},
        "reviewThreads": [],
        "closingIssuesReferences": [],
        "autoMergeRequest": None,
        "mergeQueueEntry": None,
    }
    value.update(overrides)
    return value


class DeliveryStatusClassificationTests(unittest.TestCase):
    def classify(self, pr: dict[str, object], rules: list[dict[str, object]] | None = None) -> dict[str, object]:
        return _classify(
            pr,
            rules or [],
            None,
            expected_head=HEAD,
            provider_complete=True,
        )

    def test_clean_mergeable_pull_request_is_ready(self) -> None:
        result = self.classify(pull_request())
        self.assertEqual(result["disposition"], "ready")
        self.assertEqual(result["blockers"], [])

    def test_update_restriction_is_ready_with_manual_action(self) -> None:
        rules = [
            {"type": "update", "ruleset_id": 42},
            {
                "type": "pull_request",
                "ruleset_id": 42,
                "parameters": {
                    "required_approving_review_count": 0,
                    "require_code_owner_review": False,
                    "require_last_push_approval": False,
                    "required_review_thread_resolution": False,
                },
            },
            {"type": "copilot_code_review", "ruleset_id": 42},
            {"type": "deletion", "ruleset_id": 42},
            {"type": "non_fast_forward", "ruleset_id": 42},
        ]
        result = self.classify(pull_request(mergeStateStatus="BLOCKED"), rules)
        self.assertEqual(result["disposition"], "ready-with-manual-action")
        self.assertEqual(result["blockers"], [])

    def test_auto_merge_and_queue_are_not_delivery_blockers(self) -> None:
        pr = pull_request(
            autoMergeRequest={"enabledAt": "2026-08-04T12:00:00Z", "mergeMethod": "SQUASH"},
            mergeQueueEntry={"state": "QUEUED"},
        )
        self.assertEqual(self.classify(pr)["disposition"], "ready")

    def test_required_check_states_are_typed(self) -> None:
        rules = [{"type": "required_status_checks", "parameters": {"required_status_checks": [{"context": "build"}]}}]
        pending_pr = pull_request(
            statusCheckRollup={
                "state": "PENDING",
                "contexts": [{"__typename": "CheckRun", "name": "build", "status": "IN_PROGRESS", "conclusion": None}],
            }
        )
        failing_pr = pull_request(
            statusCheckRollup={
                "state": "FAILURE",
                "contexts": [{"__typename": "CheckRun", "name": "build", "status": "COMPLETED", "conclusion": "FAILURE"}],
            }
        )
        self.assertEqual(self.classify(pending_pr, rules)["disposition"], "pending")
        failing = self.classify(failing_pr, rules)
        self.assertEqual(failing["disposition"], "blocked")
        self.assertIn("required-check-failing:build", failing["blockers"])

    def test_every_same_name_required_check_must_pass(self) -> None:
        rules = [{"type": "required_status_checks", "parameters": {"required_status_checks": [{"context": "build"}]}}]
        pr = pull_request(
            statusCheckRollup={
                "state": "FAILURE",
                "contexts": [
                    {"__typename": "CheckRun", "name": "build", "status": "COMPLETED", "conclusion": "SUCCESS"},
                    {"__typename": "StatusContext", "context": "build", "state": "FAILURE"},
                ],
            }
        )
        result = self.classify(pr, rules)
        self.assertEqual(result["disposition"], "blocked")
        self.assertIn("required-check-failing:build", result["blockers"])

    def test_required_check_source_must_match(self) -> None:
        rules = [
            {
                "type": "required_status_checks",
                "parameters": {"required_status_checks": [{"context": "build", "integration_id": 42}]},
            }
        ]
        pr = pull_request(
            statusCheckRollup={
                "state": "SUCCESS",
                "contexts": [
                    {
                        "__typename": "CheckRun",
                        "name": "build",
                        "status": "COMPLETED",
                        "conclusion": "SUCCESS",
                        "checkSuite": {"app": {"databaseId": 7}},
                    }
                ],
            }
        )
        result = self.classify(pr, rules)
        self.assertEqual(result["disposition"], "pending")
        self.assertIn("required-check-missing:build@42", result["pending"])

    def test_expected_commit_status_is_pending(self) -> None:
        rules = [{"type": "required_status_checks", "parameters": {"required_status_checks": [{"context": "build"}]}}]
        pr = pull_request(statusCheckRollup={"state": "PENDING", "contexts": [{"__typename": "StatusContext", "context": "build", "state": "EXPECTED"}]})
        self.assertEqual(self.classify(pr, rules)["disposition"], "pending")

    def test_unstable_and_non_strict_behind_are_ready(self) -> None:
        self.assertEqual(self.classify(pull_request(mergeStateStatus="UNSTABLE"))["disposition"], "ready")
        self.assertEqual(self.classify(pull_request(mergeStateStatus="BEHIND"))["disposition"], "ready")

        strict = [
            {
                "type": "required_status_checks",
                "parameters": {"strict_required_status_checks_policy": True, "required_status_checks": []},
            }
        ]
        result = self.classify(pull_request(mergeStateStatus="BEHIND"), strict)
        self.assertEqual(result["disposition"], "blocked")
        self.assertIn("head-behind-required", result["blockers"])

    def test_draft_conflict_unknown_and_head_drift_fail_closed(self) -> None:
        self.assertEqual(self.classify(pull_request(isDraft=True))["disposition"], "blocked")
        self.assertEqual(self.classify(pull_request(mergeable="CONFLICTING", mergeStateStatus="DIRTY"))["disposition"], "conflicting")
        self.assertEqual(self.classify(pull_request(mergeable="UNKNOWN", mergeStateStatus="UNKNOWN"))["disposition"], "pending")
        drifted = self.classify(pull_request(headRefOid="b" * 40))
        self.assertEqual(drifted["disposition"], "blocked")
        self.assertIn("head-mismatch", drifted["blockers"])

    def test_unattributed_blocked_state_is_unknown(self) -> None:
        result = self.classify(pull_request(mergeStateStatus="BLOCKED"))
        self.assertEqual(result["disposition"], "unknown")
        self.assertIn("blocked-cause-unattributed", result["warnings"])

    def test_graphql_surface_is_read_only(self) -> None:
        self.assertIn("query DeliveryStatus", DELIVERY_QUERY)
        self.assertNotIn("mutation", DELIVERY_QUERY.lower())


class DeliveryStatusCommandTests(unittest.TestCase):
    def test_graphql_connections_paginate_without_duplicate_completed_surfaces(self) -> None:
        def page(checks: list[dict[str, object]], *, check_next: bool, check_cursor: str | None) -> Result:
            payload = {
                "data": {
                    "repository": {
                        "nameWithOwner": "owner/repo",
                        "pullRequest": {
                            **pull_request(),
                            "statusCheckRollup": {
                                "state": "SUCCESS",
                                "contexts": {
                                    "nodes": checks,
                                    "pageInfo": {"hasNextPage": check_next, "endCursor": check_cursor},
                                },
                            },
                            "reviewThreads": {
                                "nodes": [{"id": "thread-1", "isResolved": True}],
                                "pageInfo": {"hasNextPage": False, "endCursor": None},
                            },
                            "closingIssuesReferences": {
                                "nodes": [{"number": 76, "repository": {"nameWithOwner": "owner/repo"}}],
                                "pageInfo": {"hasNextPage": False, "endCursor": None},
                            },
                        },
                    }
                }
            }
            return Result(0, json.dumps(payload), "")

        first = page([{"__typename": "CheckRun", "name": "build"}], check_next=True, check_cursor="cursor-1")
        second = page([{"__typename": "CheckRun", "name": "test"}], check_next=False, check_cursor=None)
        with mock.patch("g.delivery_status.graphql_request", side_effect=[first, second]) as graphql:
            result, complete = _read_pull_request("owner", "repo", 77)

        self.assertTrue(complete)
        self.assertEqual(graphql.call_count, 2)
        self.assertEqual([item["name"] for item in result["pull_request"]["statusCheckRollup"]["contexts"]], ["build", "test"])
        self.assertEqual(len(result["pull_request"]["reviewThreads"]), 1)
        self.assertEqual(len(result["pull_request"]["closingIssuesReferences"]), 1)

    def test_active_branch_rules_are_paginated(self) -> None:
        page_one = [{"type": "deletion"} for _ in range(100)]
        page_two = [{"type": "update", "ruleset_id": 42}]
        endpoints: list[str] = []

        def read(endpoint: str, *, optional: bool = False) -> tuple[object, str | None]:
            endpoints.append(endpoint)
            if "rules/branches" in endpoint and "&page=1" in endpoint:
                return page_one, None
            if "rules/branches" in endpoint and "&page=2" in endpoint:
                return page_two, None
            if "/rulesets/42" in endpoint:
                return {"id": 42}, None
            if endpoint.endswith("/protection"):
                return None, "not-protected"
            self.fail(f"Unexpected endpoint: {endpoint}")

        with mock.patch("g.delivery_status._rest_json", side_effect=read):
            rules, rulesets, protection = _read_rules("owner/repo", "main")

        self.assertEqual(len(rules), 101)
        self.assertEqual(rulesets, [{"id": 42}])
        self.assertIn("&page=2", endpoints[1])
        self.assertFalse(any("&page=3" in endpoint for endpoint in endpoints))
        self.assertEqual(protection["unavailable"][0]["surface"], "classic-branch-protection")

    def test_inspection_keeps_automation_separate_from_classification(self) -> None:
        repository = {
            "nameWithOwner": "owner/repo",
            "autoMergeAllowed": True,
            "mergeCommitAllowed": True,
            "rebaseMergeAllowed": True,
            "squashMergeAllowed": True,
            "viewerPermission": "ADMIN",
        }
        pr = pull_request(autoMergeRequest={"mergeMethod": "SQUASH"})
        rules = [{"type": "update", "ruleset_id": 42}]
        rulesets = [{"id": 42, "bypass_actors": [{"actor_type": "RepositoryRole", "actor_id": 5, "bypass_mode": "always"}]}]
        with mock.patch("g.delivery_status._read_pull_request", return_value=({"repository": repository, "pull_request": pr}, True)), mock.patch(
            "g.delivery_status._read_rules",
            return_value=(rules, rulesets, {"classic_branch_protection": None, "unavailable": []}),
        ):
            result = inspect_delivery_status("owner/repo", 77, HEAD)

        self.assertEqual(result["classification"]["disposition"], "ready")
        self.assertTrue(result["automation"]["repository_auto_merge_allowed"])
        self.assertIsNotNone(result["automation"]["pr_auto_merge_request"])
        self.assertTrue(result["identity"]["expected_head_matches"])

    def test_cli_emits_stable_json_envelope(self) -> None:
        expected = {"schema_version": "1.0.0", "classification": {"disposition": "ready"}}
        output = io.StringIO()
        with mock.patch.object(cli, "inspect_delivery_status", return_value=expected), contextlib.redirect_stdout(output):
            code = cli.main(["--json", "pr", "delivery-status", "--repo", "owner/repo", "--pr", "77", "--expected-head", HEAD])
        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["command"], ["pr", "delivery-status"])
        self.assertEqual(payload["data"], expected)


if __name__ == "__main__":
    unittest.main()
