from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from shutil import which
from typing import Callable

REPO_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")


class GhError(RuntimeError):
    def __init__(self, message: str, returncode: int = 1) -> None:
        super().__init__(message)
        self.returncode = returncode


def _run_gh_json(args: list[str]) -> object:
    proc = subprocess.run(args, text=True, capture_output=True)
    if proc.returncode != 0:
        message = (proc.stderr or proc.stdout or "").strip() or "gh command failed"
        raise GhError(message, proc.returncode)
    try:
        return json.loads(proc.stdout or "null")
    except json.JSONDecodeError as exc:
        raise GhError(f"Failed to parse gh output: {exc}") from exc


def graphql(query: str, variables: dict[str, object] | None = None) -> object:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in (variables or {}).items():
        if isinstance(value, list):
            if not value:
                cmd.extend(["-F", f"{key}[]"])
            else:
                for item in value:
                    cmd.extend(["-F", f"{key}[]={item}"])
        elif value is None:
            cmd.extend(["-F", f"{key}=null"])
        elif isinstance(value, bool):
            cmd.extend(["-F", f"{key}={'true' if value else 'false'}"])
        else:
            cmd.extend(["-F", f"{key}={value}"])
    return _run_gh_json(cmd)


def repo_view(repo: str) -> dict[str, object]:
    validate_repo_reference(repo)
    payload = _run_gh_json(
        [
            "gh",
            "repo",
            "view",
            repo,
            "--json",
            "id,nameWithOwner,viewerHasStarred,url",
        ]
    )
    if not isinstance(payload, dict):
        raise GhError("Unexpected repo view response shape.")
    return payload


def _page_size(limit: int, default: int = 100) -> int:
    if limit <= 0:
        return default
    return min(limit, default)


def validate_repo_reference(repo: str) -> str:
    value = repo.strip()
    if not REPO_PATTERN.match(value):
        raise GhError(f"Invalid repository reference '{repo}'. Use owner/repo.", 64)
    return value


def collect_repo_targets(repos: Iterable[str], repo_file: str | None = None) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []

    def add(repo: str) -> None:
        normalized = validate_repo_reference(repo)
        if normalized not in seen:
            seen.add(normalized)
            ordered.append(normalized)

    for repo in repos:
        if repo.strip():
            add(repo)

    if repo_file:
        try:
            with open(repo_file, "r", encoding="utf-8") as handle:
                for raw_line in handle:
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue
                    add(line)
        except OSError as exc:
            raise GhError(f"Failed to read repos file '{repo_file}': {exc.strerror or exc}", 66) from exc

    return ordered


def viewer_lists(limit: int = 0) -> dict[str, object]:
    query = """
    query($first: Int!, $after: String) {
      viewer {
        lists(first: $first, after: $after) {
          totalCount
          nodes {
            id
            name
            slug
            description
            isPrivate
            createdAt
            updatedAt
            lastAddedAt
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
    """
    items: list[dict[str, object]] = []
    cursor: str | None = None
    total_count = 0
    while True:
        payload = graphql(
            query,
            {"first": _page_size(limit - len(items) if limit > 0 else 0), "after": cursor},
        )
        try:
            lists = payload["data"]["viewer"]["lists"]
        except (TypeError, KeyError) as exc:
            raise GhError("Unexpected viewer lists response shape.") from exc
        total_count = int(lists.get("totalCount") or 0)
        nodes = lists.get("nodes") or []
        for node in nodes:
            if isinstance(node, dict):
                items.append(node)
                if limit > 0 and len(items) >= limit:
                    return {"totalCount": total_count, "items": items}
        page_info = lists.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            break
    return {"totalCount": total_count, "items": items}


