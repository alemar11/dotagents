"""Typed, exact-target review-thread reply and resolution receipts."""

from __future__ import annotations

import re
from typing import Any

from .integrity import FULL_SHA_PATTERN, SHA256_PATTERN as FINGERPRINT_PATTERN
from .integrity import fingerprint as _fingerprint


REPLY_SCHEMA = "g-review-thread-reply:v1"
RESOLUTION_SCHEMA = "g-review-thread-resolution:v1"
REPLY_STATUSES = {"replied", "recovered"}
RESOLUTION_STATUSES = {"resolved", "recovered", "already-resolved"}
NODE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_=-]+$")

REPLY_FIELDS = {
    "schema",
    "repository",
    "pr_number",
    "finding_head_sha",
    "reply_head_sha",
    "thread_id",
    "finding_comment_id",
    "finding_node_id",
    "finding_ref",
    "finding_created_at",
    "reply_comment_id",
    "reply_node_id",
    "reply_author",
    "reply_ref",
    "reply_created_at",
    "body_fingerprint",
    "identity_fingerprint",
    "status",
}
RESOLUTION_FIELDS = {
    "schema",
    "repository",
    "pr_number",
    "head_sha",
    "thread_id",
    "finding_comment_id",
    "finding_node_id",
    "reply_comment_id",
    "reply_node_id",
    "reply_identity_fingerprint",
    "resolution_fingerprint",
    "is_resolved",
    "observed_at",
    "status",
}


