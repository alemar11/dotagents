from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from shutil import which
from typing import Any


from . import __version__ as VERSION
from .common import GitStackError
from .provider_text import (
    API_VERSION,
    ProviderText,
    api_request,
    prove_mutation,
    read_text_file,
    response_text_matches,
    require_worktree,
    verify_response_text,
    verify_worktree_unchanged,
)
from .review_request import (
    RequestPlan,
    build_request,
    parse_request,
    receipt,
    receipt_matches,
    validate_receipt,
    validate_full_head,
)
REPO_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")
CODEX_LOGINS = {"chatgpt-codex-connector[bot]", "chatgpt-codex-connector"}
CODEX_TERMINAL_PREFIX = re.compile(r"(?im)^\s*Codex Review\s*:")
CODEX_CLEAN_RESULT = re.compile(
    r"(?i)(?:did(?:n['’]t| not) find any major issues|no major issues|no issues found|no findings|looks good)"
)
CODEX_ERROR_RESULT = re.compile(
    r"(?i)(?:unable to (?:complete|perform|review)|could(?:n['’]t| not) (?:complete|perform|review)|review (?:failed|errored)|encountered an error)"
)
CODEX_FINDINGS_RESULT = re.compile(
    r"(?im)(?:found\s+(?:\d+\s+|some\s+|the following\s+)?(?:issues?|findings?)|(?:issues?|findings?)\s+to\s+address|actionable\s+(?:issue|finding)|^\s*(?:[-*]\s*|#{1,6}\s*)?\[P[0-3]\])"
)
REVIEWED_COMMIT = re.compile(
    r"(?im)^\s*\*{0,2}Reviewed commit\s*:\s*\*{0,2}\s*`?([0-9a-f]{7,40})`?"
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


@dataclass(frozen=True)
class RunResult:
    returncode: int
    stdout: str
    stderr: str


class ReviewError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "command_failed",
        exit_code: int = 1,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.exit_code = exit_code
        self.details = details


class StrictParser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("allow_abbrev", False)
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> None:
        raise ReviewError("Invalid command arguments.", code="invalid_arguments", exit_code=64)


def run(command: list[str], *, cwd: Path | None = None) -> RunResult:
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    except FileNotFoundError:
        return RunResult(127, "", f"{command[0]} is not installed or not on PATH.")
    return RunResult(completed.returncode, completed.stdout, completed.stderr)


def run_gh(args: list[str]) -> RunResult:
    return run(["gh", *args])


def gh_json(args: list[str]) -> object:
    result = run_gh(args)
    if result.returncode != 0:
        raise ReviewError((result.stderr or result.stdout or "gh command failed").strip(), exit_code=result.returncode)
    try:
        return json.loads(result.stdout or "null")
    except json.JSONDecodeError as exc:
        raise ReviewError(f"Failed to parse gh JSON output: {exc}") from exc


def gh_api_paginated_list(endpoint: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    page = 1
    while True:
        payload = gh_json(["api", endpoint, "-X", "GET", "-F", "per_page=100", "-F", f"page={page}", "-H", "Accept: application/vnd.github+json"])
        if not isinstance(payload, list):
            raise ReviewError(f"Unexpected response shape for {endpoint}.")
        items.extend([item for item in payload if isinstance(item, dict)])
        if len(payload) < 100:
            break
        page += 1
    return items


def graphql(query: str, variables: dict[str, object]) -> object:
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        if value is None:
            args.extend(["-F", f"{key}=null"])
        else:
            args.extend(["-F", f"{key}={value}"])
    return gh_json(args)


def validate_repo(repo: str) -> str:
    value = repo.strip()
    if not REPO_PATTERN.fullmatch(value):
        raise ReviewError(f"Invalid repository '{repo}'. Use owner/repo.", code="invalid_arguments", exit_code=64)
    return value


def normalize_remote(remote: str | None) -> str | None:
    if not remote:
        return None
    repo = re.sub(r"^git@[^:]+:", "", remote)
    repo = re.sub(r"^https?://[^/]+/", "", repo)
    repo = re.sub(r"^ssh://[^/]+/", "", repo)
    repo = re.sub(r"^git://[^/]+/", "", repo)
    repo = re.sub(r"\.git$", "", repo).rstrip("/")
    return repo if REPO_PATTERN.fullmatch(repo) else None


def resolve_repo(repo: str | None, *, allow_non_project: bool) -> str:
    if repo:
        return validate_repo(repo)
    root = run(["git", "rev-parse", "--show-toplevel"])
    if root.returncode != 0:
        if allow_non_project:
            raise ReviewError("Pass --repo owner/repo when using --allow-non-project.", code="repo_context_missing", exit_code=2)
        raise ReviewError("No git repository detected. Pass --repo owner/repo.", code="repo_context_missing", exit_code=3)
    remote = run(["git", "remote", "get-url", "origin"], cwd=Path(root.stdout.strip()))
    if remote.returncode != 0:
        raise ReviewError("No origin remote found. Pass --repo owner/repo.", code="repo_context_missing", exit_code=4)
    resolved = normalize_remote(remote.stdout.strip())
    if not resolved:
        raise ReviewError("Could not resolve owner/repo from origin remote.", code="repo_context_missing", exit_code=5)
    return resolved


def positive_int(raw: str | None, name: str) -> int:
    if not raw or not re.fullmatch(r"[1-9][0-9]*", raw):
        raise ReviewError(f"Invalid --{name} value '{raw or ''}'. Use a positive integer.", code="invalid_arguments", exit_code=64)
    return int(raw)


def duration_seconds(raw: str, name: str) -> float:
    match = re.fullmatch(r"([1-9][0-9]*)([smh]?)", raw.strip().lower())
    if not match:
        raise ReviewError(
            f"Invalid --{name} value '{raw}'. Use a positive duration such as 30s, 15m, or 1h.",
            code="invalid_arguments",
            exit_code=64,
        )
    multipliers = {"": 1, "s": 1, "m": 60, "h": 3600}
    return int(match.group(1)) * multipliers[match.group(2)]


def is_provider_author(provider: str, login: str) -> bool:
    if provider != "codex":
        raise ReviewError(
            f"Unsupported review provider '{provider}'. Supported providers: codex.",
            code="unsupported_provider",
            exit_code=64,
        )
    return login.lower() in CODEX_LOGINS


def authored_by(item: dict[str, Any], provider: str) -> bool:
    return is_provider_author(provider, str((item.get("user") or {}).get("login") or ""))


def sha_matches(actual: object, expected: str) -> bool:
    value = str(actual or "").lower()
    target = expected.lower()
    return bool(value and target and (value.startswith(target) or target.startswith(value)))


def validate_head(raw: str) -> str:
    value = raw.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{7,40}", value):
        raise ReviewError(
            f"Invalid --head value '{raw}'. Use a hexadecimal commit SHA or unambiguous 7-40 character prefix.",
            code="invalid_arguments",
            exit_code=64,
        )
    return value


def provider_terminal_comment_any(
    comment: dict[str, Any],
    provider: str,
) -> dict[str, Any] | None:
    if not authored_by(comment, provider):
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
        "created_at": created_at,
        "reviewed_head": reviewed_head,
        "outcome": outcome,
    }


def stable_observation_fingerprint(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def provider_reactions(repo: str, comment_id: int, provider: str) -> set[str]:
    reactions = gh_api_paginated_list(f"repos/{repo}/issues/comments/{comment_id}/reactions")
    return {
        str(reaction.get("content") or "")
        for reaction in reactions
        if authored_by(reaction, provider)
    }


def _receipt_is_complete(value: object) -> bool:
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
    value: object,
    provider: str,
    repository: str,
    pr_number: int,
) -> RequestPlan | None:
    if not _receipt_is_complete(value):
        return None
    assert isinstance(value, dict)
    if value.get("provider") != provider or value.get("repository") != repository or value.get("pr_number") != pr_number:
        return None
    try:
        validate_receipt(
            value,
            provider=provider,
            repository=repository,
            pr_number=pr_number,
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
    if value.get("request_fingerprint") != plan.request_fingerprint or value.get("body_fingerprint") != plan.body_fingerprint:
        return None
    return plan


def _comment_for_plan(
    comment: dict[str, Any],
    plan: RequestPlan,
) -> bool:
    parsed = parse_request(comment.get("body") or "", plan.provider, plan.repository, plan.pr_number)
    return (
        parsed.classification == "canonical"
        and parsed.head_sha == plan.head_sha
        and parsed.request_key == plan.request_key
        and parsed.request_fingerprint == plan.request_fingerprint
        and parsed.body_fingerprint == plan.body_fingerprint
        and str(comment.get("body") or "") == plan.body
    )


def _request_conflicts(
    conversation: list[dict[str, Any]],
    plan: RequestPlan,
) -> tuple[str | None, list[dict[str, Any]]]:
    exact: list[dict[str, Any]] = []
    for item in conversation:
        parsed = parse_request(item.get("body") or "", plan.provider, plan.repository, plan.pr_number)
        if parsed.classification == "canonical" and parsed.head_sha == plan.head_sha:
            if _comment_for_plan(item, plan):
                exact.append(item)
            else:
                return "invalid", exact
        elif parsed.classification == "invalid" and parsed.head_sha == plan.head_sha:
            return "invalid", exact
    if len(exact) > 1:
        return "ambiguous", exact
    return None, exact


def _observed_request_metadata(
    plan: RequestPlan,
    comment: dict[str, Any],
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
) -> dict[str, Any]:
    # Validate before any network reads so unsupported providers fail predictably.
    is_provider_author(provider, "")
    pull = gh_json(["api", f"repos/{repo}/pulls/{pr}", "-H", "Accept: application/vnd.github+json"])
    if not isinstance(pull, dict):
        raise ReviewError("Unexpected pull request response shape.", code="api_error", exit_code=4)
    current_head = str(((pull.get("head") or {}).get("sha")) or "")
    if not current_head:
        raise ReviewError("Pull request response did not include a head SHA.", code="api_error", exit_code=4)
    current_head = validate_head(current_head)
    requested_head = validate_head(expected_head) if expected_head else current_head
    head = current_head if sha_matches(current_head, requested_head) else requested_head
    head_is_current = sha_matches(current_head, head)

    reviews = gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/reviews")
    inline_comments = gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/comments")
    conversation = gh_api_paginated_list(f"repos/{repo}/issues/{pr}/comments")
    provider_reviews = [item for item in reviews if authored_by(item, provider)]
    head_reviews = [item for item in provider_reviews if sha_matches(item.get("commit_id"), head)]
    head_findings = [
        item
        for item in inline_comments
        if authored_by(item, provider) and sha_matches(item.get("commit_id"), head)
    ]

    saved_plan = _request_plan_from_receipt(request_identity, provider, repo, pr) if request_identity else None
    binding = "absent"
    selected_request: dict[str, Any] | None = None
    selected_receipt: dict[str, Any] | None = None
    selected_plan: RequestPlan | None = saved_plan
    request_error: str | None = None
    if request_identity is not None and saved_plan is None:
        binding = "invalid"
    elif saved_plan is not None:
        binding = "unknown"
        try:
            comment_id = int(request_identity["comment_id"])  # type: ignore[index]
            selected_request = _api_object(f"repos/{repo}/issues/comments/{comment_id}")
            if not _comment_for_plan(selected_request, saved_plan) or not receipt_matches(saved_plan, selected_request, request_identity):
                binding = "invalid"
                request_error = "The persisted request receipt does not match the exact provider comment."
            else:
                binding = "recognized"
                selected_receipt = request_identity
        except (ReviewError, KeyError, TypeError, ValueError) as exc:
            request_error = str(exc)
    else:
        candidate_plan: RequestPlan | None = None
        for item in conversation:
            parsed = parse_request(item.get("body") or "", provider, repo, pr)
            if parsed.classification == "canonical" and parsed.head_sha and sha_matches(parsed.head_sha, head):
                if candidate_plan is None:
                    try:
                        candidate_plan = build_request(provider, repo, pr, parsed.head_sha, str(parsed.request_key))
                        selected_request = item
                    except (TypeError, ValueError):
                        binding = "invalid"
                        break
                else:
                    binding = "ambiguous"
                    break
        if binding == "absent" and candidate_plan is not None and selected_request is not None:
            binding = "recognized"
            selected_plan = candidate_plan
        if binding == "absent":
            conflict, _ = _request_conflicts(
                conversation,
                build_request(provider, repo, pr, current_head if head_is_current else head, "diagnostic"),
            ) if head_is_current else (None, [])
            if conflict:
                binding = conflict
            elif any(
                parse_request(item.get("body") or "", provider, repo, pr).classification == "unbound"
                for item in conversation
            ):
                binding = "unbound"

    plan = selected_plan

    if plan is not None and selected_request is not None:
        conflict, exact = _request_conflicts(conversation, plan)
        if conflict == "ambiguous" or len(exact) > 1:
            binding = "ambiguous"
        elif conflict == "invalid":
            binding = conflict

    request_created_at = (
        str(selected_receipt.get("created_at") or "")
        if selected_receipt
        else str(selected_request.get("created_at") or "") if selected_request else ""
    )
    reactions: set[str] = set()
    if binding == "recognized" and selected_request and selected_request.get("id"):
        try:
            reactions = provider_reactions(repo, int(selected_request["id"]), provider)
        except ReviewError as exc:
            binding = "unknown"
            request_error = str(exc)

    current_request_reviews = [
        item for item in head_reviews
        if request_created_at and str(item.get("submitted_at") or "") > request_created_at
    ] if binding == "recognized" else []
    current_request_findings = [
        item for item in head_findings
        if request_created_at and str(item.get("created_at") or "") > request_created_at
    ] if binding == "recognized" else []
    latest_formal_review = max(
        current_request_reviews,
        key=lambda item: str(item.get("submitted_at") or ""),
        default=None,
    )
    all_terminal_comments = [
        result for item in conversation
        if (result := provider_terminal_comment_any(item, provider)) is not None
    ]
    terminal_comments = [
        result for result in all_terminal_comments
        if binding == "recognized" and request_created_at and str(result.get("created_at") or "") > request_created_at
        and sha_matches(result.get("reviewed_head"), head)
    ]
    mismatched_terminal_comments = [
        result for result in all_terminal_comments
        if binding == "recognized" and request_created_at
        and str(result.get("created_at") or "") > request_created_at
        and not sha_matches(result.get("reviewed_head"), head)
    ]
    latest_terminal_comment = max(
        terminal_comments,
        key=lambda item: str(item.get("created_at") or ""),
        default=None,
    )
    if latest_terminal_comment and selected_request and len([item for item in conversation if _comment_for_plan(item, plan)]) > 1:  # type: ignore[arg-type]
        raise ReviewError(
            "A terminal Codex result cannot be correlated across duplicate exact requests.",
            code="ambiguous_review_evidence",
            exit_code=4,
        )

    formal_outcome = "findings" if current_request_findings else ("clean" if current_request_reviews else None)
    terminal_outcomes = {
        outcome for outcome in (
            formal_outcome,
            *(str(result.get("outcome") or "") for result in terminal_comments),
            "clean" if "+1" in reactions else None,
        ) if outcome
    }
    if binding == "recognized" and head_is_current and len(terminal_outcomes) > 1:
        raise ReviewError(
            "Conflicting terminal Codex review evidence exists for the current PR head.",
            code="ambiguous_review_evidence",
            exit_code=4,
        )

    evidence: dict[str, Any] = {
        "kind": "none",
        "object_id": None,
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
            "created_at": mismatched.get("created_at"),
            "outcome": mismatched.get("outcome"),
            "head": mismatched.get("reviewed_head"),
        }
    elif latest_terminal_comment:
        status = str(latest_terminal_comment["outcome"])
        evidence = {
            "kind": "provider-comment",
            "object_id": latest_terminal_comment.get("comment_id"),
            "created_at": latest_terminal_comment.get("created_at"),
            "outcome": status,
            "head": latest_terminal_comment.get("reviewed_head"),
        }
    elif latest_formal_review:
        status = str(formal_outcome)
        evidence = {
            "kind": "formal-review",
            "object_id": latest_formal_review.get("id"),
            "created_at": latest_formal_review.get("submitted_at"),
            "outcome": status,
            "head": latest_formal_review.get("commit_id"),
        }
    elif "+1" in reactions:
        status = "clean"
        evidence = {
            "kind": "clean-reaction",
            "object_id": selected_request.get("id") if selected_request else None,
            "created_at": selected_request.get("created_at") if selected_request else None,
            "outcome": status,
            "head": head,
        }
    else:
        status = "acknowledged" if "eyes" in reactions else "pending"

    if selected_receipt is not None:
        request_payload: dict[str, Any] = dict(selected_receipt)
    elif plan is not None and selected_request is not None:
        request_payload = _observed_request_metadata(plan, selected_request)
    else:
        request_payload = {}
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
            "latest_id": latest_formal_review.get("id") if latest_formal_review else None,
            "submitted_at": latest_formal_review.get("submitted_at") if latest_formal_review else None,
            "findings": len(current_request_findings),
        },
        "request": request_payload,
        "request_error": request_error,
        "request_observation": {
            "acknowledged": "eyes" in reactions,
            "clean_reaction": "+1" in reactions,
        },
        "terminal_comment": {
            "count": len(terminal_comments),
            "latest_id": latest_terminal_comment.get("comment_id") if latest_terminal_comment else None,
            "created_at": latest_terminal_comment.get("created_at") if latest_terminal_comment else None,
            "reviewed_head": latest_terminal_comment.get("reviewed_head") if latest_terminal_comment else None,
            "outcome": latest_terminal_comment.get("outcome") if latest_terminal_comment else None,
        },
        "evidence": evidence,
    }
    payload["observation_fingerprint"] = stable_observation_fingerprint(payload)
    return payload


