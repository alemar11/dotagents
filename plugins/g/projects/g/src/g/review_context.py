from __future__ import annotations

from typing import Any

from .review_mutation import ReservationError, thread_identity_fingerprint
from .review_request import validate_full_head
from .review_types import ReviewError


def snippet(text: str, limit: int = 220) -> str:
    compact = (text or "").replace("\r\n", "\n").replace("\n", " ").strip()
    return compact[: limit - 3] + "..." if len(compact) > limit else compact


def thread_context(thread_id: str, *, backend: Any) -> dict[str, Any]:
    query = """
query($id: ID!, $after: String) {
  node(id: $id) {
    ... on PullRequestReviewThread {
      id isResolved isOutdated viewerCanResolve path line startLine
      repository { nameWithOwner }
      pullRequest { number state headRefOid }
      comments(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes { id databaseId body createdAt updatedAt author { login } }
      }
    }
  }
}
""".strip()
    comments: list[dict[str, Any]] = []
    context: dict[str, Any] | None = None
    after: str | None = None
    while True:
        payload = backend.graphql(query, {"id": thread_id, "after": after})
        node = (
            (payload.get("data") or {}).get("node")
            if isinstance(payload, dict)
            else None
        )
        if not isinstance(node, dict) or node.get("id") != thread_id:
            raise ReviewError(
                "Review thread was not found.",
                code="review_thread_not_found",
                exit_code=4,
            )
        current = {
            "thread_id": str(node["id"]),
            "is_resolved": bool(node.get("isResolved")),
            "is_outdated": bool(node.get("isOutdated")),
            "viewer_can_resolve": bool(node.get("viewerCanResolve")),
            "path": str(node.get("path") or ""),
            "line": node.get("line"),
            "start_line": node.get("startLine"),
            "repository": str(
                (node.get("repository") or {}).get("nameWithOwner") or ""
            ),
            "pr_number": (node.get("pullRequest") or {}).get("number"),
            "pr_state": str((node.get("pullRequest") or {}).get("state") or "").lower(),
            "head_sha": str((node.get("pullRequest") or {}).get("headRefOid") or ""),
        }
        if context is not None and context != current:
            raise ReviewError(
                "Review thread identity changed during pagination.",
                code="review_thread_mismatch",
                exit_code=4,
            )
        context = current
        connection = node.get("comments") or {}
        comments.extend(
            item for item in connection.get("nodes") or [] if isinstance(item, dict)
        )
        page_info = connection.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
        if not after:
            raise ReviewError(
                "Review thread pagination omitted its cursor.",
                code="provider_response_invalid",
                exit_code=65,
            )
    assert context is not None
    context["comments"] = comments
    return context


def thread_ids(repo: str, pr: int, *, backend: Any) -> list[str]:
    owner, repo_name = repo.split("/", 1)
    query = """
query($owner: String!, $repo: String!, $number: Int!, $after: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes { id }
      }
    }
  }
}
""".strip()
    thread_ids: list[str] = []
    after: str | None = None
    while True:
        payload = backend.graphql(
            query, {"owner": owner, "repo": repo_name, "number": pr, "after": after}
        )
        pull = (
            ((payload.get("data") or {}).get("repository") or {}).get("pullRequest")
            if isinstance(payload, dict)
            else None
        )
        if not isinstance(pull, dict):
            raise ReviewError(
                "Pull request review threads were not found.",
                code="provider_target_mismatch",
                exit_code=65,
            )
        threads = pull.get("reviewThreads") or {}
        for thread in threads.get("nodes") or []:
            if isinstance(thread, dict) and isinstance(thread.get("id"), str):
                thread_ids.append(thread["id"])
        page_info = threads.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
        if not after:
            raise ReviewError(
                "Review thread pagination omitted its cursor.",
                code="provider_response_invalid",
                exit_code=65,
            )
    if len(thread_ids) != len(set(thread_ids)):
        raise ReviewError(
            "Review thread pagination returned duplicate identities.",
            code="review_thread_mismatch",
            exit_code=4,
        )
    return thread_ids


def finding_thread(
    repo: str,
    pr: int,
    finding_comment_id: int,
    finding_node_id: str,
    *,
    backend: Any,
) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    for thread_id in backend._review_thread_ids(repo, pr):
        context = backend._review_thread_context(thread_id)
        if context["repository"] != repo or context["pr_number"] != pr:
            raise ReviewError(
                "Review thread does not belong to the requested PR.",
                code="review_thread_mismatch",
                exit_code=4,
            )
        if any(
            item.get("id") == finding_node_id
            and item.get("databaseId") == finding_comment_id
            for item in context["comments"]
        ):
            matches.append(context)
    if len(matches) != 1:
        raise ReviewError(
            "The exact review finding did not map to one unique thread.",
            code="review_thread_not_found" if not matches else "review_thread_mismatch",
            exit_code=4,
        )
    return matches[0]


