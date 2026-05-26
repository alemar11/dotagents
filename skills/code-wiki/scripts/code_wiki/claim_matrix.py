"""Claim-matrix scaffolding and validation for code-wiki."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from code_wiki.evidence import parse_evidence_ref
from code_wiki.wiki_contract import (
    MAX_REVIEW_GRADE_EVIDENCE_RANGE,
    MIN_LARGE_REPO_DEEP_DIVES,
    REQUIRED_PAGES,
)

CLAIM_MATRIX_SCHEMA_VERSION = 1
READY_STATUS = "ready"
NOT_APPLICABLE_STATUS = "not_applicable"


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON at {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"expected object JSON at {path}")
    return data


def write_json(path_arg: str, data: dict[str, Any]) -> None:
    path = Path(path_arg).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def required_root_entries(inventory: dict[str, Any]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(root: str, kind: str, reason: str) -> None:
        key = (root, kind)
        if key in seen:
            return
        seen.add(key)
        entries.append(
            {
                "root": root,
                "kind": kind,
                "reason": reason,
                "status": "pending",
                "not_applicable_reason": "",
            }
        )

    for key, kind, reason in (
        ("source_roots", "source", "primary source root"),
        ("interface_roots", "interfaces", "public interface root"),
        ("test_roots", "test", "test root"),
    ):
        values = inventory.get(key)
        if isinstance(values, list):
            for value in values:
                add(str(value), kind, reason)

    governance_docs = inventory.get("governance_docs")
    if isinstance(governance_docs, list):
        for value in governance_docs:
            add(str(value), "governance", "license, ownership, security, support, or notice document")

    return sorted(entries, key=lambda item: (item["kind"], item["root"]))


def page_targets() -> list[dict[str, Any]]:
    return [
        {
            "page": page,
            "min_ready_claims": 2,
            "status": "pending",
        }
        for page in REQUIRED_PAGES
    ]


def synthesize_claim_matrix(repo_arg: str, inventory_arg: str, out_arg: str) -> dict[str, Any]:
    repo = Path(repo_arg).expanduser().resolve()
    if not repo.is_dir():
        raise SystemExit(f"repo is not a directory: {repo}")

    inventory_path = Path(inventory_arg).expanduser().resolve()
    inventory = load_json(inventory_path)
    repo_info = inventory.get("repo") if isinstance(inventory.get("repo"), dict) else {}
    matrix = {
        "schema_version": CLAIM_MATRIX_SCHEMA_VERSION,
        "repo": {
            "name": repo_info.get("name", repo.name) if isinstance(repo_info, dict) else repo.name,
            "path": str(repo),
            "web_url": repo_info.get("web_url") if isinstance(repo_info, dict) else None,
            "commit": repo_info.get("commit") if isinstance(repo_info, dict) else None,
            "dirty": repo_info.get("dirty") if isinstance(repo_info, dict) else None,
        },
        "inventory": {
            "path": str(inventory_path),
            "schema_version": inventory.get("schema_version"),
            "counts": inventory.get("counts", {}),
        },
        "page_targets": page_targets(),
        "deep_dive_targets": {
            "minimum_pages": MIN_LARGE_REPO_DEEP_DIVES,
            "min_ready_claims_per_page": 3,
            "status": "pending",
            "suggested_pages": [],
        },
        "coverage_roots": required_root_entries(inventory),
        "claims": [],
    }
    write_json(out_arg, matrix)
    return matrix


def normalize_claim(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def evidence_key(parsed_ref: dict[str, object]) -> str:
    return f"{parsed_ref['path']}:{parsed_ref['start']}-{parsed_ref['end']}"


def path_covers_root(evidence_path: str, root: str) -> bool:
    if root == ".":
        return True
    if evidence_path == root:
        return True
    return evidence_path.startswith(f"{root.rstrip('/')}/")


def root_coverage_label(root: str) -> str:
    if root == ".":
        return root
    parts = root.split("/")
    while parts and parts[-1].lower() in {
        "include",
        "includes",
        "interface",
        "interfaces",
        "lib",
        "source",
        "sources",
        "src",
        "test",
        "tests",
    }:
        parts.pop()
    return "/".join(parts) or root


def source_repo_from_inventory(inventory: dict[str, Any]) -> Path | None:
    repo_info = inventory.get("repo") if isinstance(inventory.get("repo"), dict) else {}
    repo_path = repo_info.get("path") if isinstance(repo_info, dict) else None
    if not repo_path:
        return None
    return Path(str(repo_path)).expanduser().resolve()


def validate_claim_evidence(
    claim_index: int,
    claim: dict[str, Any],
    source_repo: Path | None,
    errors: list[str],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    raw_evidence = claim.get("evidence")
    if not isinstance(raw_evidence, list) or not raw_evidence:
        errors.append(f"claim-matrix claim {claim_index} is ready but has no evidence refs")
        return [], []

    parsed_refs: list[dict[str, object]] = []
    broad_refs: list[dict[str, object]] = []
    for raw_ref in raw_evidence:
        if not isinstance(raw_ref, str):
            errors.append(f"claim-matrix claim {claim_index} evidence entry is not a string")
            continue
        parsed = parse_evidence_ref(raw_ref)
        if not parsed:
            errors.append(f"claim-matrix claim {claim_index} has invalid evidence ref: {raw_ref}")
            continue
        parsed_refs.append(parsed)

        if source_repo:
            source_file = (source_repo / str(parsed["path"])).resolve()
            try:
                source_file.relative_to(source_repo)
            except ValueError:
                errors.append(f"claim-matrix claim {claim_index} evidence path escapes repo: {parsed['path']}")
                continue
            if not source_file.is_file():
                errors.append(f"claim-matrix claim {claim_index} evidence path does not exist: {parsed['path']}")
                continue
            try:
                line_count = len(source_file.read_text(encoding="utf-8", errors="replace").splitlines())
            except OSError as exc:
                errors.append(f"claim-matrix claim {claim_index} cannot read evidence path {parsed['path']}: {exc}")
                continue
            if int(parsed["end"]) > line_count:
                errors.append(
                    f"claim-matrix claim {claim_index} evidence line range exceeds file length: "
                    f"{parsed['label']} has {line_count} lines"
                )

        if int(parsed["end"]) - int(parsed["start"]) + 1 > MAX_REVIEW_GRADE_EVIDENCE_RANGE:
            broad_refs.append(parsed)

    if parsed_refs and len(parsed_refs) == len(broad_refs):
        errors.append(
            f"claim-matrix claim {claim_index} relies only on broad evidence ranges; "
            f"add at least one range of {MAX_REVIEW_GRADE_EVIDENCE_RANGE} lines or less"
        )

    return parsed_refs, broad_refs


def coverage_not_applicable(matrix: dict[str, Any], root: str, kind: str) -> bool:
    coverage_roots = matrix.get("coverage_roots")
    if not isinstance(coverage_roots, list):
        return False
    for item in coverage_roots:
        if not isinstance(item, dict):
            continue
        if str(item.get("root")) != root or str(item.get("kind")) != kind:
            continue
        if item.get("status") != NOT_APPLICABLE_STATUS:
            return False
        reason = item.get("not_applicable_reason")
        return isinstance(reason, str) and bool(reason.strip())
    return False


def validate_claim_matrix(
    wiki_dir: Path,
    inventory: dict[str, Any],
    deep_dive_pages: list[Path],
    errors: list[str],
) -> None:
    matrix_path = wiki_dir / "data" / "claim-matrix.json"
    if not matrix_path.is_file():
        errors.append("strict validation requires data/claim-matrix.json")
        return

    try:
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid data/claim-matrix.json: {exc}")
        return
    if not isinstance(matrix, dict):
        errors.append("data/claim-matrix.json must contain an object")
        return
    if matrix.get("schema_version") != CLAIM_MATRIX_SCHEMA_VERSION:
        errors.append(
            f"data/claim-matrix.json schema_version must be {CLAIM_MATRIX_SCHEMA_VERSION}"
        )

    top_level_shapes = {
        "repo": dict,
        "inventory": dict,
        "page_targets": list,
        "deep_dive_targets": dict,
        "coverage_roots": list,
    }
    for field, expected_type in top_level_shapes.items():
        if not isinstance(matrix.get(field), expected_type):
            errors.append(f"data/claim-matrix.json {field} must be a {expected_type.__name__}")

    page_targets_value = matrix.get("page_targets")
    if isinstance(page_targets_value, list):
        target_pages = {
            str(item.get("page"))
            for item in page_targets_value
            if isinstance(item, dict) and item.get("page")
        }
        missing_targets = [page for page in REQUIRED_PAGES if page not in target_pages]
        if missing_targets:
            errors.append(
                "data/claim-matrix.json page_targets is missing required pages: "
                + ", ".join(missing_targets)
            )

    coverage_roots_value = matrix.get("coverage_roots")
    if isinstance(coverage_roots_value, list):
        for index, item in enumerate(coverage_roots_value, start=1):
            if not isinstance(item, dict):
                errors.append(f"claim-matrix coverage_roots entry {index} must be an object")
                continue
            for field in ("root", "kind", "status", "not_applicable_reason"):
                if field not in item:
                    errors.append(f"claim-matrix coverage_roots entry {index} is missing {field}")

    claims = matrix.get("claims")
    if not isinstance(claims, list):
        errors.append("data/claim-matrix.json claims must be a list")
        return

    required_fields = ("claim", "page", "evidence", "why_it_matters", "status")
    ready_by_page: dict[str, list[str]] = defaultdict(list)
    claim_pages_by_text: dict[str, set[str]] = defaultdict(set)
    broad_pages_by_ref: dict[str, set[str]] = defaultdict(set)
    covered_roots: set[tuple[str, str]] = set()
    source_repo = source_repo_from_inventory(inventory)

    for index, raw_claim in enumerate(claims, start=1):
        if not isinstance(raw_claim, dict):
            errors.append(f"claim-matrix claim {index} must be an object")
            continue
        for field in required_fields:
            if field not in raw_claim:
                errors.append(f"claim-matrix claim {index} is missing required field: {field}")

        status = raw_claim.get("status")
        if status != READY_STATUS:
            continue

        claim_text = raw_claim.get("claim")
        page = raw_claim.get("page")
        why = raw_claim.get("why_it_matters")
        if not isinstance(claim_text, str) or not normalize_claim(claim_text):
            errors.append(f"claim-matrix claim {index} is ready but claim text is empty")
            continue
        if not isinstance(page, str) or not page:
            errors.append(f"claim-matrix claim {index} is ready but page is empty")
            continue
        if not isinstance(why, str) or not why.strip():
            errors.append(f"claim-matrix claim {index} is ready but why_it_matters is empty")

        normalized = normalize_claim(claim_text)
        ready_by_page[page].append(normalized)
        claim_pages_by_text[normalized].add(page)

        parsed_refs, broad_refs = validate_claim_evidence(index, raw_claim, source_repo, errors)
        for parsed in parsed_refs:
            evidence_path = str(parsed["path"])
            for root_entry in required_root_entries(inventory):
                root = root_entry["root"]
                kind = root_entry["kind"]
                if path_covers_root(evidence_path, root):
                    covered_roots.add((root, kind))
        for parsed in broad_refs:
            broad_pages_by_ref[evidence_key(parsed)].add(page)

    for page in REQUIRED_PAGES:
        unique_claims = set(ready_by_page.get(page, []))
        if len(unique_claims) < 2:
            errors.append(
                f"strict validation requires at least 2 ready, non-duplicate claims for {page}"
            )

    for deep_dive_page in deep_dive_pages:
        rel_page = deep_dive_page.relative_to(wiki_dir).as_posix()
        unique_claims = set(ready_by_page.get(rel_page, []))
        if len(unique_claims) < 3:
            errors.append(
                f"strict validation requires at least 3 ready claims for deep dive {rel_page}"
            )

    for normalized, pages in sorted(claim_pages_by_text.items()):
        if len(pages) > 1:
            joined = ", ".join(sorted(pages))
            errors.append(f"claim-matrix repeats the same ready claim across pages: {joined}: {normalized[:90]}")

    duplicate_counts = Counter()
    for page, normalized_values in ready_by_page.items():
        for normalized, count in Counter(normalized_values).items():
            if count > 1:
                duplicate_counts[(page, normalized)] = count
    for (page, normalized), count in sorted(duplicate_counts.items()):
        errors.append(f"claim-matrix has duplicate ready claims on {page}: {count} copies of {normalized[:90]}")

    for ref, pages in sorted(broad_pages_by_ref.items()):
        if len(pages) > 2:
            errors.append(
                f"broad evidence range {ref} is reused across more than two pages: "
                + ", ".join(sorted(pages))
            )

    for root_entry in required_root_entries(inventory):
        root = root_entry["root"]
        kind = root_entry["kind"]
        key = (root, kind)
        if key in covered_roots or coverage_not_applicable(matrix, root, kind):
            continue
        label = root_coverage_label(root)
        errors.append(
            f"strict validation requires claim evidence coverage for {kind} root {root} "
            f"(coverage label {label}) or a not_applicable coverage_roots entry with a reason"
        )
