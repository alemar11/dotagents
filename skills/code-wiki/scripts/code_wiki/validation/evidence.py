"""Evidence-link validation for wiki pages."""

from __future__ import annotations

from pathlib import Path

from code_wiki.evidence import parse_evidence_ref
from code_wiki.validation.text import parse_attrs, strip_tags
from code_wiki.wiki_contract import ANCHOR_RE, MAX_REVIEW_GRADE_EVIDENCE_RANGE


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

