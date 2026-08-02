"""Canonical immutable provider-mutation reservation protocol.

The protocol is deliberately self-contained so any controller can prepare an
exact packet while G alone owns provider transport and its durable
one-use marker.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any


RESERVATION_SCHEMA = "g-review-provider-mutation:v1"
RECOVERY_POLICY = "one-read-only-exact-artifact-or-needs-owner"
RESERVATION_FIELDS = frozenset(
    {
        "schema",
        "reservation_id",
        "operation_id",
        "task_key",
        "delivery_key",
        "mutation_kind",
        "repository",
        "pr_number",
        "head_sha",
        "request_key",
        "request_fingerprint",
        "thread_id",
        "thread_fingerprint",
        "finding_comment_id",
        "body_fingerprint",
        "reply_receipt_fingerprint",
        "expected_generation",
        "expected_state_fingerprint",
        "expected_claim_fingerprint",
        "expected_task_state",
        "recovery_policy",
        "transport",
    }
)
MUTATION_KINDS = frozenset(
    {"review-request", "review-warning", "review-reply", "review-resolution"}
)
TRANSPORTS = {
    "review-request": {"tool": "g", "domain": "reviews", "operation": "request", "method": "POST"},
    "review-warning": {"tool": "g", "domain": "reviews", "operation": "comment", "method": "POST"},
    "review-reply": {"tool": "g", "domain": "reviews", "operation": "reply", "method": "POST"},
    "review-resolution": {"tool": "g", "domain": "reviews", "operation": "resolve", "method": "GRAPHQL"},
}
OPERATION_MARKER_SCHEMA = RESERVATION_SCHEMA
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
FINGERPRINT_RE = re.compile(r"^[0-9a-f]{64}$")
OPERATION_ID_RE = re.compile(r"^[0-9a-f]{32}$")
REQUEST_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
LOWER_KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9._-]+$")
NODE_ID_RE = re.compile(r"^[A-Za-z0-9_=-]+$")
MARKER_RE = re.compile(
    rf"<!-- {re.escape(OPERATION_MARKER_SCHEMA)}\n"
    r"operation_id=(?P<operation_id>[0-9a-f]{32})\n"
    r"-->"
)


class ReservationError(ValueError):
    """Raised when a reservation packet is not canonical."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def text_fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def operation_id_for_request(
    repository: str,
    pr_number: int,
    head_sha: str,
    request_key: str,
    request_fingerprint: str,
) -> str:
    return fingerprint(
        {
            "mutation_kind": "review-request",
            "repository": repository,
            "pr_number": pr_number,
            "head_sha": head_sha,
            "request_key": request_key,
            "request_fingerprint": request_fingerprint,
        }
    )[:32]


def operation_id_for_mutation(
    mutation_kind: str,
    repository: str,
    pr_number: int,
    head_sha: str,
    *,
    request_fingerprint: str | None = None,
    thread_id: str | None = None,
    finding_comment_id: int | None = None,
    reply_receipt_fingerprint: str | None = None,
) -> str:
    """Derive the stable marker identity from the immutable action target.

    Comment content is deliberately excluded.  The packet binds its exact
    final body separately, while this identity remains computable by the
    canonical validator after the marker has been added to that body.
    """
    return fingerprint(
        {
            "mutation_kind": mutation_kind,
            "repository": repository,
            "pr_number": pr_number,
            "head_sha": head_sha,
            "request_fingerprint": request_fingerprint,
            "thread_id": thread_id,
            "finding_comment_id": finding_comment_id,
            "reply_receipt_fingerprint": reply_receipt_fingerprint,
        }
    )[:32]


def thread_identity_fingerprint(
    repository: str,
    pr_number: int,
    head_sha: str,
    thread_id: str,
    comment_identities: list[dict[str, Any]],
) -> str:
    """Fingerprint the immutable provider identity of one review thread."""

    normalized_comments = [
        {"node_id": item.get("node_id"), "comment_id": item.get("comment_id")}
        for item in comment_identities
    ]
    if any(
        not isinstance(item["node_id"], str)
        or not NODE_ID_RE.fullmatch(item["node_id"])
        or not isinstance(item["comment_id"], int)
        or isinstance(item["comment_id"], bool)
        or item["comment_id"] < 1
        for item in normalized_comments
    ):
        raise ReservationError("thread comment identity is invalid")
    normalized_comments.sort(key=lambda item: (item["node_id"], item["comment_id"]))
    if not isinstance(thread_id, str) or not NODE_ID_RE.fullmatch(thread_id):
        raise ReservationError("thread_id is invalid")
    return fingerprint(
        {
            "repository": repository,
            "pr_number": pr_number,
            "head_sha": head_sha,
            "thread_id": thread_id,
            "comments": normalized_comments,
        }
    )


