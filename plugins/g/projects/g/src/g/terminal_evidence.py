"""Typed, fingerprinted terminal-provider evidence receipts."""

from __future__ import annotations

from typing import Any

from .integrity import FULL_SHA_PATTERN, SHA256_PATTERN as FINGERPRINT_PATTERN
from .integrity import fingerprint as canonical_fingerprint
from .integrity import text_fingerprint


TERMINAL_EVIDENCE_SCHEMA = "g-terminal-provider-evidence:v1"
TERMINAL_EVIDENCE_STATUSES = {"verified"}
TERMINAL_EVIDENCE_OUTCOMES = {"clean", "findings", "error"}
TERMINAL_EVIDENCE_FIELDS = {
    "schema",
    "status",
    "provider",
    "repository",
    "pr_number",
    "head_sha",
    "request_identity_fingerprint",
    "request_fingerprint",
    "provider_request_id",
    "request_ref",
    "request_created_at",
    "artifact_id",
    "artifact_ref",
    "artifact_created_at",
    "provider_actor",
    "provider_identity_fingerprint",
    "body_fingerprint",
    "reviewed_head_token",
    "resolved_head_sha",
    "outcome",
    "artifact_fingerprint",
    "verified_at",
    "receipt_fingerprint",
}


def provider_identity_fingerprint(provider: str, actor: str) -> str:
    return canonical_fingerprint({"provider": provider, "actor": actor})


def artifact_identity(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider": value["provider"],
        "repository": value["repository"],
        "pr_number": value["pr_number"],
        "head_sha": value["head_sha"],
        "artifact_id": value["artifact_id"],
        "artifact_ref": value["artifact_ref"],
        "artifact_created_at": value["artifact_created_at"],
        "provider_actor": value["provider_actor"],
        "provider_identity_fingerprint": value["provider_identity_fingerprint"],
        "body_fingerprint": value["body_fingerprint"],
        "reviewed_head_token": value["reviewed_head_token"],
        "resolved_head_sha": value["resolved_head_sha"],
        "outcome": value["outcome"],
    }


def receipt_identity(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != "receipt_fingerprint"}


def build_terminal_evidence_receipt(
    *,
    provider: str,
    repository: str,
    pr_number: int,
    head_sha: str,
    request_receipt: dict[str, Any],
    artifact: dict[str, Any],
    verified_at: str,
) -> dict[str, Any]:
    actor = str(((artifact.get("user") or {}).get("login")) or "")
    artifact_id = int(artifact["id"])
    value: dict[str, Any] = {
        "schema": TERMINAL_EVIDENCE_SCHEMA,
        "status": "verified",
        "provider": provider,
        "repository": repository,
        "pr_number": pr_number,
        "head_sha": head_sha,
        "request_identity_fingerprint": request_receipt["identity_fingerprint"],
        "request_fingerprint": request_receipt["request_fingerprint"],
        "provider_request_id": request_receipt["provider_request_id"],
        "request_ref": request_receipt["request_ref"],
        "request_created_at": request_receipt["created_at"],
        "artifact_id": {"kind": "github-issue-comment", "value": str(artifact_id)},
        "artifact_ref": str(artifact["html_url"]),
        "artifact_created_at": str(artifact["created_at"]),
        "provider_actor": actor,
        "provider_identity_fingerprint": provider_identity_fingerprint(provider, actor),
        "body_fingerprint": text_fingerprint(str(artifact["body"])),
        "reviewed_head_token": str(artifact["reviewed_head_token"]),
        "resolved_head_sha": head_sha,
        "outcome": str(artifact["outcome"]),
        "artifact_fingerprint": "",
        "verified_at": verified_at,
        "receipt_fingerprint": "",
    }
    value["artifact_fingerprint"] = canonical_fingerprint(artifact_identity(value))
    value["receipt_fingerprint"] = canonical_fingerprint(receipt_identity(value))
    return value


def validate_terminal_evidence_receipt(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != TERMINAL_EVIDENCE_FIELDS:
        raise ValueError("The terminal-provider evidence receipt is incomplete or contains unknown fields.")
    if (
        value["schema"] != TERMINAL_EVIDENCE_SCHEMA
        or value["status"] not in TERMINAL_EVIDENCE_STATUSES
        or value["provider"] != "codex"
    ):
        raise ValueError("The terminal-provider evidence receipt schema, status, or provider is invalid.")
    if (
        not isinstance(value["repository"], str)
        or "/" not in value["repository"]
        or not isinstance(value["pr_number"], int)
        or isinstance(value["pr_number"], bool)
        or value["pr_number"] < 1
        or not isinstance(value["head_sha"], str)
        or not FULL_SHA_PATTERN.fullmatch(value["head_sha"])
        or value["resolved_head_sha"] != value["head_sha"]
    ):
        raise ValueError("The terminal-provider evidence target is invalid.")
    for field in (
        "request_identity_fingerprint",
        "request_fingerprint",
        "provider_identity_fingerprint",
        "body_fingerprint",
        "artifact_fingerprint",
        "receipt_fingerprint",
    ):
        if not isinstance(value[field], str) or not FINGERPRINT_PATTERN.fullmatch(value[field]):
            raise ValueError(f"The terminal-provider evidence {field} is invalid.")
    for field in (
        "request_ref",
        "request_created_at",
        "artifact_ref",
        "artifact_created_at",
        "provider_actor",
        "reviewed_head_token",
        "verified_at",
    ):
        if not isinstance(value[field], str) or not value[field]:
            raise ValueError(f"The terminal-provider evidence {field} is invalid.")
    for field in ("provider_request_id", "artifact_id"):
        identity = value[field]
        if (
            not isinstance(identity, dict)
            or set(identity) != {"kind", "value"}
            or identity["kind"] != "github-issue-comment"
            or not isinstance(identity["value"], str)
            or not identity["value"].isdigit()
            or int(identity["value"]) < 1
        ):
            raise ValueError(f"The terminal-provider evidence {field} is invalid.")
    request_id = int(value["provider_request_id"]["value"])
    artifact_id = int(value["artifact_id"]["value"])
    if value["request_ref"] != (
        f"https://github.com/{value['repository']}/pull/{value['pr_number']}#issuecomment-{request_id}"
    ) or value["artifact_ref"] != (
        f"https://github.com/{value['repository']}/pull/{value['pr_number']}#issuecomment-{artifact_id}"
    ):
        raise ValueError("The terminal-provider evidence references are invalid.")
    if value["outcome"] not in TERMINAL_EVIDENCE_OUTCOMES:
        raise ValueError("The terminal-provider evidence outcome is invalid.")
    if value["provider_identity_fingerprint"] != provider_identity_fingerprint(
        value["provider"], value["provider_actor"]
    ):
        raise ValueError("The terminal-provider identity fingerprint is invalid.")
    if value["artifact_fingerprint"] != canonical_fingerprint(artifact_identity(value)):
        raise ValueError("The terminal-provider artifact fingerprint is invalid.")
    if value["receipt_fingerprint"] != canonical_fingerprint(receipt_identity(value)):
        raise ValueError("The terminal-provider receipt fingerprint is invalid.")
    return value
