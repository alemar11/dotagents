"""Read-only pilot readiness diagnostics."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from code_wiki.pilot.contracts import ContractError, load_graph
from code_wiki.pilot.provenance import provenance_key_status
from code_wiki.version import VERSION


def _command_output(command: list[str]) -> tuple[bool, str, str]:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as exc:
        return False, "", str(exc)
    return completed.returncode == 0, completed.stdout.strip(), completed.stderr.strip()


def doctor(skill_root: Path) -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {}
    checks["python"] = {
        "ok": sys.version_info >= (3, 11),
        "version": platform.python_version(),
        "minimum_version": "3.11",
    }
    git_path = shutil.which("git")
    git_ok, git_stdout, git_stderr = _command_output(["git", "--version"]) if git_path else (False, "", "git not found")
    checks["git"] = {
        "ok": git_ok,
        "path": git_path,
        "version": git_stdout,
        "error": git_stderr if not git_ok else None,
    }
    codex_path = shutil.which("codex")
    codex_ok, codex_stdout, codex_stderr = _command_output(["codex", "--version"]) if codex_path else (False, "", "codex not found")
    help_ok, help_stdout, help_stderr = _command_output(["codex", "exec", "--help"]) if codex_path else (False, "", "codex not found")
    required_help = {
        "json_events": "--json" in help_stdout,
        "ephemeral": "--ephemeral" in help_stdout,
        "explicit_model": "--model" in help_stdout,
        "explicit_working_directory": "--cd" in help_stdout,
        "non_repository_working_directory": "--skip-git-repo-check" in help_stdout,
        "additional_writable_directory": "--add-dir" in help_stdout,
        "workspace_write_sandbox": "workspace-write" in help_stdout,
    }
    checks["codex"] = {
        "ok": codex_ok and help_ok and all(required_help.values()),
        "path": codex_path,
        "version": codex_stdout,
        "exec_help": required_help,
        "error": (codex_stderr or help_stderr) if not (codex_ok and help_ok) else None,
    }
    try:
        baseline = load_graph(skill_root, "baseline")
        candidate = load_graph(skill_root, "node-graph")
    except (OSError, UnicodeError, ContractError) as exc:
        checks["node_contracts"] = {"ok": False, "error": str(exc)}
    else:
        checks["node_contracts"] = {
            "ok": True,
            "baseline_graph_sha256": baseline.graph_sha256,
            "baseline_node_count": len(baseline.nodes),
            "node_graph_sha256": candidate.graph_sha256,
            "node_graph_node_count": len(candidate.nodes),
        }
    signing = provenance_key_status()
    checks["provenance_signing"] = {
        **signing,
        "required_for": "live-pilot-run-and-comparison",
    }
    core_checks = [
        check for name, check in checks.items() if name != "provenance_signing"
    ]
    return {
        "ok": all(check.get("ok") is True for check in core_checks),
        "live_pilot_ready": all(check.get("ok") is True for check in checks.values()),
        "cli_version": VERSION,
        "model_invoked": False,
        "config_written": False,
        "checks": checks,
    }
