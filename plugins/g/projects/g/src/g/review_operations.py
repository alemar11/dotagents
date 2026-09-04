from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
from datetime import timezone
from pathlib import Path
from typing import Any

from .common import GError
from .review_mutation import (
    add_operation_marker,
    build_reservation,
    operation_id_for_mutation,
    operation_id_for_request,
    operation_marker,
    packet_fingerprint,
    text_fingerprint,
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
from .review_request import build_request, validate_full_head
from .review_thread import validate_reply_receipt
from .review_types import ReviewError


def _write_reservation(
    path_value: str, packet: dict[str, Any], *, backend: Any
) -> None:
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
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 384)
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise ReviewError(
            "The reservation packet could not be written atomically.",
            code="reservation_output_failed",
            exit_code=4,
        ) from exc


def prepare_reservation(args: argparse.Namespace, *, backend: Any) -> dict[str, Any]:
    repo = backend.resolve_repo(args.repo, allow_non_project=args.allow_non_project)
    pr = backend.positive_int(args.pr, "pr")
    head = validate_full_head(args.head)
    request_key = args.request_key
    request_fp = args.request_fingerprint
    thread_id = args.thread_id
    thread_fp = args.thread_fingerprint
    finding_id = (
        backend.positive_int(args.finding_comment_id, "finding-comment-id")
        if args.finding_comment_id
        else None
    )
    body_fp: str | None = None
    reply_fp: str | None = None
    operation_id: str
    if args.mutation_kind == "review-request":
        if not request_key:
            raise ReviewError(
                "review-request preparation requires --request-key.",
                code="invalid_arguments",
                exit_code=64,
            )
        plan = build_request("codex", repo, pr, head, request_key)
        request_fp = plan.request_fingerprint
        body_fp = plan.body_fingerprint
        operation_id = operation_id_for_request(
            repo, pr, head, plan.request_key, plan.request_fingerprint
        )
    elif args.mutation_kind in {"review-warning", "review-reply"}:
        if not request_key or not request_fp or (not args.body_file):
            raise ReviewError(
                "comment reservations require request identity and --body-file.",
                code="invalid_arguments",
                exit_code=64,
            )
        try:
            source_body = backend.read_text_file(args.body_file, field="body")
        except GError as exc:
            raise backend._review_error(exc) from exc
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
        if args.mutation_kind == "review-reply" and (
            thread_id is None or thread_fp is None or finding_id is None
        ):
            raise ReviewError(
                "review-reply preparation requires exact thread and finding identity.",
                code="invalid_arguments",
                exit_code=64,
            )
    else:
        if not request_key or not request_fp or (not args.reply_receipt_file):
            raise ReviewError(
                "review-resolution preparation requires request identity and --reply-receipt-file.",
                code="invalid_arguments",
                exit_code=64,
            )
        try:
            receipt_value = json.loads(
                backend.read_text_file(
                    args.reply_receipt_file, field="reply-receipt"
                ).text
            )
            saved = validate_reply_receipt(receipt_value)
        except (GError, json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ReviewError(
                "The reply receipt cannot be used to prepare a resolution reservation.",
                code="reply_receipt_invalid",
                exit_code=64,
            ) from exc
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
        backend._write_reservation(args.output_file, packet)
    return {
        "reservation": packet,
        "packet_fingerprint": packet_fingerprint(packet),
        "marker": None
        if args.mutation_kind == "review-resolution"
        else operation_marker(packet["operation_id"]),
        "output_file": args.output_file,
    }


def _read_json_object(path_value: str, name: str, *, backend: Any) -> dict[str, Any]:
    path = Path(path_value)
    if not path.is_absolute() or path.is_symlink() or (not path.is_file()):
        raise ReviewError(
            f"The {name} must be an absolute regular non-symlinked file.",
            code="invalid_arguments",
            exit_code=64,
        )
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReviewError(
            f"The {name} must contain one JSON object.",
            code="invalid_arguments",
            exit_code=64,
        ) from exc
    if not isinstance(value, dict):
        raise ReviewError(
            f"The {name} must contain one JSON object.",
            code="invalid_arguments",
            exit_code=64,
        )
    return value


def _write_json_object(path_value: str, value: dict[str, Any], *, backend: Any) -> None:
    path = Path(path_value)
    if not path.is_absolute() or path.is_symlink():
        raise ReviewError(
            "Operation output paths must be absolute and non-symlinked.",
            code="invalid_arguments",
            exit_code=64,
        )
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _operation_start_receipt(
    request: dict[str, Any], *, backend: Any
) -> dict[str, Any]:
    authority = request["authority"]
    value = {
        "schema": "g-review-operation-start:v1",
        "owner": "g",
        "operation": request["operation"],
        "operation_id": request["operation_id"],
        "request_fingerprint": request["request_fingerprint"],
        "journal_id": hashlib.sha256(
            json.dumps(
                {
                    "owner": "g",
                    "operation": request["operation"],
                    "operation_id": request["operation_id"],
                    "request_fingerprint": request["request_fingerprint"],
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest(),
        "started_generation": authority["expected_generation"] + 1,
        "started_state_fingerprint": authority["expected_state_fingerprint"],
        "receipt_fingerprint": "0" * 64,
    }
    value["receipt_fingerprint"] = hashlib.sha256(
        json.dumps(
            {key: item for key, item in value.items() if key != "receipt_fingerprint"},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()
    return validate_start_receipt(value, request)


def _read_operation_start(identity: dict[str, Any], *, backend: Any) -> dict[str, Any]:
    root = backend._operation_journal_root()
    if not root.exists() or root.is_symlink() or (not root.is_dir()):
        raise ReviewError(
            "The exact G operation start journal is absent or unsafe.",
            code="owned_operation_start_missing",
            exit_code=4,
        )
    path = root / f"{identity['operation_id']}.started.json"
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise OSError("operation start journal is not regular")
            value = json.loads(os.read(fd, 1048577).decode("utf-8"))
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
            "The exact G operation start journal is absent.",
            code="owned_operation_start_missing",
            exit_code=4,
        ) from exc
    except (OSError, UnicodeError, json.JSONDecodeError, OperationError) as exc:
        raise ReviewError(
            "The G operation start journal is invalid or conflicting.",
            code="owned_operation_start_invalid",
            exit_code=4,
        ) from exc


def _start_owned_operation(request: dict[str, Any], *, backend: Any) -> dict[str, Any]:
    receipt_value = backend._operation_start_receipt(request)
    root = backend._operation_journal_root()
    try:
        if root.exists() and (root.is_symlink() or not root.is_dir()):
            raise OSError("operation journal root is unsafe")
        root.mkdir(parents=True, exist_ok=True)
        if root.is_symlink() or not root.is_dir():
            raise OSError("operation journal root is unsafe")
        path = root / f"{request['operation_id']}.started.json"
        encoded = (
            json.dumps(receipt_value, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("utf-8")
        fd = os.open(
            path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0),
            384,
        )
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        directory_fd = os.open(
            root,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return receipt_value
    except FileExistsError as exc:
        existing = backend._read_operation_start(
            {
                "operation": request["operation"],
                "operation_id": request["operation_id"],
                "request_fingerprint": request["request_fingerprint"],
                "start_receipt_fingerprint": receipt_value["receipt_fingerprint"],
            }
        )
        raise ReviewError(
            "This G operation already started; resume or reconcile it without retrying.",
            code="owned_operation_already_started",
            exit_code=4,
            details={"start_receipt_fingerprint": existing["receipt_fingerprint"]},
        ) from exc
    except OSError as exc:
        raise ReviewError(
            "The G operation could not be durably started.",
            code="owned_operation_start_failed",
            exit_code=4,
        ) from exc


def _owned_operation_start(
    request: dict[str, Any], *, create: bool, backend: Any
) -> dict[str, Any]:
    if create:
        return backend._start_owned_operation(request)
    descriptor = operation_validation_descriptor(request)
    identity = descriptor["start_identity"]
    try:
        return backend._read_operation_start(identity)
    except ReviewError as exc:
        if (
            request["operation"] == "reconcile-mutation"
            and exc.code == "owned_operation_start_missing"
        ):
            started = request["input"]["started_operation"]
            return validate_start_receipt(started["start_receipt"], started["request"])
        raise


def prepare_owned_operation(
    controller_file: str, input_file: str, output_file: str, *, backend: Any
) -> dict[str, Any]:
    controller = backend._read_json_object(controller_file, "controller envelope")
    supplied = backend._read_json_object(input_file, "operation input")
    if set(supplied) != {"target", "input"}:
        raise ReviewError(
            "Operation input must contain exactly target and input.",
            code="invalid_arguments",
            exit_code=64,
        )
    descriptor = (controller.get("packet_template") or {}).get("operation") or {}
    operation = str(descriptor.get("name") or "")
    input_value = supplied["input"]
    if isinstance(input_value, dict):
        input_value = dict(input_value)
        for prior_field in (
            "prior_pending_result",
            "prior_findings_result",
            "prior_reply_result",
            "prior_failed_result",
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
                    code="owned_operation_invalid",
                    exit_code=64,
                ) from exc
            input_value[prior_field] = prior_result
    if operation == "reply":
        expected_fields = {
            "request_receipt",
            "prior_findings_result",
            "followup_obligation",
            "finding_comment_id",
            "body_file",
            "body_fingerprint",
        }
        if not isinstance(input_value, dict) or set(input_value) != expected_fields:
            raise ReviewError(
                "Reply prepare input must omit owner-derived thread identity.",
                code="invalid_arguments",
                exit_code=64,
            )
        try:
            target = validate_operation_target(supplied["target"])
        except OperationError as exc:
            raise ReviewError(
                str(exc), code="owned_operation_invalid", exit_code=64
            ) from exc
        finding_comment_id = input_value["finding_comment_id"]
        if not isinstance(finding_comment_id, int) or isinstance(
            finding_comment_id, bool
        ):
            raise ReviewError(
                "Reply finding_comment_id is invalid.",
                code="invalid_arguments",
                exit_code=64,
            )
        _, thread, thread_fingerprint, _ = backend._reply_thread_identity(
            target["repository"],
            target["pr_number"],
            target["head_sha"],
            finding_comment_id,
        )
        input_value = {
            **input_value,
            "thread_id": str(thread["thread_id"]),
            "thread_fingerprint": thread_fingerprint,
        }
    try:
        request = build_operation_request(
            operation=operation,
            controller_envelope=controller,
            target=supplied["target"],
            input_value=input_value,
        )
    except OperationError as exc:
        raise ReviewError(
            str(exc), code="owned_operation_invalid", exit_code=64
        ) from exc
    backend._write_json_object(output_file, request)
    return {
        "request_file": output_file,
        "request_fingerprint": request["request_fingerprint"],
        "operation_id": request["operation_id"],
        "operation": request["operation"],
    }


def _operation_outcome(
    operation: str, facts: dict[str, Any], exit_code: int = 0, *, backend: Any
) -> tuple[str, str]:
    if operation == "request":
        return (
            "completed",
            "recognized-existing" if facts.get("status") == "reused" else "created",
        )
    if operation == "wait":
        binding = facts.get("request_binding")
        state = facts.get("review_state")
        if binding != "recognized":
            return ("failed", "request-correlation-failure")
        if state == "clean":
            return ("completed", "clean")
        if state == "findings":
            return ("completed", "findings")
        if exit_code == 124:
            return ("completed", "pending-at-deadline")
        return ("failed", "provider-failure")
    if operation in {"ready-check", "ready-wait"}:
        state = facts.get("review_state")
        if state == "clean":
            return ("completed", "clean")
        if state == "findings":
            return ("completed", "findings")
        if state == "pending":
            return (
                "completed",
                "pending-at-deadline"
                if operation == "ready-wait" and exit_code == 124
                else "pending",
            )
        if state == "stale":
            return ("failed", "stale")
        if state == "ambiguous":
            return ("ambiguous", "ambiguous")
        return ("failed", "provider-failure")
    if operation == "warning":
        return (
            "completed",
            "recognized-existing" if facts.get("status") == "recovered" else "posted",
        )
    if operation == "reply":
        return (
            "completed",
            "recognized-existing" if facts.get("status") == "recovered" else "posted",
        )
    if operation == "resolve":
        return (
            "completed",
            "already-resolved"
            if facts.get("status") == "already-resolved"
            else "resolved",
        )
    if operation == "reconcile-terminal":
        return (
            "completed",
            "clean-verified"
            if facts.get("outcome") == "clean"
            else "findings-verified",
        )
    if operation == "reconcile-mutation":
        states = (facts.get("marker_state"), facts.get("provider_artifact_state"))
        if states == ("exact", "unique"):
            return ("completed", "completed-from-readback")
        if states in {("absent", "missing"), ("exact", "missing")}:
            return ("blocked", "missing")
        if states in {("conflicting", "missing"), ("exact", "conflicting")}:
            return ("ambiguous", "conflicting")
        return ("ambiguous", "ambiguous")
    raise ReviewError(
        "Unsupported owned operation outcome.",
        code="owned_operation_result_invalid",
        exit_code=4,
    )


def _mutation_artifact(
    action: dict[str, Any], receipt_value: dict[str, Any] | None = None, *, backend: Any
) -> dict[str, Any]:
    source = receipt_value or action
    object_id = (
        source.get("comment_id")
        or source.get("reply_comment_id")
        or source.get("object_id")
    )
    object_url = (
        source.get("request_ref")
        or source.get("reply_ref")
        or source.get("url")
        or source.get("object_url")
    )
    actor = source.get("actor") or source.get("reply_author") or source.get("author")
    body_fp = source.get("body_fingerprint") or (action.get("text") or {}).get("sha256")
    return {
        "status": str(action.get("status") or "posted"),
        "object_id": int(object_id),
        "object_url": str(object_url),
        "actor": str(actor),
        "body_fingerprint": str(body_fp),
    }


def _normalize_owned_facts(
    request: dict[str, Any], raw: dict[str, Any], outcome: str, *, backend: Any
) -> dict[str, Any]:
    operation, target, supplied = (
        request["operation"],
        request["target"],
        request["input"],
    )
    if operation == "request":
        receipt_value = raw["request"]
        return {
            "repository": target["repository"],
            "pr_number": target["pr_number"],
            "head_sha": target["head_sha"],
            "provider": target["provider"],
            "request_receipt": receipt_value,
            "mutation": backend._mutation_artifact(raw, receipt_value),
        }
    if operation == "wait":
        state = raw.get("review_state")
        provider_state = (
            state
            if state in {"clean", "findings"}
            else "pending"
            if outcome == "pending-at-deadline"
            else "failed"
        )
        evidence = raw.get("evidence") or {}
        kind = (
            evidence.get("kind")
            if evidence.get("kind")
            in {"formal-review", "provider-comment", "clean-reaction"}
            else "none"
        )
        artifact = {
            "kind": kind,
            "object_id": evidence.get("object_id") if kind != "none" else None,
            "object_url": evidence.get("object_url") if kind != "none" else None,
            "actor": evidence.get("actor") if kind != "none" else None,
            "body_fingerprint": evidence.get("body_fingerprint")
            if kind != "none"
            else None,
            "outcome": evidence.get("outcome") if kind != "none" else None,
        }
        return {
            "repository": target["repository"],
            "pr_number": target["pr_number"],
            "head_sha": target["head_sha"],
            "provider": target["provider"],
            "request_receipt": supplied["request_receipt"],
            "request_binding": raw.get("request_binding"),
            "provider_state": provider_state,
            "observation_fingerprint": raw.get("observation_fingerprint"),
            "finding_count": int((raw.get("review") or {}).get("findings") or 0),
            "finding_comment_ids": list(
                (raw.get("review") or {}).get("finding_comment_ids") or []
            ),
            "artifact": artifact,
        }
    if operation in {"ready-check", "ready-wait"}:
        evidence = raw.get("evidence") or {}
        kind = (
            evidence.get("kind")
            if evidence.get("kind")
            in {"formal-review", "provider-comment", "inline-finding", "clean-reaction"}
            else "none"
        )
        artifact = {
            "kind": kind,
            "object_id": evidence.get("object_id") if kind != "none" else None,
            "object_url": evidence.get("object_url") if kind != "none" else None,
            "actor": evidence.get("actor") if kind != "none" else None,
            "body_fingerprint": evidence.get("body_fingerprint")
            if kind != "none"
            else None,
            "outcome": evidence.get("outcome") if kind != "none" else None,
        }
        state = raw.get("review_state")
        provider_state = (
            state
            if state in {"clean", "findings", "pending", "stale", "ambiguous"}
            else "failed"
        )
        return {
            "repository": target["repository"],
            "pr_number": target["pr_number"],
            "head_sha": target["head_sha"],
            "provider": target["provider"],
            "ready_receipt": supplied["ready_receipt"],
            "provider_state": provider_state,
            "observation_fingerprint": raw.get("observation_fingerprint"),
            "finding_count": int((raw.get("review") or {}).get("findings") or 0),
            "finding_comment_ids": list(
                (raw.get("review") or {}).get("finding_comment_ids") or []
            ),
            "artifact": artifact,
        }
    if operation == "warning":
        return {
            "request_receipt": supplied["request_receipt"],
            "mutation": backend._mutation_artifact(raw),
        }
    if operation == "reply":
        return {
            "request_receipt": supplied["request_receipt"],
            "reply_receipt": raw["reply"],
            "mutation": backend._mutation_artifact(raw, raw["reply"]),
        }
    if operation == "resolve":
        return {
            "request_receipt": supplied["request_receipt"],
            "resolution_receipt": raw["resolution"],
        }
    if operation == "reconcile-terminal":
        return {
            "prior_result_fingerprint": supplied["prior_failed_result"][
                "result_fingerprint"
            ],
            "request_receipt": supplied["request_receipt"],
            "terminal_evidence": raw,
        }
    if operation == "reconcile-mutation":
        return raw
    raise ReviewError(
        "Unsupported owned operation normalization.",
        code="owned_operation_result_invalid",
        exit_code=4,
    )


def _mutation_provider_state(exc: ReviewError, *, backend: Any) -> str:
    if exc.code in {"reservation_not_consumed", "reservation_conflict"}:
        return "missing"
    if exc.code == "reservation_target_mismatch":
        return "conflicting"
    matches = (
        (exc.details or {}).get("matches") if isinstance(exc.details, dict) else None
    )
    if matches == 0:
        return "missing"
    if isinstance(matches, int) and matches > 1:
        return "ambiguous"
    return "unreadable"


def execute_owned_operation(
    request_file: str, result_file: str, *, mode: str, backend: Any
) -> dict[str, Any]:
    try:
        request = validate_operation_request(
            backend._read_json_object(request_file, "operation request")
        )
    except OperationError as exc:
        raise ReviewError(
            str(exc), code="owned_operation_invalid", exit_code=64
        ) from exc
    if mode == "reconcile" and request["operation"] not in {
        "reconcile-mutation",
        "reconcile-terminal",
    }:
        raise ReviewError(
            "Only reconciliation operations may use operation reconcile.",
            code="owned_operation_invalid",
            exit_code=64,
        )
    if mode == "resume" and request["operation"] not in {"wait", "ready-wait"}:
        raise ReviewError(
            "Only an already-started review wait may use operation resume.",
            code="owned_operation_invalid",
            exit_code=64,
        )
    if mode == "execute" and request["operation"] in {
        "reconcile-mutation",
        "reconcile-terminal",
    }:
        raise ReviewError(
            "Reconciliation operations require operation reconcile.",
            code="owned_operation_invalid",
            exit_code=64,
        )
    start = backend._owned_operation_start(request, create=mode == "execute")
    target, supplied = (request["target"], request["input"])
    operation = request["operation"]
    repo, pr, head, provider = (
        target["repository"],
        target["pr_number"],
        target["head_sha"],
        target["provider"],
    )
    exit_code = 0
    if operation == "request":
        facts = backend.request_automated_review(
            repo,
            pr,
            provider,
            head,
            supplied["request_key"],
            False,
            request["authority"]["managed_checkout_fingerprint"],
            request_file,
            request,
        )
    elif operation == "wait":
        from datetime import datetime as _datetime

        deadline = _datetime.fromisoformat(
            supplied["wait_deadline"].replace("Z", "+00:00")
        )
        invoked = _datetime.now(timezone.utc)
        timeout = max(0, int((deadline - invoked).total_seconds()))
        facts, exit_code = backend.wait_for_automated_review(
            repo, pr, provider, head, timeout, 10, 30, supplied["request_receipt"]
        )
    elif operation == "ready-check":
        facts = backend.check_ready_automated_review(
            repo, pr, provider, head, supplied["ready_receipt"]
        )
        exit_code = backend.REVIEW_EXIT_CODES.get(str(facts.get("review_state")), 4)
    elif operation == "ready-wait":
        from datetime import datetime as _datetime

        deadline = _datetime.fromisoformat(
            supplied["wait_deadline"].replace("Z", "+00:00")
        )
        invoked = _datetime.now(timezone.utc)
        timeout = max(0, int((deadline - invoked).total_seconds()))
        facts, exit_code = backend.wait_for_ready_automated_review(
            repo, pr, provider, head, timeout, 10, 30, supplied["ready_receipt"]
        )
    elif operation == "warning":
        body = backend.read_text_file(supplied["body_file"], field="body")
        if body.sha256 != supplied["body_fingerprint"]:
            raise ReviewError(
                "Warning body fingerprint changed.",
                code="owned_operation_drift",
                exit_code=4,
            )
        receipt_value = supplied["request_receipt"]
        facts = backend.post_conversation_comment(
            repo,
            pr,
            body,
            False,
            request["authority"]["managed_checkout_fingerprint"],
            head,
            receipt_value["request_key"],
            receipt_value["request_fingerprint"],
            request_file,
            request,
        )
    elif operation == "reply":
        body = backend.read_text_file(supplied["body_file"], field="body")
        if body.sha256 != supplied["body_fingerprint"]:
            raise ReviewError(
                "Reply body fingerprint changed.",
                code="owned_operation_drift",
                exit_code=4,
            )
        receipt_value = supplied["request_receipt"]
        facts = backend.reply_to_review_comment(
            repo,
            pr,
            head,
            supplied["finding_comment_id"],
            body,
            False,
            request["authority"]["managed_checkout_fingerprint"],
            receipt_value["request_key"],
            receipt_value["request_fingerprint"],
            request_file,
            request,
            expected_thread_id=supplied["thread_id"],
            expected_thread_fingerprint=supplied["thread_fingerprint"],
        )
    elif operation == "resolve":
        receipt_value = supplied["request_receipt"]
        facts = backend.resolve_review_thread(
            repo,
            pr,
            head,
            supplied["reply_receipt"],
            False,
            request["authority"]["managed_checkout_fingerprint"],
            receipt_value["request_key"],
            receipt_value["request_fingerprint"],
            request_file,
            request,
        )
    elif operation == "reconcile-terminal":
        facts = backend.terminal_provider_evidence(
            repo, pr, provider, head, supplied["request_receipt"]
        )
    else:
        started_operation = supplied["started_operation"]
        started = started_operation["request"]
        started_target, started_input = (started["target"], started["input"])
        recovered_result = None
        recovery_marker: dict[str, Any] = {}
        try:
            if started["operation"] == "request":
                recovered_raw = backend.request_automated_review(
                    started_target["repository"],
                    started_target["pr_number"],
                    started_target["provider"],
                    started_target["head_sha"],
                    started_input["request_key"],
                    False,
                    started["authority"]["managed_checkout_fingerprint"],
                    request_file,
                    started,
                    reconcile_consumed=True,
                    recovery_marker=recovery_marker,
                )
            elif started["operation"] == "warning":
                body = backend.read_text_file(started_input["body_file"], field="body")
                recovered_raw = backend.post_conversation_comment(
                    started_target["repository"],
                    started_target["pr_number"],
                    body,
                    False,
                    started["authority"]["managed_checkout_fingerprint"],
                    started_target["head_sha"],
                    started_input["request_receipt"]["request_key"],
                    started_input["request_receipt"]["request_fingerprint"],
                    request_file,
                    started,
                    reconcile_consumed=True,
                    recovery_marker=recovery_marker,
                )
            elif started["operation"] == "reply":
                body = backend.read_text_file(started_input["body_file"], field="body")
                recovered_raw = backend.reply_to_review_comment(
                    started_target["repository"],
                    started_target["pr_number"],
                    started_target["head_sha"],
                    started_input["finding_comment_id"],
                    body,
                    False,
                    started["authority"]["managed_checkout_fingerprint"],
                    started_input["request_receipt"]["request_key"],
                    started_input["request_receipt"]["request_fingerprint"],
                    request_file,
                    started,
                    reconcile_consumed=True,
                    recovery_marker=recovery_marker,
                    expected_thread_id=started_input["thread_id"],
                    expected_thread_fingerprint=started_input["thread_fingerprint"],
                )
            else:
                recovered_raw = backend.resolve_review_thread(
                    started_target["repository"],
                    started_target["pr_number"],
                    started_target["head_sha"],
                    started_input["reply_receipt"],
                    False,
                    started["authority"]["managed_checkout_fingerprint"],
                    started_input["request_receipt"]["request_key"],
                    started_input["request_receipt"]["request_fingerprint"],
                    request_file,
                    started,
                    reconcile_consumed=True,
                    recovery_marker=recovery_marker,
                )
            recovered_status, recovered_outcome = backend._operation_outcome(
                started["operation"], recovered_raw
            )
            recovered_facts = backend._normalize_owned_facts(
                started, recovered_raw, recovered_outcome
            )
            recovered_result = build_operation_result(
                request=started,
                start_receipt=started_operation["start_receipt"],
                status=recovered_status,
                outcome=recovered_outcome,
                facts=recovered_facts,
                evidence_ref=f"g-operation://recovered/{started['operation_id']}",
            )
            marker_state = "exact"
            provider_artifact_state = "unique"
        except ReviewError as exc:
            marker_state = (
                "conflicting"
                if exc.code == "reservation_conflict"
                else "exact"
                if recovery_marker
                else "absent"
            )
            provider_artifact_state = backend._mutation_provider_state(exc)
        verified_marker_fingerprint = (
            backend._consumed_marker_fingerprint(recovery_marker)
            if recovery_marker
            else None
        )
        facts = {
            "started_operation": started["operation"],
            "marker_state": marker_state,
            "marker_fingerprint": verified_marker_fingerprint,
            "provider_artifact_state": provider_artifact_state,
            "recovered_result": recovered_result,
        }
    status, outcome = backend._operation_outcome(operation, facts, exit_code)
    normalized_facts = backend._normalize_owned_facts(request, facts, outcome)
    try:
        result = build_operation_result(
            request=request,
            start_receipt=start,
            status=status,
            outcome=outcome,
            facts=normalized_facts,
            evidence_ref=f"g-operation://{request['operation_id']}",
        )
        validate_result_for_request(result, request)
    except OperationError as exc:
        raise ReviewError(
            str(exc), code="owned_operation_result_invalid", exit_code=4
        ) from exc
    backend._write_json_object(result_file, result)
    return {
        "result_file": result_file,
        "result_fingerprint": result["result_fingerprint"],
        "status": status,
        "outcome": outcome,
    }
