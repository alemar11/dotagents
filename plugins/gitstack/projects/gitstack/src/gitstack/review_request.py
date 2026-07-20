"""Canonical, identity-bound automated review request protocol."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from .review_mutation import ReservationError, marker_operation_id, operation_id_for_request, operation_marker


REQUEST_SCHEMA = "gitstack-codex-review-request:v1"
RECEIPT_STATUSES = {"posted", "recovered", "reused"}
RECEIPT_FIELDS = {
    "schema",
    "provider",
    "repository",
    "pr_number",
    "head_sha",
    "request_key",
    "request_fingerprint",
    "body_fingerprint",
    "identity_fingerprint",
    "provider_request_id",
    "request_ref",
    "comment_id",
    "created_at",
    "status",
}
FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
FINGERPRINT_PATTERN = re.compile(r"^[0-9a-f]{64}$")
REQUEST_KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
TRIGGER_PATTERN = re.compile(r"(?i)@codex\s+review\b")
MARKER_PREFIX = f"<!-- {REQUEST_SCHEMA}"
TYPED_HEAD_PATTERN = re.compile(r"^@codex review (?P<head>[0-9a-f]{40})(?:\n|$)")
BASE_CANONICAL_PATTERN = re.compile(
    rf"^@codex review (?P<head>[0-9a-f]{{40}})\n\n"
    rf"<!-- {re.escape(REQUEST_SCHEMA)}\n"
    r"request_key=(?P<request_key>[a-z0-9][a-z0-9._-]{0,127})\n"
    r"request_fingerprint=(?P<request_fingerprint>[0-9a-f]{64})\n"
    r"-->$"
)


@dataclass(frozen=True)
class RequestPlan:
    schema: str
    provider: str
    repository: str
    pr_number: int
    head_sha: str
    request_key: str
    request_fingerprint: str
    body: str
    body_fingerprint: str


@dataclass(frozen=True)
class ParsedRequest:
    classification: str
    head_sha: str | None = None
    request_key: str | None = None
    request_fingerprint: str | None = None
    body_fingerprint: str | None = None
    operation_id: str | None = None


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def validate_full_head(raw: str) -> str:
    value = str(raw or "").strip()
    if not FULL_SHA_PATTERN.fullmatch(value):
        raise ValueError("The typed review request requires the full 40-character lowercase head SHA.")
    return value


def validate_request_key(raw: str) -> str:
    value = str(raw or "").strip()
    if not REQUEST_KEY_PATTERN.fullmatch(value):
        raise ValueError(
            "The typed review request requires a lowercase request key using only letters, digits, '.', '_' or '-'."
        )
    return value


def request_fingerprint(
    provider: str,
    repository: str,
    pr_number: int,
    head_sha: str,
    request_key: str,
) -> str:
    return _sha256(
        _canonical_json(
            {
                "schema": REQUEST_SCHEMA,
                "provider": provider,
                "repository": repository,
                "pr_number": pr_number,
                "head_sha": head_sha,
                "request_key": request_key,
            }
        )
    )


def build_request(
    provider: str,
    repository: str,
    pr_number: int,
    head_sha: str,
    request_key: str,
) -> RequestPlan:
    normalized_head = validate_full_head(head_sha)
    normalized_key = validate_request_key(request_key)
    fingerprint = request_fingerprint(
        provider,
        repository,
        pr_number,
        normalized_head,
        normalized_key,
    )
    base_body = (
        f"@codex review {normalized_head}\n\n"
        f"<!-- {REQUEST_SCHEMA}\n"
        f"request_key={normalized_key}\n"
        f"request_fingerprint={fingerprint}\n"
        "-->"
    )
    body = (
        f"{base_body}\n\n"
        f"{operation_marker(operation_id_for_request(repository, pr_number, normalized_head, normalized_key, fingerprint))}"
    )
    return RequestPlan(
        schema=REQUEST_SCHEMA,
        provider=provider,
        repository=repository,
        pr_number=pr_number,
        head_sha=normalized_head,
        request_key=normalized_key,
        request_fingerprint=fingerprint,
        body=body,
        body_fingerprint=_sha256(body),
    )


def parse_request(
    body: str,
    provider: str,
    repository: str,
    pr_number: int,
) -> ParsedRequest:
    """Classify a comment without treating a diagnostic match as a binding."""

    text = str(body or "")
    if provider != "codex" or not TRIGGER_PATTERN.search(text):
        return ParsedRequest("absent")
    if MARKER_PREFIX not in text:
        return ParsedRequest("unbound")
    try:
        operation_id = marker_operation_id(text)
    except ReservationError:
        return ParsedRequest(
            "invalid",
            body_fingerprint=_sha256(text),
        )
    marker = operation_marker(operation_id) if operation_id is not None else None
    base_text = text[: -len(marker)].rstrip() if marker and text.endswith(marker) else text
    match = BASE_CANONICAL_PATTERN.fullmatch(base_text)
    if not match:
        typed_head = TYPED_HEAD_PATTERN.match(text)
        return ParsedRequest(
            "invalid",
            head_sha=typed_head.group("head") if typed_head else None,
            body_fingerprint=_sha256(text),
            operation_id=operation_id,
        )
    head_sha = match.group("head")
    key = match.group("request_key")
    fingerprint = match.group("request_fingerprint")
    if fingerprint != request_fingerprint(provider, repository, pr_number, head_sha, key):
        return ParsedRequest(
            "invalid",
            head_sha=head_sha,
            request_key=key,
            request_fingerprint=fingerprint,
            body_fingerprint=_sha256(text),
            operation_id=operation_id,
        )
    expected_operation_id = operation_id_for_request(
        repository,
        pr_number,
        head_sha,
        key,
        fingerprint,
    )
    if operation_id != expected_operation_id:
        return ParsedRequest(
            "invalid",
            head_sha=head_sha,
            request_key=key,
            request_fingerprint=fingerprint,
            body_fingerprint=_sha256(text),
            operation_id=operation_id,
        )
    return ParsedRequest(
        "canonical",
        head_sha=head_sha,
        request_key=key,
        request_fingerprint=fingerprint,
        body_fingerprint=_sha256(text),
        operation_id=operation_id,
    )


def identity_fingerprint(plan: RequestPlan, comment: dict[str, Any]) -> str:
    object_id = comment.get("id")
    html_url = comment.get("html_url")
    created_at = comment.get("created_at")
    if not isinstance(object_id, int) or object_id <= 0:
        raise ValueError("The provider request comment did not include a numeric identity.")
    if not isinstance(html_url, str) or not html_url:
        raise ValueError("The provider request comment did not include a URL identity.")
    if not isinstance(created_at, str) or not created_at:
        raise ValueError("The provider request comment did not include a creation timestamp.")
    return _sha256(
        _canonical_json(
            {
                "schema": plan.schema,
                "provider": plan.provider,
                "repository": plan.repository,
                "pr_number": plan.pr_number,
                "head_sha": plan.head_sha,
                "request_key": plan.request_key,
                "request_fingerprint": plan.request_fingerprint,
                "body_fingerprint": plan.body_fingerprint,
                "provider_request_id": {
                    "kind": "github-issue-comment",
                    "value": str(object_id),
                },
                "request_ref": html_url,
                "created_at": created_at,
            }
        )
    )


def receipt(plan: RequestPlan, comment: dict[str, Any], *, status: str) -> dict[str, Any]:
    if str(comment.get("body") or "") != plan.body:
        raise ValueError("The provider request comment body does not match the canonical request.")
    identity = identity_fingerprint(plan, comment)
    return {
        "schema": plan.schema,
        "provider": plan.provider,
        "repository": plan.repository,
        "pr_number": plan.pr_number,
        "head_sha": plan.head_sha,
        "request_key": plan.request_key,
        "request_fingerprint": plan.request_fingerprint,
        "body_fingerprint": plan.body_fingerprint,
        "identity_fingerprint": identity,
        "provider_request_id": {
            "kind": "github-issue-comment",
            "value": str(comment["id"]),
        },
        "request_ref": str(comment["html_url"]),
        "comment_id": comment["id"],
        "created_at": str(comment["created_at"]),
        "status": status,
    }


def validate_receipt(
    value: object,
    *,
    provider: str,
    repository: str,
    pr_number: int,
    expected_head: str | None = None,
) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != RECEIPT_FIELDS:
        raise ValueError("The typed review request receipt is incomplete or contains unknown fields.")
    if value["schema"] != REQUEST_SCHEMA or value["provider"] != provider:
        raise ValueError("The typed review request receipt schema or provider is invalid.")
    if value["repository"] != repository or value["pr_number"] != pr_number:
        raise ValueError("The typed review request receipt target does not match the requested PR.")
    head_sha = value["head_sha"]
    if not isinstance(head_sha, str) or not FULL_SHA_PATTERN.fullmatch(head_sha):
        raise ValueError("The typed review request receipt head must be a full lowercase SHA.")
    if expected_head is not None and head_sha != expected_head:
        raise ValueError("The typed review request receipt head does not match the requested revision.")
    request_key = value["request_key"]
    if not isinstance(request_key, str) or not REQUEST_KEY_PATTERN.fullmatch(request_key):
        raise ValueError("The typed review request receipt request key is invalid.")
    if value["status"] not in RECEIPT_STATUSES:
        raise ValueError("The typed review request receipt status is invalid.")
    if not isinstance(value["comment_id"], int) or isinstance(value["comment_id"], bool) or value["comment_id"] < 1:
        raise ValueError("The typed review request receipt comment identity is invalid.")
    provider_request_id = value["provider_request_id"]
    if (
        not isinstance(provider_request_id, dict)
        or set(provider_request_id) != {"kind", "value"}
        or provider_request_id["kind"] != "github-issue-comment"
        or provider_request_id["value"] != str(value["comment_id"])
    ):
        raise ValueError("The typed review request receipt provider identity is invalid.")
    created_at = value["created_at"]
    request_ref = value["request_ref"]
    expected_ref = f"https://github.com/{repository}/pull/{pr_number}#issuecomment-{value['comment_id']}"
    if not isinstance(created_at, str) or not created_at or request_ref != expected_ref:
        raise ValueError("The typed review request receipt provider reference is invalid.")
    for field in ("request_fingerprint", "body_fingerprint", "identity_fingerprint"):
        if not isinstance(value[field], str) or not FINGERPRINT_PATTERN.fullmatch(value[field]):
            raise ValueError(f"The typed review request receipt {field} is invalid.")
    plan = build_request(provider, repository, pr_number, head_sha, request_key)
    expected_comment = {
        "id": value["comment_id"],
        "html_url": request_ref,
        "body": plan.body,
        "created_at": created_at,
    }
    expected = receipt(plan, expected_comment, status=value["status"])
    if value != expected:
        raise ValueError("The typed review request receipt fingerprints do not match its exact identity and body.")
    return value


def receipt_matches(plan: RequestPlan, comment: dict[str, Any], saved: dict[str, Any]) -> bool:
    try:
        expected = receipt(plan, comment, status=str(saved.get("status") or "reused"))
    except (KeyError, TypeError, ValueError):
        return False
    for field in (
        "schema",
        "provider",
        "repository",
        "pr_number",
        "head_sha",
        "request_key",
        "request_fingerprint",
        "body_fingerprint",
        "identity_fingerprint",
        "request_ref",
        "comment_id",
        "created_at",
    ):
        if saved.get(field) != expected.get(field):
            return False
    return saved.get("provider_request_id") == expected.get("provider_request_id")
