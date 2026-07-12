#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_REPO = "GoogleCloudPlatform/knowledge-catalog"
DEFAULT_REF = "main"
SOURCE_SUBPATH = Path("okf/SPEC.md")
OFFICIAL_TREE_URL = "https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf"
USER_AGENT = "dotagents-okf-spec-refresh"

REPO_ROOT = Path(__file__).resolve().parents[4]
SKILL_DIR = REPO_ROOT / "skills" / "okf"
ASSETS_DIR = SKILL_DIR / "assets"
SPEC_PATH = ASSETS_DIR / "spec.md"
MANIFEST_PATH = ASSETS_DIR / "manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh the bundled OKF spec asset.")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--ref", default=DEFAULT_REF)
    parser.add_argument(
        "--check-stale",
        action="store_true",
        help="Report whether the bundled OKF spec is stale without changing files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force a refresh even if the local manifest matches upstream.",
    )
    return parser.parse_args()


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def download_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8")


def resolve_commit(repo: str, ref: str) -> str:
    payload = fetch_json(
        f"https://api.github.com/repos/{repo}/commits/{urllib.parse.quote(ref, safe='')}"
    )
    return payload["sha"]


def raw_source_url(repo: str, ref: str) -> str:
    owner, name = repo.split("/", 1)
    return (
        "https://raw.githubusercontent.com/"
        f"{owner}/{name}/{urllib.parse.quote(ref, safe='')}/{SOURCE_SUBPATH.as_posix()}"
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def detect_spec_version(text: str) -> str:
    match = re.search(r"\*\*Version\s+([^*]+?)\*\*", text)
    return match.group(1).strip() if match else "UNKNOWN"


def load_manifest() -> dict | None:
    if not MANIFEST_PATH.exists():
        return None
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def stale_reasons(manifest: dict | None, repo: str, ref: str, commit: str, text: str) -> list[str]:
    reasons: list[str] = []
    if not SPEC_PATH.exists():
        reasons.append("Bundled OKF spec file is missing.")
    else:
        local_hash = sha256_text(SPEC_PATH.read_text(encoding="utf-8"))
        expected_hash = sha256_text(text)
        if local_hash != expected_hash:
            reasons.append(
                f"Bundled OKF spec hash mismatch: expected {expected_hash!r}, got {local_hash!r}"
            )
    if manifest is None:
        reasons.append("Manifest is missing.")
        return reasons

    expected = {
        "repo": repo,
        "ref": ref,
        "source_subpath": SOURCE_SUBPATH.as_posix(),
        "content_sha256": sha256_text(text),
        "spec_version": detect_spec_version(text),
        "official_tree_url": OFFICIAL_TREE_URL,
    }
    for key, expected_value in expected.items():
        if manifest.get(key) != expected_value:
            reasons.append(
                f"Manifest {key} mismatch: expected {expected_value!r}, got {manifest.get(key)!r}"
            )
    return reasons


def write_bundle(repo: str, ref: str, commit: str, text: str) -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    SPEC_PATH.write_text(text, encoding="utf-8")
    manifest = {
        "repo": repo,
        "ref": ref,
        "resolved_commit": commit,
        "source_subpath": SOURCE_SUBPATH.as_posix(),
        "content_sha256": sha256_text(text),
        "spec_version": detect_spec_version(text),
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "official_tree_url": OFFICIAL_TREE_URL,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    commit = resolve_commit(args.repo, args.ref)
    text = download_text(raw_source_url(args.repo, commit))
    manifest = load_manifest()
    reasons = stale_reasons(manifest, args.repo, args.ref, commit, text)

    if args.check_stale:
        status = "STALE" if reasons else "FRESH"
        print(f"OKF bundled spec status: {status}")
        print(f"- Skill dir: {SKILL_DIR}")
        print(f"- Upstream: {args.repo}@{args.ref} ({commit})")
        print(f"- Source: {SOURCE_SUBPATH.as_posix()}")
        print(f"- Spec version: {detect_spec_version(text)}")
        if manifest and manifest.get("resolved_commit"):
            print(f"- Local manifest commit: {manifest['resolved_commit']}")
        for reason in reasons:
            print(f"- {reason}")
        return 0

    if args.force or reasons:
        write_bundle(args.repo, args.ref, commit, text)
        print("Bundled OKF spec refreshed.")
        print(f"- Spec file: {SPEC_PATH}")
        print(f"- Manifest: {MANIFEST_PATH}")
        print(f"- Upstream: {args.repo}@{args.ref} ({commit})")
        print(f"- Spec version: {detect_spec_version(text)}")
        return 0

    print("Bundled OKF spec already up to date.")
    print(f"- Manifest: {MANIFEST_PATH}")
    print(f"- Upstream: {args.repo}@{args.ref} ({commit})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
