"""Diagram-specific validation."""

from __future__ import annotations

import re
from pathlib import Path

from code_wiki.validation.links import is_external_url, local_target
from code_wiki.validation.text import parse_attrs, strip_tags
from code_wiki.wiki_contract import GENERIC_DIAGRAM_EDGE_SETS

IMG_RE = re.compile(r"""<img\b(?P<attrs>[^>]*)>""", re.IGNORECASE | re.DOTALL)
FACTUAL_DIAGRAM_TERMS = (
    "architecture",
    "component",
    "dependency",
    "diagram",
    "flow",
    "interaction",
    "lifecycle",
    "topology",
)
SOURCE_DIAGRAM_ATTRS = ("data-source-diagram", "data-canonical-diagram", "data-source-svg")


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


def looks_like_polished_diagram(src: str, attrs: dict[str, str]) -> bool:
    suffix = Path(local_target(src)).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return False
    if "assets/images/" not in src.replace("\\", "/"):
        return False
    searchable = " ".join(
        [
            src,
            attrs.get("alt", ""),
            attrs.get("class", ""),
            attrs.get("title", ""),
            attrs.get("data-diagram-kind", ""),
        ]
    ).lower()
    return any(term in searchable for term in FACTUAL_DIAGRAM_TERMS)


def source_diagram_ref(attrs: dict[str, str]) -> str:
    for attr in SOURCE_DIAGRAM_ATTRS:
        value = attrs.get(attr)
        if value:
            return value
    return ""


def validate_polished_diagram_images(
    html_file: Path,
    wiki_dir: Path,
    text: str,
    strict: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    wiki_root = wiki_dir.resolve()
    html_path = html_file.resolve()
    rel_html = html_path.relative_to(wiki_root).as_posix()
    for match in IMG_RE.finditer(text):
        attrs = parse_attrs(match.group("attrs"))
        src = attrs.get("src", "")
        if not src or src.startswith("#") or is_external_url(src):
            continue
        if not looks_like_polished_diagram(src, attrs):
            continue

        source_ref = source_diagram_ref(attrs)
        if not source_ref:
            message = (
                f"{rel_html} polished factual diagram image {src} is missing "
                "data-source-diagram pointing to deterministic SVG/spec"
            )
            if strict:
                errors.append(message)
            else:
                warnings.append(message)
            continue

        source_target = local_target(source_ref)
        source_path = (html_path.parent / source_target).resolve()
        try:
            source_path.relative_to(wiki_root)
        except ValueError:
            errors.append(f"{rel_html} polished diagram source points outside wiki: {source_ref}")
            continue
        if not source_path.exists():
            errors.append(f"{rel_html} polished diagram source does not exist: {source_ref}")
            continue
        if source_path.suffix.lower() not in {".svg", ".json", ".mmd", ".html"}:
            message = (
                f"{rel_html} polished diagram source should be deterministic SVG/spec, "
                f"got {source_ref}"
            )
            if strict:
                errors.append(message)
            else:
                warnings.append(message)
