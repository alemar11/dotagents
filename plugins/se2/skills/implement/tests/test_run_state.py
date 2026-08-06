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
        self.assertEqual(version.stdout.strip(), "3.0.0")
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
            "status": "reviewing", "checkpoint": "native-review",
            "candidate_sha": "a" * 40,
        }), encoding="utf-8")
        updated = self.payload(self.invoke(
            db, "assignment", "checkpoint", "--run-id", "run-1",
            "--assignment-id", "assignment-1", "--expected-revision", "0",
            "--input", str(source),
        ))
        self.assertEqual(updated["result"]["assignment"]["revision"], 1)

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
            "status": "plan-question", "checkpoint": "plan-question",
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
