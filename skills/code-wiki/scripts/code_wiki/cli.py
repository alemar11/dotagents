"""Command-line entrypoint for the code-wiki helper."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from code_wiki.claim_matrix import synthesize_claim_matrix
from code_wiki.evidence import render_evidence_chip, source_url_for_evidence
from code_wiki.inventory import build_inventory, write_json
from code_wiki.pilot.comparison import aggregate_comparisons, compare_runs
from code_wiki.pilot.doctor import doctor
from code_wiki.pilot.runner import REASONING_EFFORTS, run_pilot, skill_root
from code_wiki.scaffold import scaffold
from code_wiki.validation import validate
from code_wiki.version import VERSION


class JsonArgumentError(RuntimeError):
    """Raised after a JSON argument error has been emitted."""


class JsonAwareArgumentParser(argparse.ArgumentParser):
    json_errors = False

    def error(self, message: str) -> None:
        if self.json_errors:
            print(json.dumps({"ok": False, "error": f"argument error: {message}"}, sort_keys=True))
            raise JsonArgumentError(message)
        super().error(message)


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


def cmd_doctor(args: argparse.Namespace) -> int:
    result = doctor(skill_root())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            f"code-wiki {result['cli_version']} live pilot readiness: "
            f"{'ready' if result['live_pilot_ready'] else 'setup-required'}"
        )
        for name, check in result["checks"].items():
            print(f"- {name}: {'ready' if check['ok'] else 'not-ready'}")
    return 0 if result["ok"] else 1


def cmd_pilot_run(args: argparse.Namespace) -> int:
    exit_code, manifest = run_pilot(
        mode=args.mode,
        repo=args.repo,
        commit=args.commit,
        out=args.out,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        title=args.title,
        executor_fixture=args.executor_fixture,
        cache_root=args.cache_root,
    )
    result = {
        "run_manifest": manifest["output"]["manifest_path"],
        "terminal_status": manifest["terminal_status"],
        "validation_status": manifest["validation_status"],
        "reader_status": (
            manifest["reader_evaluation"].get("reader_status")
            if isinstance(manifest.get("reader_evaluation"), dict)
            else None
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else f"wrote pilot run manifest to {result['run_manifest']}")
    return exit_code


def cmd_pilot_compare(args: argparse.Namespace) -> int:
    exit_code, decision = compare_runs(args.baseline_run, args.candidate_run, args.out)
    result = {
        "promotion_status": decision["promotion_status"],
        "comparison_json": str(Path(args.out).expanduser().resolve() / "comparison.json"),
        "comparison_markdown": str(Path(args.out).expanduser().resolve() / "comparison.md"),
    }
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else f"promotion_status={result['promotion_status']}\nwrote comparison to {result['comparison_json']}")
    return exit_code


def cmd_pilot_aggregate(args: argparse.Namespace) -> int:
    exit_code, aggregate = aggregate_comparisons(args.comparison, args.out)
    result = {
        "aggregate_status": aggregate["aggregate_status"],
        "aggregate_json": str(Path(args.out).expanduser().resolve() / "aggregate.json"),
        "aggregate_markdown": str(Path(args.out).expanduser().resolve() / "aggregate.md"),
    }
    print(
        json.dumps(result, indent=2, sort_keys=True)
        if args.json
        else f"aggregate_status={result['aggregate_status']}\nwrote aggregate to {result['aggregate_json']}"
    )
    return exit_code


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
    parser = JsonAwareArgumentParser(prog="code-wiki")
    parser.add_argument("--version", action="version", version=f"code-wiki {VERSION}")
    parser.add_argument("--json", action="store_true", help="emit stable JSON for commands that support it")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser("doctor", help="check local and pilot runtime readiness without invoking a model")
    doctor_parser.set_defaults(func=cmd_doctor)

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

    pilot_parser = subparsers.add_parser("pilot", help="run or compare the opt-in two-node study-to-render pilot")
    pilot_subparsers = pilot_parser.add_subparsers(dest="pilot_command", required=True)

    pilot_run_parser = pilot_subparsers.add_parser("run", help="run one baseline or two-node candidate wiki generation")
    pilot_run_parser.add_argument("--mode", required=True, choices=("baseline", "node-graph"))
    pilot_run_parser.add_argument("--repo", required=True, help="clean local Git repository")
    pilot_run_parser.add_argument("--commit", required=True, help="commit or ref to pin in the isolated snapshot")
    pilot_run_parser.add_argument("--out", required=True, help="empty output directory outside the source repository")
    pilot_run_parser.add_argument("--model", required=True, help="explicit Codex model for every agent node")
    pilot_run_parser.add_argument(
        "--reasoning-effort",
        required=True,
        choices=tuple(sorted(REASONING_EFFORTS)),
        help="explicit Codex reasoning effort",
    )
    pilot_run_parser.add_argument("--title", help="wiki title; defaults to the source repository name")
    pilot_run_parser.add_argument(
        "--executor-fixture",
        help="explicit test-only Codex subprocess fixture JSON",
    )
    pilot_run_parser.add_argument(
        "--cache-root",
        help="override the disposable snapshot cache root for isolated tests",
    )
    pilot_run_parser.set_defaults(func=cmd_pilot_run)

    pilot_compare_parser = pilot_subparsers.add_parser("compare", help="compare complete baseline and two-node candidate run manifests")
    pilot_compare_parser.add_argument("--baseline-run", required=True, help="baseline run.json path")
    pilot_compare_parser.add_argument("--candidate-run", required=True, help="node-graph run.json path")
    pilot_compare_parser.add_argument("--out", required=True, help="comparison output directory")
    pilot_compare_parser.set_defaults(func=cmd_pilot_compare)

    pilot_aggregate_parser = pilot_subparsers.add_parser(
        "aggregate", help="aggregate exactly two canonical repository comparisons"
    )
    pilot_aggregate_parser.add_argument(
        "--comparison",
        required=True,
        action="append",
        help="repository-key=comparison.json; provide exactly twice",
    )
    pilot_aggregate_parser.add_argument("--out", required=True, help="aggregate output directory")
    pilot_aggregate_parser.set_defaults(func=cmd_pilot_aggregate)

    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = list(argv) if argv is not None else sys.argv[1:]
    JsonAwareArgumentParser.json_errors = "--json" in arguments
    parser = build_parser()
    try:
        args = parser.parse_args(arguments)
        return args.func(args)
    except JsonArgumentError:
        return 2
    except (OSError, RuntimeError, ValueError) as exc:
        if "--json" in arguments:
            print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2
    finally:
        JsonAwareArgumentParser.json_errors = False


if __name__ == "__main__":
    sys.exit(main())