def operation_marker(operation_id: str) -> str:
    if not isinstance(operation_id, str) or not OPERATION_ID_RE.fullmatch(operation_id):
        raise ReservationError("operation_id must be 32 lowercase hexadecimal characters")
    return (
        f"<!-- {OPERATION_MARKER_SCHEMA}\n"
        f"operation_id={operation_id}\n"
        "-->"
    )


def marker_operation_id(text: str) -> str | None:
    matches = list(MARKER_RE.finditer(text))
    if not matches:
        return None
    if len(matches) != 1:
        raise ReservationError("provider text contains multiple operation markers")
    return matches[0].group("operation_id")


def add_operation_marker(text: str, operation_id: str) -> str:
    marker = operation_marker(operation_id)
    existing = marker_operation_id(text)
    if existing is not None:
        if existing == operation_id and text.endswith(marker):
            return text
        raise ReservationError("provider text contains a conflicting operation marker")
    return f"{text.rstrip(chr(10))}\n\n{marker}"


def packet_fingerprint(packet: dict[str, Any]) -> str:
    validate_reservation_packet(packet)
    return fingerprint(packet)


def reservation_id_for(packet_without_id: dict[str, Any]) -> str:
    candidate = dict(packet_without_id)
    candidate.pop("reservation_id", None)
    return fingerprint(candidate)


def build_reservation(
    *,
    mutation_kind: str,
    repository: str,
    pr_number: int,
    head_sha: str,
    task_key: str,
    delivery_key: str,
    operation_id: str,
    request_key: str | None,
    request_fingerprint: str | None,
    thread_id: str | None,
    thread_fingerprint: str | None,
    finding_comment_id: int | None,
    body_fingerprint: str | None,
    reply_receipt_fingerprint: str | None,
    expected_generation: int,
    expected_state_fingerprint: str,
    expected_claim_fingerprint: str,
    expected_task_state: str,
) -> dict[str, Any]:
    packet = {
        "schema": RESERVATION_SCHEMA,
        "reservation_id": "0" * 64,
        "operation_id": operation_id,
        "task_key": task_key,
        "delivery_key": delivery_key,
        "mutation_kind": mutation_kind,
        "repository": repository,
        "pr_number": pr_number,
        "head_sha": head_sha,
        "request_key": request_key,
        "request_fingerprint": request_fingerprint,
        "thread_id": thread_id,
        "thread_fingerprint": thread_fingerprint,
        "finding_comment_id": finding_comment_id,
        "body_fingerprint": body_fingerprint,
        "reply_receipt_fingerprint": reply_receipt_fingerprint,
        "expected_generation": expected_generation,
        "expected_state_fingerprint": expected_state_fingerprint,
        "expected_claim_fingerprint": expected_claim_fingerprint,
        "expected_task_state": expected_task_state,
        "recovery_policy": RECOVERY_POLICY,
        "transport": dict(TRANSPORTS.get(mutation_kind, {})),
    }
    packet["reservation_id"] = reservation_id_for(packet)
    return validate_reservation_packet(packet)


