from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from . import __version__, attachment
from .common import GError, envelope, error_envelope
from .health import doctor, doctor_text


class Parser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("allow_abbrev", False)
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> None:
        raise GError("Invalid command arguments.", code="invalid_arguments", exit_code=64)


def build_parser() -> Parser:
    root = Parser(
        prog="attachment-upload",
        description="Upload one local file and return its stable GitHub attachment URL.",
    )
    root.add_argument("--version", action="version", version=__version__)
    root.add_argument("--json", action="store_true", help="Emit a stable JSON envelope.")
    root.add_argument("--repo", required=True, help="Repository in owner/repo format.")
    root.add_argument("--file", required=True, help="Absolute path to the local file to upload.")
    root.add_argument("--name", help="Optional attachment filename.")
    root.add_argument("--content-type", help="Optional MIME type.")
    root.add_argument("--dry-run", action="store_true", help="Validate inputs without uploading.")
    return root


def main(argv: list[str] | None = None) -> int:
    raw = list(argv if argv is not None else sys.argv[1:])
    if raw == ["--version"]:
        print(__version__)
        return 0
    json_mode = "--json" in raw
    filtered = [item for item in raw if item != "--json"]
    try:
        if filtered == ["doctor"] or filtered == ["--help"] or filtered == ["-h"]:
            if filtered == ["doctor"]:
                payload = doctor()
                print(
                    json.dumps(payload, indent=2)
                    if json_mode
                    else doctor_text(payload, f"attachment-upload {__version__}")
                )
                return 0 if payload["ok"] else 1
            build_parser().print_help()
            return 0
        args = build_parser().parse_args((["--json"] if json_mode else []) + filtered)
        data = attachment.upload(
            repo=args.repo,
            file=args.file,
            name=args.name,
            content_type=args.content_type,
            dry_run=args.dry_run,
        )
        if json_mode:
            print(json.dumps(envelope(["attachment-upload"], data), indent=2))
        else:
            print(json.dumps(data, indent=2))
        return 0
    except GError as exc:
        if json_mode:
            print(json.dumps(error_envelope(["attachment-upload"], exc), indent=2))
        else:
            print(str(exc), file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
