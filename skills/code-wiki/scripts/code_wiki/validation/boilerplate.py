"""Repeated prose validation for generated wiki pages."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from code_wiki.validation.text import strip_tags


def normalize_block(value: str) -> str:
    value = strip_tags(value).lower()
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def content_fragment(value: str) -> str:
    match = re.search(r"<main\b[^>]*>(?P<body>.*?)</main>", value, re.IGNORECASE | re.DOTALL)
    fragment = match.group("body") if match else value
    for tag in ("script", "style", "nav", "aside", "footer"):
        fragment = re.sub(
            rf"<{tag}\b.*?</{tag}>",
            " ",
            fragment,
            flags=re.IGNORECASE | re.DOTALL,
        )
    return fragment


def repeated_blocks(html_files: list[Path], wiki_dir: Path) -> list[tuple[str, list[str]]]:
    pages_by_block: dict[str, set[str]] = defaultdict(set)
    for html_file in html_files:
        rel_path = html_file.relative_to(wiki_dir).as_posix()
        text = html_file.read_text(encoding="utf-8", errors="replace")
        fragment = content_fragment(text)
        blocks = re.findall(
            r"<(?:p|li|td|th)\b[^>]*>.*?</(?:p|li|td|th)>",
            fragment,
            flags=re.IGNORECASE | re.DOTALL,
        )
        seen_on_page: set[str] = set()
        for block in blocks:
            normalized = normalize_block(block)
            if len(normalized) < 120:
                continue
            if normalized in seen_on_page:
                continue
            seen_on_page.add(normalized)
            pages_by_block[normalized].add(rel_path)

    repeated: list[tuple[str, list[str]]] = []
    for block, pages in pages_by_block.items():
        if len(pages) >= 3:
            repeated.append((block, sorted(pages)))
    return sorted(repeated, key=lambda item: (item[1], item[0]))


def validate_duplicate_boilerplate(
    html_files: list[Path],
    wiki_dir: Path,
    strict: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    for block, pages in repeated_blocks(html_files, wiki_dir):
        message = (
            "repeated long prose block appears on three or more pages "
            f"({', '.join(pages)}): {block[:120]}"
        )
        if strict:
            errors.append(message)
        else:
            warnings.append(message)