def resolve_list(*, list_id: str | None = None, selector: str | None = None) -> dict[str, object]:
    if list_id:
        query = """
        query($id: ID!) {
          node(id: $id) {
            __typename
            ... on UserList {
              id
              name
              slug
              description
              isPrivate
              createdAt
              updatedAt
              lastAddedAt
            }
          }
        }
        """
        payload = graphql(query, {"id": list_id})
        try:
            node = payload["data"]["node"]
        except (TypeError, KeyError) as exc:
            raise GhError("Unexpected list lookup response shape.") from exc
        if not isinstance(node, dict) or node.get("__typename") != "UserList":
            raise GhError(f"List id '{list_id}' was not found.", 66)
        node = dict(node)
        node.pop("__typename", None)
        return node

    if not selector:
        raise GhError("A list selector is required.", 64)

    all_lists = viewer_lists(0).get("items") or []
    slug_matches = [item for item in all_lists if item.get("slug") == selector]
    if len(slug_matches) == 1:
        return slug_matches[0]
    if len(slug_matches) > 1:
        raise GhError(
            f"List selector '{selector}' matched multiple list slugs. Use --list-id.",
            65,
        )

    name_matches = [item for item in all_lists if item.get("name") == selector]
    if len(name_matches) == 1:
        return name_matches[0]
    if len(name_matches) > 1:
        raise GhError(
            f"List selector '{selector}' matched multiple list names. Use --list-id.",
            65,
        )

    raise GhError(f"List selector '{selector}' was not found.", 66)


def list_items(list_id: str, limit: int = 0) -> dict[str, object]:
    query = """
    query($id: ID!, $first: Int!, $after: String) {
      node(id: $id) {
        __typename
        ... on UserList {
          id
          name
          slug
          description
          isPrivate
          createdAt
          updatedAt
          lastAddedAt
          items(first: $first, after: $after) {
            totalCount
            nodes {
              __typename
              ... on Repository {
                id
                nameWithOwner
                url
                viewerHasStarred
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
      }
    }
    """
    items: list[dict[str, object]] = []
    cursor: str | None = None
    metadata: dict[str, object] | None = None
    total_count = 0
    while True:
        payload = graphql(
            query,
            {
                "id": list_id,
                "first": _page_size(limit - len(items) if limit > 0 else 0),
                "after": cursor,
            },
        )
        try:
            node = payload["data"]["node"]
        except (TypeError, KeyError) as exc:
            raise GhError("Unexpected list items response shape.") from exc
        if not isinstance(node, dict) or node.get("__typename") != "UserList":
            raise GhError(f"List id '{list_id}' was not found.", 66)
        metadata = {
            "id": node.get("id"),
            "name": node.get("name"),
            "slug": node.get("slug"),
            "description": node.get("description"),
            "isPrivate": bool(node.get("isPrivate")),
            "createdAt": node.get("createdAt"),
            "updatedAt": node.get("updatedAt"),
            "lastAddedAt": node.get("lastAddedAt"),
        }
        item_connection = node.get("items") or {}
        total_count = int(item_connection.get("totalCount") or 0)
        for entry in item_connection.get("nodes") or []:
            if isinstance(entry, dict) and entry.get("__typename") == "Repository":
                cleaned = dict(entry)
                cleaned.pop("__typename", None)
                items.append(cleaned)
                if limit > 0 and len(items) >= limit:
                    metadata["totalCount"] = total_count
                    metadata["items"] = items
                    return metadata
        page_info = item_connection.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            break
    if metadata is None:
        raise GhError(f"List id '{list_id}' was not found.", 66)
    metadata["totalCount"] = total_count
    metadata["items"] = items
    return metadata


