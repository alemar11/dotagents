from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from shutil import which  # noqa: F401 - injected into ci_provider for compatibility tests
from typing import Any, Sequence


from . import __version__ as VERSION
from .health import doctor as shared_doctor, doctor_text
from .ci_output import (
    extract_failure_snippet,
    extract_job_id,
    extract_log_from_job_archive,
    extract_run_id,
    is_log_pending_message,
    normalize_field,
    parse_available_fields,
    render_results,
    tail_lines,
)
from .ci_types import GhResult, InspectionError
from . import ci_provider

FAILURE_CONCLUSIONS = {
    "failure",
    "cancelled",
    "timed_out",
    "action_required",
}

FAILURE_STATES = {
    "failure",
    "error",
    "cancelled",
    "timed_out",
    "action_required",
}

FAILURE_BUCKETS = {"fail"}

DEFAULT_MAX_LINES = 160
DEFAULT_CONTEXT_LINES = 30
ACTIONS_API_VERSION = "2022-11-28"
CI_COMMANDS = ("inspect", "permissions")
RUN_METADATA_FIELDS = [
    "conclusion",
    "status",
    "workflowName",
    "name",
    "event",
    "headBranch",
    "headSha",
    "url",
]

PRIMARY_CHECK_FIELDS = [
    "name",
    "state",
    "conclusion",
    "detailsUrl",
    "startedAt",
    "completedAt",
]

FALLBACK_CHECK_FIELDS = [
    "name",
    "state",
    "bucket",
    "link",
    "startedAt",
    "completedAt",
    "workflow",
    "conclusion",
    "event",
]


def _ci_backend() -> Any:
    return sys.modules[__name__]


def run_gh_command(args: Sequence[str], cwd: Path | None) -> GhResult:
    return ci_provider.run_gh_command(args, cwd, backend=_ci_backend())


def run_gh_command_raw(args: Sequence[str], cwd: Path | None) -> tuple[int, bytes, str]:
    return ci_provider.run_gh_command_raw(args, cwd, backend=_ci_backend())


def run_git_command(args: Sequence[str], cwd: Path | None) -> GhResult:
    return ci_provider.run_git_command(args, cwd, backend=_ci_backend())


def find_git_root(start: Path | None = None) -> Path | None:
    return ci_provider.find_git_root(start, backend=_ci_backend())


def fetch_actions_endpoint(endpoint: str, repo_root: Path | None) -> dict[str, Any]:
    return ci_provider.fetch_actions_endpoint(
        endpoint, repo_root, backend=_ci_backend()
    )


def inspect_actions_permissions(*, repo: str, repo_root: Path | None) -> dict[str, Any]:
    return ci_provider.inspect_actions_permissions(
        repo=repo, repo_root=repo_root, backend=_ci_backend()
    )


def ensure_gh_available(cwd: Path | None) -> None:
    return ci_provider.ensure_gh_available(cwd, backend=_ci_backend())


def validate_repo_reference(repo: str) -> str:
    return ci_provider.validate_repo_reference(repo, backend=_ci_backend())


def normalize_remote_url(remote: str | None) -> str | None:
    return ci_provider.normalize_remote_url(remote, backend=_ci_backend())


def resolve_repo_from_checkout(repo_root: Path) -> str:
    return ci_provider.resolve_repo_from_checkout(repo_root, backend=_ci_backend())


def resolve_repo_context(
    repo_ref: str | None, *, allow_non_project: bool
) -> tuple[str, Path | None]:
    return ci_provider.resolve_repo_context(
        repo_ref, allow_non_project=allow_non_project, backend=_ci_backend()
    )


def append_repo_flag(args: list[str], repo: str) -> list[str]:
    return ci_provider.append_repo_flag(args, repo, backend=_ci_backend())