def validate_reservation_packet(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != RESERVATION_FIELDS:
        raise ReservationError("reservation packet has unknown or missing fields")
    if value["schema"] != RESERVATION_SCHEMA:
        raise ReservationError("reservation packet schema is invalid")
    if not isinstance(value["reservation_id"], str) or not FINGERPRINT_RE.fullmatch(value["reservation_id"]):
        raise ReservationError("reservation_id is invalid")
    if not isinstance(value["operation_id"], str) or not OPERATION_ID_RE.fullmatch(value["operation_id"]):
        raise ReservationError("operation_id is invalid")
    if not isinstance(value["task_key"], str) or not LOWER_KEBAB_RE.fullmatch(value["task_key"]):
        raise ReservationError("task_key is invalid")
    if not isinstance(value["delivery_key"], str) or not LOWER_KEBAB_RE.fullmatch(value["delivery_key"]):
        raise ReservationError("delivery_key is invalid")
    kind = value["mutation_kind"]
    if kind not in MUTATION_KINDS:
        raise ReservationError("mutation_kind is invalid")
    if not isinstance(value["repository"], str) or not REPOSITORY_RE.fullmatch(value["repository"]):
        raise ReservationError("repository is invalid")
    if not isinstance(value["pr_number"], int) or isinstance(value["pr_number"], bool) or value["pr_number"] < 1:
        raise ReservationError("pr_number is invalid")
    if not isinstance(value["head_sha"], str) or not FULL_SHA_RE.fullmatch(value["head_sha"]):
        raise ReservationError("head_sha is invalid")
    if value["request_key"] is not None and (not isinstance(value["request_key"], str) or not REQUEST_KEY_RE.fullmatch(value["request_key"])):
        raise ReservationError("request_key is invalid")
    for field in ("request_fingerprint", "thread_fingerprint", "body_fingerprint", "reply_receipt_fingerprint", "expected_state_fingerprint", "expected_claim_fingerprint"):
        item = value[field]
        if item is not None and (not isinstance(item, str) or not FINGERPRINT_RE.fullmatch(item)):
            raise ReservationError(f"{field} is invalid")
    if value["expected_state_fingerprint"] is None or value["expected_claim_fingerprint"] is None:
        raise ReservationError("ledger binding fingerprints are required")
    if value["thread_id"] is not None and (not isinstance(value["thread_id"], str) or not NODE_ID_RE.fullmatch(value["thread_id"])):
        raise ReservationError("thread_id is invalid")
    if value["finding_comment_id"] is not None and (not isinstance(value["finding_comment_id"], int) or isinstance(value["finding_comment_id"], bool) or value["finding_comment_id"] < 1):
        raise ReservationError("finding_comment_id is invalid")
    if not isinstance(value["expected_generation"], int) or isinstance(value["expected_generation"], bool) or value["expected_generation"] < 1:
        raise ReservationError("expected_generation is invalid")
    if not isinstance(value["expected_task_state"], str) or not LOWER_KEBAB_RE.fullmatch(value["expected_task_state"]):
        raise ReservationError("expected_task_state is invalid")
    if value["recovery_policy"] != RECOVERY_POLICY:
        raise ReservationError("recovery_policy is invalid")
    transport = value["transport"]
    if transport != TRANSPORTS[kind]:
        raise ReservationError("transport does not match mutation_kind")
    if kind == "review-request":
        required = ("request_key", "request_fingerprint", "body_fingerprint")
        if any(value[field] is None for field in required) or any(value[field] is not None for field in ("thread_id", "thread_fingerprint", "finding_comment_id", "reply_receipt_fingerprint")):
            raise ReservationError("review-request identity is incomplete")
    elif kind == "review-warning":
        required = ("request_key", "request_fingerprint", "body_fingerprint")
        if any(value[field] is None for field in required) or any(value[field] is not None for field in ("thread_id", "thread_fingerprint", "finding_comment_id", "reply_receipt_fingerprint")):
            raise ReservationError("review-warning identity is incomplete")
    elif kind == "review-reply":
        required = ("request_key", "request_fingerprint", "thread_id", "thread_fingerprint", "finding_comment_id", "body_fingerprint")
        if any(value[field] is None for field in required) or value["reply_receipt_fingerprint"] is not None:
            raise ReservationError("review-reply identity is incomplete")
    else:
        required = ("request_key", "request_fingerprint", "thread_id", "thread_fingerprint", "finding_comment_id", "reply_receipt_fingerprint")
        if any(value[field] is None for field in required) or value["body_fingerprint"] is not None:
            raise ReservationError("review-resolution identity is incomplete")
    if kind == "review-request":
        expected_operation_id = operation_id_for_request(
            value["repository"],
            value["pr_number"],
            value["head_sha"],
            value["request_key"],
            value["request_fingerprint"],
        )
    else:
        expected_operation_id = operation_id_for_mutation(
            kind,
            value["repository"],
            value["pr_number"],
            value["head_sha"],
            request_fingerprint=value["request_fingerprint"],
            thread_id=value["thread_id"],
            finding_comment_id=value["finding_comment_id"],
            reply_receipt_fingerprint=value["reply_receipt_fingerprint"],
        )
    if value["operation_id"] != expected_operation_id:
        raise ReservationError("operation_id does not match the immutable mutation identity")
    expected_id = reservation_id_for(value)
    if value["reservation_id"] != expected_id:
        raise ReservationError("reservation_id does not match the immutable packet")
    return value
