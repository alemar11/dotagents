from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from typing import Any

from .common import GError
from .provider_text import API_VERSION
from .ready_review import ReadyReviewError, validate_ready_trigger
from .review_mutation import text_fingerprint
from .review_request import (
    FULL_SHA_PATTERN,
    RequestPlan,
    build_request,
    parse_request,
    receipt,
    receipt_matches,
    validate_full_head,
    validate_receipt,
)
from .review_types import ReviewError
from .terminal_evidence import validate_terminal_evidence_receipt

CODEX_LOGINS = {"chatgpt-codex-connector[bot]", "chatgpt-codex-connector"}

CODEX_TERMINAL_PREFIX = re.compile("(?im)^\\s*Codex Review\\s*:")

CODEX_CLEAN_RESULT = re.compile(
    "(?i)(?:did(?:n['’]t| not) find any major issues|no major issues|no issues found|no findings|looks good)"
)

CODEX_ERROR_RESULT = re.compile(
    "(?i)(?:unable to (?:complete|perform|review)|could(?:n['’]t| not) (?:complete|perform|review)|review (?:failed|errored)|encountered an error)"
)

CODEX_FINDINGS_RESULT = re.compile(
    "(?im)(?:found\\s+(?:\\d+\\s+|some\\s+|the following\\s+)?(?:issues?|findings?)|(?:issues?|findings?)\\s+to\\s+address|actionable\\s+(?:issue|finding)|^\\s*(?:[-*]\\s*|#{1,6}\\s*)?\\[P[0-3]\\])"
)

REVIEWED_COMMIT = re.compile(
    "(?im)^\\s*\\*{0,2}Reviewed commit\\s*:\\s*\\*{0,2}\\s*`?([0-9a-f]{7,40})`?"
)

REVIEW_EXIT_CODES = {
    "clean": 0,
    "findings": 1,
    "not-requested": 2,
    "acknowledged": 2,
    "pending": 2,
    "stale": 3,
    "error": 4,
}

REQUEST_BINDING_EXIT_CODES = {
    "absent": 2,
    "recognized": 0,
    "unbound": 4,
    "invalid": 4,
    "unknown": 4,
    "ambiguous": 4,
}


def positive_int(raw: str | None, name: str, *, backend: Any) -> int:
    if not raw or not re.fullmatch("[1-9][0-9]*", raw):
        raise ReviewError(
            f"Invalid --{name} value '{raw or ''}'. Use a positive integer.",
            code="invalid_arguments",
            exit_code=64,
        )
    return int(raw)


def duration_seconds(raw: str, name: str, *, backend: Any) -> float:
    match = re.fullmatch("([1-9][0-9]*)([smh]?)", raw.strip().lower())
    if not match:
        raise ReviewError(
            f"Invalid --{name} value '{raw}'. Use a positive duration such as 30s, 15m, or 1h.",
            code="invalid_arguments",
            exit_code=64,
        )
    multipliers = {"": 1, "s": 1, "m": 60, "h": 3600}
    return int(match.group(1)) * multipliers[match.group(2)]


def is_provider_author(provider: str, login: str, *, backend: Any) -> bool:
    if provider != "codex":
        raise ReviewError(
            f"Unsupported review provider '{provider}'. Supported providers: codex.",
            code="unsupported_provider",
            exit_code=64,
        )
    return login.lower() in CODEX_LOGINS


def authored_by(item: dict[str, Any], provider: str, *, backend: Any) -> bool:
    return is_provider_author(
        provider, str((item.get("user") or {}).get("login") or ""), backend=backend
    )


def sha_matches(actual: object, expected: str, *, backend: Any) -> bool:
    value = str(actual or "").lower()
    target = expected.lower()
    return bool(
        value and target and (value.startswith(target) or target.startswith(value))
    )


def validate_head(raw: str, *, backend: Any) -> str:
    value = raw.strip().lower()
    if not re.fullmatch("[0-9a-f]{7,40}", value):
        raise ReviewError(
            f"Invalid --head value '{raw}'. Use a hexadecimal commit SHA or unambiguous 7-40 character prefix.",
            code="invalid_arguments",
            exit_code=64,
        )
    return value


def provider_terminal_comment_any(
    comment: dict[str, Any], provider: str, *, backend: Any
) -> dict[str, Any] | None:
    if not authored_by(comment, provider, backend=backend):
        return None
    body = str(comment.get("body") or "")
    if provider != "codex" or not CODEX_TERMINAL_PREFIX.search(body):
        return None
    created_at = str(comment.get("created_at") or "")
    if not created_at:
        return None
    match = REVIEWED_COMMIT.search(body)
    reviewed_head = match.group(1).lower() if match else ""
    if not reviewed_head:
        return None
    if CODEX_ERROR_RESULT.search(body):
        outcome = "error"
    elif CODEX_FINDINGS_RESULT.search(body):
        outcome = "findings"
    elif CODEX_CLEAN_RESULT.search(body):
        outcome = "clean"
    else:
        return None
    return {
        "comment_id": comment.get("id"),
        "html_url": comment.get("html_url"),
        "body": body,
        "user": comment.get("user"),
        "created_at": created_at,
        "reviewed_head": reviewed_head,
        "outcome": outcome,
    }


