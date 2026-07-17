from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts/orchestrator-cache"
LOADER = importlib.machinery.SourceFileLoader("cache_helper_runtime", str(TOOL))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
CACHE_RUNTIME = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(CACHE_RUNTIME)
CLAIM_TOOL = ROOT / "scripts/orchestrator-claim"
CLAIM_LOADER = importlib.machinery.SourceFileLoader(
    "cache_helper_claim_runtime", str(CLAIM_TOOL)
)
CLAIM_SPEC = importlib.util.spec_from_loader(CLAIM_LOADER.name, CLAIM_LOADER)
assert CLAIM_SPEC is not None
CLAIM_RUNTIME = importlib.util.module_from_spec(CLAIM_SPEC)
CLAIM_LOADER.exec_module(CLAIM_RUNTIME)


def run_cache(
    *args: str, env: dict[str, str], check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([str(TOOL), *args], env=env, text=True, capture_output=True)
    if check and result.returncode:
        raise AssertionError(f"cache helper failed: {result.stdout}\n{result.stderr}")
    return result


def run_claim(
    *args: str, env: dict[str, str], check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [str(CLAIM_TOOL), *args], env=env, text=True, capture_output=True
    )
    if check and result.returncode:
        raise AssertionError(f"claim helper failed: {result.stdout}\n{result.stderr}")
    return result


class OrchestratorCacheHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.cache_root = self.base / ".cache/dotagents/skills/implement-feature"
        self.ledger_root = self.cache_root / "ledgers"
        self.archive_root = self.ledger_root / "archive"
        self.claim_root = self.cache_root / "claims"
        self.ledger_root.mkdir(parents=True)
        self.env = os.environ.copy()
        self.env["HOME"] = str(self.base)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def make_ledger(self, name: str, body: str | None = None) -> Path:
        path = self.ledger_root / f"{name}.md"
        path.write_text(body or f"# {name}\n\nfixture\n")
        return path

    def make_claim(self, root_id: str, ledger: Path) -> Path:
        self.claim_root.mkdir(exist_ok=True)
        (self.claim_root / ".lock").touch(exist_ok=True)
        value = {
            "schema_version": "5.0.0",
            "root_id": root_id,
            "acquisition_nonce": "fixture-nonce",
            "repositories": ["/fixture/repository/.git"],
            "repository_checkouts": [
                {
                    "checkout": "/fixture/repository",
                    "git_common_dir": "/fixture/repository/.git",
                }
            ],
            "sources": ["https://example.test/issues/1"],
            "ledger_ref": str(ledger),
            "opened_at": "2026-07-17T12:00:00Z",
            "heartbeat_at": "2026-07-17T12:00:00Z",
            "takeover_evidence": "none",
            "replaced_root_ids": [],
            "fingerprint": "",
        }
        value["fingerprint"] = CACHE_RUNTIME.claim_fingerprint(value)
        path = self.claim_root / f"{root_id}.json"
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        return path

    def archive_legacy(self, *ledgers: Path, evidence: str = "fixture-cutover") -> dict:
        args = ["--json", "ledger", "archive"]
        for ledger in ledgers:
            args.extend(["--ledger", str(ledger)])
        args.extend(
            [
                "--archive-reason",
                "legacy-cutover",
                "--archive-group",
                "legacy-cutover-2026-07-17",
                "--evidence-ref",
                evidence,
            ]
        )
        return json.loads(run_cache(*args, env=self.env).stdout)

    def rewrite_archived_at(self, entry: Path, value: datetime) -> None:
        metadata_path = entry / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        metadata["archived_at"] = value.astimezone(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        )
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")

    def test_doctor_is_read_only_and_versioned(self) -> None:
        empty = tempfile.TemporaryDirectory()
        self.addCleanup(empty.cleanup)
        env = os.environ.copy()
        env["HOME"] = empty.name
        root = Path(empty.name) / ".cache/dotagents/skills/implement-feature"

        self.assertEqual(run_cache("--version", env=env).stdout.strip(), "1.0.0")
        help_text = run_cache("--help", env=env).stdout
        self.assertIn("doctor", help_text)
        self.assertIn("ledger", help_text)
        self.assertIn("archive", help_text)
        doctor = json.loads(run_cache("--json", "doctor", env=env).stdout)
        self.assertTrue(doctor["ok"])
        self.assertTrue(doctor["offline"])
        self.assertEqual(doctor["archive_count"], 0)
        self.assertFalse(root.exists())

    def test_archive_scan_reports_empty_and_unexpected_directories(self) -> None:
        empty = self.archive_root / "legacy-cutover-2026-07-17" / "empty-entry"
        empty.mkdir(parents=True)
        unexpected = self.archive_root / "unexpected-container"
        unexpected.mkdir()
        (unexpected / "random.bin").write_bytes(b"unexpected")

        doctor = json.loads(run_cache("--json", "doctor", env=self.env).stdout)
        verified = run_cache(
            "--json", "archive", "verify", env=self.env, check=False
        )

        self.assertFalse(doctor["ok"])
        self.assertEqual(len(doctor["invalid"]), 2)
        self.assertEqual(verified.returncode, 5)

    def test_legacy_batch_archive_is_lossless_and_verifiable(self) -> None:
        first = self.make_ledger("first", "# first\nα\n")
        second = self.make_ledger("second", "# second\nβ\n")
        expected = {first.name: first.read_bytes(), second.name: second.read_bytes()}

        result = self.archive_legacy(first, second)

        self.assertEqual(result["archive_reason"], "legacy-cutover")
        self.assertEqual(len(result["archives"]), 2)
        self.assertFalse(first.exists())
        self.assertFalse(second.exists())
        for archive in result["archives"]:
            entry = Path(archive["entry_path"])
            self.assertEqual((entry / "ledger.md").read_bytes(), expected[f"{archive['portfolio_key']}.md"])
            self.assertEqual(archive["archive_group"], "legacy-cutover-2026-07-17")
            self.assertIsNone(archive["root_id"])
        verified = json.loads(
            run_cache("--json", "archive", "verify", env=self.env).stdout
        )
        self.assertEqual(len(verified["archives"]), 2)

    def test_staged_ledger_is_an_independent_durable_snapshot(self) -> None:
        source = self.make_ledger("snapshot", "original\n")
        destination = self.base / "snapshot-copy.md"

        CACHE_RUNTIME.stage_ledger(source, destination)
        source.write_text("changed\n")

        self.assertNotEqual(source.stat().st_ino, destination.stat().st_ino)
        self.assertEqual(destination.read_text(), "original\n")

    def test_terminal_archive_requires_released_unreferenced_ledger(self) -> None:
        ledger = self.make_ledger("terminal")
        claim = self.make_claim("root-a", ledger)
        claim_value = json.loads(claim.read_text())
        blocked = run_cache(
            "--json",
            "ledger",
            "archive",
            "--ledger",
            str(ledger),
            "--archive-reason",
            "terminal",
            "--root-id",
            "root-a",
            "--evidence-ref",
            "fixture-terminal",
            env=self.env,
            check=False,
        )
        self.assertEqual(blocked.returncode, 4)
        self.assertEqual(json.loads(blocked.stdout)["error"]["code"], "state-conflict")
        self.assertTrue(ledger.exists())

        released = json.loads(
            run_claim(
                "--json",
                "claim",
                "release",
                "--root-id",
                "root-a",
                "--expected-fingerprint",
                claim_value["fingerprint"],
                "--release-reason",
                "terminal",
                "--evidence",
                "fixture-terminal",
                env=self.env,
            ).stdout
        )
        self.assertEqual(released["state"], "released")
        archived = json.loads(
            run_cache(
                "--json",
                "ledger",
                "archive",
                "--ledger",
                str(ledger),
                "--archive-reason",
                "terminal",
                "--root-id",
                "root-a",
                "--evidence-ref",
                "fixture-terminal",
                env=self.env,
            ).stdout
        )["archives"][0]
        self.assertEqual(archived["archive_reason"], "terminal")
        self.assertEqual(archived["root_id"], "root-a")

    def test_terminal_archive_rejects_unreleased_unclaimed_ledger(self) -> None:
        ledger = self.make_ledger("terminal-without-receipt")

        blocked = run_cache(
            "--json",
            "ledger",
            "archive",
            "--ledger",
            str(ledger),
            "--archive-reason",
            "terminal",
            "--root-id",
            "root-a",
            "--evidence-ref",
            "fixture-terminal",
            env=self.env,
            check=False,
        )

        self.assertEqual(blocked.returncode, 4)
        self.assertIn("terminal release receipt is required", blocked.stdout)
        self.assertTrue(ledger.exists())

    def test_durable_handoff_receipt_cannot_authorize_terminal_archive(self) -> None:
        ledger = self.make_ledger("durable-handoff")
        claim = self.make_claim("root-a", ledger)
        claim_value = json.loads(claim.read_text())
        run_claim(
            "--json",
            "claim",
            "release",
            "--root-id",
            "root-a",
            "--expected-fingerprint",
            claim_value["fingerprint"],
            "--release-reason",
            "durable-handoff",
            "--evidence",
            "fixture-handoff",
            env=self.env,
        )

        blocked = run_cache(
            "--json",
            "ledger",
            "archive",
            "--ledger",
            str(ledger),
            "--archive-reason",
            "terminal",
            "--root-id",
            "root-a",
            "--evidence-ref",
            "fixture-handoff",
            env=self.env,
            check=False,
        )

        self.assertEqual(blocked.returncode, 4)
        self.assertTrue(ledger.exists())

    def test_terminal_archive_rejects_same_root_with_different_active_ledger(self) -> None:
        requested = self.make_ledger("terminal-requested")
        active = self.make_ledger("terminal-active")
        self.make_claim("root-a", active)

        blocked = run_cache(
            "--json",
            "ledger",
            "archive",
            "--ledger",
            str(requested),
            "--archive-reason",
            "terminal",
            "--root-id",
            "root-a",
            "--evidence-ref",
            "fixture-terminal",
            env=self.env,
            check=False,
        )

        self.assertEqual(blocked.returncode, 4)
        self.assertIn("still has active claim ownership", blocked.stdout)
        self.assertTrue(requested.exists())

    def test_archive_is_idempotent_for_the_same_evidence(self) -> None:
        ledger = self.make_ledger("idempotent")
        first = self.archive_legacy(ledger, evidence="same-cutover")["archives"][0]
        second = self.archive_legacy(ledger, evidence="same-cutover")["archives"][0]
        self.assertEqual(first["archive_id"], second["archive_id"])

    def test_archive_rejects_outside_paths_symlinks_and_malformed_claim_state(self) -> None:
        outside = self.base / "outside.md"
        outside.write_text("outside\n")
        rejected = run_cache(
            "--json",
            "ledger",
            "archive",
            "--ledger",
            str(outside),
            "--archive-reason",
            "legacy-cutover",
            "--archive-group",
            "legacy-cutover-2026-07-17",
            "--evidence-ref",
            "fixture",
            env=self.env,
            check=False,
        )
        self.assertEqual(rejected.returncode, 2)

        symlink = self.ledger_root / "symlink.md"
        symlink.symlink_to(outside)
        rejected = run_cache(
            "--json",
            "ledger",
            "archive",
            "--ledger",
            str(symlink),
            "--archive-reason",
            "legacy-cutover",
            "--archive-group",
            "legacy-cutover-2026-07-17",
            "--evidence-ref",
            "fixture",
            env=self.env,
            check=False,
        )
        self.assertEqual(rejected.returncode, 2)

        real = self.make_ledger("same-directory-target")
        same_directory_symlink = self.ledger_root / "same-directory-symlink.md"
        same_directory_symlink.symlink_to(real)
        rejected = run_cache(
            "--json",
            "ledger",
            "archive",
            "--ledger",
            str(same_directory_symlink),
            "--archive-reason",
            "legacy-cutover",
            "--archive-group",
            "legacy-cutover-2026-07-17",
            "--evidence-ref",
            "fixture",
            env=self.env,
            check=False,
        )
        self.assertEqual(rejected.returncode, 2)
        self.assertTrue(real.exists())
        self.assertTrue(same_directory_symlink.is_symlink())

        ledger = self.make_ledger("claim-blocked")
        self.claim_root.mkdir(exist_ok=True)
        (self.claim_root / ".lock").touch()
        (self.claim_root / "broken.json").write_text("not-json\n")
        rejected = run_cache(
            "--json",
            "ledger",
            "archive",
            "--ledger",
            str(ledger),
            "--archive-reason",
            "legacy-cutover",
            "--archive-group",
            "legacy-cutover-2026-07-17",
            "--evidence-ref",
            "fixture",
            env=self.env,
            check=False,
        )
        self.assertEqual(rejected.returncode, 4)
        self.assertTrue(ledger.exists())

    def test_batch_failure_restores_sources_and_removes_committed_entries(self) -> None:
        first = self.make_ledger("rollback-a")
        second = self.make_ledger("rollback-b")
        args = argparse.Namespace(
            ledger=[str(first), str(second)],
            archive_reason="legacy-cutover",
            evidence_ref="fixture-rollback",
            root_id=None,
            archive_group="legacy-cutover-2026-07-17",
        )
        original_replace = CACHE_RUNTIME.os.replace
        calls = 0

        def fail_second(source: Path, destination: Path) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected rename failure")
            original_replace(source, destination)

        with mock.patch.dict(os.environ, {"HOME": str(self.base)}), mock.patch.object(
            CACHE_RUNTIME.os, "replace", side_effect=fail_second
        ):
            with self.assertRaises(OSError):
                CACHE_RUNTIME.archive_ledgers(args)

        self.assertTrue(first.exists())
        self.assertTrue(second.exists())
        self.assertEqual(CACHE_RUNTIME.scan_archives(verify_hash=True)["valid"], [])

    def test_strict_ttl_includes_legacy_and_exact_180_day_boundary(self) -> None:
        ledger = self.make_ledger("ttl")
        archive = self.archive_legacy(ledger)["archives"][0]
        entry = Path(archive["entry_path"])
        fixed_now = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)
        self.rewrite_archived_at(entry, fixed_now - timedelta(days=180))
        args = argparse.Namespace(older_than_days=180, apply=False)
        with mock.patch.dict(os.environ, {"HOME": str(self.base)}), mock.patch.object(
            CACHE_RUNTIME, "utc_now", return_value=fixed_now
        ):
            preview = CACHE_RUNTIME.prune_archives(args)
        self.assertEqual(preview["eligible"], [archive["archive_id"]])
        self.assertEqual(preview["deleted"], [])

        args.apply = True
        with mock.patch.dict(os.environ, {"HOME": str(self.base)}), mock.patch.object(
            CACHE_RUNTIME, "utc_now", return_value=fixed_now
        ):
            applied = CACHE_RUNTIME.prune_archives(args)
        self.assertEqual(applied["deleted"], [archive["archive_id"]])
        self.assertFalse(entry.exists())

    def test_younger_archive_is_not_pruned(self) -> None:
        ledger = self.make_ledger("young")
        archive = self.archive_legacy(ledger)["archives"][0]
        entry = Path(archive["entry_path"])
        fixed_now = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)
        self.rewrite_archived_at(entry, fixed_now - timedelta(days=179, hours=23))
        args = argparse.Namespace(older_than_days=180, apply=True)
        with mock.patch.dict(os.environ, {"HOME": str(self.base)}), mock.patch.object(
            CACHE_RUNTIME, "utc_now", return_value=fixed_now
        ):
            result = CACHE_RUNTIME.prune_archives(args)
        self.assertEqual(result["eligible"], [])
        self.assertTrue(entry.exists())

    def test_checksum_mismatch_is_protected_while_valid_peer_is_deleted(self) -> None:
        bad_ledger = self.make_ledger("bad")
        good_ledger = self.make_ledger("good")
        archives = self.archive_legacy(bad_ledger, good_ledger)["archives"]
        fixed_now = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)
        entries = {item["portfolio_key"]: Path(item["entry_path"]) for item in archives}
        for entry in entries.values():
            self.rewrite_archived_at(entry, fixed_now - timedelta(days=181))
        (entries["bad"] / "ledger.md").write_text("tampered\n")

        args = argparse.Namespace(older_than_days=180, apply=True)
        with mock.patch.dict(os.environ, {"HOME": str(self.base)}), mock.patch.object(
            CACHE_RUNTIME, "utc_now", return_value=fixed_now
        ):
            result = CACHE_RUNTIME.prune_archives(args)
        self.assertTrue(entries["bad"].exists())
        self.assertFalse(entries["good"].exists())
        self.assertEqual(len(result["deleted"]), 1)
        self.assertTrue(result["protected"])

    def test_preserved_trash_is_not_reported_as_deleted(self) -> None:
        ledger = self.make_ledger("preserved-trash-report")
        archive = self.archive_legacy(ledger)["archives"][0]
        entry = Path(archive["entry_path"])
        fixed_now = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)
        self.rewrite_archived_at(entry, fixed_now - timedelta(days=181))
        args = argparse.Namespace(older_than_days=180, apply=True)

        with mock.patch.dict(os.environ, {"HOME": str(self.base)}), mock.patch.object(
            CACHE_RUNTIME, "utc_now", return_value=fixed_now
        ), mock.patch.object(CACHE_RUNTIME, "cleanup_trash", return_value=0):
            result = CACHE_RUNTIME.prune_archives(args)

        self.assertEqual(result["deleted"], [])
        self.assertTrue(
            any(
                item.get("error") == "interrupted trash preserved"
                for item in result["protected"]
            )
        )
        self.assertTrue((self.archive_root / ".trash").is_dir())

    def test_claim_reference_protects_archive_by_original_ledger_path(self) -> None:
        ledger = self.make_ledger("claimed-archive")
        archive = self.archive_legacy(ledger)["archives"][0]
        entry = Path(archive["entry_path"])
        fixed_now = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)
        self.rewrite_archived_at(entry, fixed_now - timedelta(days=181))
        self.make_claim("root-a", ledger)

        args = argparse.Namespace(older_than_days=180, apply=True)
        with mock.patch.dict(os.environ, {"HOME": str(self.base)}), mock.patch.object(
            CACHE_RUNTIME, "utc_now", return_value=fixed_now
        ):
            result = CACHE_RUNTIME.prune_archives(args)

        self.assertEqual(result["deleted"], [])
        self.assertTrue(entry.exists())
        self.assertEqual(result["protected"][0]["error"], "referenced by claim state")

    def test_unknown_claim_schema_blocks_archive_and_prune_cleanup(self) -> None:
        ledger = self.make_ledger("unknown-claim")
        self.claim_root.mkdir(exist_ok=True)
        (self.claim_root / ".lock").touch()
        (self.claim_root / "root-a.json").write_text(
            json.dumps({"schema_version": "99.0.0", "ledger_ref": str(ledger)}) + "\n"
        )
        trash = self.archive_root / ".trash" / "fixture-trash"
        trash.mkdir(parents=True)
        (trash / "ledger.md").write_text("old\n")
        (trash / "metadata.json").write_text("{}\n")

        archive = run_cache(
            "--json",
            "ledger",
            "archive",
            "--ledger",
            str(ledger),
            "--archive-reason",
            "legacy-cutover",
            "--archive-group",
            "legacy-cutover-2026-07-17",
            "--evidence-ref",
            "fixture",
            env=self.env,
            check=False,
        )
        self.assertEqual(archive.returncode, 4)
        result = json.loads(
            run_cache(
                "--json",
                "archive",
                "prune",
                "--older-than-days",
                "180",
                "--apply",
                env=self.env,
            ).stdout
        )
        self.assertTrue(trash.exists())
        self.assertTrue(result["warnings"])

    def test_actual_takeover_transaction_is_accepted_as_safe_claim_state(self) -> None:
        replaced_ledger = self.make_ledger("replaced")
        candidate_ledger = self.make_ledger("candidate")
        replaced_path = self.make_claim("root-a", replaced_ledger)
        replaced = json.loads(replaced_path.read_text())
        replaced_path.unlink()
        transaction_id = "a" * 32
        adoption = {
            "root_id": "root-a",
            "claim_fingerprint": replaced["fingerprint"],
            "task_termination_evidence": "fixture-termination",
            "specs": [
                {
                    "source_spec_ref": replaced["sources"][0],
                    "task_state": "no-task",
                    "task_ref": "none",
                    "task_model": "gpt-5.6-sol",
                    "task_thinking": "high",
                    "thinking_reason": "default-high-fixture",
                    "goal_evidence_ref": "none",
                    "managed_checkouts": [],
                    "evidence_ref": "fixture-no-task",
                }
            ],
        }
        evidence_item = {
            "claim_snapshot": replaced,
            "task_termination_evidence": "fixture-termination",
            "task_adoption": adoption,
        }
        takeover_evidence = {
            "stale_claim_takeover_permission": "granted-by-authorized-user",
            "takeover_reason": "verified-stale",
            "evidence": "fixture-takeover",
            "transaction_id": transaction_id,
            "replaced_claims": [evidence_item],
        }
        takeover_evidence["evidence_fingerprint"] = (
            CLAIM_RUNTIME.takeover_evidence_fingerprint(takeover_evidence)
        )
        candidate = dict(replaced)
        candidate.update(
            {
                "root_id": "root-b",
                "acquisition_nonce": "candidate-nonce",
                "ledger_ref": str(candidate_ledger),
                "takeover_evidence": takeover_evidence,
                "replaced_root_ids": ["root-a"],
            }
        )
        candidate["fingerprint"] = CLAIM_RUNTIME.fingerprint(candidate)
        transaction = CLAIM_RUNTIME.build_takeover_transaction(candidate, [replaced])
        transaction_path = self.claim_root / "root-b.takeover"
        CLAIM_RUNTIME.validate_takeover_transaction(transaction, transaction_path)
        transaction_path.write_text(
            json.dumps(transaction, indent=2, sort_keys=True) + "\n"
        )

        doctor = json.loads(run_cache("--json", "doctor", env=self.env).stdout)

        self.assertTrue(doctor["ok"])
        self.assertEqual(doctor["takeover_files"], [str(transaction_path)])

    def test_apply_resumes_safe_interrupted_trash_cleanup(self) -> None:
        ledger = self.make_ledger("interrupted-prune")
        archive = self.archive_legacy(ledger)["archives"][0]
        entry = Path(archive["entry_path"])
        self.rewrite_archived_at(
            entry, datetime.now(timezone.utc) - timedelta(days=181)
        )
        trash_root = self.archive_root / ".trash"
        trash_root.mkdir()
        trash = trash_root / f"{archive['archive_id']}--{'a' * 16}"
        os.replace(entry, trash)
        result = json.loads(
            run_cache(
                "--json",
                "archive",
                "prune",
                "--older-than-days",
                "180",
                "--apply",
                env=self.env,
            ).stdout
        )
        self.assertFalse(trash.exists())
        self.assertGreater(result["reclaimed_bytes"], 0)

    def test_malformed_interrupted_trash_is_preserved(self) -> None:
        trash = self.archive_root / ".trash" / f"fixture--{'a' * 16}"
        trash.mkdir(parents=True)
        (trash / "ledger.md").write_text("old\n")
        (trash / "metadata.json").write_text("{}\n")

        result = json.loads(
            run_cache(
                "--json",
                "archive",
                "prune",
                "--older-than-days",
                "180",
                "--apply",
                env=self.env,
            ).stdout
        )

        self.assertTrue(trash.exists())
        self.assertTrue(any("trash entry preserved" in item for item in result["warnings"]))

    def test_claim_referenced_interrupted_trash_is_preserved(self) -> None:
        ledger = self.make_ledger("claimed-interrupted-prune")
        archive = self.archive_legacy(ledger)["archives"][0]
        entry = Path(archive["entry_path"])
        self.rewrite_archived_at(
            entry, datetime.now(timezone.utc) - timedelta(days=181)
        )
        trash_root = self.archive_root / ".trash"
        trash_root.mkdir()
        trash = trash_root / f"{archive['archive_id']}--{'b' * 16}"
        os.replace(entry, trash)
        self.make_claim("root-a", ledger)

        result = json.loads(
            run_cache(
                "--json",
                "archive",
                "prune",
                "--older-than-days",
                "180",
                "--apply",
                env=self.env,
            ).stdout
        )

        self.assertTrue(trash.exists())
        self.assertTrue(any("referenced by claim state" in item for item in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
