from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "execution-manifest"
REPLAY_FIXTURE = SKILL_ROOT / "tests" / "fixtures" / "execution-manifest-replay-v4.json"
loader = importlib.machinery.SourceFileLoader("execution_manifest_script", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
assert spec is not None
cli = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = cli
loader.exec_module(cli)


class ExecutionManifestTests(unittest.TestCase):
    def write_json(self, path: Path, value: object) -> None:
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")

    def make_bundle(self, root: Path) -> tuple[Path, dict[str, object]]:
        source = root / "source.md"
        source.write_bytes("Café\n".encode())
        request = {
            "schema_version": "4.0.0",
            "template": False,
            "root_task_ref": "task:test",
            "entries": [
                {
                    "entry_id": "source-one",
                    "kind": "feature-spec",
                    "source_ref": "example/repo#1",
                    "snapshot_path": str(source),
                }
            ],
        }
        bundle = cli.prepare_bundle(request)
        path = root / "bundle.json"
        self.write_json(path, bundle)
        return path, bundle

    def make_repo(self, root: Path) -> Path:
        repo = root / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
        (repo / "tracked.txt").write_text("base\n")
        subprocess.run(["git", "add", "tracked.txt"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True)
        return repo

    def validation_request(
        self,
        repo: Path,
        argv: list[str],
        *,
        allowed: list[str] | None = None,
        expected: list[str] | None = None,
        dependencies: list[str] | None = None,
    ) -> dict[str, object]:
        allowed = allowed or []
        expected = expected or []
        return {
            "schema_version": "4.0.0",
            "template": False,
            "command_id": "focused-validation",
            "operation": "validation",
            "owner": "worker",
            "cwd": str(repo),
            "parameters": {"argv": argv},
            "dependency_files": dependencies or [],
            "write_set": {
                "mode": "declared" if allowed or expected else "none",
                "allowed_paths": allowed,
                "expected_paths": expected,
            },
            "expected_exit_codes": [0],
        }

    def baseline_request(self, repo: Path, argv: list[str]) -> dict[str, object]:
        return {
            "schema_version": "4.0.0",
            "template": False,
            "command_id": "baseline-validation",
            "operation": "baseline-validation",
            "owner": "worker",
            "cwd": str(repo),
            "parameters": {"argv": argv, "execution_scope_fingerprint": "a" * 64},
            "dependency_files": [],
            "write_set": {"mode": "none", "allowed_paths": [], "expected_paths": []},
            "expected_exit_codes": [0],
        }

    def make_prettier(self, root: Path, body: str) -> Path:
        tool = root / "prettier"
        tool.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if '--version' in sys.argv:\n"
            "    print('prettier 99.0.0')\n"
            "    raise SystemExit(0)\n"
            + body
        )
        tool.chmod(0o755)
        return tool

    def short_policy(
        self,
        *,
        timeout: float = 0.5,
        stdout_limit: int = 8192,
        stderr_limit: int = 8192,
    ) -> dict[str, float | int]:
        return {
            "timeout_seconds": timeout,
            "heartbeat_seconds": 0.05,
            "term_grace_seconds": 0.1,
            "cleanup_seconds": 0.3,
            "stdout_limit_bytes": stdout_limit,
            "stderr_limit_bytes": stderr_limit,
        }

    def prepare_short_validation(
        self,
        root: Path,
        repo: Path,
        argv: list[str],
        policy: dict[str, float | int],
    ) -> dict[str, object]:
        _, bundle = self.make_bundle(root)
        with mock.patch.dict(cli.EXECUTION_POLICIES, {"validation": policy}):
            return cli.prepare_command(self.validation_request(repo, argv), bundle)

    def test_bundle_hash_is_deterministic_and_reconstructable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            empty = root / "empty"
            unicode_file = root / "unicode"
            empty.write_bytes(b"")
            unicode_file.write_bytes("λ\n".encode())
            entries = [
                {"entry_id": "unicode", "kind": "issue", "source_ref": "issue:2", "snapshot_path": str(unicode_file)},
                {"entry_id": "empty", "kind": "spec", "source_ref": "spec:1", "snapshot_path": str(empty)},
            ]
            request = {"schema_version": "4.0.0", "template": False, "root_task_ref": "task:1", "entries": entries}
            first = cli.prepare_bundle(request)
            second = cli.prepare_bundle({**request, "entries": list(reversed(entries))})
            self.assertEqual(first["bundle_sha256"], second["bundle_sha256"])
            rows = [{key: row[key] for key in ("entry_id", "kind", "source_ref", "byte_length", "content_sha256")} for row in first["entries"]]
            payload = b"implement-feature-bundle\0sha256-frame-v1\0" + len(rows).to_bytes(8, "big")
            for row in rows:
                frame = cli.canonical_bytes(row)
                payload += len(frame).to_bytes(8, "big") + frame
            self.assertEqual(cli.digest(payload), first["bundle_sha256"])
            unicode_file.write_bytes("μ\n".encode())
            self.assertNotEqual(first["bundle_sha256"], cli.prepare_bundle(request)["bundle_sha256"])

    def test_seven_file_prettier_baseline_is_canonical_and_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            debt_paths = [f"frontend/baseline-{index}.tsx" for index in range(1, 8)]
            for path in debt_paths:
                target = repo / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(f"const value{path[-5]}=1\n")
            subprocess.run(["git", "add", "frontend"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "baseline debt"], cwd=repo, check=True)
            tool = self.make_prettier(
                root,
                "paths = " + repr(list(reversed(debt_paths)) + [debt_paths[0]]) + "\n"
                "for path in paths:\n"
                "    print('[warn] ' + path)\n"
                "print('[warn] Code style issues found in 7 files.')\n"
                "raise SystemExit(1)\n",
            )
            _, bundle = self.make_bundle(root)
            manifest = cli.prepare_command(self.baseline_request(repo, [str(tool), "--write", "."]), bundle)
            self.assertIn("--check", manifest["argv"])
            self.assertNotIn("--write", manifest["argv"])
            receipt, exit_code = cli.run_manifest(manifest, str(root / "baseline-receipt.json"))
            self.assertEqual(exit_code, 0)
            observation = receipt["baseline_observation"]
            self.assertEqual(observation["result"], "unchanged-debt-candidate")
            self.assertEqual([row["path"] for row in observation["diagnostics"]], debt_paths)
            self.assertEqual(len({row["content_sha256"] for row in observation["diagnostics"]}), 7)
            self.assertTrue(observation["checkout_identity"]["status_clean"])

    def test_baseline_rejects_unsafe_command_and_checkout_toctou(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            _, bundle = self.make_bundle(root)
            with self.assertRaisesRegex(cli.ManifestError, "no proven read-only"):
                cli.prepare_command(self.baseline_request(repo, [sys.executable, "-c", "print('x')"]), bundle)
            tool = self.make_prettier(root, "raise SystemExit(0)\n")
            manifest = cli.prepare_command(self.baseline_request(repo, [str(tool), "--check", "."]), bundle)
            (repo / "tracked.txt").write_text("drift\n")
            with self.assertRaises(cli.ManifestError) as error:
                cli.run_manifest(manifest, str(root / "stale-receipt.json"))
            self.assertIn(error.exception.code, {"baseline-checkout-dirty", "manifest-stale"})

    def test_baseline_detects_git_visible_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            _, bundle = self.make_bundle(root)
            tool = self.make_prettier(
                root,
                "from pathlib import Path\nPath('tracked.txt').write_text('mutated\\n')\nraise SystemExit(0)\n",
            )
            manifest = cli.prepare_command(self.baseline_request(repo, [str(tool), "--check", "."]), bundle)
            with self.assertRaises(cli.ManifestError) as error:
                cli.run_manifest(manifest, str(root / "mutation-receipt.json"))
            self.assertEqual(error.exception.code, "baseline-checkout-dirty")

    def test_templates_and_unknown_fields_are_rejected(self) -> None:
        with self.assertRaisesRegex(cli.ManifestError, "unprepared template"):
            cli.prepare_bundle(cli.bundle_template())
        request = cli.command_template("validation")
        request["unexpected"] = True
        with tempfile.TemporaryDirectory() as directory:
            _, bundle = self.make_bundle(Path(directory))
            with self.assertRaisesRegex(cli.ManifestError, "must contain exactly"):
                cli.prepare_command(request, bundle)

    def test_v3_manifest_contract_is_rejected_without_migration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.md"
            source.write_text("immutable\n")
            request = {
                "schema_version": "3.0.0",
                "template": False,
                "root_task_ref": "task:legacy",
                "entries": [{
                    "entry_id": "legacy",
                    "kind": "feature-spec",
                    "source_ref": "legacy:1",
                    "snapshot_path": str(source),
                }],
            }
            with self.assertRaises(cli.ManifestError):
                cli.prepare_bundle(request)
            self.assertEqual(source.read_text(), "immutable\n")

    def test_validation_requires_literal_non_shell_argv(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            _, bundle = self.make_bundle(root)
            invalid = [
                "python3 -m unittest",
                ["FOO=bar", "python3"],
                ["sh", "-c", "true"],
                ["python3", "-m", "unittest", "|", "tee", "out"],
                ["python3", "$(whoami)"],
                ["python3", ">", "out"],
            ]
            for argv in invalid:
                request = self.validation_request(repo, argv)  # type: ignore[arg-type]
                with self.subTest(argv=argv), self.assertRaises(cli.ManifestError):
                    cli.prepare_command(request, bundle)

    def test_manifest_validation_rejects_noncanonical_contract_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            _, bundle = self.make_bundle(root)
            manifest = cli.prepare_command(self.validation_request(repo, [sys.executable, "--version"]), bundle)
            invalid_cases = [
                ("expected_exit_codes", [0, 0]),
                ("expected_exit_codes", ["0"]),
                ("outputs", [1]),
            ]
            for field, value in invalid_cases:
                candidate = json.loads(json.dumps(manifest))
                candidate[field] = value
                candidate["manifest_sha256"] = cli.manifest_fingerprint(candidate)
                with self.subTest(field=field, value=value), self.assertRaises(cli.ManifestError):
                    cli.validate_manifest(candidate)

    def test_run_binds_cwd_argv_writes_and_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            _, bundle = self.make_bundle(root)
            argv = [
                sys.executable,
                "-c",
                "from pathlib import Path\nPath('proof.txt').write_text(str(Path.cwd()))",
            ]
            request = self.validation_request(repo, argv, allowed=["proof.txt"], expected=["proof.txt"])
            manifest = cli.prepare_command(request, bundle)
            self.assertEqual(manifest["bundle_sha256"], bundle["bundle_sha256"])
            self.assertEqual(manifest["gate_fingerprint"], cli.gate_fingerprint(manifest))
            manifest_path = root / "command.json"
            self.write_json(manifest_path, manifest)
            receipt_path = root / "receipt.json"
            receipt, exit_code = cli.run_manifest(manifest, str(receipt_path))
            self.assertEqual(exit_code, 0)
            self.assertEqual(receipt["status"], "passed")
            self.assertEqual((repo / "proof.txt").read_text(), str(repo.resolve()))
            validated = cli.validate_receipt(json.loads(receipt_path.read_text()), manifest)
            self.assertEqual(validated["argv_fingerprint"], manifest["argv_fingerprint"])
            reused = cli.reuse_receipt(manifest, validated)
            self.assertEqual(reused["status"], "reused")
            self.assertEqual(reused["prior_receipt_sha256"], validated["receipt_sha256"])
            tampered = json.loads(json.dumps(validated))
            tampered["status"] = "failed"
            with self.assertRaisesRegex(cli.ManifestError, "fingerprint"):
                cli.reuse_receipt(manifest, tampered)
            malformed = json.loads(json.dumps(validated))
            malformed["writes"]["changed_paths"] = ["proof.txt", "proof.txt"]
            malformed["receipt_sha256"] = cli.fingerprint({key: item for key, item in malformed.items() if key != "receipt_sha256"})
            with self.assertRaises(cli.ManifestError):
                cli.reuse_receipt(manifest, malformed)

    def test_undeclared_write_fails_and_dependency_drift_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            _, bundle = self.make_bundle(root)
            dependency = root / "validator.py"
            dependency.write_text("print('ok')\n")
            argv = [sys.executable, "-c", "from pathlib import Path\nPath('surprise.txt').write_text('x')"]
            request = self.validation_request(repo, argv, dependencies=[str(dependency)])
            manifest = cli.prepare_command(request, bundle)
            self.assertEqual(manifest["dependencies"][0]["source_kind"], "configured-install")
            receipt, exit_code = cli.run_manifest(manifest, str(root / "unexpected.json"))
            self.assertEqual(exit_code, 4)
            self.assertEqual(receipt["writes"]["unexpected_paths"], ["surprise.txt"])
            dependency.write_text("print('changed')\n")
            with self.assertRaisesRegex(cli.ManifestError, "pinned file changed"):
                cli.run_manifest(manifest, str(root / "stale.json"))

    def test_bundle_source_drift_blocks_command_preparation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            _, bundle = self.make_bundle(root)
            (root / "source.md").write_text("changed\n")
            with self.assertRaisesRegex(cli.ManifestError, "bundle source changed"):
                cli.prepare_command(self.validation_request(repo, [sys.executable, "--version"]), bundle)

    def test_tool_refresh_rejects_changed_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            _, bundle = self.make_bundle(root)
            manifest = cli.prepare_command(self.validation_request(repo, [sys.executable, "--version"]), bundle)
            refreshed = cli.refresh_tools(manifest)
            self.assertEqual(refreshed["tools"][0]["sha256"], manifest["tools"][0]["sha256"])
            tampered = json.loads(json.dumps(manifest))
            tampered["tools"][0]["sha256"] = "0" * 64
            tampered["gate_fingerprint"] = cli.gate_fingerprint(tampered)
            tampered["manifest_sha256"] = cli.manifest_fingerprint(tampered)
            with self.assertRaisesRegex(cli.ManifestError, "identity changed"):
                cli.refresh_tools(tampered)

    def test_delivery_preflight_adapter_runs_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, bundle = self.make_bundle(root)
            packet = root / "delivery.json"
            self.write_json(packet, {
                "schema_version": "1.0.0",
                "deliveries": [{"delivery_key": "app", "github_repository": "example/repo", "target_branch": "feature"}],
            })
            fake_gh = root / "gh"
            fake_gh.write_text(
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                "if '--version' in sys.argv: print('gh version test'); raise SystemExit(0)\n"
                "endpoint = sys.argv[2]\n"
                "if endpoint == 'repos/example/repo': value = {'default_branch':'main','permissions':{'push':True,'pull':True},'viewerPermission':'WRITE'}\n"
                "elif endpoint.endswith('/branches/main/protection'): value = {}\n"
                "elif '/commits/main' in endpoint: value = ['a' * 40]\n"
                "else: value = []\n"
                "print(json.dumps(value))\n"
            )
            fake_gh.chmod(0o755)
            request = {
                "schema_version": "4.0.0", "template": False,
                "command_id": "delivery-preflight", "operation": "delivery-preflight",
                "owner": "root", "cwd": None, "parameters": {"input": str(packet)},
                "dependency_files": [],
                "write_set": {"mode": "none", "allowed_paths": [], "expected_paths": []},
                "expected_exit_codes": [0],
            }
            path_value = str(root) + os.pathsep + os.environ["PATH"]
            with mock.patch.dict(os.environ, {"PATH": path_value}):
                manifest = cli.prepare_command(request, bundle)
                receipt, exit_code = cli.run_manifest(manifest, str(root / "preflight-receipt.json"))
            self.assertEqual(exit_code, 0)
            self.assertEqual(receipt["status"], "passed")
            self.assertIn("\"ci_availability\":\"not-configured\"", Path(receipt["stdout"]["resolved_path"]).read_text())

    def test_autoreview_adapter_uses_only_protocol_reservation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            subprocess.run(["git", "switch", "-qc", "feature"], cwd=repo, check=True)
            (repo / "tracked.txt").write_text("feature\n")
            subprocess.run(["git", "commit", "-qam", "feature"], cwd=repo, check=True)
            (root / "autoreview-next.json").write_text("{}\n")
            _, bundle = self.make_bundle(root)
            request = {
                "schema_version": "4.0.0", "template": False,
                "command_id": "autoreview-dry-run", "operation": "autoreview",
                "owner": "worker", "cwd": str(repo),
                "parameters": {
                    "reservation_file": str(root / "autoreview-next.json"),
                    "attempt_file": str(root / "attempt.jsonl"),
                    "candidate_output": str(root / "candidate.json"),
                    "operation_output": str(root / "operation.json"),
                    "dry_run": True,
                },
                "dependency_files": [],
                "write_set": {"mode": "none", "allowed_paths": [], "expected_paths": []},
                "expected_exit_codes": [0],
            }
            manifest = cli.prepare_command(request, bundle)
            self.assertIn("--reservation-file", manifest["argv"])
            self.assertNotIn("--mode", manifest["argv"])
            self.assertNotIn("--review-phase", manifest["argv"])

    def test_cli_fixture_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.md"
            source.write_text("spec\n")
            request = root / "request.json"
            bundle = root / "bundle.json"
            self.write_json(
                request,
                {
                    "schema_version": "4.0.0",
                    "template": False,
                    "root_task_ref": "task:fixture",
                    "entries": [{"entry_id": "source", "kind": "spec", "source_ref": "spec:1", "snapshot_path": str(source)}],
                },
            )
            result = subprocess.run(
                [str(SCRIPT), "--json", "bundle", "prepare", "--input", str(request), "--output", str(bundle)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["ok"])
            self.assertEqual(json.loads(bundle.read_text())["bundle_recipe"], "sha256-frame-v1")

    def test_replay_fixture_prepares_runs_and_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            source = root / "source.md"
            source.write_text("fixture\n")
            rendered = REPLAY_FIXTURE.read_text().replace("{ROOT}", str(root)).replace("{PYTHON}", sys.executable)
            fixture = json.loads(rendered)
            bundle = cli.prepare_bundle(fixture["bundle_request"])
            manifest = cli.prepare_command(fixture["validation_request"], bundle)
            receipt_path = root / "receipt.json"
            receipt, exit_code = cli.run_manifest(manifest, str(receipt_path))
            self.assertEqual(exit_code, 0)
            self.assertEqual(bundle["bundle_recipe"], fixture["expected"]["bundle_recipe"])
            self.assertEqual(manifest["operation"], fixture["expected"]["operation"])
            self.assertEqual(receipt["status"], fixture["expected"]["receipt_status"])
            self.assertEqual(cli.validate_receipt(json.loads(receipt_path.read_text()), manifest), receipt)

    def test_two_phase_launcher_never_executes_before_durable_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            marker = repo / "executed"
            policy = self.short_policy()
            manifest = self.prepare_short_validation(
                root,
                repo,
                [sys.executable, "-c", "from pathlib import Path\nPath('executed').write_text('yes')"],
                policy,
            )
            with mock.patch.dict(cli.EXECUTION_POLICIES, {"validation": policy}):
                with self.assertRaisesRegex(RuntimeError, "controller-death"):
                    cli.run_manifest(
                        manifest,
                        str(root / "receipt.json"),
                        phase_hook=lambda phase, _: (_ for _ in ()).throw(RuntimeError("controller-death"))
                        if phase == "launch-authorized"
                        else None,
                    )
            self.assertFalse(marker.exists())
            attempt = root / "receipt.json.attempt.jsonl"
            with mock.patch.dict(cli.EXECUTION_POLICIES, {"validation": policy}):
                status = cli.attempt_status(manifest, str(attempt))
            self.assertTrue(status["launch_may_have_occurred"])
            self.assertFalse(status["relaunch_allowed"])
            self.assertEqual(status["status"], "interrupted")

    def test_timeout_kills_hung_child_and_grandchild_that_ignore_term(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            policy = self.short_policy(timeout=0.25)
            code = (
                "import signal,subprocess,sys,time\n"
                "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
                "subprocess.Popen([sys.executable,'-c','import signal,time\\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\\ntime.sleep(30)'])\n"
                "time.sleep(30)\n"
            )
            manifest = self.prepare_short_validation(root, repo, [sys.executable, "-c", code], policy)
            with mock.patch.dict(cli.EXECUTION_POLICIES, {"validation": policy}):
                receipt, exit_code = cli.run_manifest(manifest, str(root / "timeout.json"))
            self.assertEqual(exit_code, 4)
            self.assertEqual(receipt["status"], "timed-out")
            self.assertIsNotNone(receipt["attempt"]["cleanup"]["kill_sent_at"])
            self.assertEqual(receipt["attempt"]["cleanup"]["remaining_pids"], [])
            transitions = [json.loads(line)["transition"] for line in Path(receipt["attempt"]["attempt_file"]).read_text().splitlines()]
            self.assertLess(transitions.index("timeout-committed"), transitions.index("terminal-observed"))

    def test_controller_death_after_release_never_relaunches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            marker = repo / "released"
            policy = self.short_policy(timeout=1)
            manifest = self.prepare_short_validation(
                root,
                repo,
                [sys.executable, "-c", "from pathlib import Path\nPath('released').write_text('yes')"],
                policy,
            )
            with mock.patch.dict(cli.EXECUTION_POLICIES, {"validation": policy}):
                with self.assertRaisesRegex(RuntimeError, "after-release"):
                    cli.run_manifest(
                        manifest,
                        str(root / "released.json"),
                        phase_hook=lambda phase, _: (_ for _ in ()).throw(RuntimeError("after-release"))
                        if phase == "launch-released"
                        else None,
                    )
            deadline = time.monotonic() + 2
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue(marker.exists())
            attempt_path = root / "released.json.attempt.jsonl"
            events = [json.loads(line) for line in attempt_path.read_text().splitlines()]
            with mock.patch.dict(cli.EXECUTION_POLICIES, {"validation": policy}):
                recovered = cli.recover_attempt(manifest, str(attempt_path))
            self.assertEqual(recovered["status"], "interrupted")
            self.assertFalse(recovered["relaunch_allowed"])
            os.waitpid(events[-1]["process"]["pid"], 0)
            with mock.patch.dict(cli.EXECUTION_POLICIES, {"validation": policy}):
                status = cli.attempt_status(manifest, str(attempt_path))
            self.assertTrue(status["launch_may_have_occurred"])
            self.assertFalse(status["relaunch_allowed"])
            self.assertEqual(status["status"], "interrupted")

    def test_output_flood_is_capped_and_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            policy = self.short_policy(stdout_limit=1024, stderr_limit=1024)
            manifest = self.prepare_short_validation(
                root,
                repo,
                [sys.executable, "-c", "import os\nos.write(1, b'x' * 65536)"],
                policy,
            )
            with mock.patch.dict(cli.EXECUTION_POLICIES, {"validation": policy}):
                receipt, exit_code = cli.run_manifest(manifest, str(root / "flood.json"))
            self.assertEqual(exit_code, 4)
            self.assertEqual(receipt["status"], "output-limit", receipt["attempt"]["cleanup"])
            capture = receipt["output_capture"]["stdout"]
            self.assertEqual(capture["stored_bytes"], 1024)
            self.assertGreater(capture["observed_bytes"], 1024)
            self.assertTrue(capture["truncated"])
            self.assertEqual(Path(receipt["stdout"]["resolved_path"]).stat().st_size, 1024)

    def test_quiet_process_is_healthy_but_does_not_extend_deadline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            policy = self.short_policy(timeout=0.6)
            manifest = self.prepare_short_validation(
                root,
                repo,
                [sys.executable, "-c", "import time\ntime.sleep(0.15)"],
                policy,
            )
            with mock.patch.dict(cli.EXECUTION_POLICIES, {"validation": policy}):
                receipt, exit_code = cli.run_manifest(manifest, str(root / "quiet.json"))
            self.assertEqual(exit_code, 0)
            self.assertEqual(receipt["status"], "passed")
            self.assertEqual(receipt["output_capture"]["stdout"]["observed_bytes"], 0)

    def test_wall_clock_jump_does_not_change_monotonic_enforcement(self) -> None:
        class JumpingDateTime(datetime):
            calls = 0

            @classmethod
            def now(cls, tz: timezone | None = None) -> datetime:
                cls.calls += 1
                base = datetime(2026, 1, 1, tzinfo=timezone.utc)
                return base + timedelta(days=cls.calls * 30)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            policy = self.short_policy(timeout=0.5)
            manifest = self.prepare_short_validation(
                root,
                repo,
                [sys.executable, "-c", "import time\ntime.sleep(0.1)"],
                policy,
            )
            with mock.patch.dict(cli.EXECUTION_POLICIES, {"validation": policy}), mock.patch.object(cli, "datetime", JumpingDateTime):
                receipt, exit_code = cli.run_manifest(manifest, str(root / "wall-clock.json"))
            self.assertEqual(exit_code, 0)
            self.assertEqual(receipt["status"], "passed")

    def test_attempt_replay_and_pid_identity_mismatch_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            _, bundle = self.make_bundle(root)
            manifest = cli.prepare_command(self.validation_request(repo, [sys.executable, "--version"]), bundle)
            receipt_path = root / "once.json"
            cli.run_manifest(manifest, str(receipt_path))
            with self.assertRaises(cli.ManifestError) as replay:
                cli.run_manifest(manifest, str(receipt_path))
            self.assertEqual(replay.exception.code, "attempt-already-exists")
            with mock.patch.object(cli, "owned_processes", return_value=([999999], [], {999999: "f" * 64})), mock.patch.object(cli, "process_start_identity", return_value="0" * 64):
                with self.assertRaises(cli.ManifestError) as mismatch:
                    cli.signal_owned_group(999999, {999999: "f" * 64}, signal.SIGTERM)
            self.assertEqual(mismatch.exception.code, "process-identity-unverifiable")

    def test_claim_loss_cancellation_requires_current_typed_ledger_authority(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            _, bundle = self.make_bundle(root)
            manifest = cli.prepare_command(self.validation_request(repo, [sys.executable, "--version"]), bundle)
            attempt_id = "a" * 32
            attempt_path = root / "cancel.attempt.jsonl"
            cli.append_attempt(
                attempt_path,
                {
                    "schema_version": "4.0.0",
                    "attempt_id": attempt_id,
                    "manifest_sha256": manifest["manifest_sha256"],
                    "command_id": manifest["command_id"],
                    "controller_session_id": "b" * 32,
                    "boot_identity": "test:boot",
                    "transition": "prepared",
                },
                create=True,
            )
            state_fingerprint = "c" * 64
            ledger = {
                "schema_version": "13.0.0",
                "content_fingerprint": state_fingerprint,
                "tasks": [{
                    "deliveries": [{
                        "command_attempts": [{
                            "attempt_id": attempt_id,
                            "manifest_sha256": manifest["manifest_sha256"],
                            "state": "cancellation-authorized",
                            "cancellation_reason": "claim-lost",
                        }]
                    }]
                }],
            }
            ledger_path = root / "ledger.json"
            self.write_json(ledger_path, ledger)
            result = cli.authorize_cancellation(
                manifest,
                str(attempt_path),
                str(root / "receipt.json"),
                str(ledger_path),
                "claim-lost",
                state_fingerprint,
            )
            self.assertEqual(result["reason"], "claim-lost")
            with self.assertRaises(cli.ManifestError) as stale:
                cli.authorize_cancellation(
                    manifest,
                    str(attempt_path),
                    str(root / "other.json"),
                    str(ledger_path),
                    "claim-lost",
                    "d" * 64,
                )
            self.assertEqual(stale.exception.code, "cancellation-unauthorized")

    def test_group_escape_is_detected_without_claiming_complete_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            policy = self.short_policy(timeout=1)
            escaped_pid = root / "escaped.pid"
            code = (
                "import subprocess,sys,time\n"
                f"child=subprocess.Popen([sys.executable,'-c',\"import os,time\\nos.setsid()\\nopen({str(escaped_pid)!r},'w').write(str(os.getpid()))\\ntime.sleep(30)\"])\n"
                "time.sleep(30)\n"
            )
            manifest = self.prepare_short_validation(root, repo, [sys.executable, "-c", code], policy)
            with mock.patch.dict(cli.EXECUTION_POLICIES, {"validation": policy}):
                receipt, exit_code = cli.run_manifest(manifest, str(root / "escape.json"))
            self.assertEqual(exit_code, 4)
            self.assertEqual(receipt["status"], "cleanup-failed")
            self.assertIsNotNone(receipt["attempt"]["cleanup"]["error_code"])
            if escaped_pid.exists():
                os.kill(int(escaped_pid.read_text()), signal.SIGKILL)


if __name__ == "__main__":
    unittest.main()
