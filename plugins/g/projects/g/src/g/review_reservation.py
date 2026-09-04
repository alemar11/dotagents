from __future__ import annotations

import hashlib
import json
import os
import stat
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from .provider_text import ProviderText
from .review_mutation import (
    MUTATION_KINDS,
    ReservationError,
    add_operation_marker,
    build_reservation,
    marker_operation_id,
    operation_id_for_mutation,
    operation_id_for_request,
    packet_fingerprint,
    validate_reservation_packet,
)
from .review_request import validate_full_head
from .review_types import ReviewError


def trusted_user_home() -> Path:
    """Return the account home without trusting a caller-provided HOME."""

    try:
        import pwd

        return Path(pwd.getpwuid(os.getuid()).pw_dir)
    except (ImportError, KeyError, OSError, AttributeError):
        return Path.home()


def read_reservation_file(path_value: str | None) -> dict[str, Any]:
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
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
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


def require_reservation(
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
    read_packet: Callable[[str | None], dict[str, Any]] = read_reservation_file,
) -> dict[str, Any]:
    if kind not in MUTATION_KINDS:
        raise ReviewError(
            "The requested mutation kind is not supported.",
            code="reservation_invalid",
            exit_code=4,
        )
    required = {
        "head": head,
        "request_key": request_key,
        "request_fingerprint": request_fingerprint,
    }
    if kind in {"review-reply", "review-resolution"}:
        required.update(
            thread_id=thread_id,
            thread_fingerprint=thread_fingerprint,
            finding_comment_id=finding_comment_id,
        )
    missing = [name for name, value in required.items() if value is None]
    if missing:
        raise ReviewError(
            f"The reservation is missing exact mutation identity: {', '.join(missing)}.",
            code="reservation_required",
            exit_code=4,
        )
    if owned_operation is None:
        packet = read_packet(path_value)
    else:
        authority = owned_operation["authority"]
        if kind == "review-request":
            operation_id = operation_id_for_request(
                repo, pr, str(head), str(request_key), str(request_fingerprint)
            )
        else:
            operation_id = operation_id_for_mutation(
                kind,
                repo,
                pr,
                str(head),
                request_fingerprint=request_fingerprint,
                thread_id=thread_id,
                finding_comment_id=finding_comment_id,
                reply_receipt_fingerprint=reply_receipt_fingerprint,
            )
        packet = build_reservation(
            mutation_kind=kind,
            repository=repo,
            pr_number=pr,
            head_sha=str(head),
            task_key=authority["task_key"],
            delivery_key=authority["delivery_key"],
            operation_id=operation_id,
            request_key=request_key,
            request_fingerprint=request_fingerprint,
            thread_id=thread_id,
            thread_fingerprint=thread_fingerprint,
            finding_comment_id=finding_comment_id,
            body_fingerprint=body_fingerprint,
            reply_receipt_fingerprint=reply_receipt_fingerprint,
            expected_generation=authority["expected_generation"],
            expected_state_fingerprint=authority["expected_state_fingerprint"],
            expected_claim_fingerprint=authority["expected_claim_fingerprint"],
            expected_task_state=authority["task_state"],
        )
    if (
        packet["mutation_kind"] != kind
        or packet["repository"] != repo
        or packet["pr_number"] != pr
    ):
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


def read_consumed_marker(
    packet: dict[str, Any],
    reservation_file: str,
    *,
    root: Path,
    require_consumed: bool = False,
    marker_observer: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if not root.exists():
        if require_consumed:
            raise ReviewError(
                "The started mutation has no consumed marker; recovery is missing.",
                code="reservation_not_consumed",
                exit_code=4,
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
                code="reservation_not_consumed",
                exit_code=4,
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


def consumed_marker_fingerprint(marker: dict[str, Any]) -> str:
    encoded = json.dumps(
        marker, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def with_consumed_marker(
    action: dict[str, Any], marker: dict[str, Any]
) -> dict[str, Any]:
    action["consumed_marker_fingerprint"] = consumed_marker_fingerprint(marker)
    return action


def recovery_required(
    message: str, *, code: str, details: dict[str, Any] | None = None
) -> ReviewError:
    return ReviewError(
        message,
        code=code,
        exit_code=4,
        details={
            "recovery": "needs-owner",
            "automatic_retry": False,
            **(details or {}),
        },
    )


def consume_reservation(
    packet: dict[str, Any],
    reservation_file: str,
    *,
    root: Path,
    consumed_at: datetime,
    read_marker: Callable[..., dict[str, Any] | None],
) -> None:
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
        "consumed_at": consumed_at.isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    encoded = (json.dumps(marker, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    try:
        fd = os.open(
            marker_path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
    except FileExistsError as exc:
        read_marker(packet, reservation_file)
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
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
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


def marked_body(body: ProviderText, packet: dict[str, Any]) -> ProviderText:
    try:
        text = add_operation_marker(body.text, packet["operation_id"])
    except ReservationError as exc:
        raise ReviewError(
            "The provider body marker is invalid.",
            code="reservation_invalid",
            exit_code=4,
        ) from exc
    marked = ProviderText(body.field, text.encode("utf-8"), text)
    if packet["body_fingerprint"] != marked.sha256:
        raise ReviewError(
            "The reservation body fingerprint does not match the exact provider text.",
            code="reservation_body_mismatch",
            exit_code=4,
        )
    return marked


def marker_matches(text: str, operation_id: str) -> bool:
    try:
        return marker_operation_id(text) == operation_id
    except ReservationError:
        return False