def wait_for_automated_review(
    repo: str,
    pr: int,
    provider: str,
    expected_head: str | None,
    timeout: float,
    initial_interval: float,
    max_interval: float,
    request_identity: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], int]:
    if not _receipt_is_complete(request_identity):
        return {
            "repo": repo,
            "pr": pr,
            "provider": provider,
            "request_binding": "invalid",
            "review_state": None,
            "error": "The identity-bound automated review waiter requires a complete request receipt.",
            "attempts": 0,
        }, REQUEST_BINDING_EXIT_CODES["invalid"]
    started = time.monotonic()
    interval = initial_interval
    attempts = 0
    transitions = 0
    unchanged_attempts = 0
    previous_fingerprint: str | None = None
    while True:
        attempts += 1
        payload = check_automated_review(repo, pr, provider, expected_head, request_identity)
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
            return payload, REVIEW_EXIT_CODES[status]
        if binding != "recognized":
            if binding == "absent" and status == "not-requested":
                return payload, REVIEW_EXIT_CODES[status]
            return payload, REQUEST_BINDING_EXIT_CODES.get(binding, 4)
        if status in {"clean", "findings", "not-requested", "stale", "error"}:
            return payload, REVIEW_EXIT_CODES[status]
        remaining = timeout - (time.monotonic() - started)
        if remaining <= 0:
            payload["timed_out"] = True
            return payload, 124
        time.sleep(min(interval, remaining))
        interval = min(max_interval, interval * 1.5)