def review_failure_classification(
    *,
    binding: str,
    status: str | None,
    head_is_current: bool,
    request_error_code: str | None,
    backend: Any,
) -> tuple[str | None, str | None]:
    """Return the stable machine failure mapping consumed by typed ledgers."""
    if not head_is_current or status == "stale":
        return ("head-drift", "head_drift")
    if status == "error":
        return ("provider-terminal-error", "provider_terminal_error")
    if binding == "ambiguous":
        return ("ambiguous-provider-evidence", "ambiguous_review_evidence")
    if binding == "invalid":
        if request_error_code == "request_correlation_failure":
            return ("request-correlation-failure", request_error_code)
        return (
            "provider-config-failure",
            request_error_code or "request_receipt_invalid",
        )
    if binding == "unknown":
        if request_error_code == "request_correlation_failure":
            return ("request-correlation-failure", request_error_code)
        return ("provider-api-failure", request_error_code or "provider_api_failure")
    if binding == "unbound":
        return ("request-correlation-failure", "request_unbound")
    return (None, None)


def stable_observation_fingerprint(payload: dict[str, Any], *, backend: Any) -> str:
    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def provider_reactions(
    repo: str, comment_id: int, provider: str, *, backend: Any
) -> set[str]:
    reactions = backend.gh_api_paginated_list(
        f"repos/{repo}/issues/comments/{comment_id}/reactions"
    )
    return {
        str(reaction.get("content") or "")
        for reaction in reactions
        if authored_by(reaction, provider, backend=backend)
    }


def _receipt_is_complete(value: object, *, backend: Any) -> bool:
    if not isinstance(value, dict):
        return False
    try:
        validate_receipt(
            value,
            provider="codex",
            repository=str(value.get("repository") or ""),
            pr_number=int(value.get("pr_number")),
            expected_head=str(value.get("head_sha") or ""),
        )
    except (TypeError, ValueError):
        return False
    return True


def _request_plan_from_receipt(
    value: object, provider: str, repository: str, pr_number: int, *, backend: Any
) -> RequestPlan | None:
    if not _receipt_is_complete(value, backend=backend):
        return None
    assert isinstance(value, dict)
    if (
        value.get("provider") != provider
        or value.get("repository") != repository
        or value.get("pr_number") != pr_number
    ):
        return None
    try:
        validate_receipt(
            value, provider=provider, repository=repository, pr_number=pr_number
        )
        plan = build_request(
            provider,
            repository,
            pr_number,
            str(value["head_sha"]),
            str(value["request_key"]),
        )
    except ValueError:
        return None
    if (
        value.get("request_fingerprint") != plan.request_fingerprint
        or value.get("body_fingerprint") != plan.body_fingerprint
    ):
        return None
    return plan


def _comment_for_plan(
    comment: dict[str, Any], plan: RequestPlan, *, backend: Any
) -> bool:
    parsed = parse_request(
        comment.get("body") or "", plan.provider, plan.repository, plan.pr_number
    )
    return (
        parsed.classification == "canonical"
        and parsed.head_sha == plan.head_sha
        and (parsed.request_key == plan.request_key)
        and (parsed.request_fingerprint == plan.request_fingerprint)
        and (parsed.body_fingerprint == plan.body_fingerprint)
        and (str(comment.get("body") or "") == plan.body)
    )


def _request_conflicts(
    conversation: list[dict[str, Any]], plan: RequestPlan, *, backend: Any
) -> tuple[str | None, list[dict[str, Any]]]:
    exact: list[dict[str, Any]] = []
    for item in conversation:
        parsed = parse_request(
            item.get("body") or "", plan.provider, plan.repository, plan.pr_number
        )
        if parsed.classification == "canonical" and parsed.head_sha == plan.head_sha:
            if _comment_for_plan(item, plan, backend=backend):
                exact.append(item)
            else:
                return ("invalid", exact)
        elif parsed.classification == "invalid" and parsed.head_sha == plan.head_sha:
            return ("invalid", exact)
    if len(exact) > 1:
        return ("ambiguous", exact)
    return (None, exact)


def _reconcile_consumed_request(
    repo: str, pr: int, plan: RequestPlan, packet: dict[str, Any], *, backend: Any
) -> dict[str, Any]:
    """Recover one already-consumed request from an exact provider artifact."""
    try:
        actor = backend._viewer_login()
        conversation = backend._read_back_list(f"repos/{repo}/issues/{pr}/comments")
    except (ReviewError, GError) as exc:
        raise backend._recovery_required(
            "The consumed review request could not be read back exactly; owner recovery is required.",
            code="request_unknown",
            details={
                "read_back_code": getattr(exc, "code", "provider_read_back_failed")
            },
        ) from exc
    matches = [
        item
        for item in conversation
        if backend._item_login(item) == actor
        and backend._request_target_comment(item, repo, pr)
        and _comment_for_plan(item, plan, backend=backend)
        and backend._marker_matches(str(item.get("body") or ""), packet["operation_id"])
    ]
    if len(matches) != 1:
        raise backend._recovery_required(
            "The consumed review request did not map to one unique provider artifact; owner recovery is required.",
            code="request_unknown",
            details={"matches": len(matches)},
        )
    try:
        saved_receipt = receipt(plan, matches[0], status="recovered")
    except (KeyError, TypeError, ValueError) as exc:
        raise backend._recovery_required(
            "The recovered review request omitted complete provider identity; owner recovery is required.",
            code="request_unknown",
        ) from exc
    return {
        "status": "recovered",
        "request": saved_receipt,
        "target": {"repo": repo, "pr": pr, "kind": "codex-review-request"},
        "text": {
            "field": "body",
            "encoding": "utf-8",
            "bytes": len(plan.body.encode("utf-8")),
            "sha256": plan.body_fingerprint,
        },
        "transport": {
            "method": "POST",
            "endpoint": f"repos/{repo}/issues/{pr}/comments",
            "api_version": API_VERSION,
            "posted": False,
            "recovered": True,
        },
    }


