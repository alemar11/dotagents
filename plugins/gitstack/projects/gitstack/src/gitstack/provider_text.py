from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Generic, TypeVar

from .common import GitStackError, Result, checked

API_VERSION = "2026-03-10"
ACCEPT_HEADER = "Accept: application/vnd.github+json"
VERSION_HEADER = f"X-GitHub-Api-Version: {API_VERSION}"
ProofValue = TypeVar("ProofValue")


@dataclass(frozen=True)
class ProviderText:
    field: str
    data: bytes
    text: str

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest()

    def proof(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "encoding": "utf-8",
            "bytes": len(self.data),
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class MutationProof(Generic[ProofValue]):
    value: ProofValue
    recovered: bool


def read_text_file(
    raw_path: str,
    *,
    field: str,
    allow_empty: bool = False,
    single_line: bool = False,
) -> ProviderText:
    path = Path(raw_path)
    if not path.is_absolute():
        raise GitStackError(
            f"--{field}-file must be an absolute path.",
            code="provider_text_path_invalid",
            exit_code=64,
        )
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise GitStackError(
            f"--{field}-file is not readable.",
            code="provider_text_path_invalid",
            exit_code=64,
        ) from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise GitStackError(
            f"--{field}-file must be a regular, non-symlink file.",
            code="provider_text_path_invalid",
            exit_code=64,
        )
    try:
        data = path.read_bytes()
        text = data.decode("utf-8", errors="strict")
    except (OSError, UnicodeError) as exc:
        raise GitStackError(
            f"--{field}-file must contain valid UTF-8.",
            code="provider_text_invalid",
            exit_code=64,
        ) from exc
    if "\x00" in text:
        raise GitStackError(
            f"--{field}-file must not contain NUL bytes.",
            code="provider_text_invalid",
            exit_code=64,
        )
    if not allow_empty and not data:
        raise GitStackError(
            f"--{field}-file must not be empty.",
            code="provider_text_invalid",
            exit_code=64,
        )
    if single_line and ("\n" in text or "\r" in text):
        raise GitStackError(
            f"--{field}-file must contain exactly one line.",
            code="provider_text_invalid",
            exit_code=64,
        )
    return ProviderText(field=field, data=data, text=text)


def json_request(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def api_request(method: str, endpoint: str, payload: dict[str, Any], *, cwd: Path | None = None) -> Result:
    command = [
        "gh",
        "api",
        "--method",
        method,
        endpoint,
        "--header",
        ACCEPT_HEADER,
        "--header",
        VERSION_HEADER,
        "--input",
        "-",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            input=json_request(payload),
            capture_output=True,
            shell=False,
        )
    except FileNotFoundError:
        return Result(127, "", "gh is not installed or not on PATH.")
    return Result(
        completed.returncode,
        completed.stdout.decode("utf-8", errors="replace"),
        completed.stderr.decode("utf-8", errors="replace"),
    )


def graphql_request(query: str, variables: dict[str, Any]) -> Result:
    command = ["gh", "api", "graphql", "--input", "-"]
    try:
        completed = subprocess.run(
            command,
            input=json_request({"query": query, "variables": variables}),
            capture_output=True,
            shell=False,
        )
    except FileNotFoundError:
        return Result(127, "", "gh is not installed or not on PATH.")
    return Result(
        completed.returncode,
        completed.stdout.decode("utf-8", errors="replace"),
        completed.stderr.decode("utf-8", errors="replace"),
    )


def parse_api_object(result: Result) -> dict[str, Any]:
    if result.returncode:
        raise GitStackError(
            "GitHub API mutation did not return a confirmed response.",
            code="provider_write_unconfirmed",
            exit_code=result.returncode,
        )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise GitStackError(
            "GitHub API mutation returned an unreadable response.",
            code="provider_response_invalid",
            exit_code=65,
        ) from exc
    if not isinstance(payload, dict):
        raise GitStackError(
            "GitHub API mutation returned an unexpected response shape.",
            code="provider_response_invalid",
            exit_code=65,
        )
    return payload


def prove_mutation(
    result: Result,
    *,
    prove_response: Callable[[dict[str, Any]], ProofValue],
    read_back: Callable[[], ProofValue],
    target: dict[str, Any],
    text: dict[str, Any],
    ambiguous_message: str,
) -> MutationProof[ProofValue]:
    response_failure = "provider_write_unconfirmed"
    if result.returncode == 0:
        try:
            return MutationProof(prove_response(parse_api_object(result)), recovered=False)
        except GitStackError as exc:
            response_failure = exc.code

    try:
        recovered = read_back()
    except GitStackError as exc:
        raise GitStackError(
            ambiguous_message,
            code="provider_write_ambiguous",
            exit_code=result.returncode or 65,
            details={
                "target": target,
                "text": text,
                "response": {
                    "code": response_failure,
                    "transport_exit_code": result.returncode,
                },
                "read_back": {"code": exc.code},
            },
        ) from exc
    return MutationProof(recovered, recovered=True)


def verify_response_text(payload: dict[str, Any], expected: ProviderText, *, field: str = "body") -> None:
    if response_text_matches(payload, expected, field=field):
        return
    raise GitStackError(
        "GitHub response text did not match the submitted byte fingerprint.",
        code="provider_text_mismatch",
        exit_code=65,
    )


def response_text_matches(payload: dict[str, Any], expected: ProviderText, *, field: str = "body") -> bool:
    actual = payload.get(field)
    if not isinstance(actual, str):
        return False
    try:
        return actual.encode("utf-8") == expected.data
    except UnicodeEncodeError:
        return False


def worktree_snapshot(cwd: Path | None = None) -> dict[str, Any]:
    root = Path(checked(["git", "rev-parse", "--show-toplevel"], cwd).stdout.strip()).resolve()
    head = checked(["git", "rev-parse", "HEAD"], root).stdout.strip()
    try:
        status_result = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            cwd=root,
            capture_output=True,
            shell=False,
        )
    except FileNotFoundError as exc:
        raise GitStackError("git is not installed or not on PATH.", code="worktree_snapshot_failed", exit_code=127) from exc
    if status_result.returncode:
        raise GitStackError(
            "Could not fingerprint the Git worktree.",
            code="worktree_snapshot_failed",
            exit_code=status_result.returncode,
        )
    status_bytes = status_result.stdout
    fingerprint = hashlib.sha256(head.encode("ascii") + b"\0" + status_bytes).hexdigest()
    return {
        "root": os.fspath(root),
        "head": head,
        "fingerprint": fingerprint,
        "dirty": bool(status_bytes),
        "status_bytes": len(status_bytes),
    }


def require_worktree(expected: str | None, cwd: Path | None = None) -> dict[str, Any] | None:
    if expected is None:
        return None
    if not re_full_sha256(expected):
        raise GitStackError(
            "--expected-worktree-fingerprint must be a 64-character SHA-256 value.",
            code="invalid_arguments",
            exit_code=64,
        )
    snapshot = worktree_snapshot(cwd)
    if snapshot["fingerprint"] != expected:
        raise GitStackError(
            "The Git worktree does not match the expected pre-call fingerprint.",
            code="worktree_changed",
            exit_code=65,
        )
    return snapshot


def verify_worktree_unchanged(before: dict[str, Any] | None, cwd: Path | None = None) -> dict[str, Any] | None:
    if before is None:
        return None
    after = worktree_snapshot(cwd)
    if after["fingerprint"] != before["fingerprint"]:
        raise GitStackError(
            "The provider mutation completed, but the Git worktree fingerprint changed.",
            code="provider_write_partial_success",
            exit_code=65,
        )
    return after


def re_full_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value.lower())