def snippet(text: str, limit: int = 220) -> str:
    compact = (text or "").replace("\r\n", "\n").replace("\n", " ").strip()
    return compact[: limit - 3] + "..." if len(compact) > limit else compact


def review_threads(repo: str, pr: int, include_resolved: bool) -> list[dict[str, Any]]:
    owner, repo_name = repo.split("/", 1)
    query = """
query($owner: String!, $repo: String!, $number: Int!, $after: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 50, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          isResolved
          isOutdated
          path
          line
          startLine
          comments(first: 100) {
            nodes {
              databaseId
              body
              createdAt
              updatedAt
              author { login }
            }
          }
        }
      }
    }
  }
}
""".strip()
    entries: list[dict[str, Any]] = []
    after: str | None = None
    while True:
        payload = graphql(query, {"owner": owner, "repo": repo_name, "number": pr, "after": after})
        threads = (((payload.get("data") or {}).get("repository") or {}).get("pullRequest") or {}).get("reviewThreads") or {}
        for thread in threads.get("nodes") or []:
            if not isinstance(thread, dict):
                continue
            resolved = bool(thread.get("isResolved"))
            outdated = bool(thread.get("isOutdated"))
            active = (not resolved) and (not outdated)
            if not include_resolved and not active:
                continue
            for comment in ((thread.get("comments") or {}).get("nodes") or []):
                if isinstance(comment, dict) and comment.get("databaseId"):
                    entries.append(
                        {
                            "type": "review_thread_comment",
                            "comment_id": int(comment["databaseId"]),
                            "author": ((comment.get("author") or {}).get("login") or ""),
                            "updated": comment.get("updatedAt") or comment.get("createdAt") or "",
                            "body": comment.get("body") or "",
                            "body_preview": snippet(comment.get("body") or ""),
                            "path": thread.get("path") or "",
                            "line": thread.get("line"),
                            "start_line": thread.get("startLine"),
                            "is_resolved": resolved,
                            "is_outdated": outdated,
                        }
                    )
        page_info = threads.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
        if not after:
            break
    return entries