def _observed_request_metadata(
    plan: RequestPlan, comment: dict[str, Any], *, backend: Any
) -> dict[str, Any]:
    """Return diagnostic metadata that cannot be mistaken for a receipt."""
    return {
        "kind": "observed-request",
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
            "value": str(comment.get("id") or ""),
        },
        "request_ref": str(comment.get("html_url") or ""),
        "comment_id": comment.get("id"),
        "created_at": str(comment.get("created_at") or ""),
    }


def check_automated_review(
    repo: str,
    pr: int,
    provider: str,
    expected_head: str | None,
    request_identity: dict[str, Any] | None = None,
    *,
    backend: Any,
) -> dict[str, Any]:
    is_provider_author(provider, "", backend=backend)
    pull = backend.gh_json(
        ["api", f"repos/{repo}/pulls/{pr}", "-H", "Accept: application/vnd.github+json"]
    )
    if not isinstance(pull, dict):
        raise ReviewError(
            "Unexpected pull request response shape.", code="api_error", exit_code=4
        )
    current_head = str((pull.get("head") or {}).get("sha") or "")
    if not current_head:
        raise ReviewError(
            "Pull request response did not include a head SHA.",
            code="api_error",
            exit_code=4,
        )
    current_head = validate_head(current_head, backend=backend)
    requested_head = (
        validate_head(expected_head, backend=backend) if expected_head else current_head
    )
    head = (
        current_head
        if sha_matches(current_head, requested_head, backend=backend)
        else requested_head
    )
    head_is_current = sha_matches(current_head, head, backend=backend)
    reviews = backend.gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/reviews")
    inline_comments = backend.gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/comments")
    conversation = backend.gh_api_paginated_list(f"repos/{repo}/issues/{pr}/comments")
    provider_reviews = [
        item for item in reviews if authored_by(item, provider, backend=backend)
    ]
    head_reviews = [
        item
        for item in provider_reviews
        if sha_matches(item.get("commit_id"), head, backend=backend)
    ]
    head_findings = [
        item
        for item in inline_comments
        if authored_by(item, provider, backend=backend)
        and sha_matches(item.get("commit_id"), head, backend=backend)
    ]
    saved_plan = (
        _request_plan_from_receipt(
            request_identity, provider, repo, pr, backend=backend
        )
        if request_identity
        else None
    )
    binding = "absent"
    selected_request: dict[str, Any] | None = None
    selected_receipt: dict[str, Any] | None = None
    selected_plan: RequestPlan | None = saved_plan
    request_error: str | None = None
    request_error_code: str | None = None
    if request_identity is not None and saved_plan is None:
        binding = "invalid"
        request_error_code = "request_receipt_invalid"
    elif saved_plan is not None:
        binding = "unknown"
        try:
            comment_id = int(request_identity["comment_id"])
            selected_request = backend._api_object(
                f"repos/{repo}/issues/comments/{comment_id}"
            )
            if not _comment_for_plan(
                selected_request, saved_plan, backend=backend
            ) or not receipt_matches(saved_plan, selected_request, request_identity):
                binding = "invalid"
                request_error = "The persisted request receipt does not match the exact provider comment."
                request_error_code = "request_correlation_failure"
            else:
                binding = "recognized"
                selected_receipt = request_identity
        except (ReviewError, KeyError, TypeError, ValueError) as exc:
            request_error = str(exc)
            request_error_code = (
                exc.code
                if isinstance(exc, ReviewError)
                else "provider_response_invalid"
            )
    else:
        candidate_plan: RequestPlan | None = None
        for item in conversation:
            parsed = parse_request(item.get("body") or "", provider, repo, pr)
            if (
                parsed.classification == "canonical"
                and parsed.head_sha
                and sha_matches(parsed.head_sha, head, backend=backend)
            ):
                if candidate_plan is None:
                    try:
                        candidate_plan = build_request(
                            provider, repo, pr, parsed.head_sha, str(parsed.request_key)
                        )
                        selected_request = item
                    except (TypeError, ValueError):
                        binding = "invalid"
                        break
                else:
                    binding = "ambiguous"
                    request_error_code = "ambiguous_review_evidence"
                    break
        if (
            binding == "absent"
            and candidate_plan is not None
            and (selected_request is not None)
        ):
            binding = "recognized"
            selected_plan = candidate_plan
        if binding == "absent":
            conflict, _ = (
                _request_conflicts(
                    conversation,
                    build_request(
                        provider,
                        repo,
                        pr,
                        current_head if head_is_current else head,
                        "diagnostic",
                    ),
                    backend=backend,
                )
                if head_is_current
                else (None, [])
            )
            if conflict:
                binding = conflict
                request_error_code = (
                    "ambiguous_review_evidence"
                    if conflict == "ambiguous"
                    else "request_correlation_failure"
                )
            elif any(
                (
                    parse_request(
                        item.get("body") or "", provider, repo, pr
                    ).classification
                    == "unbound"
                    for item in conversation
                )
            ):
                binding = "unbound"
                request_error_code = "request_unbound"
    plan = selected_plan
    if plan is not None and selected_request is not None:
        conflict, exact = _request_conflicts(conversation, plan, backend=backend)
        if conflict == "ambiguous" or len(exact) > 1:
            binding = "ambiguous"
            request_error_code = "ambiguous_review_evidence"
        elif conflict == "invalid":
            binding = conflict
            request_error_code = "request_correlation_failure"
    request_created_at = (
        str(selected_receipt.get("created_at") or "")
        if selected_receipt
        else str(selected_request.get("created_at") or "")
        if selected_request
        else ""
    )
    reactions: set[str] = set()
    if binding == "recognized" and selected_request and selected_request.get("id"):
        try:
            reactions = provider_reactions(
                repo, int(selected_request["id"]), provider, backend=backend
            )
        except ReviewError as exc:
            binding = "unknown"
            request_error = str(exc)
            request_error_code = exc.code or "provider_api_failure"
    current_request_reviews = (
        [
            item
            for item in head_reviews
            if request_created_at
            and str(item.get("submitted_at") or "") > request_created_at
        ]
        if binding == "recognized"
        else []
    )
    current_request_findings = (
        [
            item
            for item in head_findings
            if request_created_at
            and str(item.get("created_at") or "") > request_created_at
            and (item.get("in_reply_to_id") is None)
        ]
        if binding == "recognized"
        else []
    )
    latest_formal_review = max(
        current_request_reviews,
        key=lambda item: str(item.get("submitted_at") or ""),
        default=None,
    )
    all_terminal_comments = [
        result
        for item in conversation
        if (result := provider_terminal_comment_any(item, provider, backend=backend))
        is not None
    ]
    terminal_comments = [
        result
        for result in all_terminal_comments
        if binding == "recognized"
        and request_created_at
        and (str(result.get("created_at") or "") > request_created_at)
        and sha_matches(result.get("reviewed_head"), head, backend=backend)
    ]
    mismatched_terminal_comments = [
        result
        for result in all_terminal_comments
        if binding == "recognized"
        and request_created_at
        and (str(result.get("created_at") or "") > request_created_at)
        and (not sha_matches(result.get("reviewed_head"), head, backend=backend))
    ]
    latest_terminal_comment = max(
        terminal_comments,
        key=lambda item: str(item.get("created_at") or ""),
        default=None,
    )
    if (
        latest_terminal_comment
        and selected_request
        and (
            len(
                [
                    item
                    for item in conversation
                    if _comment_for_plan(item, plan, backend=backend)
                ]
            )
            > 1
        )
    ):
        raise ReviewError(
            "A terminal Codex result cannot be correlated across duplicate exact requests.",
            code="ambiguous_review_evidence",
            exit_code=4,
        )
    formal_outcome = (
        "findings"
        if current_request_findings
        else "clean"
        if current_request_reviews
        else None
    )
    terminal_outcomes = {
        outcome
        for outcome in (
            formal_outcome,
            *(str(result.get("outcome") or "") for result in terminal_comments),
            "clean" if "+1" in reactions else None,
        )
        if outcome
    }
    if binding == "recognized" and head_is_current and (len(terminal_outcomes) > 1):
        raise ReviewError(
            "Conflicting terminal Codex review evidence exists for the current PR head.",
            code="ambiguous_review_evidence",
            exit_code=4,
        )
    evidence: dict[str, Any] = {
        "kind": "none",
        "object_id": None,
        "object_url": None,
        "actor": None,
        "body_fingerprint": None,
        "created_at": None,
        "outcome": None,
        "head": head,
    }
    if not head_is_current:
        status = "stale"
    elif binding != "recognized":
        status = None
        if binding == "absent" and head_is_current:
            status = "not-requested"
    elif mismatched_terminal_comments:
        status = "stale"
        mismatched = mismatched_terminal_comments[-1]
        evidence = {
            "kind": "mismatched-provider-comment",
            "object_id": mismatched.get("comment_id"),
            "object_url": mismatched.get("html_url"),
            "actor": backend._item_login(mismatched),
            "body_fingerprint": text_fingerprint(str(mismatched.get("body") or "")),
            "created_at": mismatched.get("created_at"),
            "outcome": mismatched.get("outcome"),
            "head": mismatched.get("reviewed_head"),
        }
    elif latest_terminal_comment:
        status = str(latest_terminal_comment["outcome"])
        evidence = {
            "kind": "provider-comment",
            "object_id": latest_terminal_comment.get("comment_id"),
            "object_url": latest_terminal_comment.get("html_url"),
            "actor": backend._item_login(latest_terminal_comment),
            "body_fingerprint": text_fingerprint(
                str(latest_terminal_comment.get("body") or "")
            ),
            "created_at": latest_terminal_comment.get("created_at"),
            "outcome": status,
            "head": latest_terminal_comment.get("reviewed_head"),
        }
    elif latest_formal_review:
        status = str(formal_outcome)
        evidence = {
            "kind": "formal-review",
            "object_id": latest_formal_review.get("id"),
            "object_url": latest_formal_review.get("html_url"),
            "actor": backend._item_login(latest_formal_review),
            "body_fingerprint": text_fingerprint(
                str(latest_formal_review.get("body") or "")
            ),
            "created_at": latest_formal_review.get("submitted_at"),
            "outcome": status,
            "head": latest_formal_review.get("commit_id"),
        }
    elif "+1" in reactions:
        status = "clean"
        evidence = {
            "kind": "clean-reaction",
            "object_id": selected_request.get("id") if selected_request else None,
            "object_url": selected_request.get("html_url")
            if selected_request
            else None,
            "actor": backend._item_login(selected_request or {}),
            "body_fingerprint": text_fingerprint(
                str((selected_request or {}).get("body") or "")
            ),
            "created_at": selected_request.get("created_at")
            if selected_request
            else None,
            "outcome": status,
            "head": head,
        }
    else:
        status = "acknowledged" if "eyes" in reactions else "pending"
    if selected_receipt is not None:
        request_payload: dict[str, Any] = dict(selected_receipt)
    elif plan is not None and selected_request is not None:
        request_payload = _observed_request_metadata(
            plan, selected_request, backend=backend
        )
    else:
        request_payload = {}
    finding_comment_ids = sorted(
        (
            int(item["id"])
            for item in current_request_findings
            if isinstance(item.get("id"), int)
            and (not isinstance(item.get("id"), bool))
        )
    )
    if len(finding_comment_ids) != len(current_request_findings) or len(
        finding_comment_ids
    ) != len(set(finding_comment_ids)):
        raise ReviewError(
            "Provider inline findings omitted unique REST comment identities.",
            code="provider_response_invalid",
            exit_code=4,
        )
    payload = {
        "repo": repo,
        "pr": pr,
        "provider": provider,
        "request_binding": binding,
        "review_state": status,
        "head": head,
        "current_head": current_head,
        "head_is_current": head_is_current,
        "review": {
            "count": len(current_request_reviews),
            "latest_id": latest_formal_review.get("id")
            if latest_formal_review
            else None,
            "submitted_at": latest_formal_review.get("submitted_at")
            if latest_formal_review
            else None,
            "findings": len(current_request_findings),
            "finding_comment_ids": finding_comment_ids,
        },
        "request": request_payload,
        "request_error": request_error,
        "request_error_code": request_error_code,
        "request_observation": {
            "acknowledged": "eyes" in reactions,
            "clean_reaction": "+1" in reactions,
        },
        "terminal_comment": {
            "count": len(terminal_comments),
            "latest_id": latest_terminal_comment.get("comment_id")
            if latest_terminal_comment
            else None,
            "created_at": latest_terminal_comment.get("created_at")
            if latest_terminal_comment
            else None,
            "reviewed_head": latest_terminal_comment.get("reviewed_head")
            if latest_terminal_comment
            else None,
            "outcome": latest_terminal_comment.get("outcome")
            if latest_terminal_comment
            else None,
        },
        "evidence": evidence,
    }
    failure_kind, error_code = review_failure_classification(
        binding=binding,
        status=status,
        head_is_current=head_is_current,
        request_error_code=request_error_code,
        backend=backend,
    )
    payload["failure_kind"] = failure_kind
    payload["error_code"] = error_code
    payload["observation_fingerprint"] = stable_observation_fingerprint(
        payload, backend=backend
    )
    return payload


