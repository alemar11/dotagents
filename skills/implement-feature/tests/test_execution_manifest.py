from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "execution-manifest"
REPLAY_FIXTURE = SKILL_ROOT / "tests" / "fixtures" / "execution-manifest-replay-v1.json"
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
            "schema_version": "1.0.0",
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
            "schema_version": "1.0.0",
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
            request = {"schema_version": "1.0.0", "template": False, "root_task_ref": "task:1", "entries": entries}
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

    def test_templates_and_unknown_fields_are_rejected(self) -> None:
        with self.assertRaisesRegex(cli.ManifestError, "unprepared template"):
            cli.prepare_bundle(cli.bundle_template())
        request = cli.command_template("validation")
        request["unexpected"] = True
        with tempfile.TemporaryDirectory() as directory:
            _, bundle = self.make_bundle(Path(directory))
            with self.assertRaisesRegex(cli.ManifestError, "must contain exactly"):
                cli.prepare_command(request, bundle)

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
                "schema_version": "1.0.0", "template": False,
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

    def test_autoreview_dry_run_adapter_runs_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = self.make_repo(root)
            subprocess.run(["git", "switch", "-qc", "feature"], cwd=repo, check=True)
            (repo / "tracked.txt").write_text("feature\n")
            subprocess.run(["git", "commit", "-qam", "feature"], cwd=repo, check=True)
            _, bundle = self.make_bundle(root)
            request = {
                "schema_version": "1.0.0", "template": False,
                "command_id": "autoreview-dry-run", "operation": "autoreview",
                "owner": "worker", "cwd": str(repo),
                "parameters": {
                    "mode": "branch", "base": "main", "review_phase": "full",
                    "prior_evidence": None, "finding_file": None,
                    "evidence_output": None, "json_output": None, "dry_run": True,
                },
                "dependency_files": [],
                "write_set": {"mode": "none", "allowed_paths": [], "expected_paths": []},
                "expected_exit_codes": [0],
            }
            manifest = cli.prepare_command(request, bundle)
            receipt, exit_code = cli.run_manifest(manifest, str(root / "autoreview-receipt.json"))
            self.assertEqual(exit_code, 0)
            self.assertEqual(receipt["status"], "passed")
            self.assertIn("\"dry_run\": true", Path(receipt["stdout"]["resolved_path"]).read_text())

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
                    "schema_version": "1.0.0",
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


if __name__ == "__main__":
    unittest.main()
