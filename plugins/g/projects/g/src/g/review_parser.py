from __future__ import annotations

import argparse

from .review_mutation import MUTATION_KINDS
from .review_types import StrictParser


def _target(parser: argparse.ArgumentParser, *, head: bool = False) -> None:
    parser.add_argument("--pr", required=True, help="Pull request number.")
    parser.add_argument(
        "--repo", help="Repository in owner/repo format. Defaults to current checkout."
    )
    if head:
        parser.add_argument(
            "--head", required=True, help="Full 40-character current PR head SHA."
        )
    parser.add_argument(
        "--allow-non-project",
        action="store_true",
        help="Allow --repo usage outside a git checkout.",
    )


def _mutation(parser: argparse.ArgumentParser, *, body: bool = False) -> None:
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--expected-worktree-fingerprint")
    if body:
        parser.add_argument("--body-file", required=True)


def _review_binding(parser: argparse.ArgumentParser, command: str) -> None:
    parser.add_argument(
        "--provider", required=True, help="Automated review provider. Currently: codex."
    )
    parser.add_argument("--pr", required=True, help="Pull request number.")
    parser.add_argument(
        "--repo", help="Repository in owner/repo format. Defaults to current checkout."
    )
    parser.add_argument(
        "--head", help="Expected reviewed head SHA. Defaults to the current PR head."
    )
    parser.add_argument(
        "--request-receipt-file", help="Absolute UTF-8 JSON request receipt file."
    )
    parser.add_argument(
        "--ready-receipt-file",
        help="Absolute UTF-8 JSON ready-transition receipt file.",
    )
    parser.add_argument("--allow-non-project", action="store_true")
    if command in {"wait", "ready-wait"}:
        parser.add_argument(
            "--timeout",
            default="15m",
            help="Maximum wait, for example 30s, 15m, or 1h.",
        )
        parser.add_argument(
            "--interval", default="10s", help="Initial polling interval."
        )
        parser.add_argument(
            "--max-interval", default="30s", help="Maximum polling interval."
        )