def _ready_timestamp(value: object, name: str, *, backend: Any) -> datetime:
    if not isinstance(value, str):
        raise ReviewError(
            f"{name} is missing.", code="ready_trigger_invalid", exit_code=64
        )
    try:
        parsed = backend.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ReviewError(
            f"{name} must be a canonical UTC timestamp.",
            code="ready_trigger_invalid",
            exit_code=64,
        ) from exc
    return parsed.replace(tzinfo=timezone.utc)


def _provider_timestamp(value: object, name: str, *, backend: Any) -> datetime:
    if not isinstance(value, str) or not value:
        raise ReviewError(
            f"Provider artifact {name} is missing.",
            code="provider_response_invalid",
            exit_code=4,
        )
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = backend.datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ReviewError(
            f"Provider artifact {name} is not a valid timestamp.",
            code="provider_response_invalid",
            exit_code=4,
        ) from exc
    if parsed.tzinfo is None:
        raise ReviewError(
            f"Provider artifact {name} has no timezone.",
            code="provider_response_invalid",
            exit_code=4,
        )
    return parsed.astimezone(timezone.utc)


def _ready_artifact(
    kind: str, item: dict[str, Any], outcome: str | None, *, backend: Any
) -> dict[str, Any]:
    object_id = item.get("id") if kind != "provider-comment" else item.get("comment_id")
    object_url = item.get("html_url")
    body = str(item.get("body") or "")
    return {
        "kind": kind,
        "object_id": object_id,
        "object_url": object_url,
        "actor": backend._item_login(item),
        "body_fingerprint": text_fingerprint(body) if body else None,
        "created_at": item.get("submitted_at") or item.get("created_at"),
        "outcome": outcome,
        "head": item.get("commit_id") or item.get("reviewed_head"),
    }


