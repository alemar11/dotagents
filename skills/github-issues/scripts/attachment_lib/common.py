from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import __version__

REPO_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")


@dataclass(frozen=True)
class Result:
    returncode: int
    stdout: str
    stderr: str


class GError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        code: str = "command_failed",
        exit_code: int = 1,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code
        self.details = details


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
    except FileNotFoundError as exc:
        raise GError(
            f"Command '{command[0]}' is not installed or not on PATH.",
            code="process_spawn_failed",
            exit_code=127,
            details={"upstream_command": list(command), "reason": "not-found"},
        ) from exc
    except OSError as exc:
        details: dict[str, Any] = {
            "upstream_command": list(command),
            "reason": type(exc).__name__,
        }
        if exc.errno is not None:
            details["errno"] = exc.errno
        raise GError(
            f"Could not execute command '{command[0]}'.",
            code="process_spawn_failed",
            exit_code=126,
            details=details,
        ) from exc
    return Result(proc.returncode, proc.stdout, proc.stderr)


def envelope(command: list[str], data: Any) -> dict[str, Any]:
    return {"ok": True, "version": __version__, "command": command, "data": data}


def error_envelope(command: list[str], exc: GError) -> dict[str, Any]:
    error: dict[str, Any] = {"code": exc.code, "message": str(exc)}
    if exc.details is not None:
        error["details"] = exc.details
    return {"ok": False, "version": __version__, "command": command, "error": error}
