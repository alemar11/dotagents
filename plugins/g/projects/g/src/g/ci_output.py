from __future__ import annotations

import io
import re
import zipfile
from collections.abc import Sequence
from typing import Any

FAILURE_MARKERS = (
    "error",
    "fail",
    "failed",
    "traceback",
    "exception",
    "assert",
    "panic",
    "fatal",
    "timeout",
    "segmentation fault",
)

PENDING_LOG_MARKERS = (
    "still in progress",
    "log will be available when it is complete",
)


def extract_run_id(url: str) -> str | None:
    if not url:
        return None
    for pattern in (r"/actions/runs/(\d+)", r"/runs/(\d+)"):
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def extract_job_id(url: str) -> str | None:
    if not url:
        return None
    match = re.search(r"/actions/runs/\d+/job/(\d+)", url)
    if match:
        return match.group(1)
    match = re.search(r"/job/(\d+)", url)
    return match.group(1) if match else None


def extract_log_from_job_archive(payload: bytes) -> tuple[str, str]:
    if not payload:
        return "", "Job logs endpoint returned empty payload."
    if not zipfile.is_zipfile(io.BytesIO(payload)):
        return payload.decode(errors="replace"), ""

    try:
        with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
            names = [name for name in archive.namelist() if not name.endswith("/")]
            if not names:
                return "", "Job logs archive contains no files."
            best_text = ""
            for name in names:
                raw = archive.read(name)
                if raw:
                    text = raw.decode(errors="replace")
                    if len(text) > len(best_text):
                        best_text = text
            if not best_text.strip():
                return (
                    "",
                    f"Job logs archive is empty or unreadable; entries: {', '.join(names)}",
                )
            return best_text, ""
    except (zipfile.BadZipFile, KeyError, ValueError) as exc:
        return "", f"Unable to parse job log archive: {exc}"


def normalize_field(value: Any) -> str:
    return "" if value is None else str(value).strip().lower()


def parse_available_fields(message: str) -> list[str]:
    if "Available fields:" not in message:
        return []
    fields: list[str] = []
    in_block = False
    for line in message.splitlines():
        if "Available fields:" in line:
            in_block = True
            _, suffix = line.split(":", 1)
            value = suffix.strip()
            if value:
                fields.extend(
                    field.strip() for field in value.split(",") if field.strip()
                )
            continue
        if in_block:
            value = line.strip()
            if value and not value.startswith("Available fields:"):
                fields.append(value)
    return fields


def is_log_pending_message(message: str) -> bool:
    lowered = message.lower()
    return any(marker in lowered for marker in PENDING_LOG_MARKERS)


def extract_failure_snippet(log_text: str, max_lines: int, context: int) -> str:
    lines = log_text.splitlines()
    if not lines:
        return ""
    marker_index = find_failure_index(lines)
    if marker_index is None:
        return "\n".join(lines[-max_lines:])
    start = max(0, marker_index - context)
    end = min(len(lines), marker_index + context + 1)
    window = lines[start:end]
    if len(window) > max_lines:
        window = window[-max_lines:]
    return "\n".join(window)


def find_failure_index(lines: Sequence[str]) -> int | None:
    for index in range(len(lines) - 1, -1, -1):
        lowered = lines[index].lower()
        if any(marker in lowered for marker in FAILURE_MARKERS):
            return index
    return None


def tail_lines(text: str, max_lines: int) -> str:
    if max_lines <= 0:
        return ""
    return "\n".join(text.splitlines()[-max_lines:])


def render_results(payload: dict[str, Any]) -> str:
    repo = str(payload.get("repo") or "")
    pr = str(payload.get("pr") or "")
    results = list(payload.get("results") or [])
    if payload.get("summary") == "no_checks":
        return f"PR #{pr} in {repo}: no checks configured or reported.\n"
    if not results:
        return f"PR #{pr} in {repo}: no failing checks detected.\n"

    lines = [f"PR #{pr} in {repo}: {len(results)} failing checks analyzed."]
    for result in results:
        lines.append("-" * 60)
        lines.append(f"Check: {result.get('name', '')}")
        if result.get("detailsUrl"):
            lines.append(f"Details: {result['detailsUrl']}")
        if result.get("status"):
            lines.append(f"Status: {result['status']}")
        run_meta = result.get("run", {})
        if run_meta.get("url"):
            lines.append(f"Run URL: {run_meta['url']}")
        if result.get("jobId"):
            lines.append(f"Job ID: {result['jobId']}")
        if result.get("note"):
            lines.append(f"Note: {result['note']}")
        if result.get("error"):
            lines.append(f"Error fetching logs: {result['error']}")
            continue
        snippet = result.get("logSnippet") or ""
        if snippet:
            lines.extend(("Failure snippet:", indent_block(snippet)))
        else:
            lines.append("No snippet available.")
    lines.append("-" * 60)
    return "\n".join(lines) + "\n"


def indent_block(text: str, prefix: str = "  ") -> str:
    return "\n".join(f"{prefix}{line}" for line in text.splitlines())