def viewer_stars(limit: int = 0) -> dict[str, object]:
    query = """
    query($first: Int!, $after: String) {
      viewer {
        starredRepositories(
          first: $first
          after: $after
          orderBy: {field: STARRED_AT, direction: DESC}
        ) {
          totalCount
          nodes {
            id
            nameWithOwner
            url
            viewerHasStarred
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
    """
    items: list[dict[str, object]] = []
    cursor: str | None = None
    total_count = 0
    while True:
        payload = graphql(
            query,
            {"first": _page_size(limit - len(items) if limit > 0 else 0), "after": cursor},
        )
        try:
            connection = payload["data"]["viewer"]["starredRepositories"]
        except (TypeError, KeyError) as exc:
            raise GhError("Unexpected starred repositories response shape.") from exc
        total_count = int(connection.get("totalCount") or 0)
        for node in connection.get("nodes") or []:
            if isinstance(node, dict):
                items.append(node)
                if limit > 0 and len(items) >= limit:
                    return {"totalCount": total_count, "items": items}
        page_info = connection.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            break
    return {"totalCount": total_count, "items": items}


def repo_memberships(repo_ids: Iterable[str]) -> dict[str, list[dict[str, object]]]:
    targets = [repo_id for repo_id in repo_ids if repo_id]
    memberships: dict[str, list[dict[str, object]]] = {repo_id: [] for repo_id in targets}
    if not targets:
        return memberships

    for user_list in viewer_lists(0).get("items") or []:
        list_id = user_list.get("id")
        if not isinstance(list_id, str) or not list_id:
            continue
        payload = list_items(list_id, 0)
        list_summary = {
            "id": payload.get("id"),
            "name": payload.get("name"),
            "slug": payload.get("slug"),
        }
        for item in payload.get("items") or []:
            if not isinstance(item, dict):
                continue
            repo_id = item.get("id")
            if isinstance(repo_id, str) and repo_id in memberships:
                memberships[repo_id].append(list_summary)
    return memberships


# Star command implementation

def _stars_positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("Use a positive integer.")
    return number


def _stars_mutate_star(repo_id: str, add: bool) -> None:
    action = "addStar" if add else "removeStar"
    query = f"""
    mutation($starrableId: ID!) {{
      {action}(input: {{starrableId: $starrableId}}) {{
        starrable {{
          __typename
          ... on Repository {{
            id
          }}
        }}
      }}
    }}
    """
    graphql(query, {"starrableId": repo_id})


def _stars_emit(payload: object) -> int:
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def _stars_print_read_text(payload: dict[str, object]) -> int:
    source = payload.get("source")
    items = payload.get("items") or []
    if source == "list":
        list_payload = payload.get("list") or {}
        visibility = "private" if list_payload.get("isPrivate") else "public"
        print(
            f"Starred repositories in list: {list_payload.get('name')} ({list_payload.get('slug')})"
        )
        print(f"Visibility: {visibility}")
        print(f"Total: {payload.get('totalCount', 0)}")
        print(f"Shown: {len(items)}")
    else:
        print("Starred repositories")
        print(f"Total: {payload.get('totalCount', 0)}")
        print(f"Shown: {len(items)}")
    for item in items:
        if isinstance(item, dict):
            print(f"- {item.get('nameWithOwner')}")
    return 0


def _stars_print_write_text(payload: dict[str, object]) -> int:
    print(f"Action: {payload.get('action')}")
    print(f"Targets: {payload.get('targetCount')}")
    print(f"Succeeded: {payload.get('successCount')}")
    print(f"Failed: {payload.get('failureCount')}")
    for item in payload.get("results") or []:
        if not isinstance(item, dict):
            continue
        message = item.get("message") or item.get("status")
        print(f"- {item.get('repo')}: {message}")
    return 0


def _stars_run_list_stars(args: argparse.Namespace) -> int:
    limit = 0 if args.all else args.limit
    if args.list_id or args.by_list:
        selected_list = resolve_list(list_id=args.list_id, selector=args.by_list)
        list_payload = list_items(str(selected_list["id"]), limit=limit)
        payload = {
            "mode": "list-stars",
            "source": "list",
            "list": {
                "id": list_payload.get("id"),
                "name": list_payload.get("name"),
                "slug": list_payload.get("slug"),
                "description": list_payload.get("description"),
                "isPrivate": list_payload.get("isPrivate"),
            },
            "totalCount": list_payload.get("totalCount", 0),
            "items": list_payload.get("items") or [],
        }
    else:
        stars = viewer_stars(limit=limit)
        payload = {
            "mode": "list-stars",
            "source": "stars",
            "totalCount": stars.get("totalCount", 0),
            "items": stars.get("items") or [],
        }

    if args.json:
        return _stars_emit(payload)
    return _stars_print_read_text(payload)