def build_parser() -> argparse.ArgumentParser:
    parser = StrictParser(
        prog="g reviews",
        description="Inspect, check, wait for, or respond to pull-request reviews.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit a stable JSON envelope."
    )
    parser.add_argument(
        "--version", action="store_true", help="Print version and exit."
    )
    commands = parser.add_subparsers(dest="command")

    operation = commands.add_parser(
        "operation", help="Manage one closed owned review operation."
    )
    operation_commands = operation.add_subparsers(
        dest="operation_command", required=True
    )
    prepare_operation = operation_commands.add_parser(
        "prepare", help="Prepare one immutable G-owned request."
    )
    prepare_operation.add_argument("--controller-envelope-file", required=True)
    prepare_operation.add_argument("--input-file", required=True)
    prepare_operation.add_argument("--request-output", required=True)
    validate_request = operation_commands.add_parser(
        "validate-request", help="Validate one immutable request."
    )
    validate_request.add_argument("--request-file", required=True)
    validate_result = operation_commands.add_parser(
        "validate-result", help="Validate one immutable result."
    )
    validate_result.add_argument("--result-file", required=True)
    validate_result.add_argument("--request-file", required=True)
    for verb, help_text in (
        ("execute", "Execute one authority-started owned operation."),
        ("resume", "Resume one already-started wait."),
        ("reconcile", "Reconcile one already-started operation."),
    ):
        child = operation_commands.add_parser(verb, help=help_text)
        child.add_argument("--request-file", required=True)
        child.add_argument("--result-output", required=True)

    commands.add_parser("doctor", help="Check local git and gh readiness.")
    address = commands.add_parser("address", help="List review context read-only.")
    _target(address)
    address.add_argument("--include-resolved", action="store_true")

    comment = commands.add_parser(
        "comment", help="Post a top-level PR discussion comment."
    )
    _target(comment, head=True)
    _mutation(comment, body=True)
    comment.add_argument("--request-key", required=True)
    comment.add_argument("--request-fingerprint", required=True)
    comment.add_argument("--reservation-file", required=True)

    request = commands.add_parser(
        "request", help="Post or recover one typed automated review request."
    )
    _target(request, head=True)
    _mutation(request)
    request.add_argument("--provider", required=True)
    request.add_argument("--request-key", required=True)
    request.add_argument("--reservation-file", required=True)

    reply = commands.add_parser(
        "reply", help="Reply to one pull-request review comment."
    )
    _target(reply, head=True)
    _mutation(reply, body=True)
    reply.add_argument("--comment-id", required=True)
    reply.add_argument("--request-key", required=True)
    reply.add_argument("--request-fingerprint", required=True)
    reply.add_argument("--reservation-file", required=True)

    resolve = commands.add_parser("resolve", help="Resolve one exact review thread.")
    _target(resolve, head=True)
    _mutation(resolve)
    resolve.add_argument("--reply-receipt-file", required=True)
    resolve.add_argument("--request-key", required=True)
    resolve.add_argument("--request-fingerprint", required=True)
    resolve.add_argument("--reservation-file", required=True)

    edit = commands.add_parser(
        "edit-comment", help="Edit one conversation or review comment."
    )
    _target(edit)
    _mutation(edit, body=True)
    edit.add_argument("--comment-id", required=True)
    edit.add_argument("--kind", required=True, choices=("conversation", "review"))

    submit = commands.add_parser(
        "submit-review", help="Submit one PR review with a file-backed body."
    )
    _target(submit)
    _mutation(submit, body=True)
    submit.add_argument(
        "--event", required=True, choices=("approve", "request-changes", "comment")
    )

    prepare = commands.add_parser(
        "prepare", help="Create one immutable provider-mutation packet."
    )
    prepare.add_argument(
        "--mutation-kind", required=True, choices=tuple(sorted(MUTATION_KINDS))
    )
    prepare.add_argument("--repo")
    prepare.add_argument("--pr", required=True)
    prepare.add_argument("--head", required=True)
    for field in (
        "task-key",
        "delivery-key",
        "expected-state-fingerprint",
        "expected-claim-fingerprint",
        "expected-task-state",
    ):
        prepare.add_argument(f"--{field}", required=True)
    prepare.add_argument("--expected-generation", required=True, type=int)
    for field in (
        "request-key",
        "request-fingerprint",
        "thread-id",
        "thread-fingerprint",
        "finding-comment-id",
        "body-file",
        "reply-receipt-file",
        "output-file",
    ):
        prepare.add_argument(f"--{field}")
    prepare.add_argument("--allow-non-project", action="store_true")

    validate = commands.add_parser(
        "validate", help="Validate one immutable provider-mutation packet."
    )
    validate.add_argument("--reservation-file", required=True)

    terminal = commands.add_parser(
        "terminal-evidence", help="Verify one exact-head terminal provider artifact."
    )
    _target(terminal, head=True)
    terminal.add_argument("--provider", required=True)
    terminal.add_argument("--request-receipt-file", required=True)

    trigger = commands.add_parser(
        "ready-trigger", help="Build one typed ready-transition receipt."
    )
    trigger.add_argument("--provider", required=True, choices=("codex",))
    trigger.add_argument("--repo", required=True)
    trigger.add_argument("--pr", required=True, type=int)
    for field in (
        "head",
        "ready-event-id",
        "ready-ref",
        "ready-at",
        "base-branch",
        "body-fingerprint",
        "output-file",
    ):
        trigger.add_argument(f"--{field}", required=True)

    for command, help_text in (
        ("check", "Inspect automated review state once and exit."),
        ("wait", "Wait for an automated review to complete or time out."),
        ("ready-check", "Inspect the review triggered by one ready transition."),
        ("ready-wait", "Wait for the review triggered by one ready transition."),
    ):
        _review_binding(commands.add_parser(command, help=help_text), command)
    return parser
