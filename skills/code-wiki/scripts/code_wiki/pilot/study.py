"""Typed adaptive study contract for the opt-in Code Wiki pilot."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

from code_wiki.validation.source_state import large_repo_requires_deep_dives
from code_wiki.wiki_contract import REQUIRED_PAGES


STUDY_SCHEMA = "code-wiki-study"
STUDY_SCHEMA_VERSION = 1
DEEP_DIVE_PREFIX = "pages/deep-dives/"
PAGE_FIELDS = {
    "output_path",
    "title",
    "purpose",
    "claims",
    "section_plan",
    "flows_and_lifecycles",
    "operations_and_tests",
    "failures_and_risks",
    "change_recipes",
    "validation",
    "rollback",
}
TOPIC_FIELDS = (
    "flows_and_lifecycles",
    "operations_and_tests",
    "failures_and_risks",
    "change_recipes",
    "validation",
    "rollback",
)


class StudyContractError(RuntimeError):
    """Raised when a completed study artifact violates the typed contract."""


def _covered_details(value: Any, *, minimum: int) -> list[str] | None:
    if (
        not isinstance(value, dict)
        or set(value) != {"status", "details"}
        or value.get("status") != "covered"
    ):
        return None
    details = value.get("details")
    if (
        not isinstance(details, list)
        or len(details) < minimum
        or any(not isinstance(item, str) or not item.strip() for item in details)
    ):
        return None
    normalized = [item.strip() for item in details]
    return normalized if len(normalized) == len(set(normalized)) else None


def normalize_study_output(study_path: Path) -> bool:
    """Canonicalize exact topic-shaped records observed in live study output."""
    try:
        root = json.loads(study_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(root, dict):
        return False

    changed = False
    applicability = root.get("deep_dives_applicability")
    applicability_details = _covered_details(applicability, minimum=1)
    if applicability_details is not None:
        root["deep_dives_applicability"] = {
            "status": "applicable",
            "reason": " ".join(applicability_details),
        }
        changed = True

    for collection_name in ("fixed_pages", "deep_dives"):
        pages = root.get(collection_name)
        if not isinstance(pages, list):
            continue
        for page in pages:
            if not isinstance(page, dict):
                continue
            plan = _covered_details(page.get("section_plan"), minimum=2)
            if plan is not None:
                page["section_plan"] = plan
                changed = True

    if not changed:
        return False
    study_path.write_text(
        json.dumps(root, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return True


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StudyContractError(f"{field} must be an object")
    return value


def _nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StudyContractError(f"{field} must be a nonempty string")
    return value.strip()


def _string_list(value: Any, field: str, *, minimum: int = 1) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum:
        raise StudyContractError(f"{field} must contain at least {minimum} entries")
    result = [_nonempty_string(item, f"{field}[{index}]") for index, item in enumerate(value)]
    if len(result) != len(set(result)):
        raise StudyContractError(f"{field} contains duplicate entries")
    return result


def _topic(value: Any, field: str) -> None:
    record = _object(value, field)
    if set(record) == {"status", "details"} and record.get("status") == "covered":
        _string_list(record.get("details"), f"{field}.details")
        return
    if set(record) == {"status", "reason"} and record.get("status") == "not-applicable":
        _nonempty_string(record.get("reason"), f"{field}.reason")
        return
    raise StudyContractError(
        f"{field} must be a covered details record or a not-applicable reason record"
    )


def _canonical_relative_path(value: Any, field: str) -> str:
    raw = _nonempty_string(value, field)
    path = PurePosixPath(raw)
    if (
        path.is_absolute()
        or raw != path.as_posix()
        or "\\" in raw
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise StudyContractError(f"{field} must be a canonical repository-relative POSIX path")
    return raw


def _evidence(value: Any, field: str, source_root: Path) -> tuple[str, int, int]:
    record = _object(value, field)
    if set(record) != {"path", "start", "end"}:
        raise StudyContractError(f"{field} must contain only path, start, and end")
    relative = _canonical_relative_path(record.get("path"), f"{field}.path")
    start = record.get("start")
    end = record.get("end")
    if (
        not isinstance(start, int)
        or isinstance(start, bool)
        or not isinstance(end, int)
        or isinstance(end, bool)
        or start < 1
        or end < start
    ):
        raise StudyContractError(f"{field} has an invalid inclusive line range")
    candidate = source_root / relative
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(source_root.resolve())
    except (OSError, RuntimeError, ValueError) as exc:
        raise StudyContractError(f"{field}.path is missing or escapes the source snapshot: {relative}") from exc
    if not resolved.is_file():
        raise StudyContractError(f"{field}.path is not a source file: {relative}")
    try:
        line_count = len(resolved.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError as exc:
        raise StudyContractError(f"{field}.path cannot be read: {relative}: {exc}") from exc
    if end > line_count:
        raise StudyContractError(
            f"{field} range {start}-{end} exceeds {relative} line count {line_count}"
        )
    return relative, start, end


def _page(
    value: Any,
    field: str,
    source_root: Path,
    *,
    minimum_claims: int,
) -> str:
    page = _object(value, field)
    unknown = sorted(set(page) - PAGE_FIELDS)
    missing = sorted(PAGE_FIELDS - set(page))
    if unknown or missing:
        details = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if unknown:
            details.append("unknown=" + ",".join(unknown))
        raise StudyContractError(f"{field} fields are invalid: {'; '.join(details)}")
    output_path = _canonical_relative_path(page.get("output_path"), f"{field}.output_path")
    _nonempty_string(page.get("title"), f"{field}.title")
    _nonempty_string(page.get("purpose"), f"{field}.purpose")
    _string_list(page.get("section_plan"), f"{field}.section_plan", minimum=2)
    for topic_field in TOPIC_FIELDS:
        _topic(page.get(topic_field), f"{field}.{topic_field}")

    claims = page.get("claims")
    if not isinstance(claims, list) or len(claims) < minimum_claims:
        raise StudyContractError(f"{field}.claims must contain at least {minimum_claims} claims")
    claim_texts: list[str] = []
    evidence_records: set[tuple[str, int, int]] = set()
    for claim_index, raw_claim in enumerate(claims):
        claim_field = f"{field}.claims[{claim_index}]"
        claim = _object(raw_claim, claim_field)
        if set(claim) != {"text", "evidence"}:
            raise StudyContractError(f"{claim_field} must contain only text and evidence")
        claim_texts.append(_nonempty_string(claim.get("text"), f"{claim_field}.text"))
        raw_evidence = claim.get("evidence")
        if not isinstance(raw_evidence, list) or not raw_evidence:
            raise StudyContractError(f"{claim_field}.evidence must contain at least one record")
        for evidence_index, raw_record in enumerate(raw_evidence):
            evidence_records.add(
                _evidence(raw_record, f"{claim_field}.evidence[{evidence_index}]", source_root)
            )
    if len(claim_texts) != len(set(claim_texts)):
        raise StudyContractError(f"{field}.claims contains duplicate claim text")
    if len(evidence_records) < 2:
        raise StudyContractError(f"{field} must contain at least two distinct evidence records")
    return output_path


def load_and_validate_study(
    study_path: Path,
    *,
    source_root: Path,
    inventory_path: Path,
    claim_matrix_path: Path,
) -> dict[str, Any]:
    try:
        value = json.loads(study_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StudyContractError(f"cannot read typed study artifact: {exc}") from exc
    root = _object(value, "study")
    expected_root_fields = {
        "schema",
        "schema_version",
        "fixed_pages",
        "deep_dives",
        "deep_dives_applicability",
    }
    if set(root) != expected_root_fields:
        raise StudyContractError("study root fields do not match the typed contract")
    if root.get("schema") != STUDY_SCHEMA:
        raise StudyContractError(f"study.schema must be {STUDY_SCHEMA}")
    if root.get("schema_version") != STUDY_SCHEMA_VERSION:
        raise StudyContractError(f"study.schema_version must be {STUDY_SCHEMA_VERSION}")

    try:
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        claim_matrix = json.loads(claim_matrix_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StudyContractError(f"cannot read prepared study targets: {exc}") from exc
    if not isinstance(inventory, dict) or not isinstance(claim_matrix, dict):
        raise StudyContractError("prepared inventory and claim matrix must be objects")
    page_targets = claim_matrix.get("page_targets")
    prepared_pages = [
        item.get("page") for item in page_targets if isinstance(item, dict)
    ] if isinstance(page_targets, list) else []
    if prepared_pages != REQUIRED_PAGES:
        raise StudyContractError("prepared fixed-page targets do not match the canonical scaffold order")

    fixed_pages = root.get("fixed_pages")
    if not isinstance(fixed_pages, list):
        raise StudyContractError("study.fixed_pages must be a list")
    fixed_paths = [
        _page(page, f"study.fixed_pages[{index}]", source_root, minimum_claims=2)
        for index, page in enumerate(fixed_pages)
    ]
    if fixed_paths != REQUIRED_PAGES:
        raise StudyContractError(
            "study.fixed_pages output paths must exactly match prepared pages in canonical order"
        )

    applicability = _object(root.get("deep_dives_applicability"), "study.deep_dives_applicability")
    if set(applicability) != {"status", "reason"}:
        raise StudyContractError("study.deep_dives_applicability must contain only status and reason")
    status = applicability.get("status")
    reason = applicability.get("reason")
    if status not in {"applicable", "not-applicable"}:
        raise StudyContractError("study.deep_dives_applicability.status is invalid")
    _nonempty_string(reason, "study.deep_dives_applicability.reason")

    required = large_repo_requires_deep_dives(inventory)
    prepared_deep = claim_matrix.get("deep_dive_targets")
    prepared_status = prepared_deep.get("status") if isinstance(prepared_deep, dict) else None
    expected_status = "required" if required else "not_applicable"
    if prepared_status != expected_status:
        raise StudyContractError("prepared deep-dive applicability is inconsistent with inventory")
    if required and status != "applicable":
        raise StudyContractError("study deep dives are required by the prepared repository scope")
    if not required and status != "not-applicable":
        raise StudyContractError("study deep dives must match the prepared not-applicable scope")

    deep_dives = root.get("deep_dives")
    if not isinstance(deep_dives, list):
        raise StudyContractError("study.deep_dives must be a list")
    if required and not 2 <= len(deep_dives) <= 5:
        raise StudyContractError("study.deep_dives must contain two to five pages")
    if not required and deep_dives:
        raise StudyContractError("study.deep_dives must be empty when prepared scope is not applicable")
    deep_paths = [
        _page(page, f"study.deep_dives[{index}]", source_root, minimum_claims=3)
        for index, page in enumerate(deep_dives)
    ]
    for path in deep_paths:
        suffix = path.removeprefix(DEEP_DIVE_PREFIX)
        if not path.startswith(DEEP_DIVE_PREFIX) or not suffix.endswith(".html") or "/" in suffix:
            raise StudyContractError(
                "adaptive deep-dive output paths must be unique leaf HTML files under pages/deep-dives/"
            )
    if deep_paths != sorted(deep_paths) or len(deep_paths) != len(set(deep_paths)):
        raise StudyContractError("study.deep_dives must have unique output paths in canonical order")
    if set(fixed_paths) & set(deep_paths):
        raise StudyContractError("study page output paths must be unique")
    return root
