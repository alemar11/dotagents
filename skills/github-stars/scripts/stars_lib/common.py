from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


@dataclass(frozen=True)
class Result:
    returncode: int
    stdout: str
    stderr: str


def run(
    command: Sequence[str],
    cwd: Path | None = None,
    *,
    env: Mapping[str, str] | None = None,
    stdin: int | None = None,
) -> Result:
    try:
        proc = subprocess.run(
            list(command),
            cwd=cwd,
            text=True,
            capture_output=True,
            env=dict(env) if env is not None else None,
            stdin=stdin,
        )
    except FileNotFoundError:
        return Result(127, "", f"Command '{command[0]}' is not installed or not on PATH.")
    except OSError as exc:
        return Result(126, "", f"Could not execute command '{command[0]}': {type(exc).__name__}")
    return Result(proc.returncode, proc.stdout, proc.stderr)
