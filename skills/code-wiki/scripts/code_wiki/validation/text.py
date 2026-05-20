"""HTML text extraction helpers for wiki validation."""

from __future__ import annotations

import html
import re

from code_wiki.wiki_contract import ATTR_RE, TAG_RE


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

