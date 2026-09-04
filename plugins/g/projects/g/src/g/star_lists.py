from __future__ import annotations

import argparse
import json
import sys

from .star_api import (
    GhError,
    collect_repo_targets,
    graphql,
    list_items,
    repo_memberships,
    repo_view,
    resolve_list,
    viewer_lists,
)


def _positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("Use a positive integer.")
    return number


def _emit(payload: object) -> int:
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def _print_list_summaries(payload: dict[str, object]) -> int:
    print("GitHub star lists")
    print(f"Total: {payload.get('totalCount', 0)}")
    print(f"Shown: {len(payload.get('items') or [])}")
    for item in payload.get("items") or []:
        if isinstance(item, dict):
            visibility = "private" if item.get("isPrivate") else "public"
            print(
                f"- {item.get('name')} ({item.get('slug')}) {visibility} items={item.get('itemCount', 'unknown')}"
            )
    return 0


def _print_list_items(payload: dict[str, object]) -> int:
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


def _print_mutation(payload: dict[str, object]) -> int:
    print(f"Action: {payload.get('action')}")
    if payload.get("status"):
        print(f"Status: {payload.get('status')}")
    list_payload = payload.get("list")
    if isinstance(list_payload, dict):
        visibility = "private" if list_payload.get("isPrivate") else "public"
        slug = list_payload.get("slug")
        suffix = f" ({slug})" if slug else ""
        print(f"List: {list_payload.get('name')}{suffix} [{visibility}]")
    if "targetCount" in payload:
        print(f"Targets: {payload.get('targetCount')}")
        print(f"Succeeded: {payload.get('successCount')}")
        print(f"Failed: {payload.get('failureCount')}")
        for item in payload.get("results") or []:
            if isinstance(item, dict):
                print(
                    f"- {item.get('repo')}: {item.get('message') or item.get('status')}"
                )
    return 0


def _delete_list(list_id: str) -> None:
    query = """
    mutation($listId: ID!) {
      deleteUserList(input: {listId: $listId}) { user { login } }
    }
    """
    graphql(query, {"listId": list_id})


def _update_memberships(
    repo_id: str, desired_list_ids: list[str]
) -> list[dict[str, object]]:
    query = """
    mutation($itemId: ID!, $listIds: [ID!]!) {
      updateUserListsForItem(input: {itemId: $itemId, listIds: $listIds}) {
        lists { id name slug }
      }
    }
    """
    payload = graphql(query, {"itemId": repo_id, "listIds": desired_list_ids})
    try:
        lists_payload = payload["data"]["updateUserListsForItem"]["lists"]
    except (TypeError, KeyError) as exc:
        raise GhError("Unexpected update list memberships response shape.") from exc
    return [item for item in lists_payload or [] if isinstance(item, dict)]


def _run_list_lists(args: argparse.Namespace) -> int:
    limit = 0 if args.all else args.limit
    lists_payload = viewer_lists(limit=limit)
    enriched_items = []
    for item in lists_payload.get("items") or []:
        if isinstance(item, dict):
            items_payload = list_items(str(item["id"]), limit=1)
            enriched = dict(item)
            enriched["itemCount"] = items_payload.get("totalCount", 0)
            enriched_items.append(enriched)
    payload = {
        "action": "list-lists",
        "totalCount": lists_payload.get("totalCount", len(enriched_items)),
        "items": enriched_items,
    }
    return _emit(payload) if args.json else _print_list_summaries(payload)


def _run_list_items(args: argparse.Namespace) -> int:
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
    return _emit(payload) if args.json else _print_list_items(payload)


def _run_delete(args: argparse.Namespace) -> int:
    selected_list = resolve_list(list_id=args.list_id, selector=args.list)
    if args.dry_run:
        payload = {"action": "delete", "status": "dry-run", "list": selected_list}
    else:
        _delete_list(str(selected_list["id"]))
        payload = {"action": "delete", "status": "deleted", "list": selected_list}
    return _emit(payload) if args.json else _print_mutation(payload)


