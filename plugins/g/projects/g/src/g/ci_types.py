from __future__ import annotations

from dataclasses import dataclass


class InspectionError(Exception):
    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code


@dataclass(frozen=True)
class GhResult:
    returncode: int
    stdout: str
    stderr: str
