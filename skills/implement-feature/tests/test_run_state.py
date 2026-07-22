from __future__ import annotations

import contextlib
import gc
import io
import json
import os
import runpy
import sqlite3
import subprocess
import tempfile
import unittest
import warnings
from pathlib import Path
from unittest import mock
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "run-state"


class RunStateScenarios(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.home = self.base / "home"
        self.home.mkdir()
        self.env = {**os.environ, "HOME": str(self.home), "PYTHONDONTWRITEBYTECODE": "1"}
        self.inputs = self.base / "inputs"
        self.inputs.mkdir()
        self.common_a = self.base / "repo a" / ".git"
        self.common_b = self.base / "repo b" / ".git"
        self.common_a.mkdir(parents=True)
        self.common_b.mkdir(parents=True)
        self.revisions: dict[str, int] = {}

    def tearDown(self) -> None:
        self.temp.cleanup()

    @property
    def database(self) -> Path:
        return self.home / ".cache" / "dotagents" / "skills" / "implement-feature" / "run-state.sqlite3"

    def write_json(self, name: str, value: object) -> Path:
        path = self.inputs / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def invoke(self, *args: str, expected: int = 0) -> dict[str, object]:
        result = subprocess.run(
            [str(TOOL), "--json", *args], env=self.env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        self.assertEqual(result.returncode, expected, result.stderr + result.stdout)
        payload = json.loads(result.stdout)
        if isinstance(payload.get("run_id"), str) and isinstance(payload.get("revision"), int):
            self.revisions[payload["run_id"]] = payload["revision"]
        return payload

    def revision(self, run_id: str) -> str:
        return str(self.revisions[run_id])

    @staticmethod
    def local_identity(path: Path) -> str:
        resolved = str(path.resolve())
        info = path.stat()
        return f"local:git-common-dir:{info.st_dev}:{info.st_ino}:{quote(resolved, safe='')}"

    def manifest(
        self,
        run_id: str,
        *,
        repositories: list[tuple[str, Path]] | None = None,
        assignment_count: int = 1,
        project_prefix: str = "project",
    ) -> dict[str, object]:
        repositories = repositories or [("github:example/project", self.common_a)]
        repo_rows = [
            {"repository_identity": identity, "git_common_dir": str(common)}
            for identity, common in repositories
        ]
        assignments = []
        for index in range(assignment_count):
            identity, _ = repositories[index % len(repositories)]
            if identity.startswith("github:"):
                owner_repository = identity.removeprefix("github:")
                source_spec_ref = f"https://github.com/{owner_repository}/issues/{index + 1}"
            else:
                source_spec_ref = f"project/planning/features/feature-{index + 1}/SPEC.md"
            assignments.append(
                {
                    "assignment_id": f"spec-{index + 1:02d}",
                    "source_spec_ref": source_spec_ref,
                    "repository_identity": identity,
                    "project_id": f"{project_prefix}-{index % len(repositories) + 1}",
                    "title": f"🛠️ Feature {index + 1}",
                    "target_branch_name": f"feature/example-{index + 1}",
                }
            )
        return {
            "schema_version": 1,
            "run_id": run_id,
            "root_task_id": f"root-{run_id}",
            "repositories": repo_rows,
            "assignments": assignments,
        }

    def start(self, run_id: str, **kwargs: object) -> dict[str, object]:
        manifest = self.manifest(run_id, **kwargs)
        return self.invoke("run", "start", "--manifest", str(self.write_json(f"{run_id}.json", manifest)))

    def operation(
        self,
        run_id: str,
        key: str,
        action: str,
        subject: str,
        extra: dict[str, object],
        *,
        status: str = "succeeded",
    ) -> dict[str, object]:
        self.invoke(
            "app-operation", "begin", "--run-id", run_id,
            "--expected-revision", self.revision(run_id), "--operation-key", key,
            "--action", action, "--subject-id", subject,
        )
        observation = {
            "schema_version": 1,
            "status": status,
            "receipt_ref": f"receipt:{key}",
            "readback_ref": f"readback:{key}",
            **extra,
        }
        return self.invoke(
            "app-operation", "finish", "--run-id", run_id,
            "--expected-revision", self.revision(run_id), "--operation-key", key,
            "--observation", str(self.write_json(f"{key}-{status}.json", observation)),
        )

    def create_goal(self, run_id: str) -> None:
        self.operation(run_id, f"goal-{run_id}", "create-goal", f"root-{run_id}", {"observed_state": "active"})

    def create_worker(self, run_id: str, number: int = 1) -> None:
        assignment = f"spec-{number:02d}"
        thread = f"thread-{run_id}-{number}"
        checkout = self.base / f"checkout {run_id} {number}"
        checkout.mkdir()
        self.operation(
            run_id, f"create-{run_id}-{number}", "create-worker", assignment,
            {
                "thread_id": thread,
                "project_id": "project-1",
                "checkout_path": str(checkout),
                "git_common_dir": str(self.common_a),
                "observed_state": "active",
            },
        )
        self.operation(
            run_id, f"title-{run_id}-{number}", "set-worker-title", assignment,
            {"thread_id": thread, "observed_title": f"🛠️ Feature {number}"},
        )
        self.operation(
            run_id, f"bootstrap-{run_id}-{number}", "send-bootstrap", assignment,
            {"thread_id": thread},
        )

    def ready_worker(self, run_id: str, number: int = 1) -> dict[str, object]:
        observation = {
            "schema_version": 1,
            "assignment_id": f"spec-{number:02d}",
            "thread_id": f"thread-{run_id}-{number}",
            "head_sha": f"{100 + number:040x}",
            "head_branch_name": f"feature/example-{number}",
            "base_branch_name": "main",
            "default_branch_name": "main",
            "pr_url": f"https://github.com/example/project/pull/{number}",
            "provider_observation_ref": f"provider:pr:{number}:head:{100 + number}",
            "status": "pr-ready-for-merge",
        }
        return self.invoke(
            "assignment", "ready", "--run-id", run_id,
            "--expected-revision", self.revision(run_id),
            "--observation", str(self.write_json(f"ready-{run_id}-{number}.json", observation)),
        )

    def finish_pr_ready(self, run_id: str) -> None:
        self.operation(run_id, f"complete-{run_id}", "complete-goal", f"root-{run_id}", {"observed_state": "completed"})
        self.invoke(
            "run", "finish", "--run-id", run_id,
            "--expected-revision", self.revision(run_id), "--outcome", "pr-ready",
        )

    def test_given_fresh_user_when_doctor_runs_then_it_is_read_only(self) -> None:
        """Given no DB, when doctor runs, then it reports schema 1 without creating cache state."""
        result = self.invoke("doctor")
        self.assertEqual(result["tool_version"], "1.0.0")
        self.assertEqual(result["state_schema_version"], 1)
        self.assertEqual(result["busy_timeout_ms"], 5000)
        self.assertFalse(self.database.exists())

    def test_given_two_app_projects_when_runs_are_disjoint_then_they_share_one_database(self) -> None:
        """Given disjoint repositories in separate App projects, when both start, then one per-user DB owns both."""
        self.start("run-a", repositories=[("github:example/a", self.common_a)], project_prefix="alpha")
        self.start("run-b", repositories=[("github:example/b", self.common_b)], project_prefix="beta")
        listing = self.invoke("run", "list", "--status", "active")
        self.assertEqual({row["run_id"] for row in listing["runs"]}, {"run-a", "run-b"})
        self.assertEqual(list(self.database.parent.glob("*.sqlite3")), [self.database])

    def test_given_one_root_task_when_second_unfinished_run_starts_then_it_is_rejected(self) -> None:
        """Given a root task owns an active run, when it starts another disjoint run, then one Goal owner is preserved."""
        self.start("first-root", repositories=[("github:example/a", self.common_a)])
        second = self.manifest("second-root", repositories=[("github:example/b", self.common_b)])
        second["root_task_id"] = "root-first-root"
        error = self.invoke(
            "run", "start", "--manifest", str(self.write_json("same-root.json", second)), expected=4,
        )
        self.assertEqual(error["error"]["code"], "root-task-already-active")

    def test_given_one_app_project_for_two_repositories_when_manifest_is_validated_then_it_fails_before_state(self) -> None:
        """Given distinct repositories share a project ID, when start validates mapping, then no worker can target the wrong repo."""
        manifest = self.manifest(
            "bad-project",
            repositories=[("github:example/a", self.common_a), ("github:example/b", self.common_b)],
            assignment_count=2,
        )
        manifest["assignments"][1]["project_id"] = manifest["assignments"][0]["project_id"]
        error = self.invoke(
            "run", "start", "--manifest", str(self.write_json("bad-project.json", manifest)), expected=2,
        )
        self.assertEqual(error["error"]["code"], "invalid-input")

    def test_given_state_writes_when_inspected_then_sqlite_is_the_only_lock(self) -> None:
        """Given a writer, when state is initialized, then BEGIN IMMEDIATE and no lock file coordinate it."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            namespace = runpy.run_path(str(TOOL), run_name="run_state_test")
            with mock.patch.dict(os.environ, self.env, clear=True):
                connection = namespace["connect"](write=True)
                try:
                    self.assertTrue(connection.in_transaction)
                    connection.rollback()
                finally:
                    connection.close()
            del namespace
            gc.collect()
        self.assertFalse(any(self.database.parent.glob("*.lock")))

    def test_given_busy_writer_when_timeout_expires_then_error_is_bounded(self) -> None:
        """Given a held transaction, when a second writer exceeds the fixed wait, then it fails state-busy."""
        manifest = self.write_json("busy.json", self.manifest("busy"))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            namespace = runpy.run_path(str(TOOL), run_name="busy_test")
            with mock.patch.dict(os.environ, self.env, clear=True):
                first = namespace["connect"](write=True)
                first.rollback()
                first.close()
                blocker = sqlite3.connect(self.database, isolation_level=None)
                blocker.execute("BEGIN IMMEDIATE")
                namespace["connect"].__globals__["SQLITE_BUSY_TIMEOUT_MS"] = 1
                output = io.StringIO()
                try:
                    with contextlib.redirect_stdout(output):
                        code = namespace["main"](["--json", "run", "start", "--manifest", str(manifest)])
                finally:
                    blocker.rollback()
                    blocker.close()
            del namespace
            gc.collect()
        self.assertEqual(code, 4)
        self.assertEqual(json.loads(output.getvalue())["error"]["code"], "state-busy")

    def test_given_same_github_spec_in_different_workspaces_when_second_starts_then_it_waits(self) -> None:
        """Given one durable Spec through two paths, when roots start, then canonical Spec identity conflicts."""
        self.start("owner", repositories=[("github:example/project", self.common_a)])
        result = self.start("waiter", repositories=[("github:example/project", self.common_b)])
        self.assertEqual(result["status"], "waiting-for-spec")
        self.assertEqual(result["acquired_assignment_ids"], [])
        self.assertEqual(result["waiting_assignments"][0]["owner"]["run_id"], "owner")

    def test_given_same_local_spec_in_linked_worktrees_when_second_starts_then_it_waits(self) -> None:
        """Given linked worktrees address one local Spec, when roots start, then that Spec has one owner."""
        identity = self.local_identity(self.common_a)
        self.start("local-owner", repositories=[(identity, self.common_a)])
        result = self.start("local-waiter", repositories=[(identity, self.common_a)])
        self.assertEqual(result["status"], "waiting-for-spec")

    def test_given_different_specs_in_same_repository_when_two_roots_start_then_both_acquire(self) -> None:
        """Given distinct durable Specs in one repository, when two roots start, then worktrees may proceed concurrently."""
        first = self.start("first-spec")
        second_manifest = self.manifest("second-spec")
        second_manifest["assignments"][0]["source_spec_ref"] = "example/project#2"
        second_manifest["assignments"][0]["target_branch_name"] = "feature/example-2"
        second = self.invoke(
            "run", "start", "--manifest", str(self.write_json("second-spec.json", second_manifest))
        )
        self.assertEqual(first["acquired_assignment_ids"], ["spec-01"])
        self.assertEqual(second["acquired_assignment_ids"], ["spec-01"])
        self.assertTrue(second["may_create_goal_or_worker"])
        self.create_goal("first-spec")
        self.create_goal("second-spec")
        self.create_worker("first-spec")
        self.create_worker("second-spec")
        self.assertEqual(self.invoke("run", "show", "--run-id", "first-spec")["assignments"][0]["state"], "active")
        self.assertEqual(self.invoke("run", "show", "--run-id", "second-spec")["assignments"][0]["state"], "active")

    def test_given_same_github_spec_in_url_and_short_form_when_roots_start_then_identity_collides(self) -> None:
        """Given URL and shorthand aliases, when roots start, then canonicalization prevents duplicate implementation."""
        self.start("url-owner")
        waiter = self.manifest("short-waiter")
        waiter["assignments"][0]["source_spec_ref"] = "example/project#1"
        result = self.invoke(
            "run", "start", "--manifest", str(self.write_json("short-waiter.json", waiter))
        )
        self.assertEqual(result["status"], "waiting-for-spec")
        self.assertEqual(result["waiting_assignments"][0]["owner"]["run_id"], "url-owner")

    def test_given_two_concurrent_roots_when_same_spec_is_claimed_then_exactly_one_acquires(self) -> None:
        """Given simultaneous starts for one Spec, when SQLite serializes writers, then exactly one root acquires it."""
        manifests = [
            self.write_json(f"concurrent-{name}.json", self.manifest(f"concurrent-{name}"))
            for name in ("a", "b")
        ]
        processes = [
            subprocess.Popen(
                [str(TOOL), "--json", "run", "start", "--manifest", str(manifest)],
                env=self.env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            for manifest in manifests
        ]
        payloads = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, stderr + stdout)
            payloads.append(json.loads(stdout))
        self.assertEqual(sorted(len(item["acquired_assignment_ids"]) for item in payloads), [0, 1])

    def test_given_different_specs_reuse_one_head_branch_when_roots_start_then_branch_owner_blocks_second(self) -> None:
        """Given distinct Specs but one head branch, when roots start, then App worktree branch ownership stays unique."""
        self.start("branch-owner")
        waiter = self.manifest("branch-waiter")
        waiter["assignments"][0]["source_spec_ref"] = "example/project#2"
        result = self.invoke(
            "run", "start", "--manifest", str(self.write_json("branch-waiter.json", waiter))
        )
        self.assertEqual(result["status"], "waiting-for-spec")
        self.assertEqual(result["waiting_assignments"][0]["owner"]["conflict_kind"], "head-branch")

    def test_given_multi_spec_request_when_one_conflicts_then_free_specs_still_acquire(self) -> None:
        """Given one of two Specs is owned, when a root starts, then its free Spec still acquires."""
        self.start("owner", repositories=[("github:example/b", self.common_b)])
        manifest = self.manifest(
            "multi", repositories=[("github:example/a", self.common_a), ("github:example/b", self.common_b)], assignment_count=2,
        )
        manifest["assignments"][1]["source_spec_ref"] = "https://github.com/example/b/issues/1"
        result = self.invoke("run", "start", "--manifest", str(self.write_json("multi.json", manifest)))
        self.assertEqual(result["acquired_assignment_ids"], ["spec-01"])
        self.assertEqual(result["waiting_assignments"][0]["assignment_id"], "spec-02")
        self.assertTrue(result["may_create_goal_or_worker"])
        shown = self.invoke("run", "show", "--run-id", "multi")
        self.assertEqual([row["active"] for row in shown["spec_claims"]], [1, 0])

    def test_given_three_same_repo_specs_when_bootstrapped_then_each_has_its_own_claim(self) -> None:
        """Given three disjoint Specs in one repo, when dispatched, then each worker has one Spec claim."""
        self.start("three", assignment_count=3)
        self.create_goal("three")
        for number in (1, 2, 3):
            self.create_worker("three", number)
        shown = self.invoke("run", "show", "--run-id", "three")
        self.assertEqual(len(shown["spec_claims"]), 3)
        self.assertTrue(all(row["active"] == 1 for row in shown["spec_claims"]))
        self.assertEqual([row["state"] for row in shown["assignments"]], ["active"] * 3)

    def test_given_three_live_workers_when_fourth_creation_begins_then_capacity_blocks(self) -> None:
        """Given three live workers, when root tries a fourth, then the generic coordinator serializes it."""
        self.start("four", assignment_count=4)
        self.create_goal("four")
        for number in (1, 2, 3):
            self.create_worker("four", number)
        error = self.invoke(
            "app-operation", "begin", "--run-id", "four", "--expected-revision", self.revision("four"),
            "--operation-key", "create-fourth", "--action", "create-worker", "--subject-id", "spec-04",
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "worker-capacity-reached")

    def test_given_no_root_goal_when_worker_creation_begins_then_controller_rejects_it(self) -> None:
        """Given claimed state but no Goal, when worker creation begins, then bootstrap authority cannot start."""
        self.start("no-goal")
        error = self.invoke(
            "app-operation", "begin", "--run-id", "no-goal",
            "--expected-revision", self.revision("no-goal"),
            "--operation-key", "early-worker", "--action", "create-worker",
            "--subject-id", "spec-01", expected=4,
        )
        self.assertEqual(error["error"]["code"], "goal-not-active")

    def test_given_no_root_goal_when_goal_completion_begins_then_controller_rejects_it(self) -> None:
        """Given planned preimplementation state but no created Goal, when completion begins, then unrelated Goal mutation is blocked."""
        self.start("no-goal-complete")
        error = self.invoke(
            "app-operation", "begin", "--run-id", "no-goal-complete",
            "--expected-revision", self.revision("no-goal-complete"),
            "--operation-key", "early-complete", "--action", "complete-goal",
            "--subject-id", "root-no-goal-complete", expected=4,
        )
        self.assertEqual(error["error"]["code"], "goal-not-active")

    def test_given_unresolved_app_effect_when_goal_completion_begins_then_controller_rejects_it(self) -> None:
        """Given PR-ready delivery and an unknown App effect, when Goal completion begins, then reconciliation comes first."""
        self.start("unresolved")
        self.create_goal("unresolved")
        self.create_worker("unresolved")
        self.ready_worker("unresolved")
        self.operation(
            "unresolved", "root-title-unknown", "set-root-title", "root-unresolved",
            {"observed_title": "Implementing"}, status="unknown",
        )
        error = self.invoke(
            "app-operation", "begin", "--run-id", "unresolved",
            "--expected-revision", self.revision("unresolved"),
            "--operation-key", "complete-too-early", "--action", "complete-goal",
            "--subject-id", "root-unresolved", expected=4,
        )
        self.assertEqual(error["error"]["code"], "unresolved-app-operations")

    def test_given_existing_worker_identity_when_stale_readback_reuses_it_then_binding_fails(self) -> None:
        """Given one worker/worktree binding, when another assignment receives the same readback, then it cannot alias."""
        self.start("alias", assignment_count=2)
        self.create_goal("alias")
        self.create_worker("alias", 1)
        self.invoke(
            "app-operation", "begin", "--run-id", "alias",
            "--expected-revision", self.revision("alias"),
            "--operation-key", "create-alias-2", "--action", "create-worker",
            "--subject-id", "spec-02",
        )
        stale = {
            "schema_version": 1, "status": "succeeded",
            "receipt_ref": "receipt:create-alias-2", "readback_ref": "readback:create-alias-2",
            "thread_id": "thread-alias-1", "project_id": "project-1",
            "checkout_path": str(self.base / "checkout alias 1"),
            "git_common_dir": str(self.common_a), "observed_state": "active",
        }
        error = self.invoke(
            "app-operation", "finish", "--run-id", "alias",
            "--expected-revision", self.revision("alias"),
            "--operation-key", "create-alias-2",
            "--observation", str(self.write_json("stale-alias.json", stale)), expected=4,
        )
        self.assertEqual(error["error"]["code"], "worker-identity-conflict")

    def test_given_nondefault_pr_base_when_ready_is_recorded_then_controller_rejects_it(self) -> None:
        """Given provider default main but PR base release, when root records ready, then claims cannot release."""
        self.start("wrong-base")
        self.create_goal("wrong-base")
        self.create_worker("wrong-base")
        observation = {
            "schema_version": 1, "assignment_id": "spec-01",
            "thread_id": "thread-wrong-base-1", "head_sha": f"{101:040x}",
            "head_branch_name": "feature/example-1", "base_branch_name": "release",
            "default_branch_name": "main",
            "pr_url": "https://github.com/example/project/pull/1",
            "provider_observation_ref": "provider:wrong-base", "status": "pr-ready-for-merge",
        }
        error = self.invoke(
            "assignment", "ready", "--run-id", "wrong-base",
            "--expected-revision", self.revision("wrong-base"),
            "--observation", str(self.write_json("wrong-base.json", observation)), expected=4,
        )
        self.assertEqual(error["error"]["code"], "pull-request-base-drift")

    def test_given_waiting_root_when_owner_releases_then_next_sweep_acquires_all(self) -> None:
        """Given a bounded waiter, when the owner pre-GO aborts, then one transaction acquires the free repository."""
        self.start("owner")
        self.start("waiter")
        self.invoke("run", "finish", "--run-id", "owner", "--expected-revision", self.revision("owner"), "--outcome", "preimplementation-aborted")
        result = self.invoke("run", "wait-sweep", "--run-id", "waiter", "--assignment-id", "spec-01", "--expected-revision", self.revision("waiter"))
        self.assertTrue(result["claim_acquired"])
        self.assertTrue(result["may_create_worker"])

    def test_given_unchanged_owner_when_three_sweeps_pass_then_waiter_blocks_before_app_objects(self) -> None:
        """Given an active owner, when three unchanged sweeps pass, then waiter terminates before Goal or task."""
        self.start("owner")
        self.start("waiter")
        for _ in range(3):
            result = self.invoke("run", "wait-sweep", "--run-id", "waiter", "--assignment-id", "spec-01", "--expected-revision", self.revision("waiter"))
        self.assertEqual(result["state"], "blocked-by-active-spec")
        shown = self.invoke("run", "show", "--run-id", "waiter")
        self.assertEqual(shown["goal_state"], "not-created")
        self.assertTrue(all(row["thread_id"] is None for row in shown["assignments"]))
        self.assertEqual(shown["unresolved_app_operations"], [])
        self.assertEqual(result["conflicting_owner"]["root_task_id"], "root-owner")

    def test_given_same_owner_adds_worker_when_wait_sweeps_continue_then_bound_does_not_reset(self) -> None:
        """Given one Spec owner, when its worker list changes, then stable owner identity keeps the wait bounded."""
        self.start("churn-owner", assignment_count=2)
        self.create_goal("churn-owner")
        self.start("churn-waiter")
        first = self.invoke(
            "run", "wait-sweep", "--run-id", "churn-waiter",
            "--assignment-id", "spec-01",
            "--expected-revision", self.revision("churn-waiter"),
        )
        self.assertEqual(first["unchanged_wait_sweeps"], 1)
        self.create_worker("churn-owner", 1)
        second = self.invoke(
            "run", "wait-sweep", "--run-id", "churn-waiter",
            "--assignment-id", "spec-01",
            "--expected-revision", self.revision("churn-waiter"),
        )
        self.assertEqual(second["unchanged_wait_sweeps"], 2)
        third = self.invoke(
            "run", "wait-sweep", "--run-id", "churn-waiter",
            "--assignment-id", "spec-01",
            "--expected-revision", self.revision("churn-waiter"),
        )
        self.assertEqual(third["state"], "blocked-by-active-spec")

    def test_given_post_bootstrap_durable_block_when_other_root_waits_then_no_takeover_occurs(self) -> None:
        """Given Root A has worker authority and blocks, when Root B waits, then A retains the repository."""
        self.start("owner")
        self.create_goal("owner")
        self.create_worker("owner")
        result = self.invoke(
            "assignment", "block", "--run-id", "owner", "--expected-revision", self.revision("owner"),
            "--assignment-id", "spec-01",
        )
        self.assertTrue(result["claim_retained"])
        self.start("waiter")
        for _ in range(3):
            blocked = self.invoke("run", "wait-sweep", "--run-id", "waiter", "--assignment-id", "spec-01", "--expected-revision", self.revision("waiter"))
        self.assertEqual(blocked["state"], "blocked-by-active-spec")
        self.assertEqual(blocked["conflicting_owner"]["thread_id"], "thread-owner-1")

    def test_given_one_assignment_blocks_when_sibling_is_active_then_run_continues_sibling(self) -> None:
        """Given one durable-contract block, when a sibling is active, then only the blocked Spec retains its claim."""
        self.start("partial-block", assignment_count=2)
        self.create_goal("partial-block")
        self.create_worker("partial-block", 1)
        self.create_worker("partial-block", 2)
        result = self.invoke(
            "assignment", "block", "--run-id", "partial-block",
            "--expected-revision", self.revision("partial-block"), "--assignment-id", "spec-01",
        )
        self.assertEqual(result["run_status"], "active")
        shown = self.invoke("run", "show", "--run-id", "partial-block")
        self.assertEqual([row["state"] for row in shown["assignments"]], ["blocked-durable-contract", "active"])

    def test_given_prebootstrap_abort_when_finished_then_claim_releases(self) -> None:
        """Given a Goal and worker but no bootstrap authority, when both reconcile terminal, then claim releases."""
        self.start("abort")
        self.create_goal("abort")
        assignment = "spec-01"
        thread = "thread-abort-1"
        checkout = self.base / "abort checkout"
        checkout.mkdir()
        self.operation(
            "abort", "create-abort", "create-worker", assignment,
            {"thread_id": thread, "project_id": "project-1", "checkout_path": str(checkout), "git_common_dir": str(self.common_a), "observed_state": "active"},
        )
        self.operation(
            "abort", "archive-abort", "archive-worker", assignment,
            {"thread_id": thread, "observed_state": "archived"},
        )
        self.operation(
            "abort", "complete-abort", "complete-goal", "root-abort",
            {"observed_state": "completed"},
        )
        result = self.invoke("run", "finish", "--run-id", "abort", "--expected-revision", self.revision("abort"), "--outcome", "preimplementation-aborted")
        self.assertTrue(result["claims_released"])
        owner = self.invoke("claim", "find", "--repository-identity", "github:example/project", "--source-spec-ref", "example/project#1")
        self.assertIsNone(owner["owner"])

    def test_given_two_planned_assignments_when_one_aborts_then_only_its_claim_releases(self) -> None:
        """Given two pre-bootstrap Specs, when one aborts, then its sibling claim remains active."""
        self.start("partial-abort", assignment_count=2)
        result = self.invoke(
            "assignment", "abort", "--run-id", "partial-abort",
            "--expected-revision", self.revision("partial-abort"), "--assignment-id", "spec-01",
        )
        self.assertTrue(result["claim_released"])
        shown = self.invoke("run", "show", "--run-id", "partial-abort")
        self.assertEqual([row["active"] for row in shown["spec_claims"]], [0, 1])
        self.assertEqual(shown["status"], "active")

    def test_given_prebootstrap_owner_missing_when_waiter_reconciles_then_abort_and_acquire_are_atomic(self) -> None:
        """Given no bootstrap and authoritative missing worker proof, when reconciled, then old claim aborts safely."""
        self.start("missing-owner")
        self.start("missing-waiter")
        observation = {
            "schema_version": 1,
            "owner_run_id": "missing-owner",
            "owner_assignment_id": "spec-01",
            "owner_expected_revision": int(self.revision("missing-owner")),
            "repository_identity": "github:example/project",
            "source_spec_ref": "example/project#1",
            "worker_state": "not-found",
            "checkout_state": "not-found",
            "readback_ref": "app-read:missing-owner-worker",
        }
        result = self.invoke(
            "claim", "reconcile", "--run-id", "missing-waiter",
            "--assignment-id", "spec-01", "--expected-revision", self.revision("missing-waiter"),
            "--observation", str(self.write_json("missing-recovery.json", observation)),
        )
        self.assertEqual(result["outcome"], "preimplementation-aborted")
        self.assertTrue(result["claim_acquired"])

    def test_given_confirmed_failed_app_operation_when_retried_then_new_key_is_allowed(self) -> None:
        """Given readback proves no Goal was created, when root retries, then a new operation key may launch."""
        self.start("retry")
        self.operation(
            "retry", "goal-failed", "create-goal", "root-retry", {}, status="failed"
        )
        result = self.invoke(
            "app-operation", "begin", "--run-id", "retry",
            "--expected-revision", self.revision("retry"),
            "--operation-key", "goal-retry", "--action", "create-goal",
            "--subject-id", "root-retry",
        )
        self.assertTrue(result["launch_authorized"])

    def test_given_pr_ready_release_when_independent_root_starts_then_it_acquires(self) -> None:
        """Given an independent Spec after PR-ready release, when it starts, then merge is not required for ownership."""
        self.start("first")
        self.create_goal("first")
        self.create_worker("first")
        self.ready_worker("first")
        self.finish_pr_ready("first")
        second = self.start("second")
        self.assertEqual(second["acquired_assignment_ids"], ["spec-01"])

    def test_given_one_assignment_ready_when_sibling_remains_active_then_only_ready_claim_releases(self) -> None:
        """Given two workers, when one becomes PR-ready, then its Spec claim releases without ending the run."""
        self.start("partial-ready", assignment_count=2)
        self.create_goal("partial-ready")
        self.create_worker("partial-ready", 1)
        self.create_worker("partial-ready", 2)
        result = self.ready_worker("partial-ready", 1)
        self.assertTrue(result["claim_released"])
        shown = self.invoke("run", "show", "--run-id", "partial-ready")
        self.assertEqual([row["active"] for row in shown["spec_claims"]], [0, 1])
        self.assertEqual(shown["status"], "active")
        self.assertEqual(shown["goal_state"], "active")

    def test_given_terminal_postbootstrap_owner_when_waiter_reconciles_then_claim_transfers_atomically(self) -> None:
        """Given authoritative terminal worker proof, when waiter reconciles, then old work is abandoned and the Spec acquires."""
        self.start("terminal-owner")
        self.create_goal("terminal-owner")
        self.create_worker("terminal-owner")
        self.start("terminal-waiter")
        observation = {
            "schema_version": 1,
            "owner_run_id": "terminal-owner",
            "owner_assignment_id": "spec-01",
            "owner_expected_revision": int(self.revision("terminal-owner")),
            "repository_identity": "github:example/project",
            "source_spec_ref": "example/project#1",
            "worker_state": "completed",
            "checkout_state": "released",
            "readback_ref": "app-read:terminal-owner-worker",
        }
        result = self.invoke(
            "claim", "reconcile", "--run-id", "terminal-waiter",
            "--assignment-id", "spec-01", "--expected-revision", self.revision("terminal-waiter"),
            "--observation", str(self.write_json("terminal-recovery.json", observation)),
        )
        self.assertEqual(result["outcome"], "abandoned")
        self.assertTrue(result["claim_acquired"])
        owner = self.invoke("run", "show", "--run-id", "terminal-owner")
        waiter = self.invoke("run", "show", "--run-id", "terminal-waiter")
        self.assertEqual(owner["assignments"][0]["state"], "abandoned")
        self.assertEqual(waiter["assignments"][0]["state"], "planned")

    def test_given_active_owner_when_waiter_reconciles_then_claim_is_preserved(self) -> None:
        """Given authoritative active worker proof, when waiter reconciles, then no takeover or revision change occurs."""
        self.start("active-owner")
        self.create_goal("active-owner")
        self.create_worker("active-owner")
        self.start("active-waiter")
        observation = {
            "schema_version": 1,
            "owner_run_id": "active-owner",
            "owner_assignment_id": "spec-01",
            "owner_expected_revision": int(self.revision("active-owner")),
            "repository_identity": "github:example/project",
            "source_spec_ref": "example/project#1",
            "worker_state": "active",
            "checkout_state": "present",
            "readback_ref": "app-read:active-owner-worker",
        }
        result = self.invoke(
            "claim", "reconcile", "--run-id", "active-waiter",
            "--assignment-id", "spec-01", "--expected-revision", self.revision("active-waiter"),
            "--observation", str(self.write_json("active-recovery.json", observation)),
        )
        self.assertEqual(result["outcome"], "owner-active")
        self.assertFalse(result["claim_acquired"])

    def test_given_terminal_worker_with_bound_checkout_when_reconciled_then_claim_is_preserved(self) -> None:
        """Given a completed task still owns its checkout, when reconciled, then a duplicate branch worktree cannot start."""
        self.start("bound-owner")
        self.create_goal("bound-owner")
        self.create_worker("bound-owner")
        self.start("bound-waiter")
        observation = {
            "schema_version": 1,
            "owner_run_id": "bound-owner",
            "owner_assignment_id": "spec-01",
            "owner_expected_revision": int(self.revision("bound-owner")),
            "repository_identity": "github:example/project",
            "source_spec_ref": "example/project#1",
            "worker_state": "completed",
            "checkout_state": "present",
            "readback_ref": "app-read:bound-owner-worker",
        }
        result = self.invoke(
            "claim", "reconcile", "--run-id", "bound-waiter",
            "--assignment-id", "spec-01", "--expected-revision", self.revision("bound-waiter"),
            "--observation", str(self.write_json("bound-recovery.json", observation)),
        )
        self.assertEqual(result["outcome"], "checkout-still-bound")
        self.assertFalse(result["claim_acquired"])

    def test_given_unknown_recovery_when_explicit_abandon_runs_then_exact_claim_transfers(self) -> None:
        """Given irrecoverable App evidence, when explicit abandon is invoked, then only that Spec claim transfers."""
        self.start("unknown-owner")
        self.create_goal("unknown-owner")
        self.create_worker("unknown-owner")
        self.start("unknown-waiter")
        observation = {
            "schema_version": 1,
            "owner_run_id": "unknown-owner",
            "owner_assignment_id": "spec-01",
            "owner_expected_revision": int(self.revision("unknown-owner")),
            "repository_identity": "github:example/project",
            "source_spec_ref": "example/project#1",
            "worker_state": "unknown",
            "checkout_state": "unknown",
            "readback_ref": "app-read:unknown-owner-worker",
        }
        reconciled = self.invoke(
            "claim", "reconcile", "--run-id", "unknown-waiter",
            "--assignment-id", "spec-01", "--expected-revision", self.revision("unknown-waiter"),
            "--observation", str(self.write_json("unknown-recovery.json", observation)),
        )
        self.assertEqual(reconciled["state"], "abandoned-recovery-required")
        abandoned = self.invoke(
            "claim", "abandon", "--run-id", "unknown-waiter",
            "--assignment-id", "spec-01", "--expected-revision", self.revision("unknown-waiter"),
            "--owner-run-id", "unknown-owner", "--owner-assignment-id", "spec-01",
            "--owner-expected-revision", self.revision("unknown-owner"),
        )
        self.assertEqual(abandoned["outcome"], "manual-abandon")
        self.assertTrue(abandoned["claim_acquired"])

    def test_given_unknown_bootstrap_effect_when_readback_arrives_then_same_key_reconciles(self) -> None:
        """Given ambiguous App delivery, when receipt readback resolves, then the same key succeeds without hashes."""
        self.start("recover")
        self.create_goal("recover")
        assignment = "spec-01"
        thread = "thread-recover-1"
        checkout = self.base / "recover checkout"
        checkout.mkdir()
        self.operation("recover", "create-recover", "create-worker", assignment, {"thread_id": thread, "project_id": "project-1", "checkout_path": str(checkout), "git_common_dir": str(self.common_a), "observed_state": "active"})
        self.operation("recover", "title-recover", "set-worker-title", assignment, {"thread_id": thread, "observed_title": "🛠️ Feature 1"})
        self.operation("recover", "bootstrap-recover", "send-bootstrap", assignment, {"thread_id": thread}, status="unknown")
        relaunch = self.invoke(
            "app-operation", "begin", "--run-id", "recover", "--expected-revision", self.revision("recover"),
            "--operation-key", "bootstrap-recover-2", "--action", "send-bootstrap", "--subject-id", assignment,
            expected=4,
        )
        self.assertEqual(relaunch["error"]["code"], "protected-operation-already-started")
        observed = {"schema_version": 1, "status": "succeeded", "receipt_ref": "receipt:bootstrap-recover", "readback_ref": "thread-read:recover", "thread_id": thread}
        result = self.invoke(
            "app-operation", "finish", "--run-id", "recover", "--expected-revision", self.revision("recover"),
            "--operation-key", "bootstrap-recover", "--observation", str(self.write_json("reconciled.json", observed)),
        )
        self.assertEqual(result["status"], "succeeded")
        with sqlite3.connect(self.database) as connection:
            columns = [row[1] for row in connection.execute("PRAGMA table_info(app_operations)")]
        self.assertFalse(any("hash" in column for column in columns))

    def test_given_unknown_bootstrap_when_archive_begins_then_worker_is_preserved(self) -> None:
        """Given bootstrap may have delivered, when preimplementation archive begins, then reconciliation is mandatory."""
        self.start("archive-unknown")
        self.create_goal("archive-unknown")
        assignment = "spec-01"
        thread = "thread-archive-unknown-1"
        checkout = self.base / "archive unknown checkout"
        checkout.mkdir()
        self.operation(
            "archive-unknown", "create-archive-unknown", "create-worker", assignment,
            {"thread_id": thread, "project_id": "project-1", "checkout_path": str(checkout), "git_common_dir": str(self.common_a), "observed_state": "active"},
        )
        self.operation(
            "archive-unknown", "title-archive-unknown", "set-worker-title", assignment,
            {"thread_id": thread, "observed_title": "🛠️ Feature 1"},
        )
        self.operation(
            "archive-unknown", "bootstrap-archive-unknown", "send-bootstrap", assignment,
            {}, status="unknown",
        )
        error = self.invoke(
            "app-operation", "begin", "--run-id", "archive-unknown",
            "--expected-revision", self.revision("archive-unknown"),
            "--operation-key", "archive-after-unknown", "--action", "archive-worker",
            "--subject-id", assignment, expected=4,
        )
        self.assertEqual(error["error"]["code"], "bootstrap-reconciliation-required")

    def test_given_unknown_app_effect_before_receipt_when_recorded_then_no_reference_is_fabricated(self) -> None:
        """Given transport ambiguity before any receipt, when unknown is recorded, then nullable typed facts preserve truth."""
        self.start("no-receipt")
        self.invoke(
            "app-operation", "begin", "--run-id", "no-receipt",
            "--expected-revision", self.revision("no-receipt"),
            "--operation-key", "goal-unknown", "--action", "create-goal",
            "--subject-id", "root-no-receipt",
        )
        observation = {"schema_version": 1, "status": "unknown"}
        result = self.invoke(
            "app-operation", "finish", "--run-id", "no-receipt",
            "--expected-revision", self.revision("no-receipt"),
            "--operation-key", "goal-unknown",
            "--observation", str(self.write_json("unknown-no-receipt.json", observation)),
        )
        self.assertEqual(result["status"], "unknown")
        operations = self.invoke("app-operation", "list", "--run-id", "no-receipt")
        self.assertIsNone(operations["operations"][0]["receipt_ref"])
        self.assertIsNone(operations["operations"][0]["readback_ref"])

    def test_given_post_bootstrap_worker_when_preimplementation_finish_is_attempted_then_release_fails(self) -> None:
        """Given worker authority has started, when root requests pre-GO release, then the claim remains."""
        self.start("started")
        self.create_goal("started")
        self.create_worker("started")
        error = self.invoke("run", "finish", "--run-id", "started", "--expected-revision", self.revision("started"), "--outcome", "preimplementation-aborted", expected=4)
        self.assertEqual(error["error"]["code"], "implementation-already-started")
        owner = self.invoke("claim", "find", "--repository-identity", "github:example/project", "--source-spec-ref", "example/project#1")
        self.assertEqual(owner["owner"]["run_id"], "started")

    def test_given_schema_when_inspected_then_only_allowlisted_state_and_no_text_hashes_exist(self) -> None:
        """Given initialized schema, when tables and columns are inspected, then storage is narrow and hash-free."""
        self.start("schema")
        with sqlite3.connect(self.database) as connection:
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
            columns = [row[1] for table in tables for row in connection.execute(f"PRAGMA table_info({table})")]
            version = connection.execute("PRAGMA user_version").fetchone()[0]
        self.assertEqual(tables, {"metadata", "runs", "assignments", "spec_claims", "app_operations"})
        self.assertEqual(version, 1)
        self.assertFalse(any("sha256" in column or "body" in column or "checklist" in column or "attempt" in column for column in columns))

    def test_given_previous_schema_one_shape_when_read_then_runtime_rejects_without_migration(self) -> None:
        """Given the retired repository-claim shape, when schema 1 opens, then the fresh runtime fails closed."""
        self.start("retired-shape")
        with sqlite3.connect(self.database) as connection:
            connection.execute("ALTER TABLE spec_claims RENAME TO repository_claims")
        error = self.invoke("doctor", expected=4)
        self.assertEqual(error["error"]["code"], "invalid-state-schema")


if __name__ == "__main__":
    unittest.main()
