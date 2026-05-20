"""Evidence reference and source-link helpers for code-wiki."""

from __future__ import annotations

import html
from pathlib import Path
from urllib.parse import quote

from code_wiki.git import git_metadata
from code_wiki.wiki_contract import EVIDENCE_REF_RE


def parse_evidence_ref(value: str) -> dict[str, object] | None:
    candidate = html.unescape(value).strip()
    match = EVIDENCE_REF_RE.fullmatch(candidate)
    if not match:
        return None

    rel_path = match.group("path").strip()
    start = int(match.group("start"))
    end = int(match.group("end") or start)
    if not rel_path or start < 1 or end < start:
        return None
    path_parts = Path(rel_path).parts
    if Path(rel_path).is_absolute() or ".." in path_parts:
        return None

    return {
        "label": candidate,
        "path": rel_path,
        "start": start,
        "end": end,
    }


def source_url_for_evidence(repo_arg: str, evidence: str) -> tuple[str | None, str]:
    repo = Path(repo_arg).expanduser().resolve()
    if not repo.is_dir():
        return None, f"repo is not a directory: {repo}"

    parsed = parse_evidence_ref(evidence)
    if not parsed:
        return None, f"invalid evidence reference: {evidence}"

    source_file = (repo / str(parsed["path"])).resolve()
    try:
        source_file.relative_to(repo)
    except ValueError:
        return None, f"evidence path escapes repo: {parsed['path']}"
    if not source_file.is_file():
        return None, f"evidence path does not exist: {parsed['path']}"

    metadata = git_metadata(repo)
    if metadata.get("host") != "github" or not metadata.get("web_url"):
        return None, "no supported online source remote found; use local source fallback"
    if not metadata.get("commit"):
        return None, "repo has no analyzed commit SHA"

    rel_path = quote(str(parsed["path"]), safe="/")
    line_fragment = f"#L{parsed['start']}"
    if parsed["end"] != parsed["start"]:
        line_fragment += f"-L{parsed['end']}"
    return f"{metadata['web_url']}/blob/{metadata['commit']}/{rel_path}{line_fragment}", ""


def render_evidence_chip(repo_arg: str, evidence: str) -> tuple[str | None, str]:
    url, reason = source_url_for_evidence(repo_arg, evidence)
    if not url:
        return None, reason
    parsed = parse_evidence_ref(evidence)
    if not parsed:
        return None, f"invalid evidence reference: {evidence}"
    path = str(parsed["path"])
    file_label = Path(path).name
    if len(file_label) > 34:
        file_label = f"...{file_label[-31:]}"
    line_label = f"L{parsed['start']}"
    if parsed["end"] != parsed["start"]:
        line_label += f"-L{parsed['end']}"
    data_evidence = html.escape(evidence, quote=True)
    href = html.escape(url, quote=True)
    return (
        f'<a class="evidence-chip" href="{href}" data-evidence="{data_evidence}" '
        f'title="{data_evidence}" target="_blank" rel="noopener noreferrer">'
        f'<span class="evidence-file">{html.escape(file_label)}</span>'
        f'<span class="evidence-lines">{html.escape(line_label)}</span></a>',
        "",
    )