def _stars_run_write(args: argparse.Namespace, add: bool) -> int:
    repos = collect_repo_targets(args.repo or [], args.repos_file)
    if not repos:
        raise GhError("At least one target repository is required.", 64)

    results: list[dict[str, object]] = []
    failure_count = 0

    for repo in repos:
        result: dict[str, object] = {"repo": repo}
        try:
            repo_payload = repo_view(repo)
            repo_id = str(repo_payload["id"])
            canonical_repo = str(repo_payload["nameWithOwner"])
            already_starred = bool(repo_payload.get("viewerHasStarred"))
            result["repo"] = canonical_repo
            result["url"] = repo_payload.get("url")
            result["wasStarred"] = already_starred

            if add:
                if already_starred:
                    result["status"] = "noop"
                    result["message"] = "already starred"
                elif args.dry_run:
                    result["status"] = "dry-run"
                    result["message"] = "would star"
                else:
                    _stars_mutate_star(repo_id, add=True)
                    result["status"] = "changed"
                    result["message"] = "starred"
            else:
                if not already_starred:
                    result["status"] = "noop"
                    result["message"] = "already unstarred"
                elif args.dry_run:
                    result["status"] = "dry-run"
                    result["message"] = "would unstar"
                else:
                    _stars_mutate_star(repo_id, add=False)
                    result["status"] = "changed"
                    result["message"] = "unstarred"
        except GhError as exc:
            failure_count += 1
            result["status"] = "error"
            result["message"] = str(exc)
        results.append(result)

    payload = {
        "action": "star" if add else "unstar",
        "targetCount": len(repos),
        "successCount": len(repos) - failure_count,
        "failureCount": failure_count,
        "results": results,
    }
    if args.json:
        _stars_emit(payload)
    else:
        _stars_print_write_text(payload)
    return 1 if failure_count else 0


def build_stars_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="List, star, or unstar repositories for the authenticated GitHub account."
    )
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--list-stars", action="store_true")
    action_group.add_argument("--star", action="store_true")
    action_group.add_argument("--unstar", action="store_true")

    parser.add_argument("--repo", action="append", default=[], help="Repository in owner/repo format.")
    parser.add_argument("--repos-file", help="Newline-delimited file of owner/repo entries.")
    parser.add_argument("--by-list", help="Exact list slug or exact list name.")
    parser.add_argument("--list-id", help="Exact GitHub user list id.")
    parser.add_argument("--limit", type=_stars_positive_int, default=100, help="Maximum number of items to return.")
    parser.add_argument("--all", action="store_true", help="Fetch all available items for read actions.")
    parser.add_argument("--json", action="store_true", help="Emit normalized JSON output.")
    parser.add_argument("--dry-run", action="store_true", help="Preview write actions without mutating GitHub.")
    return parser


def _validate_stars_args(args: argparse.Namespace) -> None:
    if args.list_stars:
        if args.repo or args.repos_file:
            raise GhError("--list-stars does not accept --repo or --repos-file.", 64)
        if args.by_list and args.list_id:
            raise GhError("Pass either --by-list or --list-id, not both.", 64)
        return

    if args.by_list or args.list_id:
        raise GhError("--star and --unstar do not accept list filters.", 64)
    if args.all:
        raise GhError("--all is only valid with --list-stars.", 64)
    if args.limit != 100:
        raise GhError("--limit is only valid with --list-stars.", 64)


