from __future__ import annotations

import platform
import shutil

from . import __version__
from .common import run


def doctor() -> dict[str, object]:
    git = shutil.which("git")
    gh = shutil.which("gh")
    auth = run(["gh", "auth", "status"]) if gh else None
    root = run(["git", "rev-parse", "--show-toplevel"]) if git else None
    return {
        "ok": bool(git and gh),
        "version": __version__,
        "checks": {
            "python": {"ok": True, "version": platform.python_version(), "minimum": "3.11"},
            "git": {"ok": bool(git), "path": git},
            "gh": {"ok": bool(gh), "path": gh, "authenticated": bool(auth and auth.returncode == 0)},
            "repository": {"inside_worktree": bool(root and root.returncode == 0), "root": root.stdout.strip() if root and root.returncode == 0 else None},
            "connector": {"availability": "model-runtime-only", "cli_access": False},
        },
    }
