"""Command-line entrypoint for the code-wiki helper."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from code_wiki.evidence import render_evidence_chip, source_url_for_evidence
from code_wiki.inventory import build_inventory, write_json
from code_wiki.scaffold import scaffold
from code_wiki.validation import validate
from code_wiki.version import VERSION


def cmd_inventory(args: argparse.Namespace) -> int:
    inventory = build_inventory(args.repo)
    write_json(args.out, inventory)
    print(f"wrote inventory to {Path(args.out).expanduser()}")
    return 0


def cmd_scaffold(args: argparse.Namespace) -> int:
    scaffold(args.out, args.title, args.local_source_cache)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    return validate(args.wiki)


def cmd_evidence_link(args: argparse.Namespace) -> int:
    if args.html:
        rendered, reason = render_evidence_chip(args.repo, args.evidence)
        if rendered:
            print(rendered)
            return 0
    else:
        url, reason = source_url_for_evidence(args.repo, args.evidence)
        if url:
            print(url)
            return 0
    print(f"NO_LINK: {reason}")
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="code-wiki")
    parser.add_argument("--version", action="version", version=f"code-wiki {VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory_parser = subparsers.add_parser("inventory", help="scan a repo and write inventory JSON")
    inventory_parser.add_argument("--repo", required=True, help="local repository path")
    inventory_parser.add_argument("--out", required=True, help="output JSON path")
    inventory_parser.set_defaults(func=cmd_inventory)

    scaffold_parser = subparsers.add_parser("scaffold", help="create a static HTML wiki shell")
    scaffold_parser.add_argument("--out", required=True, help="output wiki directory")
    scaffold_parser.add_argument("--title", required=True, help="wiki title")
    scaffold_parser.add_argument(
        "--local-source-cache",
        action="store_true",
        help="create <wiki-out>/.cache/sources/ with an ignore-all .gitignore",
    )
    scaffold_parser.set_defaults(func=cmd_scaffold)

    validate_parser = subparsers.add_parser("validate", help="validate a generated wiki")
    validate_parser.add_argument("--wiki", required=True, help="wiki directory")
    validate_parser.set_defaults(func=cmd_validate)

    evidence_parser = subparsers.add_parser(
        "evidence-link",
        help="render a commit-pinned online source URL for one evidence reference",
    )
    evidence_parser.add_argument("--repo", required=True, help="local repository path")
    evidence_parser.add_argument(
        "--evidence",
        required=True,
        help="evidence reference formatted as path:line or path:start-end",
    )
    evidence_parser.add_argument(
        "--html",
        action="store_true",
        help="print an HTML evidence chip instead of only the URL",
    )
    evidence_parser.set_defaults(func=cmd_evidence_link)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
