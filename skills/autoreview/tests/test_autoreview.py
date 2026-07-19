from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "autoreview"
SKILL_PATH = Path(__file__).resolve().parents[1] / "SKILL.md"
OPENAI_YAML_PATH = Path(__file__).resolve().parents[1] / "agents" / "openai.yaml"
loader = importlib.machinery.SourceFileLoader("autoreview_script", str(SCRIPT_PATH))
spec = importlib.util.spec_from_loader(loader.name, loader)
assert spec is not None
cli = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = cli
loader.exec_module(cli)


class AutoreviewContractTests(unittest.TestCase):
    def test_skill_reuses_clean_review_for_unchanged_target(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        normalized_skill = " ".join(skill.split())

        self.assertIn("## Review Evidence Freshness", skill)
        self.assertIn("effective patch content and scope are unchanged", normalized_skill)
        self.assertIn("does not invalidate clean review evidence", normalized_skill)
        self.assertIn("A local review may cover the resulting commit", normalized_skill)
        self.assertIn(
            "A commit, push, PR, ship, or final-response boundary alone is not a rerun reason.",
            normalized_skill,
        )

    def test_skill_reruns_only_when_review_freshness_is_invalidated(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        normalized_skill = " ".join(skill.split())

        for invalidation in (
            "changed content or paths alter the effective patch",
            "formatting or generated refreshes alter it",
            "an accepted finding fix changes it",
            "the branch/base/commit scope expands",
            "the previous result or target cannot be verified",
            "the user explicitly asks to review again",
        ):
            self.assertIn(invalidation, normalized_skill)

    def test_discovery_metadata_promotes_review_evidence_reuse(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        metadata = OPENAI_YAML_PATH.read_text(encoding="utf-8")

        self.assertIn("reusing verified clean evidence for an unchanged target", skill)
        self.assertIn("separate read-only Codex execution", skill)
        self.assertIn("separate read-only Codex execution", metadata)
        self.assertIn("reuse verified clean evidence", metadata)
        self.assertIn("unchanged", metadata)
        self.assertNotIn(
            'short_description: "Run structured closeout review before final, commit, PR, or ship."',
            metadata,
        )

    def test_codex_transfer_is_intrinsic_without_a_second_authorization(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        normalized_skill = " ".join(skill.split())

        self.assertIn("## Codex Data Transfer", skill)
        for disclosed_content in (
            "Git status",
            "staged and unstaged diffs",
            "non-ignored untracked file",
            "a NUL byte replaces the contents with an omission marker",
            "all other bytes are decoded as text with replacement characters",
            "--prompt-file",
            "--dataset",
        ):
            self.assertIn(disclosed_content, normalized_skill)
        self.assertIn(
            "This transfer is intrinsic read-only runtime behavior, not a separate permission boundary.",
            normalized_skill,
        )
        self.assertIn(
            "run without a separate authorization question, acknowledgement flag, or user-controlled option",
            normalized_skill,
        )
        self.assertIn(
            "treat that single grant as covering later Auto Review reruns required by a changed target",
            normalized_skill,
        )
        self.assertIn(
            "--no-web-search` disables reviewer web search, not the Codex engine transfer",
            normalized_skill,
        )

    def test_version(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(["--version"])
        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), "autoreview 1.2.0")

    def test_findings_prepare_owns_canonical_ids(self) -> None:
        finding = {
            "title": "Canonical finding",
            "body": "The helper must derive this identifier.",
            "priority": 2,
            "confidence": 0.95,
            "finding_category": "bug",
            "code_location": {"file_path": "src/app.py", "line": 12},
        }
        draft = {
            "schema_version": "1.0.0",
            "template": False,
            "finding_source": "codex-review",
            "findings": [{"finding": finding, "disposition": "accepted", "reason": "Verified."}],
        }
        prepared = cli.prepare_findings(draft)
        self.assertEqual(prepared["findings"][0]["finding_id"], cli.finding_id(finding))
        with self.assertRaisesRegex(cli.AutoreviewError, "invalid shape"):
            cli.prepare_findings({**draft, "finding_id": "a" * 64})

    def test_findings_prepare_is_pre_codex_and_manual_mismatch_still_fails(self) -> None:
        finding = {
            "title": "Canonical finding",
            "body": "The supplied identifier is wrong.",
            "priority": 1,
            "confidence": 1.0,
            "finding_category": "regression",
            "code_location": {"file_path": "app.py", "line": 1},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft_path = root / "draft.json"
            output_path = root / "prepared.json"
            draft_path.write_text(json.dumps({
                "schema_version": "1.0.0",
                "template": False,
                "finding_source": "codex-review",
                "findings": [{"finding": finding, "disposition": "accepted", "reason": "Verified."}],
            }))
            with mock.patch.object(cli, "run_codex", side_effect=AssertionError("Codex must not run")):
                code = cli.main(["--json", "findings", "prepare", "--input", str(draft_path), "--output", str(output_path)])
            self.assertEqual(code, 0)
            prepared = json.loads(output_path.read_text())
            target_path = root / "target.json"
            target_path.write_text("unchanged")
            symlink_path = root / "symlink.json"
            symlink_path.symlink_to(target_path)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(
                    cli.main(["--json", "findings", "template", "--finding-source", "codex-review", "--output", str(symlink_path)]),
                    2,
                )
            self.assertEqual(target_path.read_text(), "unchanged")
            prepared["findings"][0]["finding_id"] = "0" * 64
            manual_path = root / "manual.json"
            manual_path.write_text(json.dumps(prepared))
            prior = {"finding_state": {"open": []}}
            with self.assertRaisesRegex(cli.AutoreviewError, "fingerprint mismatch"):
                cli.load_finding_file(str(manual_path), prior)

    def test_findings_word_in_review_option_does_not_select_prepare_command(self) -> None:
        with mock.patch.object(cli, "run_review", return_value=0) as run_review:
            self.assertEqual(cli.main(["--prompt", "findings"]), 0)
        run_review.assert_called_once()

    def test_incremental_command_surface_is_canonical(self) -> None:
        args = cli.parse_args([
            "--review-phase", "fix-verification",
            "--prior-evidence", "prior.json",
            "--finding-file", "findings.json",
            "--evidence-output", "next.json",
        ])
        self.assertEqual(args.review_phase, "fix-verification")
        self.assertEqual(cli.REVIEW_PHASES, {"full", "fix-verification", "disposition", "terminal-full"})

    def test_evidence_fingerprint_detects_tampering(self) -> None:
        evidence = {
            "schema_version": "1.0.0",
            "review_phase": "full",
            "lineage_id": "a" * 64,
            "parent_evidence_fingerprint": None,
            "repository_id": "b" * 64,
            "target": {
                "mode": "branch", "base_ref": "origin/main", "merge_base_sha": "c" * 40,
                "head_sha": "d" * 40, "target_fingerprint": "e" * 64,
                "changed_files": ["src/app.py"],
            },
            "counts": {"full_reviews": 1, "fix_verifications": 0},
            "finding_state": {"open": [], "resolved": [], "rejected": []},
            "report": {"findings": [], "review_outcome": "pass", "review_explanation": "Clean.", "review_confidence": 1.0},
            "terminal_state": "terminal-clean",
            "metrics": {"prompt_characters": 10, "elapsed_seconds": 1},
        }
        evidence["evidence_fingerprint"] = cli.evidence_fingerprint(evidence)
        self.assertEqual(cli.validate_evidence(evidence), evidence)
        evidence["terminal_state"] = "fix-required"
        with self.assertRaisesRegex(cli.AutoreviewError, "fingerprint mismatch"):
            cli.validate_evidence(evidence)

        evidence["evidence_fingerprint"] = cli.evidence_fingerprint(evidence)
        evidence["counts"]["full_reviews"] = "one"
        evidence["evidence_fingerprint"] = cli.evidence_fingerprint(evidence)
        with self.assertRaisesRegex(cli.AutoreviewError, "counter values"):
            cli.validate_evidence(evidence)

    def test_verification_findings_must_point_to_delta_lines(self) -> None:
        report = {
            "verified_findings": [{
                "finding_id": "a" * 64, "resolution": "resolved",
                "explanation": "The guard now handles the case.", "confidence": 1.0,
            }],
            "findings": [{
                "title": "Outside delta", "body": "This line was not changed.",
                "priority": 2, "confidence": 0.9, "finding_category": "regression",
                "code_location": {"file_path": "src/app.py", "line": 20},
            }],
            "review_outcome": "fail", "review_explanation": "A regression remains.", "review_confidence": 0.9,
        }
        with self.assertRaisesRegex(cli.AutoreviewError, "outside the changed delta lines"):
            cli.validate_verification_report(report, {"a" * 64}, {"src/app.py"}, {"src/app.py": [(4, 8)]})

    def test_branch_evidence_chain_runs_full_delta_and_terminal_full(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
            (repo / "app.py").write_text("value = 1\n")
            subprocess.run(["git", "add", "app.py"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "switch", "-c", "feature"], cwd=repo, check=True, capture_output=True)
            feature_tail = "".join(f"item_{index} = {index}\n" for index in range(700))
            (repo / "app.py").write_text("value = 2\n" + feature_tail)
            subprocess.run(["git", "commit", "-am", "feature"], cwd=repo, check=True, capture_output=True)

            fake = root / "fake-codex"
            fake.write_text(
                "#!/usr/bin/env python3\n"
                "import os, shutil, sys\n"
                "out = sys.argv[sys.argv.index('--output-last-message') + 1]\n"
                "shutil.copyfile(os.environ['FAKE_REPORT'], out)\n"
            )
            fake.chmod(0o755)
            report_path = root / "report.json"
            codex_home = root / "codex-home"
            codex_home.mkdir()

            def invoke(*args: str, expected: int) -> subprocess.CompletedProcess[str]:
                env = {
                    **os.environ,
                    "CODEX_HOME": str(codex_home),
                    "FAKE_REPORT": str(report_path),
                }
                result = subprocess.run(
                    [str(SCRIPT_PATH), "--mode", "branch", "--base", "main", "--codex-bin", str(fake), "--no-web-search", *args],
                    cwd=repo, env=env, text=True, capture_output=True,
                )
                self.assertEqual(result.returncode, expected, result.stderr)
                return result

            full_evidence = root / "full.json"
            full_report = {
                "findings": [{
                    "title": "Reject the changed value", "body": "The changed value is unsupported.",
                    "priority": 2, "confidence": 0.9, "finding_category": "bug",
                    "code_location": {"file_path": "app.py", "line": 1},
                }],
                "review_outcome": "fail", "review_explanation": "One defect.", "review_confidence": 0.9,
            }
            report_path.write_text(json.dumps(full_report))
            invoke("--review-phase", "full", "--evidence-output", str(full_evidence), expected=1)
            first = json.loads(full_evidence.read_text())

            rejected_intake = root / "rejected.json"
            rejected_intake.write_text(json.dumps({
                "finding_source": "autoreview",
                "findings": [{**first["finding_state"]["open"][0], "disposition": "rejected", "reason": "False positive."}],
            }))
            disposition_evidence = root / "disposition.json"
            invoke(
                "--review-phase", "disposition", "--prior-evidence", str(full_evidence),
                "--finding-file", str(rejected_intake), "--evidence-output", str(disposition_evidence), expected=0,
            )
            disposition = json.loads(disposition_evidence.read_text())
            self.assertEqual(disposition["terminal_state"], "terminal-composite-clean")
            self.assertEqual(disposition["counts"], {"full_reviews": 1, "fix_verifications": 0})

            (repo / "app.py").write_text("value = 3\n" + feature_tail)
            subprocess.run(["git", "commit", "-am", "fix"], cwd=repo, check=True, capture_output=True)
            invoke(
                "--review-phase", "disposition", "--prior-evidence", str(full_evidence),
                "--finding-file", str(rejected_intake), "--evidence-output", str(disposition_evidence), expected=2,
            )
            intake = root / "findings.json"
            intake.write_text(json.dumps({
                "finding_source": "autoreview",
                "findings": [{**first["finding_state"]["open"][0], "disposition": "accepted", "reason": "Verified."}],
            }))
            delta_evidence = root / "delta.json"
            identifier = first["finding_state"]["open"][0]["finding_id"]
            report_path.write_text(json.dumps({
                "verified_findings": [{"finding_id": identifier, "resolution": "resolved", "explanation": "Fixed.", "confidence": 1.0}],
                "findings": [], "review_outcome": "pass", "review_explanation": "Resolved.", "review_confidence": 1.0,
            }))
            invoke(
                "--review-phase", "fix-verification", "--prior-evidence", str(full_evidence),
                "--finding-file", str(intake), "--evidence-output", str(delta_evidence), expected=0,
            )
            delta = json.loads(delta_evidence.read_text())
            self.assertEqual(delta["terminal_state"], "verification-clean")
            self.assertEqual(delta["target"]["changed_files"], first["target"]["changed_files"])
            self.assertLessEqual(
                delta["metrics"]["prompt_characters"],
                int(first["metrics"]["prompt_characters"] * 0.35),
            )

            terminal_evidence = root / "terminal.json"
            report_path.write_text(json.dumps({
                "findings": [], "review_outcome": "pass", "review_explanation": "Clean.", "review_confidence": 1.0,
            }))
            invoke(
                "--review-phase", "terminal-full", "--prior-evidence", str(delta_evidence),
                "--evidence-output", str(terminal_evidence), expected=0,
            )
            terminal = json.loads(terminal_evidence.read_text())
            self.assertEqual(terminal["terminal_state"], "terminal-clean")
            self.assertEqual(terminal["counts"], {"full_reviews": 2, "fix_verifications": 1})

    def test_codex_review_intake_cannot_replace_open_autoreview_findings(self) -> None:
        finding = {
            "title": "Open defect", "body": "The defect remains.", "priority": 1,
            "confidence": 1.0, "finding_category": "bug",
            "code_location": {"file_path": "app.py", "line": 1},
        }
        identifier = cli.finding_id(finding)
        prior = {"finding_state": {"open": [{"finding_id": identifier, "finding": finding}]}}
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump({
                "finding_source": "codex-review",
                "findings": [{"finding_id": identifier, "finding": finding, "disposition": "accepted", "reason": "Verified."}],
            }, handle)
            handle.flush()
            with self.assertRaisesRegex(cli.AutoreviewError, "prior AutoReview findings"):
                cli.load_finding_file(handle.name, prior)

    def test_deletion_delta_uses_line_one_of_deleted_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
            (repo / "guard.py").write_text("def guard():\n    return True\n")
            subprocess.run(["git", "add", "guard.py"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "guard"], cwd=repo, check=True, capture_output=True)
            previous = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, text=True, capture_output=True).stdout.strip()
            (repo / "guard.py").write_text("def guard():\n")
            subprocess.run(["git", "commit", "-am", "delete last line"], cwd=repo, check=True, capture_output=True)
            _, paths, ranges = cli.delta_bundle(repo, previous)
            self.assertEqual(paths, {"guard.py"})
            self.assertEqual(ranges["guard.py"], [(1, 1)])
            previous = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, text=True, capture_output=True).stdout.strip()
            (repo / "guard.py").unlink()
            subprocess.run(["git", "add", "-u"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "delete guard"], cwd=repo, check=True, capture_output=True)
            _, paths, ranges = cli.delta_bundle(repo, previous)
            self.assertEqual(paths, {"guard.py"})
            self.assertEqual(ranges["guard.py"], [(1, 1)])

    def test_schema_uses_canonical_option_values(self) -> None:
        self.assertEqual(
            cli.SCHEMA["properties"]["review_outcome"]["enum"],
            ["fail", "pass"],
        )
        finding = cli.SCHEMA["properties"]["findings"]["items"]
        self.assertEqual(finding["properties"]["priority"]["enum"], [0, 1, 2, 3])
        self.assertIn("test-gap", finding["properties"]["finding_category"]["enum"])
        self.assertNotIn("category", finding["properties"])

    def test_canonical_report_validates_and_renders_human_labels(self) -> None:
        report = {
            "findings": [
                {
                    "title": "Handle the edge case",
                    "body": "The changed path fails for an empty value.",
                    "priority": 2,
                    "confidence": 0.9,
                    "finding_category": "test-gap",
                    "code_location": {"file_path": "src/app.py", "line": 7},
                }
            ],
            "review_outcome": "fail",
            "review_explanation": "One actionable finding remains.",
            "review_confidence": 0.95,
        }

        cli.validate_report(report, {"src/app.py"})
        rendered = cli.human_report(report)

        self.assertIn("[P2] Handle the edge case", rendered)
        self.assertIn("overall: patch is incorrect (0.95)", rendered)

    def test_legacy_prose_schema_is_rejected(self) -> None:
        report = {
            "findings": [],
            "overall_correctness": "patch is correct",
            "overall_explanation": "No findings.",
            "overall_confidence": 1.0,
        }

        with self.assertRaises(cli.AutoreviewError):
            cli.validate_report(report, set())

    def test_findings_require_fail_outcome(self) -> None:
        report = {
            "findings": [
                {
                    "title": "Handle the edge case",
                    "body": "The changed path fails for an empty value.",
                    "priority": 2,
                    "confidence": 0.9,
                    "finding_category": "bug",
                    "code_location": {"file_path": "src/app.py", "line": 7},
                }
            ],
            "review_outcome": "pass",
            "review_explanation": "Contradictory outcome.",
            "review_confidence": 0.95,
        }

        with self.assertRaisesRegex(cli.AutoreviewError, "must set review_outcome to fail"):
            cli.validate_report(report, {"src/app.py"})

    def test_environment_status_reports_codex_home_and_temp(self) -> None:
        status = cli.environment_status()
        self.assertIn("codex_home", status)
        self.assertIn("temp", status)
        self.assertTrue(status["network"]["required"])

    def test_write_probe_failure_is_not_reported_as_writable(self) -> None:
        with mock.patch.object(
            cli.tempfile,
            "NamedTemporaryFile",
            side_effect=PermissionError("sandbox denied write"),
        ):
            status = cli.writable_path_status(Path.home())

        self.assertFalse(status["writable"])
        self.assertEqual(status["probe"], "blocked")

    def test_missing_directory_is_unverified_without_being_created(self) -> None:
        with tempfile.TemporaryDirectory() as parent:
            path = Path(parent) / "nested" / "fresh" / "codex-home"

            status = cli.writable_path_status(path)

            self.assertIsNone(status["writable"])
            self.assertEqual(status["probe"], "unverified-missing-directory")
            self.assertFalse(path.exists())

    def test_run_codex_cleans_temp_files_when_execution_raises(self) -> None:
        args = cli.argparse.Namespace(
            codex_bin="codex",
            model=None,
            web_search=False,
            heartbeat_seconds=1,
        )
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(cli.tempfile, "tempdir", directory):
                with mock.patch.object(cli, "ensure_review_environment"):
                    with mock.patch.object(cli, "resolve_command", return_value="codex"):
                        with mock.patch.object(cli, "configured_codex_model", return_value=None):
                            with mock.patch.object(
                                cli,
                                "run_with_heartbeat",
                                side_effect=OSError("launch failed"),
                            ):
                                with self.assertRaises(cli.AutoreviewError) as raised:
                                    cli.run_codex(args, Path(directory), "review")

            self.assertEqual(list(Path(directory).iterdir()), [])

        self.assertEqual(raised.exception.code, "codex-engine-failed")

    def test_run_codex_cleans_temp_files_when_interrupted(self) -> None:
        args = cli.argparse.Namespace(
            codex_bin="codex",
            model=None,
            web_search=False,
            heartbeat_seconds=1,
        )
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(cli.tempfile, "tempdir", directory):
                with mock.patch.object(cli, "ensure_review_environment"):
                    with mock.patch.object(cli, "resolve_command", return_value="codex"):
                        with mock.patch.object(cli, "configured_codex_model", return_value=None):
                            with mock.patch.object(
                                cli,
                                "run_with_heartbeat",
                                side_effect=KeyboardInterrupt,
                            ):
                                with self.assertRaises(KeyboardInterrupt):
                                    cli.run_codex(args, Path(directory), "review")

            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_interrupt_preserves_cleanup_failure_as_note(self) -> None:
        args = cli.argparse.Namespace(
            codex_bin="codex",
            model=None,
            web_search=False,
            heartbeat_seconds=1,
        )
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(cli.tempfile, "tempdir", directory):
                with mock.patch.object(cli, "ensure_review_environment"):
                    with mock.patch.object(cli, "resolve_command", return_value="codex"):
                        with mock.patch.object(cli, "configured_codex_model", return_value=None):
                            with mock.patch.object(
                                cli,
                                "run_with_heartbeat",
                                side_effect=KeyboardInterrupt,
                            ):
                                with mock.patch.object(
                                    cli.Path,
                                    "unlink",
                                    side_effect=PermissionError("ACL denied cleanup"),
                                ):
                                    with self.assertRaises(KeyboardInterrupt) as raised:
                                        cli.run_codex(args, Path(directory), "review")

        notes = getattr(raised.exception, "__notes__", [])
        self.assertTrue(any("ACL denied cleanup" in note for note in notes))

    def test_schema_write_cleanup_failure_is_structured(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(cli.tempfile, "tempdir", directory):
                with mock.patch.object(
                    cli.json,
                    "dump",
                    side_effect=ValueError("schema write failed"),
                ):
                    with mock.patch.object(
                        cli.Path,
                        "unlink",
                        side_effect=PermissionError("ACL denied cleanup"),
                    ):
                        with self.assertRaises(cli.AutoreviewError) as raised:
                            cli.write_json_temp({"type": "object"})

        self.assertEqual(raised.exception.code, "temp-cleanup-failed")
        self.assertIn("ACL denied cleanup", str(raised.exception))

    def test_write_probe_cleanup_failure_is_reported_without_escaping(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(
                cli.Path,
                "unlink",
                side_effect=PermissionError("ACL denied cleanup"),
            ):
                status = cli.writable_path_status(Path(directory))

        self.assertFalse(status["writable"])
        self.assertEqual(status["probe"], "blocked-cleanup-failed")
        self.assertIn("ACL denied cleanup", status["error"])

    def test_unwritable_codex_home_requests_root_reroute(self) -> None:
        status = {
            "codex_home": {"path": "/restricted/.codex", "writable": False},
            "temp": {"path": "/tmp", "writable": True},
        }
        with mock.patch.object(cli, "environment_status", return_value=status):
            with self.assertRaises(cli.AutoreviewError) as raised:
                cli.ensure_review_environment()

        self.assertEqual(raised.exception.code, "codex-home-unwritable")
        self.assertEqual(raised.exception.recovery, "reroute-to-capable-root")

    def test_codex_failure_classification(self) -> None:
        self.assertEqual(
            cli.classify_codex_failure("permission denied opening .codex/state.sqlite"),
            ("codex-home-unwritable", "reroute-to-capable-root"),
        )
        self.assertEqual(
            cli.classify_codex_failure("network is unreachable"),
            ("codex-network-unavailable", "reroute-to-capable-root"),
        )
        self.assertEqual(
            cli.classify_codex_failure("model returned an invalid response"),
            ("codex-engine-failed", "inspect-error"),
        )

    def test_json_error_includes_code_and_recovery(self) -> None:
        stderr = io.StringIO()
        error = cli.AutoreviewError(
            "network unavailable",
            code="codex-network-unavailable",
            recovery="reroute-to-capable-root",
        )
        with mock.patch.object(cli, "run_review", side_effect=error):
            with contextlib.redirect_stderr(stderr):
                code = cli.main(["--json"])

        self.assertEqual(code, 2)
        payload = json.loads(stderr.getvalue())
        self.assertEqual(payload["error_code"], "codex-network-unavailable")
        self.assertEqual(payload["recovery"], "reroute-to-capable-root")
        secret = os.environ.get("OPENAI_API_KEY")
        if secret:
            self.assertNotIn(secret, payload["error"])


if __name__ == "__main__":
    unittest.main()
