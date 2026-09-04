from __future__ import annotations

# This module intentionally re-exports compatibility hooks used by callers and tests.
# ruff: noqa: F401

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


from . import __version__ as VERSION
from .common import GError
from .health import doctor as shared_doctor, doctor_text
from .repository import normalize_remote
from .review_types import ReviewError, RunResult
from .review_parser import build_parser
from . import review_reservation
from . import review_provider
from . import review_context
from . import review_observation
from . import review_actions
from . import review_operations
from . import review_cli
from .review_observation import REVIEW_EXIT_CODES, REQUEST_BINDING_EXIT_CODES
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
    receipt,
    validate_full_head,
)
from .review_thread import (
    build_reply_receipt,
    build_resolution_receipt,
    validate_reply_receipt,
)
from .terminal_evidence import build_terminal_evidence_receipt
from .review_mutation import (
    add_operation_marker,
    build_reservation,
    operation_marker,
    operation_id_for_mutation,
    operation_id_for_request,
    packet_fingerprint,
    text_fingerprint,
)
from .ready_review import ReadyReviewError, build_ready_trigger
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


def _trusted_user_home() -> Path:
    return review_reservation.trusted_user_home()


def _reservation_cache_root() -> Path:
    return _trusted_user_home() / ".cache/dotagents/plugins/g/review-mutations"


def _operation_journal_root() -> Path:
    return _trusted_user_home() / ".cache/dotagents/plugins/g/review-operations"


def _read_reservation_file(path_value: str | None) -> dict[str, Any]:
    return review_reservation.read_reservation_file(path_value)


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
    return review_reservation.require_reservation(
        path_value,
        kind=kind,
        repo=repo,
        pr=pr,
        head=head,
        request_key=request_key,
        request_fingerprint=request_fingerprint,
        thread_id=thread_id,
        thread_fingerprint=thread_fingerprint,
        finding_comment_id=finding_comment_id,
        body_fingerprint=body_fingerprint,
        reply_receipt_fingerprint=reply_receipt_fingerprint,
        allow_thread_fingerprint_mismatch=allow_thread_fingerprint_mismatch,
        owned_operation=owned_operation,
        read_packet=_read_reservation_file,
    )


