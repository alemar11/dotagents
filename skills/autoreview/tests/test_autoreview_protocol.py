from __future__ import annotations

import copy
import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/autoreview_protocol.py"
SPEC = importlib.util.spec_from_file_location("autoreview_protocol_test", MODULE_PATH)
assert SPEC and SPEC.loader
PROTOCOL = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PROTOCOL
SPEC.loader.exec_module(PROTOCOL)


def target(*, head: str = "1" * 40, merge_base: str = "2" * 40, patch: str = "3" * 64) -> dict:
    scope = ["skills/autoreview/scripts/autoreview"]
    review_target_key = PROTOCOL.make_review_target_key(
        repository_id="/repo/.git", base_ref="main", review_scope=scope
    )
    return {
        "repository_id": "/repo/.git",
        "base_ref": "main",
        "merge_base_sha": merge_base,
        "head_sha": head,
        "review_scope": scope,
        "review_target_key": review_target_key,
        "reviewed_patch_fingerprint": patch,
        "phase_input_fingerprint": patch,
        "committed_revision_key": PROTOCOL.make_committed_revision_key(
            review_target_key=review_target_key,
            head_sha=head,
            reviewed_patch_fingerprint=patch,
        ),
    }


def evidence(
    *,
    phase: str = "full",
    target_value: dict | None = None,
    parent: dict | None = None,
    terminal_state: str = "terminal-clean",
    open_findings: list | None = None,
    hosted_obligation_id: str | None = None,
) -> dict:
    counts = (
        {"full_reviews": 1, "terminal_full_reviews": 0, "fix_verifications": 0, "model_calls": 1}
        if parent is None
        else copy.deepcopy(parent["counts"])
    )
    if parent is not None and phase == "fix-verification":
        counts["fix_verifications"] += 1
        counts["model_calls"] += 1
    if parent is not None and phase == "terminal-full":
        counts["full_reviews"] += 1
        counts["terminal_full_reviews"] += 1
        counts["model_calls"] += 1
    value = {
        "schema_version": "2.0.0",
        "protocol_version": "2.0.0",
        "review_phase": phase,
        "lineage_id": parent["lineage_id"] if parent else "4" * 64,
        "parent_evidence_fingerprint": parent["evidence_fingerprint"] if parent else None,
        "target": target_value or target(),
        "counts": counts,
        "finding_state": {"open": open_findings or [], "resolved": [], "rejected": []},
        "hosted_obligation_id": hosted_obligation_id,
        "report": {"review_outcome": "fail" if open_findings else "pass", "findings": []},
        "terminal_state": terminal_state,
        "metrics": {"prompt_characters": 10, "elapsed_seconds": 1},
    }
    value["evidence_fingerprint"] = PROTOCOL.evidence_fingerprint(value)
    return value


def obligation(parent: dict, *, marker: str, finding_comment_ids: list[str]) -> dict:
    return {
        "schema_version": "2.0.0",
        "obligation_id": marker * 64,
        "review_target_key": parent["target"]["review_target_key"],
        "prior_lineage_id": parent["lineage_id"],
        "prior_evidence_fingerprint": parent["evidence_fingerprint"],
        "source_committed_revision_key": parent["target"]["committed_revision_key"],
        "repository_id": "/repo/.git",
        "github_repository": "example/repo",
        "pr_number": 1,
        "request_receipt_fingerprint": "b" * 64,
        "observation_fingerprint": "c" * 64,
        "provider_evidence_fingerprint": "d" * 64,
        "finding_count": 1,
        "finding_comment_ids": finding_comment_ids,
        "finding_set_ref": "/tmp/findings.json",
        "finding_set_fingerprint": "e" * 64,
    }