def collect_entries(repo: str, pr: int, include_resolved: bool) -> list[dict[str, Any]]:
    thread_entries = review_threads(repo, pr, include_resolved)
    known_thread_ids = {entry["comment_id"] for entry in thread_entries}
    review_comments = gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/comments")
    conversation_comments = gh_api_paginated_list(f"repos/{repo}/issues/{pr}/comments")
    entries = list(thread_entries)
    for comment in review_comments:
        if comment.get("id") and int(comment["id"]) not in known_thread_ids:
            entries.append(
                {
                    "type": "review_comment",
                    "comment_id": int(comment["id"]),
                    "author": ((comment.get("user") or {}).get("login") or ""),
                    "updated": comment.get("updated_at") or comment.get("created_at") or "",
                    "body": comment.get("body") or "",
                    "body_preview": snippet(comment.get("body") or ""),
                    "path": comment.get("path") or "",
                    "line": comment.get("line"),
                    "start_line": comment.get("start_line"),
                    "is_resolved": None,
                    "is_outdated": None,
                }
            )
    for comment in conversation_comments:
        if comment.get("id"):
            entries.append(
                {
                    "type": "conversation_comment",
                    "comment_id": int(comment["id"]),
                    "author": ((comment.get("user") or {}).get("login") or ""),
                    "updated": comment.get("updated_at") or comment.get("created_at") or "",
                    "body": comment.get("body") or "",
                    "body_preview": snippet(comment.get("body") or ""),
                    "path": "",
                    "line": None,
                    "start_line": None,
                    "is_resolved": None,
                    "is_outdated": None,
                }
            )
    for index, entry in enumerate(entries, start=1):
        entry["index"] = index
    return entries


def _review_error(exc: GitStackError) -> ReviewError:
    return ReviewError(str(exc), code=exc.code, exit_code=exc.exit_code, details=exc.details)


def _api_object(endpoint: str) -> dict[str, Any]:
    payload = gh_json([
        "api", endpoint, "--method", "GET",
        "--header", "Accept: application/vnd.github+json",
        "--header", f"X-GitHub-Api-Version: {API_VERSION}",
    ])
    if not isinstance(payload, dict):
        raise ReviewError("GitHub read-back returned an unexpected response.", code="provider_response_invalid", exit_code=65)
    return payload


def _viewer_login() -> str:
    payload = _api_object("user")
    login = payload.get("login")
    if not isinstance(login, str) or not login:
        raise ReviewError("Could not resolve the authenticated GitHub identity.", code="provider_identity_missing", exit_code=65)
    return login


def _verify_pr_target(repo: str, pr: int) -> dict[str, Any]:
    payload = _api_object(f"repos/{repo}/pulls/{pr}")
    if payload.get("number") != pr or not str(payload.get("url") or "").endswith(f"/repos/{repo}/pulls/{pr}"):
        raise ReviewError("GitHub pull-request read-back did not match the requested target.", code="provider_target_mismatch", exit_code=65)
    return payload


def _in_creation_window(item: dict[str, Any], field: str, started_at: str, finished_at: str) -> bool:
    timestamp = str(item.get(field) or "")
    return bool(timestamp and started_at <= timestamp <= finished_at)


def _proof(item: dict[str, Any], body: ProviderText, *, target: dict[str, Any], status: str) -> dict[str, Any]:
    verify_response_text(item, body)
    object_id = item.get("id")
    url = item.get("html_url")
    if not isinstance(object_id, int) or not isinstance(url, str) or not url:
        raise GitStackError("GitHub response omitted provider object identity.", code="provider_identity_missing", exit_code=65)
    return {"status": status, "id": object_id, "url": url, "target": target, "text": body.proof()}


def _proof_failure(message: str, code: str) -> GitStackError:
    return GitStackError(message, code=code, exit_code=65)


def _item_login(item: dict[str, Any]) -> str:
    user = item.get("user")
    return str(user.get("login") or "") if isinstance(user, dict) else ""


def _read_back_list(endpoint: str) -> list[dict[str, Any]]:
    try:
        return gh_api_paginated_list(endpoint)
    except ReviewError as exc:
        raise GitStackError(
            "GitHub exact-target read-back failed.",
            code=exc.code,
            exit_code=exc.exit_code,
        ) from exc


def _guarded_result(
    action: dict[str, Any],
    before: dict[str, Any] | None,
) -> dict[str, Any]:
    try:
        after = verify_worktree_unchanged(before)
    except GitStackError as exc:
        raise ReviewError(
            str(exc), code=exc.code, exit_code=exc.exit_code,
            details={"action": action},
        ) from exc
    if after is not None:
        action["worktree"] = after
    return action


def post_conversation_comment(
    repo: str,
    pr: int,
    body: ProviderText,
    dry_run: bool,
    expected_worktree_fingerprint: str | None,
) -> dict[str, Any]:
    _verify_pr_target(repo, pr)
    try:
        before = require_worktree(expected_worktree_fingerprint)
    except GitStackError as exc:
        raise _review_error(exc) from exc
    target = {"repo": repo, "pr": pr, "kind": "conversation-comment"}
    if dry_run:
        return {
            "status": "dry-run", "target": target, "text": body.proof(),
            "transport": {"method": "POST", "endpoint": f"repos/{repo}/issues/{pr}/comments", "api_version": API_VERSION},
        }
    actor = _viewer_login()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    result = api_request("POST", f"repos/{repo}/issues/{pr}/comments", {"body": body.text})
    finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    def prove(item: dict[str, Any]) -> dict[str, Any]:
        if (
            not str(item.get("issue_url") or "").endswith(f"/repos/{repo}/issues/{pr}")
            or _item_login(item) != actor
            or not _in_creation_window(item, "created_at", started_at, finished_at)
        ):
            raise _proof_failure("Comment response did not match the intended creation.", "provider_target_mismatch")
        _proof(item, body, target=target, status="posted")
        return item

    def read_back() -> dict[str, Any]:
        matches = [
            item for item in _read_back_list(f"repos/{repo}/issues/{pr}/comments")
            if _item_login(item) == actor
            and response_text_matches(item, body)
            and _in_creation_window(item, "created_at", started_at, finished_at)
            and str(item.get("issue_url") or "").endswith(f"/repos/{repo}/issues/{pr}")
        ]
        if len(matches) != 1:
            raise _proof_failure("Comment read-back did not uniquely prove the creation.", "provider_read_back_not_unique")
        return prove(matches[0])

    try:
        proof = prove_mutation(
            result, prove_response=prove, read_back=read_back, target=target,
            text=body.proof(), ambiguous_message="Comment creation is unconfirmed after one exact-target read-back; do not retry blindly.",
        )
        status = "recovered" if proof.recovered else "posted"
        return _guarded_result(_proof(proof.value, body, target=target, status=status), before)
    except GitStackError as exc:
        raise _review_error(exc) from exc


