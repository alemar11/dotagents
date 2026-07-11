from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from . import __version__
from . import ci, portfolio, reviews, stars
from .common import GitStackError, envelope, error_envelope, resolve_pr, resolve_repo
from .health import doctor
from .publish import open_pr, preflight, template


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise GitStackError(message, code="invalid_arguments", exit_code=64)


def parser() -> Parser:
    root = Parser(prog="gitstack", description="Safe local Git and GitHub workflow mechanics for GitStack skills.")
    root.add_argument("--version", action="version", version=__version__)
    root.add_argument("--json", action="store_true", help="Emit a stable JSON envelope.")
    commands = root.add_subparsers(dest="domain")
    commands.add_parser("doctor", help="Check Python, git, gh, authentication, and checkout readiness.")
    repo = commands.add_parser("repo", help="Resolve repository identity.")
    repo_sub = repo.add_subparsers(dest="verb", required=True)
    repo_resolve = repo_sub.add_parser("resolve", help="Resolve owner/repo from an argument or origin.")
    repo_resolve.add_argument("--repo")
    pr = commands.add_parser("pr", help="Resolve pull request context.")
    pr_sub = pr.add_subparsers(dest="verb", required=True)
    pr_resolve = pr_sub.add_parser("resolve", help="Resolve a PR number/URL or current-branch PR.")
    pr_resolve.add_argument("--repo")
    pr_resolve.add_argument("--pr")
    ci_parser = commands.add_parser("ci", help="Inspect failing GitHub Actions checks.")
    ci_parser.add_argument("args", nargs=argparse.REMAINDER)
    portfolio_parser = commands.add_parser("portfolio", help="Scan multiple repositories read-only.")
    portfolio_parser.add_argument("args", nargs=argparse.REMAINDER)
    reviews_parser = commands.add_parser("reviews", help="Inspect, check, wait for, or respond to PR reviews.")
    reviews_parser.add_argument("args", nargs=argparse.REMAINDER)
    stars_parser = commands.add_parser("stars", help="Manage stars and authenticated-user star lists.")
    stars_parser.add_argument("args", nargs=argparse.REMAINDER)
    publish = commands.add_parser("publish", help="Preflight and open draft pull requests.")
    publish_sub = publish.add_subparsers(dest="verb", required=True)
    publish_preflight = publish_sub.add_parser("preflight")
    publish_preflight.add_argument("--repo")
    publish_template = publish_sub.add_parser("template")
    publish_template.add_argument("--title")
    publish_template.add_argument("--body-file")
    publish_open = publish_sub.add_parser("open")
    publish_open.add_argument("--repo")
    publish_open.add_argument("--title", required=True)
    publish_open.add_argument("--body-file", required=True)
    publish_open.add_argument("--base")
    publish_open.add_argument("--draft", action="store_true", default=True)
    publish_open.add_argument("--dry-run", action="store_true")
    return root


def _forward(module: Any, args: list[str], json_mode: bool, expected: str) -> int:
    forwarded = list(args)
    if forwarded and forwarded[0] == expected:
        forwarded.pop(0)
    if json_mode:
        forwarded.insert(0, "--json")
    return int(module.main(forwarded))


def _emit(data: object, command: list[str], json_mode: bool) -> None:
    if json_mode:
        print(json.dumps(envelope(command, data), indent=2))
    else:
        print(json.dumps(data, indent=2))


def main(argv: list[str] | None = None) -> int:
    raw = list(argv if argv is not None else sys.argv[1:])
    if raw == ["--version"]:
        print(__version__)
        return 0
    json_mode = "--json" in raw
    if json_mode:
        raw.remove("--json")
        raw.insert(0, "--json")
    try:
        args = parser().parse_args(raw)
        if args.domain is None:
            parser().print_help()
            return 0
        if args.domain == "doctor":
            payload = doctor()
            print(json.dumps(payload, indent=2) if args.json else _doctor_text(payload))
            return 0 if payload["ok"] else 1
        if args.domain == "repo":
            _emit(resolve_repo(args.repo), ["repo", "resolve"], args.json)
            return 0
        if args.domain == "pr":
            _emit(resolve_pr(args.repo, args.pr), ["pr", "resolve"], args.json)
            return 0
        if args.domain == "ci":
            return _forward(ci, args.args, args.json, "inspect")
        if args.domain == "portfolio":
            return _forward(portfolio, args.args, args.json, "scan")
        if args.domain == "reviews":
            return _forward(reviews, args.args, args.json, "")
        if args.domain == "stars":
            return _forward(stars, args.args, args.json, "")
        if args.domain == "publish" and args.verb == "preflight":
            data = preflight(args.repo)
        elif args.domain == "publish" and args.verb == "template":
            data = template(args.title, args.body_file)
        elif args.domain == "publish" and args.verb == "open":
            data = open_pr(repo=args.repo, title=args.title, body_file=args.body_file, draft=args.draft, base=args.base, dry_run=args.dry_run)
        else:
            raise GitStackError("Unsupported command.", code="invalid_arguments", exit_code=64)
        _emit(data, ["publish", args.verb], args.json)
        return 0
    except GitStackError as exc:
        command = [item for item in raw if not item.startswith("-")][:2]
        if json_mode:
            print(json.dumps(error_envelope(command, exc), indent=2))
        else:
            print(str(exc), file=sys.stderr)
        return exc.exit_code


def _doctor_text(payload: dict[str, object]) -> str:
    checks = payload["checks"]
    assert isinstance(checks, dict)
    return "\n".join([
        f"gitstack {__version__}",
        f"git: {'ok' if checks['git']['ok'] else 'missing'}",
        f"gh: {'ok' if checks['gh']['ok'] else 'missing'}",
        f"repository: {'ok' if checks['repository']['inside_worktree'] else 'not detected'}",
        "connector: model-runtime-only",
    ])


if __name__ == "__main__":
    raise SystemExit(main())
