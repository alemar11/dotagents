"""Content-depth validation for wiki pages."""

from __future__ import annotations

import re

from code_wiki.wiki_contract import (
    COMPREHENSION_PAGE_RULES,
    DEEP_DIVE_INDEX,
    DEEP_DIVE_PAGE_RULE,
    GENERIC_PROSE_PATTERNS,
)
from code_wiki.validation.text import main_html_fragment, visible_text, word_count


def is_deep_dive_content_page(html_rel_path: str) -> bool:
    return html_rel_path.startswith("pages/deep-dives/") and html_rel_path != DEEP_DIVE_INDEX


def comprehension_rule_for_path(html_rel_path: str) -> dict[str, object] | None:
    if is_deep_dive_content_page(html_rel_path):
        return DEEP_DIVE_PAGE_RULE
    return COMPREHENSION_PAGE_RULES.get(html_rel_path)


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