def check_ready_automated_review(
    repo: str,
    pr: int,
    provider: str,
    expected_head: str,
    ready_identity: dict[str, Any],
    *,
    backend: Any,
) -> dict[str, Any]:
    """Observe the provider review caused by one exact ready transition."""
    is_provider_author(provider, "", backend=backend)
    try:
        trigger = validate_ready_trigger(
            ready_identity,
            provider=provider,
            repository=repo,
            pr_number=pr,
            expected_head=expected_head,
        )
    except ReadyReviewError as exc:
        raise ReviewError(str(exc), code="ready_trigger_invalid", exit_code=64) from exc
    ready_at = _ready_timestamp(trigger["ready_at"], "ready_at", backend=backend)
    pull = backend.gh_json(
        ["api", f"repos/{repo}/pulls/{pr}", "-H", "Accept: application/vnd.github+json"]
    )
    if not isinstance(pull, dict):
        raise ReviewError(
            "Unexpected pull request response shape.", code="api_error", exit_code=4
        )
    current_head = str((pull.get("head") or {}).get("sha") or "").lower()
    if not FULL_SHA_PATTERN.fullmatch(current_head):
        raise ReviewError(
            "Pull request response did not include an exact head SHA.",
            code="api_error",
            exit_code=4,
        )
    current_is_draft = pull.get("draft")
    current_base = str((pull.get("base") or {}).get("ref") or "")
    current_body_fingerprint = text_fingerprint(str(pull.get("body") or ""))
    head_is_current = current_head == expected_head
    ready_is_current = current_is_draft is False
    base_is_current = current_base == trigger["base_branch"]
    body_is_current = current_body_fingerprint == trigger["body_fingerprint"]
    reviews = backend.gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/reviews")
    inline_comments = backend.gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/comments")
    conversation = backend.gh_api_paginated_list(f"repos/{repo}/issues/{pr}/comments")
    issue_reactions = backend.gh_api_paginated_list(
        f"repos/{repo}/issues/{pr}/reactions"
    )
    provider_reviews = [
        item
        for item in reviews
        if authored_by(item, provider, backend=backend)
        and sha_matches(item.get("commit_id"), expected_head, backend=backend)
        and (
            _provider_timestamp(
                item.get("submitted_at"), "submitted_at", backend=backend
            )
            > ready_at
        )
    ]
    top_level_findings = [
        item
        for item in inline_comments
        if authored_by(item, provider, backend=backend)
        and sha_matches(item.get("commit_id"), expected_head, backend=backend)
        and (item.get("in_reply_to_id") is None)
        and (
            _provider_timestamp(item.get("created_at"), "created_at", backend=backend)
            > ready_at
        )
    ]
    terminal_comments = []
    for item in conversation:
        parsed = provider_terminal_comment_any(item, provider, backend=backend)
        if parsed is None or not sha_matches(
            parsed.get("reviewed_head"), expected_head, backend=backend
        ):
            continue
        if (
            _provider_timestamp(parsed.get("created_at"), "created_at", backend=backend)
            > ready_at
        ):
            terminal_comments.append(parsed)
    clean_reactions = [
        item
        for item in issue_reactions
        if authored_by(item, provider, backend=backend)
        and str(item.get("content") or "") == "+1"
        and (
            _provider_timestamp(item.get("created_at"), "created_at", backend=backend)
            > ready_at
        )
    ]
    formal_outcomes: set[str] = set()
    for item in provider_reviews:
        state = str(item.get("state") or "").upper()
        if state == "CHANGES_REQUESTED":
            formal_outcomes.add("findings")
        elif state == "APPROVED":
            formal_outcomes.add("clean")
    if top_level_findings:
        formal_outcomes.add("findings")
    terminal_outcomes = {str(item["outcome"]) for item in terminal_comments}
    reaction_outcomes = {"clean"} if clean_reactions else set()
    outcomes = formal_outcomes | terminal_outcomes | reaction_outcomes
    evidence: dict[str, Any] = {
        "kind": "none",
        "object_id": None,
        "object_url": None,
        "actor": None,
        "body_fingerprint": None,
        "created_at": None,
        "outcome": None,
        "head": expected_head,
    }
    if terminal_comments:
        evidence = _ready_artifact(
            "provider-comment",
            terminal_comments[-1],
            terminal_comments[-1]["outcome"],
            backend=backend,
        )
    elif provider_reviews:
        latest = provider_reviews[-1]
        state = str(latest.get("state") or "").upper()
        evidence = _ready_artifact(
            "formal-review",
            latest,
            "findings"
            if state == "CHANGES_REQUESTED"
            else "clean"
            if state == "APPROVED"
            else None,
            backend=backend,
        )
    elif top_level_findings:
        evidence = _ready_artifact(
            "inline-finding", top_level_findings[0], "findings", backend=backend
        )
    elif clean_reactions:
        latest_reaction = max(
            clean_reactions, key=lambda item: str(item.get("created_at") or "")
        )
        evidence = {
            "kind": "clean-reaction",
            "object_id": latest_reaction.get("id"),
            "object_url": pull.get("html_url") or trigger["ready_ref"],
            "actor": backend._item_login(latest_reaction),
            "body_fingerprint": None,
            "created_at": latest_reaction.get("created_at"),
            "outcome": "clean",
            "head": expected_head,
        }
    if (
        not head_is_current
        or not ready_is_current
        or (not base_is_current)
        or (not body_is_current)
    ):
        review_state = "stale"
    elif len(terminal_comments) > 1 or len(outcomes) > 1:
        review_state = "ambiguous"
    elif len(outcomes) == 1:
        review_state = next(iter(outcomes))
    else:
        review_state = "pending"
    finding_ids = sorted(
        (
            int(item["id"])
            for item in top_level_findings
            if isinstance(item.get("id"), int)
            and (not isinstance(item.get("id"), bool))
        )
    )
    payload: dict[str, Any] = {
        "repo": repo,
        "pr": pr,
        "provider": provider,
        "ready_trigger": trigger,
        "review_state": review_state,
        "head": expected_head,
        "current_head": current_head,
        "head_is_current": head_is_current,
        "pr_is_ready": ready_is_current,
        "base_is_current": base_is_current,
        "body_is_current": body_is_current,
        "review": {
            "count": len(provider_reviews),
            "findings": len(top_level_findings),
            "finding_comment_ids": finding_ids,
        },
        "terminal_comment": {
            "count": len(terminal_comments),
            "outcomes": sorted(terminal_outcomes),
        },
        "clean_reaction": {
            "count": len(clean_reactions),
            "latest_id": evidence.get("object_id")
            if evidence.get("kind") == "clean-reaction"
            else None,
        },
        "evidence": evidence,
        "failure_kind": "head-drift"
        if review_state == "stale"
        else "ambiguous-provider-evidence"
        if review_state == "ambiguous"
        else None,
        "error_code": "head_drift"
        if review_state == "stale"
        else "ambiguous_review_evidence"
        if review_state == "ambiguous"
        else None,
    }
    payload["observation_fingerprint"] = stable_observation_fingerprint(
        payload, backend=backend
    )
    payload["certificate"] = {
        "schema": "g-codex-ready-review-certificate:v1",
        "provider": provider,
        "repository": repo,
        "pr_number": pr,
        "head_sha": expected_head,
        "ready_trigger_fingerprint": trigger["trigger_fingerprint"],
        "review_state": review_state,
        "evidence": evidence,
        "finding_comment_ids": finding_ids,
        "observation_fingerprint": payload["observation_fingerprint"],
    }
    return payload


