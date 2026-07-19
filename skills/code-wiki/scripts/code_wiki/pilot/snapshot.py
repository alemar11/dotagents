"""Clean, commit-pinned source snapshot creation."""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

from code_wiki.pilot.common import git_output, hash_path, run_checked


FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class SourceSnapshot:
    original_checkout: Path
    original_head_before: str
    commit: str
    original_status_before: str
    snapshot_path: Path
    snapshot_tree_hash: str


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
    return tree_hash


def _reject_unsupported_entries(snapshot_path: Path) -> None:
    records = run_checked(
        ["git", "-C", str(snapshot_path), "ls-files", "--stage", "-z"]
    ).stdout.split("\0")
    symlinks = [
        record.partition("\t")[2]
        for record in records
        if record.startswith("120000 ")
    ]
    if symlinks:
        raise RuntimeError(
            "pilot source snapshots cannot contain tracked symlinks: "
            + ", ".join(sorted(symlinks)[:5])
        )
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
    _reject_unsupported_entries(snapshot_path)
    return SourceSnapshot(
        original_checkout=repo,
        original_head_before=original_head,
        commit=commit,
        original_status_before=status,
        snapshot_path=snapshot_path,
        snapshot_tree_hash=hash_path(snapshot_path, exclude_git_metadata=True),
    )
