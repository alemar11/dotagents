#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
import sys
from dataclasses import dataclass
from shutil import which
from typing import Callable

from . import lists_cli
from . import stars_cli


VERSION = "1.0.0"


@dataclass(frozen=True)
class RunResult:
    returncode: int
    stdout: str
    stderr: str


def helper_result(main_func: Callable[[list[str] | None], int], argv: list[str]) -> RunResult:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            returncode = int(main_func(argv))
        except SystemExit as exc:
            returncode = int(exc.code) if isinstance(exc.code, int) else 1
    return RunResult(returncode, stdout.getvalue(), stderr.getvalue())


def run(command: list[str]) -> RunResult:
    try:
        completed = subprocess.run(command, text=True, capture_output=True)
    except FileNotFoundError:
        return RunResult(127, "", f"{command[0]} missing")
    return RunResult(completed.returncode, completed.stdout, completed.stderr)


def doctor_payload() -> dict[str, object]:
    gh_path = which("gh")
    auth = run(["gh", "auth", "status"]) if gh_path else RunResult(127, "", "gh missing")
    return {
        "ok": bool(gh_path),
        "version": VERSION,
        "checks": {
            "gh": {
                "ok": bool(gh_path),
                "path": gh_path,
                "authenticated": auth.returncode == 0 if gh_path else False,
            }
        },
    }


def parse_json(stdout: str) -> object:
    cleaned = stdout.strip()
    if not cleaned:
        return None
    return json.loads(cleaned)


def emit_json_result(command: list[str], result: RunResult) -> int:
    if result.returncode == 0:
        payload = {"ok": True, "version": VERSION, "command": command, "data": parse_json(result.stdout)}
    else:
        payload = {
            "ok": False,
            "version": VERSION,
            "command": command,
            "error": {
                "code": "command_failed",
                "message": (result.stderr or result.stdout or "stars command failed").strip(),
            },
        }
    print(json.dumps(payload, indent=2))
    return result.returncode


def invoke(command: list[str], json_mode: bool) -> int:
    if not command:
        print(build_parser().format_help(), end="")
        return 0
    domain = command[0]
    if domain == "list":
        argv = ["--list-stars", *command[1:]]
        main_func = stars_cli.main
    elif domain == "add":
        argv = ["--star", *command[1:]]
        main_func = stars_cli.main
    elif domain == "remove":
        argv = ["--unstar", *command[1:]]
        main_func = stars_cli.main
    elif domain == "lists" and len(command) >= 2:
        mapping = {
            "list": "--list-lists",
            "items": "--list-items",
            "delete": "--delete",
            "assign": "--assign",
            "unassign": "--unassign",
        }
        if command[1] not in mapping:
            raise SystemExit(f"Unsupported lists command: {command[1]}")
        argv = [mapping[command[1]], *command[2:]]
        main_func = lists_cli.main
    else:
        raise SystemExit(f"Unsupported command: {' '.join(command)}")
    if json_mode and "--json" not in argv:
        argv.append("--json")
    result = helper_result(main_func, argv)
    if json_mode:
        return emit_json_result(command, result)
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List, star, unstar, and manage authenticated-user GitHub star lists.")
    parser.add_argument("--json", action="store_true", help="Emit a stable JSON envelope.")
    parser.add_argument("--version", action="store_true", help="Print version and exit.")
    parser.add_argument("command", nargs="*", help="Commands: list, add, remove, lists list/items/delete/assign/unassign, doctor.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.version:
        print(VERSION)
        return 0
    if args.command == ["doctor"]:
        payload = doctor_payload()
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"stars {VERSION}")
            print(f"gh: {'ok' if payload['checks']['gh']['ok'] else 'missing'}")
        return 0 if payload["ok"] else 1
    try:
        return invoke(list(args.command), args.json)
    except SystemExit as exc:
        message = str(exc)
        if args.json:
            print(json.dumps({"ok": False, "version": VERSION, "command": args.command, "error": {"code": "invalid_arguments", "message": message}}, indent=2))
        else:
            print(message, file=sys.stderr)
        return 64


if __name__ == "__main__":
    raise SystemExit(main())