def _read_consumed_marker(
    packet: dict[str, Any],
    reservation_file: str,
    *,
    require_consumed: bool = False,
    marker_observer: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    return review_reservation.read_consumed_marker(
        packet,
        reservation_file,
        root=_reservation_cache_root(),
        require_consumed=require_consumed,
        marker_observer=marker_observer,
    )


def _consumed_marker_fingerprint(marker: dict[str, Any]) -> str:
    return review_reservation.consumed_marker_fingerprint(marker)


def _with_consumed_marker(
    action: dict[str, Any], marker: dict[str, Any]
) -> dict[str, Any]:
    return review_reservation.with_consumed_marker(action, marker)


def _recovery_required(
    message: str,
    *,
    code: str,
    details: dict[str, Any] | None = None,
) -> ReviewError:
    return review_reservation.recovery_required(message, code=code, details=details)


def _consume_reservation(packet: dict[str, Any], reservation_file: str) -> None:
    review_reservation.consume_reservation(
        packet,
        reservation_file,
        root=_reservation_cache_root(),
        consumed_at=datetime.now(timezone.utc),
        read_marker=_read_consumed_marker,
    )


def _marked_body(body: ProviderText, packet: dict[str, Any]) -> ProviderText:
    return review_reservation.marked_body(body, packet)


def _marker_matches(text: str, operation_id: str) -> bool:
    return review_reservation.marker_matches(text, operation_id)


def run(command: list[str], *, cwd: Path | None = None) -> RunResult:
    return review_provider.run(command, cwd=cwd)


def run_gh(args: list[str]) -> RunResult:
    return run(["gh", *args])


def gh_json(args: list[str]) -> object:
    return review_provider.gh_json(args, runner=run_gh)


def gh_api_paginated_list(endpoint: str) -> list[dict[str, Any]]:
    return review_provider.paginated_list(endpoint, fetch_json=gh_json)


def graphql(query: str, variables: dict[str, object]) -> object:
    return review_provider.graphql(query, variables, fetch_json=gh_json)


def validate_repo(repo: str) -> str:
    return review_provider.validate_repo(repo)


def resolve_repo(repo: str | None, *, allow_non_project: bool) -> str:
    return review_provider.resolve_repo(
        repo, allow_non_project=allow_non_project, runner=run
    )


def _review_backend() -> Any:
    return sys.modules[__name__]


def snippet(text: str, limit: int = 220) -> str:
    return review_context.snippet(text, limit)


def _review_thread_context(thread_id: str) -> dict[str, Any]:
    return review_context.thread_context(thread_id, backend=_review_backend())


def _review_thread_ids(repo: str, pr: int) -> list[str]:
    return review_context.thread_ids(repo, pr, backend=_review_backend())


def _finding_thread(
    repo: str, pr: int, finding_comment_id: int, finding_node_id: str
) -> dict[str, Any]:
    return review_context.finding_thread(
        repo,
        pr,
        finding_comment_id,
        finding_node_id,
        backend=_review_backend(),
    )


def _exact_thread_fingerprint(
    thread: dict[str, Any], repo: str, pr: int, head: str
) -> str:
    return review_context.exact_thread_fingerprint(thread, repo, pr, head)


def _reply_thread_identity(
    repo: str,
    pr: int,
    head: str,
    comment_id: int,
) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    return review_context.reply_thread_identity(
        repo,
        pr,
        head,
        comment_id,
        backend=_review_backend(),
    )


def review_threads(repo: str, pr: int, include_resolved: bool) -> list[dict[str, Any]]:
    return review_context.review_threads(
        repo, pr, include_resolved, backend=_review_backend()
    )


def collect_entries(repo: str, pr: int, include_resolved: bool) -> list[dict[str, Any]]:
    return review_context.collect_entries(
        repo, pr, include_resolved, backend=_review_backend()
    )


def positive_int(raw: str | None, name: str) -> int:
    return review_observation.positive_int(raw, name, backend=_review_backend())


def duration_seconds(raw: str, name: str) -> float:
    return review_observation.duration_seconds(raw, name, backend=_review_backend())


def is_provider_author(provider: str, login: str) -> bool:
    return review_observation.is_provider_author(
        provider, login, backend=_review_backend()
    )


def authored_by(item: dict[str, Any], provider: str) -> bool:
    return review_observation.authored_by(item, provider, backend=_review_backend())


def sha_matches(actual: object, expected: str) -> bool:
    return review_observation.sha_matches(actual, expected, backend=_review_backend())


def validate_head(raw: str) -> str:
    return review_observation.validate_head(raw, backend=_review_backend())


def provider_terminal_comment_any(
    comment: dict[str, Any], provider: str
) -> dict[str, Any] | None:
    return review_observation.provider_terminal_comment_any(
        comment, provider, backend=_review_backend()
    )


def review_failure_classification(
    *,
    binding: str,
    status: str | None,
    head_is_current: bool,
    request_error_code: str | None,
) -> tuple[str | None, str | None]:
    return review_observation.review_failure_classification(
        binding=binding,
        status=status,
        head_is_current=head_is_current,
        request_error_code=request_error_code,
        backend=_review_backend(),
    )


def stable_observation_fingerprint(payload: dict[str, Any]) -> str:
    return review_observation.stable_observation_fingerprint(
        payload, backend=_review_backend()
    )


def provider_reactions(repo: str, comment_id: int, provider: str) -> set[str]:
    return review_observation.provider_reactions(
        repo, comment_id, provider, backend=_review_backend()
    )


def _receipt_is_complete(value: object) -> bool:
    return review_observation._receipt_is_complete(value, backend=_review_backend())


def _request_plan_from_receipt(
    value: object, provider: str, repository: str, pr_number: int
) -> RequestPlan | None:
    return review_observation._request_plan_from_receipt(
        value, provider, repository, pr_number, backend=_review_backend()
    )


def _comment_for_plan(comment: dict[str, Any], plan: RequestPlan) -> bool:
    return review_observation._comment_for_plan(
        comment, plan, backend=_review_backend()
    )


def _request_conflicts(
    conversation: list[dict[str, Any]], plan: RequestPlan
) -> tuple[str | None, list[dict[str, Any]]]:
    return review_observation._request_conflicts(
        conversation, plan, backend=_review_backend()
    )


def _reconcile_consumed_request(
    repo: str, pr: int, plan: RequestPlan, packet: dict[str, Any]
) -> dict[str, Any]:
    return review_observation._reconcile_consumed_request(
        repo, pr, plan, packet, backend=_review_backend()
    )


def _observed_request_metadata(
    plan: RequestPlan, comment: dict[str, Any]
) -> dict[str, Any]:
    return review_observation._observed_request_metadata(
        plan, comment, backend=_review_backend()
    )


def check_automated_review(
    repo: str,
    pr: int,
    provider: str,
    expected_head: str | None,
    request_identity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return review_observation.check_automated_review(
        repo, pr, provider, expected_head, request_identity, backend=_review_backend()
    )


def _ready_timestamp(value: object, name: str) -> datetime:
    return review_observation._ready_timestamp(value, name, backend=_review_backend())


def _provider_timestamp(value: object, name: str) -> datetime:
    return review_observation._provider_timestamp(
        value, name, backend=_review_backend()
    )


def _ready_artifact(
    kind: str, item: dict[str, Any], outcome: str | None
) -> dict[str, Any]:
    return review_observation._ready_artifact(
        kind, item, outcome, backend=_review_backend()
    )


def check_ready_automated_review(
    repo: str,
    pr: int,
    provider: str,
    expected_head: str,
    ready_identity: dict[str, Any],
) -> dict[str, Any]:
    return review_observation.check_ready_automated_review(
        repo, pr, provider, expected_head, ready_identity, backend=_review_backend()
    )


def wait_for_ready_automated_review(
    repo: str,
    pr: int,
    provider: str,
    expected_head: str,
    timeout: float,
    interval: float,
    max_interval: float,
    ready_identity: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    return review_observation.wait_for_ready_automated_review(
        repo,
        pr,
        provider,
        expected_head,
        timeout,
        interval,
        max_interval,
        ready_identity,
        backend=_review_backend(),
    )


def terminal_provider_evidence(
    repo: str,
    pr: int,
    provider: str,
    expected_head: str,
    request_identity: dict[str, Any],
) -> dict[str, Any]:
    return review_observation.terminal_provider_evidence(
        repo, pr, provider, expected_head, request_identity, backend=_review_backend()
    )


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
    return review_observation.wait_for_automated_review(
        repo,
        pr,
        provider,
        expected_head,
        timeout,
        initial_interval,
        max_interval,
        request_identity,
        backend=_review_backend(),
    )


def _review_error(exc: GError) -> ReviewError:
    return review_actions._review_error(exc, backend=_review_backend())


def _api_object(endpoint: str) -> dict[str, Any]:
    return review_actions._api_object(endpoint, backend=_review_backend())


def _viewer_login() -> str:
    return review_actions._viewer_login(backend=_review_backend())


def _verify_pr_target(repo: str, pr: int) -> dict[str, Any]:
    return review_actions._verify_pr_target(repo, pr, backend=_review_backend())


def _in_creation_window(
    item: dict[str, Any], field: str, started_at: str, finished_at: str
) -> bool:
    return review_actions._in_creation_window(
        item, field, started_at, finished_at, backend=_review_backend()
    )


def _proof(
    item: dict[str, Any], body: ProviderText, *, target: dict[str, Any], status: str
) -> dict[str, Any]:
    return review_actions._proof(
        item, body, target=target, status=status, backend=_review_backend()
    )


def _proof_failure(message: str, code: str) -> GError:
    return review_actions._proof_failure(message, code, backend=_review_backend())


def _item_login(item: dict[str, Any]) -> str:
    return review_actions._item_login(item, backend=_review_backend())


def _read_back_list(endpoint: str) -> list[dict[str, Any]]:
    return review_actions._read_back_list(endpoint, backend=_review_backend())


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
    return review_actions._reconcile_consumed_comment(
        endpoint,
        repo,
        pr,
        actor,
        body,
        packet,
        parent_comment_id=parent_comment_id,
        thread_comment_node_ids=thread_comment_node_ids,
        backend=_review_backend(),
    )


def _guarded_result(
    action: dict[str, Any], before: dict[str, Any] | None
) -> dict[str, Any]:
    return review_actions._guarded_result(action, before, backend=_review_backend())


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
    return review_actions.post_conversation_comment(
        repo,
        pr,
        body,
        dry_run,
        expected_worktree_fingerprint,
        head,
        request_key,
        request_fingerprint,
        reservation_file,
        owned_operation,
        reconcile_consumed,
        recovery_marker,
        backend=_review_backend(),
    )


def _verify_pr_head(repo: str, pr: int, expected_head: str) -> dict[str, Any]:
    return review_actions._verify_pr_head(
        repo, pr, expected_head, backend=_review_backend()
    )


def _request_target_comment(item: dict[str, Any], repo: str, pr: int) -> bool:
    return review_actions._request_target_comment(
        item, repo, pr, backend=_review_backend()
    )


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
    return review_actions.request_automated_review(
        repo,
        pr,
        provider,
        head,
        request_key,
        dry_run,
        expected_worktree_fingerprint,
        reservation_file,
        owned_operation,
        reconcile_consumed,
        recovery_marker,
        backend=_review_backend(),
    )


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
    return review_actions.reply_to_review_comment(
        repo,
        pr,
        head,
        comment_id,
        body,
        dry_run,
        expected_worktree_fingerprint,
        request_key,
        request_fingerprint,
        reservation_file,
        owned_operation,
        reconcile_consumed,
        recovery_marker,
        expected_thread_id,
        expected_thread_fingerprint,
        backend=_review_backend(),
    )


def _validate_reply_remote(
    repo: str, pr: int, head: str, receipt_value: object
) -> tuple[dict[str, Any], dict[str, Any]]:
    return review_actions._validate_reply_remote(
        repo, pr, head, receipt_value, backend=_review_backend()
    )


def _resolution_result_thread(payload: object) -> dict[str, Any]:
    return review_actions._resolution_result_thread(payload, backend=_review_backend())


def _prove_resolved_thread(
    thread: dict[str, Any], saved: dict[str, Any], *, mutation_may_have_applied: bool
) -> None:
    return review_actions._prove_resolved_thread(
        thread,
        saved,
        mutation_may_have_applied=mutation_may_have_applied,
        backend=_review_backend(),
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
    return review_actions.resolve_review_thread(
        repo,
        pr,
        head,
        reply_receipt,
        dry_run,
        expected_worktree_fingerprint,
        request_key,
        request_fingerprint,
        reservation_file,
        owned_operation,
        reconcile_consumed,
        recovery_marker,
        backend=_review_backend(),
    )


def edit_comment(
    repo: str,
    pr: int,
    comment_id: int,
    kind: str,
    body: ProviderText,
    dry_run: bool,
    expected_worktree_fingerprint: str | None,
) -> dict[str, Any]:
    return review_actions.edit_comment(
        repo,
        pr,
        comment_id,
        kind,
        body,
        dry_run,
        expected_worktree_fingerprint,
        backend=_review_backend(),
    )


def submit_review(
    repo: str,
    pr: int,
    event: str,
    body: ProviderText,
    dry_run: bool,
    expected_worktree_fingerprint: str | None,
) -> dict[str, Any]:
    return review_actions.submit_review(
        repo,
        pr,
        event,
        body,
        dry_run,
        expected_worktree_fingerprint,
        backend=_review_backend(),
    )


def _write_reservation(path_value: str, packet: dict[str, Any]) -> None:
    return review_operations._write_reservation(
        path_value, packet, backend=_review_backend()
    )


def prepare_reservation(args: argparse.Namespace) -> dict[str, Any]:
    return review_operations.prepare_reservation(args, backend=_review_backend())


def _read_json_object(path_value: str, name: str) -> dict[str, Any]:
    return review_operations._read_json_object(
        path_value, name, backend=_review_backend()
    )


def _write_json_object(path_value: str, value: dict[str, Any]) -> None:
    return review_operations._write_json_object(
        path_value, value, backend=_review_backend()
    )


def _operation_start_receipt(request: dict[str, Any]) -> dict[str, Any]:
    return review_operations._operation_start_receipt(
        request, backend=_review_backend()
    )


def _read_operation_start(identity: dict[str, Any]) -> dict[str, Any]:
    return review_operations._read_operation_start(identity, backend=_review_backend())


def _start_owned_operation(request: dict[str, Any]) -> dict[str, Any]:
    return review_operations._start_owned_operation(request, backend=_review_backend())


def _owned_operation_start(request: dict[str, Any], *, create: bool) -> dict[str, Any]:
    return review_operations._owned_operation_start(
        request, create=create, backend=_review_backend()
    )


def prepare_owned_operation(
    controller_file: str, input_file: str, output_file: str
) -> dict[str, Any]:
    return review_operations.prepare_owned_operation(
        controller_file, input_file, output_file, backend=_review_backend()
    )


def _operation_outcome(
    operation: str, facts: dict[str, Any], exit_code: int = 0
) -> tuple[str, str]:
    return review_operations._operation_outcome(
        operation, facts, exit_code, backend=_review_backend()
    )


def _mutation_artifact(
    action: dict[str, Any], receipt_value: dict[str, Any] | None = None
) -> dict[str, Any]:
    return review_operations._mutation_artifact(
        action, receipt_value, backend=_review_backend()
    )


def _normalize_owned_facts(
    request: dict[str, Any], raw: dict[str, Any], outcome: str
) -> dict[str, Any]:
    return review_operations._normalize_owned_facts(
        request, raw, outcome, backend=_review_backend()
    )


def _mutation_provider_state(exc: ReviewError) -> str:
    return review_operations._mutation_provider_state(exc, backend=_review_backend())


def execute_owned_operation(
    request_file: str, result_file: str, *, mode: str
) -> dict[str, Any]:
    return review_operations.execute_owned_operation(
        request_file, result_file, mode=mode, backend=_review_backend()
    )


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
        lines.append(
            f"[{entry['index']:>3}] {entry['type']} id={entry['comment_id']} author={entry['author'] or 'unknown'} updated={entry['updated']}"
        )
        lines.append(f"      {entry['body_preview'] or '(empty)'}")
        if entry["path"]:
            lines.append(
                f"      file={entry['path']} line={entry['line']} startLine={entry['start_line']} resolved={entry['is_resolved']} outdated={entry['is_outdated']}"
            )
    if not lines:
        lines.append("No comment context found.")
    if payload.get("actions"):
        lines.extend(["", "Reply actions:"])
        for action in payload["actions"]:
            lines.append(f"- comment {action['comment_id']}: {action['status']}")
    if payload.get("action"):
        action = payload["action"]
        lines.append(
            f"{action['status']}: review action for {payload['repo']}#{payload['pr']}"
        )
        if action.get("url"):
            lines.append(str(action["url"]))
        request = action.get("request") or {}
        if request.get("request_ref"):
            lines.append(str(request["request_ref"]))
    return "\n".join(lines) + "\n"


def doctor_payload() -> dict[str, object]:
    return shared_doctor()


def emit_success(data: object, command: list[str]) -> None:
    print(
        json.dumps(
            {"ok": True, "version": VERSION, "command": command, "data": data}, indent=2
        )
    )


def emit_error(exc: ReviewError, command: list[str]) -> None:
    error: dict[str, Any] = {"code": exc.code, "message": exc.message}
    if exc.details is not None:
        error["details"] = exc.details
    print(
        json.dumps(
            {"ok": False, "version": VERSION, "command": command, "error": error},
            indent=2,
        )
    )


def main(argv: list[str] | None = None) -> int:
    return review_cli.main(argv, backend=_review_backend())


if __name__ == "__main__":
    raise SystemExit(main())