def wait_for_ready_automated_review(
    repo: str,
    pr: int,
    provider: str,
    expected_head: str,
    timeout: float,
    interval: float,
    max_interval: float,
    ready_identity: dict[str, Any],
    *,
    backend: Any,
) -> tuple[dict[str, Any], int]:
    deadline = time.monotonic() + timeout
    attempts = 0
    current_interval = interval
    last: dict[str, Any] | None = None
    while True:
        attempts += 1
        last = backend.check_ready_automated_review(
            repo, pr, provider, expected_head, ready_identity
        )
        last["attempts"] = attempts
        if last["review_state"] in {"clean", "findings", "stale", "ambiguous"}:
            return (last, REVIEW_EXIT_CODES.get(str(last["review_state"]), 4))
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            last["timed_out"] = True
            last["review_state"] = "pending"
            return (last, 124)
        time.sleep(min(current_interval, remaining))
        current_interval = min(max_interval, current_interval * 2)


def terminal_provider_evidence(
    repo: str,
    pr: int,
    provider: str,
    expected_head: str,
    request_identity: dict[str, Any],
    *,
    backend: Any,
) -> dict[str, Any]:
    """Independently prove one exact-lineage provider terminal comment."""
    is_provider_author(provider, "", backend=backend)
    try:
        head = validate_full_head(expected_head)
        saved = validate_receipt(
            request_identity,
            provider=provider,
            repository=repo,
            pr_number=pr,
            expected_head=head,
        )
    except ValueError as exc:
        raise ReviewError(
            str(exc), code="terminal_evidence_request_mismatch", exit_code=64
        ) from exc
    pull = backend.gh_json(
        ["api", f"repos/{repo}/pulls/{pr}", "-H", "Accept: application/vnd.github+json"]
    )
    if not isinstance(pull, dict) or not isinstance(
        (pull.get("head") or {}).get("sha"), str
    ):
        raise ReviewError(
            "Pull request response did not include an exact head SHA.",
            code="terminal_evidence_invalid",
            exit_code=4,
        )
    current_head = str((pull.get("head") or {}).get("sha") or "").lower()
    if current_head != head:
        raise ReviewError(
            "The pull request head changed before terminal evidence verification.",
            code="terminal_evidence_head_drift",
            exit_code=3,
        )
    plan = build_request(provider, repo, pr, head, str(saved["request_key"]))
    try:
        request_comment = backend._api_object(
            f"repos/{repo}/issues/comments/{saved['comment_id']}"
        )
    except ReviewError as exc:
        raise ReviewError(
            "The exact typed review request comment is unavailable.",
            code="terminal_evidence_request_mismatch",
            exit_code=4,
        ) from exc
    if not _comment_for_plan(
        request_comment, plan, backend=backend
    ) or not receipt_matches(plan, request_comment, saved):
        raise ReviewError(
            "The exact typed review request comment no longer matches its receipt.",
            code="terminal_evidence_request_mismatch",
            exit_code=4,
        )
    reviews = backend.gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/reviews")
    inline_comments = backend.gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/comments")
    conversation = backend.gh_api_paginated_list(f"repos/{repo}/issues/{pr}/comments")
    request_created_at = str(saved["created_at"])
    later_requests = [
        item
        for item in conversation
        if str(item.get("created_at") or "") > request_created_at
        and parse_request(item.get("body") or "", provider, repo, pr).classification
        != "absent"
    ]
    if later_requests:
        raise ReviewError(
            "A later or overlapping Codex request makes the request lineage ambiguous.",
            code="terminal_evidence_ambiguous",
            exit_code=4,
        )
    terminal_comments = [
        (item, parsed)
        for item in conversation
        if str(item.get("created_at") or "") > request_created_at
        and (parsed := provider_terminal_comment_any(item, provider, backend=backend))
        is not None
    ]
    if not terminal_comments:
        raise ReviewError(
            "No terminal provider artifact exists for the exact request lineage.",
            code="terminal_evidence_not_found",
            exit_code=2,
        )
    if any(
        (
            not sha_matches(parsed["reviewed_head"], head, backend=backend)
            for _, parsed in terminal_comments
        )
    ):
        raise ReviewError(
            "Terminal provider artifacts disagree with the exact request head.",
            code="terminal_evidence_ambiguous",
            exit_code=4,
        )
    if len(terminal_comments) != 1:
        raise ReviewError(
            "Multiple terminal provider artifacts match the exact request lineage.",
            code="terminal_evidence_ambiguous",
            exit_code=4,
        )
    conflicting_findings = [
        item
        for item in inline_comments
        if authored_by(item, provider, backend=backend)
        and item.get("in_reply_to_id") is None
        and (str(item.get("created_at") or "") > request_created_at)
        and sha_matches(item.get("commit_id"), head, backend=backend)
    ]
    conflicting_reviews = []
    for item in reviews:
        if (
            not authored_by(item, provider, backend=backend)
            or not sha_matches(item.get("commit_id"), head, backend=backend)
            or str(item.get("submitted_at") or "") <= request_created_at
        ):
            continue
        body = str(item.get("body") or "")
        state = str(item.get("state") or "").upper()
        if (
            state in {"CHANGES_REQUESTED", "DISMISSED"}
            or CODEX_FINDINGS_RESULT.search(body)
            or CODEX_ERROR_RESULT.search(body)
        ):
            conflicting_reviews.append(item)
    if conflicting_findings or conflicting_reviews:
        raise ReviewError(
            "Conflicting provider findings or terminal outcomes exist for the exact request lineage.",
            code="terminal_evidence_ambiguous",
            exit_code=4,
        )
    artifact, parsed = terminal_comments[0]
    artifact_id = artifact.get("id")
    if (
        not isinstance(artifact_id, int)
        or isinstance(artifact_id, bool)
        or artifact_id < 1
    ):
        raise ReviewError(
            "The terminal provider artifact lacks an exact identity.",
            code="terminal_evidence_invalid",
            exit_code=4,
        )
    exact_artifact = backend._api_object(f"repos/{repo}/issues/comments/{artifact_id}")
    exact_parsed = provider_terminal_comment_any(
        exact_artifact, provider, backend=backend
    )
    if (
        exact_parsed is None
        or exact_artifact.get("body") != artifact.get("body")
        or exact_artifact.get("html_url") != artifact.get("html_url")
        or (exact_artifact.get("created_at") != artifact.get("created_at"))
        or (
            str((exact_artifact.get("user") or {}).get("login") or "")
            != str((artifact.get("user") or {}).get("login") or "")
        )
        or (exact_parsed["reviewed_head"] != parsed["reviewed_head"])
        or (exact_parsed["outcome"] != parsed["outcome"])
    ):
        raise ReviewError(
            "The exact terminal provider artifact changed during verification.",
            code="terminal_evidence_invalid",
            exit_code=4,
        )
    final_pull = backend.gh_json(
        ["api", f"repos/{repo}/pulls/{pr}", "-H", "Accept: application/vnd.github+json"]
    )
    if not isinstance(final_pull, dict) or not isinstance(
        (final_pull.get("head") or {}).get("sha"), str
    ):
        raise ReviewError(
            "Final pull request response did not include an exact head SHA.",
            code="terminal_evidence_invalid",
            exit_code=4,
        )
    try:
        final_head = validate_full_head(
            str((final_pull.get("head") or {}).get("sha") or "")
        )
    except ValueError as exc:
        raise ReviewError(
            "Final pull request response did not include a valid full head SHA.",
            code="terminal_evidence_invalid",
            exit_code=4,
        ) from exc
    if final_head != head:
        raise ReviewError(
            "The pull request head changed during terminal evidence verification.",
            code="terminal_evidence_head_drift",
            exit_code=3,
        )
    receipt_value = backend.build_terminal_evidence_receipt(
        provider=provider,
        repository=repo,
        pr_number=pr,
        head_sha=head,
        request_receipt=saved,
        artifact={
            **exact_artifact,
            "reviewed_head_token": exact_parsed["reviewed_head"],
            "outcome": exact_parsed["outcome"],
        },
        verified_at=backend.datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
    )
    validate_terminal_evidence_receipt(receipt_value)
    return receipt_value


