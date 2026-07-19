"""Shared deterministic helpers for the Code Wiki pilot."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_path(path: Path, *, exclude_git_metadata: bool = False) -> str:
    """Hash one file or directory, including relative names and empty directories."""
    if path.is_file():
        return sha256_file(path)
    if not path.is_dir():
        raise FileNotFoundError(path)
    digest = hashlib.sha256()
    for root, dirnames, filenames in os.walk(path):
        dirnames[:] = sorted(
            name
            for name in dirnames
            if not (exclude_git_metadata and name == ".git")
        )
        root_path = Path(root)
        rel_root = root_path.relative_to(path)
        digest.update(f"D\0{rel_root.as_posix()}\0".encode("utf-8"))
        for dirname in dirnames:
            directory_path = root_path / dirname
            if directory_path.is_symlink():
                target = os.readlink(directory_path)
                digest.update(
                    f"L\0{directory_path.relative_to(path).as_posix()}\0{target}\0".encode(
                        "utf-8"
                    )
                )
        for filename in sorted(filenames):
            file_path = root_path / filename
            if file_path.is_symlink():
                target = os.readlink(file_path)
                digest.update(f"L\0{file_path.relative_to(path).as_posix()}\0{target}\0".encode("utf-8"))
                continue
            digest.update(f"F\0{file_path.relative_to(path).as_posix()}\0".encode("utf-8"))
            with file_path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
    return digest.hexdigest()


def write_text_atomic(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_value = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=path.parent,
    )
    temporary = Path(temporary_value)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(value)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_json(path: Path, value: dict[str, Any]) -> None:
    write_text_atomic(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def run_checked(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            check=True,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise RuntimeError(f"cannot run {command[0]}: {exc}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise RuntimeError(f"command failed ({' '.join(command)}): {detail}") from exc


def git_output(repo: Path, *args: str) -> str:
    return run_checked(["git", "-C", str(repo), *args]).stdout.strip()
