"""Closed typed operation protocol for managed GitStack review work."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from . import __version__
from .review_request import validate_receipt
from .review_thread import validate_reply_receipt, validate_resolution_receipt
from .terminal_evidence import validate_terminal_evidence_receipt


REQUEST_SCHEMA = "gitstack-review-operation-request:v1"
RESULT_SCHEMA = "gitstack-review-operation-result:v1"
START_RECEIPT_SCHEMA = "implement-feature-owned-operation-start:v1"
VALIDATION_DESCRIPTOR_SCHEMA = "owned-operation-validation-descriptor:v1"
OPERATIONS = frozenset({
    "request", "wait", "warning", "reply", "resolve",
    "reconcile-mutation", "reconcile-terminal",
})
OUTCOMES = {
    "request": frozenset({"created", "recognized-existing"}),
    "wait": frozenset({"clean", "findings", "pending-at-deadline", "request-correlation-failure", "provider-failure"}),
    "warning": frozenset({"posted", "recognized-existing"}),
    "reply": frozenset({"posted", "recognized-existing"}),
    "resolve": frozenset({"resolved", "already-resolved"}),
    "reconcile-mutation": frozenset({"completed-from-readback", "missing", "conflicting", "ambiguous"}),
    "reconcile-terminal": frozenset({"clean-verified", "findings-verified"}),
}
STATUSES = frozenset({"completed", "failed", "ambiguous", "blocked"})
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
OPERATION_ID_RE = re.compile(r"^[0-9a-f]{32}$")
HEAD_RE = re.compile(r"^[0-9a-f]{40}$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9](?:[A-Za-z0-9._-]{0,99})$")
UTC_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
LEGAL_STATUS_OUTCOME = {
    "request": {"created": "completed", "recognized-existing": "completed"},
    "wait": {"clean": "completed", "findings": "completed", "pending-at-deadline": "completed", "request-correlation-failure": "failed", "provider-failure": "failed"},
    "warning": {"posted": "completed", "recognized-existing": "completed"},
    "reply": {"posted": "completed", "recognized-existing": "completed"},
    "resolve": {"resolved": "completed", "already-resolved": "completed"},
    "reconcile-mutation": {"completed-from-readback": "completed", "missing": "blocked", "conflicting": "ambiguous", "ambiguous": "ambiguous"},
    "reconcile-terminal": {"clean-verified": "completed", "findings-verified": "completed"},
}


class OperationError(ValueError):
    """Strict operation protocol rejection."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _exact(value: Any, fields: set[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise OperationError(f"{name} has unknown or missing fields")
    return value


