from __future__ import annotations
# Bundled under SE; implement-feature protocol and cache identifiers remain stable.

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
            "runtime_contract_version": "1.0.0",
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

    def start_same_branch(self, run_id: str, issue_number: int) -> dict[str, object]:
        manifest = self.manifest(run_id)
        manifest["assignments"][0]["source_spec_ref"] = f"owner/repository#{issue_number}"
        return self.invoke(
            "run",
            "start",
            "--manifest",
            str(self.write_json(f"{run_id}.json", manifest)),
        )

    def recovery_observation(
        self,
        name: str,
        owner_run_id: str,
        owner_revision: int,
        *,
        worker_state: str,
        checkout_state: str,
        issue_number: int = 42,
    ) -> Path:
        return self.write_json(
            name,
            {
                "schema": "implement-feature/recovery-observation",
                "schema_version": "3.0.0",
                "owner_run_id": owner_run_id,
                "owner_assignment_id": "spec-01",
                "owner_expected_revision": owner_revision,
                "repository_identity": "github:owner/repository",
                "source_spec_ref": f"owner/repository#{issue_number}",
                "worker_state": worker_state,
                "checkout_state": checkout_state,
                "readback_ref": f"readback:{name}",
            },
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

    def test_bootstrap_manifest_example_matches_runtime_contract(self) -> None:
        capabilities = self.invoke("capabilities")
        bootstrap = (ROOT / "references" / "root-bootstrap.md").read_text(encoding="utf-8")
        self.assertIn(
            f'"runtime_contract_version": "{capabilities["runtime_contract_version"]}"',
            bootstrap,
        )

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
            "🤖 Implement Feature · 1 Spec (normalized)",
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
        self.assertEqual(finished["effect_warning"], "root-title-drift")

    def test_worker_title_is_initialized_after_creation_before_bootstrap(self) -> None:
        started = self.start("worker-title-flow")
        create = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "worker-title-flow",
            "--expected-revision",
            str(started["revision"]),
            "--action",
            "create-worker",
            "--subject-id",
            "spec-01",
        )
        checkout = self.base / "worker-title-checkout"
        checkout.mkdir()
        creation_observation = self.base / "worker-creation-observation.json"
        self.invoke(
            "app-operation",
            "observation",
            "create",
            "--run-id",
            "worker-title-flow",
            "--expected-revision",
            str(create["revision"]),
            "--operation-id",
            str(create["operation_id"]),
            "--launch-count",
            "1",
            "--status",
            "succeeded",
            "--receipt-ref",
            "receipt:worker-create",
            "--readback-ref",
            "readback:worker-create",
            "--thread-id",
            "worker-title-thread",
            "--project-id",
            "repository-project",
            "--checkout-path",
            str(checkout),
            "--git-common-dir",
            str(self.repo),
            "--observed-state",
            "idle",
            "--output",
            str(creation_observation),
        )
        created = self.invoke(
            "app-operation",
            "finish",
            "--run-id",
            "worker-title-flow",
            "--expected-revision",
            str(create["revision"]),
            "--operation-id",
            str(create["operation_id"]),
            "--observation",
            str(creation_observation),
        )

        title = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "worker-title-flow",
            "--expected-revision",
            str(created["revision"]),
            "--action",
            "set-worker-title",
            "--subject-id",
            "spec-01",
        )
        self.assertEqual(title["expected_title"], "🛠️ Implement Feature · Example")
        title_observation = self.base / "worker-title-observation.json"
        self.invoke(
            "app-operation",
            "observation",
            "create",
            "--run-id",
            "worker-title-flow",
            "--expected-revision",
            str(title["revision"]),
            "--operation-id",
            str(title["operation_id"]),
            "--launch-count",
            "1",
            "--status",
            "succeeded",
            "--receipt-ref",
            "receipt:worker-title",
            "--readback-ref",
            "readback:worker-title",
            "--thread-id",
            "worker-title-thread",
            "--observed-title",
            "🛠️ Implement Feature · Example",
            "--output",
            str(title_observation),
        )
        titled = self.invoke(
            "app-operation",
            "finish",
            "--run-id",
            "worker-title-flow",
            "--expected-revision",
            str(title["revision"]),
            "--operation-id",
            str(title["operation_id"]),
            "--observation",
            str(title_observation),
        )
        self.assertEqual(titled["status"], "succeeded")

        bootstrap = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "worker-title-flow",
            "--expected-revision",
            str(titled["revision"]),
            "--action",
            "send-bootstrap",
            "--subject-id",
            "spec-01",
        )
        self.assertTrue(bootstrap["launch_authorized"])

    def test_worker_creation_title_readback_allows_bootstrap_without_fallback(self) -> None:
        started = self.start("worker-creation-title-flow")
        create = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "worker-creation-title-flow",
            "--expected-revision",
            str(started["revision"]),
            "--action",
            "create-worker",
            "--subject-id",
            "spec-01",
        )
        checkout = self.base / "worker-creation-title-checkout"
        checkout.mkdir()
        observation = self.base / "worker-creation-title-observation.json"
        self.invoke(
            "app-operation",
            "observation",
            "create",
            "--run-id",
            "worker-creation-title-flow",
            "--expected-revision",
            str(create["revision"]),
            "--operation-id",
            str(create["operation_id"]),
            "--launch-count",
            "1",
            "--status",
            "succeeded",
            "--receipt-ref",
            "receipt:worker-creation-title",
            "--readback-ref",
            "readback:worker-creation-title",
            "--thread-id",
            "worker-creation-title-thread",
            "--project-id",
            "repository-project",
            "--checkout-path",
            str(checkout),
            "--git-common-dir",
            str(self.repo),
            "--observed-title",
            "🛠️ Implement Feature · Example",
            "--observed-state",
            "idle",
            "--output",
            str(observation),
        )
        created = self.invoke(
            "app-operation",
            "finish",
            "--run-id",
            "worker-creation-title-flow",
            "--expected-revision",
            str(create["revision"]),
            "--operation-id",
            str(create["operation_id"]),
            "--observation",
            str(observation),
        )
        bootstrap = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "worker-creation-title-flow",
            "--expected-revision",
            str(created["revision"]),
            "--action",
            "send-bootstrap",
            "--subject-id",
            "spec-01",
        )
        self.assertTrue(bootstrap["launch_authorized"])

    def test_worker_title_drift_is_recorded_without_blocking_bootstrap(self) -> None:
        started = self.start("worker-title-drift-flow")
        create = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "worker-title-drift-flow",
            "--expected-revision",
            str(started["revision"]),
            "--action",
            "create-worker",
            "--subject-id",
            "spec-01",
        )
        checkout = self.base / "worker-title-drift-checkout"
        checkout.mkdir()
        creation_observation = self.base / "worker-title-drift-creation.json"
        self.invoke(
            "app-operation",
            "observation",
            "create",
            "--run-id",
            "worker-title-drift-flow",
            "--expected-revision",
            str(create["revision"]),
            "--operation-id",
            str(create["operation_id"]),
            "--launch-count",
            "1",
            "--status",
            "succeeded",
            "--receipt-ref",
            "receipt:worker-create-drift",
            "--readback-ref",
            "readback:worker-create-drift",
            "--thread-id",
            "worker-title-drift-thread",
            "--project-id",
            "repository-project",
            "--checkout-path",
            str(checkout),
            "--git-common-dir",
            str(self.repo),
            "--observed-state",
            "idle",
            "--output",
            str(creation_observation),
        )
        created = self.invoke(
            "app-operation",
            "finish",
            "--run-id",
            "worker-title-drift-flow",
            "--expected-revision",
            str(create["revision"]),
            "--operation-id",
            str(create["operation_id"]),
            "--observation",
            str(creation_observation),
        )
        self.assertEqual(created["effect_warning"], "worker-title-unverified")

        title = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "worker-title-drift-flow",
            "--expected-revision",
            str(created["revision"]),
            "--action",
            "set-worker-title",
            "--subject-id",
            "spec-01",
        )
        title_observation = self.base / "worker-title-drift-title.json"
        self.invoke(
            "app-operation",
            "observation",
            "create",
            "--run-id",
            "worker-title-drift-flow",
            "--expected-revision",
            str(title["revision"]),
            "--operation-id",
            str(title["operation_id"]),
            "--launch-count",
            "1",
            "--status",
            "succeeded",
            "--receipt-ref",
            "receipt:worker-title-drift",
            "--readback-ref",
            "readback:worker-title-drift",
            "--thread-id",
            "worker-title-drift-thread",
            "--observed-title",
            "🛠️ Implement Feature · Example (normalized)",
            "--output",
            str(title_observation),
        )
        titled = self.invoke(
            "app-operation",
            "finish",
            "--run-id",
            "worker-title-drift-flow",
            "--expected-revision",
            str(title["revision"]),
            "--operation-id",
            str(title["operation_id"]),
            "--observation",
            str(title_observation),
        )
        self.assertEqual(titled["status"], "succeeded")
        self.assertEqual(titled["effect_warning"], "worker-title-drift")
        telemetry = self.invoke(
            "app-operation",
            "list",
            "--run-id",
            "worker-title-drift-flow",
        )
        self.assertIn(
            "worker-title-drift",
            [operation["effect_warning"] for operation in telemetry["operations"] if "effect_warning" in operation],
        )

        bootstrap = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "worker-title-drift-flow",
            "--expected-revision",
            str(titled["revision"]),
            "--action",
            "send-bootstrap",
            "--subject-id",
            "spec-01",
        )
        self.assertTrue(bootstrap["launch_authorized"])

    def test_scope_repair_title_is_initialized_after_planner_creation(self) -> None:
        started = self.start("scope-title-flow")
        self.activate_assignment("scope-title-flow")
        blocked = self.invoke(
            "assignment",
            "scope-block",
            "--run-id",
            "scope-title-flow",
            "--expected-revision",
            str(started["revision"]),
            "--assignment-id",
            "spec-01",
        )
        planner = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "scope-title-flow",
            "--expected-revision",
            str(blocked["revision"]),
            "--action",
            "create-scope-repair-task",
            "--subject-id",
            "spec-01",
        )
        planner_observation = self.base / "scope-planner-observation.json"
        self.invoke(
            "app-operation",
            "observation",
            "create",
            "--run-id",
            "scope-title-flow",
            "--expected-revision",
            str(planner["revision"]),
            "--operation-id",
            str(planner["operation_id"]),
            "--launch-count",
            "1",
            "--status",
            "succeeded",
            "--receipt-ref",
            "receipt:scope-planner",
            "--readback-ref",
            "readback:scope-planner",
            "--thread-id",
            "scope-planner-thread",
            "--project-id",
            "repository-project",
            "--observed-state",
            "idle",
            "--output",
            str(planner_observation),
        )
        created = self.invoke(
            "app-operation",
            "finish",
            "--run-id",
            "scope-title-flow",
            "--expected-revision",
            str(planner["revision"]),
            "--operation-id",
            str(planner["operation_id"]),
            "--observation",
            str(planner_observation),
        )

        title = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "scope-title-flow",
            "--expected-revision",
            str(created["revision"]),
            "--action",
            "set-scope-repair-title",
            "--subject-id",
            "spec-01",
        )
        self.assertEqual(title["expected_title"], "🧭 Scope Repair · Example")
        title_observation = self.base / "scope-planner-title-observation.json"
        self.invoke(
            "app-operation",
            "observation",
            "create",
            "--run-id",
            "scope-title-flow",
            "--expected-revision",
            str(title["revision"]),
            "--operation-id",
            str(title["operation_id"]),
            "--launch-count",
            "1",
            "--status",
            "succeeded",
            "--receipt-ref",
            "receipt:scope-title",
            "--readback-ref",
            "readback:scope-title",
            "--thread-id",
            "scope-planner-thread",
            "--observed-title",
            "🧭 Scope Repair · Example",
            "--output",
            str(title_observation),
        )
        titled = self.invoke(
            "app-operation",
            "finish",
            "--run-id",
            "scope-title-flow",
            "--expected-revision",
            str(title["revision"]),
            "--operation-id",
            str(title["operation_id"]),
            "--observation",
            str(title_observation),
        )
        self.assertEqual(titled["status"], "succeeded")

    def test_scope_repair_creation_title_readback_allows_scope_observation(self) -> None:
        started = self.start("scope-creation-title-flow")
        self.activate_assignment("scope-creation-title-flow")
        blocked = self.invoke(
            "assignment",
            "scope-block",
            "--run-id",
            "scope-creation-title-flow",
            "--expected-revision",
            str(started["revision"]),
            "--assignment-id",
            "spec-01",
        )
        planner = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "scope-creation-title-flow",
            "--expected-revision",
            str(blocked["revision"]),
            "--action",
            "create-scope-repair-task",
            "--subject-id",
            "spec-01",
        )
        planner_observation = self.base / "scope-creation-title-planner.json"
        self.invoke(
            "app-operation",
            "observation",
            "create",
            "--run-id",
            "scope-creation-title-flow",
            "--expected-revision",
            str(planner["revision"]),
            "--operation-id",
            str(planner["operation_id"]),
            "--launch-count",
            "1",
            "--status",
            "succeeded",
            "--receipt-ref",
            "receipt:scope-creation-title",
            "--readback-ref",
            "readback:scope-creation-title",
            "--thread-id",
            "scope-creation-title-thread",
            "--project-id",
            "repository-project",
            "--observed-title",
            "🧭 Scope Repair · Example",
            "--observed-state",
            "idle",
            "--output",
            str(planner_observation),
        )
        created = self.invoke(
            "app-operation",
            "finish",
            "--run-id",
            "scope-creation-title-flow",
            "--expected-revision",
            str(planner["revision"]),
            "--operation-id",
            str(planner["operation_id"]),
            "--observation",
            str(planner_observation),
        )
        scope_observation = self.invoke(
            "assignment",
            "scope-repair-observation",
            "create",
            "--run-id",
            "scope-creation-title-flow",
            "--expected-revision",
            str(created["revision"]),
            "--assignment-id",
            "spec-01",
            "--repair-outcome",
            "no-op",
            "--implementation-issue-ref",
            "owner/repository#43",
            "--planning-thread-id",
            "scope-creation-title-thread",
            "--planning-result-ref",
            "planning:scope-creation-title",
            "--authoritative-readback-ref",
            "readback:scope-creation-title-source",
            "--output",
            str(self.base / "scope-creation-title-observation.json"),
        )
        self.assertEqual(scope_observation["observation_kind"], "scope-repair")
        self.assertTrue(scope_observation["artifact_written"])

    def test_scope_repair_title_drift_does_not_block_scope_revision(self) -> None:
        started = self.start("scope-title-drift-flow")
        self.activate_assignment("scope-title-drift-flow")
        blocked = self.invoke(
            "assignment",
            "scope-block",
            "--run-id",
            "scope-title-drift-flow",
            "--expected-revision",
            str(started["revision"]),
            "--assignment-id",
            "spec-01",
        )
        planner = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "scope-title-drift-flow",
            "--expected-revision",
            str(blocked["revision"]),
            "--action",
            "create-scope-repair-task",
            "--subject-id",
            "spec-01",
        )
        planner_observation = self.base / "scope-title-drift-planner.json"
        self.invoke(
            "app-operation",
            "observation",
            "create",
            "--run-id",
            "scope-title-drift-flow",
            "--expected-revision",
            str(planner["revision"]),
            "--operation-id",
            str(planner["operation_id"]),
            "--launch-count",
            "1",
            "--status",
            "succeeded",
            "--receipt-ref",
            "receipt:scope-planner-drift",
            "--readback-ref",
            "readback:scope-planner-drift",
            "--thread-id",
            "scope-title-drift-thread",
            "--project-id",
            "repository-project",
            "--observed-state",
            "idle",
            "--output",
            str(planner_observation),
        )
        created = self.invoke(
            "app-operation",
            "finish",
            "--run-id",
            "scope-title-drift-flow",
            "--expected-revision",
            str(planner["revision"]),
            "--operation-id",
            str(planner["operation_id"]),
            "--observation",
            str(planner_observation),
        )

        title = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "scope-title-drift-flow",
            "--expected-revision",
            str(created["revision"]),
            "--action",
            "set-scope-repair-title",
            "--subject-id",
            "spec-01",
        )
        title_observation = self.base / "scope-title-drift-title.json"
        self.invoke(
            "app-operation",
            "observation",
            "create",
            "--run-id",
            "scope-title-drift-flow",
            "--expected-revision",
            str(title["revision"]),
            "--operation-id",
            str(title["operation_id"]),
            "--launch-count",
            "1",
            "--status",
            "succeeded",
            "--receipt-ref",
            "receipt:scope-title-drift",
            "--readback-ref",
            "readback:scope-title-drift",
            "--thread-id",
            "scope-title-drift-thread",
            "--observed-title",
            "🧭 Scope Repair · Example (normalized)",
            "--output",
            str(title_observation),
        )
        titled = self.invoke(
            "app-operation",
            "finish",
            "--run-id",
            "scope-title-drift-flow",
            "--expected-revision",
            str(title["revision"]),
            "--operation-id",
            str(title["operation_id"]),
            "--observation",
            str(title_observation),
        )
        self.assertEqual(titled["status"], "succeeded")
        self.assertEqual(titled["effect_warning"], "scope-repair-title-drift")

        scope_observation_path = self.base / "scope-title-drift-observation.json"
        scope_observation = self.invoke(
            "assignment",
            "scope-repair-observation",
            "create",
            "--run-id",
            "scope-title-drift-flow",
            "--expected-revision",
            str(titled["revision"]),
            "--assignment-id",
            "spec-01",
            "--repair-outcome",
            "no-op",
            "--implementation-issue-ref",
            "owner/repository#43",
            "--planning-thread-id",
            "scope-title-drift-thread",
            "--planning-result-ref",
            "planning:scope-title-drift",
            "--authoritative-readback-ref",
            "readback:scope-title-drift-source",
            "--output",
            str(scope_observation_path),
        )
        self.assertTrue(scope_observation["artifact_written"])
        revision = self.invoke(
            "app-operation",
            "begin",
            "--run-id",
            "scope-title-drift-flow",
            "--expected-revision",
            str(titled["revision"]),
            "--action",
            "send-scope-revision",
            "--subject-id",
            "spec-01",
            "--scope-repair-observation",
            str(scope_observation_path),
        )
        self.assertTrue(revision["launch_authorized"])

    def test_same_branch_conflict_can_be_reconciled(self) -> None:
        owner = self.start("branch-owner")
        waiter = self.start_same_branch("branch-waiter", 43)
        self.assertEqual(waiter["status"], "waiting-for-spec")
        self.assertEqual(waiter["waiting_assignments"][0]["owner"]["conflict_kind"], "head-branch")

        reconciled = self.invoke(
            "claim",
            "reconcile",
            "--run-id",
            "branch-waiter",
            "--expected-revision",
            str(waiter["revision"]),
            "--assignment-id",
            "spec-01",
            "--observation",
            str(
                self.recovery_observation(
                    "branch-reconcile.json",
                    "branch-owner",
                    int(owner["revision"]),
                    worker_state="completed",
                    checkout_state="not-found",
                )
            ),
        )

        self.assertTrue(reconciled["claim_acquired"])
        self.assertEqual(reconciled["state"], "planned")
        owner_state = self.invoke("run", "show", "--run-id", "branch-owner")
        self.assertEqual(owner_state["assignments"][0]["state"], "preimplementation-aborted")

    def test_same_branch_conflict_can_be_manually_abandoned(self) -> None:
        owner = self.start("branch-abandon-owner")
        waiter = self.start_same_branch("branch-abandon-waiter", 43)
        unresolved = self.invoke(
            "claim",
            "reconcile",
            "--run-id",
            "branch-abandon-waiter",
            "--expected-revision",
            str(waiter["revision"]),
            "--assignment-id",
            "spec-01",
            "--observation",
            str(
                self.recovery_observation(
                    "branch-unresolved.json",
                    "branch-abandon-owner",
                    int(owner["revision"]),
                    worker_state="unknown",
                    checkout_state="unknown",
                )
            ),
        )
        self.assertEqual(unresolved["state"], "abandoned-recovery-required")

        abandoned = self.invoke(
            "claim",
            "abandon",
            "--run-id",
            "branch-abandon-waiter",
            "--expected-revision",
            str(unresolved["revision"]),
            "--assignment-id",
            "spec-01",
            "--owner-run-id",
            "branch-abandon-owner",
            "--owner-assignment-id",
            "spec-01",
            "--owner-expected-revision",
            str(owner["revision"]),
        )

        self.assertTrue(abandoned["claim_acquired"])
        self.assertEqual(abandoned["outcome"], "manual-abandon")

    def test_reconcile_rechecks_remaining_spec_and_branch_conflicts(self) -> None:
        branch_owner = self.start("branch-first-owner")
        waiter = self.start_same_branch("branch-multi-waiter", 43)
        spec_owner_manifest = self.manifest("spec-second-owner")
        spec_owner_manifest["assignments"][0]["source_spec_ref"] = "owner/repository#43"
        spec_owner_manifest["assignments"][0]["target_branch_name"] = "feature/other"
        spec_owner = self.invoke(
            "run",
            "start",
            "--manifest",
            str(self.write_json("spec-second-owner.json", spec_owner_manifest)),
        )

        still_waiting = self.invoke(
            "claim",
            "reconcile",
            "--run-id",
            "branch-multi-waiter",
            "--expected-revision",
            str(waiter["revision"]),
            "--assignment-id",
            "spec-01",
            "--observation",
            str(
                self.recovery_observation(
                    "branch-first-release.json",
                    "branch-first-owner",
                    int(branch_owner["revision"]),
                    worker_state="completed",
                    checkout_state="not-found",
                )
            ),
        )
        self.assertFalse(still_waiting["claim_acquired"])
        self.assertEqual(still_waiting["state"], "waiting-for-spec")
        self.assertEqual(still_waiting["conflicting_owner"]["run_id"], "spec-second-owner")

        acquired = self.invoke(
            "claim",
            "reconcile",
            "--run-id",
            "branch-multi-waiter",
            "--expected-revision",
            str(still_waiting["revision"]),
            "--assignment-id",
            "spec-01",
            "--observation",
            str(
                self.recovery_observation(
                    "spec-second-release.json",
                    "spec-second-owner",
                    int(spec_owner["revision"]),
                    worker_state="completed",
                    checkout_state="not-found",
                    issue_number=43,
                )
            ),
        )
        self.assertTrue(acquired["claim_acquired"])
        self.assertEqual(acquired["state"], "planned")

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

        replay = self.invoke(
            "app-operation",
            "replay",
            "--run-id",
            "marker-flow",
            "--expected-revision",
            str(operation["revision"]),
            "--operation-id",
            str(operation["operation_id"]),
            expected=4,
        )
        self.assertEqual(replay["error"]["code"], "operation-replay-unsupported")

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
        self.assertEqual(capabilities["cli_version"], "1.1.2")
        self.assertEqual(capabilities["runtime_contract_version"], "1.0.0")
        self.assertEqual(
            capabilities["protocols"]["app_operation_observation"]["version"],
            "1.0.0",
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