def exact_thread_fingerprint(
    thread: dict[str, Any], repo: str, pr: int, head: str
) -> str:
    try:
        return thread_identity_fingerprint(
            repo,
            pr,
            head,
            str(thread["thread_id"]),
            [
                {"node_id": item.get("id"), "comment_id": item.get("databaseId")}
                for item in thread.get("comments", [])
            ],
        )
    except (KeyError, ReservationError) as exc:
        raise ReviewError(
            "The exact review thread omitted stable provider identity.",
            code="review_thread_mismatch",
            exit_code=4,
        ) from exc


def reply_thread_identity(
    repo: str,
    pr: int,
    head: str,
    comment_id: int,
    *,
    backend: Any,
) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    parent = backend._api_object(f"repos/{repo}/pulls/comments/{comment_id}")
    if not str(parent.get("pull_request_url") or "").endswith(
        f"/repos/{repo}/pulls/{pr}"
    ):
        raise ReviewError(
            "Review comment does not belong to the requested PR.",
            code="provider_target_mismatch",
            exit_code=65,
        )
    if parent.get("id") != comment_id or not isinstance(parent.get("node_id"), str):
        raise ReviewError(
            "Review finding omitted its exact provider identity.",
            code="provider_identity_missing",
            exit_code=65,
        )
    if parent.get("in_reply_to_id") is not None:
        raise ReviewError(
            "Review replies must target the exact top-level finding.",
            code="review_reply_parent_invalid",
            exit_code=4,
        )
    try:
        finding_head = validate_full_head(str(parent.get("commit_id") or ""))
    except ValueError as exc:
        raise ReviewError(
            "Review finding omitted its full commit identity.",
            code="provider_identity_missing",
            exit_code=65,
        ) from exc
    thread = backend._finding_thread(repo, pr, comment_id, parent["node_id"])
    return (
        parent,
        thread,
        backend._exact_thread_fingerprint(thread, repo, pr, head),
        finding_head,
    )


def review_threads(
    repo: str, pr: int, include_resolved: bool, *, backend: Any
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for thread_id in backend._review_thread_ids(repo, pr):
        thread = backend._review_thread_context(thread_id)
        resolved = thread["is_resolved"]
        outdated = thread["is_outdated"]
        if not include_resolved and (resolved or outdated):
            continue
        fingerprint = backend._exact_thread_fingerprint(
            thread, repo, pr, thread["head_sha"]
        )
        for comment in thread["comments"]:
            if isinstance(comment.get("databaseId"), int):
                entries.append(
                    {
                        "type": "review_thread_comment",
                        "thread_id": thread_id,
                        "thread_fingerprint": fingerprint,
                        "head_sha": thread["head_sha"],
                        "comment_id": int(comment["databaseId"]),
                        "comment_node_id": comment.get("id"),
                        "author": ((comment.get("author") or {}).get("login") or ""),
                        "updated": comment.get("updatedAt")
                        or comment.get("createdAt")
                        or "",
                        "body": comment.get("body") or "",
                        "body_preview": snippet(comment.get("body") or ""),
                        "path": thread["path"],
                        "line": thread["line"],
                        "start_line": thread["start_line"],
                        "is_resolved": resolved,
                        "is_outdated": outdated,
                        "viewer_can_resolve": thread["viewer_can_resolve"],
                    }
                )
    return entries


def collect_entries(
    repo: str, pr: int, include_resolved: bool, *, backend: Any
) -> list[dict[str, Any]]:
    thread_entries = backend.review_threads(repo, pr, include_resolved)
    known_thread_ids = {entry["comment_id"] for entry in thread_entries}
    review_comments = backend.gh_api_paginated_list(f"repos/{repo}/pulls/{pr}/comments")
    conversation_comments = backend.gh_api_paginated_list(
        f"repos/{repo}/issues/{pr}/comments"
    )
    entries = list(thread_entries)
    for comment in review_comments:
        if comment.get("id") and int(comment["id"]) not in known_thread_ids:
            entries.append(
                {
                    "type": "review_comment",
                    "comment_id": int(comment["id"]),
                    "author": ((comment.get("user") or {}).get("login") or ""),
                    "updated": comment.get("updated_at")
                    or comment.get("created_at")
                    or "",
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
                    "updated": comment.get("updated_at")
                    or comment.get("created_at")
                    or "",
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
