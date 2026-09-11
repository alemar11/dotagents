from __future__ import annotations

import hashlib
import json
from datetime import timezone
from typing import Any

from .common import GError
from .provider_text import API_VERSION, ProviderText, verify_response_text
from .review_mutation import operation_id_for_request
from .review_request import build_request, receipt, validate_full_head
from .review_thread import (
    build_reply_receipt,
    build_resolution_receipt,
    validate_reply_receipt,
)
from .review_types import ReviewError


def _review_error(exc: GError, *, backend: Any) -> ReviewError:
    return ReviewError(
        str(exc), code=exc.code, exit_code=exc.exit_code, details=exc.details
    )


def _api_object(endpoint: str, *, backend: Any) -> dict[str, Any]:
    payload = backend.gh_json(
        [
            "api",
            endpoint,
            "--method",
            "GET",
            "--header",
            "Accept: application/vnd.github+json",
            "--header",
            f"X-GitHub-Api-Version: {API_VERSION}",
        ]
    )
    if not isinstance(payload, dict):
        raise ReviewError(
            "GitHub read-back returned an unexpected response.",
            code="provider_response_invalid",
            exit_code=65,
        )
    return payload


def _viewer_login(*, backend: Any) -> str:
    payload = backend._api_object("user")
    login = payload.get("login")
    if not isinstance(login, str) or not login:
        raise ReviewError(
            "Could not resolve the authenticated GitHub identity.",
            code="provider_identity_missing",
            exit_code=65,
        )
    return login


def _verify_pr_target(repo: str, pr: int, *, backend: Any) -> dict[str, Any]:
    payload = backend._api_object(f"repos/{repo}/pulls/{pr}")
    if payload.get("number") != pr or not str(payload.get("url") or "").endswith(
        f"/repos/{repo}/pulls/{pr}"
    ):
        raise ReviewError(
            "GitHub pull-request read-back did not match the requested target.",
            code="provider_target_mismatch",
            exit_code=65,
        )
    return payload


def _in_creation_window(
    item: dict[str, Any], field: str, started_at: str, finished_at: str, *, backend: Any
) -> bool:
    timestamp = str(item.get(field) or "")
    return bool(timestamp and started_at <= timestamp <= finished_at)


def _proof(
    item: dict[str, Any],
    body: ProviderText,
    *,
    target: dict[str, Any],
    status: str,
    backend: Any,
) -> dict[str, Any]:
    verify_response_text(item, body)
    object_id = item.get("id")
    url = item.get("html_url")
    if not isinstance(object_id, int) or not isinstance(url, str) or (not url):
        raise GError(
            "GitHub response omitted provider object identity.",
            code="provider_identity_missing",
            exit_code=65,
        )
    return {
        "status": status,
        "id": object_id,
        "url": url,
        "target": target,
        "text": body.proof(),
    }


def _proof_failure(message: str, code: str, *, backend: Any) -> GError:
    return GError(message, code=code, exit_code=65)


def _item_login(item: dict[str, Any], *, backend: Any) -> str:
    user = item.get("user")
    return str(user.get("login") or "") if isinstance(user, dict) else ""


def _read_back_list(endpoint: str, *, backend: Any) -> list[dict[str, Any]]:
    try:
        return backend.gh_api_paginated_list(endpoint)
    except ReviewError as exc:
        raise GError(
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
    backend: Any,
) -> dict[str, Any]:
    """Find one exact marker-bound comment after a consumed reservation."""
    try:
        items = backend._read_back_list(endpoint)
    except (ReviewError, GError) as exc:
        raise backend._recovery_required(
            "The consumed comment could not be read back exactly; owner recovery is required.",
            code="provider_recovery_ambiguous",
            details={
                "read_back_code": getattr(exc, "code", "provider_read_back_failed")
            },
        ) from exc
    if endpoint.startswith(f"repos/{repo}/issues/"):
        target_field = "issue_url"
        target_suffix = f"/repos/{repo}/issues/{pr}"
    else:
        target_field = "pull_request_url"
        target_suffix = f"/repos/{repo}/pulls/{pr}"
    matches = [
        item
        for item in items
        if backend._item_login(item) == actor
        and str(item.get(target_field) or "").endswith(target_suffix)
        and backend.response_text_matches(item, body)
        and backend._marker_matches(str(item.get("body") or ""), packet["operation_id"])
        and (
            parent_comment_id is None or item.get("in_reply_to_id") == parent_comment_id
        )
        and (
            thread_comment_node_ids is None
            or (
                isinstance(item.get("node_id"), str)
                and item["node_id"] in thread_comment_node_ids
            )
        )
    ]
    if len(matches) != 1:
        raise backend._recovery_required(
            "The consumed comment did not map to one unique provider artifact; owner recovery is required.",
            code="provider_recovery_ambiguous",
            details={"matches": len(matches), "operation_id": packet["operation_id"]},
        )
    return matches[0]


