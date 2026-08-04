from __future__ import annotations

import json
from typing import Any, Iterable
from urllib.parse import quote

from .common import GError, run, safe_diagnostic
from .provider_text import graphql_request


SCHEMA_VERSION = "1.0.0"
MAX_GRAPHQL_PAGES = 100
MAX_REST_PAGES = 100

DELIVERY_QUERY = """
query DeliveryStatus(
  $owner: String!
  $repo: String!
  $number: Int!
  $checksAfter: String
  $threadsAfter: String
  $closingAfter: String
) {
  repository(owner: $owner, name: $repo) {
    nameWithOwner
    autoMergeAllowed
    mergeCommitAllowed
    rebaseMergeAllowed
    squashMergeAllowed
    viewerPermission
    pullRequest(number: $number) {
      number
      url
      state
      isDraft
      baseRefName
      headRefName
      headRefOid
      mergeable
      mergeStateStatus
      reviewDecision
      autoMergeRequest {
        enabledAt
        mergeMethod
        enabledBy { login }
      }
      mergeQueueEntry { state }
      statusCheckRollup {
        state
        contexts(first: 100, after: $checksAfter) {
          nodes {
            __typename
            ... on CheckRun {
              name
              status
              conclusion
              detailsUrl
              checkSuite { app { databaseId slug } }
            }
            ... on StatusContext {
              context
              state
              targetUrl
            }
          }
          pageInfo { hasNextPage endCursor }
        }
      }
      reviewThreads(first: 100, after: $threadsAfter) {
        nodes { id isResolved }
        pageInfo { hasNextPage endCursor }
      }
      closingIssuesReferences(first: 100, after: $closingAfter) {
        nodes { number repository { nameWithOwner } }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}
"""


IRRELEVANT_TO_MERGE = {
    "creation",
    "deletion",
    "non_fast_forward",
    "copilot_code_review",
}


def _provider_object(result: Any, *, operation: str) -> dict[str, Any]:
    if result.returncode:
        diagnostic = safe_diagnostic(result.stderr or result.stdout)
        raise GError(
            diagnostic or f"GitHub {operation} failed.",
            code="provider_read_failed",
            exit_code=result.returncode,
            details={"operation": operation},
        )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise GError(
            f"GitHub {operation} returned unreadable JSON.",
            code="provider_response_invalid",
            exit_code=65,
        ) from exc
    if not isinstance(payload, dict):
        raise GError(
            f"GitHub {operation} returned an unexpected response shape.",
            code="provider_response_invalid",
            exit_code=65,
        )
    return payload