def wait_for_automated_review(
    repo: str,
    pr: int,
    provider: str,
    expected_head: str | None,
    timeout: float,
    initial_interval: float,
    max_interval: float,
    request_identity: dict[str, Any] | None = None,
    *,
    backend: Any,
) -> tuple[dict[str, Any], int]:
    if not _receipt_is_complete(request_identity, backend=backend):
        return (
            {
                "repo": repo,
                "pr": pr,
                "provider": provider,
                "request_binding": "invalid",
                "review_state": None,
                "error": "The identity-bound automated review waiter requires a complete request receipt.",
                "attempts": 0,
            },
            REQUEST_BINDING_EXIT_CODES["invalid"],
        )
    started = time.monotonic()
    interval = initial_interval
    attempts = 0
    transitions = 0
    unchanged_attempts = 0
    previous_fingerprint: str | None = None
    while True:
        attempts += 1
        payload = backend.check_automated_review(
            repo, pr, provider, expected_head, request_identity
        )
        fingerprint = str(payload.get("observation_fingerprint") or "")
        if previous_fingerprint is None or fingerprint != previous_fingerprint:
            transitions += 1
        else:
            unchanged_attempts += 1
        previous_fingerprint = fingerprint
        payload["attempts"] = attempts
        payload["state_transitions"] = transitions
        payload["unchanged_attempts"] = unchanged_attempts
        payload["elapsed_seconds"] = round(time.monotonic() - started, 3)
        binding = str(payload.get("request_binding") or "unknown")
        status_value = payload.get("review_state")
        status = str(status_value) if status_value is not None else ""
        if status == "stale":
            return (payload, REVIEW_EXIT_CODES[status])
        if binding != "recognized":
            if binding == "absent" and status == "not-requested":
                return (payload, REVIEW_EXIT_CODES[status])
            return (payload, REQUEST_BINDING_EXIT_CODES.get(binding, 4))
        if status in {"clean", "findings", "not-requested", "stale", "error"}:
            return (payload, REVIEW_EXIT_CODES[status])
        remaining = timeout - (time.monotonic() - started)
        if remaining <= 0:
            payload["timed_out"] = True
            return (payload, 124)
        time.sleep(min(interval, remaining))
        interval = min(max_interval, interval * 1.5)
