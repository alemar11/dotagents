from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from . import __version__, stack
from .common import GError, envelope, error_envelope
from .health import doctor, doctor_text


class Parser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("allow_abbrev", False)
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> None:
        raise GError("Invalid command arguments.", code="invalid_arguments", exit_code=64)


def build_parser() -> Parser:
    root = Parser(prog="stack", description="Wrap the GitHub gh-stack extension.")
    root.add_argument("--version", action="version", version=__version__)
    root.add_argument("--json", action="store_true", help="Emit a stable JSON envelope.")
    commands = root.add_subparsers(dest="command")
    commands.add_parser("doctor", help="Check Python, git, gh, authentication, and gh-stack readiness.")
    ensure = commands.add_parser("ensure", help="Check or explicitly install github/gh-stack.")
    ensure.add_argument("--install", action="store_true", help="Install the official extension when it is missing.")
    for command in stack.STACK_COMMANDS:
        stack_command = commands.add_parser(command, help=f"Run gh stack {command} without interactive prompts.")
        stack_command.add_argument("args", nargs=argparse.REMAINDER)
    raw = commands.add_parser("raw", help="Run a non-interactive upstream gh stack command.")
    raw.add_argument("args", nargs=argparse.REMAINDER)
    return root


def _json_option_index(argv: list[str]) -> int | None:
    raw_separator: int | None = None
    for index in range(len(argv) - 1):
        if argv[index] == "raw":
            try:
                raw_separator = argv.index("--", index + 1)
            except ValueError:
                pass
            break
    for index, argument in enumerate(argv):
        if argument != "--json":
            continue
        if raw_separator is not None and index > raw_separator:
            continue
        return index
    return None


def _normalize_passthrough(argv: list[str]) -> list[str]:
    if len(argv) >= 2 and argv[0] == "--json":
        command_index = 1
    elif argv:
        command_index = 0
    else:
        return argv
    if command_index >= len(argv) or argv[command_index] not in stack.STACK_COMMANDS:
        return argv
    args_index = command_index + 1
    if args_index >= len(argv) or argv[args_index] == "--":
        return argv
    return [*argv[:args_index], "--", *argv[args_index:]]


def main(argv: list[str] | None = None) -> int:
    raw = list(argv if argv is not None else sys.argv[1:])
    if raw == ["--version"]:
        print(__version__)
        return 0
    json_index = _json_option_index(raw)
    json_mode = json_index is not None
    if json_mode and json_index is not None:
        raw.pop(json_index)
        raw.insert(0, "--json")
    raw = _normalize_passthrough(raw)
    try:
        args = build_parser().parse_args(raw)
        if args.command is None:
            build_parser().print_help()
            return 0
        if args.command == "doctor":
            payload = doctor()
            print(json.dumps(payload, indent=2) if args.json else doctor_text(payload, f"stack {__version__}"))
            return 0 if payload["ok"] else 1
        if args.command == "ensure":
            data = stack.ensure(install=args.install, json_mode=args.json)
            if args.json:
                print(json.dumps(envelope(["ensure"], data), indent=2))
            else:
                print(json.dumps(data, indent=2))
            return 0
        if args.command == "raw":
            return stack.execute_raw(args.args, json_mode=args.json)
        forwarded = list(args.args)
        if forwarded and forwarded[0] == "--":
            forwarded.pop(0)
        return stack.execute(args.command, forwarded, json_mode=args.json)
    except GError as exc:
        command = [item for item in raw if not item.startswith("-")][:1]
        if json_mode:
            print(json.dumps(error_envelope(command, exc), indent=2))
        else:
            print(str(exc), file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
