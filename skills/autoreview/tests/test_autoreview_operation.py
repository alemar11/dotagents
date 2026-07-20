from __future__ import annotations

import copy
import re
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import autoreview_operation as operation
import autoreview_protocol as protocol


def target(head: str = "1" * 40) -> dict:
    scope = ["skills/autoreview/scripts/autoreview"]
    target_key = protocol.make_review_target_key(repository_id="/repo/.git", base_ref="main", review_scope=scope)
    patch = "3" * 64
    return {
        "repository_id": "/repo/.git", "base_ref": "main", "merge_base_sha": "2" * 40,
        "head_sha": head, "review_scope": scope, "review_target_key": target_key,
        "reviewed_patch_fingerprint": patch, "phase_input_fingerprint": patch,
        "committed_revision_key": protocol.make_committed_revision_key(review_target_key=target_key, head_sha=head, reviewed_patch_fingerprint=patch),
    }


class AutoReviewOperationTests(unittest.TestCase):
    def authority(self) -> dict:
        return {"ledger": "/tmp/ledger.json", "root_id": "root-1", "expected_claim_fingerprint": "a" * 64, "expected_generation": 4, "expected_state_fingerprint": "b" * 64, "task_key": "task-a", "delivery_key": "repo-a", "task_state": "validating", "task_observation_fingerprint": "c" * 64, "revision_key": "d" * 64, "managed_checkout_fingerprint": "e" * 64}

    def controller(self, name: str = "run-phase") -> dict:
        return {"decision": "action", "packet_template": {"schema_version": "2.0.0", "packet_kind": "owned-operation", "executor": "visible-task", "operation": {"owner": "autoreview", "name": name, "contract_version": "1.0.0"}, "authority_binding": self.authority(), "required_inputs": [], "accepted_result": {"schema": "autoreview-operation-result:v1", "operation": name}}, "projection_fingerprint": "f" * 64}

    def request(self, *, prior: dict | None = None, phase: str = "full", operation_name: str = "run-phase", started: dict | None = None, target_value: dict | None = None, hosted_obligation: dict | None = None, orchestration_descriptor: dict | None = None, lineage_reset_authority: dict | None = None) -> dict:
        return operation.build_request(operation=operation_name, controller_envelope=self.controller(operation_name), target=target_value or target(), prior_evidence=prior, hosted_obligation=hosted_obligation, orchestration_descriptor=orchestration_descriptor, lineage_reset_authority=lineage_reset_authority, requested_phase=phase, started_operation=started)

    def reset_authority(self, prior: dict, next_target: dict) -> dict:
        value = {
            "schema": "autoreview-lineage-reset-authority:v1",
            "authorization": "granted-by-authorized-user",
            "prior_lineage_id": prior["lineage_id"],
            "prior_evidence_fingerprint": prior["evidence_fingerprint"],
            "next_target_fingerprint": operation.fingerprint(next_target),
            "evidence_ref": "owner://lineage-reset/1",
            "authority_fingerprint": "0" * 64,
        }
        value["authority_fingerprint"] = operation.fingerprint(
            {key: item for key, item in value.items() if key != "authority_fingerprint"}
        )
        return value

    def start(self, request: dict) -> dict:
        value = {"schema": "implement-feature-owned-operation-start:v1", "owner": "autoreview", "operation": request["operation"], "operation_id": request["operation_id"], "request_fingerprint": request["request_fingerprint"], "journal_id": "1" * 64, "started_generation": 5, "started_state_fingerprint": "2" * 64, "receipt_fingerprint": "0" * 64}
        value["receipt_fingerprint"] = operation.fingerprint({k: v for k, v in value.items() if k != "receipt_fingerprint"})
        return value

    def evidence(self, request: dict, *, terminal: str = "terminal-clean", open_findings: bool = False) -> dict:
        parent = request["prior_evidence"]
        phase = request["requested_phase"]
        counts = {"full_reviews": 1, "terminal_full_reviews": 0, "fix_verifications": 0, "model_calls": 1}
        lineage = "4" * 64
        if parent:
            counts = dict(parent["counts"])
            lineage = parent["lineage_id"]
            if phase == "fix-verification":
                counts["fix_verifications"] += 1; counts["model_calls"] += 1
            elif phase == "terminal-full":
                counts["full_reviews"] += 1; counts["terminal_full_reviews"] += 1; counts["model_calls"] += 1
        if request["lineage_reset_authority"] is not None:
            counts = {"full_reviews": 1, "terminal_full_reviews": 0, "fix_verifications": 0, "model_calls": 1}
            lineage = "6" * 64
            parent = None
        finding = {"finding_id": "finding-1"}
        value = {"schema_version": "2.0.0", "protocol_version": "2.0.0", "review_phase": phase, "lineage_id": lineage, "parent_evidence_fingerprint": parent["evidence_fingerprint"] if parent else None, "target": request["target"], "counts": counts, "finding_state": {"open": [finding] if open_findings else [], "resolved": [] if open_findings else ([finding] if phase == "disposition" else []), "rejected": []}, "hosted_obligation_id": request["hosted_obligation"]["obligation_id"] if request["hosted_obligation"] else None, "report": {"review_outcome": "findings" if open_findings else "pass", "findings": [finding] if open_findings else []}, "terminal_state": terminal, "metrics": {"prompt_characters": 10, "elapsed_seconds": 1}}
        value["evidence_fingerprint"] = protocol.evidence_fingerprint(value)
        return value

    def journal(self, request: dict, receipt: dict, evidence: dict | None, *, launches: int = 1, failed: bool = False, interrupted: bool = False) -> tuple[str, list[dict]]:
        attempt_id = operation.fingerprint({"operation_id": request["operation_id"], "request_fingerprint": request["request_fingerprint"], "start_receipt_fingerprint": receipt["receipt_fingerprint"]})
        rows: list[dict] = []
        def add(transition: str, state: str, launch_count: int, **extra: object) -> None:
            row = {"schema_version": "2.1.0", "transition": transition, "state": state, "model_call_started": launch_count > 0, "model_launch_count": launch_count, "attempt_id": attempt_id, "reservation_id": receipt["receipt_fingerprint"], "pid": None, "invalid_output": None, "prompt_fingerprint": None, "candidate_fingerprint": None, "operation_id": None, "parent_record_fingerprint": protocol.fingerprint(rows[-1]) if rows else None}
            row.update(extra); rows.append(row)
        add("prepared", "prepared", 0)
        if launches:
            add("model-started", "model-started", 1, pid=101, prompt_fingerprint="7" * 64)
        if launches == 2:
            invalid = {"classification": "schema-parse", "validator_code": "invalid", "violated_rule": "schema", "output_fingerprint": "8" * 64, "output_size_bytes": 3, "output_truncated": False, "preview": "bad", "artifact_ref": "/tmp/bad"}
            add("repair-prepared", "model-started", 1, invalid_output=invalid, prompt_fingerprint="9" * 64)
            add("repair-model-started", "model-started", 2, pid=102, prompt_fingerprint="9" * 64)
        if interrupted:
            return attempt_id, rows
        if failed:
            add("failed", "failed", launches)
        else:
            assert evidence is not None
            add("completed", "completed", launches, candidate_fingerprint=evidence["evidence_fingerprint"], operation_id=request["operation_id"])
        protocol.validate_attempt_journal(rows)
        return attempt_id, rows

    def facts(self, request: dict, receipt: dict, evidence: dict | None, *, launches: int = 1, failed: bool = False, interrupted: bool = False) -> dict:
        attempt_id, rows = self.journal(request, receipt, evidence, launches=launches, failed=failed, interrupted=interrupted)
        return {"attempt_id": attempt_id, "model_call_started": launches > 0, "model_launch_count": launches, "candidate_fingerprint": evidence["evidence_fingerprint"] if evidence else None, "evidence": evidence, "attempt_journal": rows, "attempt_journal_fingerprint": operation.fingerprint(rows)}

    def started(self, request: dict, receipt: dict, facts: dict) -> dict:
        return {"request": request, "start_receipt": receipt, "attempt_id": facts["attempt_id"], "attempt_journal": facts["attempt_journal"], "attempt_journal_fingerprint": facts["attempt_journal_fingerprint"], "model_call_started": facts["model_call_started"], "model_launch_count": facts["model_launch_count"]}

    def result(self, request: dict, receipt: dict, evidence: dict, *, launches: int = 1) -> dict:
        return operation.build_result(request=request, start_receipt=receipt, status="completed", outcome=evidence["terminal_state"], facts=self.facts(request, receipt, evidence, launches=launches), evidence_ref="autoreview-operation://result")

    def test_owner_version_matches_cli_and_old_controller_is_rejected(self) -> None:
        cli_text = (SCRIPTS / "autoreview").read_text()
        self.assertEqual(operation.OWNER_VERSION, re.search(r'^VERSION = "([^"]+)"', cli_text, re.MULTILINE).group(1))
        old = self.controller(); old["packet_template"] = {"schema_version": "1.0.0", "packet_kind": "managed-controller-reservation"}
        with self.assertRaises(operation.OperationError):
            operation.build_request(operation="run-phase", controller_envelope=old, target=target(), prior_evidence=None, hosted_obligation=None, requested_phase="full")

    def test_request_is_protocol_derived_and_strict(self) -> None:
        value = self.request()
        self.assertEqual(operation.validate_request(value), value)
        for mutate in (
            lambda row: row.update(extra=True),
            lambda row: row["authority"].update(expected_generation=0),
            lambda row: row["phase_projection"].update(action="terminal-full"),
            lambda row: row.update(requested_phase="disposition"),
            lambda row: row.update(request_fingerprint="0" * 64),
        ):
            candidate = copy.deepcopy(value); mutate(candidate)
            with self.assertRaises((operation.OperationError, protocol.ProtocolError)):
                operation.validate_request(candidate)

    def test_result_correlation_rejects_target_parent_phase_and_journal_swaps(self) -> None:
        request = self.request(); receipt = self.start(request); evidence = self.evidence(request)
        result = self.result(request, receipt, evidence)
        self.assertEqual(operation.validate_result_for_request(result, request), result)
        other = self.request(); other["target"]["head_sha"] = "7" * 40
        for mutate in (
            lambda row: row.update(status="failed"),
            lambda row: row["facts"].update(model_call_started=False),
            lambda row: row["facts"].update(extra=True),
            lambda row: row["facts"]["evidence"]["target"].update(head_sha="7" * 40),
            lambda row: row["facts"]["evidence"].update(parent_evidence_fingerprint="8" * 64),
            lambda row: row["facts"]["attempt_journal"][0].update(reservation_id="9" * 64),
        ):
            candidate = copy.deepcopy(result); mutate(candidate)
            candidate["facts"]["evidence"]["evidence_fingerprint"] = protocol.evidence_fingerprint(candidate["facts"]["evidence"])
            candidate["facts"]["attempt_journal_fingerprint"] = operation.fingerprint(candidate["facts"]["attempt_journal"])
            candidate["result_fingerprint"] = operation.fingerprint({k: v for k, v in candidate.items() if k != "result_fingerprint"})
            with self.assertRaises((operation.OperationError, protocol.ProtocolError)):
                operation.validate_result_for_request(candidate, request)

    def test_disposition_completes_without_model_launch(self) -> None:
        initial = self.request(); initial_evidence = self.evidence(initial, terminal="fix-required", open_findings=True)
        request = self.request(prior=initial_evidence, phase="disposition")
        receipt = self.start(request); evidence = self.evidence(request, terminal="terminal-composite-clean")
        result = self.result(request, receipt, evidence, launches=0)
        self.assertFalse(result["facts"]["model_call_started"])
        self.assertEqual(operation.validate_result_for_request(result, request), result)

    def test_primary_plus_one_repair_and_second_invalid_failure_are_bounded(self) -> None:
        request = self.request(); receipt = self.start(request); evidence = self.evidence(request)
        operation.validate_result_for_request(self.result(request, receipt, evidence, launches=2), request)
        facts = self.facts(request, receipt, None, launches=2, failed=True)
        failed = operation.build_result(request=request, start_receipt=receipt, status="failed", outcome="failed", facts=facts, evidence_ref="autoreview-operation://invalid")
        operation.validate_result_for_request(failed, request)
        facts["model_launch_count"] = 3
        with self.assertRaises(operation.OperationError):
            operation.build_result(request=request, start_receipt=receipt, status="failed", outcome="failed", facts=facts, evidence_ref="autoreview-operation://third")

    def test_reconciliation_binds_exact_started_request_and_returns_terminal_evidence(self) -> None:
        run_request = self.request(); receipt = self.start(run_request); evidence = self.evidence(run_request)
        facts = self.facts(run_request, receipt, evidence)
        started = self.started(run_request, receipt, facts)
        request = self.request(operation_name="reconcile-attempt", started=started)
        result = operation.build_result(request=request, start_receipt=receipt, status="completed", outcome="terminal-clean", facts=facts, evidence_ref="autoreview-operation://recovered")
        self.assertEqual(operation.validate_result_for_request(result, request)["facts"]["evidence"], evidence)
        descriptor = operation.validation_descriptor(request, result)
        self.assertEqual(descriptor["start_identity"], {
            "owner": "autoreview",
            "operation": run_request["operation"],
            "operation_id": run_request["operation_id"],
            "request_fingerprint": run_request["request_fingerprint"],
            "start_receipt_fingerprint": receipt["receipt_fingerprint"],
        })
        self.assertTrue(descriptor["result_effect"]["evidence_produced"])
        for mutate in (
            lambda row: row["started_operation"]["request"]["target"].update(head_sha="7" * 40),
            lambda row: row["started_operation"].update(attempt_id="8" * 64),
            lambda row: row["started_operation"]["attempt_journal"][0].update(reservation_id="9" * 64),
        ):
            candidate = copy.deepcopy(request); mutate(candidate)
            candidate["request_fingerprint"] = operation.fingerprint({k: v for k, v in candidate.items() if k != "request_fingerprint"})
            with self.assertRaises((operation.OperationError, protocol.ProtocolError)):
                operation.validate_request(candidate)

    def test_interrupted_reconciliation_preserves_consumed_launch_and_never_relaunches(self) -> None:
        run_request = self.request(); receipt = self.start(run_request)
        facts = self.facts(run_request, receipt, None, launches=1, interrupted=True)
        started = self.started(run_request, receipt, facts)
        request = self.request(operation_name="reconcile-attempt", started=started)
        result = operation.build_result(request=request, start_receipt=receipt, status="blocked", outcome="interrupted", facts=facts, evidence_ref="autoreview-operation://interrupted")
        self.assertTrue(operation.validate_result_for_request(result, request)["facts"]["model_call_started"])
        self.assertFalse(
            operation.validation_descriptor(request, result)["result_effect"]["evidence_produced"]
        )

    def test_hosted_obligation_echoes_exact_orchestration_descriptor(self) -> None:
        initial = self.request()
        prior = self.evidence(initial, terminal="fix-required", open_findings=True)
        next_target = target("5" * 40)
        hosted = {
            "schema_version": "2.0.0",
            "obligation_id": "7" * 64,
            "review_target_key": prior["target"]["review_target_key"],
            "prior_lineage_id": prior["lineage_id"],
            "prior_evidence_fingerprint": prior["evidence_fingerprint"],
            "source_committed_revision_key": prior["target"]["committed_revision_key"],
            "repository_id": prior["target"]["repository_id"],
            "github_repository": "example/repo",
            "pr_number": 1,
            "request_receipt_fingerprint": "8" * 64,
            "observation_fingerprint": "9" * 64,
            "provider_evidence_fingerprint": "a" * 64,
            "finding_count": 1,
            "finding_comment_ids": ["finding-1"],
            "finding_set_ref": "/tmp/findings.json",
            "finding_set_fingerprint": "b" * 64,
        }
        descriptor = {
            "hosted_obligation_ref": "owned-obligation://finding-1",
            "source_result_fingerprint": "c" * 64,
        }
        request = self.request(
            prior=prior,
            phase="fix-verification",
            target_value=next_target,
            hosted_obligation=hosted,
            orchestration_descriptor=descriptor,
        )
        receipt = self.start(request)
        evidence = self.evidence(request, terminal="verification-clean")
        result = self.result(request, receipt, evidence)
        self.assertEqual(
            operation.validate_result_for_request(result, request)["orchestration_descriptor"],
            descriptor,
        )
        self.assertEqual(
            operation.validation_descriptor(request, result)["result_effect"],
            {
                "evidence_produced": True,
                "orchestration_descriptor": descriptor,
                "effective_result": {"operation": "run-phase", "outcome": "verification-clean"},
            },
        )
        mismatched = copy.deepcopy(result)
        mismatched["orchestration_descriptor"]["hosted_obligation_ref"] = "owned-obligation://other"
        mismatched["result_fingerprint"] = operation.fingerprint(
            {key: value for key, value in mismatched.items() if key != "result_fingerprint"}
        )
        with self.assertRaises(operation.OperationError):
            operation.validate_result_for_request(mismatched, request)

    def test_lineage_reset_requires_exact_explicit_authority(self) -> None:
        initial = self.request()
        prior = self.evidence(initial)
        next_target = target("5" * 40)
        next_target["review_scope"] = ["skills/autoreview"]
        next_target["review_target_key"] = protocol.make_review_target_key(
            repository_id=next_target["repository_id"],
            base_ref=next_target["base_ref"],
            review_scope=next_target["review_scope"],
        )
        next_target["committed_revision_key"] = protocol.make_committed_revision_key(
            review_target_key=next_target["review_target_key"],
            head_sha=next_target["head_sha"],
            reviewed_patch_fingerprint=next_target["reviewed_patch_fingerprint"],
        )
        with self.assertRaises((operation.OperationError, protocol.ProtocolError)):
            self.request(prior=prior, phase="full", target_value=next_target)
        authority = self.reset_authority(prior, next_target)
        request = self.request(
            prior=prior,
            phase="full",
            target_value=next_target,
            lineage_reset_authority=authority,
        )
        receipt = self.start(request)
        evidence = self.evidence(request)
        result = self.result(request, receipt, evidence)
        validated = operation.validate_result_for_request(result, request)
        self.assertEqual(
            validated["lineage_reset_authority_fingerprint"],
            authority["authority_fingerprint"],
        )
        stale = copy.deepcopy(request)
        stale["lineage_reset_authority"]["next_target_fingerprint"] = "d" * 64
        stale["request_fingerprint"] = operation.fingerprint(
            {key: value for key, value in stale.items() if key != "request_fingerprint"}
        )
        with self.assertRaises(operation.OperationError):
            operation.validate_request(stale)

    def test_lineage_reset_is_rejected_for_normal_fix_and_semantic_rebase(self) -> None:
        initial = self.request()
        prior = self.evidence(initial, terminal="fix-required", open_findings=True)

        normal_fix = target("5" * 40)
        normal_fix["reviewed_patch_fingerprint"] = "d" * 64
        normal_fix["phase_input_fingerprint"] = "d" * 64
        normal_fix["committed_revision_key"] = protocol.make_committed_revision_key(
            review_target_key=normal_fix["review_target_key"],
            head_sha=normal_fix["head_sha"],
            reviewed_patch_fingerprint=normal_fix["reviewed_patch_fingerprint"],
        )
        request = self.request(
            prior=prior,
            phase="fix-verification",
            target_value=normal_fix,
        )
        self.assertIsNone(request["lineage_reset_authority"])
        with self.assertRaises(operation.OperationError):
            self.request(
                prior=prior,
                phase="full",
                target_value=normal_fix,
                lineage_reset_authority=self.reset_authority(prior, normal_fix),
            )

        pure_rebase = copy.deepcopy(normal_fix)
        pure_rebase["merge_base_sha"] = "6" * 40
        pure_rebase["reviewed_patch_fingerprint"] = prior["target"]["reviewed_patch_fingerprint"]
        pure_rebase["phase_input_fingerprint"] = prior["target"]["phase_input_fingerprint"]
        pure_rebase["committed_revision_key"] = protocol.make_committed_revision_key(
            review_target_key=pure_rebase["review_target_key"],
            head_sha=pure_rebase["head_sha"],
            reviewed_patch_fingerprint=pure_rebase["reviewed_patch_fingerprint"],
        )
        rebase_request = self.request(
            prior=prior,
            phase="fix-verification",
            target_value=pure_rebase,
        )
        self.assertIsNone(rebase_request["lineage_reset_authority"])
        with self.assertRaises(operation.OperationError):
            self.request(
                prior=prior,
                phase="full",
                target_value=pure_rebase,
                lineage_reset_authority=self.reset_authority(prior, pure_rebase),
            )


if __name__ == "__main__": unittest.main()
