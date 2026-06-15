from __future__ import annotations

from . import runtime


def main(argv: list[str] | None = None) -> int:
    code = runtime.main(argv)
    if argv is None:
        raise SystemExit(code)
    return code

__all__ = ["main"]
