"""Generated wiki validation for code-wiki."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from common import (
    ANCHOR_RE,
    ATTR_RE,
    COMPREHENSION_PAGE_RULES,
    DEEP_DIVE_INDEX,
    DEEP_DIVE_PAGE_RULE,
    EVIDENCE_BLOCK_RE,
    GENERIC_DIAGRAM_EDGE_SETS,
    GENERIC_PROSE_PATTERNS,
    LARGE_REPO_FILE_THRESHOLD,
    LARGE_REPO_ROOT_THRESHOLD,
    MAX_REVIEW_GRADE_EVIDENCE_RANGE,
    MIN_LARGE_REPO_DEEP_DIVES,
    PLACEHOLDER_MARKERS,
    REQUIRED_PAGES,
    TAG_RE,
    git_output,
)
from evidence import parse_evidence_ref

def is_external_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "mailto", "tel", "data", "javascript"}


def local_target(value: str) -> str:
    return value.split("#", 1)[0].split("?", 1)[0]


def is_deep_dive_content_page(html_rel_path: str) -> bool:
    return html_rel_path.startswith("pages/deep-dives/") and html_rel_path != DEEP_DIVE_INDEX


def comprehension_rule_for_path(html_rel_path: str) -> dict[str, object] | None:
    if is_deep_dive_content_page(html_rel_path):
        return DEEP_DIVE_PAGE_RULE
    return COMPREHENSION_PAGE_RULES.get(html_rel_path)


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


def validate(wiki_arg: str) -> int:
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

    html_files = [
        path
        for path in wiki_dir.rglob("*.html")
        if ".cache" not in path.relative_to(wiki_dir).parts
    ]
    attr_re = re.compile(r"""(?:href|src)=["']([^"']+)["']""", re.IGNORECASE)
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

        for value in attr_re.findall(text):
            if value.startswith("#") or is_external_url(value):
                continue
            target = local_target(value)
            if not target:
                continue
            resolved = (html_file.parent / target).resolve()
            try:
                resolved.relative_to(wiki_dir)
            except ValueError:
                errors.append(f"{rel_html} links outside wiki: {value}")
                continue
            if not resolved.exists():
                errors.append(f"{rel_html} has missing link or asset: {value}")

    if not any((wiki_dir / "assets" / "diagrams").glob("*")):
        warnings.append("assets/diagrams is empty")
    else:
        validate_diagrams(wiki_dir, errors, warnings)

    print_report(errors, warnings)
    return 1 if errors else 0


def parse_attrs(attrs: str) -> dict[str, str]:
    return {match.group("name").lower(): html.unescape(match.group("value")) for match in ATTR_RE.finditer(attrs)}


def strip_tags(value: str) -> str:
    return html.unescape(TAG_RE.sub("", value)).strip()


def main_html_fragment(value: str) -> str:
    match = re.search(r"<main\b[^>]*>(?P<body>.*?)</main>", value, re.IGNORECASE | re.DOTALL)
    return match.group("body") if match else value


def visible_text(value: str) -> str:
    fragment = main_html_fragment(value)
    fragment = re.sub(r"<script\b.*?</script>", " ", fragment, flags=re.IGNORECASE | re.DOTALL)
    fragment = re.sub(r"<style\b.*?</style>", " ", fragment, flags=re.IGNORECASE | re.DOTALL)
    return re.sub(r"\s+", " ", strip_tags(fragment)).strip()


def word_count(value: str) -> int:
    return len(re.findall(r"\b[\w./:-]+\b", value))


def table_texts(value: str) -> list[str]:
    return [
        visible_text(match.group(0)).lower()
        for match in re.finditer(r"<table\b.*?</table>", main_html_fragment(value), re.IGNORECASE | re.DOTALL)
    ]


def any_table_has(table_values: list[str], groups: tuple[tuple[str, ...], ...]) -> bool:
    for table_value in table_values:
        if all(any(term in table_value for term in group) for group in groups):
            return True
    return False


def validate_required_table(
    html_rel_path: str,
    table_values: list[str],
    groups: tuple[tuple[str, ...], ...],
    label: str,
    errors: list[str],
) -> None:
    if not table_values:
        errors.append(f"{html_rel_path} is missing required {label} table")
        return
    if not any_table_has(table_values, groups):
        readable = ", ".join("/".join(group) for group in groups)
        errors.append(f"{html_rel_path} {label} table is missing required columns/concepts: {readable}")


def validate_required_structures(
    html_rel_path: str,
    text: str,
    inventory: dict[str, object],
    errors: list[str],
    warnings: list[str],
) -> None:
    tables = table_texts(text)
    main_text = visible_text(text).lower()

    if html_rel_path == "pages/project-context.html":
        validate_required_table(
            html_rel_path,
            tables,
            (
                ("use case", "capability", "scenario", "user", "audience"),
                ("surface", "entry", "api", "command", "package", "route", "module"),
                ("constraint", "responsibility", "owner", "license", "security", "support"),
            ),
            "project context/use-case",
            errors,
        )
        if "where to go" not in main_text and "official" not in main_text and "upstream" not in main_text:
            warnings.append(f"{html_rel_path} should route readers to official/upstream docs when the repo provides them")

    elif html_rel_path == "pages/public-interfaces.html":
        validate_required_table(
            html_rel_path,
            tables,
            (
                ("surface", "api", "command", "route", "package", "module", "export"),
                ("consumer", "entry", "caller", "usage"),
                ("owner", "file", "module", "path"),
                ("stability", "contract", "public", "internal"),
            ),
            "public surface matrix",
            errors,
        )

    elif html_rel_path == "pages/runtime-state.html":
        validate_required_table(
            html_rel_path,
            tables,
            (
                ("state", "carrier", "lifecycle", "object", "store", "context"),
                ("create", "owner", "initialize", "allocated"),
                ("mutate", "update", "write", "change"),
                ("observe", "callback", "read", "event"),
                ("cleanup", "shutdown", "destroy", "release"),
            ),
            "state/lifecycle",
            errors,
        )

    elif html_rel_path == "pages/flows-advanced.html":
        validate_required_table(
            html_rel_path,
            tables,
            (
                ("trigger", "failure", "condition", "edge"),
                ("detect", "branch", "function", "check"),
                ("owner", "cleanup", "handler"),
                ("effect", "status", "error", "callback", "event"),
                ("recover", "retry", "fallback", "abort", "rollback"),
            ),
            "failure-path",
            errors,
        )

    elif html_rel_path == "pages/testing-and-ops.html":
        validate_required_table(
            html_rel_path,
            tables,
            (
                ("task", "change", "scenario"),
                ("command", "run", "script"),
                ("when", "scope", "source"),
                ("expected", "signal", "artifact", "output"),
            ),
            "exact command",
            errors,
        )
        if not re.search(r"<pre\b|<code\b", main_html_fragment(text), re.IGNORECASE):
            errors.append(f"{html_rel_path} must include copy-paste validation commands in code/pre markup")

    elif html_rel_path == "pages/change-guide.html":
        validate_required_table(
            html_rel_path,
            tables,
            (
                ("change", "task"),
                ("compatibility", "risk", "public", "breaking"),
                ("validation", "test", "command"),
                ("rollback", "backout", "revert"),
            ),
            "compatibility/rollback",
            errors,
        )

    elif html_rel_path == "pages/source-map.html":
        if "generated" not in main_text:
            warnings.append(f"{html_rel_path} should classify generated artifacts or state that none were found")
        if "vendor" not in main_text and "third-party" not in main_text and "third party" not in main_text:
            warnings.append(f"{html_rel_path} should classify vendored or third-party code, or state that none was found")

    if is_deep_dive_content_page(html_rel_path):
        if not any(term in main_text for term in ("state", "flow", "entry", "change", "test", "risk")):
            warnings.append(f"{html_rel_path} should name entrypoints, state/flow, change risks, and tests")


def validate_comprehension_depth(
    html_rel_path: str,
    rule: dict[str, object],
    text: str,
    evidence_count: int,
    evidence_link_count: int,
    errors: list[str],
    warnings: list[str],
) -> None:
    main_text = visible_text(text)
    main_text_lower = main_text.lower()
    section_count = len(re.findall(r"<section\b", main_html_fragment(text), re.IGNORECASE))
    words = word_count(main_text)

    if words < int(rule["min_words"]):
        errors.append(
            f"{html_rel_path} is too thin for developer onboarding "
            f"({words} words, expected at least {rule['min_words']})"
        )
    if section_count < int(rule["min_sections"]):
        errors.append(
            f"{html_rel_path} has too few substantive sections "
            f"({section_count}, expected at least {rule['min_sections']})"
        )
    if evidence_count < int(rule["min_evidence"]):
        errors.append(
            f"{html_rel_path} has too few evidence-backed sections "
            f"({evidence_count}, expected at least {rule['min_evidence']})"
        )
    if evidence_link_count < int(rule["min_evidence_links"]):
        errors.append(
            f"{html_rel_path} has too few source evidence links "
            f"({evidence_link_count}, expected at least {rule['min_evidence_links']})"
        )

    for pattern in rule["patterns"]:
        if not re.search(str(pattern), main_text_lower, re.IGNORECASE):
            errors.append(
                f"{html_rel_path} is missing required comprehension topic matching /{pattern}/"
            )

    for pattern in GENERIC_PROSE_PATTERNS:
        if re.search(pattern, main_text_lower, re.IGNORECASE):
            errors.append(
                f"{html_rel_path} contains generic wiki meta-prose matching /{pattern}/; "
                "replace it with repo-specific explanation"
            )


def validate_diagrams(wiki_dir: Path, errors: list[str], warnings: list[str]) -> None:
    for rel in (
        "assets/diagrams/architecture.svg",
        "assets/diagrams/interaction-map.svg",
        "assets/diagrams/basic-flow.svg",
        "assets/diagrams/advanced-flow.svg",
        "assets/diagrams/dependency-map.svg",
    ):
        path = wiki_dir / rel
        if not path.is_file():
            warnings.append(f"missing recommended diagram: {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        text_nodes = [
            strip_tags(match.group(0)).lower()
            for match in re.finditer(r"<text\b[^>]*>.*?</text>", text, re.IGNORECASE | re.DOTALL)
        ]
        normalized = {node.strip() for node in text_nodes if node.strip()}
        for generic_edges in GENERIC_DIAGRAM_EDGE_SETS:
            if generic_edges.issubset(normalized):
                errors.append(
                    f"{rel} uses generic relationship labels {sorted(generic_edges)}; "
                    "replace label-map arrows with repo-specific relationship verbs"
                )
        if len(normalized) < 8:
            warnings.append(f"{rel} has very few diagram labels; verify it is more than a label map")


def validate_evidence_block(
    html_rel_path: str,
    block_index: int,
    block: str,
    inventory: dict[str, object],
    errors: list[str],
    warnings: list[str],
) -> None:
    anchors = [
        (parse_attrs(match.group("attrs")), strip_tags(match.group("body")))
        for match in ANCHOR_RE.finditer(block)
    ]
    if not anchors:
        errors.append(f"{html_rel_path} evidence block {block_index} has no clickable evidence links")
        return

    if "evidence-chip" not in block:
        warnings.append(f"{html_rel_path} evidence block {block_index} uses links without evidence-chip styling")

    repo_info = inventory.get("repo") if isinstance(inventory.get("repo"), dict) else {}
    repo_path = repo_info.get("path") if isinstance(repo_info, dict) else None
    source_repo = Path(str(repo_path)).expanduser().resolve() if repo_path else None
    web_url = repo_info.get("web_url") if isinstance(repo_info, dict) else None
    commit = repo_info.get("commit") if isinstance(repo_info, dict) else None
    host = repo_info.get("host") if isinstance(repo_info, dict) else None

    for attrs, label in anchors:
        href = attrs.get("href", "")
        evidence_label = attrs.get("data-evidence") or attrs.get("title") or label
        parsed_ref = parse_evidence_ref(evidence_label)
        if parsed_ref and source_repo:
            validate_evidence_file(source_repo, parsed_ref, html_rel_path, errors, warnings)
        if host == "github" and web_url and commit and parsed_ref:
            expected_prefix = f"{web_url}/blob/{commit}/"
            if not href.startswith(expected_prefix):
                errors.append(
                    f"{html_rel_path} evidence link for {evidence_label} is not pinned to analyzed commit"
                )


def validate_evidence_file(
    repo: Path,
    parsed_ref: dict[str, object],
    html_rel_path: str,
    errors: list[str],
    warnings: list[str],
) -> None:
    source_file = (repo / str(parsed_ref["path"])).resolve()
    try:
        source_file.relative_to(repo)
    except ValueError:
        errors.append(f"{html_rel_path} evidence path escapes repo: {parsed_ref['path']}")
        return
    if not source_file.is_file():
        errors.append(f"{html_rel_path} evidence path does not exist: {parsed_ref['path']}")
        return

    try:
        line_count = len(source_file.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError as exc:
        errors.append(f"{html_rel_path} cannot read evidence path {parsed_ref['path']}: {exc}")
        return
    if int(parsed_ref["end"]) > line_count:
        errors.append(
            f"{html_rel_path} evidence line range exceeds file length: "
            f"{parsed_ref['label']} has {line_count} lines"
        )
    if int(parsed_ref["end"]) - int(parsed_ref["start"]) + 1 > MAX_REVIEW_GRADE_EVIDENCE_RANGE:
        warnings.append(
            f"{html_rel_path} evidence range is broad ({parsed_ref['label']}); "
            f"prefer a range of {MAX_REVIEW_GRADE_EVIDENCE_RANGE} lines or less, or pair it with narrower evidence"
        )


def print_report(errors: list[str], warnings: list[str]) -> None:
    if errors:
        print("FAIL")
        for error in errors:
            print(f"ERROR: {error}")
    else:
        print("PASS")
    for warning in warnings:
        print(f"WARN: {warning}")
