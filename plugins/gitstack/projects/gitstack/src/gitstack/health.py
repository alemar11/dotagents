from __future__ import annotations

import json
import platform
import shutil

from . import __version__
from .common import run


AUTH_STATUS_COMMAND = [
    "gh",
    "auth",
    "status",
    "--active",
    "--hostname",
    "github.com",
    "--json",
    "hosts",
]


def _authentication_status() -> str:
    result = run(AUTH_STATUS_COMMAND)
    try:
        payload = json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError):
        return "unverified"

    hosts = payload.get("hosts") if isinstance(payload, dict) else None
    accounts = hosts.get("github.com") if isinstance(hosts, dict) else None
    if not isinstance(accounts, list):
        return "unverified"

    active = [
        account
        for account in accounts
        if isinstance(account, dict) and account.get("active") is True
    ]
    if len(active) != 1:
        return "unverified"
    return "verified" if active[0].get("state") == "success" else "unverified"


def doctor() -> dict[str, object]:
    git = shutil.which("git")
    gh = shutil.which("gh")
    authentication_status = _authentication_status() if gh else "not-checked"
    root = run(["git", "rev-parse", "--show-toplevel"]) if git else None
    return {
        "ok": bool(git and gh),
        "provider_ready": authentication_status == "verified",
        "version": __version__,
        "checks": {
            "python": {"ok": True, "version": platform.python_version(), "minimum": "3.11"},
            "git": {"ok": bool(git), "path": git},
            "gh": {
                "ok": bool(gh),
                "path": gh,
                "authenticated": authentication_status == "verified",
                "authentication_status": authentication_status,
                "authentication_source": "provider-default" if gh else "missing",
            },
            "repository": {"inside_worktree": bool(root and root.returncode == 0), "root": root.stdout.strip() if root and root.returncode == 0 else None},
            "connector": {"availability": "model-runtime-only", "cli_access": False},
        },
    }


def doctor_text(payload: dict[str, object], heading: str | None = None) -> str:
    checks = payload["checks"]
    assert isinstance(checks, dict)
    gh = checks["gh"]
    assert isinstance(gh, dict)
    if not gh["ok"]:
        gh_state = "missing"
    elif gh["authentication_status"] == "verified":
        gh_state = "installed; authentication verified"
    else:
        gh_state = "installed; authentication unverified"

    lines = [heading or f"gitstack {__version__}"]
    lines.extend(
        [
            f"git: {'ok' if checks['git']['ok'] else 'missing'}",
            f"gh: {gh_state}",
            f"provider: {'ready' if payload['provider_ready'] else 'unverified'}",
            f"repository: {'ok' if checks['repository']['inside_worktree'] else 'not detected'}",
        ]
    )
    if "connector" in checks:
        lines.append("connector: model-runtime-only")
    return "\n".join(lines)
