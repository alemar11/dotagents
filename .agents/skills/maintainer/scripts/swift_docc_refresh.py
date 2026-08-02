#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import tarfile
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_REPO = "swiftlang/swift-docc"
DEFAULT_REF = "main"
SOURCE_SUBPATH = Path("Sources/docc/DocCDocumentation.docc")
OFFICIAL_BASE_URL = "https://www.swift.org/documentation/docc"
USER_AGENT = "maintainer-swift-docc-refresh"

REPO_ROOT = Path(__file__).resolve().parents[4]
SKILL_DIR = REPO_ROOT / "skills" / "swift-docc"
ASSETS_DIR = SKILL_DIR / "assets"
ASSET_DOCC_DIR = ASSETS_DIR / "DocCDocumentation.docc"
ASSET_MANIFEST_PATH = ASSETS_DIR / "manifest.json"
REFERENCES_DIR = SKILL_DIR / "references"
CATALOG_PATH = REFERENCES_DIR / "catalog.json"
SOURCE_MAP_PATH = REFERENCES_DIR / "source-map.md"
LEGACY_OFFICIAL_DIR = REFERENCES_DIR / "official"
LEGACY_UPSTREAM_DIR = REFERENCES_DIR / "upstream"
LEGACY_MANIFEST_PATH = REFERENCES_DIR / "source-manifest.json"
SYMBOLS_PATH = ASSET_DOCC_DIR / "docc.symbols.json"
MEDIA_SOURCE_DIRECTIVES = {
    "__docc_universal_symbol_reference_$Image",
    "__docc_universal_symbol_reference_$Video",
}
SOURCE_PARAMETER_LINES = [
    {"text": "  - source: A reference to the source file for the media item."},
    {"text": "     **(required)**"},
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh the bundled Swift-DocC asset tree from Maintainer."
    )
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--ref", default=DEFAULT_REF)
    parser.add_argument(
        "--check-stale",
        action="store_true",
        help="Report whether the bundled DocC tree is stale without changing files.",
    )
    parser.add_argument(
        "--fail-if-stale",
        action="store_true",
        help="With --check-stale, return non-zero when the asset tree is stale.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force a bundled-asset refresh even if the manifest matches upstream.",
    )
    return parser.parse_args()


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def load_manifest() -> dict | None:
    if not ASSET_MANIFEST_PATH.exists():
        return None
    return json.loads(ASSET_MANIFEST_PATH.read_text(encoding="utf-8"))


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def download_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def resolve_commit(repo: str, ref: str) -> str:
    payload = fetch_json(
        f"https://api.github.com/repos/{repo}/commits/{urllib.parse.quote(ref, safe='')}"
    )
    return payload["sha"]


def safe_extract(archive: tarfile.TarFile, destination: Path) -> None:
    destination = destination.resolve()
    for member in archive.getmembers():
        member_path = (destination / member.name).resolve()
        if member_path != destination and destination not in member_path.parents:
            raise ValueError(f"Unsafe archive member path: {member.name!r}")
        if member.issym() or member.islnk():
            raise ValueError(f"Archive links are not allowed: {member.name!r}")
        if not (member.isdir() or member.isfile()):
            raise ValueError(f"Unsupported archive member type: {member.name!r}")
    archive.extractall(destination)


def download_archive(repo: str, revision: str, destination: Path) -> Path:
    archive_bytes = download_bytes(
        f"https://api.github.com/repos/{repo}/tarball/{urllib.parse.quote(revision, safe='')}"
    )
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        safe_extract(archive, destination)
    extracted = [child for child in destination.iterdir() if child.is_dir()]
    if len(extracted) != 1:
        raise RuntimeError(f"Expected exactly one extracted root, found {len(extracted)}")
    return extracted[0]


def asset_link(asset_path: str) -> str:
    return f"../{urllib.parse.quote(asset_path, safe='/')}"


