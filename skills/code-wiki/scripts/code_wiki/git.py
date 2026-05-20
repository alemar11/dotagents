"""Git metadata helpers for code-wiki."""

from __future__ import annotations

import subprocess
from pathlib import Path
from urllib.parse import urlparse


def git_output(repo: Path, *args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    output = completed.stdout.strip()
    return output or None


def normalize_github_web_url(remote_url: str | None) -> tuple[str | None, str | None]:
    if not remote_url:
        return None, None

    value = remote_url.strip()
    path: str | None = None

    if value.startswith("git@github.com:"):
        path = value.split(":", 1)[1]
    elif value.startswith("ssh://"):
        parsed = urlparse(value)
        if parsed.hostname and parsed.hostname.lower() == "github.com":
            path = parsed.path.lstrip("/")
    else:
        parsed = urlparse(value)
        if parsed.hostname and parsed.hostname.lower() in {"github.com", "www.github.com"}:
            path = parsed.path.lstrip("/")

    if not path:
        return None, None

    path = path.removesuffix(".git").strip("/")
    parts = [part for part in path.split("/") if part]
    if len(parts) < 2:
        return None, None

    return f"https://github.com/{parts[0]}/{parts[1]}", "github"


def git_metadata(repo: Path) -> dict[str, object]:
    inside = git_output(repo, "rev-parse", "--is-inside-work-tree") == "true"
    commit = git_output(repo, "rev-parse", "HEAD") if inside else None
    branch = git_output(repo, "rev-parse", "--abbrev-ref", "HEAD") if inside else None
    if branch == "HEAD":
        branch = None
    remote_url = git_output(repo, "config", "--get", "remote.origin.url") if inside else None
    web_url, host = normalize_github_web_url(remote_url)
    dirty = bool(git_output(repo, "status", "--short")) if inside else None

    return {
        "has_git_directory": (repo / ".git").exists(),
        "is_git_worktree": inside,
        "remote_url": remote_url,
        "web_url": web_url,
        "host": host,
        "commit": commit,
        "branch": branch,
        "dirty": dirty,
    }

