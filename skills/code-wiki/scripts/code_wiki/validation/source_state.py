"""Inventory and source-state validation for wiki output."""

from __future__ import annotations

from pathlib import Path

from code_wiki.git import git_output
from code_wiki.validation.text import visible_text
from code_wiki.wiki_contract import LARGE_REPO_FILE_THRESHOLD, LARGE_REPO_ROOT_THRESHOLD


def large_repo_requires_deep_dives(inventory: dict[str, object]) -> bool:
    counts = inventory.get("counts") if isinstance(inventory.get("counts"), dict) else {}
    file_count = int(counts.get("files") or 0) if isinstance(counts, dict) else 0
    source_roots = inventory.get("source_roots") if isinstance(inventory.get("source_roots"), list) else []
    interface_roots = (
        inventory.get("interface_roots") if isinstance(inventory.get("interface_roots"), list) else []
    )
    root_count = len(source_roots) + len(interface_roots)
    return file_count >= LARGE_REPO_FILE_THRESHOLD or root_count >= LARGE_REPO_ROOT_THRESHOLD


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


def validate_source_state(inventory: dict[str, object], warnings: list[str]) -> None:
    repo_info = inventory.get("repo") if isinstance(inventory.get("repo"), dict) else {}
    repo_path = repo_info.get("path") if isinstance(repo_info, dict) else None
    if not repo_path:
        return
    repo = Path(str(repo_path)).expanduser().resolve()
    if not (repo / ".git").exists():
        return
    status = git_output(repo, "status", "--short")
    inventory_dirty = bool(repo_info.get("dirty"))
    if status and not inventory_dirty:
        warnings.append(
            "analyzed source is now dirty but data/inventory.json records dirty=false; "
            "re-run inventory or document post-generation source changes"
        )
    elif not status and inventory_dirty:
        warnings.append(
            "data/inventory.json records dirty=true but analyzed source is currently clean; "
            "re-run inventory before treating evidence as current"
        )


def validate_cross_page_coverage(
    wiki_dir: Path,
    inventory: dict[str, object],
    errors: list[str],
    warnings: list[str],
) -> None:
    source_map_path = wiki_dir / "pages" / "source-map.html"
    if not source_map_path.is_file():
        return
    source_map_text = visible_text(source_map_path.read_text(encoding="utf-8", errors="replace")).lower()

    required_roots: list[str] = []
    for key in ("source_roots", "interface_roots", "test_roots"):
        values = inventory.get(key)
        if isinstance(values, list):
            required_roots.extend(str(value) for value in values)

    missing_roots = []
    for root in required_roots:
        label = root_coverage_label(root).lower()
        if label != "." and label not in source_map_text:
            missing_roots.append(root)
    if missing_roots:
        errors.append(
            "pages/source-map.html does not cover these inventory roots or explicitly scope them out: "
            + ", ".join(missing_roots[:12])
        )

    root_candidates = inventory.get("root_candidates")
    kinds: set[str] = set()
    if isinstance(root_candidates, list):
        for item in root_candidates:
            if isinstance(item, dict) and item.get("kind"):
                kinds.add(str(item["kind"]))
    for kind in sorted(kinds & {"docs", "examples", "fixtures", "generated-docs", "ops", "vendored"}):
        expected = "generated" if kind == "generated-docs" else kind.replace("-", " ")
        if expected not in source_map_text:
            warnings.append(f"pages/source-map.html does not clearly mention {kind} root handling")

    governance_docs = inventory.get("governance_docs")
    if not isinstance(governance_docs, list) or not governance_docs:
        project_context = wiki_dir / "pages" / "project-context.html"
        project_text = ""
        if project_context.is_file():
            project_text = visible_text(project_context.read_text(encoding="utf-8", errors="replace")).lower()
        absence_terms = (
            "no license",
            "no security",
            "no support",
            "no codeowners",
            "no governance",
            "not found",
            "none found",
            "absent",
        )
        if not any(term in project_text for term in absence_terms):
            warnings.append(
                "inventory found no license/security/support/ownership docs; "
                "project-context should state that absence if confirmed"
            )
        return

    project_context = wiki_dir / "pages" / "project-context.html"
    if not project_context.is_file():
        return
    project_text = visible_text(project_context.read_text(encoding="utf-8", errors="replace")).lower()
    for doc in governance_docs:
        stem = Path(str(doc)).stem.lower()
        name = Path(str(doc)).name.lower()
        term = "license" if stem in {"copying", "licence"} else stem
        if term not in project_text and name not in project_text:
            warnings.append(f"pages/project-context.html does not mention governance/support doc {doc}")

