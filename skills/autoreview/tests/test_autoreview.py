from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
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
        self.assertEqual(stdout.getvalue().strip(), "autoreview 1.0.0")

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
