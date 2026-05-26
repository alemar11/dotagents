"""Command-line entrypoint for the code-wiki helper."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from code_wiki.claim_matrix import synthesize_claim_matrix
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


def cmd_synthesize(args: argparse.Namespace) -> int:
    synthesize_claim_matrix(args.repo, args.inventory, args.out)
    print(f"wrote claim matrix to {Path(args.out).expanduser()}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    return validate(args.wiki, strict=args.strict)


def refs_from_batch_input(input_arg: str) -> list[str]:
    input_path = Path(input_arg).expanduser()
    text = sys.stdin.read() if str(input_arg) == "-" else input_path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return []
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        return [
            line.strip()
            for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]

    refs: list[str] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                refs.append(item)
            elif isinstance(item, dict):
                value = item.get("evidence") or item.get("ref")
                if isinstance(value, str):
                    refs.append(value)
    elif isinstance(data, dict):
        values = data.get("evidence") or data.get("refs")
        if isinstance(values, list):
            refs.extend(str(value) for value in values if isinstance(value, str))
    return refs


def render_evidence(args: argparse.Namespace, evidence: str) -> tuple[str | None, str]:
    if args.html:
        return render_evidence_chip(args.repo, evidence)
    return source_url_for_evidence(args.repo, evidence)


def cmd_evidence_link(args: argparse.Namespace) -> int:
    if args.batch:
        if not args.input:
            print("NO_LINK: --batch requires --in <refs.txt|json|->")
            return 2
        try:
            refs = refs_from_batch_input(args.input)
        except OSError as exc:
            print(f"NO_LINK: cannot read batch input {args.input}: {exc}")
            return 2
        failed = False
        for evidence in refs:
            rendered, reason = render_evidence(args, evidence)
            if rendered:
                print(rendered)
            else:
                failed = True
                print(f"NO_LINK: {evidence}: {reason}")
        return 2 if failed else 0

    if not args.evidence:
        print("NO_LINK: --evidence is required unless --batch is used")
        return 2
    rendered, reason = render_evidence(args, args.evidence)
    if rendered:
        print(rendered)
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

    synthesize_parser = subparsers.add_parser(
        "synthesize",
        help="write a deterministic claim-matrix scaffold from inventory JSON",
    )
    synthesize_parser.add_argument("--repo", required=True, help="local repository path")
    synthesize_parser.add_argument("--inventory", required=True, help="input inventory JSON path")
    synthesize_parser.add_argument("--out", required=True, help="output claim-matrix JSON path")
    synthesize_parser.set_defaults(func=cmd_synthesize)

    validate_parser = subparsers.add_parser("validate", help="validate a generated wiki")
    validate_parser.add_argument("--wiki", required=True, help="wiki directory")
    validate_parser.add_argument(
        "--strict",
        action="store_true",
        help="require a ready claim matrix and fail on broad/repeated evidence or boilerplate",
    )
    validate_parser.set_defaults(func=cmd_validate)

    evidence_parser = subparsers.add_parser(
        "evidence-link",
        help="render commit-pinned online source URLs or evidence chips",
    )
    evidence_parser.add_argument("--repo", required=True, help="local repository path")
    evidence_parser.add_argument(
        "--evidence",
        required=False,
        help="evidence reference formatted as path:line or path:start-end",
    )
    evidence_parser.add_argument(
        "--batch",
        action="store_true",
        help="read evidence references from --in as newline text or JSON",
    )
    evidence_parser.add_argument(
        "--in",
        dest="input",
        help="batch input path, or - for stdin",
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
