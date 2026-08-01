from __future__ import annotations
# Bundled under Feature Flow; implement-feature protocol and cache identifiers remain stable.

import json
import os
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "run-state"


class RunStateGitHubScenarios(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.home = self.base / "home"
        self.home.mkdir()
        self.repo = self.base / "repo.git"
        self.repo.mkdir()
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        self.invoke("state", "prepare")

    def tearDown(self) -> None:
        self.temp.cleanup()

    @property
    def database(self) -> Path:
        return self.home / ".cache" / "dotagents" / "skills" / "implement-feature" / "run-state.sqlite3"

    def invoke(self, *arguments: str, expected: int = 0) -> dict[str, object]:
        result = subprocess.run(
            [str(TOOL), "--json", *arguments],
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, expected, result.stderr + result.stdout)
        return json.loads(result.stdout)

    def write_json(self, name: str, value: object) -> Path:
        path = self.base / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def manifest(self, run_id: str) -> dict[str, object]:
        return {
            "schema": "implement-feature/run-manifest",
            "schema_version": "4.0.0",
            "runtime_contract_version": "9.0.0",
            "run_id": run_id,
            "root_task_id": f"root-{run_id}",
            "controller_project_id": "controller-project",
            "repositories": [
                {
                    "repository_identity": "github:owner/repository",
                    "git_common_dir": str(self.repo),
                    "project_id": "repository-project",
                }
            ],
            "assignments": [
                {
                    "assignment_id": "spec-01",
                    "source_spec_ref": "owner/repository#42",
                    "repository_identity": "github:owner/repository",
                    "title": "🛠️ Implement Feature · Example",
                    "target_branch_name": "feature/example",
                    "prerequisite_assignment_ids": [],
                }
            ],
            "feature_sets": [],
        }

    def start(self, run_id: str) -> dict[str, object]:
        return self.invoke(
            "run",
            "start",
            "--manifest",
            str(self.write_json(f"{run_id}.json", self.manifest(run_id))),
        )

    def activate_assignment(self, run_id: str) -> tuple[str, Path]:
        thread_id = f"thread-{run_id}"
        checkout = self.base / f"checkout-{run_id}"
        checkout.mkdir()
        connection = sqlite3.connect(self.database)
        try:
            connection.execute(
                """UPDATE assignments
                   SET state='active',thread_id=?,checkout_path=?
                   WHERE run_id=? AND assignment_id='spec-01'""",
                (thread_id, str(checkout.resolve()), run_id),
            )
            connection.execute(
                "UPDATE runs SET implementation_started=1,status='active' WHERE run_id=?",
                (run_id,),
            )
            connection.commit()
        finally:
            connection.close()
        return thread_id, checkout

    def ready_builder_args(
        self,
        run_id: str,
        revision: int,
        thread_id: str,
        checkout: Path,
        output: Path,
        *,
        review_profile: str = "standard",
        codex_review_head_sha: str | None = None,
        pr_url: str = "https://github.com/owner/repository/pull/44",
    ) -> list[str]:
        head_sha = "a" * 40
        arguments = [
            "assignment",
            "ready-observation",
            "create",
            "--run-id",
            run_id,
            "--expected-revision",
            str(revision),
            "--assignment-id",
            "spec-01",
            "--thread-id",
            thread_id,
            "--repository-identity",
            "github:owner/repository",
            "--head-sha",
            head_sha,
            "--head-branch-name",
            "feature/example",
            "--base-branch-name",
            "main",
            "--base-sha",
            "b" * 40,
            "--checkout-path",
            str(checkout),
            "--worktree-clean",
            "--base-is-ancestor",
            "--validation-head-sha",
            head_sha,
            "--review-head-sha",
            head_sha,
            "--review-candidate-head-sha",
            head_sha,
            "--review-profile",
            review_profile,
            "--readiness-mode",
            "terminal",
            "--codex-review-head-sha",
            codex_review_head_sha or head_sha,
            "--tracker-readback-ref",
            "tracker:example:42",
            "--default-branch-name",
            "main",
            "--pr-url",
            pr_url,
            "--provider-observation-ref",
            "provider:example:44",
            "--output",
            str(output),
        ]
        return arguments

    def test_current_schema_has_no_retired_transport_storage(self) -> None:
        prepared = self.invoke("state", "prepare")
        connection = sqlite3.connect(self.database)
        try:
            metadata_columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(runtime_metadata)")
            }
            assignment_columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(assignments)")
            }
            reservation_columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(app_operation_reservations)")
            }
            journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
            run_sql = connection.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='runs'"
            ).fetchone()[0]
            assignment_sql = connection.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='assignments'"
            ).fetchone()[0]
        finally:
            connection.close()
        self.assertEqual(metadata_columns, {"singleton", "schema_version"})
        self.assertEqual(reservation_columns, {"run_id", "action", "subject_id", "operation_id", "created_at"})
        self.assertEqual(self.invoke("capabilities")["database_schema_version"], 1)
        self.assertEqual(journal_mode, "wal")
        self.assertNotIn("regenerated", prepared)
        self.assertNotIn("tracker_backend", assignment_columns)
        self.assertNotIn("delivery_type", assignment_columns)
        self.assertNotIn("local-branch-ready", run_sql)
        self.assertNotIn("local-branch-ready", assignment_sql)

    def test_manifest_accepts_github_and_rejects_retired_inputs(self) -> None:
        started = self.start("github-only")
        shown = self.invoke("run", "show", "--run-id", "github-only")
        self.assertEqual(started["status"], "active")
        self.assertNotIn("tracker_backend", shown["assignments"][0])
        self.assertNotIn("delivery_type", shown["assignments"][0])

        with_local_field = self.manifest("retired-field")
        with_local_field["assignments"][0]["tracker_backend"] = "local"
        error = self.invoke(
            "run",
            "start",
            "--manifest",
            str(self.write_json("retired-field.json", with_local_field)),
            expected=2,
        )
        self.assertEqual(error["error"]["code"], "invalid-input")

        with_local_ref = self.manifest("retired-ref")
        with_local_ref["assignments"][0]["source_spec_ref"] = "planning/features/example/SPEC.md"
        error = self.invoke(
            "run",
            "start",
            "--manifest",
            str(self.write_json("retired-ref.json", with_local_ref)),
            expected=2,
        )
        self.assertEqual(error["error"]["code"], "invalid-input")

    def test_task_titles_use_implement_feature_vocabulary(self) -> None:
        started = self.start("title-flow")
        operation = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "title-flow",
            "--expected-revision",
            str(started["revision"]),
            "--action",
            "set-root-title",
            "--subject-id",
            "root-title-flow",
        )
        observation = self.base / "root-title-observation.json"
        self.invoke(
            "app-operation",
            "observation",
            "create",
            "--run-id",
            "title-flow",
            "--expected-revision",
            str(operation["revision"]),
            "--operation-id",
            str(operation["operation_id"]),
            "--launch-count",
            "1",
            "--status",
            "succeeded",
            "--receipt-ref",
            "receipt:title",
            "--readback-ref",
            "readback:title",
            "--observed-title",
            "🤖 Implement Feature · 1 Spec",
            "--output",
            str(observation),
        )
        finished = self.invoke(
            "app-operation",
            "finish",
            "--run-id",
            "title-flow",
            "--expected-revision",
            str(operation["revision"]),
            "--operation-id",
            str(operation["operation_id"]),
            "--observation",
            str(observation),
        )
        self.assertEqual(finished["status"], "succeeded")

    def test_single_use_operations_have_durable_reservations(self) -> None:
        started = self.start("marker-flow")
        operation = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "marker-flow",
            "--expected-revision",
            str(started["revision"]),
            "--action",
            "set-root-title",
            "--subject-id",
            "root-marker-flow",
        )
        connection = sqlite3.connect(self.database)
        try:
            reservation = connection.execute(
                """SELECT run_id,action,subject_id,operation_id
                   FROM app_operation_reservations""",
            ).fetchone()
        finally:
            connection.close()
        self.assertEqual(
            reservation,
            (
                "marker-flow",
                "set-root-title",
                "root-marker-flow",
                operation["operation_id"],
            ),
        )

        duplicate = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "marker-flow",
            "--expected-revision",
            str(operation["revision"]),
            "--action",
            "set-root-title",
            "--subject-id",
            "root-marker-flow",
            expected=4,
        )
        self.assertEqual(duplicate["error"]["code"], "protected-operation-already-started")
        self.assertIn(str(operation["operation_id"]), duplicate["error"]["message"])

        stale = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "marker-flow",
            "--expected-revision",
            str(started["revision"]),
            "--action",
            "set-root-title",
            "--subject-id",
            "root-marker-flow-2",
            expected=4,
        )
        self.assertEqual(stale["error"]["code"], "revision-conflict")

    def test_review_owner_is_fixed_to_worker(self) -> None:
        capabilities = self.invoke("capabilities")
        self.assertEqual(capabilities["cli_version"], "1.0.0")
        self.assertEqual(capabilities["runtime_contract_version"], "9.0.0")
        self.assertEqual(
            capabilities["protocols"]["app_operation_observation"]["version"],
            "4.0.0",
        )

        removed_option = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "removed-owner",
            "--expected-revision",
            "0",
            "--action",
            "set-root-title",
            "--subject-id",
            "root",
            "--review-owner",
            "root",
            expected=2,
        )
        self.assertEqual(removed_option["error"]["code"], "invalid-command-line")

        removed_action = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "removed-owner",
            "--expected-revision",
            "0",
            "--action",
            "set-review-owner",
            "--subject-id",
            "worker",
            expected=2,
        )
        self.assertEqual(removed_action["error"]["code"], "invalid-command-line")

    def test_pr_ready_builder_requires_github_evidence_and_finish(self) -> None:
        started = self.start("ready-flow")
        thread_id, checkout = self.activate_assignment("ready-flow")
        output = self.base / "ready.json"

        drift = self.invoke(
            *self.ready_builder_args(
                "ready-flow",
                int(started["revision"]),
                thread_id,
                checkout,
                output,
                pr_url="https://github.com/other/repository/pull/44",
            ),
            expected=4,
        )
        self.assertEqual(drift["error"]["code"], "pull-request-repository-drift")

        high_risk = self.invoke(
            *self.ready_builder_args(
                "ready-flow",
                int(started["revision"]),
                thread_id,
                checkout,
                output,
                review_profile="high-risk",
                codex_review_head_sha="c" * 40,
            ),
            expected=4,
        )
        self.assertEqual(high_risk["error"]["code"], "stale-ready-evidence")

        created = self.invoke(
            *self.ready_builder_args(
                "ready-flow",
                int(started["revision"]),
                thread_id,
                checkout,
                output,
            )
        )
        payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(created["observation_kind"], "delivery-ready")
        self.assertEqual(payload["status"], "pr-ready-for-merge")
        self.assertNotIn("delivery_type", payload)

        ready = self.invoke(
            "assignment",
            "ready",
            "--run-id",
            "ready-flow",
            "--expected-revision",
            str(started["revision"]),
            "--observation",
            str(output),
        )
        self.assertEqual(ready["state"], "pr-ready")
        self.assertTrue(ready["claim_released"])

        finished = self.invoke(
            "run",
            "finish",
            "--run-id",
            "ready-flow",
            "--expected-revision",
            str(ready["revision"]),
            "--outcome",
            "pr-ready",
        )
        self.assertEqual(finished["outcome"], "pr-ready")


if __name__ == "__main__":
    unittest.main()
