from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
CMD = SKILL_ROOT / "scripts" / "code-wiki"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from code_wiki.pilot.comparison import _read_manifest, build_decision  # noqa: E402
from code_wiki.pilot.common import hash_path  # noqa: E402
from code_wiki.pilot.contracts import ContractError, load_graph, parse_node  # noqa: E402
from code_wiki.pilot.provenance import (  # noqa: E402
    load_or_create_provenance_key,
    provenance_key_status,
    sign_receipt,
    verify_receipt,
)
from code_wiki.pilot.runner import (  # noqa: E402
    _assert_paths_hidden,
    _materialize_declared_inputs,
    _invoke_agent,
    _mark_agent_result,
    _node_prompt,
    _prepare,
    _promote_staged_outputs,
    _restore_source_metadata,
    _sanitize_source_metadata,
    _seed_staging_outputs,
    _validate_study_brief,
    run_pilot,
)
from code_wiki.pilot.runtime import (  # noqa: E402
    CodexExecutor,
    ExecutionError,
    FixtureExecutor,
    TokenUsage,
    _safe_environment,
    _write_source_free_config,
    parse_terminal_usage,
)
from code_wiki.pilot.snapshot import SourceSnapshot, create_snapshot  # noqa: E402
from code_wiki.wiki_contract import REQUIRED_PAGES  # noqa: E402


