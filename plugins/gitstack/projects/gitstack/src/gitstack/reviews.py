from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
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
    graphql_request,
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
from .review_thread import (
    build_reply_receipt,
    build_resolution_receipt,
    validate_reply_receipt,
)
from .review_mutation import (
    MUTATION_KINDS,
    RESERVATION_FIELDS,
    ReservationError,
    add_operation_marker,
    build_reservation,
    marker_operation_id,
    operation_marker,
    operation_id_for_mutation,
    operation_id_for_request,
    packet_fingerprint,
    thread_identity_fingerprint,
    text_fingerprint,
    validate_reservation_packet,
)
from .terminal_evidence import (
    build_terminal_evidence_receipt,
    validate_terminal_evidence_receipt,
)
from .review_operation import (
    OperationError,
    build_request as build_operation_request,
    build_result as build_operation_result,
    validation_descriptor as operation_validation_descriptor,
    validate_request as validate_operation_request,
    validate_result as validate_operation_result,
    validate_result_for_request,
    validate_start_receipt,
    validate_start_receipt_identity,
    validate_target as validate_operation_target,
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


def _reservation_cache_root() -> Path:
    return _trusted_user_home() / ".cache/dotagents/plugins/gitstack/review-mutations"


def _operation_journal_root() -> Path:
    return _trusted_user_home() / ".cache/dotagents/plugins/gitstack/review-operations"


def _trusted_user_home() -> Path:
    """Return the account home without trusting a caller-provided HOME."""

    try:
        import pwd

        return Path(pwd.getpwuid(os.getuid()).pw_dir)
    except (ImportError, KeyError, OSError, AttributeError):
        # Windows has no pwd database; Path.home() is the platform fallback.
        return Path.home()


def _read_reservation_file(path_value: str | None) -> dict[str, Any]:
    if not isinstance(path_value, str) or not path_value:
        raise ReviewError(
            "A root-issued reservation file is required before this review mutation.",
            code="reservation_required",
            exit_code=4,
        )
    path = Path(path_value)
    if not path.is_absolute():
        raise ReviewError(
            "The reservation file must be an absolute regular non-symlinked file.",
            code="reservation_invalid",
            exit_code=4,
        )
    try:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise OSError("reservation file is not regular")
            value = json.loads(os.read(fd, 1_048_577).decode("utf-8"))
        finally:
            os.close(fd)
        return validate_reservation_packet(value)
    except (OSError, UnicodeError, json.JSONDecodeError, ReservationError) as exc:
        raise ReviewError(
            "The reservation file is not a valid immutable provider-mutation packet.",
            code="reservation_invalid",
            exit_code=4,
        ) from exc


def _require_reservation(
    path_value: str | None,
    *,
    kind: str,
    repo: str,
    pr: int,
    head: str | None = None,
    request_key: str | None = None,
    request_fingerprint: str | None = None,
    thread_id: str | None = None,
    thread_fingerprint: str | None = None,
    finding_comment_id: int | None = None,
    body_fingerprint: str | None = None,
    reply_receipt_fingerprint: str | None = None,
    allow_thread_fingerprint_mismatch: bool = False,
    owned_operation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if kind not in MUTATION_KINDS:
        raise ReviewError("The requested mutation kind is not supported.", code="reservation_invalid", exit_code=4)
    required = {
        "head": head,
        "request_key": request_key,
        "request_fingerprint": request_fingerprint,
    }
    if kind in {"review-reply", "review-resolution"}:
        required.update(
            {
                "thread_id": thread_id,
                "thread_fingerprint": thread_fingerprint,
                "finding_comment_id": finding_comment_id,
            }
        )
    missing = [name for name, value in required.items() if value is None]
    if missing:
        raise ReviewError(
            f"The reservation is missing exact mutation identity: {', '.join(missing)}.",
            code="reservation_required",
            exit_code=4,
        )
    if owned_operation is None:
        packet = _read_reservation_file(path_value)
    else:
        authority = owned_operation["authority"]
        if kind == "review-request":
            operation_id = operation_id_for_request(repo, pr, str(head), str(request_key), str(request_fingerprint))
        else:
            operation_id = operation_id_for_mutation(
                kind, repo, pr, str(head), request_fingerprint=request_fingerprint,
                thread_id=thread_id, finding_comment_id=finding_comment_id,
                reply_receipt_fingerprint=reply_receipt_fingerprint,
            )
        packet = build_reservation(
            mutation_kind=kind, repository=repo, pr_number=pr, head_sha=str(head),
            task_key=authority["task_key"], delivery_key=authority["delivery_key"],
            operation_id=operation_id, request_key=request_key,
            request_fingerprint=request_fingerprint, thread_id=thread_id,
            thread_fingerprint=thread_fingerprint,
            finding_comment_id=finding_comment_id, body_fingerprint=body_fingerprint,
            reply_receipt_fingerprint=reply_receipt_fingerprint,
            expected_generation=authority["expected_generation"],
            expected_state_fingerprint=authority["expected_state_fingerprint"],
            expected_claim_fingerprint=authority["expected_claim_fingerprint"],
            expected_task_state=authority["task_state"],
        )
    if packet["mutation_kind"] != kind or packet["repository"] != repo or packet["pr_number"] != pr:
        raise ReviewError(
            "The reservation does not match the exact review mutation target.",
            code="reservation_target_mismatch",
            exit_code=4,
        )
    if head is not None and packet["head_sha"] != validate_full_head(head):
        raise ReviewError(
            "The reservation does not match the exact pull-request head.",
            code="reservation_target_mismatch",
            exit_code=4,
        )
    checks = {
        "request_key": request_key,
        "request_fingerprint": request_fingerprint,
        "thread_id": thread_id,
        "thread_fingerprint": thread_fingerprint,
        "finding_comment_id": finding_comment_id,
        "body_fingerprint": body_fingerprint,
        "reply_receipt_fingerprint": reply_receipt_fingerprint,
    }
    for field, expected in checks.items():
        if field == "thread_fingerprint" and allow_thread_fingerprint_mismatch:
            continue
        if expected is not None and packet[field] != expected:
            raise ReviewError(
                f"The reservation does not match the exact {field}.",
                code="reservation_target_mismatch",
                exit_code=4,
            )
    return packet


def _read_consumed_marker(
    packet: dict[str, Any], reservation_file: str, *, require_consumed: bool = False,
    marker_observer: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Read the one-use marker without creating or changing it."""

    root = _reservation_cache_root()
    if not root.exists():
        if require_consumed:
            raise ReviewError(
                "The started mutation has no consumed marker; recovery is missing.",
                code="reservation_not_consumed", exit_code=4,
            )
        return None
    if root.is_symlink() or not root.is_dir():
        raise ReviewError(
            "The one-use reservation marker store is unsafe; refusing recovery.",
            code="reservation_consumed_unknown",
            exit_code=4,
        )
    marker_path = root / f"{packet['operation_id']}.consumed.json"
    try:
        fd = os.open(marker_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except FileNotFoundError:
        if require_consumed:
            raise ReviewError(
                "The started mutation has no consumed marker; recovery is missing.",
                code="reservation_not_consumed", exit_code=4,
            )
        return None
    except OSError as exc:
        raise ReviewError(
            "The consumed reservation marker is unavailable; refusing retry or recovery.",
            code="reservation_consumed_unknown",
            exit_code=4,
        ) from exc
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise OSError("consumed reservation marker is not regular")
        value = json.loads(os.read(fd, 1_048_577).decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReviewError(
            "The consumed reservation marker is unreadable; refusing retry or recovery.",
            code="reservation_consumed_unknown",
            exit_code=4,
        ) from exc
    finally:
        os.close(fd)
    if isinstance(value, dict) and marker_observer is not None:
        marker_observer.update(value)
    if (
        not isinstance(value, dict)
        or value.get("schema") != packet["schema"]
        or value.get("operation_id") != packet["operation_id"]
        or value.get("reservation_id") != packet["reservation_id"]
        or value.get("packet_fingerprint") != packet_fingerprint(packet)
        or (
            not require_consumed
            and value.get("reservation_file") != str(Path(reservation_file).resolve())
        )
    ):
        raise ReviewError(
            "The operation identity is already consumed by a conflicting reservation.",
            code="reservation_conflict",
            exit_code=4,
        )
    return value


def _consumed_marker_fingerprint(marker: dict[str, Any]) -> str:
    encoded = json.dumps(marker, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _with_consumed_marker(action: dict[str, Any], marker: dict[str, Any]) -> dict[str, Any]:
    action["consumed_marker_fingerprint"] = _consumed_marker_fingerprint(marker)
    return action


def _recovery_required(
    message: str, *, code: str, details: dict[str, Any] | None = None,
) -> ReviewError:
    return ReviewError(
        message,
        code=code,
        exit_code=4,
        details={"recovery": "needs-owner", "automatic_retry": False, **(details or {})},
    )


def _consume_reservation(packet: dict[str, Any], reservation_file: str) -> None:
    """Atomically consume one packet before any provider mutation."""

    root = _reservation_cache_root()
    try:
        if root.exists() and (root.is_symlink() or not root.is_dir()):
            raise OSError("reservation marker root is unsafe")
        root.mkdir(parents=True, exist_ok=True)
        if root.is_symlink() or not root.is_dir():
            raise OSError("reservation marker root is unsafe")
    except OSError as exc:
        raise ReviewError(
            "The one-use reservation marker store is unsafe or unavailable.",
            code="reservation_consume_failed",
            exit_code=4,
        ) from exc
    marker_path = root / f"{packet['operation_id']}.consumed.json"
    marker = {
        "schema": packet["schema"],
        "reservation_id": packet["reservation_id"],
        "operation_id": packet["operation_id"],
        "packet_fingerprint": packet_fingerprint(packet),
        "reservation_file": str(Path(reservation_file).resolve()),
        "consumed_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    encoded = (json.dumps(marker, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    try:
        fd = os.open(
            marker_path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
    except FileExistsError as exc:
        _read_consumed_marker(packet, reservation_file)
        raise ReviewError(
            "This provider mutation reservation was already consumed; reconcile read-only and do not retry.",
            code="reservation_consumed",
            exit_code=4,
        ) from exc
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise ReviewError(
            "The one-use reservation could not be durably consumed; no provider retry is allowed.",
            code="reservation_consume_failed",
            exit_code=4,
        ) from exc
    try:
        directory_fd = os.open(
            root,
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except OSError as exc:
        raise ReviewError(
            "The one-use reservation directory could not be durably synced; no provider mutation is allowed.",
            code="reservation_consume_failed",
            exit_code=4,
        ) from exc


def _marked_body(body: ProviderText, packet: dict[str, Any]) -> ProviderText:
    try:
        text = add_operation_marker(body.text, packet["operation_id"])
    except ReservationError as exc:
        raise ReviewError("The provider body marker is invalid.", code="reservation_invalid", exit_code=4) from exc
    marked = ProviderText(body.field, text.encode("utf-8"), text)
    if packet["body_fingerprint"] != marked.sha256:
        raise ReviewError(
            "The reservation body fingerprint does not match the exact provider text.",
            code="reservation_body_mismatch",
            exit_code=4,
        )
    return marked


def _marker_matches(text: str, operation_id: str) -> bool:
    try:
        return marker_operation_id(text) == operation_id
    except ReservationError:
        return False


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
) -> tuple[str | None, str | None]:
    """Return the stable machine failure mapping consumed by typed ledgers."""

    if not head_is_current or status == "stale":
        return "head-drift", "head_drift"
    if status == "error":
        return "provider-terminal-error", "provider_terminal_error"
    if binding == "ambiguous":
        return "ambiguous-provider-evidence", "ambiguous_review_evidence"
    if binding == "invalid":
        if request_error_code == "request_correlation_failure":
            return "request-correlation-failure", request_error_code
        return "provider-config-failure", request_error_code or "request_receipt_invalid"
    if binding == "unknown":
        if request_error_code == "request_correlation_failure":
            return "request-correlation-failure", request_error_code
        return "provider-api-failure", request_error_code or "provider_api_failure"
    if binding == "unbound":
        return "request-correlation-failure", "request_unbound"
    return None, None


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


def _reconcile_consumed_request(
    repo: str, pr: int, plan: RequestPlan, packet: dict[str, Any],
) -> dict[str, Any]:
    """Recover one already-consumed request from an exact provider artifact."""

    try:
        actor = _viewer_login()
        conversation = _read_back_list(f"repos/{repo}/issues/{pr}/comments")
    except (ReviewError, GitStackError) as exc:
        raise _recovery_required(
            "The consumed review request could not be read back exactly; owner recovery is required.",
            code="request_unknown",
            details={"read_back_code": getattr(exc, "code", "provider_read_back_failed")},
        ) from exc
    matches = [
        item for item in conversation
        if _item_login(item) == actor
        and _request_target_comment(item, repo, pr)
        and _comment_for_plan(item, plan)
        and _marker_matches(str(item.get("body") or ""), packet["operation_id"])
    ]
    if len(matches) != 1:
        raise _recovery_required(
            "The consumed review request did not map to one unique provider artifact; owner recovery is required.",
            code="request_unknown",
            details={"matches": len(matches)},
        )
    try:
        saved_receipt = receipt(plan, matches[0], status="recovered")
    except (KeyError, TypeError, ValueError) as exc:
        raise _recovery_required(
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
    request_error_code: str | None = None
    if request_identity is not None and saved_plan is None:
        binding = "invalid"
        request_error_code = "request_receipt_invalid"
    elif saved_plan is not None:
        binding = "unknown"
        try:
            comment_id = int(request_identity["comment_id"])  # type: ignore[index]
            selected_request = _api_object(f"repos/{repo}/issues/comments/{comment_id}")
            if not _comment_for_plan(selected_request, saved_plan) or not receipt_matches(saved_plan, selected_request, request_identity):
                binding = "invalid"
                request_error = "The persisted request receipt does not match the exact provider comment."
                request_error_code = "request_correlation_failure"
            else:
                binding = "recognized"
                selected_receipt = request_identity
        except (ReviewError, KeyError, TypeError, ValueError) as exc:
            request_error = str(exc)
            request_error_code = (
                exc.code if isinstance(exc, ReviewError) else "provider_response_invalid"
            )
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
                    request_error_code = "ambiguous_review_evidence"
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
                request_error_code = (
                    "ambiguous_review_evidence"
                    if conflict == "ambiguous"
                    else "request_correlation_failure"
                )
            elif any(
                parse_request(item.get("body") or "", provider, repo, pr).classification == "unbound"
                for item in conversation
            ):
                binding = "unbound"
                request_error_code = "request_unbound"

    plan = selected_plan

    if plan is not None and selected_request is not None:
        conflict, exact = _request_conflicts(conversation, plan)
        if conflict == "ambiguous" or len(exact) > 1:
            binding = "ambiguous"
            request_error_code = "ambiguous_review_evidence"
        elif conflict == "invalid":
            binding = conflict
            request_error_code = "request_correlation_failure"

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
            request_error_code = exc.code or "provider_api_failure"

    current_request_reviews = [
        item for item in head_reviews
        if request_created_at and str(item.get("submitted_at") or "") > request_created_at
    ] if binding == "recognized" else []
    current_request_findings = [
        item for item in head_findings
        if request_created_at and str(item.get("created_at") or "") > request_created_at
        and item.get("in_reply_to_id") is None
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
            "actor": _item_login(mismatched),
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
            "actor": _item_login(latest_terminal_comment),
            "body_fingerprint": text_fingerprint(str(latest_terminal_comment.get("body") or "")),
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
            "actor": _item_login(latest_formal_review),
            "body_fingerprint": text_fingerprint(str(latest_formal_review.get("body") or "")),
            "created_at": latest_formal_review.get("submitted_at"),
            "outcome": status,
            "head": latest_formal_review.get("commit_id"),
        }
    elif "+1" in reactions:
        status = "clean"
        evidence = {
            "kind": "clean-reaction",
            "object_id": selected_request.get("id") if selected_request else None,
            "object_url": selected_request.get("html_url") if selected_request else None,
            "actor": _item_login(selected_request or {}),
            "body_fingerprint": text_fingerprint(str((selected_request or {}).get("body") or "")),
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
    finding_comment_ids = sorted(
        int(item["id"])
        for item in current_request_findings
        if isinstance(item.get("id"), int) and not isinstance(item.get("id"), bool)
    )
    if (
        len(finding_comment_ids) != len(current_request_findings)
        or len(finding_comment_ids) != len(set(finding_comment_ids))
    ):
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
            "latest_id": latest_formal_review.get("id") if latest_formal_review else None,
            "submitted_at": latest_formal_review.get("submitted_at") if latest_formal_review else None,
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
            "latest_id": latest_terminal_comment.get("comment_id") if latest_terminal_comment else None,
            "created_at": latest_terminal_comment.get("created_at") if latest_terminal_comment else None,
            "reviewed_head": latest_terminal_comment.get("reviewed_head") if latest_terminal_comment else None,
            "outcome": latest_terminal_comment.get("outcome") if latest_terminal_comment else None,
        },
        "evidence": evidence,
    }
    failure_kind, error_code = review_failure_classification(
        binding=binding,
        status=status,
        head_is_current=head_is_current,
        request_error_code=request_error_code,
    )
    payload["failure_kind"] = failure_kind
    payload["error_code"] = error_code
    payload["observation_fingerprint"] = stable_observation_fingerprint(payload)
    return payload


def terminal_provider_evidence(
    repo: str,
    pr: int,
    provider: str,
    expected_head: str,
    request_identity: dict[str, Any],
) -> dict[str, Any]:
    """Independently prove one exact-lineage provider terminal comment."""

    is_provider_author(provider, "")
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
        raise ReviewError(str(exc), code="terminal_evidence_request_mismatch", exit_code=64) from exc

    pull = gh_json(["api", f"repos/{repo}/pulls/{pr}", "-H", "Accept: application/vnd.github+json"])
    if not isinstance(pull, dict) or not isinstance((pull.get("head") or {}).get("sha"), str):
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
        request_comment = _api_object(f"repos/{repo}/issues/comments/{saved['comment_id']}")
    except ReviewError as exc:
        raise ReviewError(
            "The exact typed review request comment is unavailable.",
            code="terminal_evidence_request_mismatch",
            exit_code=4,
        ) from exc
    if not _comment_for_plan(request_comment, plan) or not receipt_matches(plan, request_comment, saved):
        raise ReviewError(
            "The exact typed review request comment no longer matches its receipt.",
            code="terminal_evidence_request_mismatch",
            exit_code=4,
        )

    reviews = gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/reviews")
    inline_comments = gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/comments")
    conversation = gh_api_paginated_list(f"repos/{repo}/issues/{pr}/comments")
    request_created_at = str(saved["created_at"])

    later_requests = [
        item
        for item in conversation
        if str(item.get("created_at") or "") > request_created_at
        and parse_request(item.get("body") or "", provider, repo, pr).classification != "absent"
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
        and (parsed := provider_terminal_comment_any(item, provider)) is not None
    ]
    if not terminal_comments:
        raise ReviewError(
            "No terminal provider artifact exists for the exact request lineage.",
            code="terminal_evidence_not_found",
            exit_code=2,
        )
    if any(not sha_matches(parsed["reviewed_head"], head) for _, parsed in terminal_comments):
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
        if authored_by(item, provider)
        and item.get("in_reply_to_id") is None
        and str(item.get("created_at") or "") > request_created_at
        and sha_matches(item.get("commit_id"), head)
    ]
    conflicting_reviews = []
    for item in reviews:
        if (
            not authored_by(item, provider)
            or not sha_matches(item.get("commit_id"), head)
            or str(item.get("submitted_at") or "") <= request_created_at
        ):
            continue
        body = str(item.get("body") or "")
        state = str(item.get("state") or "").upper()
        if state in {"CHANGES_REQUESTED", "DISMISSED"} or CODEX_FINDINGS_RESULT.search(body) or CODEX_ERROR_RESULT.search(body):
            conflicting_reviews.append(item)
    if conflicting_findings or conflicting_reviews:
        raise ReviewError(
            "Conflicting provider findings or terminal outcomes exist for the exact request lineage.",
            code="terminal_evidence_ambiguous",
            exit_code=4,
        )

    artifact, parsed = terminal_comments[0]
    artifact_id = artifact.get("id")
    if not isinstance(artifact_id, int) or isinstance(artifact_id, bool) or artifact_id < 1:
        raise ReviewError(
            "The terminal provider artifact lacks an exact identity.",
            code="terminal_evidence_invalid",
            exit_code=4,
        )
    exact_artifact = _api_object(f"repos/{repo}/issues/comments/{artifact_id}")
    exact_parsed = provider_terminal_comment_any(exact_artifact, provider)
    if (
        exact_parsed is None
        or exact_artifact.get("body") != artifact.get("body")
        or exact_artifact.get("html_url") != artifact.get("html_url")
        or exact_artifact.get("created_at") != artifact.get("created_at")
        or str(((exact_artifact.get("user") or {}).get("login")) or "")
        != str(((artifact.get("user") or {}).get("login")) or "")
        or exact_parsed["reviewed_head"] != parsed["reviewed_head"]
        or exact_parsed["outcome"] != parsed["outcome"]
    ):
        raise ReviewError(
            "The exact terminal provider artifact changed during verification.",
            code="terminal_evidence_invalid",
            exit_code=4,
        )

    final_pull = gh_json(
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
        final_head = validate_full_head(str((final_pull.get("head") or {}).get("sha") or ""))
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

    receipt_value = build_terminal_evidence_receipt(
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
        verified_at=datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
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


def _review_thread_context(thread_id: str) -> dict[str, Any]:
    query = """
query($id: ID!, $after: String) {
  node(id: $id) {
    ... on PullRequestReviewThread {
      id
      isResolved
      isOutdated
      viewerCanResolve
      path
      line
      startLine
      repository { nameWithOwner }
      pullRequest { number state headRefOid }
      comments(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
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
""".strip()
    comments: list[dict[str, Any]] = []
    context: dict[str, Any] | None = None
    after: str | None = None
    while True:
        payload = graphql(query, {"id": thread_id, "after": after})
        node = (payload.get("data") or {}).get("node") if isinstance(payload, dict) else None
        if not isinstance(node, dict) or node.get("id") != thread_id:
            raise ReviewError("Review thread was not found.", code="review_thread_not_found", exit_code=4)
        current = {
            "thread_id": str(node["id"]),
            "is_resolved": bool(node.get("isResolved")),
            "is_outdated": bool(node.get("isOutdated")),
            "viewer_can_resolve": bool(node.get("viewerCanResolve")),
            "path": str(node.get("path") or ""),
            "line": node.get("line"),
            "start_line": node.get("startLine"),
            "repository": str((node.get("repository") or {}).get("nameWithOwner") or ""),
            "pr_number": (node.get("pullRequest") or {}).get("number"),
            "pr_state": str((node.get("pullRequest") or {}).get("state") or "").lower(),
            "head_sha": str((node.get("pullRequest") or {}).get("headRefOid") or ""),
        }
        if context is not None and context != current:
            raise ReviewError("Review thread identity changed during pagination.", code="review_thread_mismatch", exit_code=4)
        context = current
        connection = node.get("comments") or {}
        comments.extend(item for item in connection.get("nodes") or [] if isinstance(item, dict))
        page_info = connection.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
        if not after:
            raise ReviewError("Review thread pagination omitted its cursor.", code="provider_response_invalid", exit_code=65)
    assert context is not None
    context["comments"] = comments
    return context


def _review_thread_ids(repo: str, pr: int) -> list[str]:
    owner, repo_name = repo.split("/", 1)
    query = """
query($owner: String!, $repo: String!, $number: Int!, $after: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes { id }
      }
    }
  }
}
""".strip()
    thread_ids: list[str] = []
    after: str | None = None
    while True:
        payload = graphql(query, {"owner": owner, "repo": repo_name, "number": pr, "after": after})
        pull = ((payload.get("data") or {}).get("repository") or {}).get("pullRequest") if isinstance(payload, dict) else None
        if not isinstance(pull, dict):
            raise ReviewError("Pull request review threads were not found.", code="provider_target_mismatch", exit_code=65)
        threads = pull.get("reviewThreads") or {}
        for thread in threads.get("nodes") or []:
            if isinstance(thread, dict) and isinstance(thread.get("id"), str):
                thread_ids.append(thread["id"])
        page_info = threads.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
        if not after:
            raise ReviewError("Review thread pagination omitted its cursor.", code="provider_response_invalid", exit_code=65)
    if len(thread_ids) != len(set(thread_ids)):
        raise ReviewError("Review thread pagination returned duplicate identities.", code="review_thread_mismatch", exit_code=4)
    return thread_ids


def _finding_thread(repo: str, pr: int, finding_comment_id: int, finding_node_id: str) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    for thread_id in _review_thread_ids(repo, pr):
        context = _review_thread_context(thread_id)
        if context["repository"] != repo or context["pr_number"] != pr:
            raise ReviewError("Review thread does not belong to the requested PR.", code="review_thread_mismatch", exit_code=4)
        if any(
            item.get("id") == finding_node_id and item.get("databaseId") == finding_comment_id
            for item in context["comments"]
        ):
            matches.append(context)
    if len(matches) != 1:
        raise ReviewError(
            "The exact review finding did not map to one unique thread.",
            code="review_thread_not_found" if not matches else "review_thread_mismatch",
            exit_code=4,
        )
    return matches[0]


def _exact_thread_fingerprint(thread: dict[str, Any], repo: str, pr: int, head: str) -> str:
    try:
        return thread_identity_fingerprint(
            repo,
            pr,
            head,
            str(thread["thread_id"]),
            [
                {"node_id": item.get("id"), "comment_id": item.get("databaseId")}
                for item in thread.get("comments", [])
            ],
        )
    except (KeyError, ReservationError) as exc:
        raise ReviewError(
            "The exact review thread omitted stable provider identity.",
            code="review_thread_mismatch",
            exit_code=4,
        ) from exc


def _reply_thread_identity(
    repo: str, pr: int, head: str, comment_id: int,
) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    """Read the exact top-level finding thread used by prepare and execute."""

    parent = _api_object(f"repos/{repo}/pulls/comments/{comment_id}")
    if not str(parent.get("pull_request_url") or "").endswith(f"/repos/{repo}/pulls/{pr}"):
        raise ReviewError("Review comment does not belong to the requested PR.", code="provider_target_mismatch", exit_code=65)
    if parent.get("id") != comment_id or not isinstance(parent.get("node_id"), str):
        raise ReviewError("Review finding omitted its exact provider identity.", code="provider_identity_missing", exit_code=65)
    if parent.get("in_reply_to_id") is not None:
        raise ReviewError(
            "Review replies must target the exact top-level finding.",
            code="review_reply_parent_invalid", exit_code=4,
        )
    try:
        finding_head = validate_full_head(str(parent.get("commit_id") or ""))
    except ValueError as exc:
        raise ReviewError("Review finding omitted its full commit identity.", code="provider_identity_missing", exit_code=65) from exc
    thread = _finding_thread(repo, pr, comment_id, parent["node_id"])
    return parent, thread, _exact_thread_fingerprint(thread, repo, pr, head), finding_head


def review_threads(repo: str, pr: int, include_resolved: bool) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for thread_id in _review_thread_ids(repo, pr):
        thread = _review_thread_context(thread_id)
        resolved = thread["is_resolved"]
        outdated = thread["is_outdated"]
        if not include_resolved and (resolved or outdated):
            continue
        exact_thread_fingerprint = _exact_thread_fingerprint(
            thread,
            repo,
            pr,
            thread["head_sha"],
        )
        for comment in thread["comments"]:
            if isinstance(comment.get("databaseId"), int):
                entries.append(
                    {
                        "type": "review_thread_comment",
                        "thread_id": thread_id,
                        "thread_fingerprint": exact_thread_fingerprint,
                        "head_sha": thread["head_sha"],
                        "comment_id": int(comment["databaseId"]),
                        "comment_node_id": comment.get("id"),
                        "author": ((comment.get("author") or {}).get("login") or ""),
                        "updated": comment.get("updatedAt") or comment.get("createdAt") or "",
                        "body": comment.get("body") or "",
                        "body_preview": snippet(comment.get("body") or ""),
                        "path": thread["path"],
                        "line": thread["line"],
                        "start_line": thread["start_line"],
                        "is_resolved": resolved,
                        "is_outdated": outdated,
                        "viewer_can_resolve": thread["viewer_can_resolve"],
                    }
                )
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


def _reconcile_consumed_comment(
    endpoint: str,
    repo: str,
    pr: int,
    actor: str,
    body: ProviderText,
    packet: dict[str, Any],
    *,
    parent_comment_id: int | None = None,
    thread_comment_node_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Find one exact marker-bound comment after a consumed reservation."""

    try:
        items = _read_back_list(endpoint)
    except (ReviewError, GitStackError) as exc:
        raise _recovery_required(
            "The consumed comment could not be read back exactly; owner recovery is required.",
            code="provider_recovery_ambiguous",
            details={"read_back_code": getattr(exc, "code", "provider_read_back_failed")},
        ) from exc
    if endpoint.startswith(f"repos/{repo}/issues/"):
        target_field = "issue_url"
        target_suffix = f"/repos/{repo}/issues/{pr}"
    else:
        target_field = "pull_request_url"
        target_suffix = f"/repos/{repo}/pulls/{pr}"
    matches = [
        item for item in items
        if _item_login(item) == actor
        and str(item.get(target_field) or "").endswith(target_suffix)
        and response_text_matches(item, body)
        and _marker_matches(str(item.get("body") or ""), packet["operation_id"])
        and (parent_comment_id is None or item.get("in_reply_to_id") == parent_comment_id)
        and (
            thread_comment_node_ids is None
            or isinstance(item.get("node_id"), str)
            and item["node_id"] in thread_comment_node_ids
        )
    ]
    if len(matches) != 1:
        raise _recovery_required(
            "The consumed comment did not map to one unique provider artifact; owner recovery is required.",
            code="provider_recovery_ambiguous",
            details={"matches": len(matches), "operation_id": packet["operation_id"]},
        )
    return matches[0]


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
    head: str | None = None,
    request_key: str | None = None,
    request_fingerprint: str | None = None,
    reservation_file: str | None = None,
    owned_operation: dict[str, Any] | None = None,
    reconcile_consumed: bool = False,
    recovery_marker: dict[str, Any] | None = None,
) -> dict[str, Any]:
    packet = _require_reservation(
        reservation_file,
        kind="review-warning",
        repo=repo,
        pr=pr,
        head=head,
        request_key=request_key,
        request_fingerprint=request_fingerprint,
        body_fingerprint=body.sha256 if owned_operation is not None else None,
        owned_operation=owned_operation,
    )
    body = _marked_body(body, packet)
    try:
        before = require_worktree(expected_worktree_fingerprint)
    except GitStackError as exc:
        raise _review_error(exc) from exc
    target = {"repo": repo, "pr": pr, "kind": "conversation-comment"}
    consumed_marker = _read_consumed_marker(packet, reservation_file or "", require_consumed=reconcile_consumed, marker_observer=recovery_marker)
    if consumed_marker is not None and recovery_marker is not None:
        recovery_marker.update(consumed_marker)
    if consumed_marker is not None:
        actor = _viewer_login()
        item = _reconcile_consumed_comment(
            f"repos/{repo}/issues/{pr}/comments",
            repo,
            pr,
            actor,
            body,
            packet,
        )
        return _with_consumed_marker(_guarded_result(_proof(item, body, target=target, status="recovered"), before), consumed_marker)
    if reconcile_consumed:
        raise ReviewError("Mutation reconciliation cannot enter transport.", code="reservation_not_consumed", exit_code=4)
    _verify_pr_head(repo, pr, packet["head_sha"])
    if dry_run:
        return {
            "status": "dry-run", "target": target, "text": body.proof(),
            "transport": {"method": "POST", "endpoint": f"repos/{repo}/issues/{pr}/comments", "api_version": API_VERSION},
        }
    actor = _viewer_login()
    _consume_reservation(packet, reservation_file or "")
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    result = api_request("POST", f"repos/{repo}/issues/{pr}/comments", {"body": body.text})
    finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    def prove(item: dict[str, Any]) -> dict[str, Any]:
        if (
            not str(item.get("issue_url") or "").endswith(f"/repos/{repo}/issues/{pr}")
            or _item_login(item) != actor
            or not _marker_matches(str(item.get("body") or ""), packet["operation_id"])
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
            and _marker_matches(str(item.get("body") or ""), packet["operation_id"])
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
    reservation_file: str | None = None,
    owned_operation: dict[str, Any] | None = None,
    reconcile_consumed: bool = False,
    recovery_marker: dict[str, Any] | None = None,
) -> dict[str, Any]:
    is_provider_author(provider, "")
    try:
        plan = build_request(provider, repo, pr, head, request_key)
    except ValueError as exc:
        raise ReviewError(str(exc), code="invalid_request", exit_code=64) from exc
    packet = _require_reservation(
        reservation_file,
        kind="review-request",
        repo=repo,
        pr=pr,
        head=plan.head_sha,
        request_key=plan.request_key,
        request_fingerprint=plan.request_fingerprint,
        body_fingerprint=plan.body_fingerprint,
        owned_operation=owned_operation,
    )
    if packet["operation_id"] != operation_id_for_request(
        repo, pr, plan.head_sha, plan.request_key, plan.request_fingerprint
    ):
        raise ReviewError(
            "The request reservation operation identity is invalid.",
            code="reservation_target_mismatch",
            exit_code=4,
        )
    consumed_marker = _read_consumed_marker(packet, reservation_file or "", require_consumed=reconcile_consumed, marker_observer=recovery_marker)
    if consumed_marker is not None and recovery_marker is not None:
        recovery_marker.update(consumed_marker)
    if consumed_marker is not None:
        return _with_consumed_marker(_reconcile_consumed_request(repo, pr, plan, packet), consumed_marker)
    if reconcile_consumed:
        raise ReviewError("Mutation reconciliation cannot enter transport.", code="reservation_not_consumed", exit_code=4)
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
        actor = _viewer_login()
        owned = [item for item in exact if _item_login(item) == actor]
        if len(owned) != 1:
            raise _recovery_required(
                "The exact Codex request is not uniquely owned by the authenticated actor; owner recovery is required.",
                code="request_unknown",
                details={"matches": len(owned), "exact_matches": len(exact)},
            )
        existing = owned[0]
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
    _consume_reservation(packet, reservation_file or "")
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
    head: str,
    comment_id: int,
    body: ProviderText,
    dry_run: bool,
    expected_worktree_fingerprint: str | None,
    request_key: str | None = None,
    request_fingerprint: str | None = None,
    reservation_file: str | None = None,
    owned_operation: dict[str, Any] | None = None,
    reconcile_consumed: bool = False,
    recovery_marker: dict[str, Any] | None = None,
    expected_thread_id: str | None = None,
    expected_thread_fingerprint: str | None = None,
) -> dict[str, Any]:
    try:
        reply_head = validate_full_head(head)
    except ValueError as exc:
        raise ReviewError(str(exc), code="invalid_arguments", exit_code=64) from exc
    parent, thread, exact_thread_fingerprint, finding_head = _reply_thread_identity(
        repo, pr, reply_head, comment_id,
    )
    if expected_thread_id is not None and str(thread["thread_id"]) != expected_thread_id:
        raise ReviewError("Review thread differs from the owned request.", code="review_thread_mismatch", exit_code=4)
    if not reconcile_consumed and expected_thread_fingerprint is not None and exact_thread_fingerprint != expected_thread_fingerprint:
        raise ReviewError("Review thread fingerprint differs from the owned request.", code="review_thread_mismatch", exit_code=4)
    reserved_thread_fingerprint = expected_thread_fingerprint or exact_thread_fingerprint
    packet = _require_reservation(
        reservation_file,
        kind="review-reply",
        repo=repo,
        pr=pr,
        head=reply_head,
        request_key=request_key,
        request_fingerprint=request_fingerprint,
        thread_id=str(thread["thread_id"]),
        # Validate the immutable pre-reply fingerprint below. A consumed
        # replay may already contain the one marker-bound reply, so the live
        # thread's comment set is intentionally allowed to differ here.
        thread_fingerprint=reserved_thread_fingerprint,
        finding_comment_id=comment_id,
        allow_thread_fingerprint_mismatch=True,
        body_fingerprint=body.sha256 if owned_operation is not None else None,
        owned_operation=owned_operation,
    )
    body = _marked_body(body, packet)
    try:
        before = require_worktree(expected_worktree_fingerprint)
    except GitStackError as exc:
        raise _review_error(exc) from exc
    target = {
        "repo": repo,
        "pr": pr,
        "head": reply_head,
        "kind": "review-reply",
        "thread_id": thread["thread_id"],
        "finding_comment_id": comment_id,
        "finding_node_id": parent["node_id"],
    }
    endpoint = f"repos/{repo}/pulls/{pr}/comments/{comment_id}/replies"
    consumed_marker = _read_consumed_marker(packet, reservation_file or "", require_consumed=reconcile_consumed, marker_observer=recovery_marker)
    if consumed_marker is not None and recovery_marker is not None:
        recovery_marker.update(consumed_marker)
    if consumed_marker is not None:
        try:
            recovery_thread = _review_thread_context(str(packet["thread_id"]))
        except ReviewError as exc:
            raise _recovery_required(
                "The consumed review reply thread could not be read back exactly; owner recovery is required.",
                code="provider_recovery_ambiguous",
                details={"read_back_code": exc.code},
            ) from exc
        recovered_reply_node_id: str | None = None
        if (
            recovery_thread.get("thread_id") != packet["thread_id"]
            or recovery_thread.get("repository") != repo
            or recovery_thread.get("pr_number") != pr
            or recovery_thread.get("head_sha") != packet["head_sha"]
        ):
            raise _recovery_required(
                "The consumed review reply thread changed; owner recovery is required.",
                code="provider_recovery_ambiguous",
            )
        thread_comment_node_ids = {
            str(item["id"])
            for item in recovery_thread.get("comments", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        actor = _viewer_login()
        item = _reconcile_consumed_comment(
            f"repos/{repo}/pulls/{pr}/comments",
            repo,
            pr,
            actor,
            body,
            packet,
            parent_comment_id=comment_id,
            thread_comment_node_ids=thread_comment_node_ids,
        )
        recovered_reply_node_id = str(item.get("node_id") or "")
        original_comments = [
            comment for comment in recovery_thread.get("comments", [])
            if not (
                isinstance(comment, dict)
                and (
                    comment.get("id") == recovered_reply_node_id
                    or comment.get("databaseId") == item.get("id")
                )
            )
        ]
        if len(original_comments) + 1 != len(recovery_thread.get("comments", [])):
            raise _recovery_required(
                "The consumed review reply was not the sole added thread comment; owner recovery is required.",
                code="provider_recovery_ambiguous",
            )
        original_thread = {**recovery_thread, "comments": original_comments}
        if _exact_thread_fingerprint(original_thread, repo, pr, reply_head) != packet["thread_fingerprint"]:
            raise _recovery_required(
                "The consumed review reply did not restore the reserved thread identity; owner recovery is required.",
                code="provider_recovery_ambiguous",
            )
        proof = _proof(item, body, target=target, status="recovered")
        proof["reply"] = build_reply_receipt(
            repository=repo,
            pr_number=pr,
            finding_head_sha=finding_head,
            reply_head_sha=reply_head,
            thread_id=recovery_thread["thread_id"],
            finding=parent,
            reply=item,
            body_fingerprint=body.sha256,
            status="recovered",
        )
        proof["transport"] = {"method": "POST", "endpoint": endpoint, "recovered": True}
        return _with_consumed_marker(_guarded_result(proof, before), consumed_marker)
    if reconcile_consumed:
        raise ReviewError("Mutation reconciliation cannot enter transport.", code="reservation_not_consumed", exit_code=4)
    _verify_pr_head(repo, pr, reply_head)
    if packet.get("thread_fingerprint") is not None and exact_thread_fingerprint != packet["thread_fingerprint"]:
        raise ReviewError(
            "The review thread changed before the typed reply could be posted.",
            code="review_thread_mismatch",
            exit_code=4,
        )
    if dry_run:
        return {
            "status": "dry-run",
            "target": target,
            "text": body.proof(),
            "transport": {"method": "POST", "endpoint": endpoint, "api_version": API_VERSION},
        }
    actor = _viewer_login()
    _consume_reservation(packet, reservation_file or "")
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    result = api_request("POST", endpoint, {"body": body.text})
    finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    def prove(item: dict[str, Any]) -> dict[str, Any]:
        if (
            item.get("in_reply_to_id") != comment_id
            or not str(item.get("pull_request_url") or "").endswith(f"/repos/{repo}/pulls/{pr}")
            or _item_login(item) != actor
            or not _marker_matches(str(item.get("body") or ""), packet["operation_id"])
            or not _in_creation_window(item, "created_at", started_at, finished_at)
            or not isinstance(item.get("node_id"), str)
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
            and _marker_matches(str(item.get("body") or ""), packet["operation_id"])
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
        action = _proof(proof.value, body, target=target, status=status)
        try:
            _verify_pr_head(repo, pr, reply_head)
        except ReviewError as exc:
            head_drift = exc.code == "head_drift"
            raise ReviewError(
                (
                    "The pull-request head moved after the review reply mutation; do not retry blindly."
                    if head_drift
                    else "The pull-request head could not be proven after the review reply mutation; do not retry blindly."
                ),
                code="reply_head_drift" if head_drift else "reply_head_unknown",
                exit_code=4,
                details={
                    "mutation_attempted": True,
                    "mutation_may_have_applied": True,
                    "head_check": {"code": exc.code},
                },
            ) from exc
        action["reply"] = build_reply_receipt(
            repository=repo,
            pr_number=pr,
            finding_head_sha=finding_head,
            reply_head_sha=reply_head,
            thread_id=thread["thread_id"],
            finding=parent,
            reply=proof.value,
            body_fingerprint=body.sha256,
            status=status,
        )
        return _guarded_result(action, before)
    except GitStackError as exc:
        raise _review_error(exc) from exc


def _validate_reply_remote(
    repo: str,
    pr: int,
    head: str,
    receipt_value: object,
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        saved = validate_reply_receipt(receipt_value)
        expected_head = validate_full_head(head)
    except ValueError as exc:
        raise ReviewError(str(exc), code="reply_receipt_invalid", exit_code=64) from exc
    if saved["repository"] != repo or saved["pr_number"] != pr or saved["reply_head_sha"] != expected_head:
        raise ReviewError("Reply receipt does not match the exact resolution target.", code="review_thread_mismatch", exit_code=4)
    _verify_pr_head(repo, pr, expected_head)
    finding = _api_object(f"repos/{repo}/pulls/comments/{saved['finding_comment_id']}")
    reply = _api_object(f"repos/{repo}/pulls/comments/{saved['reply_comment_id']}")
    if (
        finding.get("id") != saved["finding_comment_id"]
        or finding.get("node_id") != saved["finding_node_id"]
        or finding.get("html_url") != saved["finding_ref"]
        or finding.get("created_at") != saved["finding_created_at"]
        or finding.get("commit_id") != saved["finding_head_sha"]
        or finding.get("in_reply_to_id") is not None
        or not str(finding.get("pull_request_url") or "").endswith(f"/repos/{repo}/pulls/{pr}")
    ):
        raise ReviewError("Review finding no longer matches its reply receipt.", code="evidence_reply_mismatch", exit_code=4)
    try:
        reply_bytes = str(reply.get("body") or "").encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ReviewError("Evidence reply body cannot be verified as UTF-8.", code="evidence_reply_mismatch", exit_code=4) from exc
    if (
        reply.get("id") != saved["reply_comment_id"]
        or reply.get("node_id") != saved["reply_node_id"]
        or reply.get("in_reply_to_id") != saved["finding_comment_id"]
        or _item_login(reply) != saved["reply_author"]
        or reply.get("html_url") != saved["reply_ref"]
        or reply.get("created_at") != saved["reply_created_at"]
        or hashlib.sha256(reply_bytes).hexdigest() != saved["body_fingerprint"]
        or not str(reply.get("pull_request_url") or "").endswith(f"/repos/{repo}/pulls/{pr}")
    ):
        raise ReviewError("Evidence reply no longer matches its immutable receipt.", code="evidence_reply_mismatch", exit_code=4)
    thread = _review_thread_context(saved["thread_id"])
    if thread["repository"] != repo or thread["pr_number"] != pr or thread["head_sha"] != expected_head:
        raise ReviewError("Review thread does not match the exact repository, PR, and head.", code="review_thread_mismatch", exit_code=4)
    if thread["is_outdated"]:
        raise ReviewError("Outdated review threads are not eligible for typed resolution.", code="review_thread_outdated", exit_code=4)
    node_ids = {item.get("id") for item in thread["comments"]}
    if saved["finding_node_id"] not in node_ids or saved["reply_node_id"] not in node_ids:
        raise ReviewError("Finding and evidence reply are not members of the exact thread.", code="evidence_reply_not_found", exit_code=4)
    return saved, thread


def _resolution_result_thread(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("errors"):
        raise ReviewError("Review-thread mutation returned GraphQL errors.", code="provider_response_invalid", exit_code=65)
    thread = (((payload.get("data") or {}).get("resolveReviewThread") or {}).get("thread"))
    if not isinstance(thread, dict):
        raise ReviewError("Review-thread mutation omitted its target.", code="provider_response_invalid", exit_code=65)
    return {
        "thread_id": thread.get("id"),
        "is_resolved": bool(thread.get("isResolved")),
        "is_outdated": bool(thread.get("isOutdated")),
        "viewer_can_resolve": bool(thread.get("viewerCanResolve")),
        "repository": str((thread.get("repository") or {}).get("nameWithOwner") or ""),
        "pr_number": (thread.get("pullRequest") or {}).get("number"),
        "pr_state": str((thread.get("pullRequest") or {}).get("state") or "").lower(),
        "head_sha": str((thread.get("pullRequest") or {}).get("headRefOid") or ""),
    }


def _prove_resolved_thread(
    thread: dict[str, Any],
    saved: dict[str, Any],
    *,
    mutation_may_have_applied: bool,
) -> None:
    if thread.get("head_sha") != saved["reply_head_sha"]:
        raise ReviewError(
            "The pull-request head moved across the review-thread resolution window.",
            code="resolution_head_drift",
            exit_code=4,
            details={"mutation_may_have_applied": mutation_may_have_applied},
        )
    if (
        thread.get("thread_id") != saved["thread_id"]
        or thread.get("repository") != saved["repository"]
        or thread.get("pr_number") != saved["pr_number"]
        or thread.get("pr_state") != "open"
    ):
        raise ReviewError(
            "Review-thread resolution target changed.",
            code="review_thread_mismatch",
            exit_code=4,
            details={"mutation_may_have_applied": mutation_may_have_applied},
        )
    if not thread.get("is_resolved"):
        raise ReviewError(
            "Review-thread resolution is unknown after one exact read-back; do not retry blindly.",
            code="resolution_unknown",
            exit_code=4,
            details={"mutation_may_have_applied": mutation_may_have_applied},
        )


def resolve_review_thread(
    repo: str,
    pr: int,
    head: str,
    reply_receipt: object,
    dry_run: bool,
    expected_worktree_fingerprint: str | None,
    request_key: str | None = None,
    request_fingerprint: str | None = None,
    reservation_file: str | None = None,
    owned_operation: dict[str, Any] | None = None,
    reconcile_consumed: bool = False,
    recovery_marker: dict[str, Any] | None = None,
) -> dict[str, Any]:
    saved, thread = _validate_reply_remote(repo, pr, head, reply_receipt)
    expected_head = validate_full_head(head)
    exact_thread_fingerprint = _exact_thread_fingerprint(thread, repo, pr, expected_head)
    packet = _require_reservation(
        reservation_file,
        kind="review-resolution",
        repo=repo,
        pr=pr,
        head=head,
        request_key=request_key,
        request_fingerprint=request_fingerprint,
        thread_id=str(saved["thread_id"]),
        thread_fingerprint=exact_thread_fingerprint,
        finding_comment_id=int(saved["finding_comment_id"]),
        reply_receipt_fingerprint=str(saved["identity_fingerprint"]),
        owned_operation=owned_operation,
    )
    try:
        before = require_worktree(expected_worktree_fingerprint)
    except GitStackError as exc:
        raise _review_error(exc) from exc
    target = {
        "repo": repo,
        "pr": pr,
        "head": saved["reply_head_sha"],
        "kind": "review-thread",
        "thread_id": saved["thread_id"],
        "finding_comment_id": saved["finding_comment_id"],
    }
    observed_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    consumed_marker = _read_consumed_marker(packet, reservation_file or "", require_consumed=reconcile_consumed, marker_observer=recovery_marker)
    if consumed_marker is not None and recovery_marker is not None:
        recovery_marker.update(consumed_marker)
    if consumed_marker is not None:
        try:
            recovery_thread = _review_thread_context(str(packet["thread_id"]))
            if _exact_thread_fingerprint(recovery_thread, repo, pr, expected_head) != packet["thread_fingerprint"]:
                raise ReviewError(
                    "The consumed review-thread identity changed.",
                    code="review_thread_mismatch",
                    exit_code=4,
                )
            _prove_resolved_thread(recovery_thread, saved, mutation_may_have_applied=True)
        except ReviewError as exc:
            raise _recovery_required(
                "The consumed review-thread resolution could not be proven exactly; owner recovery is required.",
                code=exc.code,
                details=exc.details,
            ) from exc
        receipt_value = build_resolution_receipt(saved, status="recovered", observed_at=observed_at)
        return _with_consumed_marker(_guarded_result(
            {
                "status": "recovered",
                "target": target,
                "resolution": receipt_value,
                "mutation_attempted": True,
                "mutation_may_have_applied": True,
                "transport": {"method": "POST", "endpoint": "graphql:resolveReviewThread", "recovered": True},
            },
            before,
        ), consumed_marker)
    if reconcile_consumed:
        raise ReviewError("Mutation reconciliation cannot enter transport.", code="reservation_not_consumed", exit_code=4)
    if thread["is_resolved"]:
        receipt_value = build_resolution_receipt(saved, status="already-resolved", observed_at=observed_at)
        return _guarded_result(
            {
                "status": "already-resolved",
                "target": target,
                "resolution": receipt_value,
                "mutation_attempted": False,
                "mutation_may_have_applied": False,
            },
            before,
        )
    if not thread["viewer_can_resolve"]:
        raise ReviewError("Authenticated viewer cannot resolve the exact review thread.", code="review_thread_not_resolvable", exit_code=4)
    if dry_run:
        return _guarded_result(
            {
                "status": "dry-run",
                "target": target,
                "reply_identity_fingerprint": saved["identity_fingerprint"],
                "mutation_attempted": False,
                "mutation_may_have_applied": False,
            },
            before,
        )
    mutation = """
mutation($threadId: ID!) {
  resolveReviewThread(input: {threadId: $threadId}) {
    thread {
      id
      isResolved
      isOutdated
      viewerCanResolve
      repository { nameWithOwner }
      pullRequest { number state headRefOid }
    }
  }
}
""".strip()
    _consume_reservation(packet, reservation_file or "")
    result = graphql_request(mutation, {"threadId": saved["thread_id"]})
    response_proven = False
    response_failure = "provider_write_unconfirmed"
    response_mismatch: ReviewError | None = None
    if result.returncode == 0:
        try:
            response_thread = _resolution_result_thread(json.loads(result.stdout))
            _prove_resolved_thread(response_thread, saved, mutation_may_have_applied=True)
            response_proven = True
            response_failure = "exact_state_proven"
        except json.JSONDecodeError:
            response_failure = "provider_response_invalid"
        except ReviewError as exc:
            response_failure = exc.code
            if exc.code in {"resolution_head_drift", "review_thread_mismatch"}:
                response_mismatch = exc

    read_back_error: ReviewError | None = None
    try:
        read_back_thread = _review_thread_context(saved["thread_id"])
        _prove_resolved_thread(read_back_thread, saved, mutation_may_have_applied=True)
    except ReviewError as exc:
        read_back_error = exc

    uncertainty = {
        "mutation_attempted": True,
        "mutation_may_have_applied": True,
        "response": {
            "code": response_failure,
            "transport_exit_code": result.returncode,
        },
        "read_back": {"code": read_back_error.code if read_back_error else "exact_state_proven"},
    }
    if response_mismatch is not None:
        raise ReviewError(
            response_mismatch.message,
            code=response_mismatch.code,
            exit_code=response_mismatch.exit_code,
            details=uncertainty,
        ) from response_mismatch
    if read_back_error is not None:
        if read_back_error.code in {"resolution_head_drift", "review_thread_mismatch", "resolution_unknown"}:
            raise ReviewError(
                read_back_error.message,
                code=read_back_error.code,
                exit_code=read_back_error.exit_code,
                details=uncertainty,
            ) from read_back_error
        raise ReviewError(
            "Review-thread mutation may have applied, but exact read-back failed; do not retry, undo, or fall back.",
            code="resolution_unknown",
            exit_code=4,
            details=uncertainty,
        ) from read_back_error

    status = "resolved" if response_proven else "recovered"
    observed_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    receipt_value = build_resolution_receipt(saved, status=status, observed_at=observed_at)
    action = {
        "status": status,
        "target": target,
        "resolution": receipt_value,
        "mutation_attempted": True,
        "mutation_may_have_applied": False,
        "transport": {"method": "POST", "endpoint": "graphql:resolveReviewThread"},
    }
    return _guarded_result(action, before)


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


def _write_reservation(path_value: str, packet: dict[str, Any]) -> None:
    path = Path(path_value)
    if not path.is_absolute() or path.is_symlink() or path.exists():
        raise ReviewError(
            "The reservation output must be a new absolute regular file.",
            code="reservation_output_invalid",
            exit_code=64,
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(packet, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise ReviewError("The reservation packet could not be written atomically.", code="reservation_output_failed", exit_code=4) from exc


def prepare_reservation(args: argparse.Namespace) -> dict[str, Any]:
    repo = resolve_repo(args.repo, allow_non_project=args.allow_non_project)
    pr = positive_int(args.pr, "pr")
    head = validate_full_head(args.head)
    request_key = args.request_key
    request_fp = args.request_fingerprint
    thread_id = args.thread_id
    thread_fp = args.thread_fingerprint
    finding_id = positive_int(args.finding_comment_id, "finding-comment-id") if args.finding_comment_id else None
    body_fp: str | None = None
    reply_fp: str | None = None
    operation_id: str
    if args.mutation_kind == "review-request":
        if not request_key:
            raise ReviewError("review-request preparation requires --request-key.", code="invalid_arguments", exit_code=64)
        plan = build_request("codex", repo, pr, head, request_key)
        request_fp = plan.request_fingerprint
        body_fp = plan.body_fingerprint
        operation_id = operation_id_for_request(repo, pr, head, plan.request_key, plan.request_fingerprint)
    elif args.mutation_kind in {"review-warning", "review-reply"}:
        if not request_key or not request_fp or not args.body_file:
            raise ReviewError("comment reservations require request identity and --body-file.", code="invalid_arguments", exit_code=64)
        try:
            source_body = read_text_file(args.body_file, field="body")
        except GitStackError as exc:
            raise _review_error(exc) from exc
        operation_id = operation_id_for_mutation(
            args.mutation_kind,
            repo,
            pr,
            head,
            request_fingerprint=request_fp,
            thread_id=thread_id,
            finding_comment_id=finding_id,
        )
        body_fp = text_fingerprint(add_operation_marker(source_body.text, operation_id))
        if args.mutation_kind == "review-reply" and (thread_id is None or thread_fp is None or finding_id is None):
            raise ReviewError("review-reply preparation requires exact thread and finding identity.", code="invalid_arguments", exit_code=64)
    else:
        if not request_key or not request_fp or not args.reply_receipt_file:
            raise ReviewError("review-resolution preparation requires request identity and --reply-receipt-file.", code="invalid_arguments", exit_code=64)
        try:
            receipt_value = json.loads(read_text_file(args.reply_receipt_file, field="reply-receipt").text)
            saved = validate_reply_receipt(receipt_value)
        except (GitStackError, json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ReviewError("The reply receipt cannot be used to prepare a resolution reservation.", code="reply_receipt_invalid", exit_code=64) from exc
        thread_id = str(saved["thread_id"])
        finding_id = int(saved["finding_comment_id"])
        if not thread_fp:
            raise ReviewError(
                "review-resolution preparation requires --thread-fingerprint.",
                code="invalid_arguments",
                exit_code=64,
            )
        reply_fp = str(saved["identity_fingerprint"])
        operation_id = operation_id_for_mutation(
            args.mutation_kind,
            repo,
            pr,
            head,
            request_fingerprint=request_fp,
            thread_id=thread_id,
            finding_comment_id=finding_id,
            reply_receipt_fingerprint=reply_fp,
        )
    packet = build_reservation(
        mutation_kind=args.mutation_kind,
        repository=repo,
        pr_number=pr,
        head_sha=head,
        task_key=args.task_key,
        delivery_key=args.delivery_key,
        operation_id=operation_id,
        request_key=request_key,
        request_fingerprint=request_fp,
        thread_id=thread_id,
        thread_fingerprint=thread_fp,
        finding_comment_id=finding_id,
        body_fingerprint=body_fp,
        reply_receipt_fingerprint=reply_fp,
        expected_generation=args.expected_generation,
        expected_state_fingerprint=args.expected_state_fingerprint,
        expected_claim_fingerprint=args.expected_claim_fingerprint,
        expected_task_state=args.expected_task_state,
    )
    if args.output_file:
        _write_reservation(args.output_file, packet)
    return {
        "reservation": packet,
        "packet_fingerprint": packet_fingerprint(packet),
        "marker": None if args.mutation_kind == "review-resolution" else operation_marker(packet["operation_id"]),
        "output_file": args.output_file,
    }


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


def _read_json_object(path_value: str, name: str) -> dict[str, Any]:
    path = Path(path_value)
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise ReviewError(f"The {name} must be an absolute regular non-symlinked file.", code="invalid_arguments", exit_code=64)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReviewError(f"The {name} must contain one JSON object.", code="invalid_arguments", exit_code=64) from exc
    if not isinstance(value, dict):
        raise ReviewError(f"The {name} must contain one JSON object.", code="invalid_arguments", exit_code=64)
    return value


def _write_json_object(path_value: str, value: dict[str, Any]) -> None:
    path = Path(path_value)
    if not path.is_absolute() or path.is_symlink():
        raise ReviewError("Operation output paths must be absolute and non-symlinked.", code="invalid_arguments", exit_code=64)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _operation_start_receipt(request: dict[str, Any]) -> dict[str, Any]:
    authority = request["authority"]
    value = {
        "schema": "gitstack-review-operation-start:v1",
        "owner": "gitstack",
        "operation": request["operation"],
        "operation_id": request["operation_id"],
        "request_fingerprint": request["request_fingerprint"],
        "journal_id": hashlib.sha256(json.dumps({
            "owner": "gitstack",
            "operation": request["operation"],
            "operation_id": request["operation_id"],
            "request_fingerprint": request["request_fingerprint"],
        }, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest(),
        "started_generation": authority["expected_generation"] + 1,
        "started_state_fingerprint": authority["expected_state_fingerprint"],
        "receipt_fingerprint": "0" * 64,
    }
    value["receipt_fingerprint"] = hashlib.sha256(json.dumps(
        {key: item for key, item in value.items() if key != "receipt_fingerprint"},
        sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8")).hexdigest()
    return validate_start_receipt(value, request)


def _read_operation_start(identity: dict[str, Any]) -> dict[str, Any]:
    root = _operation_journal_root()
    if not root.exists() or root.is_symlink() or not root.is_dir():
        raise ReviewError(
            "The exact GitStack operation start journal is absent or unsafe.",
            code="owned_operation_start_missing", exit_code=4,
        )
    path = root / f"{identity['operation_id']}.started.json"
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise OSError("operation start journal is not regular")
            value = json.loads(os.read(fd, 1_048_577).decode("utf-8"))
        finally:
            os.close(fd)
        return validate_start_receipt_identity(
            value,
            operation=identity["operation"],
            operation_id=identity["operation_id"],
            request_fingerprint=identity["request_fingerprint"],
            receipt_fingerprint=identity.get("start_receipt_fingerprint"),
        )
    except FileNotFoundError as exc:
        raise ReviewError(
            "The exact GitStack operation start journal is absent.",
            code="owned_operation_start_missing", exit_code=4,
        ) from exc
    except (OSError, UnicodeError, json.JSONDecodeError, OperationError) as exc:
        raise ReviewError(
            "The GitStack operation start journal is invalid or conflicting.",
            code="owned_operation_start_invalid", exit_code=4,
        ) from exc


def _start_owned_operation(request: dict[str, Any]) -> dict[str, Any]:
    receipt_value = _operation_start_receipt(request)
    root = _operation_journal_root()
    try:
        if root.exists() and (root.is_symlink() or not root.is_dir()):
            raise OSError("operation journal root is unsafe")
        root.mkdir(parents=True, exist_ok=True)
        if root.is_symlink() or not root.is_dir():
            raise OSError("operation journal root is unsafe")
        path = root / f"{request['operation_id']}.started.json"
        encoded = (json.dumps(receipt_value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        directory_fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return receipt_value
    except FileExistsError as exc:
        existing = _read_operation_start({
            "operation": request["operation"],
            "operation_id": request["operation_id"],
            "request_fingerprint": request["request_fingerprint"],
            "start_receipt_fingerprint": receipt_value["receipt_fingerprint"],
        })
        raise ReviewError(
            "This GitStack operation already started; resume or reconcile it without retrying.",
            code="owned_operation_already_started", exit_code=4,
            details={"start_receipt_fingerprint": existing["receipt_fingerprint"]},
        ) from exc
    except OSError as exc:
        raise ReviewError(
            "The GitStack operation could not be durably started.",
            code="owned_operation_start_failed", exit_code=4,
        ) from exc


def _owned_operation_start(request: dict[str, Any], *, create: bool) -> dict[str, Any]:
    if create:
        return _start_owned_operation(request)
    descriptor = operation_validation_descriptor(request)
    identity = descriptor["start_identity"]
    try:
        return _read_operation_start(identity)
    except ReviewError as exc:
        if request["operation"] == "reconcile-mutation" and exc.code == "owned_operation_start_missing":
            started = request["input"]["started_operation"]
            return validate_start_receipt(started["start_receipt"], started["request"])
        raise


def prepare_owned_operation(controller_file: str, input_file: str, output_file: str) -> dict[str, Any]:
    controller = _read_json_object(controller_file, "controller envelope")
    supplied = _read_json_object(input_file, "operation input")
    if set(supplied) != {"target", "input"}:
        raise ReviewError("Operation input must contain exactly target and input.", code="invalid_arguments", exit_code=64)
    descriptor = ((controller.get("packet_template") or {}).get("operation") or {})
    operation = str(descriptor.get("name") or "")
    input_value = supplied["input"]
    if isinstance(input_value, dict):
        input_value = dict(input_value)
        for prior_field in (
            "prior_pending_result", "prior_findings_result",
            "prior_reply_result", "prior_failed_result",
        ):
            if prior_field not in input_value:
                continue
            try:
                prior_result = validate_operation_result(input_value[prior_field])
                if (
                    prior_result["operation"] == "reconcile-mutation"
                    and prior_result["outcome"] == "completed-from-readback"
                ):
                    prior_result = validate_operation_result(
                        prior_result["facts"]["recovered_result"]
                    )
            except (KeyError, OperationError) as exc:
                raise ReviewError(
                    f"{prior_field} is not an exact owner result.",
                    code="owned_operation_invalid", exit_code=64,
                ) from exc
            input_value[prior_field] = prior_result
    if operation == "reply":
        expected_fields = {
            "request_receipt", "prior_findings_result", "followup_obligation",
            "finding_comment_id", "body_file", "body_fingerprint",
        }
        if not isinstance(input_value, dict) or set(input_value) != expected_fields:
            raise ReviewError(
                "Reply prepare input must omit owner-derived thread identity.",
                code="invalid_arguments", exit_code=64,
            )
        try:
            target = validate_operation_target(supplied["target"])
        except OperationError as exc:
            raise ReviewError(str(exc), code="owned_operation_invalid", exit_code=64) from exc
        finding_comment_id = input_value["finding_comment_id"]
        if not isinstance(finding_comment_id, int) or isinstance(finding_comment_id, bool):
            raise ReviewError("Reply finding_comment_id is invalid.", code="invalid_arguments", exit_code=64)
        _, thread, thread_fingerprint, _ = _reply_thread_identity(
            target["repository"], target["pr_number"], target["head_sha"], finding_comment_id,
        )
        input_value = {
            **input_value,
            "thread_id": str(thread["thread_id"]),
            "thread_fingerprint": thread_fingerprint,
        }
    try:
        request = build_operation_request(
            operation=operation, controller_envelope=controller,
            target=supplied["target"], input_value=input_value,
        )
    except OperationError as exc:
        raise ReviewError(str(exc), code="owned_operation_invalid", exit_code=64) from exc
    _write_json_object(output_file, request)
    return {"request_file": output_file, "request_fingerprint": request["request_fingerprint"], "operation_id": request["operation_id"], "operation": request["operation"]}


def _operation_outcome(operation: str, facts: dict[str, Any], exit_code: int = 0) -> tuple[str, str]:
    if operation == "request":
        return "completed", "recognized-existing" if facts.get("status") == "reused" else "created"
    if operation == "wait":
        binding = facts.get("request_binding")
        state = facts.get("review_state")
        if binding != "recognized":
            return "failed", "request-correlation-failure"
        if state == "clean": return "completed", "clean"
        if state == "findings": return "completed", "findings"
        if exit_code == 124: return "completed", "pending-at-deadline"
        return "failed", "provider-failure"
    if operation == "warning":
        return "completed", "recognized-existing" if facts.get("status") == "recovered" else "posted"
    if operation == "reply":
        return "completed", "recognized-existing" if facts.get("status") == "recovered" else "posted"
    if operation == "resolve":
        return "completed", "already-resolved" if facts.get("status") == "already-resolved" else "resolved"
    if operation == "reconcile-terminal":
        return "completed", "clean-verified" if facts.get("outcome") == "clean" else "findings-verified"
    if operation == "reconcile-mutation":
        states = (facts.get("marker_state"), facts.get("provider_artifact_state"))
        if states == ("exact", "unique"):
            return "completed", "completed-from-readback"
        if states in {("absent", "missing"), ("exact", "missing")}:
            return "blocked", "missing"
        if states in {("conflicting", "missing"), ("exact", "conflicting")}:
            return "ambiguous", "conflicting"
        return "ambiguous", "ambiguous"
    raise ReviewError("Unsupported owned operation outcome.", code="owned_operation_result_invalid", exit_code=4)


def _mutation_artifact(action: dict[str, Any], receipt_value: dict[str, Any] | None = None) -> dict[str, Any]:
    source = receipt_value or action
    object_id = source.get("comment_id") or source.get("reply_comment_id") or source.get("object_id")
    object_url = source.get("request_ref") or source.get("reply_ref") or source.get("url") or source.get("object_url")
    actor = source.get("actor") or source.get("reply_author") or source.get("author")
    body_fp = source.get("body_fingerprint") or ((action.get("text") or {}).get("sha256"))
    return {"status": str(action.get("status") or "posted"), "object_id": int(object_id), "object_url": str(object_url), "actor": str(actor), "body_fingerprint": str(body_fp)}


def _normalize_owned_facts(request: dict[str, Any], raw: dict[str, Any], outcome: str) -> dict[str, Any]:
    operation, target, supplied = request["operation"], request["target"], request["input"]
    if operation == "request":
        receipt_value = raw["request"]
        return {"repository": target["repository"], "pr_number": target["pr_number"], "head_sha": target["head_sha"], "provider": target["provider"], "request_receipt": receipt_value, "mutation": _mutation_artifact(raw, receipt_value)}
    if operation == "wait":
        state = raw.get("review_state")
        provider_state = state if state in {"clean", "findings"} else ("pending" if outcome == "pending-at-deadline" else "failed")
        evidence = raw.get("evidence") or {}
        kind = evidence.get("kind") if evidence.get("kind") in {"formal-review", "provider-comment", "clean-reaction"} else "none"
        artifact = {"kind": kind, "object_id": evidence.get("object_id") if kind != "none" else None, "object_url": evidence.get("object_url") if kind != "none" else None, "actor": evidence.get("actor") if kind != "none" else None, "body_fingerprint": evidence.get("body_fingerprint") if kind != "none" else None, "outcome": evidence.get("outcome") if kind != "none" else None}
        return {"repository": target["repository"], "pr_number": target["pr_number"], "head_sha": target["head_sha"], "provider": target["provider"], "request_receipt": supplied["request_receipt"], "request_binding": raw.get("request_binding"), "provider_state": provider_state, "observation_fingerprint": raw.get("observation_fingerprint"), "finding_count": int((raw.get("review") or {}).get("findings") or 0), "finding_comment_ids": list((raw.get("review") or {}).get("finding_comment_ids") or []), "artifact": artifact}
    if operation == "warning":
        return {"request_receipt": supplied["request_receipt"], "mutation": _mutation_artifact(raw)}
    if operation == "reply":
        return {"request_receipt": supplied["request_receipt"], "reply_receipt": raw["reply"], "mutation": _mutation_artifact(raw, raw["reply"])}
    if operation == "resolve":
        return {"request_receipt": supplied["request_receipt"], "resolution_receipt": raw["resolution"]}
    if operation == "reconcile-terminal":
        return {"prior_result_fingerprint": supplied["prior_failed_result"]["result_fingerprint"], "request_receipt": supplied["request_receipt"], "terminal_evidence": raw}
    if operation == "reconcile-mutation":
        return raw
    raise ReviewError("Unsupported owned operation normalization.", code="owned_operation_result_invalid", exit_code=4)


def _mutation_provider_state(exc: ReviewError) -> str:
    if exc.code in {"reservation_not_consumed", "reservation_conflict"}:
        return "missing"
    if exc.code == "reservation_target_mismatch":
        return "conflicting"
    matches = (exc.details or {}).get("matches") if isinstance(exc.details, dict) else None
    if matches == 0:
        return "missing"
    if isinstance(matches, int) and matches > 1:
        return "ambiguous"
    return "unreadable"


def execute_owned_operation(request_file: str, result_file: str, *, mode: str) -> dict[str, Any]:
    try:
        request = validate_operation_request(_read_json_object(request_file, "operation request"))
    except OperationError as exc:
        raise ReviewError(str(exc), code="owned_operation_invalid", exit_code=64) from exc
    if mode == "reconcile" and request["operation"] not in {"reconcile-mutation", "reconcile-terminal"}:
        raise ReviewError("Only reconciliation operations may use operation reconcile.", code="owned_operation_invalid", exit_code=64)
    if mode == "resume" and request["operation"] != "wait":
        raise ReviewError("Only an already-started wait may use operation resume.", code="owned_operation_invalid", exit_code=64)
    if mode == "execute" and request["operation"] in {"reconcile-mutation", "reconcile-terminal"}:
        raise ReviewError("Reconciliation operations require operation reconcile.", code="owned_operation_invalid", exit_code=64)
    start = _owned_operation_start(request, create=mode == "execute")
    target, supplied = request["target"], request["input"]
    operation = request["operation"]
    repo, pr, head, provider = target["repository"], target["pr_number"], target["head_sha"], target["provider"]
    exit_code = 0
    if operation == "request":
        facts = request_automated_review(repo, pr, provider, head, supplied["request_key"], False, request["authority"]["managed_checkout_fingerprint"], request_file, request)
    elif operation == "wait":
        from datetime import datetime as _datetime
        deadline = _datetime.fromisoformat(supplied["wait_deadline"].replace("Z", "+00:00"))
        invoked = _datetime.now(timezone.utc)
        timeout = max(0, int((deadline - invoked).total_seconds()))
        facts, exit_code = wait_for_automated_review(repo, pr, provider, head, timeout, 10, 30, supplied["request_receipt"])
    elif operation == "warning":
        body = read_text_file(supplied["body_file"], field="body")
        if body.sha256 != supplied["body_fingerprint"]: raise ReviewError("Warning body fingerprint changed.", code="owned_operation_drift", exit_code=4)
        receipt_value = supplied["request_receipt"]
        facts = post_conversation_comment(repo, pr, body, False, request["authority"]["managed_checkout_fingerprint"], head, receipt_value["request_key"], receipt_value["request_fingerprint"], request_file, request)
    elif operation == "reply":
        body = read_text_file(supplied["body_file"], field="body")
        if body.sha256 != supplied["body_fingerprint"]: raise ReviewError("Reply body fingerprint changed.", code="owned_operation_drift", exit_code=4)
        receipt_value = supplied["request_receipt"]
        facts = reply_to_review_comment(repo, pr, head, supplied["finding_comment_id"], body, False, request["authority"]["managed_checkout_fingerprint"], receipt_value["request_key"], receipt_value["request_fingerprint"], request_file, request, expected_thread_id=supplied["thread_id"], expected_thread_fingerprint=supplied["thread_fingerprint"])
    elif operation == "resolve":
        receipt_value = supplied["request_receipt"]
        facts = resolve_review_thread(repo, pr, head, supplied["reply_receipt"], False, request["authority"]["managed_checkout_fingerprint"], receipt_value["request_key"], receipt_value["request_fingerprint"], request_file, request)
    elif operation == "reconcile-terminal":
        facts = terminal_provider_evidence(repo, pr, provider, head, supplied["request_receipt"])
    else:
        started_operation = supplied["started_operation"]
        started = started_operation["request"]
        started_target, started_input = started["target"], started["input"]
        recovered_result = None
        recovery_marker: dict[str, Any] = {}
        try:
            if started["operation"] == "request":
                recovered_raw = request_automated_review(
                    started_target["repository"], started_target["pr_number"], started_target["provider"],
                    started_target["head_sha"], started_input["request_key"], False,
                    started["authority"]["managed_checkout_fingerprint"], request_file,
                    started, reconcile_consumed=True,
                    recovery_marker=recovery_marker,
                )
            elif started["operation"] == "warning":
                body = read_text_file(started_input["body_file"], field="body")
                recovered_raw = post_conversation_comment(
                    started_target["repository"], started_target["pr_number"], body, False,
                    started["authority"]["managed_checkout_fingerprint"], started_target["head_sha"],
                    started_input["request_receipt"]["request_key"], started_input["request_receipt"]["request_fingerprint"],
                    request_file, started, reconcile_consumed=True,
                    recovery_marker=recovery_marker,
                )
            elif started["operation"] == "reply":
                body = read_text_file(started_input["body_file"], field="body")
                recovered_raw = reply_to_review_comment(
                    started_target["repository"], started_target["pr_number"], started_target["head_sha"],
                    started_input["finding_comment_id"], body, False,
                    started["authority"]["managed_checkout_fingerprint"],
                    started_input["request_receipt"]["request_key"], started_input["request_receipt"]["request_fingerprint"],
                    request_file, started, reconcile_consumed=True,
                    recovery_marker=recovery_marker,
                    expected_thread_id=started_input["thread_id"],
                    expected_thread_fingerprint=started_input["thread_fingerprint"],
                )
            else:
                recovered_raw = resolve_review_thread(
                    started_target["repository"], started_target["pr_number"], started_target["head_sha"],
                    started_input["reply_receipt"], False,
                    started["authority"]["managed_checkout_fingerprint"],
                    started_input["request_receipt"]["request_key"], started_input["request_receipt"]["request_fingerprint"],
                    request_file, started, reconcile_consumed=True,
                    recovery_marker=recovery_marker,
                )
            recovered_status, recovered_outcome = _operation_outcome(started["operation"], recovered_raw)
            recovered_facts = _normalize_owned_facts(started, recovered_raw, recovered_outcome)
            recovered_result = build_operation_result(
                request=started, start_receipt=started_operation["start_receipt"],
                status=recovered_status, outcome=recovered_outcome, facts=recovered_facts,
                evidence_ref=f"gitstack-operation://recovered/{started['operation_id']}",
            )
            marker_state = "exact"
            provider_artifact_state = "unique"
        except ReviewError as exc:
            marker_state = (
                "conflicting" if exc.code == "reservation_conflict"
                else "exact" if recovery_marker else "absent"
            )
            provider_artifact_state = _mutation_provider_state(exc)
        verified_marker_fingerprint = (
            _consumed_marker_fingerprint(recovery_marker) if recovery_marker else None
        )
        facts = {
            "started_operation": started["operation"],
            "marker_state": marker_state,
            "marker_fingerprint": verified_marker_fingerprint,
            "provider_artifact_state": provider_artifact_state,
            "recovered_result": recovered_result,
        }
    status, outcome = _operation_outcome(operation, facts, exit_code)
    normalized_facts = _normalize_owned_facts(request, facts, outcome)
    try:
        result = build_operation_result(request=request, start_receipt=start, status=status, outcome=outcome, facts=normalized_facts, evidence_ref=f"gitstack-operation://{request['operation_id']}")
        validate_result_for_request(result, request)
    except OperationError as exc:
        raise ReviewError(str(exc), code="owned_operation_result_invalid", exit_code=4) from exc
    _write_json_object(result_file, result)
    return {"result_file": result_file, "result_fingerprint": result["result_fingerprint"], "status": status, "outcome": outcome}


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
    operation = subparsers.add_parser("operation", help="Prepare, validate, execute, or reconcile one closed owned review operation.")
    operation_sub = operation.add_subparsers(dest="operation_command", required=True)
    operation_prepare = operation_sub.add_parser("prepare", help="Prepare one immutable GitStack-owned request without side effects.")
    operation_prepare.add_argument("--controller-envelope-file", required=True)
    operation_prepare.add_argument("--input-file", required=True)
    operation_prepare.add_argument("--request-output", required=True)
    for verb, help_text in (("validate-request", "Validate one immutable request."), ("validate-result", "Validate one immutable result.")):
        child = operation_sub.add_parser(verb, help=help_text)
        child.add_argument("--request-file" if verb == "validate-request" else "--result-file", required=True)
        if verb == "validate-result":
            child.add_argument("--request-file", required=True)
    for verb, help_text in (("execute", "Execute one authority-started owned operation."), ("resume", "Resume one already-started wait without resetting its deadline."), ("reconcile", "Reconcile one already-started operation without a new side effect.")):
        child = operation_sub.add_parser(verb, help=help_text)
        child.add_argument("--request-file", required=True)
        child.add_argument("--result-output", required=True)
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
    comment.add_argument("--head", required=True, help="Full 40-character current PR head SHA.")
    comment.add_argument("--request-key", required=True, help="Exact review request key bound to the warning.")
    comment.add_argument("--request-fingerprint", required=True, help="Exact typed review request fingerprint.")
    comment.add_argument("--reservation-file", required=True, help="Absolute immutable provider-mutation reservation packet.")
    comment.add_argument("--dry-run", action="store_true", help="Preview the comment action without posting.")
    comment.add_argument("--expected-worktree-fingerprint")
    comment.add_argument("--allow-non-project", action="store_true", help="Allow --repo usage outside a git checkout.")
    request = subparsers.add_parser("request", help="Post or recover one typed, exact-head automated review request.")
    request.add_argument("--provider", required=True, help="Automated review provider. Currently: codex.")
    request.add_argument("--pr", required=True, help="Pull request number.")
    request.add_argument("--repo", help="Repository in owner/repo format. Defaults to current checkout.")
    request.add_argument("--head", required=True, help="Full 40-character expected reviewed head SHA.")
    request.add_argument("--request-key", required=True, help="Stable caller-owned request lineage key.")
    request.add_argument("--reservation-file", required=True, help="Absolute immutable provider-mutation reservation packet.")
    request.add_argument("--dry-run", action="store_true", help="Preview the canonical request without posting.")
    request.add_argument("--expected-worktree-fingerprint")
    request.add_argument("--allow-non-project", action="store_true", help="Allow --repo usage outside a git checkout.")
    reply = subparsers.add_parser("reply", help="Reply to one pull-request review comment.")
    reply.add_argument("--pr", required=True)
    reply.add_argument("--repo")
    reply.add_argument("--head", required=True, help="Full 40-character current PR head SHA.")
    reply.add_argument("--comment-id", required=True)
    reply.add_argument("--body-file", required=True)
    reply.add_argument("--request-key", required=True)
    reply.add_argument("--request-fingerprint", required=True)
    reply.add_argument("--reservation-file", required=True)
    reply.add_argument("--dry-run", action="store_true")
    reply.add_argument("--expected-worktree-fingerprint")
    reply.add_argument("--allow-non-project", action="store_true")
    resolve = subparsers.add_parser("resolve", help="Resolve one exact review thread from its typed evidence-reply receipt.")
    resolve.add_argument("--pr", required=True)
    resolve.add_argument("--repo")
    resolve.add_argument("--head", required=True, help="Full 40-character current PR head SHA.")
    resolve.add_argument("--reply-receipt-file", required=True, help="Absolute UTF-8 JSON file containing the typed reply receipt.")
    resolve.add_argument("--request-key", required=True)
    resolve.add_argument("--request-fingerprint", required=True)
    resolve.add_argument("--reservation-file", required=True)
    resolve.add_argument("--dry-run", action="store_true")
    resolve.add_argument("--expected-worktree-fingerprint")
    resolve.add_argument("--allow-non-project", action="store_true")
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
    prepare = subparsers.add_parser(
        "prepare",
        help="Create one canonical immutable provider-mutation packet for a managed root handoff; does not authorize transport.",
    )
    prepare.add_argument("--mutation-kind", required=True, choices=tuple(sorted(MUTATION_KINDS)))
    prepare.add_argument("--repo")
    prepare.add_argument("--pr", required=True)
    prepare.add_argument("--head", required=True)
    prepare.add_argument("--task-key", required=True)
    prepare.add_argument("--delivery-key", required=True)
    prepare.add_argument("--expected-generation", required=True, type=int)
    prepare.add_argument("--expected-state-fingerprint", required=True)
    prepare.add_argument("--expected-claim-fingerprint", required=True)
    prepare.add_argument("--expected-task-state", required=True)
    prepare.add_argument("--request-key")
    prepare.add_argument("--request-fingerprint")
    prepare.add_argument("--thread-id")
    prepare.add_argument("--thread-fingerprint")
    prepare.add_argument("--finding-comment-id")
    prepare.add_argument("--body-file")
    prepare.add_argument("--reply-receipt-file")
    prepare.add_argument("--output-file")
    prepare.add_argument("--allow-non-project", action="store_true")
    validate = subparsers.add_parser(
        "validate",
        help="Validate one canonical immutable provider-mutation packet; does not authorize transport.",
    )
    validate.add_argument("--reservation-file", required=True)
    terminal = subparsers.add_parser(
        "terminal-evidence",
        help="Verify one typed exact-head terminal provider artifact read-only.",
    )
    terminal.add_argument("--provider", required=True, help="Automated review provider. Currently: codex.")
    terminal.add_argument("--pr", required=True, help="Pull request number.")
    terminal.add_argument("--repo", help="Repository in owner/repo format. Defaults to current checkout.")
    terminal.add_argument("--head", required=True, help="Full 40-character expected reviewed head SHA.")
    terminal.add_argument(
        "--request-receipt-file",
        required=True,
        help="Absolute UTF-8 JSON file containing the complete typed request receipt.",
    )
    terminal.add_argument("--allow-non-project", action="store_true", help="Allow --repo usage outside a git checkout.")
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
            emit_error(exc, [next((item for item in raw if item in {"address", "comment", "request", "reply", "resolve", "edit-comment", "submit-review", "prepare", "validate", "check", "wait", "terminal-evidence"}), "")])
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
    if args.command == "validate":
        try:
            packet = _read_reservation_file(args.reservation_file)
        except ReviewError as exc:
            if args.json:
                emit_error(exc, ["validate"])
            else:
                print(exc.message, file=sys.stderr)
            return exc.exit_code
        payload = {
            "reservation": packet,
            "packet_fingerprint": packet_fingerprint(packet),
            "marker": None if packet["mutation_kind"] == "review-resolution" else operation_marker(packet["operation_id"]),
        }
        if args.json:
            emit_success(payload, ["validate"])
        else:
            print(json.dumps(payload, indent=2))
        return 0
    if args.command == "prepare":
        try:
            payload = prepare_reservation(args)
        except ReviewError as exc:
            if args.json:
                emit_error(exc, ["prepare"])
            else:
                print(exc.message, file=sys.stderr)
            return exc.exit_code
        if args.json:
            emit_success(payload, ["prepare"])
        else:
            print(json.dumps(payload, indent=2))
        return 0
    if args.command == "operation":
        try:
            if args.operation_command == "prepare":
                payload = prepare_owned_operation(args.controller_envelope_file, args.input_file, args.request_output)
            elif args.operation_command == "validate-request":
                request = validate_operation_request(_read_json_object(args.request_file, "operation request"))
                payload = {"request": request, "validation_descriptor": operation_validation_descriptor(request)}
            elif args.operation_command == "validate-result":
                request = _read_json_object(args.request_file, "operation request")
                result = _read_json_object(args.result_file, "operation result")
                payload = {
                    "result": validate_result_for_request(result, request),
                    "validation_descriptor": operation_validation_descriptor(request, result),
                }
            else:
                payload = execute_owned_operation(args.request_file, args.result_output, mode=args.operation_command)
        except (OperationError, ReviewError) as exc:
            error = exc if isinstance(exc, ReviewError) else ReviewError(str(exc), code="owned_operation_invalid", exit_code=64)
            if args.json:
                emit_error(error, ["operation", args.operation_command])
            else:
                print(error.message, file=sys.stderr)
            return error.exit_code
        if args.json:
            emit_success(payload, ["operation", args.operation_command])
        else:
            print(json.dumps(payload, indent=2))
        return 0
    if args.command not in {"address", "comment", "request", "reply", "resolve", "edit-comment", "submit-review", "check", "wait", "terminal-evidence"}:
        parser.print_help()
        return 0
    try:
        pr = positive_int(args.pr, "pr")
        repo = resolve_repo(args.repo, allow_non_project=args.allow_non_project)
        if args.command in {"check", "wait", "terminal-evidence"}:
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
            if args.command in {"wait", "terminal-evidence"} and request_identity is None:
                raise ReviewError(
                    "The identity-bound automated review waiter requires --request-receipt-file.",
                    code="request_binding_required",
                    exit_code=64,
                )
            if args.command == "terminal-evidence":
                payload = terminal_provider_evidence(
                    repo,
                    pr,
                    args.provider,
                    args.head,
                    request_identity,
                )
                exit_code = 0
            elif args.command == "check":
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
                args.reservation_file,
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
            payload = {"repo": repo, "pr": pr, "action": post_conversation_comment(repo, pr, body, args.dry_run, args.expected_worktree_fingerprint, args.head, args.request_key, args.request_fingerprint, args.reservation_file)}
            if args.json:
                emit_success(payload, ["comment"])
            else:
                print(render_text(payload), end="")
            return 0
        if args.command == "resolve":
            try:
                receipt_text = read_text_file(args.reply_receipt_file, field="reply-receipt").text
                reply_receipt = json.loads(receipt_text)
            except (GitStackError, json.JSONDecodeError, TypeError) as exc:
                if isinstance(exc, GitStackError):
                    raise _review_error(exc) from exc
                raise ReviewError("The reply receipt file must contain one JSON object.", code="reply_receipt_invalid", exit_code=64) from exc
            action = resolve_review_thread(
                repo,
                pr,
                args.head,
                reply_receipt,
                args.dry_run,
                args.expected_worktree_fingerprint,
                args.request_key,
                args.request_fingerprint,
                args.reservation_file,
            )
            payload = {"repo": repo, "pr": pr, "action": action}
            if args.json:
                emit_success(payload, ["resolve"])
            else:
                print(json.dumps(payload, indent=2))
            return 0
        if args.command in {"reply", "edit-comment", "submit-review"}:
            try:
                body = read_text_file(args.body_file, field="body")
            except GitStackError as exc:
                raise _review_error(exc) from exc
            if args.command == "reply":
                comment_id = positive_int(args.comment_id, "comment-id")
                action = reply_to_review_comment(repo, pr, args.head, comment_id, body, args.dry_run, args.expected_worktree_fingerprint, args.request_key, args.request_fingerprint, args.reservation_file)
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
        if args.command in {"check", "wait", "terminal-evidence"} and exc.code == "command_failed":
            exc = ReviewError(exc.message, code="api_error", exit_code=4)
        if args.json:
            emit_error(exc, [args.command or ""])
        else:
            print(exc.message, file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