def _verify_pr_head(repo: str, pr: int, expected_head: str) -> dict[str, Any]:
    pull = _verify_pr_target(repo, pr)
    actual = str(((pull.get("head") or {}).get("sha")) or "")
    try:
        actual = validate_full_head(actual)
    except ValueError as exc:
        raise ReviewError("GitHub pull-request read-back omitted a full head SHA.", code="provider_target_mismatch", exit_code=65) from exc
    if actual != expected_head:
        raise ReviewError(
            "The pull-request head changed before the typed review request could be posted.",
            code="head_drift",
            exit_code=3,
            details={"expected_head": expected_head, "current_head": actual},
        )
    return pull


def _request_target_comment(item: dict[str, Any], repo: str, pr: int) -> bool:
    return str(item.get("issue_url") or "").endswith(f"/repos/{repo}/issues/{pr}")


def request_automated_review(
    repo: str,
    pr: int,
    provider: str,
    head: str,
    request_key: str,
    dry_run: bool,
    expected_worktree_fingerprint: str | None,
) -> dict[str, Any]:
    is_provider_author(provider, "")
    try:
        plan = build_request(provider, repo, pr, head, request_key)
    except ValueError as exc:
        raise ReviewError(str(exc), code="invalid_request", exit_code=64) from exc
    _verify_pr_head(repo, pr, plan.head_sha)
    conversation = gh_api_paginated_list(f"repos/{repo}/issues/{pr}/comments")
    conflict, exact = _request_conflicts(conversation, plan)
    if conflict == "unbound":
        raise ReviewError(
            "An existing unbound Codex review trigger prevents a typed request from being posted.",
            code="request_unbound",
            exit_code=4,
            details={"request_binding": "unbound", "head": plan.head_sha},
        )
    if conflict == "invalid":
        raise ReviewError(
            "An existing conflicting or malformed typed Codex request prevents a new request.",
            code="invalid_request",
            exit_code=4,
            details={"request_binding": "invalid", "head": plan.head_sha},
        )
    if conflict == "ambiguous" or len(exact) > 1:
        raise ReviewError(
            "Multiple exact-key Codex requests exist for this PR head; refusing to choose one.",
            code="ambiguous_request",
            exit_code=4,
            details={"request_binding": "ambiguous", "head": plan.head_sha},
        )
    if exact:
        existing = exact[0]
        try:
            saved_receipt = receipt(plan, existing, status="reused")
        except (KeyError, TypeError, ValueError) as exc:
            raise ReviewError(
                "The existing typed Codex request cannot prove complete provider identity.",
                code="request_unknown",
                exit_code=4,
                details={"request_binding": "unknown"},
            ) from exc
        return {
            "status": "reused",
            "request": saved_receipt,
            "target": {"repo": repo, "pr": pr, "kind": "codex-review-request"},
            "text": {"field": "body", "encoding": "utf-8", "bytes": len(plan.body.encode("utf-8")), "sha256": plan.body_fingerprint},
            "transport": {"method": "POST", "endpoint": f"repos/{repo}/issues/{pr}/comments", "api_version": API_VERSION, "posted": False},
        }
    try:
        before = require_worktree(expected_worktree_fingerprint)
    except GitStackError as exc:
        raise _review_error(exc) from exc
    target = {"repo": repo, "pr": pr, "kind": "codex-review-request"}
    body = ProviderText("body", plan.body.encode("utf-8"), plan.body)
    if dry_run:
        return {
            "status": "dry-run",
            "request": {
                "schema": plan.schema,
                "provider": plan.provider,
                "repository": plan.repository,
                "pr_number": plan.pr_number,
                "head_sha": plan.head_sha,
                "request_key": plan.request_key,
                "request_fingerprint": plan.request_fingerprint,
                "body_fingerprint": plan.body_fingerprint,
            },
            "target": target,
            "text": body.proof(),
            "transport": {"method": "POST", "endpoint": f"repos/{repo}/issues/{pr}/comments", "api_version": API_VERSION, "posted": False},
        }
    actor = _viewer_login()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    result = api_request("POST", f"repos/{repo}/issues/{pr}/comments", {"body": plan.body})
    finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    def prove(item: dict[str, Any]) -> dict[str, Any]:
        if (
            not _request_target_comment(item, repo, pr)
            or _item_login(item) != actor
            or not _in_creation_window(item, "created_at", started_at, finished_at)
            or not _comment_for_plan(item, plan)
        ):
            raise _proof_failure("Typed request response did not match the intended creation.", "provider_target_mismatch")
        _proof(item, body, target=target, status="posted")
        return item

    def read_back() -> dict[str, Any]:
        matches = [
            item for item in _read_back_list(f"repos/{repo}/issues/{pr}/comments")
            if _item_login(item) == actor
            and _request_target_comment(item, repo, pr)
            and _in_creation_window(item, "created_at", started_at, finished_at)
            and _comment_for_plan(item, plan)
        ]
        if len(matches) != 1:
            raise _proof_failure("Typed request read-back did not uniquely prove the creation.", "provider_read_back_not_unique")
        return prove(matches[0])

    try:
        proof = prove_mutation(
            result,
            prove_response=prove,
            read_back=read_back,
            target=target,
            text=body.proof(),
            ambiguous_message="Typed review request creation is unconfirmed after one exact-target read-back; do not retry blindly.",
        )
        status = "recovered" if proof.recovered else "posted"
        action = {
            "status": status,
            "request": receipt(plan, proof.value, status=status),
            "target": target,
            "text": body.proof(),
            "transport": {"method": "POST", "endpoint": f"repos/{repo}/issues/{pr}/comments", "api_version": API_VERSION, "posted": True, "recovered": proof.recovered},
        }
        return _guarded_result(action, before)
    except GitStackError as exc:
        if exc.code == "provider_write_ambiguous":
            raise ReviewError(
                "The typed review request identity is unknown after one read-only recovery; do not retry or start the waiter.",
                code="request_unknown",
                exit_code=4,
                details=exc.details,
            ) from exc
        raise _review_error(exc) from exc


