"""Closed typed owned-operation protocol for managed AutoReview work."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

import autoreview_protocol as protocol


OWNER_VERSION = "5.0.0"
REQUEST_SCHEMA = "autoreview-operation-request:v1"
RESULT_SCHEMA = "autoreview-operation-result:v1"
START_RECEIPT_SCHEMA = "implement-feature-owned-operation-start:v1"
VALIDATION_DESCRIPTOR_SCHEMA = "owned-operation-validation-descriptor:v1"
OPERATIONS = frozenset({"run-phase", "reconcile-attempt"})
OUTCOMES = {
    "run-phase": frozenset({"terminal-clean", "terminal-composite-clean", "verification-clean", "fix-required", "failed"}),
    "reconcile-attempt": frozenset({"terminal-clean", "terminal-composite-clean", "verification-clean", "fix-required", "interrupted", "consumed-failed"}),
}
LEGAL_STATUS = {
    "run-phase": {"terminal-clean": "completed", "terminal-composite-clean": "completed", "verification-clean": "completed", "fix-required": "completed", "failed": "failed"},
    "reconcile-attempt": {"terminal-clean": "completed", "terminal-composite-clean": "completed", "verification-clean": "completed", "fix-required": "completed", "interrupted": "blocked", "consumed-failed": "failed"},
}
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
OP_RE = re.compile(r"^[0-9a-f]{32}$")


class OperationError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def _exact(value: Any, fields: set[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise OperationError(f"{name} has unknown or missing fields")
    return value


def _sha(value: Any, name: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        raise OperationError(f"{name} must be a sha256 fingerprint")
    return value


def validate_authority(value: Any) -> dict[str, Any]:
    item = _exact(value, {
        "ledger", "root_id", "expected_claim_fingerprint", "expected_generation",
        "expected_state_fingerprint", "task_key", "delivery_key", "task_state",
        "task_observation_fingerprint", "revision_key", "managed_checkout_fingerprint",
    }, "authority")
    for name in ("ledger", "root_id", "task_key", "delivery_key", "task_state"):
        if not isinstance(item[name], str) or not item[name]:
            raise OperationError(f"authority.{name} must be non-empty text")
    if not item["ledger"].startswith("/"):
        raise OperationError("authority.ledger must be absolute")
    if not isinstance(item["expected_generation"], int) or isinstance(item["expected_generation"], bool) or item["expected_generation"] < 1:
        raise OperationError("authority.expected_generation is invalid")
    for name in ("expected_claim_fingerprint", "expected_state_fingerprint", "revision_key", "managed_checkout_fingerprint"):
        _sha(item[name], f"authority.{name}")
    _sha(item["task_observation_fingerprint"], "authority.task_observation_fingerprint", nullable=True)
    return item


def validate_orchestration_descriptor(
    value: Any, hosted_obligation: dict[str, Any] | None
) -> dict[str, Any] | None:
    if value is None:
        if hosted_obligation is not None:
            raise OperationError("hosted obligation requires an orchestration descriptor")
        return None
    item = _exact(
        value,
        {"hosted_obligation_ref", "source_result_fingerprint"},
        "orchestration_descriptor",
    )
    if hosted_obligation is None:
        raise OperationError("orchestration descriptor requires a hosted obligation")
    if not isinstance(item["hosted_obligation_ref"], str) or not item["hosted_obligation_ref"]:
        raise OperationError("orchestration descriptor obligation ref is invalid")
    _sha(item["source_result_fingerprint"], "orchestration_descriptor.source_result_fingerprint")
    return item


def validate_lineage_reset_authority(
    value: Any,
    prior_evidence: dict[str, Any] | None,
    target: dict[str, Any],
) -> dict[str, Any] | None:
    reset_required = prior_evidence is not None and (
        prior_evidence["target"]["review_target_key"] != target["review_target_key"]
        or (
            prior_evidence["target"]["merge_base_sha"] != target["merge_base_sha"]
            and not protocol.same_semantic_target(prior_evidence["target"], target)
        )
    )
    if value is None:
        if reset_required:
            raise OperationError("changed semantic target requires explicit lineage reset authority")
        return None
    item = _exact(
        value,
        {
            "schema", "authorization", "prior_lineage_id",
            "prior_evidence_fingerprint", "next_target_fingerprint",
            "evidence_ref", "authority_fingerprint",
        },
        "lineage_reset_authority",
    )
    if item["schema"] != "autoreview-lineage-reset-authority:v1":
        raise OperationError("lineage reset authority schema is invalid")
    if item["authorization"] != "granted-by-authorized-user":
        raise OperationError("lineage reset authority is not explicitly authorized")
    if prior_evidence is None:
        raise OperationError("initial AutoReview cannot carry lineage reset authority")
    if not reset_required:
        raise OperationError("lineage reset authority is not required for this target change")
    for name in (
        "prior_lineage_id", "prior_evidence_fingerprint",
        "next_target_fingerprint", "authority_fingerprint",
    ):
        _sha(item[name], f"lineage_reset_authority.{name}")
    if (
        item["prior_lineage_id"] != prior_evidence["lineage_id"]
        or item["prior_evidence_fingerprint"] != prior_evidence["evidence_fingerprint"]
        or item["next_target_fingerprint"] != fingerprint(target)
    ):
        raise OperationError("lineage reset authority binding is stale")
    if not isinstance(item["evidence_ref"], str) or not item["evidence_ref"]:
        raise OperationError("lineage reset authority evidence ref is invalid")
    if item["authority_fingerprint"] != fingerprint(
        {key: value for key, value in item.items() if key != "authority_fingerprint"}
    ):
        raise OperationError("lineage reset authority fingerprint is invalid")
    return item


def _phase_projection(prior_evidence: dict[str, Any] | None, target: dict[str, Any], hosted_obligation: dict[str, Any] | None, requested_phase: str, *, lineage_reset_authorized: bool = False) -> dict[str, Any]:
    projection_parent = None if lineage_reset_authorized else prior_evidence
    projection = protocol.next_projection(projection_parent, target=target, hosted_obligation=hosted_obligation)
    if requested_phase not in projection["allowed_transitions"]:
        raise OperationError("requested phase is not allowed by the AutoReview protocol")
    packet = {
        "protocol_version": protocol.PROTOCOL_VERSION,
        "action": requested_phase,
        "mode": "branch",
        "prompt_route": "managed-fix-verification" if requested_phase == "fix-verification" else f"managed-{requested_phase}",
        "target": target,
        "prior_evidence_fingerprint": projection_parent["evidence_fingerprint"] if projection_parent else None,
        "hosted_obligation_id": hosted_obligation["obligation_id"] if hosted_obligation else None,
    }
    projection = {**projection, "action": requested_phase, "packet": packet}
    projection["projection_fingerprint"] = fingerprint({key: value for key, value in projection.items() if key != "projection_fingerprint"})
    return projection


def build_request(*, operation: str, controller_envelope: dict[str, Any], target: dict[str, Any], prior_evidence: dict[str, Any] | None, hosted_obligation: dict[str, Any] | None, requested_phase: str, orchestration_descriptor: dict[str, Any] | None = None, lineage_reset_authority: dict[str, Any] | None = None, started_operation: dict[str, Any] | None = None) -> dict[str, Any]:
    if operation not in OPERATIONS:
        raise OperationError("operation is unsupported")
    template = controller_envelope.get("packet_template") if isinstance(controller_envelope, dict) else None
    if not isinstance(template, dict) or template.get("packet_kind") != "owned-operation":
        raise OperationError("controller envelope is not an owned operation")
    if template.get("operation") != {"owner": "autoreview", "name": operation, "contract_version": "1.0.0"}:
        raise OperationError("controller operation does not match AutoReview")
    authority = validate_authority(template.get("authority_binding"))
    projection_fp = controller_envelope.get("projection_fingerprint")
    _sha(projection_fp, "controller_envelope.projection_fingerprint")
    if prior_evidence is not None:
        protocol.validate_evidence(prior_evidence)
    if hosted_obligation is not None:
        protocol.validate_hosted_obligation(hosted_obligation)
    target = protocol.validate_target(target)
    orchestration_descriptor = validate_orchestration_descriptor(
        orchestration_descriptor, hosted_obligation
    )
    lineage_reset_authority = validate_lineage_reset_authority(
        lineage_reset_authority, prior_evidence, target
    )
    projection = _phase_projection(
        prior_evidence, target, hosted_obligation, requested_phase,
        lineage_reset_authorized=lineage_reset_authority is not None,
    )
    if operation == "run-phase" and started_operation is not None:
        raise OperationError("run-phase cannot carry a prior started operation")
    if operation == "reconcile-attempt":
        started_operation = validate_started_operation(started_operation)
        started_request = validate_request(started_operation["request"])
        if started_request["operation"] != "run-phase" or started_request["target"] != target or started_request["prior_evidence"] != prior_evidence or started_request["hosted_obligation"] != hosted_obligation or started_request["orchestration_descriptor"] != orchestration_descriptor or started_request["lineage_reset_authority"] != lineage_reset_authority or started_request["requested_phase"] != requested_phase:
            raise OperationError("attempt reconciliation differs from its started run request")
    value = {
        "schema": REQUEST_SCHEMA, "owner_version": OWNER_VERSION,
        "operation": operation, "operation_id": "0" * 32,
        "controller_envelope": controller_envelope,
        "controller_projection_fingerprint": projection_fp,
        "authority": authority, "target": target,
        "prior_evidence": prior_evidence, "hosted_obligation": hosted_obligation,
        "orchestration_descriptor": orchestration_descriptor,
        "lineage_reset_authority": lineage_reset_authority,
        "requested_phase": requested_phase, "phase_projection": projection, "started_operation": started_operation,
        "request_fingerprint": "0" * 64,
    }
    value["operation_id"] = fingerprint({k: v for k, v in value.items() if k not in {"operation_id", "request_fingerprint"}})[:32]
    value["request_fingerprint"] = fingerprint({k: v for k, v in value.items() if k != "request_fingerprint"})
    return validate_request(value)


def validate_request(value: Any) -> dict[str, Any]:
    item = _exact(value, {
        "schema", "owner_version", "operation", "operation_id", "controller_envelope",
        "controller_projection_fingerprint", "authority", "target", "prior_evidence",
        "hosted_obligation", "orchestration_descriptor", "lineage_reset_authority",
        "requested_phase", "phase_projection", "started_operation", "request_fingerprint",
    }, "request")
    if item["schema"] != REQUEST_SCHEMA or item["owner_version"] != OWNER_VERSION or item["operation"] not in OPERATIONS:
        raise OperationError("request schema, version, or operation is invalid")
    if not isinstance(item["operation_id"], str) or not OP_RE.fullmatch(item["operation_id"]):
        raise OperationError("request.operation_id is invalid")
    authority = validate_authority(item["authority"])
    _sha(item["controller_projection_fingerprint"], "request.controller_projection_fingerprint")
    envelope = item["controller_envelope"]
    if not isinstance(envelope, dict) or envelope.get("projection_fingerprint") != item["controller_projection_fingerprint"]:
        raise OperationError("request controller projection fingerprint differs")
    template = envelope.get("packet_template")
    if not isinstance(template, dict) or template.get("authority_binding") != authority or template.get("operation") != {"owner": "autoreview", "name": item["operation"], "contract_version": "1.0.0"}:
        raise OperationError("request differs from controller operation authority")
    target = protocol.validate_target(item["target"])
    if item["prior_evidence"] is not None:
        protocol.validate_evidence(item["prior_evidence"])
    if item["hosted_obligation"] is not None:
        protocol.validate_hosted_obligation(item["hosted_obligation"])
    validate_orchestration_descriptor(
        item["orchestration_descriptor"], item["hosted_obligation"]
    )
    validate_lineage_reset_authority(
        item["lineage_reset_authority"], item["prior_evidence"], target
    )
    if not isinstance(item["requested_phase"], str):
        raise OperationError("request.requested_phase is invalid")
    expected_projection = _phase_projection(
        item["prior_evidence"], target, item["hosted_obligation"],
        item["requested_phase"],
        lineage_reset_authorized=item["lineage_reset_authority"] is not None,
    )
    if item["phase_projection"] != expected_projection:
        raise OperationError("request phase projection is not protocol-derived")
    if item["operation"] == "run-phase" and item["started_operation"] is not None:
        raise OperationError("run-phase request cannot carry started operation identity")
    if item["operation"] == "reconcile-attempt":
        started = validate_started_operation(item["started_operation"])
        started_request = validate_request(started["request"])
        if started_request["operation"] != "run-phase" or started_request["target"] != target or started_request["prior_evidence"] != item["prior_evidence"] or started_request["hosted_obligation"] != item["hosted_obligation"] or started_request["orchestration_descriptor"] != item["orchestration_descriptor"] or started_request["lineage_reset_authority"] != item["lineage_reset_authority"] or started_request["requested_phase"] != item["requested_phase"]:
            raise OperationError("reconciliation started operation does not match request lineage")
    expected_id = fingerprint({k: v for k, v in item.items() if k not in {"operation_id", "request_fingerprint"}})[:32]
    if item["operation_id"] != expected_id or item["request_fingerprint"] != fingerprint({k: v for k, v in item.items() if k != "request_fingerprint"}):
        raise OperationError("request identity is invalid")
    return item


def validate_started_operation(value: Any) -> dict[str, Any]:
    item = _exact(value, {"request", "start_receipt", "attempt_id", "attempt_journal", "attempt_journal_fingerprint", "model_call_started", "model_launch_count"}, "started_operation")
    request = validate_request(item["request"])
    if request["operation"] != "run-phase":
        raise OperationError("started operation must be a run-phase request")
    receipt = validate_start_receipt(item["start_receipt"], request)
    for name in ("attempt_id", "attempt_journal_fingerprint"):
        _sha(item[name], f"started_operation.{name}")
    journal = protocol.validate_attempt_journal(item["attempt_journal"])
    if not journal or item["attempt_journal_fingerprint"] != fingerprint(journal):
        raise OperationError("started operation journal fingerprint is invalid")
    expected_attempt = fingerprint({"operation_id": request["operation_id"], "request_fingerprint": request["request_fingerprint"], "start_receipt_fingerprint": receipt["receipt_fingerprint"]})
    if item["attempt_id"] != expected_attempt:
        raise OperationError("started operation attempt identity is invalid")
    if any(row["attempt_id"] != expected_attempt or row["reservation_id"] != receipt["receipt_fingerprint"] for row in journal):
        raise OperationError("started operation journal has unrelated identity")
    if not isinstance(item["model_call_started"], bool) or not isinstance(item["model_launch_count"], int) or isinstance(item["model_launch_count"], bool) or item["model_launch_count"] not in {0, 1, 2}:
        raise OperationError("started operation launch accounting is invalid")
    if item["model_call_started"] != (item["model_launch_count"] > 0):
        raise OperationError("started operation launch accounting disagrees")
    last = journal[-1]
    if item["model_call_started"] != last["model_call_started"] or item["model_launch_count"] != last["model_launch_count"]:
        raise OperationError("started operation launch accounting differs from journal")
    return item


def validate_start_receipt(value: Any, request: dict[str, Any]) -> dict[str, Any]:
    item = _exact(value, {"schema", "owner", "operation", "operation_id", "request_fingerprint", "journal_id", "started_generation", "started_state_fingerprint", "receipt_fingerprint"}, "start_receipt")
    if item["schema"] != START_RECEIPT_SCHEMA or item["owner"] != "autoreview":
        raise OperationError("start receipt schema or owner is invalid")
    for name in ("operation", "operation_id", "request_fingerprint"):
        if item[name] != request[name]: raise OperationError(f"start receipt {name} differs")
    for name in ("journal_id", "started_state_fingerprint", "receipt_fingerprint"):
        _sha(item[name], f"start_receipt.{name}")
    if not isinstance(item["started_generation"], int) or item["started_generation"] < request["authority"]["expected_generation"]:
        raise OperationError("start receipt generation is invalid")
    if item["receipt_fingerprint"] != fingerprint({k: v for k, v in item.items() if k != "receipt_fingerprint"}):
        raise OperationError("start receipt fingerprint is invalid")
    return item


def validate_facts(operation: str, outcome: str, value: Any) -> dict[str, Any]:
    item = _exact(value, {"attempt_id", "model_call_started", "model_launch_count", "candidate_fingerprint", "evidence", "attempt_journal", "attempt_journal_fingerprint"}, "facts")
    for name in ("attempt_id", "attempt_journal_fingerprint"):
        _sha(item[name], f"facts.{name}")
    _sha(item["candidate_fingerprint"], "facts.candidate_fingerprint", nullable=outcome in {"failed", "interrupted", "consumed-failed"})
    if not isinstance(item["model_call_started"], bool) or not isinstance(item["model_launch_count"], int) or isinstance(item["model_launch_count"], bool) or item["model_launch_count"] not in {0, 1, 2}:
        raise OperationError("facts model launch accounting is invalid")
    if item["model_call_started"] != (item["model_launch_count"] > 0):
        raise OperationError("facts model_call_started disagrees with launch count")
    journal = protocol.validate_attempt_journal(item["attempt_journal"])
    if not journal or item["attempt_journal_fingerprint"] != fingerprint(journal):
        raise OperationError("facts attempt journal fingerprint is invalid")
    last = journal[-1]
    if any(row["attempt_id"] != item["attempt_id"] for row in journal):
        raise OperationError("facts attempt identity differs from journal")
    if item["model_call_started"] != last["model_call_started"] or item["model_launch_count"] != last["model_launch_count"]:
        raise OperationError("facts launch accounting differs from journal")
    if item["model_launch_count"] == 2 and outcome not in {"terminal-clean", "terminal-composite-clean", "verification-clean", "fix-required", "failed", "consumed-failed"}:
        raise OperationError("second launch is allowed only for bounded invalid-output repair")
    if outcome in protocol.TERMINAL_STATES:
        evidence = protocol.validate_evidence(item["evidence"])
        if evidence["terminal_state"] != outcome:
            raise OperationError("result outcome differs from evidence terminal state")
        if last["state"] != "completed" or last["candidate_fingerprint"] != evidence["evidence_fingerprint"]:
            raise OperationError("terminal evidence differs from completed attempt journal")
    elif item["evidence"] is not None:
        raise OperationError("non-evidence outcome cannot carry evidence")
    elif outcome == "interrupted":
        if last["state"] != "model-started":
            raise OperationError("interrupted outcome requires an in-flight started journal")
    elif last["state"] != "failed":
        raise OperationError("failed outcome requires a failed attempt journal")
    if operation == "reconcile-attempt" and outcome == "interrupted" and not item["model_call_started"]:
        raise OperationError("interrupted reconciliation requires a prior model launch")
    return item


def build_result(*, request: dict[str, Any], start_receipt: dict[str, Any], status: str, outcome: str, facts: dict[str, Any], evidence_ref: str) -> dict[str, Any]:
    request = validate_request(request)
    receipt_request = request if request["operation"] == "run-phase" else validate_request(validate_started_operation(request["started_operation"])["request"])
    start_receipt = validate_start_receipt(start_receipt, receipt_request)
    correlation_request = request if request["operation"] == "run-phase" else validate_request(validate_started_operation(request["started_operation"])["request"])
    value = {"schema": RESULT_SCHEMA, "owner_version": OWNER_VERSION, "operation": request["operation"], "operation_id": request["operation_id"], "request_fingerprint": request["request_fingerprint"], "start_receipt_fingerprint": start_receipt["receipt_fingerprint"], "status": status, "outcome": outcome, "facts": facts, "orchestration_descriptor": correlation_request["orchestration_descriptor"], "lineage_reset_authority_fingerprint": correlation_request["lineage_reset_authority"]["authority_fingerprint"] if correlation_request["lineage_reset_authority"] else None, "evidence_ref": evidence_ref, "result_fingerprint": "0" * 64}
    value["result_fingerprint"] = fingerprint({k: v for k, v in value.items() if k != "result_fingerprint"})
    return validate_result(value)


def validate_result(value: Any) -> dict[str, Any]:
    item = _exact(value, {"schema", "owner_version", "operation", "operation_id", "request_fingerprint", "start_receipt_fingerprint", "status", "outcome", "facts", "orchestration_descriptor", "lineage_reset_authority_fingerprint", "evidence_ref", "result_fingerprint"}, "result")
    if item["schema"] != RESULT_SCHEMA or item["owner_version"] != OWNER_VERSION or item["operation"] not in OPERATIONS or item["outcome"] not in OUTCOMES[item["operation"]]:
        raise OperationError("result schema, version, operation, or outcome is invalid")
    if LEGAL_STATUS[item["operation"]][item["outcome"]] != item["status"]:
        raise OperationError("result status and outcome are inconsistent")
    if not isinstance(item["operation_id"], str) or not OP_RE.fullmatch(item["operation_id"]): raise OperationError("result operation_id is invalid")
    for name in ("request_fingerprint", "start_receipt_fingerprint", "result_fingerprint"):
        _sha(item[name], f"result.{name}")
    if not isinstance(item["evidence_ref"], str) or not item["evidence_ref"]: raise OperationError("result evidence_ref is invalid")
    validate_facts(item["operation"], item["outcome"], item["facts"])
    if item["orchestration_descriptor"] is not None:
        _exact(
            item["orchestration_descriptor"],
            {"hosted_obligation_ref", "source_result_fingerprint"},
            "result.orchestration_descriptor",
        )
        if not isinstance(item["orchestration_descriptor"]["hosted_obligation_ref"], str) or not item["orchestration_descriptor"]["hosted_obligation_ref"]:
            raise OperationError("result orchestration descriptor ref is invalid")
        _sha(item["orchestration_descriptor"]["source_result_fingerprint"], "result.orchestration_descriptor.source_result_fingerprint")
    _sha(item["lineage_reset_authority_fingerprint"], "result.lineage_reset_authority_fingerprint", nullable=True)
    if item["result_fingerprint"] != fingerprint({k: v for k, v in item.items() if k != "result_fingerprint"}): raise OperationError("result fingerprint is invalid")
    return item


def validate_result_for_request(result_value: Any, request_value: Any) -> dict[str, Any]:
    result = validate_result(result_value); request = validate_request(request_value)
    for name in ("operation", "operation_id", "request_fingerprint"):
        if result[name] != request[name]: raise OperationError(f"result {name} does not match request")
    evidence = result["facts"]["evidence"]
    correlation_request = request
    if request["operation"] == "reconcile-attempt":
        started = validate_started_operation(request["started_operation"])
        correlation_request = validate_request(started["request"])
        facts = result["facts"]
        if result["start_receipt_fingerprint"] != started["start_receipt"]["receipt_fingerprint"]:
            raise OperationError("reconciliation result start receipt differs from started operation")
        if facts["attempt_id"] != started["attempt_id"] or facts["attempt_journal"] != started["attempt_journal"] or facts["attempt_journal_fingerprint"] != started["attempt_journal_fingerprint"]:
            raise OperationError("reconciliation result attempt identity differs from started operation")
        if facts["model_call_started"] != started["model_call_started"] or facts["model_launch_count"] != started["model_launch_count"]:
            raise OperationError("reconciliation result launch accounting differs from started operation")
    else:
        expected_attempt = fingerprint({"operation_id": request["operation_id"], "request_fingerprint": request["request_fingerprint"], "start_receipt_fingerprint": result["start_receipt_fingerprint"]})
        if result["facts"]["attempt_id"] != expected_attempt:
            raise OperationError("result attempt identity does not match request and start receipt")
        if any(row["reservation_id"] != result["start_receipt_fingerprint"] for row in result["facts"]["attempt_journal"]):
            raise OperationError("result attempt journal does not match start receipt")
    if evidence is not None:
        protocol.validate_transition(
            correlation_request["prior_evidence"], evidence,
            hosted_obligation=correlation_request["hosted_obligation"],
            lineage_reset_authorized=correlation_request["lineage_reset_authority"] is not None,
        )
        if evidence["target"] != correlation_request["target"]:
            raise OperationError("result evidence target does not match request")
        if evidence["review_phase"] != correlation_request["phase_projection"]["action"]:
            raise OperationError("result evidence phase does not match request projection")
        expected_parent = (
            None if correlation_request["lineage_reset_authority"] is not None
            else correlation_request["prior_evidence"]["evidence_fingerprint"]
            if correlation_request["prior_evidence"] else None
        )
        if evidence["parent_evidence_fingerprint"] != expected_parent:
            raise OperationError("result evidence parent does not match request")
        expected_obligation = correlation_request["hosted_obligation"]["obligation_id"] if correlation_request["hosted_obligation"] else None
        if evidence["hosted_obligation_id"] != expected_obligation:
            raise OperationError("result evidence obligation does not match request")
    if result["orchestration_descriptor"] != correlation_request["orchestration_descriptor"]:
        raise OperationError("result orchestration descriptor does not match request")
    expected_reset = (
        correlation_request["lineage_reset_authority"]["authority_fingerprint"]
        if correlation_request["lineage_reset_authority"] else None
    )
    if result["lineage_reset_authority_fingerprint"] != expected_reset:
        raise OperationError("result lineage reset authority does not match request")
    return result


def validation_descriptor(
    request_value: Any, result_value: Any | None = None,
) -> dict[str, Any]:
    """Return the narrow orchestration projection of a validated owner operation."""

    request = validate_request(request_value)
    start_request = request
    start_receipt_fingerprint = None
    if request["operation"] == "reconcile-attempt":
        started = validate_started_operation(request["started_operation"])
        start_request = validate_request(started["request"])
        start_receipt_fingerprint = started["start_receipt"]["receipt_fingerprint"]
    result_effect = None
    if result_value is not None:
        result = validate_result_for_request(result_value, request)
        result_effect = {
            "evidence_produced": result["facts"]["evidence"] is not None,
            "orchestration_descriptor": result["orchestration_descriptor"],
            "effective_result": {"operation": result["operation"], "outcome": result["outcome"]},
        }
    return {
        "schema": VALIDATION_DESCRIPTOR_SCHEMA,
        "owner": "autoreview",
        "operation": request["operation"],
        "operation_id": request["operation_id"],
        "request_fingerprint": request["request_fingerprint"],
        "start_identity": {
            "owner": "autoreview",
            "operation": start_request["operation"],
            "operation_id": start_request["operation_id"],
            "request_fingerprint": start_request["request_fingerprint"],
            "start_receipt_fingerprint": start_receipt_fingerprint,
        },
        "prior_result_effect": None,
        "followup_effect": None,
        "result_effect": result_effect,
    }