def _connection(pr: dict[str, Any], name: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    value = pr.get(name)
    if not isinstance(value, dict):
        return [], {"hasNextPage": False, "endCursor": None}
    nodes = value.get("nodes")
    page_info = value.get("pageInfo")
    return (
        [item for item in nodes if isinstance(item, dict)] if isinstance(nodes, list) else [],
        page_info if isinstance(page_info, dict) else {"hasNextPage": False, "endCursor": None},
    )


def _status_connection(pr: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rollup = pr.get("statusCheckRollup")
    if not isinstance(rollup, dict):
        return [], {"hasNextPage": False, "endCursor": None}
    contexts = rollup.get("contexts")
    if not isinstance(contexts, dict):
        return [], {"hasNextPage": False, "endCursor": None}
    nodes = contexts.get("nodes")
    page_info = contexts.get("pageInfo")
    return (
        [item for item in nodes if isinstance(item, dict)] if isinstance(nodes, list) else [],
        page_info if isinstance(page_info, dict) else {"hasNextPage": False, "endCursor": None},
    )


def _read_pull_request(owner: str, repo: str, number: int) -> tuple[dict[str, Any], bool]:
    cursors: dict[str, str | None] = {"checksAfter": None, "threadsAfter": None, "closingAfter": None}
    active_connections = set(cursors)
    checks: list[dict[str, Any]] = []
    threads: list[dict[str, Any]] = []
    closing: list[dict[str, Any]] = []
    repository: dict[str, Any] | None = None
    pull_request: dict[str, Any] | None = None
    complete = True

    for _ in range(MAX_GRAPHQL_PAGES):
        result = graphql_request(
            DELIVERY_QUERY,
            {"owner": owner, "repo": repo, "number": number, **cursors},
        )
        payload = _provider_object(result, operation="GraphQL delivery-status query")
        errors = payload.get("errors")
        if errors:
            raise GError(
                "GitHub GraphQL delivery-status query returned errors.",
                code="provider_response_invalid",
                exit_code=65,
                details={"errors": errors},
            )
        data = payload.get("data")
        current_repo = data.get("repository") if isinstance(data, dict) else None
        if not isinstance(current_repo, dict):
            raise GError("GitHub repository was not found.", code="repo_context_missing", exit_code=3)
        current_pr = current_repo.get("pullRequest")
        if not isinstance(current_pr, dict):
            raise GError("GitHub pull request was not found.", code="pr_context_missing", exit_code=3)
        if repository is None:
            repository = dict(current_repo)
            repository.pop("pullRequest", None)
            pull_request = dict(current_pr)

        pages = {
            "checksAfter": (*_status_connection(current_pr), checks),
            "threadsAfter": (*_connection(current_pr, "reviewThreads"), threads),
            "closingAfter": (*_connection(current_pr, "closingIssuesReferences"), closing),
        }
        for key in tuple(active_connections):
            nodes, info, destination = pages[key]
            destination.extend(nodes)
            if info.get("hasNextPage") is True:
                cursor = info.get("endCursor")
                if not isinstance(cursor, str) or not cursor:
                    complete = False
                    active_connections.remove(key)
                    continue
                cursors[key] = cursor
            else:
                active_connections.remove(key)
        if not active_connections:
            break
    else:
        complete = False

    assert repository is not None and pull_request is not None
    rollup = pull_request.get("statusCheckRollup")
    if isinstance(rollup, dict):
        rollup = dict(rollup)
        rollup["contexts"] = checks
        pull_request["statusCheckRollup"] = rollup
    pull_request["reviewThreads"] = threads
    pull_request["closingIssuesReferences"] = closing
    return {"repository": repository, "pull_request": pull_request}, complete


def _rest_json(endpoint: str, *, optional: bool = False) -> tuple[Any | None, str | None]:
    result = run([
        "gh", "api", "--method", "GET", endpoint,
        "--header", "Accept: application/vnd.github+json",
        "--header", "X-GitHub-Api-Version: 2022-11-28",
    ])
    if result.returncode:
        diagnostic = safe_diagnostic(result.stderr or result.stdout)
        if optional:
            return None, diagnostic or "provider-read-unavailable"
        raise GError(
            diagnostic or "GitHub REST delivery-status read failed.",
            code="provider_read_failed",
            exit_code=result.returncode,
            details={"endpoint": endpoint},
        )
    try:
        return json.loads(result.stdout), None
    except json.JSONDecodeError as exc:
        if optional:
            return None, "provider-response-invalid"
        raise GError(
            "GitHub REST delivery-status read returned unreadable JSON.",
            code="provider_response_invalid",
            exit_code=65,
        ) from exc


def _read_rules(repository: str, branch: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    encoded_branch = quote(branch, safe="")
    rules: list[dict[str, Any]] = []
    unavailable: list[dict[str, Any]] = []
    for page in range(1, MAX_REST_PAGES + 1):
        rules_value, rules_error = _rest_json(
            f"/repos/{repository}/rules/branches/{encoded_branch}?per_page=100&page={page}",
            optional=True,
        )
        if rules_error:
            unavailable.append({"surface": "active-branch-rules", "reason": rules_error})
            break
        page_rules = [item for item in rules_value if isinstance(item, dict)] if isinstance(rules_value, list) else []
        rules.extend(page_rules)
        if len(page_rules) < 100:
            break
    else:
        unavailable.append({"surface": "active-branch-rules", "reason": "pagination-limit-reached"})

    rulesets: list[dict[str, Any]] = []
    ruleset_ids = sorted({item.get("ruleset_id") for item in rules if isinstance(item.get("ruleset_id"), int)})
    for ruleset_id in ruleset_ids:
        value, error = _rest_json(
            f"/repos/{repository}/rulesets/{ruleset_id}?includes_parents=true",
            optional=True,
        )
        if isinstance(value, dict):
            rulesets.append(value)
        elif error:
            unavailable.append({"surface": f"ruleset-{ruleset_id}", "reason": error})

    protection, protection_error = _rest_json(
        f"/repos/{repository}/branches/{encoded_branch}/protection",
        optional=True,
    )
    if protection_error:
        unavailable.append({"surface": "classic-branch-protection", "reason": protection_error})
    return rules, rulesets, {
        "classic_branch_protection": protection if isinstance(protection, dict) else None,
        "unavailable": unavailable,
    }


def _rule_types(rules: Iterable[dict[str, Any]]) -> set[str]:
    return {item["type"] for item in rules if isinstance(item.get("type"), str)}


def _required_checks(rules: Iterable[dict[str, Any]], protection: dict[str, Any] | None) -> set[tuple[str, int | None]]:
    required: set[tuple[str, int | None]] = set()
    rule_contexts: set[str] = set()
    for rule in rules:
        if rule.get("type") != "required_status_checks":
            continue
        parameters = rule.get("parameters")
        values = parameters.get("required_status_checks") if isinstance(parameters, dict) else None
        if isinstance(values, list):
            for value in values:
                context = value.get("context") if isinstance(value, dict) else None
                if isinstance(context, str) and context:
                    integration_id = value.get("integration_id")
                    app_id = integration_id if isinstance(integration_id, int) and integration_id > 0 else None
                    required.add((context, app_id))
                    rule_contexts.add(context)
    protection_checks = protection.get("required_status_checks") if isinstance(protection, dict) else None
    if not isinstance(protection_checks, dict):
        return required
    check_contexts: set[str] = set()
    checks = protection_checks.get("checks")
    if isinstance(checks, list):
        for value in checks:
            if not isinstance(value, dict):
                continue
            context = value.get("context")
            if not isinstance(context, str) or not context or context in rule_contexts:
                continue
            app_id_value = value.get("app_id")
            app_id = app_id_value if isinstance(app_id_value, int) and app_id_value > 0 else None
            required.add((context, app_id))
            check_contexts.add(context)
    contexts = protection_checks.get("contexts")
    if isinstance(contexts, list):
        for context in contexts:
            if isinstance(context, str) and context and context not in rule_contexts and context not in check_contexts:
                required.add((context, None))
    return required


def _check_name(item: dict[str, Any]) -> str | None:
    value = item.get("name") if item.get("__typename") == "CheckRun" else item.get("context")
    return value if isinstance(value, str) else None


def _check_app_id(item: dict[str, Any]) -> int | None:
    suite = item.get("checkSuite")
    app = suite.get("app") if isinstance(suite, dict) else None
    value = app.get("databaseId") if isinstance(app, dict) else None
    return value if isinstance(value, int) else None


def _check_state(item: dict[str, Any]) -> str:
    if item.get("__typename") == "CheckRun":
        status = str(item.get("status") or "UNKNOWN").upper()
        if status != "COMPLETED":
            return "pending"
        conclusion = str(item.get("conclusion") or "UNKNOWN").upper()
        if conclusion in {"SUCCESS", "NEUTRAL", "SKIPPED"}:
            return "passing"
        if conclusion in {"ACTION_REQUIRED", "CANCELLED", "FAILURE", "STALE", "STARTUP_FAILURE", "TIMED_OUT"}:
            return "failing"
        return "unknown"
    state = str(item.get("state") or "UNKNOWN").upper()
    if state == "SUCCESS":
        return "passing"
    if state in {"EXPECTED", "PENDING"}:
        return "pending"
    if state in {"ERROR", "FAILURE"}:
        return "failing"
    return "unknown"


def _pull_request_rule_state(rules: Iterable[dict[str, Any]], pr: dict[str, Any], unresolved_threads: int) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    pending: list[str] = []
    for rule in rules:
        if rule.get("type") != "pull_request":
            continue
        parameters = rule.get("parameters")
        if not isinstance(parameters, dict):
            continue
        approvals = parameters.get("required_approving_review_count")
        requires_review = isinstance(approvals, int) and approvals > 0
        requires_review = requires_review or parameters.get("require_code_owner_review") is True
        requires_review = requires_review or parameters.get("require_last_push_approval") is True
        decision = pr.get("reviewDecision")
        if requires_review and decision != "APPROVED":
            if decision == "CHANGES_REQUESTED":
                blockers.append("changes-requested")
            else:
                pending.append("required-review")
        if parameters.get("required_review_thread_resolution") is True and unresolved_threads:
            blockers.append("required-review-threads-unresolved")
    return blockers, pending


def _requires_up_to_date(rules: Iterable[dict[str, Any]], protection: dict[str, Any] | None) -> bool:
    for rule in rules:
        if rule.get("type") != "required_status_checks":
            continue
        parameters = rule.get("parameters")
        if isinstance(parameters, dict) and parameters.get("strict_required_status_checks_policy") is True:
            return True
    required = protection.get("required_status_checks") if isinstance(protection, dict) else None
    return isinstance(required, dict) and required.get("strict") is True


def _classify(
    pr: dict[str, Any],
    rules: list[dict[str, Any]],
    protection: dict[str, Any] | None,
    *,
    expected_head: str | None,
    provider_complete: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    pending: list[str] = []
    warnings: list[str] = []
    head = pr.get("headRefOid")
    state = str(pr.get("state") or "UNKNOWN").upper()
    mergeable = str(pr.get("mergeable") or "UNKNOWN").upper()
    merge_state = str(pr.get("mergeStateStatus") or "UNKNOWN").upper()
    threads = pr.get("reviewThreads")
    unresolved_threads = sum(1 for item in threads if isinstance(item, dict) and item.get("isResolved") is False) if isinstance(threads, list) else 0

    if expected_head and head != expected_head:
        blockers.append("head-mismatch")
    if state != "OPEN":
        blockers.append("pull-request-not-open")
    if pr.get("isDraft") is True:
        blockers.append("draft")

    review_blockers, review_pending = _pull_request_rule_state(rules, pr, unresolved_threads)
    blockers.extend(review_blockers)
    pending.extend(review_pending)

    rollup = pr.get("statusCheckRollup")
    contexts = rollup.get("contexts") if isinstance(rollup, dict) else None
    contexts = [item for item in contexts if isinstance(item, dict)] if isinstance(contexts, list) else []
    by_name: dict[str, list[dict[str, Any]]] = {}
    for item in contexts:
        name = _check_name(item)
        if name:
            by_name.setdefault(name, []).append(item)
    for name, app_id in sorted(_required_checks(rules, protection), key=lambda item: (item[0], item[1] or -1)):
        matches = by_name.get(name, [])
        if app_id is not None:
            matches = [item for item in matches if _check_app_id(item) == app_id]
        label = f"{name}@{app_id}" if app_id is not None else name
        if not matches:
            pending.append(f"required-check-missing:{label}")
            continue
        states = {_check_state(item) for item in matches}
        if "failing" in states:
            blockers.append(f"required-check-failing:{label}")
        elif "pending" in states:
            pending.append(f"required-check-pending:{label}")
        elif "unknown" in states:
            warnings.append(f"required-check-unknown:{label}")

    if mergeable == "CONFLICTING" or merge_state == "DIRTY":
        disposition = "conflicting"
    elif mergeable == "UNKNOWN" or merge_state == "UNKNOWN":
        disposition = "pending"
        pending.append("mergeability-calculating")
    elif blockers:
        disposition = "blocked"
    elif pending:
        disposition = "pending"
    elif mergeable != "MERGEABLE":
        disposition = "unknown"
        warnings.append(f"unrecognized-mergeable:{mergeable}")
    elif merge_state in {"CLEAN", "HAS_HOOKS"}:
        disposition = "ready"
    elif merge_state == "BLOCKED":
        types = _rule_types(rules)
        unsupported = sorted(types - IRRELEVANT_TO_MERGE - {"update", "pull_request", "required_status_checks"})
        if "update" in types and not unsupported:
            disposition = "ready-with-manual-action"
        else:
            disposition = "unknown"
            warnings.extend(f"unattributed-rule:{value}" for value in unsupported)
            if "update" not in types:
                warnings.append("blocked-cause-unattributed")
    elif merge_state == "UNSTABLE":
        disposition = "ready"
    elif merge_state == "BEHIND":
        if _requires_up_to_date(rules, protection):
            disposition = "blocked"
            blockers.append("head-behind-required")
        else:
            disposition = "ready"
    elif merge_state == "DRAFT":
        disposition = "blocked"
        blockers.append("draft")
    else:
        disposition = "unknown"
        warnings.append(f"unrecognized-merge-state:{merge_state}")

    if not provider_complete:
        warnings.append("provider-evidence-incomplete")

    return {
        "disposition": disposition,
        "attribution": "verified" if disposition in {"ready", "ready-with-manual-action", "blocked", "conflicting"} and not warnings else "partial",
        "blockers": sorted(set(blockers)),
        "pending": sorted(set(pending)),
        "warnings": sorted(set(warnings)),
    }


def inspect_delivery_status(repository: str, pr_number: int, expected_head: str | None = None) -> dict[str, Any]:
    if "/" not in repository:
        raise GError("Repository must use owner/repo.", code="invalid_arguments", exit_code=64)
    owner, repo = repository.split("/", 1)
    if pr_number <= 0:
        raise GError("Pull request number must be positive.", code="invalid_arguments", exit_code=64)
    if expected_head is not None and (len(expected_head) != 40 or any(ch not in "0123456789abcdefABCDEF" for ch in expected_head)):
        raise GError("Expected HEAD must be one full commit SHA.", code="invalid_arguments", exit_code=64)

    graphql_data, graphql_complete = _read_pull_request(owner, repo, pr_number)
    repo_data = graphql_data["repository"]
    pr = graphql_data["pull_request"]
    base = pr.get("baseRefName")
    if not isinstance(base, str) or not base:
        raise GError("Pull request base branch is unavailable.", code="provider_response_invalid", exit_code=65)
    rules, rulesets, protection_data = _read_rules(repository, base)
    unavailable = protection_data["unavailable"]
    provider_complete = graphql_complete and not any(item.get("surface") == "active-branch-rules" for item in unavailable)
    classification = _classify(
        pr,
        rules,
        protection_data["classic_branch_protection"],
        expected_head=expected_head,
        provider_complete=provider_complete,
    )

    rollup = pr.get("statusCheckRollup")
    contexts = rollup.get("contexts") if isinstance(rollup, dict) else []
    threads = pr.get("reviewThreads")
    closing = pr.get("closingIssuesReferences")
    return {
        "schema_version": SCHEMA_VERSION,
        "identity": {
            "repository": repo_data.get("nameWithOwner") or repository,
            "pull_request": pr.get("number"),
            "url": pr.get("url"),
            "base_branch": base,
            "head_branch": pr.get("headRefName"),
            "head_sha": pr.get("headRefOid"),
            "expected_head": expected_head,
            "expected_head_matches": expected_head is None or pr.get("headRefOid") == expected_head,
        },
        "lifecycle": {"state": str(pr.get("state") or "UNKNOWN").lower(), "draft": pr.get("isDraft") is True},
        "technical_mergeability": {
            "provider_value": pr.get("mergeable"),
            "normalized": str(pr.get("mergeable") or "unknown").lower(),
        },
        "policy": {
            "merge_state_status": pr.get("mergeStateStatus"),
            "review_decision": pr.get("reviewDecision"),
            "status_rollup_state": rollup.get("state") if isinstance(rollup, dict) else None,
            "active_rules": rules,
            "rulesets": rulesets,
            "classic_branch_protection": protection_data["classic_branch_protection"],
        },
        "checks": contexts if isinstance(contexts, list) else [],
        "review_threads": {
            "total": len(threads) if isinstance(threads, list) else 0,
            "unresolved": sum(1 for item in threads if isinstance(item, dict) and item.get("isResolved") is False) if isinstance(threads, list) else 0,
        },
        "automation": {
            "repository_auto_merge_allowed": repo_data.get("autoMergeAllowed"),
            "pr_auto_merge_request": pr.get("autoMergeRequest"),
            "merge_queue_entry": pr.get("mergeQueueEntry"),
        },
        "merge_methods": {
            "merge": repo_data.get("mergeCommitAllowed"),
            "rebase": repo_data.get("rebaseMergeAllowed"),
            "squash": repo_data.get("squashMergeAllowed"),
        },
        "viewer_permission": repo_data.get("viewerPermission"),
        "closing_issue_refs": closing if isinstance(closing, list) else [],
        "classification": classification,
        "completeness": {
            "complete": provider_complete,
            "graphql_connections_complete": graphql_complete,
            "unavailable_surfaces": unavailable,
        },
    }
