from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any


REQUEST_KEYS = {
    "repair_id",
    "source_spec_ref",
    "implementation_issue_ref",
    "requested_paths",
    "reason",
    "contract_evidence_refs",
    "evidence_refs",
}
RUNTIME_KEYS = {
    "run_id",
    "root_task_id",
    "worker_id",
    "thread_id",
    "claim_id",
    "assignment_id",
    "assignment_generation",
    "worktree",
    "checkout_path",
}
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def portable_path(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("scope paths must be nonempty portable strings")
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        raise ValueError("scope paths must not be absolute")
    path = value[:-3] if value.endswith("/**") else value.rstrip("/")
    parts = PurePosixPath(path).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError("scope paths must not contain traversal")
    if "*" in path:
        raise ValueError("only a terminal /** wildcard is supported")
    return value


def string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a nonempty list")
    if any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{field} must contain nonempty strings")
    if len(value) != len(set(value)):
        raise ValueError(f"{field} must not contain duplicates")
    return value


def contains(envelope: str, requested: str) -> bool:
    if envelope == requested:
        return True
    if envelope.endswith("/**"):
        return requested.startswith(envelope[:-2])
    if envelope.endswith("/"):
        return requested.startswith(envelope)
    return False


def artifact(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"stable", "allowed_paths"}:
        raise ValueError(f"{label} must contain stable and allowed_paths")
    if not isinstance(value["stable"], dict) or not value["stable"]:
        raise ValueError(f"{label}.stable must be a nonempty object")
    paths = string_list(value["allowed_paths"], f"{label}.allowed_paths")
    for path in paths:
        portable_path(path)
    return {"stable": value["stable"], "allowed_paths": paths}


def validate_scope_repair(
    before: object,
    after: object,
    request: object,
) -> dict[str, object]:
    if not isinstance(request, dict) or set(request) != REQUEST_KEYS:
        raise ValueError("scope_repair_request keys are not exact")
    if set(request) & RUNTIME_KEYS:
        raise ValueError("scope_repair_request contains runtime identity")
    if not UUID_RE.fullmatch(str(request["repair_id"])):
        raise ValueError("repair_id must be a canonical lowercase UUID")
    requested_paths = string_list(request["requested_paths"], "requested_paths")
    for path in requested_paths:
        portable_path(path)
    string_list(request["contract_evidence_refs"], "contract_evidence_refs")
    string_list(request["evidence_refs"], "evidence_refs")
    if not isinstance(request["reason"], str) or not request["reason"].strip():
        raise ValueError("reason must be nonempty")

    if not isinstance(before, dict) or set(before) != {"spec", "issue"}:
        raise ValueError("before bundle must contain spec and issue")
    if not isinstance(after, dict) or set(after) != {"spec", "issue", "audit"}:
        raise ValueError("after bundle must contain spec, issue, and audit")
    before_spec = artifact(before["spec"], "before.spec")
    before_issue = artifact(before["issue"], "before.issue")
    after_spec = artifact(after["spec"], "after.spec")
    after_issue = artifact(after["issue"], "after.issue")

    if before_spec["stable"] != after_spec["stable"]:
        raise ValueError("scope repair changed a stable Feature Spec field")
    if before_issue["stable"] != after_issue["stable"]:
        raise ValueError("scope repair changed a stable issue field")

    old_spec = set(before_spec["allowed_paths"])
    old_issue = set(before_issue["allowed_paths"])
    new_spec = set(after_spec["allowed_paths"])
    new_issue = set(after_issue["allowed_paths"])
    if not old_spec <= new_spec or not old_issue <= new_issue:
        raise ValueError("scope repair removed an allowed path")
    for requested in requested_paths:
        if not any(contains(envelope, requested) for envelope in new_issue):
            raise ValueError(f"requested path is not authorized: {requested}")
    for issue_path in new_issue:
        if not any(contains(spec_path, issue_path) for spec_path in new_spec):
            raise ValueError(f"issue path exceeds Feature Spec scope: {issue_path}")

    audit = after["audit"]
    if not isinstance(audit, dict) or set(audit) != {
        "repair_id",
        "source_spec_ref",
        "implementation_issue_ref",
        "requested_paths",
        "previous_spec_allowed_paths",
        "authorized_spec_allowed_paths",
        "previous_issue_allowed_paths",
        "authorized_issue_allowed_paths",
        "reason",
        "contract_evidence_refs",
        "evidence_refs",
        "completed_operations",
    }:
        raise ValueError("scope repair audit keys are not exact")
    expected_audit = {
        "repair_id": request["repair_id"],
        "source_spec_ref": request["source_spec_ref"],
        "implementation_issue_ref": request["implementation_issue_ref"],
        "requested_paths": requested_paths,
        "previous_spec_allowed_paths": before_spec["allowed_paths"],
        "authorized_spec_allowed_paths": after_spec["allowed_paths"],
        "previous_issue_allowed_paths": before_issue["allowed_paths"],
        "authorized_issue_allowed_paths": after_issue["allowed_paths"],
        "reason": request["reason"],
        "contract_evidence_refs": request["contract_evidence_refs"],
        "evidence_refs": request["evidence_refs"],
        "completed_operations": audit["completed_operations"],
    }
    string_list(audit["completed_operations"], "audit.completed_operations")
    if audit != expected_audit:
        raise ValueError("scope repair audit does not match the before/after bundle")

    changed = old_spec != new_spec or old_issue != new_issue
    return {
        "repair_id": request["repair_id"],
        "repair_outcome": "applied" if changed else "no-op",
        "added_spec_paths": sorted(new_spec - old_spec),
        "added_issue_paths": sorted(new_issue - old_issue),
    }
