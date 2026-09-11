from __future__ import annotations

import re

REPO_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")


def is_repo_reference(value: str) -> bool:
    """Return whether *value* is an exact ``owner/repo`` reference."""

    return REPO_PATTERN.fullmatch(value.strip()) is not None
