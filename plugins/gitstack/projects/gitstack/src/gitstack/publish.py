from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .common import GitStackError, REPO_PATTERN, checked, normalize_remote, run


def _find_open_pr(repo: str, branch: str, root: Path) -> dict[str, Any] | None:
    owner, name = repo.split("/", 1)
    result = checked(
        [
            "gh", "pr", "list", "--repo", repo, "--state", "open",
            "--head", f"{owner}:{branch}", "--limit", "2", "--json",
            "number,url,title,state,isDraft,headRefName,headRepositoryOwner,headRepository",
        ],
        root,
    )
    try:
        matches = json.loads(result.stdout or "[]")
    except json.JSONDecodeError as exc:
        raise GitStackError(f"Could not parse open PR lookup: {exc}") from exc
    if not isinstance(matches, list):
        raise GitStackError("Open PR lookup returned an unexpected response.")
    if not matches:
        return None
    if len(matches) > 1:
        raise GitStackError(
            f"Multiple open PRs match {repo}:{branch}; select one explicitly.",
            code="ambiguous_pull_request",
            exit_code=65,
        )
    match = matches[0]
    owner_value = match.get("headRepositoryOwner")
    repo_value = match.get("headRepository")
    head_owner = owner_value.get("login") if isinstance(owner_value, dict) else owner_value
    head_repo = repo_value.get("name") if isinstance(repo_value, dict) else repo_value
    if match.get("state") != "OPEN" or match.get("headRefName") != branch or head_owner != owner or head_repo != name:
        raise GitStackError(
            "Open PR lookup returned a PR from an unexpected head repository or branch.",
            code="pull_request_mismatch",
            exit_code=65,
        )
    return match


def preflight(repo: str | None = None) -> dict[str, Any]:
    root_result = checked(["git", "rev-parse", "--show-toplevel"])
    root = Path(root_result.stdout.strip())
    origin_url = checked(["git", "remote", "get-url", "origin"], root).stdout.strip()
    origin_repo = normalize_remote(origin_url)
    if not origin_repo:
        raise GitStackError("Could not resolve owner/repo from origin.", code="repo_context_missing", exit_code=3)
    if repo and not REPO_PATTERN.fullmatch(repo.strip()):
        raise GitStackError(f"Invalid repository '{repo}'. Use owner/repo.", code="invalid_arguments", exit_code=64)
    selected_repo = repo.strip() if repo else origin_repo
    if selected_repo != origin_repo:
        raise GitStackError(
            f"Explicit repository '{selected_repo}' does not match origin '{origin_repo}'.",
            code="repo_mismatch",
            exit_code=65,
        )
    checked(["gh", "auth", "status"], root)
    branch = checked(["git", "branch", "--show-current"], root).stdout.strip()
    if not branch:
        raise GitStackError("Refusing to publish from a detached HEAD.", code="unsafe_branch", exit_code=65)
    status = checked(["git", "status", "--short", "--branch"], root).stdout.splitlines()
    default_branch = checked(
        ["gh", "repo", "view", selected_repo, "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"],
        root,
    ).stdout.strip()
    if not default_branch:
        raise GitStackError("Could not resolve the repository default branch.", code="repo_context_missing", exit_code=3)
    if branch == default_branch:
        raise GitStackError("Refusing to publish from the default branch.", code="unsafe_branch", exit_code=65)
    remote_config = run(["git", "config", "--get", f"branch.{branch}.remote"], root)
    merge_config = run(["git", "config", "--get", f"branch.{branch}.merge"], root)
    remote_name = remote_config.stdout.strip() if remote_config.returncode == 0 else None
    merge_ref = merge_config.stdout.strip() if merge_config.returncode == 0 else None
    if bool(remote_name) != bool(merge_ref):
        raise GitStackError(
            "Branch upstream configuration is incomplete; expected both remote and merge ref.",
            code="upstream_mismatch",
            exit_code=65,
        )
    expected_upstream = f"origin/{branch}"
    upstream_name: str | None = None
    ahead = 0
    behind = 0
    if remote_name is not None and merge_ref is not None:
        expected_merge = f"refs/heads/{branch}"
        if remote_name != "origin" or merge_ref != expected_merge:
            actual = f"{remote_name}:{merge_ref}"
            raise GitStackError(
                f"Expected upstream 'origin:{expected_merge}', found '{actual}'.",
                code="upstream_mismatch",
                exit_code=65,
            )
        upstream_name = expected_upstream
        counts = checked(["git", "rev-list", "--left-right", "--count", f"HEAD...{upstream_name}"], root).stdout.split()
        if len(counts) != 2 or not all(item.isdigit() for item in counts):
            raise GitStackError("Could not determine upstream ahead/behind state.", code="upstream_mismatch", exit_code=65)
        ahead, behind = (int(item) for item in counts)
        if behind:
            raise GitStackError(
                f"Local branch is behind '{upstream_name}' by {behind} commit(s).",
                code="upstream_mismatch",
                exit_code=65,
            )
    existing = _find_open_pr(selected_repo, branch, root)
    return {
        "repo": selected_repo, "root": str(root), "branch": branch,
        "origin": origin_url, "default_branch": default_branch,
        "on_default_branch": False, "upstream": upstream_name,
        "upstream_valid": True, "ahead": ahead, "behind": behind,
        "needs_push": upstream_name is None or ahead > 0,
        "dirty": any(line and not line.startswith("##") for line in status),
        "status": status, "existing_pull_request": existing,
    }


def template(title: str | None, body_file: str | None) -> dict[str, Any]:
    body = ""
    if body_file:
        try:
            body = Path(body_file).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise GitStackError(f"Could not read body file '{body_file}': {exc}", code="invalid_arguments", exit_code=64) from exc
    return {"title": title or "", "body": body, "draft": True}


def open_pr(*, repo: str | None, title: str, body_file: str, draft: bool, base: str | None, dry_run: bool) -> dict[str, Any]:
    state = preflight(repo)
    if state["on_default_branch"]:
        raise GitStackError("Refusing to publish from the default branch.", code="unsafe_branch", exit_code=65)
    if state["dirty"]:
        raise GitStackError("Working tree is dirty; commit or stash changes before publishing.", code="dirty_worktree", exit_code=65)
    if state.get("needs_push"):
        raise GitStackError(
            "Branch has no origin upstream; push it with tracking before opening a PR.",
            code="branch_not_pushed",
            exit_code=65,
        )
    if state["existing_pull_request"]:
        return {"status": "reused", "pull_request": state["existing_pull_request"], "preflight": state}
    command = ["gh", "pr", "create", "--repo", state["repo"], "--title", title, "--body-file", body_file]
    if draft:
        command.append("--draft")
    if base:
        command += ["--base", base]
    if dry_run:
        return {"status": "dry-run", "command": command, "preflight": state}
    result = checked(command, Path(state["root"]))
    url = result.stdout.strip()
    return {"status": "created", "url": url, "preflight": state}