def _sha(value: Any, name: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise OperationError(f"{name} must be a sha256 fingerprint")
    return value


def validate_authority(value: Any) -> dict[str, Any]:
    item = _exact(value, {
        "ledger", "root_id", "expected_claim_fingerprint", "expected_generation",
        "expected_state_fingerprint",
        "task_key", "delivery_key", "task_state", "task_observation_fingerprint",
        "revision_key", "managed_checkout_fingerprint",
    }, "authority")
    for name in ("ledger", "root_id", "task_key", "delivery_key", "task_state"):
        if not isinstance(item[name], str) or not item[name]:
            raise OperationError(f"authority.{name} must be non-empty text")
    if not item["ledger"].startswith("/"):
        raise OperationError("authority.ledger must be absolute")
    if not isinstance(item["expected_generation"], int) or isinstance(item["expected_generation"], bool) or item["expected_generation"] < 1:
        raise OperationError("authority.expected_generation must be positive")
    for name in (
        "expected_claim_fingerprint", "expected_state_fingerprint",
        "revision_key", "managed_checkout_fingerprint",
    ):
        _sha(item[name], f"authority.{name}")
    _sha(item["task_observation_fingerprint"], "authority.task_observation_fingerprint", nullable=True)
    return item


def validate_target(value: Any) -> dict[str, Any]:
    item = _exact(value, {"repository", "pr_number", "head_sha", "provider"}, "target")
    if not isinstance(item["repository"], str) or not REPOSITORY_RE.fullmatch(item["repository"]):
        raise OperationError("target.repository is invalid")
    if not isinstance(item["pr_number"], int) or isinstance(item["pr_number"], bool) or item["pr_number"] < 1:
        raise OperationError("target.pr_number is invalid")
    if not isinstance(item["head_sha"], str) or not HEAD_RE.fullmatch(item["head_sha"]):
        raise OperationError("target.head_sha is invalid")
    if item["provider"] != "codex":
        raise OperationError("target.provider is unsupported")
    return item


def _validate_input(operation: str, value: Any, target: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "request": {"request_key"},
        "wait": {"request_receipt", "wait_started_at", "wait_deadline"},
        "warning": {"request_receipt", "prior_pending_result", "body_file", "body_fingerprint"},
        "reply": {"request_receipt", "prior_findings_result", "followup_obligation", "finding_comment_id", "thread_id", "thread_fingerprint", "body_file", "body_fingerprint"},
        "resolve": {"request_receipt", "prior_reply_result", "followup_obligation", "reply_receipt"},
        "reconcile-mutation": {"started_operation"},
        "reconcile-terminal": {"request_receipt", "prior_failed_result"},
    }[operation]
    item = _exact(value, fields, "input")
    if "request_receipt" in item:
        try:
            validate_receipt(
                item["request_receipt"], provider=target["provider"],
                repository=target["repository"], pr_number=target["pr_number"],
                expected_head=target["head_sha"],
            )
        except ValueError as exc:
            raise OperationError(str(exc)) from exc
    for name in ("body_fingerprint", "thread_fingerprint"):
        if name in item:
            _sha(item[name], f"input.{name}")
    for name in ("body_file", "thread_id"):
        if name in item and (not isinstance(item[name], str) or not item[name]):
            raise OperationError(f"input.{name} must be non-empty text")
    if "body_file" in item and not item["body_file"].startswith("/"):
        raise OperationError("input.body_file must be absolute")
    if "finding_comment_id" in item and (not isinstance(item["finding_comment_id"], int) or isinstance(item["finding_comment_id"], bool) or item["finding_comment_id"] < 1):
        raise OperationError("input.finding_comment_id is invalid")
    if operation == "request":
        _sha(item["request_key"], "input.request_key")
    if operation == "wait":
        started = _utc_timestamp(item["wait_started_at"], "input.wait_started_at")
        deadline = _utc_timestamp(item["wait_deadline"], "input.wait_deadline")
        if deadline != started + timedelta(minutes=45):
            raise OperationError("input.wait_deadline must equal wait_started_at plus exactly 45 minutes")
    if operation == "warning":
        prior = validate_result(item["prior_pending_result"])
        if (
            prior["operation"] != "wait"
            or prior["status"] != "completed"
            or prior["outcome"] != "pending-at-deadline"
            or prior["facts"]["request_receipt"] != item["request_receipt"]
        ):
            raise OperationError("warning prior result is not the exact pending request lineage")
    if operation == "reply":
        prior = validate_result(item["prior_findings_result"])
        if prior["operation"] != "wait" or prior["outcome"] != "findings":
            raise OperationError("reply prior result is not findings")
        try:
            finding_index = prior["facts"]["finding_comment_ids"].index(item["finding_comment_id"])
        except ValueError:
            finding_index = -1
        expected_obligations = _followup_effect_for_result(prior)["creates"]
        if (
            prior["facts"]["request_receipt"] != item["request_receipt"]
            or finding_index < 0
            or item["followup_obligation"] != expected_obligations[finding_index]
        ):
            raise OperationError("reply does not bind one exact findings follow-up obligation")
    if operation == "resolve":
        prior = validate_result(item["prior_reply_result"])
        if (
            prior["operation"] != "reply" or prior["outcome"] not in {"posted", "recognized-existing"}
            or prior["facts"]["request_receipt"] != item["request_receipt"]
            or prior["facts"]["reply_receipt"] != item["reply_receipt"]
            or item["followup_obligation"] not in _followup_effect_for_result(prior)["creates"]
        ):
            raise OperationError("resolution does not bind one exact replied follow-up obligation")
    if operation == "reconcile-mutation":
        started_operation = validate_started_mutation(item["started_operation"])
        started = started_operation["request"]
        if started["operation"] not in {"request", "warning", "reply", "resolve"}:
            raise OperationError("input.started_operation is not a physical GitHub mutation")
        if started["target"] != target:
            raise OperationError("input.started_operation target differs from reconciliation target")
    if operation == "reconcile-terminal":
        prior = validate_result(item["prior_failed_result"])
        if prior["operation"] != "wait" or prior["status"] != "failed" or prior["outcome"] != "request-correlation-failure":
            raise OperationError("input.prior_failed_result is not a correlation failure")
        receipt_value = item["request_receipt"]
        prior_facts = prior["facts"]
        if (
            prior_facts["request_receipt"] != receipt_value
            or prior_facts["repository"] != target["repository"]
            or prior_facts["pr_number"] != target["pr_number"]
            or prior_facts["head_sha"] != target["head_sha"]
            or prior_facts["provider"] != target["provider"]
        ):
            raise OperationError("terminal reconciliation identity differs from the failed result")
    return item


def _utc_timestamp(value: Any, name: str) -> datetime:
    if not isinstance(value, str) or not UTC_TIMESTAMP_RE.fullmatch(value):
        raise OperationError(f"{name} must be a canonical UTC timestamp")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise OperationError(f"{name} is not a valid UTC timestamp") from exc
    return parsed


def build_request(*, operation: str, controller_envelope: dict[str, Any], target: dict[str, Any], input_value: dict[str, Any]) -> dict[str, Any]:
    if operation not in OPERATIONS:
        raise OperationError("operation is unsupported")
    target = validate_target(target)
    template = controller_envelope.get("packet_template") if isinstance(controller_envelope, dict) else None
    if not isinstance(template, dict) or template.get("packet_kind") != "owned-operation":
        raise OperationError("controller envelope is not an owned operation")
    descriptor = template.get("operation")
    if descriptor != {"owner": "gitstack", "name": operation, "contract_version": "1.0.0"}:
        raise OperationError("controller operation does not match the GitStack request")
    authority = validate_authority(template.get("authority_binding"))
    projection_fingerprint = controller_envelope.get("projection_fingerprint")
    _sha(projection_fingerprint, "controller_envelope.projection_fingerprint")
    input_value = _validate_input(operation, input_value, target)
    base = {
        "schema": REQUEST_SCHEMA,
        "owner_version": __version__,
        "operation": operation,
        "operation_id": "0" * 32,
        "controller_envelope": controller_envelope,
        "controller_projection_fingerprint": projection_fingerprint,
        "authority": authority,
        "target": target,
        "input": input_value,
        "request_fingerprint": "0" * 64,
    }
    base["operation_id"] = fingerprint({k: v for k, v in base.items() if k not in {"operation_id", "request_fingerprint"}})[:32]
    base["request_fingerprint"] = fingerprint({k: v for k, v in base.items() if k != "request_fingerprint"})
    return validate_request(base)


def validate_request(value: Any) -> dict[str, Any]:
    item = _exact(value, {
        "schema", "owner_version", "operation", "operation_id", "controller_envelope", "controller_projection_fingerprint",
        "authority", "target", "input", "request_fingerprint",
    }, "request")
    if item["schema"] != REQUEST_SCHEMA or item["owner_version"] != __version__ or item["operation"] not in OPERATIONS:
        raise OperationError("request schema, version, or operation is invalid")
    if not isinstance(item["operation_id"], str) or not OPERATION_ID_RE.fullmatch(item["operation_id"]):
        raise OperationError("request.operation_id is invalid")
    authority = validate_authority(item["authority"])
    _sha(item["controller_projection_fingerprint"], "request.controller_projection_fingerprint")
    if item["controller_envelope"].get("projection_fingerprint") != item["controller_projection_fingerprint"]:
        raise OperationError("request controller projection fingerprint differs from its envelope")
    target = validate_target(item["target"])
    _validate_input(item["operation"], item["input"], target)
    expected_id = fingerprint({k: v for k, v in item.items() if k not in {"operation_id", "request_fingerprint"}})[:32]
    if item["operation_id"] != expected_id:
        raise OperationError("request.operation_id does not match its immutable content")
    if item["request_fingerprint"] != fingerprint({k: v for k, v in item.items() if k != "request_fingerprint"}):
        raise OperationError("request fingerprint is invalid")
    template = item["controller_envelope"].get("packet_template") if isinstance(item["controller_envelope"], dict) else None
    if not isinstance(template, dict) or template.get("authority_binding") != authority:
        raise OperationError("request authority differs from the controller envelope")
    return item


def validate_start_receipt(value: Any, request: dict[str, Any]) -> dict[str, Any]:
    item = _exact(value, {
        "schema", "owner", "operation", "operation_id", "request_fingerprint",
        "journal_id", "started_generation", "started_state_fingerprint", "receipt_fingerprint",
    }, "start_receipt")
    if item["schema"] != START_RECEIPT_SCHEMA or item["owner"] != "gitstack":
        raise OperationError("start receipt schema or owner is invalid")
    for name in ("operation", "operation_id", "request_fingerprint"):
        if item[name] != request[name]:
            raise OperationError(f"start receipt {name} does not match request")
    for name in ("journal_id", "started_state_fingerprint", "receipt_fingerprint"):
        _sha(item[name], f"start_receipt.{name}")
    if not isinstance(item["started_generation"], int) or item["started_generation"] < request["authority"]["expected_generation"]:
        raise OperationError("start receipt generation is invalid")
    if item["receipt_fingerprint"] != fingerprint({k: v for k, v in item.items() if k != "receipt_fingerprint"}):
        raise OperationError("start receipt fingerprint is invalid")
    return item


def validate_started_mutation(value: Any) -> dict[str, Any]:
    item = _exact(value, {"request", "start_receipt"}, "started_operation")
    request = validate_request(item["request"])
    if request["operation"] not in {"request", "warning", "reply", "resolve"}:
        raise OperationError("started operation is not a GitStack mutation")
    validate_start_receipt(item["start_receipt"], request)
    return item


def build_result(*, request: dict[str, Any], start_receipt: dict[str, Any], status: str, outcome: str, facts: dict[str, Any], evidence_ref: str) -> dict[str, Any]:
    request = validate_request(request)
    receipt_request = request
    if request["operation"] == "reconcile-mutation":
        receipt_request = validate_started_mutation(request["input"]["started_operation"])["request"]
    start_receipt = validate_start_receipt(start_receipt, receipt_request)
    value = {
        "schema": RESULT_SCHEMA, "owner_version": __version__,
        "operation": request["operation"], "operation_id": request["operation_id"],
        "request_fingerprint": request["request_fingerprint"],
        "start_receipt_fingerprint": start_receipt["receipt_fingerprint"],
        "status": status, "outcome": outcome, "facts": facts,
        "evidence_ref": evidence_ref, "result_fingerprint": "0" * 64,
    }
    value["result_fingerprint"] = fingerprint({k: v for k, v in value.items() if k != "result_fingerprint"})
    return validate_result(value)


def _positive_int(value: Any, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise OperationError(f"{name} must be a positive integer")
    return value


def _validate_mutation_artifact(value: Any, name: str) -> dict[str, Any]:
    item = _exact(value, {"status", "object_id", "object_url", "actor", "body_fingerprint"}, name)
    if item["status"] not in {"posted", "recovered", "reused"}:
        raise OperationError(f"{name}.status is invalid")
    _positive_int(item["object_id"], f"{name}.object_id")
    for field in ("object_url", "actor"):
        if not isinstance(item[field], str) or not item[field]:
            raise OperationError(f"{name}.{field} must be non-empty text")
    _sha(item["body_fingerprint"], f"{name}.body_fingerprint")
    return item


def _validate_observation_artifact(value: Any) -> dict[str, Any]:
    item = _exact(value, {"kind", "object_id", "object_url", "actor", "body_fingerprint", "outcome"}, "facts.artifact")
    if item["kind"] not in {"none", "formal-review", "provider-comment", "clean-reaction"}:
        raise OperationError("facts.artifact.kind is invalid")
    if item["outcome"] not in {None, "clean", "findings", "error"}:
        raise OperationError("facts.artifact.outcome is invalid")
    if item["kind"] == "none":
        if any(item[name] is not None for name in ("object_id", "object_url", "actor", "body_fingerprint", "outcome")):
            raise OperationError("facts.artifact none shape is invalid")
    else:
        _positive_int(item["object_id"], "facts.artifact.object_id")
        for name in ("object_url", "actor"):
            if not isinstance(item[name], str) or not item[name]:
                raise OperationError(f"facts.artifact.{name} must be non-empty text")
        _sha(item["body_fingerprint"], "facts.artifact.body_fingerprint")
    return item


def validate_facts(operation: str, outcome: str, value: Any) -> dict[str, Any]:
    if operation == "request":
        item = _exact(value, {"repository", "pr_number", "head_sha", "provider", "request_receipt", "mutation"}, "facts")
        validate_receipt(item["request_receipt"], provider=item["provider"], repository=item["repository"], pr_number=item["pr_number"], expected_head=item["head_sha"])
        mutation = _validate_mutation_artifact(item["mutation"], "facts.mutation")
        expected = "reused" if outcome == "recognized-existing" else {"posted", "recovered"}
        if (isinstance(expected, str) and mutation["status"] != expected) or (isinstance(expected, set) and mutation["status"] not in expected):
            raise OperationError("request outcome does not match mutation status")
        return item
    if operation == "wait":
        item = _exact(value, {
            "repository", "pr_number", "head_sha", "provider", "request_receipt",
            "request_binding", "provider_state", "observation_fingerprint",
            "finding_count", "finding_comment_ids", "artifact",
        }, "facts")
        validate_receipt(item["request_receipt"], provider=item["provider"], repository=item["repository"], pr_number=item["pr_number"], expected_head=item["head_sha"])
        if item["request_binding"] not in {"recognized", "absent", "invalid", "unbound", "unknown", "ambiguous"}:
            raise OperationError("facts.request_binding is invalid")
        if item["provider_state"] not in {"clean", "findings", "pending", "failed"}:
            raise OperationError("facts.provider_state is invalid")
        _sha(item["observation_fingerprint"], "facts.observation_fingerprint")
        if not isinstance(item["finding_count"], int) or isinstance(item["finding_count"], bool) or item["finding_count"] < 0:
            raise OperationError("facts.finding_count is invalid")
        ids = item["finding_comment_ids"]
        if not isinstance(ids, list) or ids != sorted(set(ids)) or any(not isinstance(v, int) or isinstance(v, bool) or v < 1 for v in ids):
            raise OperationError("facts.finding_comment_ids is invalid")
        _validate_observation_artifact(item["artifact"])
        expected = {
            "clean": ("recognized", "clean"), "findings": ("recognized", "findings"),
            "pending-at-deadline": ("recognized", "pending"),
            "request-correlation-failure": (None, "failed"), "provider-failure": ("recognized", "failed"),
        }[outcome]
        if expected[0] is not None and item["request_binding"] != expected[0]:
            raise OperationError("wait outcome does not match request binding")
        if outcome == "request-correlation-failure" and item["request_binding"] == "recognized":
            raise OperationError("correlation failure requires a proven non-recognized request")
        if item["provider_state"] != expected[1]:
            raise OperationError("wait outcome does not match provider state")
        return item
    if operation == "warning":
        item = _exact(value, {"request_receipt", "mutation"}, "facts")
        _validate_mutation_artifact(item["mutation"], "facts.mutation")
        return item
    if operation == "reply":
        item = _exact(value, {"request_receipt", "reply_receipt", "mutation"}, "facts")
        validate_reply_receipt(item["reply_receipt"])
        _validate_mutation_artifact(item["mutation"], "facts.mutation")
        return item
    if operation == "resolve":
        item = _exact(value, {"request_receipt", "resolution_receipt"}, "facts")
        validate_resolution_receipt(item["resolution_receipt"])
        return item
    if operation == "reconcile-mutation":
        item = _exact(value, {"started_operation", "marker_state", "marker_fingerprint", "provider_artifact_state", "recovered_result"}, "facts")
        if item["started_operation"] not in {"request", "warning", "reply", "resolve"}:
            raise OperationError("mutation reconciliation facts are invalid")
        if item["marker_state"] not in {"absent", "exact", "conflicting"} or item["provider_artifact_state"] not in {"missing", "unique", "conflicting", "ambiguous", "unreadable"}:
            raise OperationError("mutation reconciliation evidence states are invalid")
        _sha(item["marker_fingerprint"], "facts.marker_fingerprint", nullable=item["marker_state"] == "absent")
        if (item["marker_state"] == "absent") != (item["marker_fingerprint"] is None):
            raise OperationError("mutation reconciliation marker evidence is inconsistent")
        expected_states = {
            "completed-from-readback": {("exact", "unique")},
            "missing": {("absent", "missing"), ("exact", "missing")},
            "conflicting": {("conflicting", "missing"), ("exact", "conflicting")},
            "ambiguous": {("exact", "ambiguous"), ("exact", "unreadable")},
        }[outcome]
        if (item["marker_state"], item["provider_artifact_state"]) not in expected_states:
            raise OperationError("mutation reconciliation outcome differs from evidence states")
        if item["provider_artifact_state"] == "unique":
            recovered = validate_result(item["recovered_result"])
            if recovered["operation"] != item["started_operation"]:
                raise OperationError("recovered mutation result operation differs")
        elif item["recovered_result"] is not None:
            raise OperationError("non-verified mutation reconciliation carries a result")
        return item
    item = _exact(value, {"prior_result_fingerprint", "request_receipt", "terminal_evidence"}, "facts")
    _sha(item["prior_result_fingerprint"], "facts.prior_result_fingerprint")
    terminal = validate_terminal_evidence_receipt(item["terminal_evidence"])
    if terminal["outcome"] != ("clean" if outcome == "clean-verified" else "findings"):
        raise OperationError("terminal reconciliation outcome differs from terminal evidence")
    receipt_value = item["request_receipt"]
    if terminal["request_identity_fingerprint"] != receipt_value["identity_fingerprint"] or terminal["request_fingerprint"] != receipt_value["request_fingerprint"]:
        raise OperationError("terminal reconciliation request lineage differs")
    return item


def validate_result(value: Any) -> dict[str, Any]:
    item = _exact(value, {
        "schema", "owner_version", "operation", "operation_id", "request_fingerprint",
        "start_receipt_fingerprint", "status", "outcome", "facts", "evidence_ref", "result_fingerprint",
    }, "result")
    if item["schema"] != RESULT_SCHEMA or item["owner_version"] != __version__ or item["operation"] not in OPERATIONS:
        raise OperationError("result schema, version, or operation is invalid")
    if item["status"] not in STATUSES or item["outcome"] not in OUTCOMES[item["operation"]]:
        raise OperationError("result status or outcome is invalid")
    if LEGAL_STATUS_OUTCOME[item["operation"]][item["outcome"]] != item["status"]:
        raise OperationError("result status and outcome combination is invalid")
    if not isinstance(item["operation_id"], str) or not OPERATION_ID_RE.fullmatch(item["operation_id"]):
        raise OperationError("result operation id is invalid")
    for name in ("request_fingerprint", "start_receipt_fingerprint", "result_fingerprint"):
        _sha(item[name], f"result.{name}")
    if not isinstance(item["facts"], dict) or not isinstance(item["evidence_ref"], str) or not item["evidence_ref"]:
        raise OperationError("result facts or evidence ref is invalid")
    try:
        validate_facts(item["operation"], item["outcome"], item["facts"])
    except ValueError as exc:
        if isinstance(exc, OperationError):
            raise
        raise OperationError(str(exc)) from exc
    if item["result_fingerprint"] != fingerprint({k: v for k, v in item.items() if k != "result_fingerprint"}):
        raise OperationError("result fingerprint is invalid")
    return item


def validate_result_for_request(result_value: Any, request_value: Any) -> dict[str, Any]:
    """Validate one result and prove every owner fact belongs to its request."""

    result = validate_result(result_value)
    request = validate_request(request_value)
    for name in ("operation", "operation_id", "request_fingerprint"):
        if result[name] != request[name]:
            raise OperationError(f"result {name} does not match request")
    target, supplied, facts = request["target"], request["input"], result["facts"]
    if request["operation"] in {"request", "wait"}:
        for name in ("repository", "pr_number", "head_sha", "provider"):
            if facts[name] != target[name]:
                raise OperationError(f"result facts {name} does not match request target")
    if request["operation"] == "request":
        receipt_value = facts["request_receipt"]
        if receipt_value["request_key"] != supplied["request_key"]:
            raise OperationError("request result receipt key does not match request input")
    elif request["operation"] == "wait":
        if facts["request_receipt"] != supplied["request_receipt"]:
            raise OperationError("wait result receipt does not match request input")
    elif request["operation"] == "warning":
        if facts["request_receipt"] != supplied["request_receipt"]:
            raise OperationError("warning result receipt does not match request input")
    elif request["operation"] == "reply":
        if facts["request_receipt"] != supplied["request_receipt"]:
            raise OperationError("reply result request receipt does not match request input")
        reply = facts["reply_receipt"]
        if (
            reply["repository"] != target["repository"]
            or reply["pr_number"] != target["pr_number"]
            or reply["reply_head_sha"] != target["head_sha"]
            or reply["finding_comment_id"] != supplied["finding_comment_id"]
            or reply["thread_id"] != supplied["thread_id"]
            or reply["body_fingerprint"] != supplied["body_fingerprint"]
        ):
            raise OperationError("reply receipt identity does not match request")
    elif request["operation"] == "resolve":
        if facts["request_receipt"] != supplied["request_receipt"]:
            raise OperationError("resolution result request receipt does not match request input")
        resolution = facts["resolution_receipt"]
        reply = supplied["reply_receipt"]
        if (
            resolution["repository"] != target["repository"]
            or resolution["pr_number"] != target["pr_number"]
            or resolution["head_sha"] != target["head_sha"]
            or resolution["reply_identity_fingerprint"] != reply["identity_fingerprint"]
            or resolution["thread_id"] != reply["thread_id"]
            or resolution["finding_comment_id"] != reply["finding_comment_id"]
        ):
            raise OperationError("resolution receipt identity does not match request")
    elif request["operation"] == "reconcile-mutation":
        started_operation = validate_started_mutation(supplied["started_operation"])
        started = started_operation["request"]
        if result["start_receipt_fingerprint"] != started_operation["start_receipt"]["receipt_fingerprint"]:
            raise OperationError("mutation reconciliation result start receipt differs")
        if facts["started_operation"] != started["operation"]:
            raise OperationError("mutation reconciliation started operation does not match request")
        if facts["provider_artifact_state"] == "unique":
            recovered = validate_result_for_request(facts["recovered_result"], started)
            if recovered["start_receipt_fingerprint"] != started_operation["start_receipt"]["receipt_fingerprint"]:
                raise OperationError("recovered mutation result start receipt differs")
    else:
        prior = supplied["prior_failed_result"]
        terminal = facts["terminal_evidence"]
        receipt_value = supplied["request_receipt"]
        if facts["prior_result_fingerprint"] != prior["result_fingerprint"] or facts["request_receipt"] != receipt_value:
            raise OperationError("terminal reconciliation supersession lineage does not match request")
        if (
            terminal["repository"] != target["repository"]
            or terminal["pr_number"] != target["pr_number"]
            or terminal["head_sha"] != target["head_sha"]
            or terminal["provider"] != target["provider"]
            or terminal["request_identity_fingerprint"] != receipt_value["identity_fingerprint"]
            or terminal["request_fingerprint"] != receipt_value["request_fingerprint"]
        ):
            raise OperationError("terminal reconciliation artifact does not match request target")
    return result


def _followup_obligation(
    action: str, source_result: dict[str, Any], ordinal: int,
    artifact_identity_fingerprint: str,
) -> dict[str, Any]:
    identity = {
        "kind": "review-thread", "action": action,
        "source_result_fingerprint": source_result["result_fingerprint"],
        "ordinal": ordinal,
    }
    return {
        "kind": "review-thread", "action": action,
        "obligation_id": fingerprint(identity),
        "source_result_fingerprint": source_result["result_fingerprint"],
        "artifact_identity_fingerprint": artifact_identity_fingerprint,
        "artifact_ref": f"{source_result['evidence_ref']}#followup-{ordinal}",
    }


def _followup_effect_for_result(result: dict[str, Any]) -> dict[str, Any] | None:
    if result["operation"] == "wait" and result["outcome"] == "findings":
        return {
            "consumes_obligation_id": None,
            "creates": [
                _followup_obligation(
                    "reply", result, index,
                    fingerprint({
                        "request_identity_fingerprint": result["facts"]["request_receipt"]["identity_fingerprint"],
                        "finding_comment_id": finding_comment_id,
                    }),
                )
                for index, finding_comment_id in enumerate(result["facts"]["finding_comment_ids"], start=1)
            ],
        }
    if result["operation"] == "reply":
        return {
            "consumes_obligation_id": result.get("_request_followup_obligation_id"),
            "creates": [_followup_obligation(
                "resolve", result, 1,
                fingerprint({
                    "reply_identity_fingerprint": result["facts"]["reply_receipt"]["identity_fingerprint"],
                }),
            )],
        }
    if result["operation"] == "resolve":
        return {
            "consumes_obligation_id": result.get("_request_followup_obligation_id"),
            "creates": [],
        }
    return None


def validation_descriptor(
    request_value: Any, result_value: Any | None = None,
) -> dict[str, Any]:
    """Return the only orchestration-facing projection of owner operation identity."""

    request = validate_request(request_value)
    start_request = request
    start_receipt_fingerprint = None
    if request["operation"] == "reconcile-mutation":
        started = validate_started_mutation(request["input"]["started_operation"])
        start_request = validate_request(started["request"])
        start_receipt_fingerprint = started["start_receipt"]["receipt_fingerprint"]
    elif request["operation"] == "reconcile-terminal":
        prior = validate_result(request["input"]["prior_failed_result"])
        start_request = {
            "operation": prior["operation"],
            "operation_id": prior["operation_id"],
            "request_fingerprint": prior["request_fingerprint"],
        }
        start_receipt_fingerprint = prior["start_receipt_fingerprint"]
    result_effect = None
    if result_value is not None:
        result = validate_result_for_request(result_value, request)
        result_effect = {
            "evidence_produced": False,
            "orchestration_descriptor": None,
            "effective_result": {"operation": result["operation"], "outcome": result["outcome"]},
        }
        projected_result = dict(result)
        if request["operation"] in {"reply", "resolve"}:
            projected_result["_request_followup_obligation_id"] = request["input"]["followup_obligation"]["obligation_id"]
        if request["operation"] == "reconcile-mutation" and result["facts"]["provider_artifact_state"] == "unique":
            projected_result = dict(result["facts"]["recovered_result"])
            result_effect["effective_result"] = {
                "operation": projected_result["operation"], "outcome": projected_result["outcome"],
            }
            started_request = validate_started_mutation(request["input"]["started_operation"])["request"]
            if started_request["operation"] in {"reply", "resolve"}:
                projected_result["_request_followup_obligation_id"] = started_request["input"]["followup_obligation"]["obligation_id"]
        followup_effect = _followup_effect_for_result(projected_result)
    else:
        followup_effect = None
    prior_result_effect = None
    if request["operation"] == "warning":
        prior = validate_result(request["input"]["prior_pending_result"])
        prior_result_effect = {
            "relationship": "predecessor",
            "owner": "gitstack",
            "result_fingerprint": prior["result_fingerprint"],
            "required_disposition": "pending-warning",
        }
    elif request["operation"] == "reconcile-terminal":
        prior = validate_result(request["input"]["prior_failed_result"])
        prior_result_effect = {
            "relationship": "supersedes",
            "owner": "gitstack",
            "result_fingerprint": prior["result_fingerprint"],
            "required_disposition": "needs-owner",
        }
    return {
        "schema": VALIDATION_DESCRIPTOR_SCHEMA,
        "owner": "gitstack",
        "operation": request["operation"],
        "operation_id": request["operation_id"],
        "request_fingerprint": request["request_fingerprint"],
        "start_identity": {
            "owner": "gitstack",
            "operation": start_request["operation"],
            "operation_id": start_request["operation_id"],
            "request_fingerprint": start_request["request_fingerprint"],
            "start_receipt_fingerprint": start_receipt_fingerprint,
        },
        "prior_result_effect": prior_result_effect,
        "followup_effect": followup_effect,
        "result_effect": result_effect,
    }