def stars_main(argv: list[str] | None = None) -> int:
    parser = build_stars_parser()
    args = parser.parse_args(argv)
    try:
        _validate_stars_args(args)
        if args.list_stars:
            return _stars_run_list_stars(args)
        if args.star:
            return _stars_run_write(args, add=True)
        return _stars_run_write(args, add=False)
    except GhError as exc:
        print(str(exc), file=sys.stderr)
        return exc.returncode


# Star-list command implementation

def _lists_positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("Use a positive integer.")
    return number


def _lists_emit(payload: object) -> int:
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def _lists_print_list_summaries(payload: dict[str, object]) -> int:
    print("GitHub star lists")
    print(f"Total: {payload.get('totalCount', 0)}")
    print(f"Shown: {len(payload.get('items') or [])}")
    for item in payload.get("items") or []:
        if not isinstance(item, dict):
            continue
        visibility = "private" if item.get("isPrivate") else "public"
        print(
            f"- {item.get('name')} ({item.get('slug')}) {visibility} items={item.get('itemCount', 'unknown')}"
        )
    return 0


def _lists_print_list_items(payload: dict[str, object]) -> int:
    list_payload = payload.get("list") or {}
    visibility = "private" if list_payload.get("isPrivate") else "public"
    print(f"List items: {list_payload.get('name')} ({list_payload.get('slug')})")
    print(f"Visibility: {visibility}")
    print(f"Total: {payload.get('totalCount', 0)}")
    print(f"Shown: {len(payload.get('items') or [])}")
    for item in payload.get("items") or []:
        if isinstance(item, dict):
            print(f"- {item.get('nameWithOwner')}")
    return 0


def _lists_print_mutation(payload: dict[str, object]) -> int:
    print(f"Action: {payload.get('action')}")
    status = payload.get("status")
    if status:
        print(f"Status: {status}")
    list_payload = payload.get("list")
    if isinstance(list_payload, dict):
        visibility = "private" if list_payload.get("isPrivate") else "public"
        slug = list_payload.get("slug")
        if slug:
            print(f"List: {list_payload.get('name')} ({slug}) [{visibility}]")
        else:
            print(f"List: {list_payload.get('name')} [{visibility}]")
    if "targetCount" in payload:
        print(f"Targets: {payload.get('targetCount')}")
        print(f"Succeeded: {payload.get('successCount')}")
        print(f"Failed: {payload.get('failureCount')}")
        for item in payload.get("results") or []:
            if not isinstance(item, dict):
                continue
            message = item.get("message") or item.get("status")
            print(f"- {item.get('repo')}: {message}")
    return 0


def _lists_delete_list(list_id: str) -> None:
    query = """
    mutation($listId: ID!) {
      deleteUserList(input: {listId: $listId}) {
        user {
          login
        }
      }
    }
    """
    graphql(query, {"listId": list_id})


def _lists_update_list_memberships(repo_id: str, desired_list_ids: list[str]) -> list[dict[str, object]]:
    query = """
    mutation($itemId: ID!, $listIds: [ID!]!) {
      updateUserListsForItem(input: {itemId: $itemId, listIds: $listIds}) {
        lists {
          id
          name
          slug
        }
      }
    }
    """
    payload = graphql(query, {"itemId": repo_id, "listIds": desired_list_ids})
    try:
        lists_payload = payload["data"]["updateUserListsForItem"]["lists"]
    except (TypeError, KeyError) as exc:
        raise GhError("Unexpected update list memberships response shape.") from exc
    return [item for item in lists_payload or [] if isinstance(item, dict)]


def _lists_run_list_lists(args: argparse.Namespace) -> int:
    limit = 0 if args.all else args.limit
    lists_payload = viewer_lists(limit=limit)
    lists = lists_payload.get("items") or []
    enriched_items = []
    for item in lists:
        if not isinstance(item, dict):
            continue
        items_payload = list_items(str(item["id"]), limit=1)
        enriched = dict(item)
        enriched["itemCount"] = items_payload.get("totalCount", 0)
        enriched_items.append(enriched)
    payload = {
        "action": "list-lists",
        "totalCount": lists_payload.get("totalCount", len(enriched_items)),
        "items": enriched_items,
    }
    if args.json:
        return _lists_emit(payload)
    return _lists_print_list_summaries(payload)


