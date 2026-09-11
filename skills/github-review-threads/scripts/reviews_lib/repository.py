from __future__ import annotations

import re

REPO_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")


def is_repo_reference(value: str) -> bool:
    """Return whether *value* is an exact ``owner/repo`` reference."""

    return REPO_PATTERN.fullmatch(value.strip()) is not None


def normalize_remote(value: str | None) -> str | None:
    """Normalize a common Git remote URL to ``owner/repo`` when possible."""

    if not value:
        return None
    repo = re.sub(r"^git@[^:]+:", "", value.strip())
    repo = re.sub(r"^https?://[^/]+/", "", repo)
    repo = re.sub(r"^ssh://[^/]+/", "", repo)
    repo = re.sub(r"^git://[^/]+/", "", repo)
    repo = re.sub(r"\.git$", "", repo).rstrip("/")
    return repo if is_repo_reference(repo) else None
