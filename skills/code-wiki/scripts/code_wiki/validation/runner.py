"""Generated wiki validation orchestration for code-wiki."""

from __future__ import annotations

import json
from pathlib import Path

from code_wiki.claim_matrix import validate_claim_matrix
from code_wiki.validation.boilerplate import validate_duplicate_boilerplate
from code_wiki.validation.content import (
    comprehension_rule_for_path,
    is_deep_dive_content_page,
    validate_comprehension_depth,
)
from code_wiki.validation.diagrams import validate_diagrams, validate_polished_diagram_images
from code_wiki.validation.evidence import validate_evidence_block
from code_wiki.validation.links import validate_local_references
from code_wiki.validation.report import print_report
from code_wiki.validation.source_state import (
    large_repo_requires_deep_dives,
    validate_cross_page_coverage,
    validate_source_state,
)
from code_wiki.validation.structures import validate_required_structures
from code_wiki.validation.ui import validate_ui_patterns
from code_wiki.wiki_contract import (
    ANCHOR_RE,
    EVIDENCE_BLOCK_RE,
    MIN_LARGE_REPO_DEEP_DIVES,
    PLACEHOLDER_MARKERS,
    REQUIRED_PAGES,
)


def validate(wiki_arg: str, strict: bool = False) -> int:
    wiki_dir = Path(wiki_arg).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not wiki_dir.is_dir():
        errors.append(f"wiki directory does not exist: {wiki_dir}")
        print_report(errors, warnings)
        return 1

    for rel in REQUIRED_PAGES:
        if not (wiki_dir / rel).is_file():
            errors.append(f"missing required page: {rel}")

    for rel in ("assets/style.css", "assets/app.js"):
        if not (wiki_dir / rel).is_file():
            errors.append(f"missing required asset: {rel}")
    app_js_text = ""
    app_js_path = wiki_dir / "assets" / "app.js"
    if app_js_path.is_file():
        app_js_text = app_js_path.read_text(encoding="utf-8", errors="replace")
    runtime_wraps_tables = "table-wrap" in app_js_text and "querySelectorAll(\"main table\")" in app_js_text

    inventory_path = wiki_dir / "data" / "inventory.json"
    inventory: dict[str, object] = {}
    if not inventory_path.is_file():
        errors.append("missing required data file: data/inventory.json")
    else:
        try:
            inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid data/inventory.json: {exc}")

    if inventory:
        validate_source_state(inventory, warnings)
        validate_cross_page_coverage(wiki_dir, inventory, errors, warnings)

    deep_dive_pages = sorted(
        path
        for path in (wiki_dir / "pages" / "deep-dives").glob("*.html")
        if path.name != "index.html"
    )
    if inventory and large_repo_requires_deep_dives(inventory):
        if len(deep_dive_pages) < MIN_LARGE_REPO_DEEP_DIVES:
            errors.append(
                "large repos require adaptive deep-dive pages: "
                f"found {len(deep_dive_pages)}, expected at least {MIN_LARGE_REPO_DEEP_DIVES} "
                "under pages/deep-dives/"
            )
    if strict:
        if inventory:
            validate_claim_matrix(wiki_dir, inventory, deep_dive_pages, errors)
        else:
            errors.append("strict validation requires valid data/inventory.json before claim-matrix checks")

    html_files = [
        path
        for path in wiki_dir.rglob("*.html")
        if ".cache" not in path.relative_to(wiki_dir).parts
    ]
    for html_file in html_files:
        rel_html = html_file.relative_to(wiki_dir)
        text = html_file.read_text(encoding="utf-8", errors="replace")
        for marker in PLACEHOLDER_MARKERS:
            if marker in text:
                errors.append(f"{rel_html} still contains scaffold placeholder text: {marker}")

        evidence_blocks = [match.group("body") for match in EVIDENCE_BLOCK_RE.finditer(text)]
        html_rel_path = rel_html.as_posix()
        if (html_rel_path in REQUIRED_PAGES or is_deep_dive_content_page(html_rel_path)) and not evidence_blocks:
            errors.append(f"{rel_html} has no evidence block")
        for index, block in enumerate(evidence_blocks, start=1):
            validate_evidence_block(rel_html.as_posix(), index, block, inventory, errors, warnings)

        rule = comprehension_rule_for_path(html_rel_path)
        if rule:
            evidence_link_count = sum(
                len(list(ANCHOR_RE.finditer(block))) for block in evidence_blocks
            )
            validate_comprehension_depth(
                html_rel_path,
                rule,
                text,
                len(evidence_blocks),
                evidence_link_count,
                errors,
                warnings,
            )
            validate_required_structures(html_rel_path, text, inventory, errors, warnings)

        if "<table" in text.lower() and "table-wrap" not in text and not runtime_wraps_tables:
            warnings.append(f"{rel_html} has table markup without an explicit table-wrap container")

        validate_local_references(html_file, wiki_dir, text, errors)
        validate_polished_diagram_images(html_file, wiki_dir, text, strict, errors, warnings)
        validate_ui_patterns(html_file, wiki_dir, text, strict, errors, warnings)

    validate_duplicate_boilerplate(html_files, wiki_dir, strict, errors, warnings)

    if not any((wiki_dir / "assets" / "diagrams").glob("*")):
        warnings.append("assets/diagrams is empty")
    else:
        validate_diagrams(wiki_dir, errors, warnings)

    print_report(errors, warnings)
    return 1 if errors else 0