def _lists_run_list_items(args: argparse.Namespace) -> int:
    limit = 0 if args.all else args.limit
    selected_list = resolve_list(list_id=args.list_id, selector=args.list)
    items_payload = list_items(str(selected_list["id"]), limit=limit)
    payload = {
        "action": "list-items",
        "list": {
            "id": items_payload.get("id"),
            "name": items_payload.get("name"),
            "slug": items_payload.get("slug"),
            "description": items_payload.get("description"),
            "isPrivate": items_payload.get("isPrivate"),
        },
        "totalCount": items_payload.get("totalCount", 0),
        "items": items_payload.get("items") or [],
    }
    if args.json:
        return _lists_emit(payload)
    return _lists_print_list_items(payload)


def _lists_run_delete(args: argparse.Namespace) -> int:
    selected_list = resolve_list(list_id=args.list_id, selector=args.list)
    if args.dry_run:
        payload = {"action": "delete", "status": "dry-run", "list": selected_list}
    else:
        _lists_delete_list(str(selected_list["id"]))
        payload = {"action": "delete", "status": "deleted", "list": selected_list}
    if args.json:
        return _lists_emit(payload)
    return _lists_print_mutation(payload)


def _lists_run_membership(args: argparse.Namespace, assign: bool) -> int:
    selected_list = resolve_list(list_id=args.list_id, selector=args.list)
    repos = collect_repo_targets(args.repo or [], args.repos_file)
    if not repos:
        raise GhError("At least one target repository is required.", 64)

    resolved_repos: list[dict[str, object]] = []
    results: list[dict[str, object]] = []
    failure_count = 0

    for repo in repos:
        result: dict[str, object] = {"repo": repo}
        try:
            repo_payload = repo_view(repo)
            repo_record = {
                "repo": str(repo_payload["nameWithOwner"]),
                "repoId": str(repo_payload["id"]),
                "url": repo_payload.get("url"),
                "viewerHasStarred": bool(repo_payload.get("viewerHasStarred")),
            }
            resolved_repos.append(repo_record)
            result.update(repo_record)
        except GhError as exc:
            failure_count += 1
            result["status"] = "error"
            result["message"] = str(exc)
        results.append(result)

    memberships = repo_memberships([item["repoId"] for item in resolved_repos])
    repo_index = {item["repo"]: item for item in resolved_repos}

    for result in results:
        repo_name = result.get("repo")
        if result.get("status") == "error" or not isinstance(repo_name, str):
            continue
        repo_record = repo_index[repo_name]
        current_lists = memberships.get(repo_record["repoId"], [])
        current_list_ids = [str(item["id"]) for item in current_lists if isinstance(item, dict) and item.get("id")]
        target_list_id = str(selected_list["id"])

        if assign and not repo_record["viewerHasStarred"]:
            failure_count += 1
            result["status"] = "error"
            result["message"] = "repository is not starred by the authenticated user"
            continue

        if not assign and not repo_record["viewerHasStarred"]:
            result["status"] = "noop"
            result["message"] = "not starred; nothing to remove"
            continue

        if assign:
            if target_list_id in current_list_ids:
                result["status"] = "noop"
                result["message"] = "already assigned to list"
                continue
            desired_list_ids = current_list_ids + [target_list_id]
        else:
            if target_list_id not in current_list_ids:
                result["status"] = "noop"
                result["message"] = "not present in list"
                continue
            desired_list_ids = [item for item in current_list_ids if item != target_list_id]

        if args.dry_run:
            result["status"] = "dry-run"
            result["message"] = "would assign" if assign else "would unassign"
            continue

        try:
            _lists_update_list_memberships(repo_record["repoId"], desired_list_ids)
        except GhError as exc:
            failure_count += 1
            result["status"] = "error"
            result["message"] = str(exc)
            continue

        result["status"] = "changed"
        result["message"] = "assigned" if assign else "unassigned"

    payload = {
        "action": "assign" if assign else "unassign",
        "list": selected_list,
        "targetCount": len(repos),
        "successCount": len(repos) - failure_count,
        "failureCount": failure_count,
        "results": results,
    }
    if args.json:
        _lists_emit(payload)
    else:
        _lists_print_mutation(payload)
    return 1 if failure_count else 0