def reply_to_review_comment(
    repo: str,
    pr: int,
    comment_id: int,
    body: ProviderText,
    dry_run: bool,
    expected_worktree_fingerprint: str | None,
) -> dict[str, Any]:
    parent = _api_object(f"repos/{repo}/pulls/comments/{comment_id}")
    if not str(parent.get("pull_request_url") or "").endswith(f"/repos/{repo}/pulls/{pr}"):
        raise ReviewError("Review comment does not belong to the requested PR.", code="provider_target_mismatch", exit_code=65)
    try:
        before = require_worktree(expected_worktree_fingerprint)
    except GitStackError as exc:
        raise _review_error(exc) from exc
    target = {"repo": repo, "pr": pr, "kind": "review-reply", "parent_id": comment_id}
    endpoint = f"repos/{repo}/pulls/{pr}/comments/{comment_id}/replies"
    if dry_run:
        return {"status": "dry-run", "target": target, "text": body.proof(), "transport": {"method": "POST", "endpoint": endpoint, "api_version": API_VERSION}}
    actor = _viewer_login()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    result = api_request("POST", endpoint, {"body": body.text})
    finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    def prove(item: dict[str, Any]) -> dict[str, Any]:
        if (
            item.get("in_reply_to_id") != comment_id
            or not str(item.get("pull_request_url") or "").endswith(f"/repos/{repo}/pulls/{pr}")
            or _item_login(item) != actor
            or not _in_creation_window(item, "created_at", started_at, finished_at)
        ):
            raise _proof_failure("Review reply did not match the intended creation.", "provider_target_mismatch")
        _proof(item, body, target=target, status="replied")
        return item

    def read_back() -> dict[str, Any]:
        matches = [
            item for item in _read_back_list(f"repos/{repo}/pulls/{pr}/comments")
            if item.get("in_reply_to_id") == comment_id
            and _item_login(item) == actor
            and response_text_matches(item, body)
            and _in_creation_window(item, "created_at", started_at, finished_at)
            and str(item.get("pull_request_url") or "").endswith(f"/repos/{repo}/pulls/{pr}")
        ]
        if len(matches) != 1:
            raise _proof_failure("Review reply read-back did not uniquely prove the creation.", "provider_read_back_not_unique")
        return prove(matches[0])

    try:
        proof = prove_mutation(
            result, prove_response=prove, read_back=read_back, target=target,
            text=body.proof(), ambiguous_message="Review reply is unconfirmed after one exact-thread read-back; do not retry blindly.",
        )
        status = "recovered" if proof.recovered else "replied"
        return _guarded_result(_proof(proof.value, body, target=target, status=status), before)
    except GitStackError as exc:
        raise _review_error(exc) from exc


def edit_comment(
    repo: str,
    pr: int,
    comment_id: int,
    kind: str,
    body: ProviderText,
    dry_run: bool,
    expected_worktree_fingerprint: str | None,
) -> dict[str, Any]:
    namespace = "issues/comments" if kind == "conversation" else "pulls/comments"
    endpoint = f"repos/{repo}/{namespace}/{comment_id}"
    current = _api_object(endpoint)
    target_url = current.get("issue_url") if kind == "conversation" else current.get("pull_request_url")
    target_noun = "issues" if kind == "conversation" else "pulls"
    if not str(target_url or "").endswith(f"/repos/{repo}/{target_noun}/{pr}"):
        raise ReviewError("Comment does not belong to the requested PR.", code="provider_target_mismatch", exit_code=65)
    target = {"repo": repo, "pr": pr, "kind": f"{kind}-comment", "comment_id": comment_id}
    try:
        before = require_worktree(expected_worktree_fingerprint)
    except GitStackError as exc:
        raise _review_error(exc) from exc
    if response_text_matches(current, body):
        try:
            return _guarded_result(_proof(current, body, target=target, status="reused"), before)
        except GitStackError as exc:
            raise _review_error(exc) from exc
    if dry_run:
        return {"status": "dry-run", "target": target, "text": body.proof(), "transport": {"method": "PATCH", "endpoint": endpoint, "api_version": API_VERSION}}
    actor = _viewer_login()
    if _item_login(current) != actor:
        raise ReviewError("Authenticated identity does not own the requested comment.", code="provider_identity_mismatch", exit_code=65)
    result = api_request("PATCH", endpoint, {"body": body.text})

    def prove(item: dict[str, Any]) -> dict[str, Any]:
        item_target_url = item.get("issue_url") if kind == "conversation" else item.get("pull_request_url")
        if (
            item.get("id") != comment_id
            or not str(item_target_url or "").endswith(f"/repos/{repo}/{target_noun}/{pr}")
            or _item_login(item) != actor
        ):
            raise _proof_failure("Comment edit did not match the intended object.", "provider_target_mismatch")
        _proof(item, body, target=target, status="edited")
        return item

    def read_back() -> dict[str, Any]:
        try:
            item = _api_object(endpoint)
        except ReviewError as exc:
            raise _proof_failure("Comment edit read-back failed.", exc.code) from exc
        return prove(item)

    try:
        proof = prove_mutation(
            result, prove_response=prove, read_back=read_back, target=target,
            text=body.proof(), ambiguous_message="Comment edit is unconfirmed after one exact-object read-back; do not retry blindly.",
        )
        status = "recovered" if proof.recovered else "edited"
        return _guarded_result(_proof(proof.value, body, target=target, status=status), before)
    except GitStackError as exc:
        raise _review_error(exc) from exc


def submit_review(
    repo: str,
    pr: int,
    event: str,
    body: ProviderText,
    dry_run: bool,
    expected_worktree_fingerprint: str | None,
) -> dict[str, Any]:
    pr_payload = _verify_pr_target(repo, pr)
    try:
        before = require_worktree(expected_worktree_fingerprint)
    except GitStackError as exc:
        raise _review_error(exc) from exc
    provider_event = {"approve": "APPROVE", "request-changes": "REQUEST_CHANGES", "comment": "COMMENT"}[event]
    expected_state = {"approve": "APPROVED", "request-changes": "CHANGES_REQUESTED", "comment": "COMMENTED"}[event]
    target = {"repo": repo, "pr": pr, "kind": "review", "head": str((pr_payload.get("head") or {}).get("sha") or ""), "event": event}
    endpoint = f"repos/{repo}/pulls/{pr}/reviews"
    if dry_run:
        return {"status": "dry-run", "target": target, "text": body.proof(), "transport": {"method": "POST", "endpoint": endpoint, "api_version": API_VERSION}}
    actor = _viewer_login()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    result = api_request("POST", endpoint, {"body": body.text, "event": provider_event})
    finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    def prove(item: dict[str, Any]) -> dict[str, Any]:
        if (
            _item_login(item) != actor
            or item.get("state") != expected_state
            or not str(item.get("pull_request_url") or "").endswith(f"/repos/{repo}/pulls/{pr}")
            or str(item.get("commit_id") or "") != target["head"]
            or not _in_creation_window(item, "submitted_at", started_at, finished_at)
        ):
            raise _proof_failure("Review did not match the intended target and event.", "provider_target_mismatch")
        _proof(item, body, target=target, status="submitted")
        return item

    def read_back() -> dict[str, Any]:
        matches = [
            item for item in _read_back_list(endpoint)
            if _item_login(item) == actor
            and item.get("state") == expected_state
            and response_text_matches(item, body)
            and str(item.get("commit_id") or "") == target["head"]
            and _in_creation_window(item, "submitted_at", started_at, finished_at)
            and str(item.get("pull_request_url") or "").endswith(f"/repos/{repo}/pulls/{pr}")
        ]
        if len(matches) != 1:
            raise _proof_failure("Review read-back did not uniquely prove the submission.", "provider_read_back_not_unique")
        return prove(matches[0])

    try:
        proof = prove_mutation(
            result, prove_response=prove, read_back=read_back, target=target,
            text=body.proof(), ambiguous_message="Review submission is unconfirmed after one exact-target read-back; do not retry blindly.",
        )
        status = "recovered" if proof.recovered else "submitted"
        return _guarded_result(_proof(proof.value, body, target=target, status=status), before)
    except GitStackError as exc:
        raise _review_error(exc) from exc


