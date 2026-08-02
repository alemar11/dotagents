from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import __version__

REPO_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")


@dataclass(frozen=True)
class Result:
    returncode: int
    stdout: str
    stderr: str


class GitStackError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        code: str = "command_failed",
        exit_code: int = 1,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code
        self.details = details


def run(
    command: Sequence[str],
    cwd: Path | None = None,
    *,
    env: Mapping[str, str] | None = None,
    stdin: int | None = None,
) -> Result:
    try:
        proc = subprocess.run(
            list(command),
            cwd=cwd,
            text=True,
            capture_output=True,
            env=dict(env) if env is not None else None,
            stdin=stdin,
        )
    except FileNotFoundError:
        return Result(127, "", f"{command[0]} is not installed or not on PATH.")
    return Result(proc.returncode, proc.stdout, proc.stderr)


def checked(
    command: Sequence[str],
    cwd: Path | None = None,
    *,
    env: Mapping[str, str] | None = None,
    stdin: int | None = None,
) -> Result:
    result = run(command, cwd, env=env, stdin=stdin)
    if result.returncode:
        raise GitStackError((result.stderr or result.stdout or "command failed").strip(), exit_code=result.returncode)
    return result


def normalize_remote(value: str) -> str | None:
    repo = re.sub(r"^git@[^:]+:", "", value.strip())
    repo = re.sub(r"^https?://[^/]+/", "", repo)
    repo = re.sub(r"^ssh://[^/]+/", "", repo)
    repo = re.sub(r"^git://[^/]+/", "", repo)
    repo = re.sub(r"\.git$", "", repo).rstrip("/")
    return repo if REPO_PATTERN.fullmatch(repo) else None


def resolve_repo(value: str | None = None, cwd: Path | None = None) -> dict[str, Any]:
    if value:
        if not REPO_PATTERN.fullmatch(value.strip()):
            raise GitStackError(f"Invalid repository '{value}'. Use owner/repo.", code="invalid_arguments", exit_code=64)
        repo = value.strip()
        return {"repo": repo, "source": "argument", "root": None}
    root_result = checked(["git", "rev-parse", "--show-toplevel"], cwd)
    root = Path(root_result.stdout.strip())
    remote = checked(["git", "remote", "get-url", "origin"], root).stdout.strip()
    repo = normalize_remote(remote)
    if not repo:
        raise GitStackError("Could not resolve owner/repo from origin remote.", code="repo_context_missing", exit_code=3)
    return {"repo": repo, "source": "origin", "root": str(root), "remote": remote}


def resolve_pr(repo: str | None = None, pr: str | None = None, cwd: Path | None = None) -> dict[str, Any]:
    context = resolve_repo(repo, cwd)
    args = ["gh", "pr", "view"]
    if pr:
        args.append(str(pr))
    args += ["--repo", context["repo"], "--json", "number,url,title,state,isDraft,headRefName,baseRefName"]
    result = checked(args, Path(context["root"]) if context.get("root") else cwd)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise GitStackError(f"Failed to parse gh JSON output: {exc}") from exc
    return {"repo": context["repo"], "source": "argument" if pr else "current_branch", "pull_request": data}


def envelope(command: list[str], data: Any) -> dict[str, Any]:
    return {"ok": True, "version": __version__, "command": command, "data": data}


def error_envelope(command: list[str], exc: GitStackError) -> dict[str, Any]:
    error: dict[str, Any] = {"code": exc.code, "message": str(exc)}
    if exc.details is not None:
        error["details"] = exc.details
    return {"ok": False, "version": __version__, "command": command, "error": error}
