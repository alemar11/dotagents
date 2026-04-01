#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
import urllib.request
from dataclasses import dataclass

INDEX_MARKDOWN_URL = (
    "https://docs.developer.apple.com/tutorials/data/documentation/"
    "xcode-release-notes.md"
)
APPLE_DOCS_BASE = "https://developer.apple.com"
MARKDOWN_DOCS_BASE = "https://docs.developer.apple.com/tutorials/data"


@dataclass
class XcodeInfo:
    version: str | None
    build_version: str | None
    developer_dir: str | None
    app_path: str | None
    resolution_errors: tuple[str, ...]


@dataclass
class ReleaseEntry:
    title: str
    version: str
    is_beta: bool
    page_path: str

    @property
    def source_url(self) -> str:
        return f"{APPLE_DOCS_BASE}{self.page_path.lower()}"

    @property
    def markdown_url(self) -> str:
        return f"{MARKDOWN_DOCS_BASE}{self.page_path.lower()}.md"


@dataclass
class TargetSpec:
    raw: str
    version: str | None
    beta_requested: bool
    normalized_text: str


@dataclass
class MatchResult:
    entry: ReleaseEntry
    matched_candidate: str | None
    fallback_message: str | None
    attempted_versions: tuple[str, ...]


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_text_key(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return normalize_space(lowered)


def run_command(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True).strip()
    except Exception as exc:
        joined = " ".join(args)
        raise RuntimeError(f"Failed to run '{joined}'.") from exc


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "text/markdown,text/plain,text/html,application/xhtml+xml",
            "User-Agent": "xcode-version-changelog",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8")


def derive_app_path(developer_dir: str | None) -> str | None:
    if not developer_dir:
        return None
    marker = ".app/Contents/Developer"
    index = developer_dir.find(marker)
    if index == -1:
        return None
    return developer_dir[: index + len(".app")]


def read_plist_value(app_path: str, key: str) -> str | None:
    plist_path = os.path.join(app_path, "Contents", "Info.plist")
    if not os.path.exists(plist_path):
        return None
    try:
        value = run_command(["plutil", "-extract", key, "raw", plist_path])
    except RuntimeError:
        return None
    return value or None


def get_active_xcode_info() -> XcodeInfo:
    version = None
    build_version = None
    developer_dir = None
    app_path = None
    errors: list[str] = []

    try:
        output = run_command(["xcodebuild", "-version"])
        version_match = re.search(r"^Xcode\s+([0-9]+(?:\.[0-9]+){0,2})$", output, re.M)
        build_match = re.search(r"^Build version\s+(.+)$", output, re.M)
        if version_match:
            version = version_match.group(1)
        else:
            errors.append(f"Unable to parse Xcode version from: {output!r}")
        if build_match:
            build_version = build_match.group(1).strip()
    except RuntimeError as exc:
        errors.append(str(exc))

    try:
        developer_dir_output = run_command(["xcode-select", "-p"])
        developer_dir = developer_dir_output or None
    except RuntimeError as exc:
        errors.append(str(exc))

    app_path = derive_app_path(developer_dir)
    if app_path:
        version = version or read_plist_value(app_path, "CFBundleShortVersionString")
        build_version = build_version or read_plist_value(app_path, "CFBundleVersion")

    return XcodeInfo(
        version=version,
        build_version=build_version,
        developer_dir=developer_dir,
        app_path=app_path,
        resolution_errors=tuple(errors),
    )


def parse_index_entries(markdown: str) -> list[ReleaseEntry]:
    entry_pattern = re.compile(
        r"^\[(Xcode [^\]]+ Release Notes)\]\((/documentation/Xcode-Release-Notes/[^)]+)\)$",
        re.M,
    )
    title_pattern = re.compile(
        r"^Xcode ([0-9]+(?:\.[0-9]+){0,2})( Beta)? Release Notes$"
    )
    entries: list[ReleaseEntry] = []

    for match in entry_pattern.finditer(markdown):
        title = match.group(1)
        page_path = match.group(2)
        title_match = title_pattern.match(title)
        if not title_match:
            continue
        entries.append(
            ReleaseEntry(
                title=title,
                version=title_match.group(1),
                is_beta=bool(title_match.group(2)),
                page_path=page_path,
            )
        )

    if not entries:
        raise RuntimeError("No Xcode release-note entries were parsed from the index.")
    return entries


def parse_target(raw: str) -> TargetSpec:
    normalized_raw = normalize_space(raw)
    version_match = re.search(r"([0-9]+(?:\.[0-9]+){0,2})", normalized_raw)
    return TargetSpec(
        raw=normalized_raw,
        version=version_match.group(1) if version_match else None,
        beta_requested="beta" in normalized_raw.lower(),
        normalized_text=normalize_text_key(normalized_raw),
    )


def candidate_versions(version: str | None) -> list[str]:
    if not version:
        return []
    parts = version.split(".")
    candidates: list[str] = []
    for candidate in (version, ".".join(parts[:2]), parts[0]):
        if candidate and candidate not in candidates:
            candidates.append(candidate)
    return candidates


def choose_same_major_fallback(
    entries: list[ReleaseEntry], target: TargetSpec
) -> ReleaseEntry | None:
    if not target.version:
        return None
    major = target.version.split(".")[0]
    same_major = [entry for entry in entries if entry.version.split(".")[0] == major]
    if not same_major:
        return None
    if target.beta_requested:
        beta_entries = [entry for entry in same_major if entry.is_beta]
        if beta_entries:
            return beta_entries[0]
    stable_entries = [entry for entry in same_major if not entry.is_beta]
    if stable_entries:
        return stable_entries[0]
    return same_major[0]


def match_release_entry(
    entries: list[ReleaseEntry], target: TargetSpec | None
) -> MatchResult:
    if target is None:
        return MatchResult(
            entry=entries[0],
            matched_candidate=None,
            fallback_message=None,
            attempted_versions=(),
        )

    exact_title = next(
        (
            entry
            for entry in entries
            if normalize_text_key(entry.title) == target.normalized_text
        ),
        None,
    )
    if exact_title is not None:
        return MatchResult(
            entry=exact_title,
            matched_candidate=exact_title.version,
            fallback_message=None,
            attempted_versions=tuple(candidate_versions(target.version)),
        )

    attempted_versions = tuple(candidate_versions(target.version))
    for candidate in attempted_versions:
        exact_candidate = next(
            (
                entry
                for entry in entries
                if entry.version == candidate and entry.is_beta == target.beta_requested
            ),
            None,
        )
        if exact_candidate is not None:
            return MatchResult(
                entry=exact_candidate,
                matched_candidate=candidate,
                fallback_message=None,
                attempted_versions=attempted_versions,
            )

    fuzzy_title = next(
        (
            entry
            for entry in entries
            if target.normalized_text and target.normalized_text in normalize_text_key(entry.title)
        ),
        None,
    )
    if fuzzy_title is not None:
        return MatchResult(
            entry=fuzzy_title,
            matched_candidate=fuzzy_title.version,
            fallback_message=None,
            attempted_versions=attempted_versions,
        )

    fallback_entry = choose_same_major_fallback(entries, target) or entries[0]
    fallback_message = "No exact Xcode release notes matched the requested version."
    return MatchResult(
        entry=fallback_entry,
        matched_candidate=None,
        fallback_message=fallback_message,
        attempted_versions=attempted_versions,
    )


def clean_release_markdown(markdown: str) -> str:
    markdown = re.sub(r"^<!--.*?-->\s*", "", markdown, flags=re.S)
    markdown = re.sub(
        r"\n---\n\nCopyright[\s\S]*$",
        "",
        markdown,
        flags=re.I,
    )
    return markdown.strip()


def format_section(title: str, body: str) -> str:
    divider = "=" * len(title)
    return f"{title}\n{divider}\n{body.strip()}"


def build_output(
    info: XcodeInfo, requested_version: str | None, match_result: MatchResult, body: str
) -> str:
    lines: list[str] = []

    if requested_version:
        lines.append(f"Requested version: {requested_version}")
        if info.version:
            lines.append(f"Active Xcode: {info.version}")
    elif info.version:
        lines.append(f"Installed version: {info.version}")
    else:
        lines.append("Installed version: (unavailable)")

    if info.build_version:
        label = "Active build version" if requested_version else "Build version"
        lines.append(f"{label}: {info.build_version}")
    if info.developer_dir:
        lines.append(f"Developer dir: {info.developer_dir}")
    if info.app_path:
        lines.append(f"App path: {info.app_path}")

    if match_result.fallback_message:
        lines.append(match_result.fallback_message)
    elif (
        requested_version
        and match_result.matched_candidate
        and match_result.matched_candidate != parse_target(requested_version).version
    ):
        lines.append(
            f"Matched requested version via normalized candidate: "
            f"{match_result.matched_candidate}"
        )

    if match_result.attempted_versions and match_result.fallback_message:
        lines.append(f"Attempted versions: {', '.join(match_result.attempted_versions)}")

    if info.resolution_errors and not info.version:
        lines.append(f"Resolution note: {info.resolution_errors[0]}")

    lines.extend(
        [
            f"Matched release notes: {match_result.entry.title}",
            f"Source: {match_result.entry.source_url}",
            "",
            body,
        ]
    )
    return format_section("Xcode", "\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print Apple Xcode release notes for the active or requested version."
    )
    parser.add_argument(
        "--version",
        help="Explicit Xcode version label to match, for example '26.5 beta' or '16.4'.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    info = get_active_xcode_info()

    target = parse_target(args.version) if args.version else None
    if target is None and info.version:
        target = parse_target(info.version)

    entries = parse_index_entries(fetch_text(INDEX_MARKDOWN_URL))
    match_result = match_release_entry(entries, target)
    release_body = clean_release_markdown(fetch_text(match_result.entry.markdown_url))

    print(build_output(info, args.version, match_result, release_body))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