def render_source_map(catalog: dict) -> str:
    topics = {topic["id"]: topic for topic in catalog["topics"]}
    lines = [
        "# Source Map",
        "",
        "Task-language routing for the `swift-docc` skill.",
        "",
        "| Question | Summary | Local source |",
        "| --- | --- | --- |",
    ]
    for intent in catalog["intents"]:
        primary = topics[intent["primary_topic_id"]]
        summary = f"[Summary]({intent['summary_page']})"
        local = f"[Local source]({asset_link(primary['asset_path'])})"
        lines.append(f"| {intent['question']} | {summary} | {local} |")
    lines.append("")
    return "\n".join(lines)


def asset_stale_reasons(manifest: dict | None, repo: str, ref: str, latest_commit: str) -> list[str]:
    reasons: list[str] = []
    if not ASSET_DOCC_DIR.exists():
        reasons.append("Bundled DocCDocumentation.docc tree is missing.")
    if manifest is None:
        reasons.append("Manifest is missing.")
        return reasons

    expected = {
        "repo": repo,
        "ref": ref,
        "resolved_commit": latest_commit,
        "source_subpath": SOURCE_SUBPATH.as_posix(),
        "official_base_url": OFFICIAL_BASE_URL,
    }
    for key, expected_value in expected.items():
        if manifest.get(key) != expected_value:
            reasons.append(
                f"Manifest {key} mismatch: expected {expected_value!r}, got {manifest.get(key)!r}"
            )
    return reasons


def stale_exit_code(reasons: list[str], fail_if_stale: bool) -> int:
    return 1 if fail_if_stale and reasons else 0