def render_text(payload: dict[str, Any]) -> str:
    if "review_state" in payload:
        lines = [
            f"{payload['provider']} review for {payload['repo']}#{payload['pr']}: {payload['review_state']}",
            f"head={payload['head']} current={payload['current_head']}",
        ]
        if payload.get("timed_out"):
            lines.append("wait timed out")
        return "\n".join(lines) + "\n"
    lines: list[str] = []
    for entry in payload["entries"]:
        lines.append(f"[{entry['index']:>3}] {entry['type']} id={entry['comment_id']} author={entry['author'] or 'unknown'} updated={entry['updated']}")
        lines.append(f"      {entry['body_preview'] or '(empty)'}")
        if entry["path"]:
            lines.append(f"      file={entry['path']} line={entry['line']} startLine={entry['start_line']} resolved={entry['is_resolved']} outdated={entry['is_outdated']}")
    if not lines:
        lines.append("No comment context found.")
    if payload.get("actions"):
        lines.extend(["", "Reply actions:"])
        for action in payload["actions"]:
            lines.append(f"- comment {action['comment_id']}: {action['status']}")
    if payload.get("action"):
        action = payload["action"]
        lines.append(f"{action['status']}: review action for {payload['repo']}#{payload['pr']}")
        if action.get("url"):
            lines.append(str(action["url"]))
        request = action.get("request") or {}
        if request.get("request_ref"):
            lines.append(str(request["request_ref"]))
    return "\n".join(lines) + "\n"


