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
STABLE_CHANNEL = "stable"
BETA_CHANNEL = "beta"


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
    release_channel: str
    beta_iteration: int | None
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
    release_channel: str
    beta_iteration: int | None
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
        version_match = re.search(r"^Xcode\s+([0-9]+(?:\.[0-9]+){0,2})$", output, re.MULTILINE)
        build_match = re.search(r"^Build version\s+(.+)$", output, re.MULTILINE)
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
        re.MULTILINE,
    )
    title_pattern = re.compile(
        r"^Xcode (?P<version>[0-9]+(?:\.[0-9]+){0,2})"
        r"(?: (?P<beta>Beta)(?: (?P<beta_iteration>[0-9]+))?)?"
        r" Release Notes$"
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
                version=title_match.group("version"),
                release_channel=(
                    BETA_CHANNEL if title_match.group("beta") else STABLE_CHANNEL
                ),
                beta_iteration=(
                    int(title_match.group("beta_iteration"))
                    if title_match.group("beta_iteration")
                    else None
                ),
                page_path=page_path,
            )
        )

    if not entries:
        raise RuntimeError("No Xcode release-note entries were parsed from the index.")
    return entries


def parse_target(raw: str) -> TargetSpec:
    normalized_raw = normalize_space(raw)
    version_match = re.search(r"([0-9]+(?:\.[0-9]+){0,2})", normalized_raw)
    beta_match = re.search(r"\bbeta(?:\s+([0-9]+))?\b", normalized_raw, re.IGNORECASE)
    return TargetSpec(
        raw=normalized_raw,
        version=version_match.group(1) if version_match else None,
        release_channel=BETA_CHANNEL if beta_match else STABLE_CHANNEL,
        beta_iteration=(
            int(beta_match.group(1)) if beta_match and beta_match.group(1) else None
        ),
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
    if target.release_channel == BETA_CHANNEL:
        if target.beta_iteration is not None:
            return None
        beta_entries = [
            entry
            for entry in same_major
            if entry.release_channel == BETA_CHANNEL
        ]
        if beta_entries:
            return beta_entries[0]
        return None
    stable_entries = [
        entry for entry in same_major if entry.release_channel == STABLE_CHANNEL
    ]
    if stable_entries:
        return stable_entries[0]
    return None


def choose_latest_fallback(
    entries: list[ReleaseEntry], release_channel: str
) -> ReleaseEntry:
    matching_entries = [
        entry for entry in entries if entry.release_channel == release_channel
    ]
    if matching_entries:
        return matching_entries[0]
    raise RuntimeError(f"No Xcode {release_channel} release notes are available.")


def choose_latest_stable_entry(entries: list[ReleaseEntry]) -> ReleaseEntry | None:
    return next(
        (
            entry
            for entry in entries
            if entry.release_channel == STABLE_CHANNEL
        ),
        None,
    )


def choose_latest_beta_entry(entries: list[ReleaseEntry]) -> ReleaseEntry | None:
    return next(
        (entry for entry in entries if entry.release_channel == BETA_CHANNEL),
        None,
    )


def choose_supplementary_entries(
    entries: list[ReleaseEntry], primary_entry: ReleaseEntry
) -> list[ReleaseEntry]:
    candidates = (
        choose_latest_stable_entry(entries),
        choose_latest_beta_entry(entries),
    )
    supplementary: list[ReleaseEntry] = []
    seen_paths = {primary_entry.page_path.lower()}

    for entry in candidates:
        if entry is None or entry.page_path.lower() in seen_paths:
            continue
        supplementary.append(entry)
        seen_paths.add(entry.page_path.lower())

    return supplementary


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
                if entry.version == candidate
                and entry.release_channel == target.release_channel
                and (
                    target.beta_iteration is None
                    or entry.beta_iteration == target.beta_iteration
                )
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
            if target.normalized_text
            and target.normalized_text in normalize_text_key(entry.title)
            and entry.release_channel == target.release_channel
            and (
                target.beta_iteration is None
                or entry.beta_iteration == target.beta_iteration
            )
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

    fallback_entry = choose_same_major_fallback(entries, target)
    if fallback_entry is None and target.version:
        if target.release_channel == BETA_CHANNEL:
            requested_beta = target.raw or target.version
            raise RuntimeError(
                f"No Xcode beta release notes matched requested version: "
                f"{requested_beta}."
            )
        fallback_entry = choose_latest_fallback(entries, target.release_channel)
    elif fallback_entry is None:
        fallback_entry = choose_latest_fallback(entries, target.release_channel)
    fallback_message = "No exact Xcode release notes matched the requested version."
    return MatchResult(
        entry=fallback_entry,
        matched_candidate=None,
        fallback_message=fallback_message,
        attempted_versions=attempted_versions,
    )


def resolve_target(
    info: XcodeInfo, requested_version: str | None
) -> TargetSpec:
    if requested_version:
        return parse_target(requested_version)
    if info.version:
        channel = active_release_channel(info)
        channel_suffix = " beta" if channel == BETA_CHANNEL else ""
        return parse_target(f"{info.version}{channel_suffix}")

    detail = (
        f" {info.resolution_errors[0]}"
        if info.resolution_errors
        else ""
    )
    raise RuntimeError(f"Unable to resolve the active Xcode version.{detail}")


def active_release_channel(info: XcodeInfo) -> str:
    selected_paths = (info.developer_dir, info.app_path)
    if any(
        path
        and re.search(r"(?<![a-z])beta(?![a-z])", path.lower())
        for path in selected_paths
    ):
        return BETA_CHANNEL
    return STABLE_CHANNEL


def clean_release_markdown(markdown: str) -> str:
    markdown = re.sub(r"^<!--.*?-->\s*", "", markdown, flags=re.DOTALL)
    markdown = re.sub(
        r"\n---\n\nCopyright[\s\S]*$",
        "",
        markdown,
        flags=re.IGNORECASE,
    )
    return markdown.strip()


def format_section(title: str, body: str) -> str:
    divider = "=" * len(title)
    return f"{title}\n{divider}\n{body.strip()}"


def build_list_output(info: XcodeInfo, entries: list[ReleaseEntry]) -> str:
    lines: list[str] = []
    if info.version:
        lines.append(f"Active Xcode: {info.version}")
    if info.build_version:
        lines.append(f"Active build version: {info.build_version}")
    if info.developer_dir:
        lines.append(f"Developer dir: {info.developer_dir}")
    if info.app_path:
        lines.append(f"App path: {info.app_path}")
    lines.append(f"Available release notes: {len(entries)}")
    lines.append("")

    for entry in entries:
        lines.append(f"- {entry.title}")
        lines.append(f"  Source: {entry.source_url}")

    return format_section("Xcode", "\n".join(lines))


def build_output(
    info: XcodeInfo,
    requested_version: str | None,
    match_result: MatchResult,
    body: str,
    supplementary_releases: list[tuple[ReleaseEntry, str]] | None = None,
) -> str:
    lines: list[str] = []
    supplementary_releases = supplementary_releases or []

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
        lines.append(
            f"Attempted versions: {', '.join(match_result.attempted_versions)}"
        )

    if info.resolution_errors and not info.version:
        lines.append(f"Resolution note: {info.resolution_errors[0]}")

    lines.extend(
        [
            f"Matched release notes: {match_result.entry.title}",
            f"Source: {match_result.entry.source_url}",
        ]
    )

    for entry, _ in supplementary_releases:
        lines.extend(
            [
                f"Latest {entry.release_channel} release notes: {entry.title}",
                f"Source: {entry.source_url}",
            ]
        )

    if supplementary_releases:
        primary_heading = (
            "Requested Xcode Release Notes"
            if requested_version
            else "Installed Xcode Release Notes"
        )
        lines.extend(
            [
                "",
                f"## {primary_heading}",
                "",
                body,
            ]
        )
        for entry, supplementary_body in supplementary_releases:
            lines.extend(
                [
                    "",
                    f"## Latest {entry.release_channel.title()} Xcode Release Notes",
                    "",
                    supplementary_body,
                ]
            )
    else:
        lines.extend(["", body])

    return format_section("Xcode", "\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Print Apple stable and beta Xcode release notes for the active "
            "or requested version."
        )
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List the available Xcode release-note versions from Apple.",
    )
    parser.add_argument(
        "--version",
        help=(
            "Explicit Xcode version label to match, for example '27 beta', "
            "'27 beta 6', or '16.4'."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.list and args.version:
        raise SystemExit("Use either --list or --version, not both.")

    info = get_active_xcode_info()
    entries = parse_index_entries(fetch_text(INDEX_MARKDOWN_URL))

    if args.list:
        print(build_list_output(info, entries))
        return 0

    try:
        target = resolve_target(info, args.version)
        match_result = match_release_entry(entries, target)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
    release_body = clean_release_markdown(fetch_text(match_result.entry.markdown_url))
    supplementary_releases: list[tuple[ReleaseEntry, str]] = []
    if not args.version:
        for entry in choose_supplementary_entries(entries, match_result.entry):
            supplementary_releases.append(
                (entry, clean_release_markdown(fetch_text(entry.markdown_url)))
            )

    print(
        build_output(
            info,
            args.version,
            match_result,
            release_body,
            supplementary_releases,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
