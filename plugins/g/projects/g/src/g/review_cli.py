from __future__ import annotations

import json
import sys
from typing import Any

from .common import GError
from .ready_review import ReadyReviewError
from .review_operation import OperationError
from .review_types import ReviewError


def main(argv: list[str] | None = None, *, backend: Any) -> int:
    parser = backend.build_parser()
    try:
        args = parser.parse_args(argv)
    except ReviewError as exc:
        raw = list(argv or [])
        if "--json" in raw:
            backend.emit_error(
                exc,
                [
                    next(
                        (
                            item
                            for item in raw
                            if item
                            in {
                                "address",
                                "comment",
                                "request",
                                "reply",
                                "resolve",
                                "edit-comment",
                                "submit-review",
                                "prepare",
                                "validate",
                                "check",
                                "wait",
                                "ready-check",
                                "ready-wait",
                                "ready-trigger",
                                "terminal-evidence",
                            }
                        ),
                        "",
                    )
                ],
            )
        else:
            print(exc.message, file=sys.stderr)
        return exc.exit_code
    if args.version:
        print(backend.VERSION)
        return 0
    if args.command == "doctor":
        payload = backend.doctor_payload()
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(backend.doctor_text(payload, f"g reviews {backend.VERSION}"))
        return 0 if payload["ok"] else 1
    if args.command == "validate":
        try:
            packet = backend._read_reservation_file(args.reservation_file)
        except ReviewError as exc:
            if args.json:
                backend.emit_error(exc, ["validate"])
            else:
                print(exc.message, file=sys.stderr)
            return exc.exit_code
        payload = {
            "reservation": packet,
            "packet_fingerprint": backend.packet_fingerprint(packet),
            "marker": None
            if packet["mutation_kind"] == "review-resolution"
            else backend.operation_marker(packet["operation_id"]),
        }
        if args.json:
            backend.emit_success(payload, ["validate"])
        else:
            print(json.dumps(payload, indent=2))
        return 0
    if args.command == "ready-trigger":
        try:
            trigger = backend.build_ready_trigger(
                provider=args.provider,
                repository=args.repo,
                pr_number=backend.positive_int(str(args.pr), "pr"),
                head_sha=backend.validate_full_head(args.head),
                ready_event_id=args.ready_event_id,
                ready_ref=args.ready_ref,
                ready_at=args.ready_at,
                base_branch=args.base_branch,
                body_fingerprint=args.body_fingerprint,
            )
            backend._write_json_object(args.output_file, trigger)
            payload = {"ready_trigger": trigger, "output_file": args.output_file}
        except (ReadyReviewError, ReviewError) as exc:
            error = (
                exc
                if isinstance(exc, ReviewError)
                else ReviewError(str(exc), code="ready_trigger_invalid", exit_code=64)
            )
            if args.json:
                backend.emit_error(error, ["ready-trigger"])
            else:
                print(error.message, file=sys.stderr)
            return error.exit_code
        if args.json:
            backend.emit_success(payload, ["ready-trigger"])
        else:
            print(json.dumps(payload, indent=2))
        return 0
    if args.command == "prepare":
        try:
            payload = backend.prepare_reservation(args)
        except ReviewError as exc:
            if args.json:
                backend.emit_error(exc, ["prepare"])
            else:
                print(exc.message, file=sys.stderr)
            return exc.exit_code
        if args.json:
            backend.emit_success(payload, ["prepare"])
        else:
            print(json.dumps(payload, indent=2))
        return 0
    if args.command == "operation":
        try:
            if args.operation_command == "prepare":
                payload = backend.prepare_owned_operation(
                    args.controller_envelope_file, args.input_file, args.request_output
                )
            elif args.operation_command == "validate-request":
                request = backend.validate_operation_request(
                    backend._read_json_object(args.request_file, "operation request")
                )
                payload = {
                    "request": request,
                    "validation_descriptor": backend.operation_validation_descriptor(
                        request
                    ),
                }
            elif args.operation_command == "validate-result":
                request = backend._read_json_object(
                    args.request_file, "operation request"
                )
                result = backend._read_json_object(args.result_file, "operation result")
                payload = {
                    "result": backend.validate_result_for_request(result, request),
                    "validation_descriptor": backend.operation_validation_descriptor(
                        request, result
                    ),
                }
            else:
                payload = backend.execute_owned_operation(
                    args.request_file, args.result_output, mode=args.operation_command
                )
        except (OperationError, ReviewError) as exc:
            error = (
                exc
                if isinstance(exc, ReviewError)
                else ReviewError(str(exc), code="owned_operation_invalid", exit_code=64)
            )
            if args.json:
                backend.emit_error(error, ["operation", args.operation_command])
            else:
                print(error.message, file=sys.stderr)
            return error.exit_code
        if args.json:
            backend.emit_success(payload, ["operation", args.operation_command])
        else:
            print(json.dumps(payload, indent=2))
        return 0
    if args.command not in {
        "address",
        "comment",
        "request",
        "reply",
        "resolve",
        "edit-comment",
        "submit-review",
        "check",
        "wait",
        "ready-check",
        "ready-wait",
        "terminal-evidence",
    }:
        parser.print_help()
        return 0
    try:
        pr = backend.positive_int(args.pr, "pr")
        repo = backend.resolve_repo(args.repo, allow_non_project=args.allow_non_project)
        if args.command in {
            "check",
            "wait",
            "ready-check",
            "ready-wait",
            "terminal-evidence",
        }:
            request_identity = None
            ready_identity = None
            if args.request_receipt_file:
                try:
                    receipt_text = backend.read_text_file(
                        args.request_receipt_file, field="request-receipt"
                    ).text
                    request_identity = json.loads(receipt_text)
                except (GError, json.JSONDecodeError, TypeError) as exc:
                    if isinstance(exc, GError):
                        raise backend._review_error(exc) from exc
                    raise ReviewError(
                        "The request receipt file must contain one JSON object.",
                        code="invalid_request",
                        exit_code=64,
                    ) from exc
                if not isinstance(request_identity, dict):
                    raise ReviewError(
                        "The request receipt file must contain one JSON object.",
                        code="invalid_request",
                        exit_code=64,
                    )
            ready_receipt_file = getattr(args, "ready_receipt_file", None)
            if ready_receipt_file:
                ready_identity = backend._read_json_object(
                    ready_receipt_file, "ready receipt"
                )
            if (
                args.command in {"wait", "terminal-evidence"}
                and request_identity is None
            ):
                raise ReviewError(
                    "The identity-bound automated review waiter requires --request-receipt-file.",
                    code="request_binding_required",
                    exit_code=64,
                )
            if args.command in {"ready-check", "ready-wait"} and ready_identity is None:
                raise ReviewError(
                    "The ready-triggered review operation requires --ready-receipt-file.",
                    code="ready_binding_required",
                    exit_code=64,
                )
            if (
                args.command in {"ready-check", "ready-wait"}
                and request_identity is not None
            ):
                raise ReviewError(
                    "A ready-triggered review operation cannot use a request receipt.",
                    code="ready_binding_conflict",
                    exit_code=64,
                )
            if args.command == "terminal-evidence":
                payload = backend.terminal_provider_evidence(
                    repo, pr, args.provider, args.head, request_identity
                )
                exit_code = 0
            elif args.command == "check":
                payload = backend.check_automated_review(
                    repo, pr, args.provider, args.head, request_identity
                )
                binding = str(payload.get("request_binding") or "unknown")
                if payload.get("review_state") == "stale":
                    exit_code = backend.REVIEW_EXIT_CODES["stale"]
                elif binding != "recognized":
                    status = payload.get("review_state")
                    exit_code = (
                        backend.REVIEW_EXIT_CODES[str(status)]
                        if binding == "absent" and status == "not-requested"
                        else backend.REQUEST_BINDING_EXIT_CODES.get(binding, 4)
                    )
                else:
                    exit_code = backend.REVIEW_EXIT_CODES[str(payload["review_state"])]
            elif args.command == "wait":
                timeout = backend.duration_seconds(args.timeout, "timeout")
                interval = backend.duration_seconds(args.interval, "interval")
                max_interval = backend.duration_seconds(
                    args.max_interval, "max-interval"
                )
                if interval > max_interval:
                    raise ReviewError(
                        "--interval cannot be greater than --max-interval.",
                        code="invalid_arguments",
                        exit_code=64,
                    )
                payload, exit_code = backend.wait_for_automated_review(
                    repo,
                    pr,
                    args.provider,
                    args.head,
                    timeout,
                    interval,
                    max_interval,
                    request_identity,
                )
            elif args.command == "ready-check":
                if not args.head:
                    raise ReviewError(
                        "ready-check requires --head.",
                        code="invalid_arguments",
                        exit_code=64,
                    )
                payload = backend.check_ready_automated_review(
                    repo,
                    pr,
                    args.provider,
                    backend.validate_full_head(args.head),
                    ready_identity,
                )
                exit_code = backend.REVIEW_EXIT_CODES.get(
                    str(payload["review_state"]), 4
                )
            else:
                if not args.head:
                    raise ReviewError(
                        "ready-wait requires --head.",
                        code="invalid_arguments",
                        exit_code=64,
                    )
                timeout = backend.duration_seconds(args.timeout, "timeout")
                interval = backend.duration_seconds(args.interval, "interval")
                max_interval = backend.duration_seconds(
                    args.max_interval, "max-interval"
                )
                if interval > max_interval:
                    raise ReviewError(
                        "--interval cannot be greater than --max-interval.",
                        code="invalid_arguments",
                        exit_code=64,
                    )
                payload, exit_code = backend.wait_for_ready_automated_review(
                    repo,
                    pr,
                    args.provider,
                    backend.validate_full_head(args.head),
                    timeout,
                    interval,
                    max_interval,
                    ready_identity,
                )
            if args.json:
                backend.emit_success(payload, [args.command])
            else:
                print(backend.render_text(payload), end="")
            return exit_code
        if args.command == "request":
            action = backend.request_automated_review(
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
                backend.emit_success(payload, ["request"])
            else:
                print(backend.render_text(payload), end="")
            return 0
        if args.command == "comment":
            try:
                body = backend.read_text_file(args.body_file, field="body")
            except GError as exc:
                raise backend._review_error(exc) from exc
            payload = {
                "repo": repo,
                "pr": pr,
                "action": backend.post_conversation_comment(
                    repo,
                    pr,
                    body,
                    args.dry_run,
                    args.expected_worktree_fingerprint,
                    args.head,
                    args.request_key,
                    args.request_fingerprint,
                    args.reservation_file,
                ),
            }
            if args.json:
                backend.emit_success(payload, ["comment"])
            else:
                print(backend.render_text(payload), end="")
            return 0
        if args.command == "resolve":
            try:
                receipt_text = backend.read_text_file(
                    args.reply_receipt_file, field="reply-receipt"
                ).text
                reply_receipt = json.loads(receipt_text)
            except (GError, json.JSONDecodeError, TypeError) as exc:
                if isinstance(exc, GError):
                    raise backend._review_error(exc) from exc
                raise ReviewError(
                    "The reply receipt file must contain one JSON object.",
                    code="reply_receipt_invalid",
                    exit_code=64,
                ) from exc
            action = backend.resolve_review_thread(
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
                backend.emit_success(payload, ["resolve"])
            else:
                print(json.dumps(payload, indent=2))
            return 0
        if args.command in {"reply", "edit-comment", "submit-review"}:
            try:
                body = backend.read_text_file(args.body_file, field="body")
            except GError as exc:
                raise backend._review_error(exc) from exc
            if args.command == "reply":
                comment_id = backend.positive_int(args.comment_id, "comment-id")
                action = backend.reply_to_review_comment(
                    repo,
                    pr,
                    args.head,
                    comment_id,
                    body,
                    args.dry_run,
                    args.expected_worktree_fingerprint,
                    args.request_key,
                    args.request_fingerprint,
                    args.reservation_file,
                )
            elif args.command == "edit-comment":
                comment_id = backend.positive_int(args.comment_id, "comment-id")
                action = backend.edit_comment(
                    repo,
                    pr,
                    comment_id,
                    args.kind,
                    body,
                    args.dry_run,
                    args.expected_worktree_fingerprint,
                )
            else:
                action = backend.submit_review(
                    repo,
                    pr,
                    args.event,
                    body,
                    args.dry_run,
                    args.expected_worktree_fingerprint,
                )
            payload = {"repo": repo, "pr": pr, "action": action}
            if args.json:
                backend.emit_success(payload, [args.command])
            else:
                print(json.dumps(payload, indent=2))
            return 0
        entries = backend.collect_entries(repo, pr, args.include_resolved)
        payload: dict[str, Any] = {"repo": repo, "pr": pr, "entries": entries}
        if args.json:
            backend.emit_success(payload, ["address"])
        else:
            print(backend.render_text(payload), end="")
        return 0
    except ReviewError as exc:
        if (
            args.command in {"check", "wait", "terminal-evidence"}
            and exc.code == "command_failed"
        ):
            exc = ReviewError(exc.message, code="api_error", exit_code=4)
        if args.json:
            backend.emit_error(exc, [args.command or ""])
        else:
            print(exc.message, file=sys.stderr)
        return exc.exit_code
