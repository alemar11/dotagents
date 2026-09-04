from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Sequence

from .ci_types import GhResult, InspectionError
from .repository import is_repo_reference, normalize_remote

ACTIONS_API_VERSION = "2022-11-28"


def run_gh_command(args: Sequence[str], cwd: Path | None, *, backend: Any) -> GhResult:
    process = subprocess.run(["gh", *args], cwd=cwd, text=True, capture_output=True)
    return GhResult(process.returncode, process.stdout, process.stderr)


def run_gh_command_raw(
    args: Sequence[str], cwd: Path | None, *, backend: Any
) -> tuple[int, bytes, str]:
    process = subprocess.run(["gh", *args], cwd=cwd, capture_output=True)
    return (process.returncode, process.stdout, process.stderr.decode(errors="replace"))


def run_git_command(args: Sequence[str], cwd: Path | None, *, backend: Any) -> GhResult:
    process = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)
    return GhResult(process.returncode, process.stdout, process.stderr)


def find_git_root(start: Path | None = None, *, backend: Any) -> Path | None:
    result = backend.run_git_command(
        ["rev-parse", "--show-toplevel"], cwd=start or Path.cwd()
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())


def fetch_actions_endpoint(
    endpoint: str, repo_root: Path | None, *, backend: Any
) -> dict[str, Any]:
    result = backend.run_gh_command(
        [
            "api",
            endpoint,
            "--method",
            "GET",
            "--header",
            "Accept: application/vnd.github+json",
            "--header",
            f"X-GitHub-Api-Version: {ACTIONS_API_VERSION}",
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "").strip()
        raise InspectionError(message or f"gh api failed for {endpoint}.", 1)
    try:
        data = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise InspectionError(
            f"Unable to parse GitHub Actions permissions JSON: {exc}", 1
        ) from exc
    if not isinstance(data, dict):
        raise InspectionError(
            "GitHub Actions permissions endpoint returned an unexpected JSON shape.", 1
        )
    return data


def inspect_actions_permissions(
    *, repo: str, repo_root: Path | None, backend: Any
) -> dict[str, Any]:
    backend.ensure_gh_available(repo_root)
    actions = backend.fetch_actions_endpoint(
        f"repos/{repo}/actions/permissions", repo_root
    )
    workflow = backend.fetch_actions_endpoint(
        f"repos/{repo}/actions/permissions/workflow", repo_root
    )
    actions_enabled = actions.get("enabled")
    default_workflow_permissions = workflow.get("default_workflow_permissions")
    can_approve = workflow.get("can_approve_pull_request_reviews")
    if not isinstance(actions_enabled, bool):
        raise InspectionError(
            "GitHub Actions permissions response omitted the enabled flag.", 1
        )
    if default_workflow_permissions not in {"read", "write"}:
        raise InspectionError(
            "GitHub Actions permissions response has an invalid default permission value.",
            1,
        )
    if not isinstance(can_approve, bool):
        raise InspectionError(
            "GitHub Actions workflow permissions response omitted the PR approval flag.",
            1,
        )
    if not actions_enabled:
        repository_gate = "blocked"
        warning = "The workflow may be written, but GitHub Actions is disabled and cannot run until it is enabled."
    elif not can_approve:
        repository_gate = "blocked"
        warning = "The workflow may be written, but its pull-request operation will not work until the repository setting is enabled."
    else:
        repository_gate = "enabled"
        warning = None
    return {
        "repository": repo,
        "actions_enabled": actions_enabled,
        "default_workflow_permissions": default_workflow_permissions,
        "can_approve_pull_request_reviews": can_approve,
        "pull_requests_write": {
            "repository_gate": repository_gate,
            "workflow_declaration": {"contents": "read", "pull-requests": "write"},
            "effective": "not-verifiable-before-workflow-run",
        },
        "workflow_authoring": {
            "status": "allowed-with-warning" if warning else "ready",
            "warning": warning,
        },
        "contents_write_required_for": ["branch", "tag"],
        "limitations": [
            "The repository API exposes the Actions setting and workflow defaults, not the effective token permissions of a future workflow.",
            "The workflow must declare pull-requests: write explicitly; use contents: write when it creates branches or tags.",
            "A missing or forbidden API response can reflect token scope, plan, account, organization, or enterprise policy.",
        ],
    }


def ensure_gh_available(cwd: Path | None, *, backend: Any) -> None:
    if backend.which("gh") is None:
        raise InspectionError("gh is not installed or not on PATH.", 127)
    result = backend.run_gh_command(["auth", "status"], cwd=cwd)
    if result.returncode == 0:
        return
    message = (result.stderr or result.stdout or "").strip()
    raise InspectionError(message or "gh not authenticated.", 1)


def validate_repo_reference(repo: str, *, backend: Any) -> str:
    value = repo.strip()
    if not is_repo_reference(value):
        raise InspectionError(f"Invalid --repo value '{repo}'. Use owner/repo.", 64)
    return value


def normalize_remote_url(remote: str | None, *, backend: Any) -> str | None:
    return normalize_remote(remote)


def resolve_repo_from_checkout(repo_root: Path, *, backend: Any) -> str:
    result = backend.run_git_command(["remote", "get-url", "origin"], cwd=repo_root)
    if result.returncode != 0:
        raise InspectionError("No origin remote found. Pass --repo <owner/repo>.", 4)
    repo = backend.normalize_remote_url(result.stdout.strip())
    if repo is None:
        raise InspectionError(
            f"Could not resolve owner/repo from git remote: {result.stdout.strip()}", 5
        )
    return repo


def resolve_repo_context(
    repo_ref: str | None, *, allow_non_project: bool, backend: Any
) -> tuple[str, Path | None]:
    repo_root = backend.find_git_root()
    if repo_ref:
        repo = backend.validate_repo_reference(repo_ref)
        if repo_root is None and (not allow_non_project):
            raise InspectionError(
                "No git repository detected. Pass --allow-non-project with --repo <owner/repo>.",
                3,
            )
        return (repo, repo_root)
    if repo_root is None:
        raise InspectionError(
            "No git repository detected. Pass --repo <owner/repo> for non-project operations.",
            3,
        )
    return (backend.resolve_repo_from_checkout(repo_root), repo_root)


def append_repo_flag(args: list[str], repo: str, *, backend: Any) -> list[str]:
    return [*args, "--repo", repo]


def resolve_pr(
    pr_value: str | None, repo: str, repo_root: Path | None, *, backend: Any
) -> str:
    if pr_value:
        if pr_value.startswith("http://") or pr_value.startswith("https://"):
            match = re.search("/pull/(\\d+)", pr_value)
            if match:
                return match.group(1)
        return pr_value
    result = backend.run_gh_command(
        backend.append_repo_flag(["pr", "view", "--json", "number"], repo),
        cwd=repo_root,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "").strip()
        raise InspectionError(message or "Error: unable to resolve PR.", 1)
    try:
        data = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise InspectionError(f"Error: unable to parse PR JSON: {exc}", 1) from exc
    number = data.get("number")
    if not number:
        raise InspectionError("Error: no PR number found. Provide --pr explicitly.", 1)
    return str(number)
