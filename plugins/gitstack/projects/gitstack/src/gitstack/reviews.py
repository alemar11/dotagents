from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from shutil import which
from typing import Any


from . import __version__ as VERSION
REPO_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")
CODEX_LOGINS = {"chatgpt-codex-connector[bot]", "chatgpt-codex-connector"}
REVIEW_EXIT_CODES = {
    "clean": 0,
    "findings": 1,
    "not-requested": 2,
    "acknowledged": 2,
    "pending": 2,
    "stale": 3,
}


@dataclass(frozen=True)
class RunResult:
    returncode: int
    stdout: str
    stderr: str


class ReviewError(Exception):
    def __init__(self, message: str, *, code: str = "command_failed", exit_code: int = 1) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.exit_code = exit_code


def run(command: list[str], *, cwd: Path | None = None) -> RunResult:
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    except FileNotFoundError:
        return RunResult(127, "", f"{command[0]} is not installed or not on PATH.")
    return RunResult(completed.returncode, completed.stdout, completed.stderr)


def run_gh(args: list[str]) -> RunResult:
    return run(["gh", *args])


def gh_json(args: list[str]) -> object:
    result = run_gh(args)
    if result.returncode != 0:
        raise ReviewError((result.stderr or result.stdout or "gh command failed").strip(), exit_code=result.returncode)
    try:
        return json.loads(result.stdout or "null")
    except json.JSONDecodeError as exc:
        raise ReviewError(f"Failed to parse gh JSON output: {exc}") from exc