def build_lists_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stars-lists",
        description="Inspect and update GitHub star lists for the authenticated account.",
    )
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--list-lists", action="store_true")
    action_group.add_argument("--list-items", action="store_true")
    action_group.add_argument("--delete", action="store_true")
    action_group.add_argument("--assign", action="store_true")
    action_group.add_argument("--unassign", action="store_true")

    parser.add_argument("--list", help="Exact list slug or exact list name.")
    parser.add_argument("--list-id", help="Exact GitHub user list id.")
    parser.add_argument("--repo", action="append", default=[], help="Repository in owner/repo format.")
    parser.add_argument("--repos-file", help="Newline-delimited file of owner/repo entries.")
    parser.add_argument("--limit", type=_lists_positive_int, default=100, help="Maximum number of items to return.")
    parser.add_argument("--all", action="store_true", help="Fetch all available items for read actions.")
    parser.add_argument("--json", action="store_true", help="Emit normalized JSON output.")
    parser.add_argument("--dry-run", action="store_true", help="Preview write actions without mutating GitHub.")
    return parser


def _lists_ensure_selector(args: argparse.Namespace) -> None:
    if bool(args.list) == bool(args.list_id):
        raise GhError("Pass exactly one of --list or --list-id.", 64)


def _validate_lists_args(args: argparse.Namespace) -> None:
    if args.list_lists:
        if args.list or args.list_id or args.repo or args.repos_file:
            raise GhError("--list-lists only supports read flags.", 64)
        return

    if args.list_items:
        _lists_ensure_selector(args)
        if args.repo or args.repos_file:
            raise GhError("--list-items only supports a list selector and read flags.", 64)
        return

    if args.delete:
        _lists_ensure_selector(args)
        if args.repo or args.repos_file:
            raise GhError("--delete does not accept repo targets.", 64)
        if args.all:
            raise GhError("--all is only valid with read actions.", 64)
        if args.limit != 100:
            raise GhError("--limit is only valid with read actions.", 64)
        return

    if args.assign or args.unassign:
        _lists_ensure_selector(args)
        if args.all:
            raise GhError("--all is only valid with read actions.", 64)
        if args.limit != 100:
            raise GhError("--limit is only valid with read actions.", 64)
        return


def lists_main(argv: list[str] | None = None) -> int:
    parser = build_lists_parser()
    args = parser.parse_args(argv)
    try:
        _validate_lists_args(args)
        if args.list_lists:
            return _lists_run_list_lists(args)
        if args.list_items:
            return _lists_run_list_items(args)
        if args.delete:
            return _lists_run_delete(args)
        if args.assign:
            return _lists_run_membership(args, assign=True)
        return _lists_run_membership(args, assign=False)
    except GhError as exc:
        print(str(exc), file=sys.stderr)
        return exc.returncode


# Public command dispatcher

from . import __version__ as VERSION
from .health import doctor as shared_doctor, doctor_text


@dataclass(frozen=True)
class RunResult:
    returncode: int
    stdout: str
    stderr: str


def helper_result(main_func: Callable[[list[str] | None], int], argv: list[str]) -> RunResult:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            returncode = int(main_func(argv))
        except SystemExit as exc:
            returncode = int(exc.code) if isinstance(exc.code, int) else 1
    return RunResult(returncode, stdout.getvalue(), stderr.getvalue())


