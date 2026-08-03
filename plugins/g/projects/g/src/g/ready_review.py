"""Typed evidence for a provider review triggered by a PR ready transition."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any


READY_TRIGGER_SCHEMA = "g-codex-ready-trigger:v1"
READY_TRIGGER_FIELDS = {
    "schema",
    "provider",
    "repository",
    "pr_number",
    "head_sha",
    "ready_event_id",
    "ready_ref",
    "ready_at",
    "pre_is_draft",
    "post_is_draft",
    "base_branch",
    "body_fingerprint",
    "trigger_fingerprint",
}

FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9](?:[A-Za-z0-9._-]{0,99})$")
UTC_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class ReadyReviewError(ValueError):
    """Strict ready-trigger evidence rejection."""


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _timestamp(value: Any, name: str) -> datetime:
    if not isinstance(value, str) or not UTC_TIMESTAMP_RE.fullmatch(value):
        raise ReadyReviewError(f"{name} must be a canonical UTC timestamp")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ReadyReviewError(f"{name} is not a valid UTC timestamp") from exc


def build_ready_trigger(
    *,
    provider: str,
    repository: str,
    pr_number: int,
    head_sha: str,
    ready_event_id: str,
    ready_ref: str,
    ready_at: str,
    base_branch: str,
    body_fingerprint: str,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema": READY_TRIGGER_SCHEMA,
        "provider": provider,
        "repository": repository,
        "pr_number": pr_number,
        "head_sha": head_sha,
        "ready_event_id": ready_event_id,
        "ready_ref": ready_ref,
        "ready_at": ready_at,
        "pre_is_draft": True,
        "post_is_draft": False,
        "base_branch": base_branch,
        "body_fingerprint": body_fingerprint,
        "trigger_fingerprint": "0" * 64,
    }
    value["trigger_fingerprint"] = _fingerprint(
        {key: item for key, item in value.items() if key != "trigger_fingerprint"}
    )
    return validate_ready_trigger(
        value,
        provider=provider,
        repository=repository,
        pr_number=pr_number,
        expected_head=head_sha,
    )


def validate_ready_trigger(
    value: Any,
    *,
    provider: str,
    repository: str,
    pr_number: int,
    expected_head: str | None = None,
) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != READY_TRIGGER_FIELDS:
        raise ReadyReviewError("The typed ready-trigger receipt is incomplete or contains unknown fields.")
    if value["schema"] != READY_TRIGGER_SCHEMA or value["provider"] != provider:
        raise ReadyReviewError("The typed ready-trigger receipt schema or provider is invalid.")
    if value["repository"] != repository or value["pr_number"] != pr_number:
        raise ReadyReviewError("The typed ready-trigger receipt target does not match the requested PR.")
    if not isinstance(repository, str) or not REPOSITORY_RE.fullmatch(repository):
        raise ReadyReviewError("The typed ready-trigger repository is invalid.")
    head = value["head_sha"]
    if not isinstance(head, str) or not FULL_SHA_RE.fullmatch(head):
        raise ReadyReviewError("The typed ready-trigger head must be a full lowercase SHA.")
    if expected_head is not None and head != expected_head:
        raise ReadyReviewError("The typed ready-trigger head does not match the requested revision.")
    if not isinstance(value["ready_event_id"], str) or not value["ready_event_id"]:
        raise ReadyReviewError("The typed ready-trigger event identity is invalid.")
    if not isinstance(value["ready_ref"], str) or not value["ready_ref"].startswith("https://"):
        raise ReadyReviewError("The typed ready-trigger provider reference is invalid.")
    _timestamp(value["ready_at"], "ready_at")
    if value["pre_is_draft"] is not True or value["post_is_draft"] is not False:
        raise ReadyReviewError("The typed ready-trigger must prove draft=true to ready=false.")
    if not isinstance(value["base_branch"], str) or not value["base_branch"]:
        raise ReadyReviewError("The typed ready-trigger base branch is invalid.")
    if not isinstance(value["body_fingerprint"], str) or not SHA256_RE.fullmatch(value["body_fingerprint"]):
        raise ReadyReviewError("The typed ready-trigger body fingerprint is invalid.")
    if not isinstance(value["trigger_fingerprint"], str) or not SHA256_RE.fullmatch(value["trigger_fingerprint"]):
        raise ReadyReviewError("The typed ready-trigger fingerprint is invalid.")
    expected = _fingerprint({key: item for key, item in value.items() if key != "trigger_fingerprint"})
    if value["trigger_fingerprint"] != expected:
        raise ReadyReviewError("The typed ready-trigger fingerprint does not match its contents.")
    return value
