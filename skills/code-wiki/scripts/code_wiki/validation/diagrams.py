"""Diagram-specific validation."""

from __future__ import annotations

import re
from pathlib import Path

from code_wiki.validation.text import strip_tags
from code_wiki.wiki_contract import GENERIC_DIAGRAM_EDGE_SETS


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

