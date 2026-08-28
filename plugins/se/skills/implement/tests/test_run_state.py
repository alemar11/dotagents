import json
import os
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/run-state"


class RunStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def invoke(self, db: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [str(SCRIPT), "--json", "--db", str(db), *args],
            text=True, capture_output=True, check=False,
        )
        if check and result.returncode:
            self.fail(result.stdout or result.stderr)
        return result

    @staticmethod
    def payload(result: subprocess.CompletedProcess[str]) -> dict:
        return json.loads(result.stdout)

    def test_version_and_absent_doctor_are_read_only(self) -> None:
        version = subprocess.run(
            [str(SCRIPT), "--version"], text=True, capture_output=True, check=True
        )
        self.assertEqual(version.stdout.strip(), "3.13.3")
        db = self.root / "nested/run-state.sqlite3"
        result = self.payload(self.invoke(db, "doctor"))["result"]
        self.assertEqual(result["database_state"], "absent")
        self.assertFalse(db.parent.exists())

    def test_doctor_does_not_create_sidecars_and_escapes_custom_path(self) -> None:
        parent = self.root / "question?mark"
        db = parent / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        for suffix in ("-wal", "-shm"):
            sidecar = Path(f"{db}{suffix}")
            if sidecar.exists():
                sidecar.unlink()
        before = sorted(path.name for path in parent.iterdir())
        result = self.payload(self.invoke(db, "doctor"))["result"]
        after = sorted(path.name for path in parent.iterdir())
        self.assertTrue(result["ready"])
        self.assertEqual(before, ["run-state.sqlite3"])
        self.assertEqual(after, before)

    def test_prepare_uses_wal_and_exact_schema(self) -> None:
        db = self.root / "run-state.sqlite3"
        result = self.payload(self.invoke(db, "state", "prepare"))["result"]
        self.assertEqual(result["journal_mode"], "wal")
        self.assertEqual(os.stat(db).st_mode & 0o777, 0o600)
        with sqlite3.connect(db) as connection:
            tables = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            self.assertEqual(
                tables,
                {"runtime_metadata", "runs", "feature_claims", "assignments", "operations"},
            )
            self.assertEqual(connection.execute("PRAGMA journal_mode").fetchone()[0], "wal")

    def test_run_assignment_and_operation_lifecycle(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        started = self.payload(self.invoke(
            db, "run", "start", "--run-id", "run-1",
            "--orchestrator-task-id", "task-root",
        ))
        self.assertEqual(started["result"]["run"]["revision"], 0)

        features = self.root / "features.json"
        features.write_text(json.dumps({"feature_refs": ["owner/repo#10"]}), encoding="utf-8")
        claimed = self.payload(self.invoke(
            db, "feature", "claim", "--run-id", "run-1", "--input", str(features)
        ))
        self.assertEqual(claimed["result"]["feature_claims"][0]["status"], "active")

        source = self.root / "assignment.json"
        source.write_text(json.dumps({
            "feature_ref": "owner/repo#10",
            "repository_identity": "github:owner/repo", "status": "active",
            "checkpoint": "worker-bootstrap", "worker_task_id": "feature-worker-1",
            "implementation_worktree": "/tmp/worktree-a",
        }), encoding="utf-8")
        created = self.payload(self.invoke(
            db, "assignment", "checkpoint", "--run-id", "run-1",
            "--assignment-id", "assignment-1", "--expected-revision", "0",
            "--input", str(source),
        ))
        self.assertTrue(created["result"]["created"])

        source.write_text(json.dumps({
            "status": "active", "checkpoint": "native-review",
            "candidate_sha": "a" * 40,
        }), encoding="utf-8")
        updated = self.payload(self.invoke(
            db, "assignment", "checkpoint", "--run-id", "run-1",
            "--assignment-id", "assignment-1", "--expected-revision", "0",
            "--input", str(source),
        ))
        self.assertEqual(updated["result"]["assignment"]["revision"], 1)

        source.write_text(json.dumps({
            "status": "delivery-pending", "checkpoint": "candidate-published",
        }), encoding="utf-8")
        published = self.payload(self.invoke(
            db, "assignment", "checkpoint", "--run-id", "run-1",
            "--assignment-id", "assignment-1", "--expected-revision", "1",
            "--input", str(source),
        ))
        self.assertEqual(published["result"]["assignment"]["revision"], 2)
        self.assertEqual(
            published["result"]["assignment"]["status"], "delivery-pending"
        )
        self.assertEqual(
            published["result"]["assignment"]["checkpoint"], "candidate-published"
        )

        begun = self.payload(self.invoke(
            db, "operation", "begin", "--run-id", "run-1",
            "--assignment-id", "assignment-1", "--action", "publish-pr",
            "--subject-id", "candidate-a",
        ))
        operation_id = begun["result"]["operation"]["operation_id"]
        duplicate = self.payload(self.invoke(
            db, "operation", "begin", "--run-id", "run-1",
            "--assignment-id", "assignment-1", "--action", "publish-pr",
            "--subject-id", "candidate-a",
        ))
        self.assertFalse(duplicate["result"]["created"])
        self.assertEqual(duplicate["result"]["operation"]["operation_id"], operation_id)
        finished = self.payload(self.invoke(
            db, "operation", "finish", "--operation-id", operation_id,
            "--status", "applied", "--receipt-ref", "receipt-1",
            "--readback-ref", "readback-1",
        ))
        self.assertEqual(finished["result"]["operation"]["status"], "applied")
        shown = self.payload(self.invoke(db, "run", "show", "--run-id", "run-1"))
        self.assertEqual(len(shown["result"]["feature_claims"]), 1)
        self.assertEqual(len(shown["result"]["assignments"]), 1)
        self.assertEqual(len(shown["result"]["operations"]), 1)

    def test_revision_conflict_and_explicit_reset(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        self.invoke(db, "run", "start", "--run-id", "run-1",
                    "--orchestrator-task-id", "task-root")
        checkpoint = ("run", "checkpoint", "--run-id", "run-1",
                      "--expected-revision", "0", "--status", "active",
                      "--checkpoint", "schedule")
        self.invoke(db, *checkpoint)
        conflict = self.invoke(db, *checkpoint, check=False)
        self.assertEqual(self.payload(conflict)["error"]["code"], "revision-conflict")
        rejected = self.invoke(db, "state", "reset", "--confirm", "wrong", check=False)
        self.assertEqual(
            self.payload(rejected)["error"]["code"], "reset-confirmation-required"
        )
        reset = self.payload(self.invoke(
            db, "state", "reset", "--confirm", "drop-and-recreate"
        ))
        self.assertEqual(reset["result"]["journal_mode"], "wal")
        missing = self.invoke(db, "run", "show", "--run-id", "run-1", check=False)
        self.assertEqual(self.payload(missing)["error"]["code"], "run-not-found")

    def test_capabilities_publish_the_complete_state_registry(self) -> None:
        db = self.root / "run-state.sqlite3"
        capabilities = self.payload(self.invoke(db, "capabilities"))["result"]
        registry = capabilities["state_registry"]
        self.assertEqual(capabilities["feature_commands"], ["claim", "recover", "release"])
        self.assertEqual(
            capabilities["claim_recovery"],
            {
                "dispositions": ["retire", "supersede"],
                "required_claim_fields": [
                    "authority_ref", "expected_orchestrator_task_id",
                    "expected_revision", "expected_run_id", "feature_ref",
                    "ownership_observation_ref",
                ],
                "audit_actions": [
                    "feature-claim-retire", "feature-claim-supersede"
                ],
                "atomic": True,
                "compare_and_swap": "feature-claim-revision",
            },
        )
        self.assertEqual(
            registry["run_pairs"],
            [
                {"status": "active", "checkpoint": "prepare-run"},
                {"status": "active", "checkpoint": "release-claims"},
                {"status": "active", "checkpoint": "schedule"},
                {"status": "blocked", "checkpoint": "blocked"},
                {"status": "complete", "checkpoint": "complete"},
                {"status": "deferred", "checkpoint": "deferred"},
            ],
        )
        self.assertEqual(
            registry["feature_claim_statuses"], ["active", "released"]
        )
        self.assertEqual(
            registry["operation_statuses"],
            ["applied", "blocked", "not-applied", "pending", "unknown"],
        )
        self.assertIn(
            {"status": "delivery-pending", "checkpoint": "candidate-published"},
            registry["assignment_pairs"],
        )
        self.assertIn(
            {"status": "delivery-ready", "checkpoint": "final-verify"},
            registry["assignment_pairs"],
        )

    def test_rejects_undocumented_run_and_assignment_state_pairs(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        self.invoke(
            db, "run", "start", "--run-id", "run-1",
            "--orchestrator-task-id", "task-root",
        )
        invalid_run = self.invoke(
            db, "run", "checkpoint", "--run-id", "run-1",
            "--expected-revision", "0", "--status", "reviewing",
            "--checkpoint", "native-review", check=False,
        )
        self.assertEqual(self.payload(invalid_run)["error"]["code"], "invalid-input")

        features = self.root / "features.json"
        features.write_text(
            json.dumps({"feature_refs": ["owner/repo#10"]}), encoding="utf-8"
        )
        self.invoke(
            db, "feature", "claim", "--run-id", "run-1", "--input", str(features)
        )
        assignment = self.root / "assignment.json"
        assignment.write_text(json.dumps({
            "feature_ref": "owner/repo#10",
            "repository_identity": "github:owner/repo",
            "status": "reviewing",
            "checkpoint": "native-review",
        }), encoding="utf-8")
        invalid_assignment = self.invoke(
            db, "assignment", "checkpoint", "--run-id", "run-1",
            "--assignment-id", "assignment-1", "--expected-revision", "0",
            "--input", str(assignment), check=False,
        )
        self.assertEqual(
            self.payload(invalid_assignment)["error"]["code"], "invalid-input"
        )

    def test_plan_question_assignment_cannot_release_claims(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        self.invoke(db, "run", "start", "--run-id", "run-1",
                    "--orchestrator-task-id", "task-root")
        features = self.root / "features.json"
        features.write_text(json.dumps({
            "feature_refs": ["owner/repo#10"]
        }), encoding="utf-8")
        self.invoke(db, "feature", "claim", "--run-id", "run-1",
                    "--input", str(features))
        assignment = self.root / "assignment.json"
        assignment.write_text(json.dumps({
            "feature_ref": "owner/repo#10",
            "repository_identity": "github:owner/repo",
            "status": "deferred", "checkpoint": "plan-question",
            "worker_task_id": "feature-worker-1",
        }), encoding="utf-8")
        self.invoke(db, "assignment", "checkpoint", "--run-id", "run-1",
                    "--assignment-id", "feature-10", "--expected-revision", "0",
                    "--input", str(assignment))
        self.invoke(db, "run", "checkpoint", "--run-id", "run-1",
                    "--expected-revision", "0", "--status", "active",
                    "--checkpoint", "release-claims")
        release = self.root / "release.json"
        release.write_text(json.dumps({"feature_claims": [{
            "feature_ref": "owner/repo#10", "expected_revision": 0
        }]}), encoding="utf-8")
        rejected = self.invoke(
            db, "feature", "release", "--run-id", "run-1",
            "--input", str(release), check=False,
        )
        self.assertEqual(
            self.payload(rejected)["error"]["code"], "assignments-not-ready"
        )

    def test_rejects_unsafe_database_name(self) -> None:
        result = self.invoke(self.root / "other.sqlite3", "doctor", check=False)
        self.assertEqual(self.payload(result)["error"]["code"], "unsafe-database-path")
        target = self.root / "target.sqlite3"
        target.touch()
        link = self.root / "run-state.sqlite3"
        link.symlink_to(target)
        linked = self.invoke(link, "doctor", check=False)
        self.assertEqual(self.payload(linked)["error"]["code"], "unsafe-database-file")

        directory = self.root / "ledger-target"
        directory.mkdir()
        linked_directory = self.root / "ledger-link"
        linked_directory.symlink_to(directory, target_is_directory=True)
        parent_link = self.invoke(
            linked_directory / "run-state.sqlite3", "state", "prepare", check=False
        )
        self.assertEqual(
            self.payload(parent_link)["error"]["code"], "unsafe-database-path"
        )

        blocker = self.root / "not-a-directory"
        blocker.write_text("x", encoding="utf-8")
        blocked_parent = self.invoke(
            blocker / "run-state.sqlite3", "state", "prepare", check=False
        )
        self.assertEqual(
            self.payload(blocked_parent)["error"]["code"], "state-prepare-error"
        )

    def test_empty_run_cannot_complete_and_release_input_is_typed(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        self.invoke(
            db, "run", "start", "--run-id", "run-1",
            "--orchestrator-task-id", "task-root",
        )
        complete = self.invoke(
            db, "run", "checkpoint", "--run-id", "run-1",
            "--expected-revision", "0", "--status", "complete",
            "--checkpoint", "complete", check=False,
        )
        self.assertEqual(
            self.payload(complete)["error"]["code"], "missing-feature-claims"
        )

        release = self.root / "release.json"
        release.write_text(json.dumps({
            "feature_claims": [{"feature_ref": 123, "expected_revision": 0}]
        }), encoding="utf-8")
        malformed = self.invoke(
            db, "feature", "release", "--run-id", "run-1",
            "--input", str(release), check=False,
        )
        self.assertEqual(self.payload(malformed)["error"]["code"], "invalid-input")

    def test_detects_journal_drift_without_repairing_it(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        with sqlite3.connect(db) as connection:
            self.assertEqual(connection.execute("PRAGMA journal_mode=DELETE").fetchone()[0], "delete")
        Path(f"{db}-wal").unlink(missing_ok=True)
        Path(f"{db}-shm").unlink(missing_ok=True)
        doctor = self.invoke(db, "doctor", check=False)
        self.assertEqual(self.payload(doctor)["error"]["code"], "invalid-state-journal")
        with sqlite3.connect(db) as connection:
            self.assertEqual(connection.execute("PRAGMA journal_mode").fetchone()[0], "delete")
        repaired = self.payload(self.invoke(db, "state", "prepare"))["result"]
        self.assertEqual(repaired["journal_mode"], "wal")

    def test_detects_schema_definition_drift(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        with sqlite3.connect(db) as connection:
            connection.execute("DROP INDEX feature_claims_run_idx")
            connection.execute(
                "CREATE INDEX feature_claims_run_idx ON feature_claims(status, run_id)"
            )
        doctor = self.invoke(db, "doctor", check=False)
        self.assertEqual(self.payload(doctor)["error"]["code"], "invalid-state-schema")

    def test_doctor_rejects_undocumented_persisted_state(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        self.invoke(
            db, "run", "start", "--run-id", "run-1",
            "--orchestrator-task-id", "task-root",
        )
        with sqlite3.connect(db) as connection:
            connection.execute(
                "UPDATE runs SET status='reviewing', checkpoint='native-review' "
                "WHERE run_id='run-1'"
            )
        doctor = self.invoke(db, "doctor", check=False)
        self.assertEqual(
            self.payload(doctor)["error"]["code"], "invalid-state-data"
        )

    def test_doctor_rejects_permission_and_artifact_drift(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        db.chmod(0o644)
        unsafe = self.invoke(db, "doctor", check=False)
        self.assertEqual(
            self.payload(unsafe)["error"]["code"], "unsafe-database-permissions"
        )
        self.invoke(db, "state", "prepare")
        with sqlite3.connect(db) as connection:
            connection.execute(
                "UPDATE runtime_metadata SET runtime_artifact_sha256='wrong'"
            )
        mismatch = self.invoke(db, "doctor", check=False)
        self.assertEqual(
            self.payload(mismatch)["error"]["code"], "runtime-artifact-mismatch"
        )
        self.invoke(db, "state", "prepare")
        ready = self.payload(self.invoke(db, "doctor"))["result"]
        self.assertTrue(ready["artifact_matches"])

    def test_rejects_ledger_from_pre_handoff_runtime_contract(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        with sqlite3.connect(db) as connection:
            connection.execute(
                "UPDATE runtime_metadata SET runtime_contract_version='3.1.1'"
            )
        rejected = self.invoke(db, "doctor", check=False)
        self.assertEqual(
            self.payload(rejected)["error"]["code"],
            "incompatible-runtime-contract",
        )
        self.invoke(
            db, "state", "reset", "--confirm", "drop-and-recreate"
        )
        prepared = self.payload(self.invoke(db, "state", "prepare"))["result"]
        self.assertEqual(prepared["schema_version"], 3)
        self.assertTrue(self.payload(self.invoke(db, "doctor"))["result"]["ready"])

    def test_feature_claim_is_atomic_and_excludes_another_orchestrator(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        for run_id in ("run-1", "run-2"):
            self.invoke(db, "run", "start", "--run-id", run_id,
                        "--orchestrator-task-id", f"task-{run_id}")
        source = self.root / "features.json"
        source.write_text(json.dumps({
            "feature_refs": ["owner/repo#10", "owner/repo#20"]
        }), encoding="utf-8")
        self.invoke(db, "feature", "claim", "--run-id", "run-1", "--input", str(source))
        conflict = self.invoke(
            db, "feature", "claim", "--run-id", "run-2", "--input", str(source),
            check=False,
        )
        self.assertEqual(self.payload(conflict)["error"]["code"], "feature-already-claimed")
        with sqlite3.connect(db) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT count(*) FROM feature_claims WHERE run_id='run-2'"
                ).fetchone()[0], 0,
            )
        assignment = self.root / "assignment.json"
        for number in (10, 20):
            assignment.write_text(json.dumps({
                "feature_ref": f"owner/repo#{number}",
                "repository_identity": "github:owner/repo",
                "status": "delivery-ready", "checkpoint": "final-verify",
            }), encoding="utf-8")
            self.invoke(
                db, "assignment", "checkpoint", "--run-id", "run-1",
                "--assignment-id", f"assignment-{number}", "--expected-revision", "0",
                "--input", str(assignment),
            )
        self.invoke(
            db, "run", "checkpoint", "--run-id", "run-1",
            "--expected-revision", "0", "--status", "active",
            "--checkpoint", "release-claims",
        )
        release = self.root / "release.json"
        release.write_text(json.dumps({"feature_claims": [
            {"feature_ref": "owner/repo#10", "expected_revision": 0},
            {"feature_ref": "owner/repo#20", "expected_revision": 0},
        ]}), encoding="utf-8")
        subset = self.root / "release-subset.json"
        subset.write_text(json.dumps({"feature_claims": [
            {"feature_ref": "owner/repo#10", "expected_revision": 0},
        ]}), encoding="utf-8")
        rejected_subset = self.invoke(
            db, "feature", "release", "--run-id", "run-1", "--input", str(subset),
            check=False,
        )
        self.assertEqual(self.payload(rejected_subset)["error"]["code"], "revision-conflict")
        released = self.payload(self.invoke(
            db, "feature", "release", "--run-id", "run-1", "--input", str(release)
        ))
        self.assertTrue(released["result"]["changed"])
        self.assertTrue(all(
            claim["status"] == "released"
            for claim in released["result"]["feature_claims"]
        ))
        stale_effect = self.invoke(
            db, "operation", "begin", "--run-id", "run-1",
            "--assignment-id", "assignment-10", "--action", "push",
            "--subject-id", "candidate", check=False,
        )
        self.assertEqual(
            self.payload(stale_effect)["error"]["code"], "feature-claim-required"
        )
        self.invoke(
            db, "run", "checkpoint", "--run-id", "run-1",
            "--expected-revision", "1", "--status", "complete", "--checkpoint", "complete",
        )
        completed_claim = self.invoke(
            db, "feature", "claim", "--run-id", "run-1", "--input", str(source),
            check=False,
        )
        self.assertEqual(self.payload(completed_claim)["error"]["code"], "run-not-active")
        only_released = self.root / "released.json"
        only_released.write_text(json.dumps({
            "feature_refs": ["owner/repo#10"]
        }), encoding="utf-8")
        reclaimed = self.payload(self.invoke(
            db, "feature", "claim", "--run-id", "run-2", "--input", str(only_released)
        ))
        self.assertEqual(reclaimed["result"]["feature_claims"][0]["run_id"], "run-2")

    def test_feature_claim_canonicalizes_equivalent_github_refs(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        for run_id in ("run-1", "run-2"):
            self.invoke(db, "run", "start", "--run-id", run_id,
                        "--orchestrator-task-id", f"task-{run_id}")
        short = self.root / "short.json"
        short.write_text(json.dumps({"feature_refs": ["Owner/Repo#10"]}), encoding="utf-8")
        claimed = self.payload(self.invoke(
            db, "feature", "claim", "--run-id", "run-1", "--input", str(short)
        ))
        self.assertEqual(
            claimed["result"]["feature_claims"][0]["feature_ref"], "owner/repo#10"
        )
        url = self.root / "url.json"
        url.write_text(json.dumps({
            "feature_refs": ["https://github.com/owner/repo/issues/10"]
        }), encoding="utf-8")
        conflict = self.invoke(
            db, "feature", "claim", "--run-id", "run-2", "--input", str(url),
            check=False,
        )
        self.assertEqual(self.payload(conflict)["error"]["code"], "feature-already-claimed")

    def test_scoped_claim_recovery_retires_supersedes_and_retries_idempotently(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        for run_id, task_id in (("old-run", "old-task"), ("new-run", "new-task")):
            self.invoke(
                db, "run", "start", "--run-id", run_id,
                "--orchestrator-task-id", task_id,
            )
        features = self.root / "features.json"
        features.write_text(json.dumps({
            "feature_refs": ["owner/repo#10", "owner/repo#20"]
        }), encoding="utf-8")
        self.invoke(
            db, "feature", "claim", "--run-id", "old-run", "--input", str(features)
        )

        recovery = self.root / "recovery.json"
        recovery.write_text(json.dumps({
            "disposition": "retire",
            "feature_claims": [{
                "feature_ref": "owner/repo#10",
                "expected_run_id": "old-run",
                "expected_orchestrator_task_id": "old-task",
                "expected_revision": 0,
                "authority_ref": "authority/retire-10",
                "ownership_observation_ref": "observation/old-task-terminal",
            }],
        }), encoding="utf-8")
        retired = self.payload(self.invoke(
            db, "feature", "recover", "--run-id", "new-run",
            "--orchestrator-task-id", "new-task", "--input", str(recovery),
        ))["result"]
        self.assertTrue(retired["changed"])
        self.assertEqual(retired["recoveries"][0]["feature_claim"]["status"], "released")
        self.assertEqual(retired["recoveries"][0]["feature_claim"]["run_id"], "old-run")
        self.assertEqual(retired["recoveries"][0]["operation"]["status"], "applied")
        operation_id = retired["recoveries"][0]["operation"]["operation_id"]
        retried = self.payload(self.invoke(
            db, "feature", "recover", "--run-id", "new-run",
            "--orchestrator-task-id", "new-task", "--input", str(recovery),
        ))["result"]
        self.assertFalse(retried["changed"])
        self.assertEqual(
            retried["recoveries"][0]["operation"]["operation_id"], operation_id
        )
        conflicting_payload = json.loads(recovery.read_text(encoding="utf-8"))
        conflicting_payload["feature_claims"][0]["authority_ref"] = "authority/different"
        recovery.write_text(json.dumps(conflicting_payload), encoding="utf-8")
        conflicting_retry = self.invoke(
            db, "feature", "recover", "--run-id", "new-run",
            "--orchestrator-task-id", "new-task", "--input", str(recovery),
            check=False,
        )
        self.assertEqual(
            self.payload(conflicting_retry)["error"]["code"], "recovery-conflict"
        )

        recovery.write_text(json.dumps({
            "disposition": "supersede",
            "feature_claims": [{
                "feature_ref": "owner/repo#20",
                "expected_run_id": "old-run",
                "expected_orchestrator_task_id": "old-task",
                "expected_revision": 0,
                "authority_ref": "authority/supersede-20",
                "ownership_observation_ref": "observation/old-task-abandoned",
            }],
        }), encoding="utf-8")
        superseded = self.payload(self.invoke(
            db, "feature", "recover", "--run-id", "new-run",
            "--orchestrator-task-id", "new-task", "--input", str(recovery),
        ))["result"]
        claim = superseded["recoveries"][0]["feature_claim"]
        self.assertEqual((claim["run_id"], claim["status"], claim["revision"]),
                         ("new-run", "active", 1))
        stale_effect = self.invoke(
            db, "operation", "begin", "--run-id", "old-run", "--action", "push",
            "--subject-id", "stale-candidate", check=False,
        )
        self.assertEqual(
            self.payload(stale_effect)["error"]["code"], "feature-claim-required"
        )

    def test_claim_recovery_conflicts_and_ambiguous_ownership_are_atomic(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        for run_id, task_id in (("old-run", "old-task"), ("new-run", "new-task")):
            self.invoke(
                db, "run", "start", "--run-id", run_id,
                "--orchestrator-task-id", task_id,
            )
        features = self.root / "features.json"
        features.write_text(json.dumps({
            "feature_refs": ["owner/repo#10", "owner/repo#20"]
        }), encoding="utf-8")
        self.invoke(
            db, "feature", "claim", "--run-id", "old-run", "--input", str(features)
        )
        recovery = self.root / "recovery.json"
        base = {
            "expected_run_id": "old-run",
            "expected_orchestrator_task_id": "old-task",
            "expected_revision": 0,
            "authority_ref": "authority/recover",
            "ownership_observation_ref": "observation/exact-owner",
        }
        recovery.write_text(json.dumps({
            "disposition": "supersede",
            "feature_claims": [
                {**base, "feature_ref": "owner/repo#10"},
                {**base, "feature_ref": "owner/repo#20", "expected_revision": 1},
            ],
        }), encoding="utf-8")
        conflict = self.invoke(
            db, "feature", "recover", "--run-id", "new-run",
            "--orchestrator-task-id", "new-task", "--input", str(recovery),
            check=False,
        )
        self.assertEqual(
            self.payload(conflict)["error"]["code"], "revision-conflict"
        )
        with sqlite3.connect(db) as connection:
            claims = connection.execute(
                "SELECT run_id,status,revision FROM feature_claims ORDER BY feature_ref"
            ).fetchall()
            operations = connection.execute(
                "SELECT count(*) FROM operations WHERE run_id='new-run'"
            ).fetchone()[0]
        self.assertEqual(claims, [("old-run", "active", 0), ("old-run", "active", 0)])
        self.assertEqual(operations, 0)

        malformed = self.root / "malformed.json"
        malformed.write_text(json.dumps({
            "disposition": "retire",
            "feature_claims": [{
                key: value for key, value in {**base, "feature_ref": "owner/repo#10"}.items()
                if key != "ownership_observation_ref"
            }],
        }), encoding="utf-8")
        ambiguous = self.invoke(
            db, "feature", "recover", "--run-id", "new-run",
            "--orchestrator-task-id", "new-task", "--input", str(malformed),
            check=False,
        )
        self.assertEqual(
            self.payload(ambiguous)["error"]["code"], "ambiguous-claim-ownership"
        )
        ambiguous_owner = self.root / "ambiguous-owner.json"
        ambiguous_owner.write_text(json.dumps({
            "disposition": "retire",
            "feature_claims": [{
                **base,
                "feature_ref": "owner/repo#10",
                "expected_orchestrator_task_id": "unverified-task",
            }],
        }), encoding="utf-8")
        ambiguous = self.invoke(
            db, "feature", "recover", "--run-id", "new-run",
            "--orchestrator-task-id", "new-task",
            "--input", str(ambiguous_owner), check=False,
        )
        self.assertEqual(
            self.payload(ambiguous)["error"]["code"], "ambiguous-claim-ownership"
        )
        wrong_controller = self.invoke(
            db, "feature", "recover", "--run-id", "new-run",
            "--orchestrator-task-id", "other-task", "--input", str(recovery),
            check=False,
        )
        self.assertEqual(self.payload(wrong_controller)["error"]["code"], "run-conflict")

    def test_claim_recovery_rejects_unresolved_source_effects(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        for run_id, task_id in (("old-run", "old-task"), ("new-run", "new-task")):
            self.invoke(
                db, "run", "start", "--run-id", run_id,
                "--orchestrator-task-id", task_id,
            )
        features = self.root / "features.json"
        features.write_text(
            json.dumps({"feature_refs": ["owner/repo#10"]}), encoding="utf-8"
        )
        self.invoke(
            db, "feature", "claim", "--run-id", "old-run", "--input", str(features)
        )
        self.invoke(
            db, "operation", "begin", "--run-id", "old-run", "--action", "push",
            "--subject-id", "candidate",
        )
        recovery = self.root / "recovery.json"
        recovery.write_text(json.dumps({
            "disposition": "supersede",
            "feature_claims": [{
                "feature_ref": "owner/repo#10",
                "expected_run_id": "old-run",
                "expected_orchestrator_task_id": "old-task",
                "expected_revision": 0,
                "authority_ref": "authority/supersede",
                "ownership_observation_ref": "observation/old-task-terminal",
            }],
        }), encoding="utf-8")
        rejected = self.invoke(
            db, "feature", "recover", "--run-id", "new-run",
            "--orchestrator-task-id", "new-task", "--input", str(recovery),
            check=False,
        )
        self.assertEqual(
            self.payload(rejected)["error"]["code"], "recovery-effects-unresolved"
        )

    def test_assignment_requires_claim_and_rejects_non_text_state(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        self.invoke(db, "run", "start", "--run-id", "run-1",
                    "--orchestrator-task-id", "task-root")
        source = self.root / "assignment.json"
        base = {
            "feature_ref": "owner/repo#10",
            "repository_identity": "github:owner/repo", "status": "active",
            "checkpoint": "worker-bootstrap",
        }
        source.write_text(json.dumps(base), encoding="utf-8")
        unclaimed = self.invoke(
            db, "assignment", "checkpoint", "--run-id", "run-1",
            "--assignment-id", "assignment-1", "--expected-revision", "0",
            "--input", str(source), check=False,
        )
        self.assertEqual(
            self.payload(unclaimed)["error"]["code"], "feature-claim-required"
        )
        bad = {**base, "status": True}
        source.write_text(json.dumps(bad), encoding="utf-8")
        invalid = self.invoke(
            db, "assignment", "checkpoint", "--run-id", "run-1",
            "--assignment-id", "assignment-1", "--expected-revision", "0",
            "--input", str(source), check=False,
        )
        self.assertEqual(self.payload(invalid)["error"]["code"], "invalid-input")
        features = self.root / "features.json"
        features.write_text(json.dumps({"feature_refs": ["owner/repo#10"]}), encoding="utf-8")
        self.invoke(db, "feature", "claim", "--run-id", "run-1", "--input", str(features))
        bad_sha = {**base, "candidate_sha": "not-a-git-sha"}
        source.write_text(json.dumps(bad_sha), encoding="utf-8")
        invalid_sha = self.invoke(
            db, "assignment", "checkpoint", "--run-id", "run-1",
            "--assignment-id", "assignment-1", "--expected-revision", "0",
            "--input", str(source), check=False,
        )
        self.assertEqual(self.payload(invalid_sha)["error"]["code"], "invalid-input")

    def test_assignment_identity_is_immutable(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        self.invoke(db, "run", "start", "--run-id", "run-1",
                    "--orchestrator-task-id", "task-root")
        features = self.root / "features.json"
        features.write_text(json.dumps({"feature_refs": ["owner/repo#10"]}), encoding="utf-8")
        self.invoke(db, "feature", "claim", "--run-id", "run-1", "--input", str(features))
        source = self.root / "assignment.json"
        source.write_text(json.dumps({
            "feature_ref": "owner/repo#10",
            "repository_identity": "github:owner/repo", "status": "active",
            "checkpoint": "worker-bootstrap",
        }), encoding="utf-8")
        self.invoke(db, "assignment", "checkpoint", "--run-id", "run-1",
                    "--assignment-id", "assignment-1", "--expected-revision", "0",
                    "--input", str(source))
        source.write_text(json.dumps({
            "repository_identity": "github:owner/other-repo"
        }), encoding="utf-8")
        immutable = self.invoke(
            db, "assignment", "checkpoint", "--run-id", "run-1",
            "--assignment-id", "assignment-1", "--expected-revision", "0",
            "--input", str(source), check=False,
        )
        self.assertEqual(
            self.payload(immutable)["error"]["code"], "immutable-assignment-identity"
        )
        source.write_text(json.dumps({
            "feature_ref": "owner/repo#10",
            "repository_identity": "github:owner/repo", "status": "active",
            "checkpoint": "worker-bootstrap",
        }), encoding="utf-8")
        duplicate = self.invoke(
            db, "assignment", "checkpoint", "--run-id", "run-1",
            "--assignment-id", "assignment-2", "--expected-revision", "0",
            "--input", str(source), check=False,
        )
        self.assertEqual(
            self.payload(duplicate)["error"]["code"], "feature-assignment-exists"
        )
    def test_concurrent_operation_begin_and_finish_are_serialized(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        self.invoke(db, "run", "start", "--run-id", "run-1",
                    "--orchestrator-task-id", "task-root")
        features = self.root / "features.json"
        features.write_text(json.dumps({"feature_refs": ["owner/repo#10"]}), encoding="utf-8")
        self.invoke(db, "feature", "claim", "--run-id", "run-1", "--input", str(features))
        begin = [
            subprocess.Popen(
                [str(SCRIPT), "--json", "--db", str(db), "operation", "begin",
                 "--run-id", "run-1", "--action", "push", "--subject-id", "candidate"],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            for _ in range(2)
        ]
        results = [json.loads(process.communicate()[0]) for process in begin]
        self.assertTrue(all(result["ok"] for result in results))
        operation_ids = {result["result"]["operation"]["operation_id"] for result in results}
        self.assertEqual(len(operation_ids), 1)
        operation_id = operation_ids.pop()
        finish_commands = [
            ("applied", ["--receipt-ref", "receipt", "--readback-ref", "applied-readback"]),
            ("blocked", ["--readback-ref", "blocked-readback"]),
        ]
        finish = [
            subprocess.Popen(
                [str(SCRIPT), "--json", "--db", str(db), "operation", "finish",
                 "--operation-id", operation_id, "--status", status, *evidence],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            for status, evidence in finish_commands
        ]
        finished = [json.loads(process.communicate()[0]) for process in finish]
        self.assertEqual(sum(result["ok"] for result in finished), 1)
        self.assertEqual(
            next(result for result in finished if not result["ok"])["error"]["code"],
            "operation-conflict",
        )

    def test_operation_finish_requires_evidence_and_can_refine_unknown(self) -> None:
        db = self.root / "run-state.sqlite3"
        self.invoke(db, "state", "prepare")
        self.invoke(db, "run", "start", "--run-id", "run-1",
                    "--orchestrator-task-id", "task-root")
        features = self.root / "features.json"
        features.write_text(json.dumps({"feature_refs": ["owner/repo#10"]}), encoding="utf-8")
        self.invoke(db, "feature", "claim", "--run-id", "run-1", "--input", str(features))
        begun = self.payload(self.invoke(
            db, "operation", "begin", "--run-id", "run-1",
            "--action", "push", "--subject-id", "candidate",
        ))
        operation_id = begun["result"]["operation"]["operation_id"]
        missing = self.invoke(
            db, "operation", "finish", "--operation-id", operation_id,
            "--status", "applied", check=False,
        )
        self.assertEqual(
            self.payload(missing)["error"]["code"], "operation-evidence-required"
        )
        unknown = self.payload(self.invoke(
            db, "operation", "finish", "--operation-id", operation_id,
            "--status", "unknown", "--receipt-ref", "receipt",
            "--readback-ref", "ambiguous-readback",
        ))
        self.assertEqual(unknown["result"]["operation"]["status"], "unknown")
        refined = self.payload(self.invoke(
            db, "operation", "finish", "--operation-id", operation_id,
            "--status", "not-applied", "--readback-ref", "absent-readback",
        ))
        self.assertEqual(refined["result"]["operation"]["status"], "not-applied")
        self.assertEqual(refined["result"]["operation"]["receipt_ref"], "receipt")


if __name__ == "__main__":
    unittest.main()
