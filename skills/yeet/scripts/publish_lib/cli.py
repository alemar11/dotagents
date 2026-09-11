from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from . import __version__
from .common import GError, envelope, error_envelope
from .health import doctor, doctor_text
from .provider_text import worktree_snapshot
from .publish import open_pr, preflight


class Parser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("allow_abbrev", False)
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> None:
        raise GError("Invalid command arguments.", code="invalid_arguments", exit_code=64)


def build_parser() -> Parser:
    root = Parser(prog="publish", description="Verified pull-request publication helpers for Yeet.")
    root.add_argument("--version", action="version", version=__version__)
    root.add_argument("--json", action="store_true", help="Emit a stable JSON envelope.")
    commands = root.add_subparsers(dest="command")
    commands.add_parser("doctor", help="Check Python, git, gh, authentication, and checkout readiness.")
    commands.add_parser("snapshot", help="Fingerprint the current Git HEAD and porcelain worktree state.")
    preflight_parser = commands.add_parser("preflight", help="Verify local readiness to open or reuse a PR.")
    preflight_parser.add_argument("--repo")
    open_parser = commands.add_parser("open", help="Open or reuse a draft pull request.")
    open_parser.add_argument("--repo")
    open_parser.add_argument("--title-file", required=True)
    open_parser.add_argument("--body-file", required=True)
    open_parser.add_argument("--base")
    open_parser.add_argument("--draft", action="store_true", default=True)
    open_parser.add_argument("--dry-run", action="store_true")
    open_parser.add_argument("--expected-worktree-fingerprint")
    return root


def _emit(data: object, command: list[str], json_mode: bool) -> None:
    if json_mode:
        print(json.dumps(envelope(command, data), indent=2))
    else:
        print(json.dumps(data, indent=2))


def main(argv: list[str] | None = None) -> int:
    raw = list(argv if argv is not None else sys.argv[1:])
    if raw == ["--version"]:
        print(__version__)
        return 0
    json_mode = "--json" in raw
    if json_mode:
        raw = [item for item in raw if item != "--json"]
        raw.insert(0, "--json")
    try:
        args = build_parser().parse_args(raw)
        if args.command is None:
            build_parser().print_help()
            return 0
        if args.command == "doctor":
            payload = doctor()
            print(json.dumps(payload, indent=2) if args.json else doctor_text(payload, f"publish {__version__}"))
            return 0 if payload["ok"] else 1
        if args.command == "snapshot":
            _emit(worktree_snapshot(), ["snapshot"], args.json)
            return 0
        if args.command == "preflight":
            _emit(preflight(args.repo), ["preflight"], args.json)
            return 0
        if args.command == "open":
            data = open_pr(
                repo=args.repo,
                title_file=args.title_file,
                body_file=args.body_file,
                draft=args.draft,
                base=args.base,
                dry_run=args.dry_run,
                expected_worktree_fingerprint=args.expected_worktree_fingerprint,
            )
            _emit(data, ["open"], args.json)
            return 0
        raise GError("Unsupported command.", code="invalid_arguments", exit_code=64)
    except GError as exc:
        command = [item for item in raw if not item.startswith("-")][:1]
        if json_mode:
            print(json.dumps(error_envelope(command, exc), indent=2))
        else:
            print(str(exc), file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