def _positive_int(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{field} must be a positive integer.")
    return value


def _nonempty(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string.")
    return value


def _node_id(value: object, field: str) -> str:
    item = _nonempty(value, field)
    if not NODE_ID_PATTERN.fullmatch(item):
        raise ValueError(f"{field} must be an opaque GitHub node id.")
    return item


def _full_sha(value: object, field: str) -> str:
    item = _nonempty(value, field)
    if not FULL_SHA_PATTERN.fullmatch(item):
        raise ValueError(f"{field} must be a full lowercase commit SHA.")
    return item


def _sha256(value: object, field: str) -> str:
    item = _nonempty(value, field)
    if not FINGERPRINT_PATTERN.fullmatch(item):
        raise ValueError(f"{field} must be a SHA-256 fingerprint.")
    return item


def _reply_identity(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": REPLY_SCHEMA,
        "repository": value["repository"],
        "pr_number": value["pr_number"],
        "finding_head_sha": value["finding_head_sha"],
        "reply_head_sha": value["reply_head_sha"],
        "thread_id": value["thread_id"],
        "finding_comment_id": value["finding_comment_id"],
        "finding_node_id": value["finding_node_id"],
        "finding_ref": value["finding_ref"],
        "finding_created_at": value["finding_created_at"],
        "reply_comment_id": value["reply_comment_id"],
        "reply_node_id": value["reply_node_id"],
        "reply_author": value["reply_author"],
        "reply_ref": value["reply_ref"],
        "reply_created_at": value["reply_created_at"],
        "body_fingerprint": value["body_fingerprint"],
    }


def build_reply_receipt(
    *,
    repository: str,
    pr_number: int,
    finding_head_sha: str,
    reply_head_sha: str,
    thread_id: str,
    finding: dict[str, Any],
    reply: dict[str, Any],
    body_fingerprint: str,
    status: str,
) -> dict[str, Any]:
    value = {
        "schema": REPLY_SCHEMA,
        "repository": repository,
        "pr_number": pr_number,
        "finding_head_sha": finding_head_sha,
        "reply_head_sha": reply_head_sha,
        "thread_id": thread_id,
        "finding_comment_id": finding.get("id"),
        "finding_node_id": finding.get("node_id"),
        "finding_ref": finding.get("html_url"),
        "finding_created_at": finding.get("created_at"),
        "reply_comment_id": reply.get("id"),
        "reply_node_id": reply.get("node_id"),
        "reply_author": ((reply.get("user") or {}).get("login") if isinstance(reply.get("user"), dict) else None),
        "reply_ref": reply.get("html_url"),
        "reply_created_at": reply.get("created_at"),
        "body_fingerprint": body_fingerprint,
        "identity_fingerprint": "",
        "status": status,
    }
    value["identity_fingerprint"] = _fingerprint(_reply_identity(value))
    return validate_reply_receipt(value)


def validate_reply_receipt(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != REPLY_FIELDS:
        raise ValueError("The typed review-thread reply receipt is incomplete or contains unknown fields.")
    if value["schema"] != REPLY_SCHEMA or value["status"] not in REPLY_STATUSES:
        raise ValueError("The typed review-thread reply receipt schema or status is invalid.")
    _nonempty(value["repository"], "repository")
    _positive_int(value["pr_number"], "pr_number")
    _full_sha(value["finding_head_sha"], "finding_head_sha")
    _full_sha(value["reply_head_sha"], "reply_head_sha")
    _node_id(value["thread_id"], "thread_id")
    _positive_int(value["finding_comment_id"], "finding_comment_id")
    _node_id(value["finding_node_id"], "finding_node_id")
    _nonempty(value["finding_ref"], "finding_ref")
    _nonempty(value["finding_created_at"], "finding_created_at")
    _positive_int(value["reply_comment_id"], "reply_comment_id")
    _node_id(value["reply_node_id"], "reply_node_id")
    _nonempty(value["reply_author"], "reply_author")
    _nonempty(value["reply_ref"], "reply_ref")
    _nonempty(value["reply_created_at"], "reply_created_at")
    _sha256(value["body_fingerprint"], "body_fingerprint")
    _sha256(value["identity_fingerprint"], "identity_fingerprint")
    if value["finding_ref"] != (
        f"https://github.com/{value['repository']}/pull/{value['pr_number']}"
        f"#discussion_r{value['finding_comment_id']}"
    ):
        raise ValueError("The finding reference does not match the exact review comment.")
    if value["reply_ref"] != (
        f"https://github.com/{value['repository']}/pull/{value['pr_number']}"
        f"#discussion_r{value['reply_comment_id']}"
    ):
        raise ValueError("The reply reference does not match the exact review comment.")
    if value["identity_fingerprint"] != _fingerprint(_reply_identity(value)):
        raise ValueError("The review-thread reply identity fingerprint is invalid.")
    return value


def _resolution_identity(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": RESOLUTION_SCHEMA,
        "repository": value["repository"],
        "pr_number": value["pr_number"],
        "head_sha": value["head_sha"],
        "thread_id": value["thread_id"],
        "finding_comment_id": value["finding_comment_id"],
        "finding_node_id": value["finding_node_id"],
        "reply_comment_id": value["reply_comment_id"],
        "reply_node_id": value["reply_node_id"],
        "reply_identity_fingerprint": value["reply_identity_fingerprint"],
    }


def build_resolution_receipt(
    reply_receipt: dict[str, Any],
    *,
    status: str,
    observed_at: str,
) -> dict[str, Any]:
    reply = validate_reply_receipt(reply_receipt)
    value = {
        "schema": RESOLUTION_SCHEMA,
        "repository": reply["repository"],
        "pr_number": reply["pr_number"],
        "head_sha": reply["reply_head_sha"],
        "thread_id": reply["thread_id"],
        "finding_comment_id": reply["finding_comment_id"],
        "finding_node_id": reply["finding_node_id"],
        "reply_comment_id": reply["reply_comment_id"],
        "reply_node_id": reply["reply_node_id"],
        "reply_identity_fingerprint": reply["identity_fingerprint"],
        "resolution_fingerprint": "",
        "is_resolved": True,
        "observed_at": observed_at,
        "status": status,
    }
    value["resolution_fingerprint"] = _fingerprint(_resolution_identity(value))
    return validate_resolution_receipt(value)


def validate_resolution_receipt(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != RESOLUTION_FIELDS:
        raise ValueError("The typed review-thread resolution receipt is incomplete or contains unknown fields.")
    if value["schema"] != RESOLUTION_SCHEMA or value["status"] not in RESOLUTION_STATUSES:
        raise ValueError("The typed review-thread resolution receipt schema or status is invalid.")
    _nonempty(value["repository"], "repository")
    _positive_int(value["pr_number"], "pr_number")
    _full_sha(value["head_sha"], "head_sha")
    _node_id(value["thread_id"], "thread_id")
    _positive_int(value["finding_comment_id"], "finding_comment_id")
    _node_id(value["finding_node_id"], "finding_node_id")
    _positive_int(value["reply_comment_id"], "reply_comment_id")
    _node_id(value["reply_node_id"], "reply_node_id")
    _sha256(value["reply_identity_fingerprint"], "reply_identity_fingerprint")
    _sha256(value["resolution_fingerprint"], "resolution_fingerprint")
    _nonempty(value["observed_at"], "observed_at")
    if value["is_resolved"] is not True:
        raise ValueError("A resolution receipt must prove is_resolved=true.")
    if value["resolution_fingerprint"] != _fingerprint(_resolution_identity(value)):
        raise ValueError("The review-thread resolution fingerprint is invalid.")
    return value
