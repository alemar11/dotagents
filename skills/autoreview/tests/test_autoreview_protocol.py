from __future__ import annotations

import copy
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


class AutoReviewProtocolTests(unittest.TestCase):
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
        obligation = {
            "schema_version": "2.0.0",
            "obligation_id": "a" * 64,
            "review_target_key": terminal["target"]["review_target_key"],
            "prior_lineage_id": terminal["lineage_id"],
            "prior_evidence_fingerprint": terminal["evidence_fingerprint"],
            "source_committed_revision_key": terminal["target"]["committed_revision_key"],
            "repository_id": "/repo/.git",
            "github_repository": "example/repo",
            "pr_number": 1,
            "request_receipt_fingerprint": "b" * 64,
            "observation_fingerprint": "c" * 64,
            "provider_evidence_fingerprint": "d" * 64,
            "finding_count": 1,
            "finding_comment_ids": [],
            "finding_set_ref": "/tmp/findings.json",
            "finding_set_fingerprint": "e" * 64,
        }
        projection = PROTOCOL.next_projection(terminal, target=terminal["target"], hosted_obligation=obligation)
        self.assertEqual(projection["action"], "fix-verification")
        self.assertEqual(projection["packet"]["prompt_route"], "managed-fix-verification")

    def test_attempt_history_distinguishes_prepared_from_model_started(self) -> None:
        prepared = {"state": "prepared", "model_call_started": False}
        PROTOCOL.validate_attempt_transition([], prepared)
        started = {"state": "model-started", "model_call_started": True}
        PROTOCOL.validate_attempt_transition([prepared], started)
        with self.assertRaises(PROTOCOL.ProtocolError):
            PROTOCOL.validate_attempt_transition([prepared, started], started)


if __name__ == "__main__":
    unittest.main()
