"""Local link and asset validation for wiki pages."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse


def is_external_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "mailto", "tel", "data", "javascript"}


def local_target(value: str) -> str:
    return value.split("#", 1)[0].split("?", 1)[0]


def validate_local_references(html_file: Path, wiki_dir: Path, text: str, errors: list[str]) -> None:
    attr_re = re.compile(r"""(?:href|src)=["']([^"']+)["']""", re.IGNORECASE)
    rel_html = html_file.relative_to(wiki_dir)
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

