from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .repository import is_repo_reference, normalize_remote
from .review_types import ReviewError, RunResult


def run(command: list[str], *, cwd: Path | None = None) -> RunResult:
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    except FileNotFoundError:
        return RunResult(127, "", f"{command[0]} is not installed or not on PATH.")
    return RunResult(completed.returncode, completed.stdout, completed.stderr)


def gh_json(args: list[str], *, runner: Callable[[list[str]], RunResult]) -> object:
    result = runner(args)
    if result.returncode != 0:
        raise ReviewError(
            (result.stderr or result.stdout or "gh command failed").strip(),
            exit_code=result.returncode,
        )
    try:
        return json.loads(result.stdout or "null")
    except json.JSONDecodeError as exc:
        raise ReviewError(f"Failed to parse gh JSON output: {exc}") from exc


def paginated_list(
    endpoint: str, *, fetch_json: Callable[[list[str]], object]
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    page = 1
    while True:
        payload = fetch_json(
            [
                "api",
                endpoint,
                "-X",
                "GET",
                "-F",
                "per_page=100",
                "-F",
                f"page={page}",
                "-H",
                "Accept: application/vnd.github+json",
            ]
        )
        if not isinstance(payload, list):
            raise ReviewError(f"Unexpected response shape for {endpoint}.")
        items.extend(item for item in payload if isinstance(item, dict))
        if len(payload) < 100:
            return items
        page += 1


def graphql(
    query: str,
    variables: dict[str, object],
    *,
    fetch_json: Callable[[list[str]], object],
) -> object:
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        args.extend(["-F", f"{key}={'null' if value is None else value}"])
    return fetch_json(args)


def validate_repo(repo: str) -> str:
    value = repo.strip()
    if not is_repo_reference(value):
        raise ReviewError(
            f"Invalid repository '{repo}'. Use owner/repo.",
            code="invalid_arguments",
            exit_code=64,
        )
    return value


def resolve_repo(
    repo: str | None,
    *,
    allow_non_project: bool,
    runner: Callable[..., RunResult],
) -> str:
    if repo:
        return validate_repo(repo)
    root = runner(["git", "rev-parse", "--show-toplevel"])
    if root.returncode != 0:
        if allow_non_project:
            raise ReviewError(
                "Pass --repo owner/repo when using --allow-non-project.",
                code="repo_context_missing",
                exit_code=2,
            )
        raise ReviewError(
            "No git repository detected. Pass --repo owner/repo.",
            code="repo_context_missing",
            exit_code=3,
        )
    remote = runner(
        ["git", "remote", "get-url", "origin"], cwd=Path(root.stdout.strip())
    )
    if remote.returncode != 0:
        raise ReviewError(
            "No origin remote found. Pass --repo owner/repo.",
            code="repo_context_missing",
            exit_code=4,
        )
    resolved = normalize_remote(remote.stdout.strip())
    if not resolved:
        raise ReviewError(
            "Could not resolve owner/repo from origin remote.",
            code="repo_context_missing",
            exit_code=5,
        )
    return resolved