def _guarded_result(
    action: dict[str, Any], before: dict[str, Any] | None, *, backend: Any
) -> dict[str, Any]:
    try:
        after = backend.verify_worktree_unchanged(before)
    except GError as exc:
        raise ReviewError(
            str(exc), code=exc.code, exit_code=exc.exit_code, details={"action": action}
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
    *,
    backend: Any,
) -> dict[str, Any]:
    packet = backend._require_reservation(
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
    body = backend._marked_body(body, packet)
    try:
        before = backend.require_worktree(expected_worktree_fingerprint)
    except GError as exc:
        raise backend._review_error(exc) from exc
    target = {"repo": repo, "pr": pr, "kind": "conversation-comment"}
    consumed_marker = backend._read_consumed_marker(
        packet,
        reservation_file or "",
        require_consumed=reconcile_consumed,
        marker_observer=recovery_marker,
    )
    if consumed_marker is not None and recovery_marker is not None:
        recovery_marker.update(consumed_marker)
    if consumed_marker is not None:
        actor = backend._viewer_login()
        item = backend._reconcile_consumed_comment(
            f"repos/{repo}/issues/{pr}/comments", repo, pr, actor, body, packet
        )
        return backend._with_consumed_marker(
            backend._guarded_result(
                backend._proof(item, body, target=target, status="recovered"), before
            ),
            consumed_marker,
        )
    if reconcile_consumed:
        raise ReviewError(
            "Mutation reconciliation cannot enter transport.",
            code="reservation_not_consumed",
            exit_code=4,
        )
    backend._verify_pr_head(repo, pr, packet["head_sha"])
    if dry_run:
        return {
            "status": "dry-run",
            "target": target,
            "text": body.proof(),
            "transport": {
                "method": "POST",
                "endpoint": f"repos/{repo}/issues/{pr}/comments",
                "api_version": API_VERSION,
            },
        }
    actor = backend._viewer_login()
    backend._consume_reservation(packet, reservation_file or "")
    started_at = (
        backend.datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
    result = backend.api_request(
        "POST", f"repos/{repo}/issues/{pr}/comments", {"body": body.text}
    )
    finished_at = (
        backend.datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )

    def prove(item: dict[str, Any]) -> dict[str, Any]:
        if (
            not str(item.get("issue_url") or "").endswith(f"/repos/{repo}/issues/{pr}")
            or backend._item_login(item) != actor
            or (
                not backend._marker_matches(
                    str(item.get("body") or ""), packet["operation_id"]
                )
            )
            or (
                not backend._in_creation_window(
                    item, "created_at", started_at, finished_at
                )
            )
        ):
            raise backend._proof_failure(
                "Comment response did not match the intended creation.",
                "provider_target_mismatch",
            )
        backend._proof(item, body, target=target, status="posted")
        return item

    def read_back() -> dict[str, Any]:
        matches = [
            item
            for item in backend._read_back_list(f"repos/{repo}/issues/{pr}/comments")
            if backend._item_login(item) == actor
            and backend.response_text_matches(item, body)
            and backend._marker_matches(
                str(item.get("body") or ""), packet["operation_id"]
            )
            and backend._in_creation_window(item, "created_at", started_at, finished_at)
            and str(item.get("issue_url") or "").endswith(f"/repos/{repo}/issues/{pr}")
        ]
        if len(matches) != 1:
            raise backend._proof_failure(
                "Comment read-back did not uniquely prove the creation.",
                "provider_read_back_not_unique",
            )
        return prove(matches[0])

    try:
        proof = backend.prove_mutation(
            result,
            prove_response=prove,
            read_back=read_back,
            target=target,
            text=body.proof(),
            ambiguous_message="Comment creation is unconfirmed after one exact-target read-back; do not retry blindly.",
        )
        status = "recovered" if proof.recovered else "posted"
        return backend._guarded_result(
            backend._proof(proof.value, body, target=target, status=status), before
        )
    except GError as exc:
        raise backend._review_error(exc) from exc


def _verify_pr_head(
    repo: str, pr: int, expected_head: str, *, backend: Any
) -> dict[str, Any]:
    pull = backend._verify_pr_target(repo, pr)
    actual = str((pull.get("head") or {}).get("sha") or "")
    try:
        actual = validate_full_head(actual)
    except ValueError as exc:
        raise ReviewError(
            "GitHub pull-request read-back omitted a full head SHA.",
            code="provider_target_mismatch",
            exit_code=65,
        ) from exc
    if actual != expected_head:
        raise ReviewError(
            "The pull-request head changed before the typed review request could be posted.",
            code="head_drift",
            exit_code=3,
            details={"expected_head": expected_head, "current_head": actual},
        )
    return pull


def _request_target_comment(
    item: dict[str, Any], repo: str, pr: int, *, backend: Any
) -> bool:
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
    *,
    backend: Any,
) -> dict[str, Any]:
    backend.is_provider_author(provider, "")
    try:
        plan = build_request(provider, repo, pr, head, request_key)
    except ValueError as exc:
        raise ReviewError(str(exc), code="invalid_request", exit_code=64) from exc
    packet = backend._require_reservation(
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
    consumed_marker = backend._read_consumed_marker(
        packet,
        reservation_file or "",
        require_consumed=reconcile_consumed,
        marker_observer=recovery_marker,
    )
    if consumed_marker is not None and recovery_marker is not None:
        recovery_marker.update(consumed_marker)
    if consumed_marker is not None:
        return backend._with_consumed_marker(
            backend._reconcile_consumed_request(repo, pr, plan, packet), consumed_marker
        )
    if reconcile_consumed:
        raise ReviewError(
            "Mutation reconciliation cannot enter transport.",
            code="reservation_not_consumed",
            exit_code=4,
        )
    backend._verify_pr_head(repo, pr, plan.head_sha)
    conversation = backend.gh_api_paginated_list(f"repos/{repo}/issues/{pr}/comments")
    conflict, exact = backend._request_conflicts(conversation, plan)
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
        actor = backend._viewer_login()
        owned = [item for item in exact if backend._item_login(item) == actor]
        if len(owned) != 1:
            raise backend._recovery_required(
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
            },
        }
    try:
        before = backend.require_worktree(expected_worktree_fingerprint)
    except GError as exc:
        raise backend._review_error(exc) from exc
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
            "transport": {
                "method": "POST",
                "endpoint": f"repos/{repo}/issues/{pr}/comments",
                "api_version": API_VERSION,
                "posted": False,
            },
        }
    actor = backend._viewer_login()
    backend._consume_reservation(packet, reservation_file or "")
    started_at = (
        backend.datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
    result = backend.api_request(
        "POST", f"repos/{repo}/issues/{pr}/comments", {"body": plan.body}
    )
    finished_at = (
        backend.datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )

    def prove(item: dict[str, Any]) -> dict[str, Any]:
        if (
            not backend._request_target_comment(item, repo, pr)
            or backend._item_login(item) != actor
            or (
                not backend._in_creation_window(
                    item, "created_at", started_at, finished_at
                )
            )
            or (not backend._comment_for_plan(item, plan))
        ):
            raise backend._proof_failure(
                "Typed request response did not match the intended creation.",
                "provider_target_mismatch",
            )
        backend._proof(item, body, target=target, status="posted")
        return item

    def read_back() -> dict[str, Any]:
        matches = [
            item
            for item in backend._read_back_list(f"repos/{repo}/issues/{pr}/comments")
            if backend._item_login(item) == actor
            and backend._request_target_comment(item, repo, pr)
            and backend._in_creation_window(item, "created_at", started_at, finished_at)
            and backend._comment_for_plan(item, plan)
        ]
        if len(matches) != 1:
            raise backend._proof_failure(
                "Typed request read-back did not uniquely prove the creation.",
                "provider_read_back_not_unique",
            )
        return prove(matches[0])

    try:
        proof = backend.prove_mutation(
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
            "transport": {
                "method": "POST",
                "endpoint": f"repos/{repo}/issues/{pr}/comments",
                "api_version": API_VERSION,
                "posted": True,
                "recovered": proof.recovered,
            },
        }
        return backend._guarded_result(action, before)
    except GError as exc:
        if exc.code == "provider_write_ambiguous":
            raise ReviewError(
                "The typed review request identity is unknown after one read-only recovery; do not retry or start the waiter.",
                code="request_unknown",
                exit_code=4,
                details=exc.details,
            ) from exc
        raise backend._review_error(exc) from exc


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
    *,
    backend: Any,
) -> dict[str, Any]:
    try:
        reply_head = validate_full_head(head)
    except ValueError as exc:
        raise ReviewError(str(exc), code="invalid_arguments", exit_code=64) from exc
    parent, thread, exact_thread_fingerprint, finding_head = (
        backend._reply_thread_identity(repo, pr, reply_head, comment_id)
    )
    if (
        expected_thread_id is not None
        and str(thread["thread_id"]) != expected_thread_id
    ):
        raise ReviewError(
            "Review thread differs from the owned request.",
            code="review_thread_mismatch",
            exit_code=4,
        )
    if (
        not reconcile_consumed
        and expected_thread_fingerprint is not None
        and (exact_thread_fingerprint != expected_thread_fingerprint)
    ):
        raise ReviewError(
            "Review thread fingerprint differs from the owned request.",
            code="review_thread_mismatch",
            exit_code=4,
        )
    reserved_thread_fingerprint = (
        expected_thread_fingerprint or exact_thread_fingerprint
    )
    packet = backend._require_reservation(
        reservation_file,
        kind="review-reply",
        repo=repo,
        pr=pr,
        head=reply_head,
        request_key=request_key,
        request_fingerprint=request_fingerprint,
        thread_id=str(thread["thread_id"]),
        thread_fingerprint=reserved_thread_fingerprint,
        finding_comment_id=comment_id,
        allow_thread_fingerprint_mismatch=True,
        body_fingerprint=body.sha256 if owned_operation is not None else None,
        owned_operation=owned_operation,
    )
    body = backend._marked_body(body, packet)
    try:
        before = backend.require_worktree(expected_worktree_fingerprint)
    except GError as exc:
        raise backend._review_error(exc) from exc
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
    consumed_marker = backend._read_consumed_marker(
        packet,
        reservation_file or "",
        require_consumed=reconcile_consumed,
        marker_observer=recovery_marker,
    )
    if consumed_marker is not None and recovery_marker is not None:
        recovery_marker.update(consumed_marker)
    if consumed_marker is not None:
        try:
            recovery_thread = backend._review_thread_context(str(packet["thread_id"]))
        except ReviewError as exc:
            raise backend._recovery_required(
                "The consumed review reply thread could not be read back exactly; owner recovery is required.",
                code="provider_recovery_ambiguous",
                details={"read_back_code": exc.code},
            ) from exc
        recovered_reply_node_id: str | None = None
        if (
            recovery_thread.get("thread_id") != packet["thread_id"]
            or recovery_thread.get("repository") != repo
            or recovery_thread.get("pr_number") != pr
            or (recovery_thread.get("head_sha") != packet["head_sha"])
        ):
            raise backend._recovery_required(
                "The consumed review reply thread changed; owner recovery is required.",
                code="provider_recovery_ambiguous",
            )
        thread_comment_node_ids = {
            str(item["id"])
            for item in recovery_thread.get("comments", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        actor = backend._viewer_login()
        item = backend._reconcile_consumed_comment(
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
            comment
            for comment in recovery_thread.get("comments", [])
            if not (
                isinstance(comment, dict)
                and (
                    comment.get("id") == recovered_reply_node_id
                    or comment.get("databaseId") == item.get("id")
                )
            )
        ]
        if len(original_comments) + 1 != len(recovery_thread.get("comments", [])):
            raise backend._recovery_required(
                "The consumed review reply was not the sole added thread comment; owner recovery is required.",
                code="provider_recovery_ambiguous",
            )
        original_thread = {**recovery_thread, "comments": original_comments}
        if (
            backend._exact_thread_fingerprint(original_thread, repo, pr, reply_head)
            != packet["thread_fingerprint"]
        ):
            raise backend._recovery_required(
                "The consumed review reply did not restore the reserved thread identity; owner recovery is required.",
                code="provider_recovery_ambiguous",
            )
        proof = backend._proof(item, body, target=target, status="recovered")
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
        return backend._with_consumed_marker(
            backend._guarded_result(proof, before), consumed_marker
        )
    if reconcile_consumed:
        raise ReviewError(
            "Mutation reconciliation cannot enter transport.",
            code="reservation_not_consumed",
            exit_code=4,
        )
    backend._verify_pr_head(repo, pr, reply_head)
    if (
        packet.get("thread_fingerprint") is not None
        and exact_thread_fingerprint != packet["thread_fingerprint"]
    ):
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
            "transport": {
                "method": "POST",
                "endpoint": endpoint,
                "api_version": API_VERSION,
            },
        }
    actor = backend._viewer_login()
    backend._consume_reservation(packet, reservation_file or "")
    started_at = (
        backend.datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
    result = backend.api_request("POST", endpoint, {"body": body.text})
    finished_at = (
        backend.datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )

    def prove(item: dict[str, Any]) -> dict[str, Any]:
        if (
            item.get("in_reply_to_id") != comment_id
            or not str(item.get("pull_request_url") or "").endswith(
                f"/repos/{repo}/pulls/{pr}"
            )
            or backend._item_login(item) != actor
            or (
                not backend._marker_matches(
                    str(item.get("body") or ""), packet["operation_id"]
                )
            )
            or (
                not backend._in_creation_window(
                    item, "created_at", started_at, finished_at
                )
            )
            or (not isinstance(item.get("node_id"), str))
        ):
            raise backend._proof_failure(
                "Review reply did not match the intended creation.",
                "provider_target_mismatch",
            )
        backend._proof(item, body, target=target, status="replied")
        return item

    def read_back() -> dict[str, Any]:
        matches = [
            item
            for item in backend._read_back_list(f"repos/{repo}/pulls/{pr}/comments")
            if item.get("in_reply_to_id") == comment_id
            and backend._item_login(item) == actor
            and backend.response_text_matches(item, body)
            and backend._marker_matches(
                str(item.get("body") or ""), packet["operation_id"]
            )
            and backend._in_creation_window(item, "created_at", started_at, finished_at)
            and str(item.get("pull_request_url") or "").endswith(
                f"/repos/{repo}/pulls/{pr}"
            )
        ]
        if len(matches) != 1:
            raise backend._proof_failure(
                "Review reply read-back did not uniquely prove the creation.",
                "provider_read_back_not_unique",
            )
        return prove(matches[0])

    try:
        proof = backend.prove_mutation(
            result,
            prove_response=prove,
            read_back=read_back,
            target=target,
            text=body.proof(),
            ambiguous_message="Review reply is unconfirmed after one exact-thread read-back; do not retry blindly.",
        )
        status = "recovered" if proof.recovered else "replied"
        action = backend._proof(proof.value, body, target=target, status=status)
        try:
            backend._verify_pr_head(repo, pr, reply_head)
        except ReviewError as exc:
            head_drift = exc.code == "head_drift"
            raise ReviewError(
                "The pull-request head moved after the review reply mutation; do not retry blindly."
                if head_drift
                else "The pull-request head could not be proven after the review reply mutation; do not retry blindly.",
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
        return backend._guarded_result(action, before)
    except GError as exc:
        raise backend._review_error(exc) from exc


def _validate_reply_remote(
    repo: str, pr: int, head: str, receipt_value: object, *, backend: Any
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        saved = validate_reply_receipt(receipt_value)
        expected_head = validate_full_head(head)
    except ValueError as exc:
        raise ReviewError(str(exc), code="reply_receipt_invalid", exit_code=64) from exc
    if (
        saved["repository"] != repo
        or saved["pr_number"] != pr
        or saved["reply_head_sha"] != expected_head
    ):
        raise ReviewError(
            "Reply receipt does not match the exact resolution target.",
            code="review_thread_mismatch",
            exit_code=4,
        )
    backend._verify_pr_head(repo, pr, expected_head)
    finding = backend._api_object(
        f"repos/{repo}/pulls/comments/{saved['finding_comment_id']}"
    )
    reply = backend._api_object(
        f"repos/{repo}/pulls/comments/{saved['reply_comment_id']}"
    )
    if (
        finding.get("id") != saved["finding_comment_id"]
        or finding.get("node_id") != saved["finding_node_id"]
        or finding.get("html_url") != saved["finding_ref"]
        or (finding.get("created_at") != saved["finding_created_at"])
        or (finding.get("commit_id") != saved["finding_head_sha"])
        or (finding.get("in_reply_to_id") is not None)
        or (
            not str(finding.get("pull_request_url") or "").endswith(
                f"/repos/{repo}/pulls/{pr}"
            )
        )
    ):
        raise ReviewError(
            "Review finding no longer matches its reply receipt.",
            code="evidence_reply_mismatch",
            exit_code=4,
        )
    try:
        reply_bytes = str(reply.get("body") or "").encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ReviewError(
            "Evidence reply body cannot be verified as UTF-8.",
            code="evidence_reply_mismatch",
            exit_code=4,
        ) from exc
    if (
        reply.get("id") != saved["reply_comment_id"]
        or reply.get("node_id") != saved["reply_node_id"]
        or reply.get("in_reply_to_id") != saved["finding_comment_id"]
        or (backend._item_login(reply) != saved["reply_author"])
        or (reply.get("html_url") != saved["reply_ref"])
        or (reply.get("created_at") != saved["reply_created_at"])
        or (hashlib.sha256(reply_bytes).hexdigest() != saved["body_fingerprint"])
        or (
            not str(reply.get("pull_request_url") or "").endswith(
                f"/repos/{repo}/pulls/{pr}"
            )
        )
    ):
        raise ReviewError(
            "Evidence reply no longer matches its immutable receipt.",
            code="evidence_reply_mismatch",
            exit_code=4,
        )
    thread = backend._review_thread_context(saved["thread_id"])
    if (
        thread["repository"] != repo
        or thread["pr_number"] != pr
        or thread["head_sha"] != expected_head
    ):
        raise ReviewError(
            "Review thread does not match the exact repository, PR, and head.",
            code="review_thread_mismatch",
            exit_code=4,
        )
    if thread["is_outdated"]:
        raise ReviewError(
            "Outdated review threads are not eligible for typed resolution.",
            code="review_thread_outdated",
            exit_code=4,
        )
    node_ids = {item.get("id") for item in thread["comments"]}
    if (
        saved["finding_node_id"] not in node_ids
        or saved["reply_node_id"] not in node_ids
    ):
        raise ReviewError(
            "Finding and evidence reply are not members of the exact thread.",
            code="evidence_reply_not_found",
            exit_code=4,
        )
    return (saved, thread)


def _resolution_result_thread(payload: object, *, backend: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("errors"):
        raise ReviewError(
            "Review-thread mutation returned GraphQL errors.",
            code="provider_response_invalid",
            exit_code=65,
        )
    thread = ((payload.get("data") or {}).get("resolveReviewThread") or {}).get(
        "thread"
    )
    if not isinstance(thread, dict):
        raise ReviewError(
            "Review-thread mutation omitted its target.",
            code="provider_response_invalid",
            exit_code=65,
        )
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
    backend: Any,
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
        or (thread.get("pr_state") != "open")
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
    *,
    backend: Any,
) -> dict[str, Any]:
    saved, thread = backend._validate_reply_remote(repo, pr, head, reply_receipt)
    expected_head = validate_full_head(head)
    exact_thread_fingerprint = backend._exact_thread_fingerprint(
        thread, repo, pr, expected_head
    )
    packet = backend._require_reservation(
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
        before = backend.require_worktree(expected_worktree_fingerprint)
    except GError as exc:
        raise backend._review_error(exc) from exc
    target = {
        "repo": repo,
        "pr": pr,
        "head": saved["reply_head_sha"],
        "kind": "review-thread",
        "thread_id": saved["thread_id"],
        "finding_comment_id": saved["finding_comment_id"],
    }
    observed_at = (
        backend.datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
    consumed_marker = backend._read_consumed_marker(
        packet,
        reservation_file or "",
        require_consumed=reconcile_consumed,
        marker_observer=recovery_marker,
    )
    if consumed_marker is not None and recovery_marker is not None:
        recovery_marker.update(consumed_marker)
    if consumed_marker is not None:
        try:
            recovery_thread = backend._review_thread_context(str(packet["thread_id"]))
            if (
                backend._exact_thread_fingerprint(
                    recovery_thread, repo, pr, expected_head
                )
                != packet["thread_fingerprint"]
            ):
                raise ReviewError(
                    "The consumed review-thread identity changed.",
                    code="review_thread_mismatch",
                    exit_code=4,
                )
            backend._prove_resolved_thread(
                recovery_thread, saved, mutation_may_have_applied=True
            )
        except ReviewError as exc:
            raise backend._recovery_required(
                "The consumed review-thread resolution could not be proven exactly; owner recovery is required.",
                code=exc.code,
                details=exc.details,
            ) from exc
        receipt_value = build_resolution_receipt(
            saved, status="recovered", observed_at=observed_at
        )
        return backend._with_consumed_marker(
            backend._guarded_result(
                {
                    "status": "recovered",
                    "target": target,
                    "resolution": receipt_value,
                    "mutation_attempted": True,
                    "mutation_may_have_applied": True,
                    "transport": {
                        "method": "POST",
                        "endpoint": "graphql:resolveReviewThread",
                        "recovered": True,
                    },
                },
                before,
            ),
            consumed_marker,
        )
    if reconcile_consumed:
        raise ReviewError(
            "Mutation reconciliation cannot enter transport.",
            code="reservation_not_consumed",
            exit_code=4,
        )
    if thread["is_resolved"]:
        receipt_value = build_resolution_receipt(
            saved, status="already-resolved", observed_at=observed_at
        )
        return backend._guarded_result(
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
        raise ReviewError(
            "Authenticated viewer cannot resolve the exact review thread.",
            code="review_thread_not_resolvable",
            exit_code=4,
        )
    if dry_run:
        return backend._guarded_result(
            {
                "status": "dry-run",
                "target": target,
                "reply_identity_fingerprint": saved["identity_fingerprint"],
                "mutation_attempted": False,
                "mutation_may_have_applied": False,
            },
            before,
        )
    mutation = "\nmutation($threadId: ID!) {\n  resolveReviewThread(input: {threadId: $threadId}) {\n    thread {\n      id\n      isResolved\n      isOutdated\n      viewerCanResolve\n      repository { nameWithOwner }\n      pullRequest { number state headRefOid }\n    }\n  }\n}\n".strip()
    backend._consume_reservation(packet, reservation_file or "")
    result = backend.graphql_request(mutation, {"threadId": saved["thread_id"]})
    response_proven = False
    response_failure = "provider_write_unconfirmed"
    response_mismatch: ReviewError | None = None
    if result.returncode == 0:
        try:
            response_thread = backend._resolution_result_thread(
                json.loads(result.stdout)
            )
            backend._prove_resolved_thread(
                response_thread, saved, mutation_may_have_applied=True
            )
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
        read_back_thread = backend._review_thread_context(saved["thread_id"])
        backend._prove_resolved_thread(
            read_back_thread, saved, mutation_may_have_applied=True
        )
    except ReviewError as exc:
        read_back_error = exc
    uncertainty = {
        "mutation_attempted": True,
        "mutation_may_have_applied": True,
        "response": {
            "code": response_failure,
            "transport_exit_code": result.returncode,
        },
        "read_back": {
            "code": read_back_error.code if read_back_error else "exact_state_proven"
        },
    }
    if response_mismatch is not None:
        raise ReviewError(
            response_mismatch.message,
            code=response_mismatch.code,
            exit_code=response_mismatch.exit_code,
            details=uncertainty,
        ) from response_mismatch
    if read_back_error is not None:
        if read_back_error.code in {
            "resolution_head_drift",
            "review_thread_mismatch",
            "resolution_unknown",
        }:
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
    observed_at = (
        backend.datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
    receipt_value = build_resolution_receipt(
        saved, status=status, observed_at=observed_at
    )
    action = {
        "status": status,
        "target": target,
        "resolution": receipt_value,
        "mutation_attempted": True,
        "mutation_may_have_applied": False,
        "transport": {"method": "POST", "endpoint": "graphql:resolveReviewThread"},
    }
    return backend._guarded_result(action, before)


def edit_comment(
    repo: str,
    pr: int,
    comment_id: int,
    kind: str,
    body: ProviderText,
    dry_run: bool,
    expected_worktree_fingerprint: str | None,
    *,
    backend: Any,
) -> dict[str, Any]:
    namespace = "issues/comments" if kind == "conversation" else "pulls/comments"
    endpoint = f"repos/{repo}/{namespace}/{comment_id}"
    current = backend._api_object(endpoint)
    target_url = (
        current.get("issue_url")
        if kind == "conversation"
        else current.get("pull_request_url")
    )
    target_noun = "issues" if kind == "conversation" else "pulls"
    if not str(target_url or "").endswith(f"/repos/{repo}/{target_noun}/{pr}"):
        raise ReviewError(
            "Comment does not belong to the requested PR.",
            code="provider_target_mismatch",
            exit_code=65,
        )
    target = {
        "repo": repo,
        "pr": pr,
        "kind": f"{kind}-comment",
        "comment_id": comment_id,
    }
    try:
        before = backend.require_worktree(expected_worktree_fingerprint)
    except GError as exc:
        raise backend._review_error(exc) from exc
    if backend.response_text_matches(current, body):
        try:
            return backend._guarded_result(
                backend._proof(current, body, target=target, status="reused"), before
            )
        except GError as exc:
            raise backend._review_error(exc) from exc
    if dry_run:
        return {
            "status": "dry-run",
            "target": target,
            "text": body.proof(),
            "transport": {
                "method": "PATCH",
                "endpoint": endpoint,
                "api_version": API_VERSION,
            },
        }
    actor = backend._viewer_login()
    if backend._item_login(current) != actor:
        raise ReviewError(
            "Authenticated identity does not own the requested comment.",
            code="provider_identity_mismatch",
            exit_code=65,
        )
    result = backend.api_request("PATCH", endpoint, {"body": body.text})

    def prove(item: dict[str, Any]) -> dict[str, Any]:
        item_target_url = (
            item.get("issue_url")
            if kind == "conversation"
            else item.get("pull_request_url")
        )
        if (
            item.get("id") != comment_id
            or not str(item_target_url or "").endswith(
                f"/repos/{repo}/{target_noun}/{pr}"
            )
            or backend._item_login(item) != actor
        ):
            raise backend._proof_failure(
                "Comment edit did not match the intended object.",
                "provider_target_mismatch",
            )
        backend._proof(item, body, target=target, status="edited")
        return item

    def read_back() -> dict[str, Any]:
        try:
            item = backend._api_object(endpoint)
        except ReviewError as exc:
            raise backend._proof_failure(
                "Comment edit read-back failed.", exc.code
            ) from exc
        return prove(item)

    try:
        proof = backend.prove_mutation(
            result,
            prove_response=prove,
            read_back=read_back,
            target=target,
            text=body.proof(),
            ambiguous_message="Comment edit is unconfirmed after one exact-object read-back; do not retry blindly.",
        )
        status = "recovered" if proof.recovered else "edited"
        return backend._guarded_result(
            backend._proof(proof.value, body, target=target, status=status), before
        )
    except GError as exc:
        raise backend._review_error(exc) from exc


def submit_review(
    repo: str,
    pr: int,
    event: str,
    body: ProviderText,
    dry_run: bool,
    expected_worktree_fingerprint: str | None,
    *,
    backend: Any,
) -> dict[str, Any]:
    pr_payload = backend._verify_pr_target(repo, pr)
    try:
        before = backend.require_worktree(expected_worktree_fingerprint)
    except GError as exc:
        raise backend._review_error(exc) from exc
    provider_event = {
        "approve": "APPROVE",
        "request-changes": "REQUEST_CHANGES",
        "comment": "COMMENT",
    }[event]
    expected_state = {
        "approve": "APPROVED",
        "request-changes": "CHANGES_REQUESTED",
        "comment": "COMMENTED",
    }[event]
    target = {
        "repo": repo,
        "pr": pr,
        "kind": "review",
        "head": str((pr_payload.get("head") or {}).get("sha") or ""),
        "event": event,
    }
    endpoint = f"repos/{repo}/pulls/{pr}/reviews"
    if dry_run:
        return {
            "status": "dry-run",
            "target": target,
            "text": body.proof(),
            "transport": {
                "method": "POST",
                "endpoint": endpoint,
                "api_version": API_VERSION,
            },
        }
    actor = backend._viewer_login()
    started_at = (
        backend.datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
    result = backend.api_request(
        "POST", endpoint, {"body": body.text, "event": provider_event}
    )
    finished_at = (
        backend.datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )

    def prove(item: dict[str, Any]) -> dict[str, Any]:
        if (
            backend._item_login(item) != actor
            or item.get("state") != expected_state
            or (
                not str(item.get("pull_request_url") or "").endswith(
                    f"/repos/{repo}/pulls/{pr}"
                )
            )
            or (str(item.get("commit_id") or "") != target["head"])
            or (
                not backend._in_creation_window(
                    item, "submitted_at", started_at, finished_at
                )
            )
        ):
            raise backend._proof_failure(
                "Review did not match the intended target and event.",
                "provider_target_mismatch",
            )
        backend._proof(item, body, target=target, status="submitted")
        return item

    def read_back() -> dict[str, Any]:
        matches = [
            item
            for item in backend._read_back_list(endpoint)
            if backend._item_login(item) == actor
            and item.get("state") == expected_state
            and backend.response_text_matches(item, body)
            and (str(item.get("commit_id") or "") == target["head"])
            and backend._in_creation_window(
                item, "submitted_at", started_at, finished_at
            )
            and str(item.get("pull_request_url") or "").endswith(
                f"/repos/{repo}/pulls/{pr}"
            )
        ]
        if len(matches) != 1:
            raise backend._proof_failure(
                "Review read-back did not uniquely prove the submission.",
                "provider_read_back_not_unique",
            )
        return prove(matches[0])

    try:
        proof = backend.prove_mutation(
            result,
            prove_response=prove,
            read_back=read_back,
            target=target,
            text=body.proof(),
            ambiguous_message="Review submission is unconfirmed after one exact-target read-back; do not retry blindly.",
        )
        status = "recovered" if proof.recovered else "submitted"
        return backend._guarded_result(
            backend._proof(proof.value, body, target=target, status=status), before
        )
    except GError as exc:
        raise backend._review_error(exc) from exc