def resolve_pr(pr_value: str | None, repo: str, repo_root: Path | None) -> str:
    return ci_provider.resolve_pr(pr_value, repo, repo_root, backend=_ci_backend())


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect failing GitHub PR checks or read the repository GitHub Actions "
            "permissions preflight."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=CI_COMMANDS,
        default="inspect",
        help="inspect failing checks or permissions for creating pull requests",
    )
    parser.add_argument(
        "--repo",
        default=None,
        help="Target repository as owner/repo. Defaults to the current checkout.",
    )
    parser.add_argument(
        "--pr",
        default=None,
        help="PR number or URL (defaults to current branch PR).",
    )
    parser.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    parser.add_argument("--context", type=int, default=DEFAULT_CONTEXT_LINES)
    parser.add_argument(
        "--allow-non-project",
        action="store_true",
        help="Allow use outside a local git checkout when --repo is provided.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of human-readable output.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def doctor_payload() -> dict[str, object]:
    return shared_doctor()


def emit_doctor(json_mode: bool) -> int:
    payload = doctor_payload()
    if json_mode:
        print(json.dumps(payload, indent=2))
    else:
        print(doctor_text(payload, f"g ci inspect {VERSION}"))
    return 0 if payload["ok"] else 1


def emit_success(data: object, command: list[str]) -> None:
    print(
        json.dumps(
            {"ok": True, "version": VERSION, "command": command, "data": data}, indent=2
        )
    )


def emit_error(exc: InspectionError, command: list[str]) -> None:
    print(
        json.dumps(
            {
                "ok": False,
                "version": VERSION,
                "command": command,
                "error": {
                    "code": "inspection_error",
                    "message": exc.message,
                },
            },
            indent=2,
        )
    )


def render_permissions(payload: dict[str, Any]) -> str:
    actions = "enabled" if payload["actions_enabled"] else "disabled"
    approval = "enabled" if payload["can_approve_pull_request_reviews"] else "disabled"
    pull_requests = payload["pull_requests_write"]
    lines = [
        f"Repository: {payload['repository']}",
        f"GitHub Actions: {actions}",
        f"Workflow default permissions: {payload['default_workflow_permissions']}",
        f"PR create/approve repository setting: {approval}",
        "Required workflow permissions: contents: read, pull-requests: write",
        f"pull-requests: write repository gate: {pull_requests['repository_gate']}",
        "contents: write is required when the workflow creates branches or tags.",
        "The effective token permission must still be verified from the workflow and its run.",
    ]
    warning = payload["workflow_authoring"]["warning"]
    if warning:
        lines.append(f"Warning: {warning}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    if raw_argv == ["--version"]:
        print(VERSION)
        return 0
    if raw_argv == ["doctor"]:
        return emit_doctor(False)
    if raw_argv == ["--json", "doctor"]:
        return emit_doctor(True)

    args = parse_args(argv)
    try:
        repo, repo_root = resolve_repo_context(
            args.repo,
            allow_non_project=args.allow_non_project,
        )
        if args.command == "permissions":
            payload = inspect_actions_permissions(repo=repo, repo_root=repo_root)
            if args.json:
                emit_success(payload, ["permissions"])
            else:
                print(render_permissions(payload), end="")
            return 0
        payload, exit_code = inspect_pr_failures(
            repo=repo,
            repo_root=repo_root,
            pr_value=args.pr,
            max_lines=max(1, args.max_lines),
            context=max(1, args.context),
        )
    except InspectionError as exc:
        if args.json:
            emit_error(exc, [args.command])
        else:
            print(exc.message, file=sys.stderr)
        return exc.exit_code

    if args.json:
        emit_success(payload, ["inspect"])
    else:
        print(render_results(payload), end="")
    return exit_code


def inspect_pr_failures(
    *,
    repo: str,
    repo_root: Path | None,
    pr_value: str | None,
    max_lines: int,
    context: int,
) -> tuple[dict[str, Any], int]:
    ensure_gh_available(repo_root)
    pr_number = resolve_pr(pr_value, repo, repo_root)
    checks = fetch_checks(pr_number, repo, repo_root)
    failing = [check for check in checks if is_failing(check)]
    payload: dict[str, Any] = {
        "repo": repo,
        "pr": pr_number,
        "checkCount": len(checks),
        "failingCount": len(failing),
        "results": [],
    }
    if not checks:
        payload["summary"] = "no_checks"
        payload["message"] = f"PR #{pr_number}: no checks configured or reported."
        return payload, 0
    if not failing:
        payload["summary"] = "no_failing_checks"
        payload["message"] = f"PR #{pr_number}: no failing checks detected."
        return payload, 0

    payload["summary"] = "failing_checks"
    payload["results"] = [
        analyze_check(
            check,
            repo=repo,
            repo_root=repo_root,
            max_lines=max_lines,
            context=context,
        )
        for check in failing
    ]
    payload["message"] = f"PR #{pr_number}: {len(failing)} failing checks analyzed."
    return payload, 1


def fetch_checks(
    pr_value: str, repo: str, repo_root: Path | None
) -> list[dict[str, Any]]:
    fallback_field_sets = [PRIMARY_CHECK_FIELDS, FALLBACK_CHECK_FIELDS]
    index = 0
    result: GhResult | None = None
    seen_field_sets = {tuple(fields) for fields in fallback_field_sets}

    while index < len(fallback_field_sets):
        fields = fallback_field_sets[index]
        result = run_gh_command(
            append_repo_flag(
                ["pr", "checks", pr_value, "--json", ",".join(fields)], repo
            ),
            cwd=repo_root,
        )
        if result.returncode == 0:
            break

        message = (result.stderr or result.stdout or "").strip()
        available_fields = parse_available_fields(message)
        discovered_fields = [
            field for field in FALLBACK_CHECK_FIELDS if field in available_fields
        ]
        if discovered_fields:
            discovered_tuple = tuple(discovered_fields)
            if discovered_tuple not in seen_field_sets:
                fallback_field_sets.append(discovered_fields)
                seen_field_sets.add(discovered_tuple)
        index += 1

    if result is None or result.returncode != 0:
        if confirm_empty_check_rollup(pr_value, repo, repo_root):
            return []
        message = (
            (result.stderr or result.stdout or "").strip() if result is not None else ""
        )
        if index > 1:
            raise InspectionError(
                "Error: gh pr checks failed and no compatible field list succeeded.",
                1,
            )
        raise InspectionError(message or "Error: gh pr checks failed.", 1)

    try:
        data = json.loads(result.stdout or "[]")
    except json.JSONDecodeError as exc:
        raise InspectionError(f"Error: unable to parse checks JSON: {exc}", 1) from exc
    if not isinstance(data, list):
        raise InspectionError("Error: unexpected checks JSON shape.", 1)
    return data


def confirm_empty_check_rollup(
    pr_value: str,
    repo: str,
    repo_root: Path | None,
) -> bool:
    result = run_gh_command(
        append_repo_flag(
            ["pr", "view", pr_value, "--json", "statusCheckRollup"],
            repo,
        ),
        cwd=repo_root,
    )
    if result.returncode != 0:
        return False
    try:
        data = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return False
    if not isinstance(data, dict):
        return False
    rollup = data.get("statusCheckRollup")
    return isinstance(rollup, list) and not rollup


def is_failing(check: dict[str, Any]) -> bool:
    conclusion = normalize_field(check.get("conclusion"))
    if conclusion in FAILURE_CONCLUSIONS:
        return True
    state = normalize_field(check.get("state") or check.get("status"))
    if state in FAILURE_STATES:
        return True
    bucket = normalize_field(check.get("bucket"))
    return bucket in FAILURE_BUCKETS


def analyze_check(
    check: dict[str, Any],
    *,
    repo: str,
    repo_root: Path | None,
    max_lines: int,
    context: int,
) -> dict[str, Any]:
    url = check.get("detailsUrl") or check.get("link") or ""
    run_id = extract_run_id(url)
    job_id = extract_job_id(url)
    base: dict[str, Any] = {
        "name": check.get("name", ""),
        "detailsUrl": url,
        "runId": run_id,
        "jobId": job_id,
    }

    if run_id is None:
        base["status"] = "external"
        base["note"] = "No GitHub Actions run id detected in details URL."
        return base

    metadata = fetch_run_metadata(run_id, repo, repo_root)
    if metadata is not None:
        base["run"] = metadata

    log_text, log_error, log_status = fetch_check_log(
        run_id=run_id,
        job_id=job_id,
        repo=repo,
        repo_root=repo_root,
    )

    if log_status == "pending":
        base["status"] = "log_pending"
        base["note"] = log_error or "Logs are not available yet."
        return base

    if log_error:
        base["status"] = "log_unavailable"
        base["error"] = log_error
        return base

    base["status"] = "ok"
    base["logSnippet"] = extract_failure_snippet(
        log_text, max_lines=max_lines, context=context
    )
    base["logTail"] = tail_lines(log_text, max_lines)
    return base


def fetch_run_metadata(
    run_id: str, repo: str, repo_root: Path | None
) -> dict[str, Any] | None:
    result = run_gh_command(
        append_repo_flag(
            ["run", "view", run_id, "--json", ",".join(RUN_METADATA_FIELDS)], repo
        ),
        cwd=repo_root,
    )
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def fetch_check_log(
    *,
    run_id: str,
    job_id: str | None,
    repo: str,
    repo_root: Path | None,
) -> tuple[str, str, str]:
    log_text, log_error = fetch_run_log(run_id, repo, repo_root)
    if not log_error:
        return log_text, "", "ok"

    if is_log_pending_message(log_error) and job_id:
        job_log, job_error = fetch_job_log(job_id, repo, repo_root)
        if job_log:
            return job_log, "", "ok"
        if job_error and is_log_pending_message(job_error):
            return "", job_error, "pending"
        if job_error:
            return "", job_error, "error"
        return "", log_error, "pending"

    if is_log_pending_message(log_error):
        return "", log_error, "pending"
    return "", log_error, "error"


def fetch_run_log(run_id: str, repo: str, repo_root: Path | None) -> tuple[str, str]:
    result = run_gh_command(
        append_repo_flag(["run", "view", run_id, "--log"], repo),
        cwd=repo_root,
    )
    if result.returncode != 0:
        error = (result.stderr or result.stdout or "").strip()
        return "", error or "gh run view failed"
    return result.stdout, ""


def fetch_job_log(job_id: str, repo: str, repo_root: Path | None) -> tuple[str, str]:
    endpoint = f"/repos/{repo}/actions/jobs/{job_id}/logs"
    returncode, stdout_bytes, stderr = run_gh_command_raw(
        ["api", endpoint], cwd=repo_root
    )
    if returncode != 0:
        message = (stderr or "").strip() or "gh api job logs failed"
        return "", message

    log_text, parse_error = extract_log_from_job_archive(stdout_bytes)
    if parse_error:
        return "", parse_error
    return log_text, ""


if __name__ == "__main__":
    raise SystemExit(main())