class AutoReviewProtocolTests(unittest.TestCase):
    def journal_record(
        self,
        prior: dict | None,
        transition: str,
        launches: int,
        **overrides: object,
    ) -> dict:
        state = {
            "prepared": "prepared", "model-started": "model-started",
            "repair-prepared": "model-started", "repair-model-started": "model-started",
            "completed": "completed", "failed": "failed",
        }[transition]
        record = {
            "schema_version": "2.1.0", "transition": transition, "state": state,
            "model_call_started": launches > 0, "model_launch_count": launches,
            "attempt_id": "a" * 64, "reservation_id": "b" * 64,
            "pid": 101 if transition in {"model-started", "repair-model-started"} else None,
            "invalid_output": None, "prompt_fingerprint": None,
            "candidate_fingerprint": None, "operation_id": None,
            "parent_record_fingerprint": PROTOCOL.fingerprint(prior) if prior else None,
        }
        record.update(overrides)
        return record

    def test_identity_separates_target_revision_and_publication(self) -> None:
        first = target()
        same = target()
        self.assertEqual(first["review_target_key"], same["review_target_key"])
        self.assertEqual(first["committed_revision_key"], same["committed_revision_key"])
        moved = target(head="5" * 40)
        self.assertEqual(first["review_target_key"], moved["review_target_key"])
        self.assertNotEqual(first["committed_revision_key"], moved["committed_revision_key"])

    def test_rebase_continuity_requires_equivalent_patch_and_scope(self) -> None:
        previous = target()
        equivalent = target(head="5" * 40, merge_base="6" * 40)
        self.assertTrue(PROTOCOL.same_semantic_target(previous, equivalent))
        changed = target(head="5" * 40, merge_base="6" * 40, patch="7" * 64)
        self.assertFalse(PROTOCOL.same_semantic_target(previous, changed))

    def test_budget_is_one_initial_and_one_terminal_full(self) -> None:
        initial = evidence(terminal_state="fix-required", open_findings=[{"finding_id": "8" * 64}])
        PROTOCOL.validate_transition(None, initial)
        fixed = evidence(
            phase="fix-verification",
            parent=initial,
            target_value=target(head="5" * 40, patch="9" * 64),
            terminal_state="verification-clean",
        )
        PROTOCOL.validate_transition(initial, fixed)
        terminal = evidence(
            phase="terminal-full",
            parent=fixed,
            target_value=target(head="5" * 40, patch="9" * 64),
            terminal_state="terminal-clean",
        )
        PROTOCOL.validate_transition(fixed, terminal)
        third = evidence(
            phase="terminal-full",
            parent=terminal,
            target_value=target(head="5" * 40, patch="9" * 64),
            terminal_state="terminal-clean",
        )
        with self.assertRaisesRegex(PROTOCOL.ProtocolError, "full review budget"):
            PROTOCOL.validate_transition(terminal, third)

    def test_hosted_finding_after_terminal_routes_to_focused_verification(self) -> None:
        terminal = evidence()
        summary = obligation(terminal, marker="a", finding_comment_ids=[])
        projection = PROTOCOL.next_projection(terminal, target=terminal["target"], hosted_obligation=summary)
        self.assertEqual(projection["action"], "fix-verification")
        self.assertEqual(projection["packet"]["prompt_route"], "managed-fix-verification")

    def test_repeated_hosted_cycles_continue_after_terminal_composite(self) -> None:
        initial = evidence(terminal_state="fix-required", open_findings=[{"finding_id": "1" * 64}])
        fixed = evidence(
            phase="fix-verification", parent=initial,
            target_value=target(head="5" * 40, patch="6" * 64),
            terminal_state="verification-clean",
        )
        PROTOCOL.validate_transition(initial, fixed)
        terminal_full = evidence(
            phase="terminal-full", parent=fixed,
            target_value=target(head="5" * 40, patch="6" * 64),
            terminal_state="fix-required", open_findings=[{"finding_id": "2" * 64}],
        )
        PROTOCOL.validate_transition(fixed, terminal_full)
        composite = evidence(
            phase="fix-verification", parent=terminal_full,
            target_value=target(head="7" * 40, patch="8" * 64),
            terminal_state="terminal-composite-clean",
        )
        PROTOCOL.validate_transition(terminal_full, composite)
        first_obligation = obligation(composite, marker="9", finding_comment_ids=[])
        first_hosted = evidence(
            phase="fix-verification", parent=composite,
            target_value=target(head="a" * 40, patch="b" * 64),
            terminal_state="terminal-composite-clean",
            hosted_obligation_id=first_obligation["obligation_id"],
        )
        PROTOCOL.validate_transition(composite, first_hosted, hosted_obligation=first_obligation)
        second_obligation = obligation(first_hosted, marker="f", finding_comment_ids=["inline-42"])
        second_hosted = evidence(
            phase="fix-verification", parent=first_hosted,
            target_value=target(head="c" * 40, patch="d" * 64),
            terminal_state="terminal-composite-clean",
            hosted_obligation_id=second_obligation["obligation_id"],
        )
        PROTOCOL.validate_transition(first_hosted, second_hosted, hosted_obligation=second_obligation)
        self.assertEqual(second_hosted["counts"]["full_reviews"], 2)
        self.assertEqual(second_hosted["counts"]["terminal_full_reviews"], 1)

    def test_attempt_history_distinguishes_prepared_from_model_started(self) -> None:
        prepared = {"state": "prepared", "model_call_started": False}
        PROTOCOL.validate_attempt_transition([], prepared)
        started = {"state": "model-started", "model_call_started": True}
        PROTOCOL.validate_attempt_transition([prepared], started)
        with self.assertRaises(PROTOCOL.ProtocolError):
            PROTOCOL.validate_attempt_transition([prepared, started], started)

    def test_attempt_journal_replays_every_crash_boundary_and_rejects_tampering(self) -> None:
        records: list[dict] = []
        for transition, launches, overrides in (
            ("prepared", 0, {}),
            ("model-started", 1, {"prompt_fingerprint": "c" * 64}),
            ("repair-prepared", 1, {
                "prompt_fingerprint": "d" * 64,
                "invalid_output": {
                    "classification": "semantic-invariant",
                    "validator_code": "review-fail-without-finding",
                    "violated_rule": "Fail requires a discrete finding.",
                    "output_fingerprint": hashlib.sha256(b"invalid").hexdigest(),
                    "output_size_bytes": 7,
                    "output_truncated": False,
                    "preview": "invalid",
                    "artifact_ref": "attempt://a/record-3",
                },
            }),
            ("repair-model-started", 2, {"prompt_fingerprint": "d" * 64}),
        ):
            records.append(self.journal_record(records[-1] if records else None, transition, launches, **overrides))
            self.assertEqual(PROTOCOL.validate_attempt_journal(copy.deepcopy(records)), records)

        for index in range(len(records)):
            tampered = copy.deepcopy(records)
            tampered[index]["reservation_id"] = "f" * 64
            with self.assertRaises(PROTOCOL.ProtocolError):
                PROTOCOL.validate_attempt_journal(tampered)

        unknown = copy.deepcopy(records)
        unknown[-1]["retry"] = True
        with self.assertRaisesRegex(PROTOCOL.ProtocolError, "invalid field set"):
            PROTOCOL.validate_attempt_journal(unknown)

        broken_chain = copy.deepcopy(records)
        broken_chain[-1]["parent_record_fingerprint"] = "0" * 64
        with self.assertRaisesRegex(PROTOCOL.ProtocolError, "parent_record_fingerprint"):
            PROTOCOL.validate_attempt_journal(broken_chain)

        duplicate = copy.deepcopy(records)
        duplicate.append(self.journal_record(duplicate[-1], "repair-prepared", 2))
        with self.assertRaises(PROTOCOL.ProtocolError):
            PROTOCOL.validate_attempt_journal(duplicate)

    def test_attempt_journal_terminal_records_preserve_launch_count(self) -> None:
        prepared = self.journal_record(None, "prepared", 0)
        started = self.journal_record(prepared, "model-started", 1, prompt_fingerprint="c" * 64)
        failed = self.journal_record(started, "failed", 1)
        PROTOCOL.validate_attempt_journal([prepared, started, failed])

        completed = self.journal_record(
            started, "completed", 1,
            candidate_fingerprint="d" * 64, operation_id="e" * 32,
        )
        PROTOCOL.validate_attempt_journal([prepared, started, completed])


if __name__ == "__main__":
    unittest.main()
