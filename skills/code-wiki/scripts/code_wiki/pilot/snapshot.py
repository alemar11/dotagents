"""Clean, commit-pinned source snapshot creation."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

from code_wiki.pilot.common import git_output, hash_path, run_checked


FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
EMPTY_SYMLINK_IDENTITY_SHA256 = hashlib.sha256(b"[]").hexdigest()


@dataclass(frozen=True)
class SourceSnapshot:
    original_checkout: Path
    original_head_before: str
    commit: str
    original_status_before: str
    snapshot_path: Path
    snapshot_tree_hash: str
    source_symlinks: tuple[dict[str, str], ...] = ()
    source_symlink_identity_sha256: str = EMPTY_SYMLINK_IDENTITY_SHA256


def default_cache_root() -> Path:
    return Path("~/.cache/dotagents/skills/code-wiki/pilot").expanduser()


def source_status(repo: Path) -> str:
    return git_output(repo, "status", "--porcelain=v1", "--untracked-files=all")


def assert_snapshot_clean(snapshot: SourceSnapshot) -> str:
    status = source_status(snapshot.snapshot_path)
    if status:
        raise RuntimeError(f"source snapshot was mutated: {status.splitlines()[0]}")
    tree_hash = hash_path(snapshot.snapshot_path, exclude_git_metadata=True)
    if tree_hash != snapshot.snapshot_tree_hash:
        raise RuntimeError("source snapshot bytes changed without a clean Git-status signal")
    symlinks = _tracked_symlink_identity(snapshot.snapshot_path)
    if symlinks != snapshot.source_symlinks:
        raise RuntimeError("source snapshot tracked-symlink identity changed")
    if _symlink_identity_sha256(symlinks) != snapshot.source_symlink_identity_sha256:
        raise RuntimeError("source snapshot tracked-symlink provenance changed")
    return tree_hash


def _tracked_index_records(snapshot_path: Path) -> list[str]:
    return run_checked(
        ["git", "-C", str(snapshot_path), "ls-files", "--stage", "-z"]
    ).stdout.split("\0")


def _resolve_tracked_symlink(snapshot_path: Path, relative: str) -> dict[str, str]:
    root = snapshot_path.resolve()
    link = snapshot_path / relative
    try:
        raw_target = os.readlink(link)
    except OSError as exc:
        raise RuntimeError(f"tracked symlink cannot be read: {relative}: {exc}") from exc
    if Path(raw_target).is_absolute():
        raise RuntimeError(f"tracked symlink target must be relative: {relative} -> {raw_target}")
    lexical_target = Path(os.path.normpath(str(link.parent / raw_target)))
    try:
        lexical_target.relative_to(root)
    except ValueError as exc:
        raise RuntimeError(f"tracked symlink escapes source snapshot: {relative} -> {raw_target}") from exc
    try:
        resolved = link.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise RuntimeError(
            f"tracked symlink target must exist and be acyclic: {relative} -> {raw_target}"
        ) from exc
    try:
        resolved_relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise RuntimeError(f"tracked symlink escapes source snapshot: {relative} -> {raw_target}") from exc
    if not resolved.is_file() and not resolved.is_dir():
        raise RuntimeError(f"tracked symlink target is not a file or directory: {relative}")
    return {
        "link_path": Path(relative).as_posix(),
        "raw_target": raw_target,
        "resolved_target": resolved_relative,
        "resolved_content_sha256": hash_path(resolved),
    }


def _tracked_symlink_identity(snapshot_path: Path) -> tuple[dict[str, str], ...]:
    symlinks = sorted(
        record.partition("\t")[2]
        for record in _tracked_index_records(snapshot_path)
        if record.startswith("120000 ")
    )
    return tuple(_resolve_tracked_symlink(snapshot_path, relative) for relative in symlinks)


def _symlink_identity_sha256(records: tuple[dict[str, str], ...]) -> str:
    encoded = json.dumps(records, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _reject_unsupported_entries(snapshot_path: Path) -> tuple[dict[str, str], ...]:
    records = _tracked_index_records(snapshot_path)
    gitlinks = [
        record.partition("\t")[2]
        for record in records
        if record.startswith("160000 ")
    ]
    if gitlinks:
        raise RuntimeError(
            "pilot source snapshots cannot contain unmaterialized gitlinks/submodules: "
            + ", ".join(sorted(gitlinks)[:5])
        )
    return _tracked_symlink_identity(snapshot_path)


def create_snapshot(repo_arg: str, commit_arg: str, cache_root_arg: str | None = None) -> SourceSnapshot:
    repo = Path(repo_arg).expanduser().resolve()
    if not repo.is_dir():
        raise RuntimeError(f"source repository is not a directory: {repo}")
    if git_output(repo, "rev-parse", "--is-inside-work-tree") != "true":
        raise RuntimeError(f"source is not a Git worktree: {repo}")
    status = source_status(repo)
    if status:
        raise RuntimeError("pilot source checkout must be clean, including untracked files")
    original_head = git_output(repo, "rev-parse", "HEAD")
    commit = git_output(repo, "rev-parse", "--verify", f"{commit_arg}^{{commit}}")
    if not FULL_SHA_RE.fullmatch(commit):
        raise RuntimeError(f"source commit did not resolve to a full SHA: {commit_arg}")

    cache_root = Path(cache_root_arg).expanduser().resolve() if cache_root_arg else default_cache_root()
    cache_root.mkdir(parents=True, exist_ok=True)
    run_root = Path(tempfile.mkdtemp(prefix=f"{repo.name}-{commit[:12]}-", dir=cache_root))
    snapshot_path = run_root / "source"
    run_checked(["git", "clone", "--no-local", "--no-checkout", "--", str(repo), str(snapshot_path)])
    run_checked(["git", "-C", str(snapshot_path), "checkout", "--detach", commit])
    resolved = git_output(snapshot_path, "rev-parse", "HEAD")
    if resolved != commit:
        raise RuntimeError(f"snapshot resolved unexpected commit: {resolved}")
    if source_status(snapshot_path):
        raise RuntimeError("new source snapshot is not clean")
    source_symlinks = _reject_unsupported_entries(snapshot_path)
    return SourceSnapshot(
        original_checkout=repo,
        original_head_before=original_head,
        commit=commit,
        original_status_before=status,
        snapshot_path=snapshot_path,
        snapshot_tree_hash=hash_path(snapshot_path, exclude_git_metadata=True),
        source_symlinks=source_symlinks,
        source_symlink_identity_sha256=_symlink_identity_sha256(source_symlinks),
    )
