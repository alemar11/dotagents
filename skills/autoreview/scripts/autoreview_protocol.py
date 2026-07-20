#!/usr/bin/env python3
"""Pure AutoReview lifecycle protocol shared by producer and consumers."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any


PROTOCOL_VERSION = "2.0.0"
EVIDENCE_SCHEMA_VERSION = "2.0.0"
RESERVATION_SCHEMA_VERSION = "2.0.0"
OBLIGATION_SCHEMA_VERSION = "2.0.0"
ATTEMPT_SCHEMA_VERSION = "2.1.0"

REVIEW_PHASES = frozenset({"full", "fix-verification", "disposition", "terminal-full"})
TERMINAL_STATES = frozenset(
    {"fix-required", "verification-clean", "terminal-clean", "terminal-composite-clean"}
)
ATTEMPT_STATES = frozenset({"prepared", "model-started", "completed", "failed"})
ATTEMPT_TRANSITIONS = (
    "prepared",
    "model-started",
    "repair-prepared",
    "repair-model-started",
    "completed",
    "failed",
)
INVALID_OUTPUT_CLASSIFICATIONS = frozenset({"schema-parse", "semantic-invariant"})
MODEL_PHASES = frozenset({"full", "fix-verification", "terminal-full"})
FULL_REVIEW_LIMIT = 2
TERMINAL_FULL_LIMIT = 1
FINGERPRINT_RE = re.compile(r"^[0-9a-f]{64}$")
REVISION_RE = re.compile(r"^[0-9a-f]{40,64}$")


class ProtocolError(ValueError):
    """Stable protocol rejection."""

    def __init__(self, code: str, message: str, *, recovery: str = "needs-owner") -> None:
        super().__init__(message)
        self.code = code
        self.recovery = recovery


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def evidence_fingerprint(value: dict[str, Any]) -> str:
    return fingerprint({key: item for key, item in value.items() if key != "evidence_fingerprint"})


def state_fingerprint(value: Any) -> str:
    return fingerprint(value)


def _exact(value: Any, fields: set[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ProtocolError("protocol-invalid", f"{name} has an invalid field set")
    return value


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProtocolError("protocol-invalid", f"{name} must be non-empty text")
    return value


def _fingerprint(value: Any, name: str) -> str:
    if not isinstance(value, str) or not FINGERPRINT_RE.fullmatch(value):
        raise ProtocolError("protocol-invalid", f"{name} must be a sha256 fingerprint")
    return value


def _revision(value: Any, name: str) -> str:
    if not isinstance(value, str) or not REVISION_RE.fullmatch(value):
        raise ProtocolError("protocol-invalid", f"{name} must be an exact committed revision")
    return value


def _paths(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not value or value != sorted(set(value)):
        raise ProtocolError("protocol-invalid", f"{name} must be a non-empty sorted unique list")
    for path in value:
        if not isinstance(path, str) or not path or path.startswith("/") or ".." in path.split("/"):
            raise ProtocolError("protocol-invalid", f"{name} contains an unsafe path")
    return value


def make_review_target_key(*, repository_id: str, base_ref: str, review_scope: list[str]) -> str:
    return fingerprint(
        {
            "protocol_version": PROTOCOL_VERSION,
            "repository_id": _text(repository_id, "repository_id"),
            "base_ref": _text(base_ref, "base_ref"),
            "review_scope": _paths(sorted(set(review_scope)), "review_scope"),
        }
    )


def make_committed_revision_key(
    *, review_target_key: str, head_sha: str, reviewed_patch_fingerprint: str
) -> str:
    return fingerprint(
        {
            "protocol_version": PROTOCOL_VERSION,
            "review_target_key": _fingerprint(review_target_key, "review_target_key"),
            "head_sha": _revision(head_sha, "head_sha"),
            "reviewed_patch_fingerprint": _fingerprint(
                reviewed_patch_fingerprint, "reviewed_patch_fingerprint"
            ),
        }
    )


def same_semantic_target(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    """A pure rebase is continuous only when scope and canonical patch are equal."""
    return (
        previous["review_target_key"] == current["review_target_key"]
        and previous["review_scope"] == current["review_scope"]
        and previous["reviewed_patch_fingerprint"] == current["reviewed_patch_fingerprint"]
    )


def validate_target(value: Any, name: str = "target") -> dict[str, Any]:
    target = _exact(
        value,
        {
            "repository_id",
            "base_ref",
            "merge_base_sha",
            "head_sha",
            "review_scope",
            "review_target_key",
            "reviewed_patch_fingerprint",
            "phase_input_fingerprint",
            "committed_revision_key",
        },
        name,
    )
    _text(target["repository_id"], f"{name}.repository_id")
    _text(target["base_ref"], f"{name}.base_ref")
    _revision(target["merge_base_sha"], f"{name}.merge_base_sha")
    _revision(target["head_sha"], f"{name}.head_sha")
    scope = _paths(target["review_scope"], f"{name}.review_scope")
    expected_target = make_review_target_key(
        repository_id=target["repository_id"], base_ref=target["base_ref"], review_scope=scope
    )
    if _fingerprint(target["review_target_key"], f"{name}.review_target_key") != expected_target:
        raise ProtocolError("target-key-mismatch", f"{name}.review_target_key is stale")
    _fingerprint(target["reviewed_patch_fingerprint"], f"{name}.reviewed_patch_fingerprint")
    _fingerprint(target["phase_input_fingerprint"], f"{name}.phase_input_fingerprint")
    expected_revision = make_committed_revision_key(
        review_target_key=expected_target,
        head_sha=target["head_sha"],
        reviewed_patch_fingerprint=target["reviewed_patch_fingerprint"],
    )
    if _fingerprint(target["committed_revision_key"], f"{name}.committed_revision_key") != expected_revision:
        raise ProtocolError("revision-key-mismatch", f"{name}.committed_revision_key is stale")
    return target


def validate_hosted_obligation(value: Any) -> dict[str, Any]:
    item = _exact(
        value,
        {
            "schema_version",
            "obligation_id",
            "review_target_key",
            "prior_lineage_id",
            "prior_evidence_fingerprint",
            "source_committed_revision_key",
            "repository_id",
            "github_repository",
            "pr_number",
            "request_receipt_fingerprint",
            "observation_fingerprint",
            "provider_evidence_fingerprint",
            "finding_count",
            "finding_comment_ids",
            "finding_set_ref",
            "finding_set_fingerprint",
        },
        "hosted_obligation",
    )
    if item["schema_version"] != OBLIGATION_SCHEMA_VERSION:
        raise ProtocolError("schema-unsupported", "hosted obligation schema is unsupported")
    for name in (
        "obligation_id", "review_target_key", "prior_lineage_id",
        "prior_evidence_fingerprint", "source_committed_revision_key",
        "request_receipt_fingerprint", "observation_fingerprint",
        "provider_evidence_fingerprint", "finding_set_fingerprint",
    ):
        _fingerprint(item[name], f"hosted_obligation.{name}")
    _text(item["repository_id"], "hosted_obligation.repository_id")
    _text(item["github_repository"], "hosted_obligation.github_repository")
    _text(item["finding_set_ref"], "hosted_obligation.finding_set_ref")
    if not isinstance(item["pr_number"], int) or isinstance(item["pr_number"], bool) or item["pr_number"] < 1:
        raise ProtocolError("protocol-invalid", "hosted_obligation.pr_number is invalid")
    if not isinstance(item["finding_count"], int) or item["finding_count"] < 1:
        raise ProtocolError("protocol-invalid", "hosted_obligation requires accepted findings")
    ids = item["finding_comment_ids"]
    if not isinstance(ids, list) or ids != sorted(set(ids)) or any(not isinstance(v, str) or not v for v in ids):
        raise ProtocolError("protocol-invalid", "hosted_obligation.finding_comment_ids is invalid")
    # An empty list is valid for a summary-only terminal comment.
    return item


def _expected_result(parent: dict[str, Any] | None, phase: str, open_findings: bool) -> str:
    if parent is None:
        if phase != "full":
            raise ProtocolError("action-not-allowed", "a lineage must start with one full review")
        return "fix-required" if open_findings else "terminal-clean"
    prior_state = parent["terminal_state"]
    if phase == "full":
        raise ProtocolError("full-review-budget-exhausted", "an existing lineage cannot run another initial full")
    if phase == "terminal-full":
        if parent["counts"]["full_reviews"] != 1 or prior_state != "verification-clean":
            raise ProtocolError("terminal-full-not-allowed", "terminal full requires first-pass verification-clean")
        return "fix-required" if open_findings else "terminal-clean"
    if phase == "disposition":
        if prior_state != "fix-required" or open_findings:
            raise ProtocolError("action-not-allowed", "disposition must close the current findings")
        return "terminal-composite-clean"
    if prior_state not in {"fix-required", "terminal-clean", "terminal-composite-clean"}:
        raise ProtocolError("action-not-allowed", "fix verification has no accepted finding obligation")
    if open_findings:
        return "fix-required"
    if parent["counts"]["full_reviews"] == 1 and prior_state == "fix-required":
        return "verification-clean"
    return "terminal-composite-clean"


def validate_evidence(value: Any) -> dict[str, Any]:
    item = _exact(
        value,
        {
            "schema_version", "protocol_version", "review_phase", "lineage_id",
            "parent_evidence_fingerprint", "target", "counts", "finding_state",
            "hosted_obligation_id", "report", "terminal_state", "metrics",
            "evidence_fingerprint",
        },
        "evidence",
    )
    if item["schema_version"] != EVIDENCE_SCHEMA_VERSION or item["protocol_version"] != PROTOCOL_VERSION:
        raise ProtocolError("schema-unsupported", "AutoReview evidence schema is unsupported")
    if item["evidence_fingerprint"] != evidence_fingerprint(item):
        raise ProtocolError("evidence-fingerprint-mismatch", "evidence fingerprint mismatch")
    phase = item["review_phase"]
    if phase not in REVIEW_PHASES or item["terminal_state"] not in TERMINAL_STATES:
        raise ProtocolError("protocol-invalid", "evidence uses an invalid phase or terminal state")
    _fingerprint(item["lineage_id"], "evidence.lineage_id")
    if item["parent_evidence_fingerprint"] is not None:
        _fingerprint(item["parent_evidence_fingerprint"], "evidence.parent_evidence_fingerprint")
    validate_target(item["target"], "evidence.target")
    counts = _exact(item["counts"], {"full_reviews", "terminal_full_reviews", "fix_verifications", "model_calls"}, "evidence.counts")
    for name, count in counts.items():
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ProtocolError("protocol-invalid", f"evidence.counts.{name} is invalid")
    if not 1 <= counts["full_reviews"] <= FULL_REVIEW_LIMIT:
        raise ProtocolError("full-review-budget-exhausted", "full review budget is invalid")
    if counts["terminal_full_reviews"] not in {0, 1} or counts["terminal_full_reviews"] > counts["full_reviews"] - 1:
        raise ProtocolError("full-review-budget-exhausted", "terminal full budget is invalid")
    if counts["model_calls"] != counts["full_reviews"] + counts["fix_verifications"]:
        raise ProtocolError("model-call-accounting-invalid", "model call count does not match launched review phases")
    finding_state = _exact(item["finding_state"], {"open", "resolved", "rejected"}, "evidence.finding_state")
    if not all(isinstance(finding_state[name], list) for name in finding_state):
        raise ProtocolError("protocol-invalid", "evidence finding state is invalid")
    if item["hosted_obligation_id"] is not None:
        _fingerprint(item["hosted_obligation_id"], "evidence.hosted_obligation_id")
        if phase != "fix-verification":
            raise ProtocolError("protocol-invalid", "only fix verification can consume a hosted obligation")
    if not isinstance(item["report"], dict):
        raise ProtocolError("protocol-invalid", "evidence.report is invalid")
    _exact(item["metrics"], {"prompt_characters", "elapsed_seconds"}, "evidence.metrics")
    open_findings = bool(finding_state["open"])
    if item["parent_evidence_fingerprint"] is None:
        if item["terminal_state"] != _expected_result(None, phase, open_findings):
            raise ProtocolError("transition-invalid", "initial evidence terminal state is inconsistent")
    return item


def validate_transition(
    parent: dict[str, Any] | None,
    candidate: dict[str, Any],
    *,
    hosted_obligation: dict[str, Any] | None = None,
    lineage_reset_authorized: bool = False,
) -> dict[str, Any]:
    candidate = validate_evidence(candidate)
    if parent is None:
        if candidate["parent_evidence_fingerprint"] is not None:
            raise ProtocolError("parent-mismatch", "initial evidence cannot have a parent")
        expected = _expected_result(None, candidate["review_phase"], bool(candidate["finding_state"]["open"]))
    else:
        parent = validate_evidence(parent)
        if candidate["lineage_id"] != parent["lineage_id"]:
            if not lineage_reset_authorized:
                raise ProtocolError("lineage-reset-authority-required", "lineage identity changed without explicit authority")
            return validate_transition(None, candidate)
        if candidate["parent_evidence_fingerprint"] != parent["evidence_fingerprint"]:
            raise ProtocolError("parent-mismatch", "candidate evidence parent is stale")
        previous_target, current_target = parent["target"], candidate["target"]
        if previous_target["review_target_key"] != current_target["review_target_key"]:
            raise ProtocolError("lineage-reset-authority-required", "repository, base, or review scope changed")
        if previous_target["merge_base_sha"] != current_target["merge_base_sha"]:
            if not same_semantic_target(previous_target, current_target):
                raise ProtocolError("lineage-reset-authority-required", "rebase changed the canonical reviewed patch")
        if candidate["review_phase"] == "disposition" and current_target["head_sha"] != previous_target["head_sha"]:
            raise ProtocolError("action-not-allowed", "disposition requires an unchanged head")
        if candidate["review_phase"] == "fix-verification" and current_target["head_sha"] == previous_target["head_sha"]:
            raise ProtocolError("review-no-progress", "fix verification requires a new committed head")
        expected_counts = dict(parent["counts"])
        if candidate["review_phase"] == "terminal-full":
            expected_counts["full_reviews"] += 1
            expected_counts["terminal_full_reviews"] += 1
            expected_counts["model_calls"] += 1
        elif candidate["review_phase"] == "fix-verification":
            expected_counts["fix_verifications"] += 1
            expected_counts["model_calls"] += 1
        if candidate["counts"] != expected_counts:
            raise ProtocolError("counter-mismatch", "candidate counters are not the protocol projection")
        if hosted_obligation is not None:
            hosted_obligation = validate_hosted_obligation(hosted_obligation)
            if candidate["hosted_obligation_id"] != hosted_obligation["obligation_id"]:
                raise ProtocolError("obligation-mismatch", "candidate does not consume the reserved hosted obligation")
            if hosted_obligation["prior_evidence_fingerprint"] != parent["evidence_fingerprint"]:
                raise ProtocolError("obligation-mismatch", "hosted obligation is not bound to the prior evidence tip")
        elif candidate["hosted_obligation_id"] is not None:
            raise ProtocolError("obligation-mismatch", "candidate references an unavailable hosted obligation")
        expected = _expected_result(parent, candidate["review_phase"], bool(candidate["finding_state"]["open"]))
    if candidate["terminal_state"] != expected:
        raise ProtocolError("transition-invalid", "candidate terminal state is inconsistent with its phase")
    return candidate


def allowed_actions(parent: dict[str, Any] | None, *, hosted_obligation: bool = False) -> list[str]:
    if parent is None:
        return ["full"]
    parent = validate_evidence(parent)
    if hosted_obligation:
        return ["fix-verification"]
    if parent["terminal_state"] == "fix-required":
        return ["fix-verification", "disposition"]
    if parent["terminal_state"] == "verification-clean":
        return ["terminal-full"]
    return []


def next_projection(
    parent: dict[str, Any] | None,
    *,
    target: dict[str, Any],
    hosted_obligation: dict[str, Any] | None = None,
    blockers: list[str] | None = None,
) -> dict[str, Any]:
    target = validate_target(target)
    if hosted_obligation is not None:
        validate_hosted_obligation(hosted_obligation)
    blockers = sorted(set(blockers or []))
    actions = allowed_actions(parent, hosted_obligation=hosted_obligation is not None)
    action = actions[0] if actions and not blockers else None
    packet = None if action is None else {
        "protocol_version": PROTOCOL_VERSION,
        "action": action,
        "mode": "branch",
        "prompt_route": "managed-fix-verification" if action == "fix-verification" else f"managed-{action}",
        "target": target,
        "prior_evidence_fingerprint": parent["evidence_fingerprint"] if parent else None,
        "hosted_obligation_id": hosted_obligation["obligation_id"] if hosted_obligation else None,
    }
    completion = (
        "terminal-clean-or-terminal-composite-clean"
        if parent is None or parent["terminal_state"] not in {"terminal-clean", "terminal-composite-clean"}
        else "complete"
    )
    projection = {
        "protocol_version": PROTOCOL_VERSION,
        "action": action,
        "packet": packet,
        "allowed_transitions": actions,
        "completion_criterion": completion,
        "blockers": blockers,
    }
    projection["projection_fingerprint"] = fingerprint(projection)
    return projection


def validate_attempt_transition(records: list[dict[str, Any]], candidate: dict[str, Any]) -> None:
    state = candidate.get("state")
    if state not in ATTEMPT_STATES:
        raise ProtocolError("attempt-invalid", "attempt state is invalid")
    prior = records[-1]["state"] if records else None
    allowed = {
        None: {"prepared"},
        "prepared": {"model-started", "completed", "failed"},
        "model-started": {"completed", "failed"},
        "completed": set(),
        "failed": set(),
    }
    if state not in allowed[prior]:
        raise ProtocolError("attempt-transition-invalid", f"attempt cannot transition from {prior} to {state}")
    started = state == "model-started" or any(row["state"] == "model-started" for row in records)
    if candidate.get("model_call_started") is not started:
        raise ProtocolError("model-call-accounting-invalid", "model_call_started does not match attempt history")


def validate_invalid_output(value: Any, name: str = "invalid_output") -> dict[str, Any]:
    item = _exact(
        value,
        {
            "classification", "validator_code", "violated_rule",
            "output_fingerprint", "output_size_bytes", "output_truncated",
            "preview", "artifact_ref",
        },
        name,
    )
    if item["classification"] not in INVALID_OUTPUT_CLASSIFICATIONS:
        raise ProtocolError("attempt-invalid", f"{name}.classification is invalid")
    _text(item["validator_code"], f"{name}.validator_code")
    _text(item["violated_rule"], f"{name}.violated_rule")
    _fingerprint(item["output_fingerprint"], f"{name}.output_fingerprint")
    if (
        not isinstance(item["output_size_bytes"], int)
        or isinstance(item["output_size_bytes"], bool)
        or item["output_size_bytes"] < 0
    ):
        raise ProtocolError("attempt-invalid", f"{name}.output_size_bytes is invalid")
    if not isinstance(item["output_truncated"], bool):
        raise ProtocolError("attempt-invalid", f"{name}.output_truncated is invalid")
    if not isinstance(item["preview"], str) or len(item["preview"].encode("utf-8")) > 2048:
        raise ProtocolError("attempt-invalid", f"{name}.preview is invalid")
    _text(item["artifact_ref"], f"{name}.artifact_ref")
    return item


def validate_attempt_journal(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prior: dict[str, Any] | None = None
    identity: tuple[str, str] | None = None
    repair_seen = False
    for index, value in enumerate(records):
        name = f"attempt[{index}]"
        item = _exact(
            value,
            {
                "schema_version", "transition", "state", "model_call_started",
                "model_launch_count", "attempt_id", "reservation_id", "pid",
                "invalid_output", "prompt_fingerprint", "candidate_fingerprint",
                "operation_id", "parent_record_fingerprint",
            },
            name,
        )
        if item["schema_version"] != ATTEMPT_SCHEMA_VERSION:
            raise ProtocolError("attempt-invalid", f"{name}.schema_version is unsupported")
        transition = item["transition"]
        allowed = {
            None: {"prepared"},
            "prepared": {"model-started", "completed", "failed"},
            "model-started": {"repair-prepared", "completed", "failed"},
            "repair-prepared": {"repair-model-started", "failed"},
            "repair-model-started": {"completed", "failed"},
            "completed": set(),
            "failed": set(),
        }
        previous = prior["transition"] if prior else None
        if transition not in ATTEMPT_TRANSITIONS or transition not in allowed[previous]:
            raise ProtocolError("attempt-transition-invalid", f"{name} cannot follow {previous}")
        state_by_transition = {
            "prepared": "prepared",
            "model-started": "model-started",
            "repair-prepared": "model-started",
            "repair-model-started": "model-started",
            "completed": "completed",
            "failed": "failed",
        }
        if item["state"] != state_by_transition[transition]:
            raise ProtocolError("attempt-invalid", f"{name}.state is inconsistent")
        attempt_id = _fingerprint(item["attempt_id"], f"{name}.attempt_id")
        reservation_id = _fingerprint(item["reservation_id"], f"{name}.reservation_id")
        if identity is None:
            identity = (attempt_id, reservation_id)
        elif identity != (attempt_id, reservation_id):
            raise ProtocolError("attempt-invalid", f"{name} changed attempt identity")
        expected_parent = fingerprint(prior) if prior else None
        if item["parent_record_fingerprint"] != expected_parent:
            raise ProtocolError("attempt-invalid", f"{name}.parent_record_fingerprint is invalid")
        if transition == "prepared":
            expected_launches = 0
        elif transition == "model-started":
            expected_launches = 1
        elif transition == "repair-model-started":
            expected_launches = 2
        else:
            expected_launches = prior["model_launch_count"] if prior else 0
        if (
            not isinstance(item["model_launch_count"], int)
            or isinstance(item["model_launch_count"], bool)
            or item["model_launch_count"] != expected_launches
        ):
            raise ProtocolError("model-call-accounting-invalid", f"{name}.model_launch_count is invalid")
        if item["model_call_started"] is not (expected_launches > 0):
            raise ProtocolError("model-call-accounting-invalid", f"{name}.model_call_started is invalid")
        if item["pid"] is not None and (
            not isinstance(item["pid"], int) or isinstance(item["pid"], bool) or item["pid"] < 1
        ):
            raise ProtocolError("attempt-invalid", f"{name}.pid is invalid")
        if transition in {"model-started", "repair-model-started"}:
            if item["pid"] is None:
                raise ProtocolError("attempt-invalid", f"{name}.pid is required")
        elif item["pid"] is not None:
            raise ProtocolError("attempt-invalid", f"{name}.pid is forbidden")
        for field in ("prompt_fingerprint", "candidate_fingerprint"):
            if item[field] is not None:
                _fingerprint(item[field], f"{name}.{field}")
        if item["operation_id"] is not None and (
            not isinstance(item["operation_id"], str)
            or not re.fullmatch(r"[0-9a-f]{32}", item["operation_id"])
        ):
            raise ProtocolError("attempt-invalid", f"{name}.operation_id is invalid")
        if transition in {"repair-prepared", "failed"} and item["invalid_output"] is not None:
            validate_invalid_output(item["invalid_output"], f"{name}.invalid_output")
        elif item["invalid_output"] is not None:
            raise ProtocolError("attempt-invalid", f"{name}.invalid_output is forbidden")
        if transition == "repair-prepared":
            if repair_seen or item["prompt_fingerprint"] is None or item["invalid_output"] is None:
                raise ProtocolError("attempt-invalid", "duplicate or incomplete repair preparation")
            repair_seen = True
        if transition in {"model-started", "repair-model-started"} and item["prompt_fingerprint"] is None:
            raise ProtocolError("attempt-invalid", f"{name}.prompt_fingerprint is required")
        if transition == "repair-model-started" and not repair_seen:
            raise ProtocolError("attempt-invalid", "repair launch lacks invalid-output preparation")
        if transition == "completed" and (
            item["candidate_fingerprint"] is None or item["operation_id"] is None
        ):
            raise ProtocolError("attempt-invalid", "completed attempt lacks candidate identity")
        if transition != "completed" and (
            item["candidate_fingerprint"] is not None or item["operation_id"] is not None
        ):
            raise ProtocolError("attempt-invalid", f"{name} has premature candidate identity")
        prior = item
    return records