def doctor_payload() -> dict[str, object]:
    git_path = which("git")
    gh_path = which("gh")
    auth = run(["gh", "auth", "status"]) if gh_path else RunResult(127, "", "gh missing")
    return {
        "ok": bool(git_path and gh_path),
        "version": VERSION,
        "checks": {
            "git": {"ok": bool(git_path), "path": git_path},
            "gh": {"ok": bool(gh_path), "path": gh_path, "authenticated": auth.returncode == 0 if gh_path else False},
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = StrictParser(
        prog="gitstack reviews",
        description="Inspect, check, wait for, or respond to pull-request reviews.",
    )
    parser.add_argument("--json", action="store_true", help="Emit a stable JSON envelope.")
    parser.add_argument("--version", action="store_true", help="Print version and exit.")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("doctor", help="Check local git and gh readiness.")
    address = subparsers.add_parser("address", help="List review context read-only.")
    address.add_argument("--pr", required=True, help="Pull request number.")
    address.add_argument("--repo", help="Repository in owner/repo format. Defaults to current checkout.")
    address.add_argument("--include-resolved", action="store_true", help="Include resolved or outdated review threads.")
    address.add_argument("--allow-non-project", action="store_true", help="Allow --repo usage outside a git checkout.")
    comment = subparsers.add_parser("comment", help="Post a top-level PR discussion comment.")
    comment.add_argument("--pr", required=True, help="Pull request number.")
    comment.add_argument("--repo", help="Repository in owner/repo format. Defaults to current checkout.")
    comment.add_argument("--body-file", required=True, help="Absolute UTF-8 regular-file path containing the comment body.")
    comment.add_argument("--dry-run", action="store_true", help="Preview the comment action without posting.")
    comment.add_argument("--expected-worktree-fingerprint")
    comment.add_argument("--allow-non-project", action="store_true", help="Allow --repo usage outside a git checkout.")
    request = subparsers.add_parser("request", help="Post or recover one typed, exact-head automated review request.")
    request.add_argument("--provider", required=True, help="Automated review provider. Currently: codex.")
    request.add_argument("--pr", required=True, help="Pull request number.")
    request.add_argument("--repo", help="Repository in owner/repo format. Defaults to current checkout.")
    request.add_argument("--head", required=True, help="Full 40-character expected reviewed head SHA.")
    request.add_argument("--request-key", required=True, help="Stable caller-owned request lineage key.")
    request.add_argument("--dry-run", action="store_true", help="Preview the canonical request without posting.")
    request.add_argument("--expected-worktree-fingerprint")
    request.add_argument("--allow-non-project", action="store_true", help="Allow --repo usage outside a git checkout.")
    reply = subparsers.add_parser("reply", help="Reply to one pull-request review comment.")
    reply.add_argument("--pr", required=True)
    reply.add_argument("--repo")
    reply.add_argument("--comment-id", required=True)
    reply.add_argument("--body-file", required=True)
    reply.add_argument("--dry-run", action="store_true")
    reply.add_argument("--expected-worktree-fingerprint")
    reply.add_argument("--allow-non-project", action="store_true")
    edit = subparsers.add_parser("edit-comment", help="Edit one conversation or review comment.")
    edit.add_argument("--pr", required=True)
    edit.add_argument("--repo")
    edit.add_argument("--comment-id", required=True)
    edit.add_argument("--kind", required=True, choices=("conversation", "review"))
    edit.add_argument("--body-file", required=True)
    edit.add_argument("--dry-run", action="store_true")
    edit.add_argument("--expected-worktree-fingerprint")
    edit.add_argument("--allow-non-project", action="store_true")
    submit = subparsers.add_parser("submit-review", help="Submit one PR review with a file-backed body.")
    submit.add_argument("--pr", required=True)
    submit.add_argument("--repo")
    submit.add_argument("--event", required=True, choices=("approve", "request-changes", "comment"))
    submit.add_argument("--body-file", required=True)
    submit.add_argument("--dry-run", action="store_true")
    submit.add_argument("--expected-worktree-fingerprint")
    submit.add_argument("--allow-non-project", action="store_true")
    for command, help_text in (
        ("check", "Inspect automated review state once and exit."),
        ("wait", "Wait for an automated review to complete or time out."),
    ):
        review = subparsers.add_parser(command, help=help_text)
        review.add_argument("--provider", required=True, help="Automated review provider. Currently: codex.")
        review.add_argument("--pr", required=True, help="Pull request number.")
        review.add_argument("--repo", help="Repository in owner/repo format. Defaults to current checkout.")
        review.add_argument("--head", help="Expected reviewed head SHA. Defaults to the current PR head.")
        review.add_argument("--request-receipt-file", help="Absolute UTF-8 JSON file containing the complete typed request receipt.")
        review.add_argument("--allow-non-project", action="store_true", help="Allow --repo usage outside a git checkout.")
        if command == "wait":
            review.add_argument("--timeout", default="15m", help="Maximum wait, for example 30s, 15m, or 1h.")
            review.add_argument("--interval", default="10s", help="Initial polling interval. Default: 10s.")
            review.add_argument("--max-interval", default="30s", help="Maximum polling interval. Default: 30s.")
    return parser


def emit_success(data: object, command: list[str]) -> None:
    print(json.dumps({"ok": True, "version": VERSION, "command": command, "data": data}, indent=2))


def emit_error(exc: ReviewError, command: list[str]) -> None:
    error: dict[str, Any] = {"code": exc.code, "message": exc.message}
    if exc.details is not None:
        error["details"] = exc.details
    print(json.dumps({"ok": False, "version": VERSION, "command": command, "error": error}, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except ReviewError as exc:
        raw = list(argv or [])
        if "--json" in raw:
            emit_error(exc, [next((item for item in raw if item in {"address", "comment", "request", "reply", "edit-comment", "submit-review", "check", "wait"}), "")])
        else:
            print(exc.message, file=sys.stderr)
        return exc.exit_code
    if args.version:
        print(VERSION)
        return 0
    if args.command == "doctor":
        payload = doctor_payload()
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"gitstack reviews {VERSION}")
            print(f"git: {'ok' if payload['checks']['git']['ok'] else 'missing'}")
            print(f"gh: {'ok' if payload['checks']['gh']['ok'] else 'missing'}")
        return 0 if payload["ok"] else 1
    if args.command not in {"address", "comment", "request", "reply", "edit-comment", "submit-review", "check", "wait"}:
        parser.print_help()
        return 0
    try:
        pr = positive_int(args.pr, "pr")
        repo = resolve_repo(args.repo, allow_non_project=args.allow_non_project)
        if args.command in {"check", "wait"}:
            request_identity = None
            if args.request_receipt_file:
                try:
                    receipt_text = read_text_file(args.request_receipt_file, field="request-receipt").text
                    request_identity = json.loads(receipt_text)
                except (GitStackError, json.JSONDecodeError, TypeError) as exc:
                    if isinstance(exc, GitStackError):
                        raise _review_error(exc) from exc
                    raise ReviewError("The request receipt file must contain one JSON object.", code="invalid_request", exit_code=64) from exc
                if not isinstance(request_identity, dict):
                    raise ReviewError("The request receipt file must contain one JSON object.", code="invalid_request", exit_code=64)
            if args.command == "wait" and request_identity is None:
                raise ReviewError(
                    "The identity-bound automated review waiter requires --request-receipt-file.",
                    code="request_binding_required",
                    exit_code=64,
                )
            if args.command == "check":
                payload = check_automated_review(repo, pr, args.provider, args.head, request_identity)
                binding = str(payload.get("request_binding") or "unknown")
                if payload.get("review_state") == "stale":
                    exit_code = REVIEW_EXIT_CODES["stale"]
                elif binding != "recognized":
                    status = payload.get("review_state")
                    exit_code = REVIEW_EXIT_CODES[str(status)] if binding == "absent" and status == "not-requested" else REQUEST_BINDING_EXIT_CODES.get(binding, 4)
                else:
                    exit_code = REVIEW_EXIT_CODES[str(payload["review_state"])]
            else:
                timeout = duration_seconds(args.timeout, "timeout")
                interval = duration_seconds(args.interval, "interval")
                max_interval = duration_seconds(args.max_interval, "max-interval")
                if interval > max_interval:
                    raise ReviewError(
                        "--interval cannot be greater than --max-interval.",
                        code="invalid_arguments",
                        exit_code=64,
                    )
                payload, exit_code = wait_for_automated_review(
                    repo, pr, args.provider, args.head, timeout, interval, max_interval, request_identity
                )
            if args.json:
                emit_success(payload, [args.command])
            else:
                print(render_text(payload), end="")
            return exit_code
        if args.command == "request":
            action = request_automated_review(
                repo,
                pr,
                args.provider,
                args.head,
                args.request_key,
                args.dry_run,
                args.expected_worktree_fingerprint,
            )
            payload = {"repo": repo, "pr": pr, "action": action}
            if args.json:
                emit_success(payload, ["request"])
            else:
                print(render_text(payload), end="")
            return 0
        if args.command == "comment":
            try:
                body = read_text_file(args.body_file, field="body")
            except GitStackError as exc:
                raise _review_error(exc) from exc
            payload = {"repo": repo, "pr": pr, "action": post_conversation_comment(repo, pr, body, args.dry_run, args.expected_worktree_fingerprint)}
            if args.json:
                emit_success(payload, ["comment"])
            else:
                print(render_text(payload), end="")
            return 0
        if args.command in {"reply", "edit-comment", "submit-review"}:
            try:
                body = read_text_file(args.body_file, field="body")
            except GitStackError as exc:
                raise _review_error(exc) from exc
            if args.command == "reply":
                comment_id = positive_int(args.comment_id, "comment-id")
                action = reply_to_review_comment(repo, pr, comment_id, body, args.dry_run, args.expected_worktree_fingerprint)
            elif args.command == "edit-comment":
                comment_id = positive_int(args.comment_id, "comment-id")
                action = edit_comment(repo, pr, comment_id, args.kind, body, args.dry_run, args.expected_worktree_fingerprint)
            else:
                action = submit_review(repo, pr, args.event, body, args.dry_run, args.expected_worktree_fingerprint)
            payload = {"repo": repo, "pr": pr, "action": action}
            if args.json:
                emit_success(payload, [args.command])
            else:
                print(json.dumps(payload, indent=2))
            return 0
        entries = collect_entries(repo, pr, args.include_resolved)
        payload: dict[str, Any] = {"repo": repo, "pr": pr, "entries": entries}
        if args.json:
            emit_success(payload, ["address"])
        else:
            print(render_text(payload), end="")
        return 0
    except ReviewError as exc:
        if args.command in {"check", "wait"} and exc.code == "command_failed":
            exc = ReviewError(exc.message, code="api_error", exit_code=4)
        if args.json:
            emit_error(exc, [args.command or ""])
        else:
            print(exc.message, file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