def gh_api_paginated_list(endpoint: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    page = 1
    while True:
        payload = gh_json(["api", endpoint, "-X", "GET", "-F", "per_page=100", "-F", f"page={page}", "-H", "Accept: application/vnd.github+json"])
        if not isinstance(payload, list):
            raise ReviewError(f"Unexpected response shape for {endpoint}.")
        items.extend([item for item in payload if isinstance(item, dict)])
        if len(payload) < 100:
            break
        page += 1
    return items


def graphql(query: str, variables: dict[str, object]) -> object:
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        if value is None:
            args.extend(["-F", f"{key}=null"])
        else:
            args.extend(["-F", f"{key}={value}"])
    return gh_json(args)


def validate_repo(repo: str) -> str:
    value = repo.strip()
    if not REPO_PATTERN.fullmatch(value):
        raise ReviewError(f"Invalid repository '{repo}'. Use owner/repo.", code="invalid_arguments", exit_code=64)
    return value


def normalize_remote(remote: str | None) -> str | None:
    if not remote:
        return None
    repo = re.sub(r"^git@[^:]+:", "", remote)
    repo = re.sub(r"^https?://[^/]+/", "", repo)
    repo = re.sub(r"^ssh://[^/]+/", "", repo)
    repo = re.sub(r"^git://[^/]+/", "", repo)
    repo = re.sub(r"\.git$", "", repo).rstrip("/")
    return repo if REPO_PATTERN.fullmatch(repo) else None


def resolve_repo(repo: str | None, *, allow_non_project: bool) -> str:
    if repo:
        return validate_repo(repo)
    root = run(["git", "rev-parse", "--show-toplevel"])
    if root.returncode != 0:
        if allow_non_project:
            raise ReviewError("Pass --repo owner/repo when using --allow-non-project.", code="repo_context_missing", exit_code=2)
        raise ReviewError("No git repository detected. Pass --repo owner/repo.", code="repo_context_missing", exit_code=3)
    remote = run(["git", "remote", "get-url", "origin"], cwd=Path(root.stdout.strip()))
    if remote.returncode != 0:
        raise ReviewError("No origin remote found. Pass --repo owner/repo.", code="repo_context_missing", exit_code=4)
    resolved = normalize_remote(remote.stdout.strip())
    if not resolved:
        raise ReviewError("Could not resolve owner/repo from origin remote.", code="repo_context_missing", exit_code=5)
    return resolved


def positive_int(raw: str | None, name: str) -> int:
    if not raw or not re.fullmatch(r"[1-9][0-9]*", raw):
        raise ReviewError(f"Invalid --{name} value '{raw or ''}'. Use a positive integer.", code="invalid_arguments", exit_code=64)
    return int(raw)


def duration_seconds(raw: str, name: str) -> float:
    match = re.fullmatch(r"([1-9][0-9]*)([smh]?)", raw.strip().lower())
    if not match:
        raise ReviewError(
            f"Invalid --{name} value '{raw}'. Use a positive duration such as 30s, 15m, or 1h.",
            code="invalid_arguments",
            exit_code=64,
        )
    multipliers = {"": 1, "s": 1, "m": 60, "h": 3600}
    return int(match.group(1)) * multipliers[match.group(2)]


def is_provider_author(provider: str, login: str) -> bool:
    if provider != "codex":
        raise ReviewError(
            f"Unsupported review provider '{provider}'. Supported providers: codex.",
            code="unsupported_provider",
            exit_code=64,
        )
    return login.lower() in CODEX_LOGINS


def authored_by(item: dict[str, Any], provider: str) -> bool:
    return is_provider_author(provider, str((item.get("user") or {}).get("login") or ""))


def sha_matches(actual: object, expected: str) -> bool:
    value = str(actual or "").lower()
    target = expected.lower()
    return bool(value and target and (value.startswith(target) or target.startswith(value)))


def validate_head(raw: str) -> str:
    value = raw.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{7,40}", value):
        raise ReviewError(
            f"Invalid --head value '{raw}'. Use a hexadecimal commit SHA or unambiguous 7-40 character prefix.",
            code="invalid_arguments",
            exit_code=64,
        )
    return value


def review_request_matches(comment: dict[str, Any], provider: str, head: str) -> bool:
    body = str(comment.get("body") or "")
    command = re.search(r"(?is)@codex\s+review\b(?P<tail>.*)", body) if provider == "codex" else None
    if provider == "codex" and not command:
        return False
    evidence = command.group("tail") if command else body
    tokens = re.findall(r"(?i)(?<![0-9a-f])([0-9a-f]{7,40})(?![0-9a-f])", evidence)
    return any(sha_matches(token, head) for token in tokens)


def provider_reactions(repo: str, comment_id: int, provider: str) -> set[str]:
    reactions = gh_api_paginated_list(f"repos/{repo}/issues/comments/{comment_id}/reactions")
    return {
        str(reaction.get("content") or "")
        for reaction in reactions
        if authored_by(reaction, provider)
    }


def check_automated_review(repo: str, pr: int, provider: str, expected_head: str | None) -> dict[str, Any]:
    # Validate before any network reads so unsupported providers fail predictably.
    is_provider_author(provider, "")
    pull = gh_json(["api", f"repos/{repo}/pulls/{pr}", "-H", "Accept: application/vnd.github+json"])
    if not isinstance(pull, dict):
        raise ReviewError("Unexpected pull request response shape.", code="api_error", exit_code=4)
    current_head = str(((pull.get("head") or {}).get("sha")) or "")
    if not current_head:
        raise ReviewError("Pull request response did not include a head SHA.", code="api_error", exit_code=4)
    current_head = validate_head(current_head)
    requested_head = validate_head(expected_head) if expected_head else current_head
    head = current_head if sha_matches(current_head, requested_head) else requested_head

    reviews = gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/reviews")
    inline_comments = gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/comments")
    conversation = gh_api_paginated_list(f"repos/{repo}/issues/{pr}/comments")
    provider_reviews = [item for item in reviews if authored_by(item, provider)]
    head_reviews = [item for item in provider_reviews if sha_matches(item.get("commit_id"), head)]
    head_findings = [
        item
        for item in inline_comments
        if authored_by(item, provider) and sha_matches(item.get("commit_id"), head)
    ]
    requests = [
        item
        for item in conversation
        if review_request_matches(item, provider, head)
    ]
    latest_request = max(requests, key=lambda item: str(item.get("created_at") or ""), default=None)
    reactions: set[str] = set()
    if latest_request and latest_request.get("id"):
        reactions = provider_reactions(repo, int(latest_request["id"]), provider)

    head_is_current = sha_matches(current_head, head)
    if not head_is_current:
        status = "stale"
    elif head_reviews:
        status = "findings" if head_findings else "clean"
    elif "+1" in reactions:
        status = "clean"
    elif latest_request:
        status = "acknowledged" if "eyes" in reactions else "pending"
    elif provider_reviews or any(
        provider == "codex" and re.search(r"(?i)@codex\s+review\b", str(item.get("body") or ""))
        for item in conversation
    ):
        status = "stale"
    else:
        status = "not-requested"

    return {
        "repo": repo,
        "pr": pr,
        "provider": provider,
        "review_state": status,
        "head": head,
        "current_head": current_head,
        "head_is_current": head_is_current,
        "review": {
            "count": len(head_reviews),
            "latest_id": head_reviews[-1].get("id") if head_reviews else None,
            "submitted_at": head_reviews[-1].get("submitted_at") if head_reviews else None,
            "findings": len(head_findings),
        },
        "request": {
            "comment_id": latest_request.get("id") if latest_request else None,
            "created_at": latest_request.get("created_at") if latest_request else None,
            "acknowledged": "eyes" in reactions,
            "clean_reaction": "+1" in reactions,
        },
    }


def wait_for_automated_review(
    repo: str,
    pr: int,
    provider: str,
    expected_head: str | None,
    timeout: float,
    initial_interval: float,
    max_interval: float,
) -> tuple[dict[str, Any], int]:
    started = time.monotonic()
    interval = initial_interval
    attempts = 0
    while True:
        attempts += 1
        payload = check_automated_review(repo, pr, provider, expected_head)
        payload["attempts"] = attempts
        payload["elapsed_seconds"] = round(time.monotonic() - started, 3)
        status = str(payload["review_state"])
        if status in {"clean", "findings", "not-requested", "stale"}:
            return payload, REVIEW_EXIT_CODES[status]
        remaining = timeout - (time.monotonic() - started)
        if remaining <= 0:
            payload["timed_out"] = True
            return payload, 124
        time.sleep(min(interval, remaining))
        interval = min(max_interval, interval * 1.5)


def snippet(text: str, limit: int = 220) -> str:
    compact = (text or "").replace("\r\n", "\n").replace("\n", " ").strip()
    return compact[: limit - 3] + "..." if len(compact) > limit else compact


def review_threads(repo: str, pr: int, include_resolved: bool) -> list[dict[str, Any]]:
    owner, repo_name = repo.split("/", 1)
    query = """
query($owner: String!, $repo: String!, $number: Int!, $after: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 50, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          isResolved
          isOutdated
          path
          line
          startLine
          comments(first: 100) {
            nodes {
              databaseId
              body
              createdAt
              updatedAt
              author { login }
            }
          }
        }
      }
    }
  }
}
""".strip()
    entries: list[dict[str, Any]] = []
    after: str | None = None
    while True:
        payload = graphql(query, {"owner": owner, "repo": repo_name, "number": pr, "after": after})
        threads = (((payload.get("data") or {}).get("repository") or {}).get("pullRequest") or {}).get("reviewThreads") or {}
        for thread in threads.get("nodes") or []:
            if not isinstance(thread, dict):
                continue
            resolved = bool(thread.get("isResolved"))
            outdated = bool(thread.get("isOutdated"))
            active = (not resolved) and (not outdated)
            if not include_resolved and not active:
                continue
            for comment in ((thread.get("comments") or {}).get("nodes") or []):
                if isinstance(comment, dict) and comment.get("databaseId"):
                    entries.append(
                        {
                            "type": "review_thread_comment",
                            "comment_id": int(comment["databaseId"]),
                            "author": ((comment.get("author") or {}).get("login") or ""),
                            "updated": comment.get("updatedAt") or comment.get("createdAt") or "",
                            "body": comment.get("body") or "",
                            "body_preview": snippet(comment.get("body") or ""),
                            "path": thread.get("path") or "",
                            "line": thread.get("line"),
                            "start_line": thread.get("startLine"),
                            "is_resolved": resolved,
                            "is_outdated": outdated,
                        }
                    )
        page_info = threads.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
        if not after:
            break
    return entries


def collect_entries(repo: str, pr: int, include_resolved: bool) -> list[dict[str, Any]]:
    thread_entries = review_threads(repo, pr, include_resolved)
    known_thread_ids = {entry["comment_id"] for entry in thread_entries}
    review_comments = gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/comments")
    conversation_comments = gh_api_paginated_list(f"repos/{repo}/issues/{pr}/comments")
    entries = list(thread_entries)
    for comment in review_comments:
        if comment.get("id") and int(comment["id"]) not in known_thread_ids:
            entries.append(
                {
                    "type": "review_comment",
                    "comment_id": int(comment["id"]),
                    "author": ((comment.get("user") or {}).get("login") or ""),
                    "updated": comment.get("updated_at") or comment.get("created_at") or "",
                    "body": comment.get("body") or "",
                    "body_preview": snippet(comment.get("body") or ""),
                    "path": comment.get("path") or "",
                    "line": comment.get("line"),
                    "start_line": comment.get("start_line"),
                    "is_resolved": None,
                    "is_outdated": None,
                }
            )
    for comment in conversation_comments:
        if comment.get("id"):
            entries.append(
                {
                    "type": "conversation_comment",
                    "comment_id": int(comment["id"]),
                    "author": ((comment.get("user") or {}).get("login") or ""),
                    "updated": comment.get("updated_at") or comment.get("created_at") or "",
                    "body": comment.get("body") or "",
                    "body_preview": snippet(comment.get("body") or ""),
                    "path": "",
                    "line": None,
                    "start_line": None,
                    "is_resolved": None,
                    "is_outdated": None,
                }
            )
    for index, entry in enumerate(entries, start=1):
        entry["index"] = index
    return entries


def selected_entries(entries: list[dict[str, Any]], selection: str | None, comment_ids: str | None) -> list[dict[str, Any]]:
    if selection and comment_ids:
        raise ReviewError(
            "Use either --selection or --comment-ids with a reply body, not both.",
            code="invalid_arguments",
            exit_code=64,
        )
    if not selection and not comment_ids:
        raise ReviewError(
            "--reply-body or --reply-body-file requires --selection or --comment-ids.",
            code="invalid_arguments",
            exit_code=64,
        )
    key = "index" if selection else "comment_id"
    lookup = {str(entry[key]): entry for entry in entries}
    selected: list[dict[str, Any]] = []
    for part in str(selection or comment_ids or "").replace(",", " ").split():
        if part not in lookup:
            raise ReviewError(f"{key} '{part}' was not found.", code="invalid_arguments", exit_code=64)
        selected.append(lookup[part])
    return selected


def read_body(body: str | None, body_file: str | None, *, option_prefix: str = "body") -> str:
    if body and body_file:
        raise ReviewError(
            f"Use either --{option_prefix} or --{option_prefix}-file, not both.",
            code="invalid_arguments",
            exit_code=64,
        )
    if body_file:
        try:
            value = Path(body_file).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ReviewError(
                f"Could not read --{option_prefix}-file '{body_file}': {exc}",
                code="invalid_arguments",
                exit_code=64,
            ) from exc
    else:
        value = body or ""
    if not value.strip():
        raise ReviewError(
            f"A non-empty --{option_prefix} or --{option_prefix}-file is required.",
            code="invalid_arguments",
            exit_code=64,
        )
    return value


def post_conversation_comment(repo: str, pr: int, body: str, dry_run: bool) -> dict[str, Any]:
    action: dict[str, Any] = {
        "type": "conversation_comment",
        "status": "dry-run" if dry_run else "pending",
        "body_preview": snippet(body),
    }
    if dry_run:
        return action
    result = run_gh(["pr", "comment", str(pr), "--repo", repo, "--body", body])
    action["transport"] = "gh pr comment"
    if result.returncode != 0:
        raise ReviewError((result.stderr or result.stdout or "comment failed").strip(), exit_code=result.returncode)
    action["status"] = "posted"
    output = result.stdout.strip()
    if output:
        action["url"] = output
    return action


def post_replies(repo: str, pr: int, entries: list[dict[str, Any]], body: str, dry_run: bool) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for entry in entries:
        action: dict[str, Any] = {"comment_id": entry["comment_id"], "type": entry["type"], "status": "dry-run" if dry_run else "pending"}
        if dry_run:
            actions.append(action)
            continue
        if entry["type"] == "conversation_comment":
            result = run_gh(["pr", "comment", str(pr), "--repo", repo, "--body", f"{body} (ref: {entry['comment_id']})"])
            action["transport"] = "gh pr comment"
            action["status"] = "posted" if result.returncode == 0 else "error"
        else:
            endpoint = f"repos/{repo}/pulls/{pr}/comments/{entry['comment_id']}/replies"
            result = run_gh(["api", "-X", "POST", endpoint, "-H", "Accept: application/vnd.github+json", "-f", f"body={body}"])
            action["transport"] = "gh api"
            action["status"] = "replied" if result.returncode == 0 else "error"
        if result.returncode != 0:
            action["message"] = (result.stderr or result.stdout or "reply failed").strip()
        actions.append(action)
    return actions


def render_text(payload: dict[str, Any]) -> str:
    if "review_state" in payload:
        lines = [
            f"{payload['provider']} review for {payload['repo']}#{payload['pr']}: {payload['review_state']}",
            f"head={payload['head']} current={payload['current_head']}",
        ]
        if payload.get("timed_out"):
            lines.append("wait timed out")
        return "\n".join(lines) + "\n"
    lines: list[str] = []
    for entry in payload["entries"]:
        lines.append(f"[{entry['index']:>3}] {entry['type']} id={entry['comment_id']} author={entry['author'] or 'unknown'} updated={entry['updated']}")
        lines.append(f"      {entry['body_preview'] or '(empty)'}")
        if entry["path"]:
            lines.append(f"      file={entry['path']} line={entry['line']} startLine={entry['start_line']} resolved={entry['is_resolved']} outdated={entry['is_outdated']}")
    if not lines:
        lines.append("No comment context found.")
    if payload.get("actions"):
        lines.extend(["", "Reply actions:"])
        for action in payload["actions"]:
            lines.append(f"- comment {action['comment_id']}: {action['status']}")
    if payload.get("action"):
        action = payload["action"]
        lines.append(f"{action['status']}: conversation comment for {payload['repo']}#{payload['pr']}")
        if action.get("url"):
            lines.append(str(action["url"]))
    return "\n".join(lines) + "\n"


def doctor_payload() -> dict[str, object]:
    git_path = which("git")
    gh_path = which("gh")
    auth = run(["gh", "auth", "status"]) if gh_path else RunResult(127, "", "gh missing")
    return {
        "ok": bool(git_path and gh_path),
        "version": VERSION,
        "checks": {
            "git": {"ok": bool(git_path), "path": git_path},
            "gh": {"ok": bool(gh_path), "path": gh_path, "authenticated": auth.returncode == 0 if gh_path else False},
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gitstack reviews",
        description="Inspect, check, wait for, or respond to pull-request reviews.",
    )
    parser.add_argument("--json", action="store_true", help="Emit a stable JSON envelope.")
    parser.add_argument("--version", action="store_true", help="Print version and exit.")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("doctor", help="Check local git and gh readiness.")
    address = subparsers.add_parser("address", help="List review context or reply to selected comments.")
    address.add_argument("--pr", required=True, help="Pull request number.")
    address.add_argument("--repo", help="Repository in owner/repo format. Defaults to current checkout.")
    address.add_argument("--include-resolved", action="store_true", help="Include resolved or outdated review threads.")
    address.add_argument("--selection", help="Space or comma separated row indexes to reply to.")
    address.add_argument("--comment-ids", help="Space or comma separated GitHub comment ids to reply to.")
    address.add_argument("--reply-body", help="Reply body. Requires --selection or --comment-ids.")
    address.add_argument("--reply-body-file", help="Read the reply body from a UTF-8 file. Requires --selection or --comment-ids.")
    address.add_argument("--dry-run", action="store_true", help="Preview reply actions without posting.")
    address.add_argument("--allow-non-project", action="store_true", help="Allow --repo usage outside a git checkout.")
    comment = subparsers.add_parser("comment", help="Post a top-level PR discussion comment.")
    comment.add_argument("--pr", required=True, help="Pull request number.")
    comment.add_argument("--repo", help="Repository in owner/repo format. Defaults to current checkout.")
    comment.add_argument("--body", help="Comment body.")
    comment.add_argument("--body-file", help="Read the comment body from a UTF-8 file.")
    comment.add_argument("--dry-run", action="store_true", help="Preview the comment action without posting.")
    comment.add_argument("--allow-non-project", action="store_true", help="Allow --repo usage outside a git checkout.")
    for command, help_text in (
        ("check", "Inspect automated review state once and exit."),
        ("wait", "Wait for an automated review to complete or time out."),
    ):
        review = subparsers.add_parser(command, help=help_text)
        review.add_argument("--provider", required=True, help="Automated review provider. Currently: codex.")
        review.add_argument("--pr", required=True, help="Pull request number.")
        review.add_argument("--repo", help="Repository in owner/repo format. Defaults to current checkout.")
        review.add_argument("--head", help="Expected reviewed head SHA. Defaults to the current PR head.")
        review.add_argument("--allow-non-project", action="store_true", help="Allow --repo usage outside a git checkout.")
        if command == "wait":
            review.add_argument("--timeout", default="15m", help="Maximum wait, for example 30s, 15m, or 1h.")
            review.add_argument("--interval", default="10s", help="Initial polling interval. Default: 10s.")
            review.add_argument("--max-interval", default="30s", help="Maximum polling interval. Default: 30s.")
    return parser


def emit_success(data: object, command: list[str]) -> None:
    print(json.dumps({"ok": True, "version": VERSION, "command": command, "data": data}, indent=2))


def emit_error(exc: ReviewError, command: list[str]) -> None:
    print(json.dumps({"ok": False, "version": VERSION, "command": command, "error": {"code": exc.code, "message": exc.message}}, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version:
        print(VERSION)
        return 0
    if args.command == "doctor":
        payload = doctor_payload()
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"gitstack reviews {VERSION}")
            print(f"git: {'ok' if payload['checks']['git']['ok'] else 'missing'}")
            print(f"gh: {'ok' if payload['checks']['gh']['ok'] else 'missing'}")
        return 0 if payload["ok"] else 1
    if args.command not in {"address", "comment", "check", "wait"}:
        parser.print_help()
        return 0
    try:
        pr = positive_int(args.pr, "pr")
        repo = resolve_repo(args.repo, allow_non_project=args.allow_non_project)
        if args.command in {"check", "wait"}:
            if args.command == "check":
                payload = check_automated_review(repo, pr, args.provider, args.head)
                exit_code = REVIEW_EXIT_CODES[str(payload["review_state"])]
            else:
                timeout = duration_seconds(args.timeout, "timeout")
                interval = duration_seconds(args.interval, "interval")
                max_interval = duration_seconds(args.max_interval, "max-interval")
                if interval > max_interval:
                    raise ReviewError(
                        "--interval cannot be greater than --max-interval.",
                        code="invalid_arguments",
                        exit_code=64,
                    )
                payload, exit_code = wait_for_automated_review(
                    repo, pr, args.provider, args.head, timeout, interval, max_interval
                )
            if args.json:
                emit_success(payload, [args.command])
            else:
                print(render_text(payload), end="")
            return exit_code
        if args.command == "comment":
            body = read_body(args.body, args.body_file)
            payload = {"repo": repo, "pr": pr, "action": post_conversation_comment(repo, pr, body, args.dry_run)}
            if args.json:
                emit_success(payload, ["comment"])
            else:
                print(render_text(payload), end="")
            return 0
        entries = collect_entries(repo, pr, args.include_resolved)
        payload: dict[str, Any] = {"repo": repo, "pr": pr, "entries": entries}
        if args.reply_body or args.reply_body_file:
            targets = selected_entries(entries, args.selection, args.comment_ids)
            reply_body = read_body(args.reply_body, args.reply_body_file, option_prefix="reply-body")
            payload["actions"] = post_replies(repo, pr, targets, reply_body, args.dry_run)
        elif args.selection or args.comment_ids:
            raise ReviewError(
                "--selection and --comment-ids require --reply-body or --reply-body-file.",
                code="invalid_arguments",
                exit_code=64,
            )
        if args.json:
            emit_success(payload, ["address"])
        else:
            print(render_text(payload), end="")
        return 0
    except ReviewError as exc:
        if args.command in {"check", "wait"} and exc.code == "command_failed":
            exc = ReviewError(exc.message, code="api_error", exit_code=4)
        if args.json:
            emit_error(exc, [args.command or ""])
        else:
            print(exc.message, file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
