"""UI-pattern validation for generated wiki pages."""

from __future__ import annotations

import re
from pathlib import Path

from code_wiki.validation.text import parse_attrs

FIGURE_RE = re.compile(r"<figure\b(?P<attrs>[^>]*)>(?P<body>.*?)</figure>", re.IGNORECASE | re.DOTALL)
IMG_RE = re.compile(r"<img\b(?P<attrs>[^>]*)>", re.IGNORECASE | re.DOTALL)


def add_ui_issue(message: str, strict: bool, errors: list[str], warnings: list[str]) -> None:
    if strict:
        errors.append(message)
    else:
        warnings.append(message)


def validate_ui_patterns(
    html_file: Path,
    wiki_dir: Path,
    text: str,
    strict: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    rel_html = html_file.resolve().relative_to(wiki_dir.resolve()).as_posix()

    evidence_chip_count = len(re.findall(r"\bevidence-chip\b", text))
    collapsible_evidence_count = len(
        re.findall(r"<details\b[^>]*class=[\"'][^\"']*\bevidence\b", text, re.IGNORECASE)
    )
    if evidence_chip_count >= 12 and collapsible_evidence_count == 0:
        add_ui_issue(
            f"{rel_html} has {evidence_chip_count} evidence chips but no collapsible details.evidence block",
            strict,
            errors,
            warnings,
        )

    for match in FIGURE_RE.finditer(text):
        figure_attrs = parse_attrs(match.group("attrs"))
        figure_class = figure_attrs.get("class", "")
        body = match.group("body")
        image_match = IMG_RE.search(body)
        if not image_match:
            continue
        image_attrs = parse_attrs(image_match.group("attrs"))
        src = image_attrs.get("src", "").replace("\\", "/")
        if "assets/diagrams/" not in src and "../assets/diagrams/" not in src:
            continue
        if "diagram-frame" not in figure_class and "hybrid-diagram" not in figure_class:
            add_ui_issue(
                f"{rel_html} embeds diagram {src} without diagram-frame or hybrid-diagram figure class",
                strict,
                errors,
                warnings,
            )