def path_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def remove_path(path: Path) -> None:
    if not path_exists(path):
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def reserve_backup_path(path: Path) -> Path:
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.backup-",
        dir=path.parent,
    )
    os.close(file_descriptor)
    temporary_path = Path(temporary_name)
    temporary_path.unlink()
    return temporary_path


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=path.parent,
        text=True,
    )
    temporary_path = Path(temporary_name)
    try:
        os.chmod(temporary_path, mode)
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def write_text_if_changed(path: Path, text: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    atomic_write_text(path, text)
    return True


def commit_staged_outputs(outputs: list[tuple[Path, Path]]) -> None:
    backups: list[tuple[Path, Path | None]] = []
    installed: list[Path] = []
    try:
        for _, target in outputs:
            target.parent.mkdir(parents=True, exist_ok=True)
            backup = None
            if path_exists(target):
                backup = reserve_backup_path(target)
                os.replace(target, backup)
            backups.append((target, backup))

        for staged, target in outputs:
            os.replace(staged, target)
            installed.append(target)
    except Exception:
        for target in reversed(installed):
            remove_path(target)
        for target, backup in reversed(backups):
            if backup is not None and path_exists(backup):
                os.replace(backup, target)
        raise

    for _, backup in backups:
        if backup is not None:
            remove_path(backup)


def cleanup_legacy_outputs() -> None:
    for path in [LEGACY_OFFICIAL_DIR, LEGACY_UPSTREAM_DIR, LEGACY_MANIFEST_PATH]:
        remove_path(path)


def refresh_assets(
    catalog: dict,
    repo: str,
    revision: str,
    staging_root: Path,
) -> tuple[Path, int]:
    staged_asset_dir = staging_root / ASSET_DOCC_DIR.name
    with tempfile.TemporaryDirectory() as temp_dir:
        extracted_root = download_archive(repo, revision, Path(temp_dir))
        upstream_root = extracted_root / SOURCE_SUBPATH
        if not upstream_root.exists():
            raise FileNotFoundError(f"Missing upstream DocCDocumentation.docc at {upstream_root}")
        shutil.copytree(upstream_root, staged_asset_dir)
        ensure_media_source_parameter_docs(staged_asset_dir / SYMBOLS_PATH.name)

    for topic in catalog["topics"]:
        relative_asset_path = Path(topic["asset_path"]).relative_to(
            "assets/DocCDocumentation.docc"
        )
        asset_path = staged_asset_dir / relative_asset_path
        if not asset_path.exists():
            raise FileNotFoundError(
                f"Missing bundled asset for topic {topic['id']}: {asset_path}"
            )

    return staged_asset_dir, sum(1 for path in staged_asset_dir.rglob("*") if path.is_file())


def ensure_media_source_parameter_docs(symbols_path: Path) -> bool:
    if not symbols_path.exists():
        return False
    data = json.loads(symbols_path.read_text(encoding="utf-8"))
    changed = False
    for symbol in data.get("symbols", []):
        precise = symbol.get("identifier", {}).get("precise")
        if precise not in MEDIA_SOURCE_DIRECTIVES:
            continue
        lines = symbol.get("docComment", {}).get("lines", [])
        if any(line.get("text", "").startswith("  - source:") for line in lines):
            continue
        for index, line in enumerate(lines):
            if line.get("text") == "- Parameters:":
                lines[index + 1:index + 1] = SOURCE_PARAMETER_LINES
                changed = True
                break
    if changed:
        atomic_write_text(symbols_path, json.dumps(data, indent=2) + "\n")
    return changed


def render_manifest(repo: str, ref: str, commit: str) -> str:
    return json.dumps(
        {
            "repo": repo,
            "ref": ref,
            "resolved_commit": commit,
            "source_subpath": SOURCE_SUBPATH.as_posix(),
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
            "official_base_url": OFFICIAL_BASE_URL,
        },
        indent=2,
    ) + "\n"


def write_manifest(repo: str, ref: str, commit: str) -> None:
    atomic_write_text(ASSET_MANIFEST_PATH, render_manifest(repo, ref, commit))


def main() -> int:
    args = parse_args()
    catalog = load_catalog()
    latest_commit = resolve_commit(args.repo, args.ref)
    manifest = load_manifest()
    reasons = asset_stale_reasons(manifest, args.repo, args.ref, latest_commit)

    if args.check_stale:
        status = "STALE" if reasons else "FRESH"
        print(f"swift-docc bundled assets status: {status}")
        print(f"- Skill dir: {SKILL_DIR}")
        print(f"- Upstream: {args.repo}@{args.ref} ({latest_commit})")
        if manifest and manifest.get("resolved_commit"):
            print(f"- Local manifest commit: {manifest['resolved_commit']}")
        if reasons:
            for reason in reasons:
                print(f"- {reason}")
        return stale_exit_code(reasons, args.fail_if_stale)

    source_map_text = render_source_map(catalog)
    if args.force or reasons:
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix=".swift-docc-refresh-",
            dir=REPO_ROOT,
        ) as temporary_dir:
            staging_root = Path(temporary_dir)
            staged_asset_dir, asset_file_count = refresh_assets(
                catalog,
                args.repo,
                latest_commit,
                staging_root,
            )
            staged_source_map = staging_root / SOURCE_MAP_PATH.name
            staged_source_map.write_text(source_map_text, encoding="utf-8")
            staged_manifest = staging_root / ASSET_MANIFEST_PATH.name
            staged_manifest.write_text(
                render_manifest(args.repo, args.ref, latest_commit),
                encoding="utf-8",
            )
            commit_staged_outputs(
                [
                    (staged_asset_dir, ASSET_DOCC_DIR),
                    (staged_source_map, SOURCE_MAP_PATH),
                    (staged_manifest, ASSET_MANIFEST_PATH),
                ]
            )
        cleanup_legacy_outputs()
        print("Bundled Swift-DocC assets refreshed.")
        print(f"- Asset root: {ASSET_DOCC_DIR}")
        print(f"- Asset files: {asset_file_count}")
        print(f"- Source map: {SOURCE_MAP_PATH}")
        print(f"- Manifest: {ASSET_MANIFEST_PATH}")
        print(f"- Upstream: {args.repo}@{args.ref} ({latest_commit})")
        return 0

    source_map_changed = write_text_if_changed(SOURCE_MAP_PATH, source_map_text)
    print("Bundled Swift-DocC assets already up to date.")
    print(f"- Manifest: {ASSET_MANIFEST_PATH}")
    print(f"- Upstream: {args.repo}@{args.ref} ({latest_commit})")
    if source_map_changed:
        print(f"- Source map updated: {SOURCE_MAP_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
