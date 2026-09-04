from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RunResult:
    returncode: int
    stdout: str
    stderr: str


class ReviewError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "command_failed",
        exit_code: int = 1,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.exit_code = exit_code
        self.details = details


class StrictParser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("allow_abbrev", False)
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> None:
        raise ReviewError(
            "Invalid command arguments.", code="invalid_arguments", exit_code=64
        )
