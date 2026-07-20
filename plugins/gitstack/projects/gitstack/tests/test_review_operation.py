from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gitstack.review_operation import (
    OperationError, build_request, build_result, fingerprint,
    validation_descriptor,
    validate_request, validate_result,
    validate_result_for_request,
)
from gitstack.review_request import build_request as build_provider_request, receipt
from gitstack import reviews


class ReviewOperationContractTests(unittest.TestCase):
    def authority(self) -> dict[str, object]:
        return {
            "ledger": "/tmp/ledger.json", "root_id": "root-1",
            "expected_claim_fingerprint": "a" * 64, "expected_generation": 4,
            "expected_state_fingerprint": "b" * 64, "task_key": "task-a",
            "delivery_key": "repo-a", "task_state": "review-polling",
            "task_observation_fingerprint": "c" * 64, "revision_key": "d" * 64,
            "managed_checkout_fingerprint": "e" * 64,
        }

    def target(self) -> dict[str, object]:
        return {"repository": "owner/repo", "pr_number": 12, "head_sha": "f" * 40, "provider": "codex"}

    def receipt(self) -> dict[str, object]:
        plan = build_provider_request("codex", "owner/repo", 12, "f" * 40, "9" * 64)
        return receipt(plan, {
            "id": 99, "html_url": "https://github.com/owner/repo/pull/12#issuecomment-99",
            "body": plan.body, "created_at": "2026-07-20T12:00:00Z",
            "user": {"login": "agent"},
        }, status="posted")

    def controller(self, operation: str) -> dict[str, object]:
        return {
            "decision": "action", "action": f"gitstack-{operation}",
            "packet_template": {
                "schema_version": "2.0.0", "packet_kind": "owned-operation",
                "executor": "visible-task",
                "operation": {"owner": "gitstack", "name": operation, "contract_version": "1.0.0"},
                "authority_binding": self.authority(), "required_inputs": [],
                "accepted_result": {"schema": "gitstack-review-operation-result:v1", "operation": operation},
            },
            "projection_fingerprint": "1" * 64,
        }

    def request(self, operation: str = "request") -> dict[str, object]:
        inputs: dict[str, object] = {"request_key": "9" * 64}
        if operation == "wait":
            inputs = {"request_receipt": self.receipt(), "wait_started_at": "2026-07-20T12:00:00Z", "wait_deadline": "2026-07-20T12:45:00Z"}
        return build_request(operation=operation, controller_envelope=self.controller(operation), target=self.target(), input_value=inputs)

    def start(self, request_value: dict[str, object]) -> dict[str, object]:
        value = {
            "schema": "implement-feature-owned-operation-start:v1", "owner": "gitstack",
            "operation": request_value["operation"], "operation_id": request_value["operation_id"],
            "request_fingerprint": request_value["request_fingerprint"], "journal_id": "2" * 64,
            "started_generation": 5, "started_state_fingerprint": "3" * 64,
            "receipt_fingerprint": "0" * 64,
        }
        value["receipt_fingerprint"] = fingerprint({k: v for k, v in value.items() if k != "receipt_fingerprint"})
        return value

    def test_prepare_is_strict_and_fingerprinted(self) -> None:
        value = self.request()
        self.assertEqual(validate_request(value), value)
        for mutation in (
            lambda row: row.update(extra=True),
            lambda row: row["target"].update(repository="/repo"),
            lambda row: row["input"].update(request_key="loose"),
            lambda row: row.update(request_fingerprint="0" * 64),
            lambda row: row["authority"].update(expected_generation=0),
        ):
            candidate = copy.deepcopy(value)
            mutation(candidate)
            with self.assertRaises(OperationError):
                validate_request(candidate)

    def test_wait_requires_canonical_utc_exact_45_minutes(self) -> None:
        self.assertEqual(validate_request(self.request("wait"))["operation"], "wait")
        for started, deadline in (
            ("2026-07-20 12:00:00", "2026-07-20T12:45:00Z"),
            ("2026-07-20T12:00:00Z", "2026-07-20T12:44:59Z"),
            ("2026-07-20T12:00:00+00:00", "2026-07-20T12:45:00Z"),
        ):
            with self.assertRaises(OperationError):
                build_request(operation="wait", controller_envelope=self.controller("wait"), target=self.target(), input_value={"request_receipt": self.receipt(), "wait_started_at": started, "wait_deadline": deadline})

    def test_result_status_outcome_and_facts_are_closed(self) -> None:
        request_value = self.request("wait")
        facts = {
            "repository": "owner/repo", "pr_number": 12, "head_sha": "f" * 40,
            "provider": "codex", "request_receipt": self.receipt(),
            "request_binding": "recognized", "provider_state": "clean",
            "observation_fingerprint": "4" * 64, "finding_count": 0,
            "finding_comment_ids": [],
            "artifact": {"kind": "provider-comment", "object_id": 100,
                "object_url": "https://github.com/owner/repo/pull/12#issuecomment-100",
                "actor": "chatgpt-codex-connector[bot]", "body_fingerprint": "5" * 64,
                "outcome": "clean"},
        }
        result = build_result(request=request_value, start_receipt=self.start(request_value), status="completed", outcome="clean", facts=facts, evidence_ref="gitstack-operation://clean")
        self.assertEqual(validate_result(result), result)
        for mutation in (
            lambda row: row.update(status="failed"),
            lambda row: row["facts"].update(extra=True),
            lambda row: row["facts"].update(request_binding="unbound"),
            lambda row: row["facts"]["artifact"].update(object_id="100"),
            lambda row: row.update(result_fingerprint="0" * 64),
        ):
            candidate = copy.deepcopy(result)
            mutation(candidate)
            if candidate["result_fingerprint"] != "0" * 64:
                candidate["result_fingerprint"] = fingerprint({k: v for k, v in candidate.items() if k != "result_fingerprint"})
            with self.assertRaises(OperationError):
                validate_result(candidate)

    def test_plain_request_receipt_and_reconciliation_identity_fail_closed(self) -> None:
        invalid = self.receipt()
        invalid["request_key"] = "plain"
        with self.assertRaises(OperationError):
            build_request(operation="wait", controller_envelope=self.controller("wait"), target=self.target(), input_value={"request_receipt": invalid, "wait_started_at": "2026-07-20T12:00:00Z", "wait_deadline": "2026-07-20T12:45:00Z"})

    def test_result_correlation_rejects_valid_cross_request_receipt(self) -> None:
        request_a = self.request("wait")
        plan_b = build_provider_request("codex", "owner/repo", 12, "f" * 40, "8" * 64)
        receipt_b = receipt(plan_b, {
            "id": 98, "html_url": "https://github.com/owner/repo/pull/12#issuecomment-98",
            "body": plan_b.body, "created_at": "2026-07-20T12:01:00Z", "user": {"login": "agent"},
        }, status="posted")
        request_b = build_request(
            operation="wait", controller_envelope=self.controller("wait"), target=self.target(),
            input_value={"request_receipt": receipt_b, "wait_started_at": "2026-07-20T12:01:00Z", "wait_deadline": "2026-07-20T12:46:00Z"},
        )
        facts_a = {
            "repository": "owner/repo", "pr_number": 12, "head_sha": "f" * 40,
            "provider": "codex", "request_receipt": self.receipt(),
            "request_binding": "recognized", "provider_state": "pending",
            "observation_fingerprint": "4" * 64, "finding_count": 0,
            "finding_comment_ids": [], "artifact": {"kind": "none", "object_id": None,
                "object_url": None, "actor": None, "body_fingerprint": None, "outcome": None},
        }
        unrelated = build_result(
            request=request_b, start_receipt=self.start(request_b), status="completed",
            outcome="pending-at-deadline", facts=facts_a, evidence_ref="gitstack-operation://pending",
        )
        self.assertEqual(validate_result(unrelated), unrelated)
        with self.assertRaises(OperationError):
            validate_result_for_request(unrelated, request_b)
        with self.assertRaises(OperationError):
            validate_result_for_request(unrelated, request_a)

    def test_result_correlation_rejects_cross_pr_and_head_artifacts(self) -> None:
        receipt_a = self.receipt()
        facts_a = {
            "repository": "owner/repo", "pr_number": 12, "head_sha": "f" * 40,
            "provider": "codex", "request_receipt": receipt_a,
            "mutation": {"status": "posted", "object_id": 99,
                "object_url": receipt_a["request_ref"], "actor": receipt_a["actor"],
                "body_fingerprint": receipt_a["body_fingerprint"]},
        }
        for target in (
            {"repository": "owner/other", "pr_number": 12, "head_sha": "f" * 40, "provider": "codex"},
            {"repository": "owner/repo", "pr_number": 13, "head_sha": "f" * 40, "provider": "codex"},
            {"repository": "owner/repo", "pr_number": 12, "head_sha": "e" * 40, "provider": "codex"},
        ):
            request_value = build_request(
                operation="request", controller_envelope=self.controller("request"),
                target=target, input_value={"request_key": "9" * 64},
            )
            result = build_result(
                request=request_value, start_receipt=self.start(request_value), status="completed",
                outcome="created", facts=facts_a, evidence_ref="gitstack-operation://cross-target",
            )
            self.assertEqual(validate_result(result), result)
            with self.assertRaises(OperationError):
                validate_result_for_request(result, request_value)

    def test_validation_descriptor_projects_exact_reconciliation_start(self) -> None:
        started = self.request("request")
        request_value = build_request(
            operation="reconcile-mutation",
            controller_envelope=self.controller("reconcile-mutation"),
            target=self.target(),
            input_value={
                "started_operation": {"request": started, "start_receipt": self.start(started)},
            },
        )
        descriptor = validation_descriptor(request_value)
        self.assertEqual(
            descriptor["start_identity"],
            {
                "owner": "gitstack",
                "operation": started["operation"],
                "operation_id": started["operation_id"],
                "request_fingerprint": started["request_fingerprint"],
                "start_receipt_fingerprint": self.start(started)["receipt_fingerprint"],
            },
        )
        self.assertIsNone(descriptor["result_effect"])
        self.assertEqual(descriptor["owner"], "gitstack")

    def test_warning_descriptor_binds_exact_pending_predecessor(self) -> None:
        wait_request = self.request("wait")
        facts = {
            "repository": "owner/repo", "pr_number": 12, "head_sha": "f" * 40,
            "provider": "codex", "request_receipt": self.receipt(),
            "request_binding": "recognized", "provider_state": "pending",
            "observation_fingerprint": "4" * 64, "finding_count": 0,
            "finding_comment_ids": [],
            "artifact": {"kind": "none", "object_id": None, "object_url": None,
                "actor": None, "body_fingerprint": None, "outcome": None},
        }
        pending = build_result(
            request=wait_request, start_receipt=self.start(wait_request),
            status="completed", outcome="pending-at-deadline", facts=facts,
            evidence_ref="gitstack-operation://pending",
        )
        warning = build_request(
            operation="warning", controller_envelope=self.controller("warning"),
            target=self.target(), input_value={
                "request_receipt": self.receipt(),
                "prior_pending_result": pending,
                "body_file": "/tmp/warning.md",
                "body_fingerprint": "6" * 64,
            },
        )
        self.assertEqual(validation_descriptor(warning)["prior_result_effect"], {
            "relationship": "predecessor", "owner": "gitstack",
            "result_fingerprint": pending["result_fingerprint"],
            "required_disposition": "pending-warning",
        })

        plan_b = build_provider_request("codex", "owner/repo", 12, "f" * 40, "8" * 64)
        receipt_b = receipt(plan_b, {
            "id": 98, "html_url": "https://github.com/owner/repo/pull/12#issuecomment-98",
            "body": plan_b.body, "created_at": "2026-07-20T12:01:00Z",
            "user": {"login": "agent"},
        }, status="posted")
        request_b = build_request(
            operation="wait", controller_envelope=self.controller("wait"), target=self.target(),
            input_value={"request_receipt": receipt_b, "wait_started_at": "2026-07-20T12:01:00Z", "wait_deadline": "2026-07-20T12:46:00Z"},
        )
        facts_b = copy.deepcopy(facts)
        facts_b["request_receipt"] = receipt_b
        swapped = build_result(
            request=request_b, start_receipt=self.start(request_b), status="completed",
            outcome="pending-at-deadline", facts=facts_b,
            evidence_ref="gitstack-operation://other-pending",
        )
        with self.assertRaises(OperationError):
            build_request(
                operation="warning", controller_envelope=self.controller("warning"),
                target=self.target(), input_value={
                    "request_receipt": self.receipt(),
                    "prior_pending_result": swapped,
                    "body_file": "/tmp/warning.md",
                    "body_fingerprint": "6" * 64,
                },
            )

    def test_two_finding_followup_obligations_reject_cross_swap(self) -> None:
        wait_request = self.request("wait")
        facts = {
            "repository": "owner/repo", "pr_number": 12, "head_sha": "f" * 40,
            "provider": "codex", "request_receipt": self.receipt(),
            "request_binding": "recognized", "provider_state": "findings",
            "observation_fingerprint": "4" * 64, "finding_count": 2,
            "finding_comment_ids": [101, 102],
            "artifact": {"kind": "formal-review", "object_id": 100,
                "object_url": "https://github.com/owner/repo/pull/12#pullrequestreview-100",
                "actor": "chatgpt-codex-connector[bot]", "body_fingerprint": "5" * 64,
                "outcome": "findings"},
        }
        findings = build_result(
            request=wait_request, start_receipt=self.start(wait_request),
            status="completed", outcome="findings", facts=facts,
            evidence_ref="gitstack-operation://findings",
        )
        obligations = validation_descriptor(wait_request, findings)["followup_effect"]["creates"]
        common = {
            "request_receipt": self.receipt(), "prior_findings_result": findings,
            "thread_id": "thread-101", "thread_fingerprint": "6" * 64,
            "body_file": "/tmp/reply.md", "body_fingerprint": "7" * 64,
        }
        accepted = build_request(
            operation="reply", controller_envelope=self.controller("reply"), target=self.target(),
            input_value={**common, "finding_comment_id": 101, "followup_obligation": obligations[0]},
        )
        self.assertEqual(accepted["input"]["followup_obligation"], obligations[0])
        with self.assertRaises(OperationError):
            build_request(
                operation="reply", controller_envelope=self.controller("reply"), target=self.target(),
                input_value={**common, "finding_comment_id": 101, "followup_obligation": obligations[1]},
            )

    def test_reply_prepare_derives_exact_remote_thread_identity(self) -> None:
        wait_request = self.request("wait")
        findings = build_result(
            request=wait_request, start_receipt=self.start(wait_request),
            status="completed", outcome="findings",
            facts={
                "repository": "owner/repo", "pr_number": 12, "head_sha": "f" * 40,
                "provider": "codex", "request_receipt": self.receipt(),
                "request_binding": "recognized", "provider_state": "findings",
                "observation_fingerprint": "4" * 64, "finding_count": 1,
                "finding_comment_ids": [101],
                "artifact": {
                    "kind": "formal-review", "object_id": 100,
                    "object_url": "https://github.com/owner/repo/pull/12#pullrequestreview-100",
                    "actor": "chatgpt-codex-connector[bot]", "body_fingerprint": "5" * 64,
                    "outcome": "findings",
                },
            },
            evidence_ref="gitstack-operation://findings",
        )
        obligation = validation_descriptor(wait_request, findings)["followup_effect"]["creates"][0]
        supplied = {
            "target": self.target(),
            "input": {
                "request_receipt": self.receipt(), "prior_findings_result": findings,
                "followup_obligation": obligation, "finding_comment_id": 101,
                "body_file": "/tmp/reply.md", "body_fingerprint": "7" * 64,
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            controller_file = root / "controller.json"
            input_file = root / "input.json"
            output_file = root / "request.json"
            controller_file.write_text(json.dumps(self.controller("reply")))
            input_file.write_text(json.dumps(supplied))
            thread = {"thread_id": "PRRT_thread_101", "comments": []}
            with mock.patch.object(
                reviews, "_reply_thread_identity",
                return_value=({}, thread, "6" * 64, "f" * 40),
            ) as derive:
                reviews.prepare_owned_operation(
                    str(controller_file), str(input_file), str(output_file),
                )
            prepared = json.loads(output_file.read_text())
            self.assertEqual(prepared["input"]["thread_id"], "PRRT_thread_101")
            self.assertEqual(prepared["input"]["thread_fingerprint"], "6" * 64)
            derive.assert_called_once_with("owner/repo", 12, "f" * 40, 101)

            supplied["input"]["thread_id"] = "caller-thread"
            input_file.write_text(json.dumps(supplied))
            with self.assertRaises(reviews.ReviewError) as rejected:
                reviews.prepare_owned_operation(
                    str(controller_file), str(input_file), str(output_file),
                )
            self.assertEqual(rejected.exception.code, "invalid_arguments")

    def test_wait_resume_reuses_original_deadline_and_never_starts_again(self) -> None:
        now = datetime.now(timezone.utc).replace(microsecond=0)
        for deadline, expected_zero in (
            (now + timedelta(minutes=45), False),
            (now - timedelta(seconds=1), True),
        ):
            request_value = build_request(
                operation="wait", controller_envelope=self.controller("wait"), target=self.target(),
                input_value={
                    "request_receipt": self.receipt(),
                    "wait_started_at": (deadline - timedelta(minutes=45)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "wait_deadline": deadline.strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
            )
            raw = {
                "request_binding": "recognized", "review_state": "clean",
                "observation_fingerprint": "4" * 64,
                "review": {"findings": 0, "finding_comment_ids": []},
                "evidence": {"kind": "provider-comment", "object_id": 100,
                    "object_url": "https://github.com/owner/repo/pull/12#issuecomment-100",
                    "actor": "chatgpt-codex-connector[bot]", "body_fingerprint": "5" * 64,
                    "outcome": "clean"},
            }
            with tempfile.TemporaryDirectory() as root:
                request_file = Path(root) / "request.json"
                result_file = Path(root) / "result.json"
                request_file.write_text(json.dumps(request_value))
                with mock.patch.object(reviews, "_owned_operation_bridge", return_value=self.start(request_value)) as bridge, \
                     mock.patch.object(reviews, "wait_for_automated_review", return_value=(raw, 0)) as waiter:
                    reviews.execute_owned_operation(str(request_file), str(result_file), mode="resume")
                bridge.assert_called_once_with(str(request_file), "read-start")
                timeout = waiter.call_args.args[4]
                self.assertEqual(timeout == 0, expected_zero)
                self.assertLessEqual(timeout, 45 * 60)


if __name__ == "__main__":
    unittest.main()