class CodeWikiPilotTests(unittest.TestCase):
    maxDiff = None

    def run_cli(
        self,
        *args: str,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(CMD), *args],
            cwd=SKILL_ROOT,
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )

    def create_repo(self, root: Path) -> tuple[Path, str]:
        repo = root / "source-repo"
        (repo / "pkg").mkdir(parents=True)
        (repo / "tests").mkdir()
        (repo / "README.md").write_text(
            "# Representative repository\n"
            + "\n".join(f"documented source behavior line {index}" for index in range(1, 620))
            + "\n",
            encoding="utf-8",
        )
        (repo / "pyproject.toml").write_text(
            "[project]\nname = \"representative\"\nversion = \"1.0.0\"\n",
            encoding="utf-8",
        )
        (repo / "pkg" / "__init__.py").write_text("from .main import run\n", encoding="utf-8")
        (repo / "pkg" / "main.py").write_text(
            "def run(value: str) -> str:\n"
            "    if not value:\n"
            "        raise ValueError('value')\n"
            "    return value.strip()\n",
            encoding="utf-8",
        )
        (repo / "tests" / "test_main.py").write_text(
            "from pkg.main import run\n\n"
            "def test_run():\n"
            "    assert run(' ok ') == 'ok'\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "pilot@example.test"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Pilot Fixture"], cwd=repo, check=True)
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=repo, check=True, capture_output=True, text=True)
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return repo, commit

    @staticmethod
    def usage_event(input_tokens: int = 100, cached: int = 10, output: int = 20, reasoning: int = 5) -> dict[str, object]:
        return {
            "type": "turn.completed",
            "usage": {
                "input_tokens": input_tokens,
                "cached_input_tokens": cached,
                "output_tokens": output,
                "reasoning_output_tokens": reasoning,
            },
        }

    @staticmethod
    def reader_evaluation(status: str = "pass") -> str:
        return json.dumps(
            {
                "reader_status": status,
                "required_page_completeness": status,
                "navigation_link_integrity": status,
                "evidence_fidelity": status,
                "unsupported_claim_risk": "none" if status == "pass" else "material",
                "material_omissions": [] if status == "pass" else ["missing maintainer path"],
                "summary": "The fixture wiki satisfies the identical reader contract.",
            },
            sort_keys=True,
        ) + "\n"

    @staticmethod
    def page_html(page: str) -> str:
        page_token = page.replace("/", " ").replace(".", " ")
        vocabulary = (
            "use case capability scenario user audience surface entry api command package route module "
            "constraint responsibility owner license security support official upstream public interface "
            "header export consumer caller usage file path stability contract internal state carrier lifecycle "
            "object store context create initialize allocated mutate update write change observe callback read "
            "event cleanup shutdown destroy release component subsystem interaction call path sequence class "
            "struct protocol trait function type registration thread lock async worker concurrency cache dependency "
            "manifest build runtime target provider pattern convention abstraction layer configuration extension "
            "basic request startup flow step output failure edge retry background integration branch condition "
            "cancel abort timeout overload fallback rollback validation test ci workflow operation deploy "
            "observability environment release lint debug add remove risk caveat collaborator first source root "
            "docs example generated third-party vendor trigger detect handler effect status error recover task run "
            "script when scope expected signal artifact compatibility breaking backout revert pkg tests no governance"
        )
        sections = []
        for index in range(1, 5):
            evidence = "".join(
                f'<a class="evidence-chip" href="#" data-evidence="README.md:{line}" title="README.md:{line}">README.md:{line}</a>'
                for line in range(index * 3 - 2, index * 3 + 1)
            )
            table = (
                f"<table><tr><th>{page_token} {vocabulary}</th></tr>"
                f"<tr><td>{page_token} pkg tests generated vendor</td></tr></table>"
                if index == 1
                else ""
            )
            command = "<pre><code>python3 -m unittest</code></pre>" if index == 1 else ""
            sections.append(
                f"<section><h2>Concrete contract {index}</h2>"
                f"<p>{page_token} section {index} explains {vocabulary}. "
                f"The representative package behavior for {page_token} is concrete evidence item {index} and "
                f"connects maintainers to pkg and tests with an explicit ownership boundary.</p>"
                f"{table}{command}<details class=\"evidence\"><summary>Evidence</summary>{evidence}</details>"
                "</section>"
            )
        return f"""<!doctype html>
<html><head><title>{page_token}</title></head><body><main>
<h1>{page_token}</h1>{''.join(sections)}</main></body></html>
"""

    def valid_wiki_writes(self) -> dict[str, str]:
        writes = {f"wiki/{page}": self.page_html(page) for page in REQUIRED_PAGES}
        claims = []
        for index, page in enumerate(REQUIRED_PAGES):
            first_evidence = "pkg/main.py:1-4" if index == 0 else f"README.md:{index + 1}"
            second_evidence = "tests/test_main.py:1-4" if index == 0 else f"README.md:{index + 30}"
            claims.extend(
                [
                    {
                        "claim": f"{page} owns representative behavior claim alpha {index}",
                        "page": page,
                        "evidence": [first_evidence],
                        "why_it_matters": "A maintainer needs the concrete owner and change boundary.",
                        "status": "ready",
                    },
                    {
                        "claim": f"{page} validates representative behavior claim beta {index}",
                        "page": page,
                        "evidence": [second_evidence],
                        "why_it_matters": "A maintainer needs the exact verification surface.",
                        "status": "ready",
                    },
                ]
            )
        matrix = {
            "schema_version": 1,
            "repo": {},
            "inventory": {},
            "page_targets": [
                {"page": page, "min_ready_claims": 2, "status": "ready"}
                for page in REQUIRED_PAGES
            ],
            "deep_dive_targets": {
                "minimum_pages": 2,
                "min_ready_claims_per_page": 3,
                "status": "not_applicable",
                "suggested_pages": [],
            },
            "coverage_roots": [
                {"root": "pkg", "kind": "source", "status": "ready", "not_applicable_reason": ""},
                {"root": "tests", "kind": "test", "status": "ready", "not_applicable_reason": ""},
            ],
            "claims": claims,
        }
        writes["wiki/data/claim-matrix.json"] = json.dumps(matrix, indent=2, sort_keys=True) + "\n"
        return writes

    @staticmethod
    def study_brief(
        *,
        omit_page: str | None = None,
        invalid_evidence: bool = False,
        missing_topic: str | None = None,
    ) -> str:
        sections = []
        second_evidence = "pkg/missing.py:1-4" if invalid_evidence else "pkg/main.py:1-4"
        for page in REQUIRED_PAGES:
            if page == omit_page:
                continue
            sections.append(
                f"## Page: `{page}`\n\n"
                "The architecture section names the representative package boundary and explains how its "
                "public interface participates in the runtime lifecycle and state model. The basic call flow "
                "starts at the documented entrypoint, crosses the package operation, and returns the normalized "
                "result. The advanced flow covers failure behavior, retry limits, cleanup ownership, and observable "
                "errors. Maintainer operations include the exact test and validation commands, expected artifacts, "
                "and source ownership. The change recipe starts with the implementation, updates its public contract, "
                "runs focused tests, and checks compatibility. Risk analysis covers unsupported input and accidental "
                "boundary changes; rollback reverts the implementation and validates the restored behavior. The page "
                "will render two distinct ready claims: one about implementation ownership and one about verification "
                "ownership. Evidence demonstrates both the documented project context and concrete executable path, "
                "so the renderer does not need another repository study. Interface, lifecycle, flow, operation, test, "
                "failure, change, risk, validation, rollback, and architecture coverage are all explicit. "
                f"[README.md:1-10] [{second_evidence}]\n"
            )
        result = "\n".join(sections)
        return result.replace(missing_topic, "omitted-topic") if missing_topic else result

    def write_fixture(self, root: Path, mode: str, *, repair: bool = False, failure: str | None = None) -> Path:
        success = self.usage_event()
        invocations: dict[str, list[dict[str, object]]]
        if mode == "baseline":
            reader_output = self.reader_evaluation()
            if failure == "reader-inconsistent":
                reader_value = json.loads(reader_output)
                reader_value["evidence_fidelity"] = "fail"
                reader_output = json.dumps(reader_value, sort_keys=True) + "\n"
            generate: dict[str, object] = {"events": [success], "writes": self.valid_wiki_writes()}
            if failure == "missing-usage":
                generate = {"events": [{"type": "turn.started"}]}
            if failure == "mutation":
                generate["mutate_source"] = {"path": "README.md", "content": "mutated\n"}
            invocations = {
                "baseline-generate": [generate],
                "reader": [
                    {
                        "events": [success],
                        "writes": {
                            "artifacts/reader-evaluation.json": reader_output,
                            "wiki/index.html": "undeclared reader mutation must not be promoted\n",
                        },
                    }
                ],
            }
        else:
            study: dict[str, object] = {
                "events": [success],
                "writes": {
                    "artifacts/study.md": self.study_brief(
                        omit_page=REQUIRED_PAGES[-1] if failure == "study-missing-page" else None,
                        invalid_evidence=failure == "study-invalid-evidence",
                        missing_topic="rollback" if failure == "study-missing-topic" else None,
                    )
                },
            }
            if failure == "study-failure":
                study["exit_code"] = 1
            invocations = {
                "study": [study],
                "render": [
                    {
                        "events": [success],
                        "writes": {} if repair else self.valid_wiki_writes(),
                    }
                ],
                "repair": [
                    {
                        "events": [success],
                        "writes": self.valid_wiki_writes(),
                    }
                ],
                "reader": [
                    {
                        "events": [success],
                        "writes": {
                            "artifacts/reader-evaluation.json": self.reader_evaluation(),
                            "wiki/index.html": "undeclared reader mutation must not be promoted\n",
                        },
                    }
                ],
            }
        path = root / f"{mode}-fixture.json"
        path.write_text(json.dumps({"invocations": invocations}, indent=2), encoding="utf-8")
        return path

    def run_fixture(self, root: Path, repo: Path, commit: str, mode: str, fixture: Path, name: str) -> tuple[subprocess.CompletedProcess[str], Path, dict[str, object]]:
        out = root / name
        result = self.run_cli(
            "--json",
            "pilot",
            "run",
            "--mode",
            mode,
            "--repo",
            str(repo),
            "--commit",
            commit,
            "--out",
            str(out),
            "--model",
            "fixture-model",
            "--reasoning-effort",
            "high",
            "--executor-fixture",
            str(fixture),
            "--cache-root",
            str(root / "cache"),
        )
        manifest = json.loads((out / "run.json").read_text(encoding="utf-8"))
        return result, out, manifest

    def test_doctor_is_read_only_and_reports_pilot_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            before = set(SKILL_ROOT.rglob("*"))
            env = os.environ.copy()
            env["HOME"] = tmp
            key_path = Path(tmp) / ".cache" / "dotagents" / "skills" / "code-wiki" / "pilot" / "provenance.key"
            result = self.run_cli("--json", "doctor", env=env)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["cli_version"], "0.7.0")
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["live_pilot_ready"])
            self.assertFalse(payload["model_invoked"])
            self.assertFalse(payload["config_written"])
            self.assertFalse(key_path.exists())
            self.assertEqual(before, set(SKILL_ROOT.rglob("*")))

    def test_strict_node_contracts_bind_graph_order_and_reader_identity(self) -> None:
        baseline = load_graph(SKILL_ROOT, "baseline")
        candidate = load_graph(SKILL_ROOT, "node-graph")
        self.assertEqual(
            set(candidate.nodes),
            {"prepare", "study", "render", "validate", "repair", "reader"},
        )
        self.assertEqual(candidate.nodes["study"].dependencies, ("prepare",))
        self.assertEqual(candidate.nodes["study"].output_artifacts, ("artifacts/study.md",))
        self.assertEqual(candidate.nodes["render"].dependencies, ("prepare", "study"))
        self.assertNotIn("source", candidate.nodes["render"].input_artifacts)
        self.assertEqual(candidate.nodes["repair"].repair_target, "validate")
        self.assertEqual(
            baseline.nodes["reader"].sha256,
            candidate.nodes["reader"].sha256,
        )

        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.md"
            bad.write_text(
                "# Bad\n\n| Field | Value |\n| --- | --- |\n"
                "| `node_id` | `bad` |\n| `node_kind` | `shell` |\n"
                "| `dependencies` | `none` |\n| `input_artifacts` | `source` |\n"
                "| `output_artifacts` | `out` |\n| `repair_target` | `none` |\n"
                "\n## Instructions\n\nRun arbitrary commands.\n",
                encoding="utf-8",
            )
            with self.assertRaises(ContractError):
                parse_node(bad)

            copied_root = Path(tmp) / "copied-skill"
            shutil.copytree(SKILL_ROOT / "references", copied_root / "references")
            stale = copied_root / "references" / "pilot-nodes" / "node-graph" / "synthesize.md"
            stale.write_text("retired topology\n", encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "retired candidate node contracts"):
                load_graph(copied_root, "node-graph")

    def test_internal_provenance_key_is_private_and_detects_receipt_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_root = Path(tmp) / "pilot-cache"
            key = load_or_create_provenance_key(cache_root)
            key_path = cache_root / "provenance.key"
            self.assertEqual(key_path.stat().st_mode & 0o777, 0o600)
            self.assertTrue(provenance_key_status(key_path)["ok"])
            receipt = {
                "schema_version": 1,
                "run_id": "fixture-run",
                "signature": None,
            }
            receipt["signature"] = sign_receipt(receipt, key)
            self.assertTrue(verify_receipt(receipt, key))
            receipt["run_id"] = "tampered-run"
            self.assertFalse(verify_receipt(receipt, key))

    def test_jsonl_usage_aggregation_rejects_missing_duplicate_and_negative_usage(self) -> None:
        first = self.usage_event(120, 20, 30, 10)
        usage = parse_terminal_usage(json.dumps(first) + "\n")
        self.assertEqual(usage.uncached_input_tokens, 100)
        self.assertEqual(usage.total_model_tokens, 150)
        for payload in (
            json.dumps({"type": "turn.started"}) + "\n",
            json.dumps(first) + "\n" + json.dumps(first) + "\n",
            json.dumps({"type": "turn.completed", "usage": {**first["usage"], "input_tokens": -1}}) + "\n",
            "not-json\n",
        ):
            with self.subTest(payload=payload), self.assertRaises(ExecutionError):
                parse_terminal_usage(payload)

    def test_live_executor_keeps_snapshot_out_of_all_writable_roots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot = root / "snapshot"
            output = root / "output"
            raw = output / "raw"
            snapshot.mkdir()
            output.mkdir()
            terminal = json.dumps(self.usage_event()) + "\n"
            executor = CodexExecutor("fixture-model", "high")
            completed = subprocess.CompletedProcess(
                args=["codex"], returncode=0, stdout=terminal, stderr=""
            )
            with mock.patch("code_wiki.pilot.runtime.subprocess.run", return_value=completed) as run:
                executor.invoke(
                    node_id="reader",
                    attempt=1,
                    prompt="read only",
                    snapshot=snapshot,
                    input_root=snapshot,
                    output_root=output,
                    raw_root=raw,
                    source_allowed=True,
                )
            command = run.call_args.args[0]
            working_directory = Path(command[command.index("--cd") + 1])
            writable_additions = [
                Path(command[index + 1])
                for index, value in enumerate(command)
                if value == "--add-dir"
            ]
            self.assertNotEqual(working_directory, snapshot)
            self.assertEqual(writable_additions, [output])
            self.assertNotIn(snapshot, writable_additions)
            self.assertIn("--skip-git-repo-check", command)
            self.assertIn(
                'shell_environment_policy.exclude=["^OPENAI_API_KEY$"]',
                command,
            )

    def test_source_free_executor_uses_restricted_permission_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            auth_home = root / "auth-home"
            input_root = root / "input"
            output_root = root / "output"
            raw_root = root / "raw"
            snapshot = root / "hidden-snapshot"
            for path in (auth_home, input_root, output_root, snapshot):
                path.mkdir()
            (auth_home / "auth.json").write_text('{"fixture": true}\n', encoding="utf-8")
            terminal = json.dumps(self.usage_event()) + "\n"
            observed: dict[str, object] = {}

            def capture(
                command: list[str],
                *,
                input: str,
                text: bool,
                capture_output: bool,
                check: bool,
                env: dict[str, str],
            ) -> subprocess.CompletedProcess[str]:
                del input, text, capture_output, check
                isolated_home = Path(env["CODEX_HOME"])
                observed["command"] = command
                observed["config"] = (isolated_home / "config.toml").read_text(encoding="utf-8")
                observed["auth_mode"] = (isolated_home / "auth.json").stat().st_mode & 0o777
                observed["codex_home"] = isolated_home
                return subprocess.CompletedProcess(command, 0, stdout=terminal, stderr="")

            executor = CodexExecutor("fixture-model", "high")
            with mock.patch.dict(
                os.environ,
                {"CODEX_HOME": str(auth_home), "HOME": str(root), "PATH": os.environ["PATH"]},
                clear=True,
            ), mock.patch("code_wiki.pilot.runtime.subprocess.run", side_effect=capture):
                executor.invoke(
                    node_id="render",
                    attempt=1,
                    prompt="source free",
                    snapshot=snapshot,
                    input_root=input_root,
                    output_root=output_root,
                    raw_root=raw_root,
                    source_allowed=False,
                )

            command = observed["command"]
            self.assertNotIn("--sandbox", command)
            self.assertNotIn("--add-dir", command)
            self.assertNotIn("--ignore-user-config", command)
            self.assertIn("--strict-config", command)
            config = str(observed["config"])
            self.assertIn('default_permissions = "code_wiki_source_free"', config)
            self.assertIn(f'{json.dumps(str(input_root.resolve()))} = "read"', config)
            self.assertIn(f'{json.dumps(str(output_root.resolve()))} = "write"', config)
            self.assertNotIn(str(snapshot), config)
            self.assertEqual(observed["auth_mode"], 0o600)
            self.assertNotEqual(observed["codex_home"], auth_home)

    def test_restricted_permission_profile_blocks_undeclared_reads_and_writes(self) -> None:
        codex = shutil.which("codex")
        if not codex:
            self.skipTest("Codex CLI is unavailable")
        help_result = subprocess.run(
            [codex, "sandbox", "--help"], text=True, capture_output=True, check=False
        )
        if help_result.returncode != 0 or "--permission-profile" not in help_result.stdout:
            self.skipTest("Codex CLI lacks named permission profiles")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / "codex-home"
            input_root = root / "declared-input"
            output_root = root / "declared-output"
            working_root = root / "working"
            hidden_root = root / "undeclared-source"
            for path in (codex_home, input_root, output_root, working_root, hidden_root):
                path.mkdir()
            (input_root / "allowed.txt").write_text("allowed\n", encoding="utf-8")
            (hidden_root / "hidden.txt").write_text("hidden\n", encoding="utf-8")
            _write_source_free_config(
                codex_home,
                input_root=input_root,
                output_root=output_root,
                working_directory=working_root,
            )
            (codex_home / "auth.json").write_text(
                '{"secret": "must-not-reach-tools"}\n', encoding="utf-8"
            )
            environment = os.environ.copy()
            environment["CODEX_HOME"] = str(codex_home)
            probe = subprocess.run(
                [
                    codex,
                    "sandbox",
                    "--permission-profile",
                    "code_wiki_source_free",
                    "--cd",
                    str(working_root),
                    "--",
                    "/bin/sh",
                    "-c",
                    (
                        f'test -r {json.dumps(str(input_root / "allowed.txt"))} && '
                        f'! test -r {json.dumps(str(hidden_root / "hidden.txt"))} && '
                        f'! test -r {json.dumps(str(codex_home / "auth.json"))} && '
                        f'touch {json.dumps(str(output_root / "written.txt"))} && '
                        f'! touch {json.dumps(str(hidden_root / "blocked.txt"))} 2>/dev/null'
                    ),
                ],
                text=True,
                capture_output=True,
                check=False,
                env=environment,
            )
            self.assertEqual(probe.returncode, 0, probe.stdout + probe.stderr)
            self.assertTrue((output_root / "written.txt").is_file())
            self.assertFalse((hidden_root / "blocked.txt").exists())

    def test_live_executor_environment_preserves_api_key_authentication(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "fixture-key", "CODE_WIKI_UNRELATED": "discard-me"},
            clear=True,
        ):
            environment = _safe_environment()
        self.assertEqual(environment["OPENAI_API_KEY"], "fixture-key")
        self.assertNotIn("CODE_WIKI_UNRELATED", environment)

    def test_snapshot_rejects_tracked_symlinks_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, _ = self.create_repo(root)
            os.symlink("/etc/hosts", repo / "host-escape")
            subprocess.run(["git", "add", "host-escape"], cwd=repo, check=True)
            subprocess.run(
                ["git", "commit", "-m", "add unsafe symlink"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            fixture = self.write_fixture(root, "baseline")
            result = self.run_cli(
                "--json", "pilot", "run",
                "--mode", "baseline",
                "--repo", str(repo),
                "--commit", commit,
                "--out", str(root / "symlink-run"),
                "--model", "fixture-model",
                "--reasoning-effort", "high",
                "--executor-fixture", str(fixture),
                "--cache-root", str(root / "cache"),
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("cannot contain tracked symlinks", result.stdout)

    def test_artifact_hash_includes_nested_git_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "wiki"
            artifact.mkdir()
            (artifact / "index.html").write_text("wiki\n", encoding="utf-8")
            artifact_hash = hash_path(artifact)
            source_hash = hash_path(artifact, exclude_git_metadata=True)

            (artifact / ".git").mkdir()
            (artifact / ".git" / "config").write_text("unverified\n", encoding="utf-8")

            self.assertNotEqual(hash_path(artifact), artifact_hash)
            self.assertEqual(
                hash_path(artifact, exclude_git_metadata=True),
                source_hash,
            )

    def test_snapshot_rejects_unmaterialized_gitlinks_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, dependency_commit = self.create_repo(root)
            (repo / "vendor").mkdir()
            subprocess.run(
                ["git", "clone", "--no-local", str(repo), str(repo / "vendor" / "dependency")],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "checkout", "--detach", dependency_commit],
                cwd=repo / "vendor" / "dependency",
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    "git", "update-index", "--add", "--cacheinfo",
                    "160000", dependency_commit, "vendor/dependency",
                ],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "add pinned submodule entry"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            fixture = self.write_fixture(root, "baseline")
            result = self.run_cli(
                "--json", "pilot", "run",
                "--mode", "baseline",
                "--repo", str(repo),
                "--commit", commit,
                "--out", str(root / "gitlink-run"),
                "--model", "fixture-model",
                "--reasoning-effort", "high",
                "--executor-fixture", str(fixture),
                "--cache-root", str(root / "cache"),
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("cannot contain unmaterialized gitlinks/submodules", result.stdout)

    def test_fixture_schema_rejects_external_tree_copy_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, commit = self.create_repo(root)
            fixture = self.write_fixture(root, "baseline")
            payload = json.loads(fixture.read_text(encoding="utf-8"))
            payload["invocations"]["baseline-generate"][0]["copy_trees"] = {
                "wiki/leak": "/etc"
            }
            fixture.write_text(json.dumps(payload), encoding="utf-8")
            result, _, manifest = self.run_fixture(
                root, repo, commit, "baseline", fixture, "copy-tree-rejection"
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsupported fields: copy_trees", manifest["error"])
            attempt = manifest["nodes"]["baseline-generate"]["attempts"][0]
            self.assertFalse(attempt["model_call_started"])
            self.assertEqual(manifest["metrics"]["generation"]["model_call_count"], 0)
            self.assertEqual(manifest["metrics"]["generation"]["failed_terminal_calls"], 0)

    def test_failed_directory_replacement_preserves_previous_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_root = root / "output"
            staging_root = root / "staging"
            (output_root / "wiki").mkdir(parents=True)
            (staging_root / "wiki").mkdir(parents=True)
            (output_root / "wiki" / "index.html").write_text("old\n", encoding="utf-8")
            (staging_root / "wiki" / "index.html").write_text("new\n", encoding="utf-8")
            with mock.patch(
                "code_wiki.pilot.runner.shutil.copytree",
                side_effect=OSError("simulated disk full"),
            ), self.assertRaises(OSError):
                _promote_staged_outputs(output_root, staging_root, ("wiki",))
            self.assertEqual(
                (output_root / "wiki" / "index.html").read_text(encoding="utf-8"),
                "old\n",
            )
            self.assertFalse(any(output_root.glob(".wiki.replacement-*")))

    def test_post_execution_artifact_failure_preserves_terminal_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, commit = self.create_repo(root)
            graph = load_graph(SKILL_ROOT, "node-graph")
            snapshot = create_snapshot(str(repo), commit, str(root / "cache"))
            output_root = root / "run"
            output_root.mkdir()
            _prepare(graph.nodes["prepare"], snapshot, output_root, "fixture")
            fixture = self.write_fixture(root, "node-graph")
            executor = FixtureExecutor(fixture)

            with mock.patch(
                "code_wiki.pilot.runner._promote_staged_outputs",
                side_effect=OSError("simulated promotion failure"),
            ):
                attempt, result, error = _invoke_agent(
                    executor=executor,
                    node=graph.nodes["study"],
                    graph=graph,
                    snapshot=snapshot,
                    output_root=output_root,
                    attempt=1,
                )

            self.assertIsNotNone(result)
            self.assertEqual(attempt["status"], "fail")
            self.assertEqual(attempt["exit_code"], 0)
            self.assertEqual(attempt["usage"]["input_tokens"], 100)
            self.assertGreater(attempt["duration_ms"], 0)
            self.assertIn("simulated promotion failure", error)
            manifest = {
                "nodes": {"study": {"status": "pending", "attempts": []}},
                "metrics": {
                    "generation": {
                        **TokenUsage.zero().as_dict(),
                        "model_call_count": 0,
                        "failed_terminal_calls": 0,
                        "wall_time_ms": 0,
                    },
                    "reader": {
                        **TokenUsage.zero().as_dict(),
                        "model_call_count": 0,
                        "failed_terminal_calls": 0,
                        "wall_time_ms": 0,
                    },
                },
                "error": None,
            }
            _mark_agent_result(
                manifest,
                graph.nodes["study"],
                attempt,
                result,
                error,
            )
            self.assertEqual(manifest["nodes"]["study"]["status"], "fail")
            self.assertEqual(manifest["metrics"]["generation"]["model_call_count"], 1)
            self.assertEqual(manifest["metrics"]["generation"]["failed_terminal_calls"], 0)
            self.assertEqual(manifest["metrics"]["generation"]["input_tokens"], 100)

            prelaunch_output = root / "prelaunch-run"
            prelaunch_output.mkdir()
            _prepare(graph.nodes["prepare"], snapshot, prelaunch_output, "fixture")
            with mock.patch(
                "code_wiki.pilot.runner._persist_artifact_evidence",
                side_effect=OSError("simulated pre-launch evidence failure"),
            ):
                prelaunch_attempt, prelaunch_result, prelaunch_error = _invoke_agent(
                    executor=executor,
                    node=graph.nodes["study"],
                    graph=graph,
                    snapshot=snapshot,
                    output_root=prelaunch_output,
                    attempt=1,
                )
            self.assertIsNone(prelaunch_result)
            self.assertFalse(prelaunch_attempt["model_call_started"])
            self.assertIsNone(prelaunch_attempt["usage"])
            self.assertIn("simulated pre-launch evidence failure", prelaunch_error)
            prelaunch_manifest = {
                "nodes": {"study": {"status": "pending", "attempts": []}},
                "metrics": {
                    "generation": {
                        **TokenUsage.zero().as_dict(),
                        "model_call_count": 0,
                        "failed_terminal_calls": 0,
                        "wall_time_ms": 0,
                    },
                    "reader": {
                        **TokenUsage.zero().as_dict(),
                        "model_call_count": 0,
                        "failed_terminal_calls": 0,
                        "wall_time_ms": 0,
                    },
                },
                "error": None,
            }
            _mark_agent_result(
                prelaunch_manifest,
                graph.nodes["study"],
                prelaunch_attempt,
                prelaunch_result,
                prelaunch_error,
            )
            self.assertEqual(prelaunch_manifest["metrics"]["generation"]["model_call_count"], 0)
            self.assertEqual(
                prelaunch_manifest["metrics"]["generation"]["failed_terminal_calls"], 0
            )

    def test_source_free_render_gets_only_sanitized_declared_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = root / "original-checkout"
            snapshot_path = root / "snapshot"
            output_root = root / "durable-output"
            input_root = root / "isolated-input"
            staging_root = root / "isolated-output"
            original.mkdir()
            snapshot_path.mkdir()
            (snapshot_path / "README.md").write_text("source\n", encoding="utf-8")
            inventory_path = output_root / "wiki" / "data" / "inventory.json"
            matrix_path = output_root / "wiki" / "data" / "claim-matrix.json"
            inventory_path.parent.mkdir(parents=True)
            trusted_inventory = {
                "schema_version": 1,
                "repo": {
                    "name": "fixture",
                    "path": str(snapshot_path),
                    "remote_url": str(original),
                },
            }
            trusted_matrix = {
                "schema_version": 1,
                "repo": {
                    "name": "fixture",
                    "path": str(snapshot_path),
                    "web_url": str(original),
                },
                "inventory": {"path": str(inventory_path), "schema_version": 1},
                "claims": [],
            }
            inventory_path.write_text(
                json.dumps(trusted_inventory, indent=2) + "\n", encoding="utf-8"
            )
            matrix_path.write_text(
                json.dumps(trusted_matrix, indent=2) + "\n", encoding="utf-8"
            )
            (output_root / "wiki" / "index.html").write_text("scaffold\n", encoding="utf-8")
            (output_root / "artifacts").mkdir()
            (output_root / "artifacts" / "study.md").write_text(
                "source-backed brief without local checkout paths\n", encoding="utf-8"
            )
            (output_root / "run.json").write_text(
                json.dumps({"source": {"snapshot_path": str(snapshot_path)}}), encoding="utf-8"
            )
            snapshot = SourceSnapshot(
                original_checkout=original,
                original_head_before="0" * 40,
                commit="0" * 40,
                original_status_before="",
                snapshot_path=snapshot_path,
                snapshot_tree_hash="fixture",
            )
            graph = load_graph(SKILL_ROOT, "node-graph")
            render = graph.nodes["render"]

            _materialize_declared_inputs(
                output_root, input_root, snapshot, render.input_artifacts
            )
            _seed_staging_outputs(output_root, staging_root, render.output_artifacts)
            _sanitize_source_metadata(input_root)
            _sanitize_source_metadata(staging_root)
            hidden_paths = (snapshot_path, original, output_root)
            _assert_paths_hidden(input_root, hidden_paths)
            _assert_paths_hidden(staging_root, hidden_paths)

            self.assertFalse((input_root / "run.json").exists())
            self.assertFalse((input_root / "source").exists())
            isolated_inventory = json.loads(
                (input_root / "wiki" / "data" / "inventory.json").read_text(encoding="utf-8")
            )
            isolated_matrix = json.loads(
                (input_root / "wiki" / "data" / "claim-matrix.json").read_text(encoding="utf-8")
            )
            self.assertEqual(isolated_inventory["repo"]["path"], "source-not-declared")
            self.assertIsNone(isolated_inventory["repo"]["remote_url"])
            self.assertEqual(isolated_matrix["repo"]["path"], "source-not-declared")
            self.assertIsNone(isolated_matrix["repo"]["web_url"])
            self.assertEqual(isolated_matrix["inventory"]["path"], "wiki/data/inventory.json")

            prompt = _node_prompt(
                node=render,
                graph=graph,
                snapshot=snapshot,
                input_root=input_root,
                agent_output_root=staging_root,
                input_hashes={artifact: "0" * 64 for artifact in render.input_artifacts},
                attempt=1,
                validation_feedback=None,
            )
            self.assertNotIn(str(snapshot_path), prompt)
            self.assertNotIn(str(original), prompt)
            self.assertNotIn(str(output_root), prompt)
            self.assertIn(str(input_root), prompt)

            rendered_matrix = json.loads(
                (staging_root / "wiki" / "data" / "claim-matrix.json").read_text(
                    encoding="utf-8"
                )
            )
            rendered_matrix["claims"] = [{"claim": "model-rendered"}]
            (staging_root / "wiki" / "data" / "claim-matrix.json").write_text(
                json.dumps(rendered_matrix, indent=2) + "\n", encoding="utf-8"
            )
            _restore_source_metadata(output_root, staging_root)
            restored_inventory = json.loads(
                (staging_root / "wiki" / "data" / "inventory.json").read_text(encoding="utf-8")
            )
            restored_matrix = json.loads(
                (staging_root / "wiki" / "data" / "claim-matrix.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(restored_inventory, trusted_inventory)
            self.assertEqual(restored_matrix["repo"], trusted_matrix["repo"])
            self.assertEqual(restored_matrix["inventory"], trusted_matrix["inventory"])
            self.assertEqual(restored_matrix["claims"], [{"claim": "model-rendered"}])

    def test_study_evidence_rejects_parent_traversal_even_when_target_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot_path = root / "snapshot"
            output_root = root / "output"
            (snapshot_path / "pkg").mkdir(parents=True)
            (snapshot_path / "README.md").write_text("line\n" * 20, encoding="utf-8")
            (snapshot_path / "pkg" / "main.py").write_text("line\n" * 20, encoding="utf-8")
            (root / "outside.md").write_text("outside\n" * 20, encoding="utf-8")
            (output_root / "artifacts").mkdir(parents=True)
            escaped = self.study_brief().replace(
                "pkg/main.py:1-4", "../outside.md:1-4"
            )
            (output_root / "artifacts" / "study.md").write_text(escaped, encoding="utf-8")
            snapshot = SourceSnapshot(
                original_checkout=root / "original",
                original_head_before="0" * 40,
                commit="0" * 40,
                original_status_before="",
                snapshot_path=snapshot_path,
                snapshot_tree_hash="fixture",
            )
            with self.assertRaisesRegex(RuntimeError, "evidence path is unsafe"):
                _validate_study_brief(output_root, snapshot)

    def test_study_evidence_accepts_canonical_paths_with_spaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot_path = root / "snapshot"
            output_root = root / "output"
            (snapshot_path / "docs").mkdir(parents=True)
            (snapshot_path / "README.md").write_text("line\n" * 20, encoding="utf-8")
            (snapshot_path / "docs" / "API Guide.md").write_text(
                "line\n" * 20, encoding="utf-8"
            )
            (output_root / "artifacts").mkdir(parents=True)
            spaced = self.study_brief().replace(
                "pkg/main.py:1-4", "docs/API Guide.md:1-4"
            )
            (output_root / "artifacts" / "study.md").write_text(spaced, encoding="utf-8")
            snapshot = SourceSnapshot(
                original_checkout=root / "original",
                original_head_before="0" * 40,
                commit="0" * 40,
                original_status_before="",
                snapshot_path=snapshot_path,
                snapshot_tree_hash="fixture",
            )
            _validate_study_brief(output_root, snapshot)

    def test_fixture_backed_baseline_and_node_graph_runs_are_complete_and_isolated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, commit = self.create_repo(root)
            source_status_before = subprocess.run(
                ["git", "status", "--porcelain=v1"], cwd=repo, check=True, capture_output=True, text=True
            ).stdout
            baseline_fixture = self.write_fixture(root, "baseline")
            candidate_fixture = self.write_fixture(root, "node-graph")
            baseline_result, baseline_out, baseline = self.run_fixture(
                root, repo, commit, "baseline", baseline_fixture, "baseline-run"
            )
            candidate_result, candidate_out, candidate = self.run_fixture(
                root, repo, commit, "node-graph", candidate_fixture, "candidate-run"
            )

            validation_debug = json.loads((baseline_out / "artifacts" / "validation.json").read_text(encoding="utf-8"))["validator_output"]
            self.assertEqual(baseline_result.returncode, 0, baseline_result.stdout + baseline_result.stderr + validation_debug)
            self.assertEqual(
                candidate_result.returncode,
                0,
                candidate_result.stdout + candidate_result.stderr + str(candidate["error"]),
            )
            self.assertEqual(json.loads(baseline_result.stdout)["terminal_status"], "completed")
            self.assertEqual(json.loads(candidate_result.stdout)["terminal_status"], "completed")
            self.assertEqual(candidate["metrics"]["generation"]["model_call_count"], 2)
            self.assertEqual(candidate["metrics"]["reader"]["model_call_count"], 1)
            self.assertEqual(len(candidate["nodes"]["study"]["attempts"]), 1)
            self.assertEqual(len(candidate["nodes"]["render"]["attempts"]), 1)
            self.assertEqual(candidate["nodes"]["repair"]["attempts"], [])
            render_attempt = candidate["nodes"]["render"]["attempts"][0]
            self.assertNotEqual(
                render_attempt["input_source_artifacts"]["wiki"],
                render_attempt["input_artifacts"]["wiki"],
            )
            self.assertEqual(
                render_attempt["input_source_artifacts"]["artifacts/study.md"],
                render_attempt["input_artifacts"]["artifacts/study.md"],
            )
            self.assertEqual(
                render_attempt["input_source_evidence_path"],
                "artifacts/node-evidence/input-source/render-attempt-1",
            )
            self.assertEqual(
                render_attempt["input_evidence_path"],
                "artifacts/node-evidence/input/render-attempt-1",
            )
            source_inventory = json.loads(
                (
                    candidate_out
                    / render_attempt["input_source_evidence_path"]
                    / "wiki"
                    / "data"
                    / "inventory.json"
                ).read_text(encoding="utf-8")
            )
            renderer_inventory = json.loads(
                (
                    candidate_out
                    / render_attempt["input_evidence_path"]
                    / "wiki"
                    / "data"
                    / "inventory.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(source_inventory["repo"]["path"], candidate["source"]["snapshot_path"])
            self.assertEqual(renderer_inventory["repo"]["path"], "source-not-declared")
            self.assertIsNone(renderer_inventory["repo"]["remote_url"])
            self.assertTrue((candidate_out / "artifacts" / "study.md").is_file())
            for manifest, out in ((baseline, baseline_out), (candidate, candidate_out)):
                self.assertEqual(manifest["terminal_status"], "completed")
                self.assertEqual(manifest["identity"]["execution_evidence"], "fixture")
                self.assertEqual(manifest["validation_status"], "pass")
                self.assertEqual(manifest["reader_evaluation"]["reader_status"], "pass")
                self.assertFalse(manifest["source"]["source_mutation"])
                self.assertTrue(manifest["source"]["original_checkout_unchanged"])
                self.assertEqual(
                    manifest["source"]["original_head_before"],
                    manifest["source"]["original_head_after"],
                )
                self.assertTrue((out / "wiki" / "pages" / "architecture.html").is_file())
                validation = json.loads(
                    (out / "artifacts" / "validation.json").read_text(encoding="utf-8")
                )
                self.assertEqual(
                    validation["validated_wiki_sha256"],
                    manifest["output"]["wiki_sha256"],
                )
                self.assertGreater(manifest["metrics"]["generation"]["input_tokens"], 0)
                self.assertGreater(manifest["metrics"]["reader"]["input_tokens"], 0)
            source_status_after = subprocess.run(
                ["git", "status", "--porcelain=v1"], cwd=repo, check=True, capture_output=True, text=True
            ).stdout
            self.assertEqual(source_status_after, source_status_before)

    def test_fixture_run_does_not_probe_codex_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, commit = self.create_repo(root)
            fixture = self.write_fixture(root, "baseline")
            with mock.patch(
                "code_wiki.pilot.runner._codex_version",
                side_effect=AssertionError("fixture execution must not probe Codex"),
            ):
                return_code, manifest = run_pilot(
                    mode="baseline",
                    repo=str(repo),
                    commit=commit,
                    out=str(root / "fixture-output"),
                    model="fixture-model",
                    reasoning_effort="high",
                    executor_fixture=str(fixture),
                    cache_root=str(root / "cache"),
                )

            self.assertEqual(return_code, 0, manifest["error"])
            self.assertEqual(
                manifest["identity"]["codex_cli_version"],
                "fixture-not-invoked",
            )

    def test_fixture_backed_repair_is_bounded_and_second_validation_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, commit = self.create_repo(root)
            fixture = self.write_fixture(root, "node-graph", repair=True)
            result, _, manifest = self.run_fixture(root, repo, commit, "node-graph", fixture, "repair-run")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr + str(manifest["error"]))
            validation_debug = json.loads((Path(manifest["output"]["root"]) / "artifacts" / "validation.json").read_text(encoding="utf-8"))["validator_output"]
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr + validation_debug)
            self.assertEqual(len(manifest["nodes"]["repair"]["attempts"]), 1)
            self.assertEqual(len(manifest["nodes"]["validate"]["attempts"]), 2)
            self.assertEqual(manifest["metrics"]["generation"]["model_call_count"], 3)
            self.assertEqual(manifest["metrics"]["reader"]["model_call_count"], 1)
            self.assertEqual(manifest["validation_status"], "pass")

    def test_candidate_study_validation_and_dependency_failures_stop_before_render(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, commit = self.create_repo(root)
            cases = (
                ("study-missing-page", "study brief page sections"),
                ("study-invalid-evidence", "evidence path does not exist"),
                ("study-missing-topic", "cross-page coverage topics: rollback"),
                ("study-failure", "exited 1"),
            )
            for index, (failure, expected_error) in enumerate(cases):
                with self.subTest(failure=failure):
                    fixture = self.write_fixture(root, "node-graph", failure=failure)
                    result, out, manifest = self.run_fixture(
                        root,
                        repo,
                        commit,
                        "node-graph",
                        fixture,
                        f"candidate-failure-{index}",
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(manifest["terminal_status"], "failed")
                    self.assertEqual(manifest["nodes"]["render"]["attempts"], [])
                    self.assertEqual(manifest["metrics"]["generation"]["model_call_count"], 1)
                    if failure == "study-failure":
                        self.assertEqual(
                            manifest["metrics"]["generation"]["failed_terminal_calls"],
                            1,
                        )
                    else:
                        self.assertEqual(
                            manifest["metrics"]["generation"]["failed_terminal_calls"],
                            0,
                        )
                        self.assertGreater(
                            manifest["metrics"]["generation"]["input_tokens"],
                            0,
                        )
                        _, comparison_errors = _read_manifest(
                            out / "run.json", "node-graph"
                        )
                        self.assertFalse(
                            any(
                                "usage does not match raw terminal events" in error
                                or "failed-terminal count is inconsistent" in error
                                for error in comparison_errors
                            ),
                            comparison_errors,
                        )
                    self.assertIn(expected_error, manifest["error"])

    def test_fixture_failures_close_on_missing_usage_and_source_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, commit = self.create_repo(root)
            for failure in ("missing-usage", "mutation", "reader-inconsistent"):
                fixture = self.write_fixture(root, "baseline", failure=failure)
                result, _, manifest = self.run_fixture(
                    root, repo, commit, "baseline", fixture, f"failure-{failure}"
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(manifest["terminal_status"], "failed")
                if failure == "missing-usage":
                    self.assertEqual(manifest["metrics"]["generation"]["failed_terminal_calls"], 1)
                    self.assertIn("terminal usage", manifest["error"])
                else:
                    if failure == "mutation":
                        self.assertTrue(manifest["source"]["source_mutation"])
                    else:
                        self.assertIn("reader_status must be fail", manifest["error"])

    def test_fixture_cache_root_cannot_overlap_source_or_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, commit = self.create_repo(root)
            fixture = self.write_fixture(root, "baseline")
            status_before = subprocess.run(
                ["git", "status", "--porcelain=v1"], cwd=repo, check=True, capture_output=True, text=True
            ).stdout
            for cache_root, output in (
                (repo / "pilot-cache", root / "outside-output"),
                (root / "inside-output" / "cache", root / "inside-output"),
            ):
                with self.subTest(cache_root=cache_root):
                    result = self.run_cli(
                        "--json", "pilot", "run",
                        "--mode", "baseline",
                        "--repo", str(repo),
                        "--commit", commit,
                        "--out", str(output),
                        "--model", "fixture-model",
                        "--reasoning-effort", "high",
                        "--executor-fixture", str(fixture),
                        "--cache-root", str(cache_root),
                    )
                    self.assertEqual(result.returncode, 2)
                    self.assertFalse(cache_root.exists())
            status_after = subprocess.run(
                ["git", "status", "--porcelain=v1"], cwd=repo, check=True, capture_output=True, text=True
            ).stdout
            self.assertEqual(status_after, status_before)

    @staticmethod
    def set_generation_metrics(manifest: dict[str, object], *, input_tokens: int, cached: int, output: int, reasoning: int, wall: int) -> None:
        generation = manifest["metrics"]["generation"]
        generation.update(
            {
                "input_tokens": input_tokens,
                "cached_input_tokens": cached,
                "uncached_input_tokens": input_tokens - cached,
                "output_tokens": output,
                "reasoning_output_tokens": reasoning,
                "total_model_tokens": input_tokens + output,
                "wall_time_ms": wall,
                "failed_terminal_calls": 0,
            }
        )

    def copy_run(self, source: Path, target: Path, *, relabel_live: bool = False) -> dict[str, object]:
        shutil.copytree(source, target)
        manifest_path = target / "run.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["output"]["root"] = str(target.resolve())
        manifest["output"]["wiki_path"] = str((target / "wiki").resolve())
        manifest["output"]["manifest_path"] = str(manifest_path.resolve())
        manifest["output"]["provenance_path"] = str(
            (target / "artifacts" / "execution-provenance.json").resolve()
        )
        if relabel_live:
            manifest["identity"]["execution_evidence"] = "live"
        source_prefix = str(source.resolve())
        target_prefix = str(target.resolve())
        for state in manifest["nodes"].values():
            for attempt in state["attempts"]:
                for field in ("stdout_path", "stderr_path"):
                    value = attempt.get(field)
                    if isinstance(value, str) and value.startswith(source_prefix):
                        attempt[field] = target_prefix + value[len(source_prefix) :]
        return manifest

    def test_comparison_statuses_and_exact_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, commit = self.create_repo(root)
            baseline_fixture = self.write_fixture(root, "baseline")
            candidate_fixture = self.write_fixture(root, "node-graph")
            baseline_result, baseline_out, _ = self.run_fixture(
                root, repo, commit, "baseline", baseline_fixture, "baseline-source"
            )
            candidate_result, candidate_out, candidate_manifest = self.run_fixture(
                root, repo, commit, "node-graph", candidate_fixture, "candidate-source"
            )
            self.assertEqual(baseline_result.returncode, 0)
            self.assertEqual(candidate_result.returncode, 0, str(candidate_manifest["error"]))

            fixture_compare_out = root / "fixture-comparison"
            fixture_compare = self.run_cli(
                "--json", "pilot", "compare",
                "--baseline-run", str(baseline_out / "run.json"),
                "--candidate-run", str(candidate_out / "run.json"),
                "--out", str(fixture_compare_out),
            )
            self.assertEqual(fixture_compare.returncode, 0)
            fixture_report = json.loads(
                (fixture_compare_out / "comparison.json").read_text(encoding="utf-8")
            )
            self.assertEqual(fixture_report["promotion_status"], "inconclusive")
            self.assertFalse(fixture_report["gates"]["live_execution_evidence"]["pass"])
            self.assertTrue(fixture_report["gates"]["model_call_shape"]["pass"])
            self.assertFalse(fixture_report["call_shape"]["candidate"]["repair_occurred"])
            self.assertEqual(
                fixture_report["call_shape"]["candidate"]["generation_model_call_count"],
                2,
            )

            study_path = candidate_out / "artifacts" / "study.md"
            study_bytes = study_path.read_bytes()
            study_path.write_text("tampered durable study\n", encoding="utf-8")
            _, durable_tamper_errors = _read_manifest(
                candidate_out / "run.json", "node-graph"
            )
            self.assertIn(
                "node-graph durable artifact hash is invalid: artifacts/study.md",
                durable_tamper_errors,
            )
            study_path.write_bytes(study_bytes)

            study_evidence_path = (
                candidate_out
                / "artifacts"
                / "node-evidence"
                / "output"
                / "study-attempt-1"
                / "artifacts"
                / "study.md"
            )
            study_evidence_bytes = study_evidence_path.read_bytes()
            study_evidence_path.write_text("tampered evidence copy\n", encoding="utf-8")
            _, evidence_tamper_errors = _read_manifest(
                candidate_out / "run.json", "node-graph"
            )
            self.assertIn(
                "node-graph study output artifact hash is invalid: artifacts/study.md",
                evidence_tamper_errors,
            )
            study_evidence_path.write_bytes(study_evidence_bytes)

            stale_manifest = json.loads(
                (candidate_out / "run.json").read_text(encoding="utf-8")
            )
            stale_manifest["nodes"]["synthesize"] = {
                "node_kind": "agent-synthesize",
                "contract_sha256": "0" * 64,
                "status": "pass",
                "attempts": [],
            }
            (candidate_out / "run.json").write_text(
                json.dumps(stale_manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            _, stale_errors = _read_manifest(candidate_out / "run.json", "node-graph")
            self.assertIn(
                "node-graph manifest contains unexpected nodes: synthesize",
                stale_errors,
            )
            (candidate_out / "run.json").write_text(
                json.dumps(candidate_manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            overlapping_out = baseline_out / "wiki" / "comparison"
            overlapping_result = self.run_cli(
                "--json", "pilot", "compare",
                "--baseline-run", str(baseline_out / "run.json"),
                "--candidate-run", str(candidate_out / "run.json"),
                "--out", str(overlapping_out),
            )
            self.assertEqual(overlapping_result.returncode, 2)
            self.assertIn("disjoint from both input run roots", overlapping_result.stdout)
            self.assertFalse(overlapping_out.exists())

            symlink_out = root / "symlink-comparison"
            symlink_out.mkdir()
            victim = root / "comparison-victim.txt"
            victim.write_text("preserve me\n", encoding="utf-8")
            os.symlink(victim, symlink_out / "comparison.md")
            symlink_result = self.run_cli(
                "--json", "pilot", "compare",
                "--baseline-run", str(baseline_out / "run.json"),
                "--candidate-run", str(candidate_out / "run.json"),
                "--out", str(symlink_out),
            )
            self.assertEqual(symlink_result.returncode, 2)
            self.assertEqual(victim.read_text(encoding="utf-8"), "preserve me\n")

            malformed_dir = root / "malformed-baseline"
            malformed = self.copy_run(baseline_out, malformed_dir)
            malformed["source"] = []
            malformed["output"]["manifest_path"] = "bad\0path"
            (malformed_dir / "run.json").write_text(
                json.dumps(malformed, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            malformed_out = root / "malformed-comparison"
            malformed_result = self.run_cli(
                "--json", "pilot", "compare",
                "--baseline-run", str(malformed_dir / "run.json"),
                "--candidate-run", str(candidate_out / "run.json"),
                "--out", str(malformed_out),
            )
            self.assertEqual(malformed_result.returncode, 0, malformed_result.stderr)
            malformed_report = json.loads(
                (malformed_out / "comparison.json").read_text(encoding="utf-8")
            )
            self.assertEqual(malformed_report["promotion_status"], "inconclusive")
            self.assertIn(
                "baseline source evidence must be an object",
                malformed_report["gates"]["evidence_complete"]["errors"],
            )
            self.assertIn(
                "baseline output path manifest_path is invalid",
                malformed_report["gates"]["evidence_complete"]["errors"],
            )

            tampered_baseline_dir = root / "tampered-baseline"
            tampered_candidate_dir = root / "tampered-candidate"
            tampered_baseline = self.copy_run(
                baseline_out, tampered_baseline_dir, relabel_live=True
            )
            tampered_candidate = self.copy_run(
                candidate_out, tampered_candidate_dir, relabel_live=True
            )
            for manifest, target in (
                (tampered_baseline, tampered_baseline_dir),
                (tampered_candidate, tampered_candidate_dir),
            ):
                provenance_path = target / "artifacts" / "execution-provenance.json"
                provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
                provenance.update(
                    {
                        "execution_evidence": "live",
                        "signature_algorithm": "hmac-sha256-v1",
                        "signing_key_sha256": "0" * 64,
                        "signature": "0" * 64,
                    }
                )
                provenance_path.write_text(
                    json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                manifest["output"]["provenance_sha256"] = hashlib.sha256(
                    provenance_path.read_bytes()
                ).hexdigest()
            (tampered_baseline_dir / "run.json").write_text(
                json.dumps(tampered_baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            (tampered_candidate_dir / "run.json").write_text(
                json.dumps(tampered_candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            tampered_out = root / "tampered-comparison"
            tampered_result = self.run_cli(
                "--json", "pilot", "compare",
                "--baseline-run", str(tampered_baseline_dir / "run.json"),
                "--candidate-run", str(tampered_candidate_dir / "run.json"),
                "--out", str(tampered_out),
            )
            self.assertEqual(tampered_result.returncode, 0)
            tampered_report = json.loads(
                (tampered_out / "comparison.json").read_text(encoding="utf-8")
            )
            self.assertEqual(tampered_report["promotion_status"], "inconclusive")
            self.assertTrue(
                any(
                    "live execution provenance cannot be verified" in error
                    or "live execution signing key does not match" in error
                    for error in tampered_report["gates"]["evidence_complete"]["errors"]
                )
            )

            baseline_template = json.loads((baseline_out / "run.json").read_text(encoding="utf-8"))
            candidate_template = json.loads((candidate_out / "run.json").read_text(encoding="utf-8"))

            cases = (
                ("promote", {}, {}),
                ("revise", {}, {"candidate_input": 901}),
                ("reject", {}, {"candidate_quality_regression": True}),
                ("inconclusive", {}, {"identity_mismatch": True}),
                ("inconclusive", {}, {"model_mismatch": True}),
                ("inconclusive", {}, {"effort_mismatch": True}),
                ("inconclusive", {"baseline_input": 0, "baseline_cached": 0}, {}),
                ("inconclusive", {}, {"reader_failure": True}),
                ("reject", {}, {"validation_failure": True}),
            )
            for index, (expected, baseline_changes, candidate_changes) in enumerate(cases):
                with self.subTest(expected=expected, index=index):
                    baseline = json.loads(json.dumps(baseline_template))
                    candidate = json.loads(json.dumps(candidate_template))
                    baseline["identity"]["execution_evidence"] = "live"
                    candidate["identity"]["execution_evidence"] = "live"
                    baseline["_validated_execution_evidence"] = "live"
                    candidate["_validated_execution_evidence"] = "live"
                    self.set_generation_metrics(
                        baseline,
                        input_tokens=baseline_changes.get("baseline_input", 1100),
                        cached=baseline_changes.get("baseline_cached", 100),
                        output=100,
                        reasoning=100,
                        wall=1000,
                    )
                    self.set_generation_metrics(
                        candidate,
                        input_tokens=candidate_changes.get("candidate_input", 900),
                        cached=100,
                        output=200,
                        reasoning=200,
                        wall=1250,
                    )
                    if candidate_changes.get("candidate_quality_regression"):
                        candidate["reader_evaluation"]["reader_status"] = "fail"
                        candidate["reader_evaluation"]["evidence_fidelity"] = "fail"
                        candidate["reader_evaluation"]["summary"] = "Candidate evidence fidelity regressed."
                    if candidate_changes.get("identity_mismatch"):
                        candidate["identity"]["source_commit"] = "0" * 40
                    if candidate_changes.get("model_mismatch"):
                        candidate["identity"]["model"] = "different-model"
                    if candidate_changes.get("effort_mismatch"):
                        candidate["identity"]["reasoning_effort"] = "low"
                    if candidate_changes.get("reader_failure"):
                        candidate["terminal_status"] = "failed"
                        candidate["reader_evaluation"] = None
                    if candidate_changes.get("validation_failure"):
                        candidate["terminal_status"] = "completed"
                        candidate["validation_status"] = "fail"
                        candidate["nodes"]["validate"]["status"] = "fail"
                        candidate["nodes"]["reader"]["status"] = "pending"
                        candidate["nodes"]["reader"]["attempts"] = []
                        candidate["reader_evaluation"] = None
                        candidate["metrics"]["reader"] = {
                            **TokenUsage.zero().as_dict(),
                            "model_call_count": 0,
                            "failed_terminal_calls": 0,
                            "wall_time_ms": 0,
                        }
                    report = build_decision(
                        baseline,
                        candidate,
                        [],
                        [],
                        baseline_out / "run.json",
                        candidate_out / "run.json",
                    )
                    self.assertEqual(report["promotion_status"], expected)
                    if index == 0:
                        self.assertTrue(report["gates"]["uncached_input_reduction"]["pass"])
                    elif index == 1:
                        self.assertFalse(report["gates"]["uncached_input_reduction"]["pass"])

            boundary_cases = (
                (
                    "uncached_input_reduction",
                    {"input_tokens": 901, "cached": 100, "output": 199, "reasoning": 200, "wall": 1250},
                ),
                (
                    "total_generation_tokens",
                    {"input_tokens": 900, "cached": 100, "output": 301, "reasoning": 200, "wall": 1250},
                ),
                (
                    "wall_time",
                    {"input_tokens": 900, "cached": 100, "output": 200, "reasoning": 200, "wall": 1251},
                ),
            )
            for failed_gate, candidate_values in boundary_cases:
                with self.subTest(failed_gate=failed_gate):
                    baseline = json.loads(json.dumps(baseline_template))
                    candidate = json.loads(json.dumps(candidate_template))
                    baseline["identity"]["execution_evidence"] = "live"
                    candidate["identity"]["execution_evidence"] = "live"
                    baseline["_validated_execution_evidence"] = "live"
                    candidate["_validated_execution_evidence"] = "live"
                    self.set_generation_metrics(
                        baseline,
                        input_tokens=1100,
                        cached=100,
                        output=100,
                        reasoning=100,
                        wall=1000,
                    )
                    self.set_generation_metrics(candidate, **candidate_values)
                    report = build_decision(
                        baseline,
                        candidate,
                        [],
                        [],
                        baseline_out / "run.json",
                        candidate_out / "run.json",
                    )
                    self.assertEqual(report["promotion_status"], "revise")
                    self.assertFalse(report["gates"][failed_gate]["pass"])
                    for gate in {
                        "uncached_input_reduction",
                        "total_generation_tokens",
                        "wall_time",
                    } - {failed_gate}:
                        self.assertTrue(report["gates"][gate]["pass"])


if __name__ == "__main__":
    unittest.main()