def doctor_payload() -> dict[str, object]:
    return shared_doctor()


def parse_json(stdout: str) -> object:
    cleaned = stdout.strip()
    if not cleaned:
        return None
    return json.loads(cleaned)


def emit_json_result(command: list[str], result: RunResult) -> int:
    if result.returncode == 0:
        payload = {"ok": True, "version": VERSION, "command": command, "data": parse_json(result.stdout)}
    else:
        payload = {
            "ok": False,
            "version": VERSION,
            "command": command,
            "error": {
                "code": "command_failed",
                "message": (result.stderr or result.stdout or "stars command failed").strip(),
            },
        }
    print(json.dumps(payload, indent=2))
    return result.returncode


def invoke(command: list[str], json_mode: bool) -> int:
    if not command:
        print(build_top_parser().format_help(), end="")
        return 0
    domain = command[0]
    if domain == "list":
        argv = ["--list-stars", *command[1:]]
        main_func = stars_main
    elif domain == "add":
        argv = ["--star", *_repo_args(command[1:])]
        main_func = stars_main
    elif domain == "remove":
        argv = ["--unstar", *_repo_args(command[1:])]
        main_func = stars_main
    elif domain == "lists" and len(command) >= 2:
        mapping = {
            "list": "--list-lists",
            "items": "--list-items",
            "delete": "--delete",
            "assign": "--assign",
            "unassign": "--unassign",
        }
        if command[1] not in mapping:
            raise SystemExit(f"Unsupported lists command: {command[1]}")
        argv = [mapping[command[1]], *_list_args(command[1], command[2:])]
        main_func = lists_main
    else:
        raise SystemExit(f"Unsupported command: {' '.join(command)}")
    if json_mode and "--json" not in argv:
        argv.append("--json")
    result = helper_result(main_func, argv)
    if json_mode:
        return emit_json_result(command, result)
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


def _repo_args(args: list[str]) -> list[str]:
    if not args or args[0].startswith("-"):
        return args
    return ["--repo", args[0], *args[1:]]


def _list_args(action: str, args: list[str]) -> list[str]:
    if not args or args[0].startswith("-"):
        return args
    converted = ["--list-id", args[0]]
    rest = args[1:]
    if action in {"assign", "unassign"} and rest and not rest[0].startswith("-"):
        converted += ["--repo", rest[0]]
        rest = rest[1:]
    return [*converted, *rest]


def build_top_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List, star, unstar, and manage authenticated-user GitHub star lists.")
    parser.add_argument("--json", action="store_true", help="Emit a stable JSON envelope.")
    parser.add_argument("--version", action="store_true", help="Print version and exit.")
    parser.add_argument("command", nargs="*", help="Commands: list, add, remove, lists list/items/delete/assign/unassign, doctor.")
    return parser


def main(argv: list[str] | None = None) -> int:
    raw = list(argv if argv is not None else sys.argv[1:])
    if not raw or raw in (["-h"], ["--help"]):
        print(build_top_parser().format_help(), end="")
        return 0
    json_mode = "--json" in raw
    raw = [item for item in raw if item != "--json"]
    if raw == ["--version"]:
        print(VERSION)
        return 0
    if raw == ["doctor"]:
        payload = doctor_payload()
        if json_mode:
            print(json.dumps(payload, indent=2))
        else:
            print(doctor_text(payload, f"gitstack stars {VERSION}"))
        return 0 if payload["ok"] else 1
    try:
        return invoke(raw, json_mode)
    except SystemExit as exc:
        message = str(exc)
        if json_mode:
            print(json.dumps({"ok": False, "version": VERSION, "command": raw, "error": {"code": "invalid_arguments", "message": message}}, indent=2))
        else:
            print(message, file=sys.stderr)
        return 64


if __name__ == "__main__":
    raise SystemExit(main())