def _run_membership(args: argparse.Namespace, assign: bool) -> int:
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
            result.update(status="error", message=str(exc))
        results.append(result)

    memberships = repo_memberships([str(item["repoId"]) for item in resolved_repos])
    repo_index = {str(item["repo"]): item for item in resolved_repos}
    for result in results:
        repo_name = result.get("repo")
        if result.get("status") == "error" or not isinstance(repo_name, str):
            continue
        repo_record = repo_index[repo_name]
        repo_id = str(repo_record["repoId"])
        current_lists = memberships.get(repo_id, [])
        current_ids = [
            str(item["id"])
            for item in current_lists
            if isinstance(item, dict) and item.get("id")
        ]
        target_id = str(selected_list["id"])

        if assign and not repo_record["viewerHasStarred"]:
            failure_count += 1
            result.update(
                status="error",
                message="repository is not starred by the authenticated user",
            )
            continue
        if not assign and not repo_record["viewerHasStarred"]:
            result.update(status="noop", message="not starred; nothing to remove")
            continue
        if assign and target_id in current_ids:
            result.update(status="noop", message="already assigned to list")
            continue
        if not assign and target_id not in current_ids:
            result.update(status="noop", message="not present in list")
            continue

        desired_ids = (
            current_ids + [target_id]
            if assign
            else [item for item in current_ids if item != target_id]
        )
        if args.dry_run:
            result.update(
                status="dry-run", message="would assign" if assign else "would unassign"
            )
            continue
        try:
            _update_memberships(repo_id, desired_ids)
        except GhError as exc:
            failure_count += 1
            result.update(status="error", message=str(exc))
            continue
        result.update(status="changed", message="assigned" if assign else "unassigned")

    payload = {
        "action": "assign" if assign else "unassign",
        "list": selected_list,
        "targetCount": len(repos),
        "successCount": len(repos) - failure_count,
        "failureCount": failure_count,
        "results": results,
    }
    (_emit if args.json else _print_mutation)(payload)
    return 1 if failure_count else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stars-lists",
        description="Inspect and update GitHub star lists for the authenticated account.",
    )
    actions = parser.add_mutually_exclusive_group(required=True)
    for name in ("list-lists", "list-items", "delete", "assign", "unassign"):
        actions.add_argument(f"--{name}", action="store_true")
    parser.add_argument("--list", help="Exact list slug or exact list name.")
    parser.add_argument("--list-id", help="Exact GitHub user list id.")
    parser.add_argument(
        "--repo", action="append", default=[], help="Repository in owner/repo format."
    )
    parser.add_argument(
        "--repos-file", help="Newline-delimited file of owner/repo entries."
    )
    parser.add_argument(
        "--limit",
        type=_positive_int,
        default=100,
        help="Maximum number of items to return.",
    )
    parser.add_argument(
        "--all", action="store_true", help="Fetch all available items for read actions."
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit normalized JSON output."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview write actions without mutating GitHub.",
    )
    return parser


def _ensure_selector(args: argparse.Namespace) -> None:
    if bool(args.list) == bool(args.list_id):
        raise GhError("Pass exactly one of --list or --list-id.", 64)


def _validate_args(args: argparse.Namespace) -> None:
    if args.list_lists:
        if args.list or args.list_id or args.repo or args.repos_file:
            raise GhError("--list-lists only supports read flags.", 64)
        return
    if args.list_items:
        _ensure_selector(args)
        if args.repo or args.repos_file:
            raise GhError(
                "--list-items only supports a list selector and read flags.", 64
            )
        return
    _ensure_selector(args)
    if args.delete and (args.repo or args.repos_file):
        raise GhError("--delete does not accept repo targets.", 64)
    if args.all:
        raise GhError("--all is only valid with read actions.", 64)
    if args.limit != 100:
        raise GhError("--limit is only valid with read actions.", 64)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _validate_args(args)
        if args.list_lists:
            return _run_list_lists(args)
        if args.list_items:
            return _run_list_items(args)
        if args.delete:
            return _run_delete(args)
        return _run_membership(args, assign=bool(args.assign))
    except GhError as exc:
        print(str(exc), file=sys.stderr)
        return exc.returncode
