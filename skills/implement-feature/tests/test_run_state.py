from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import runpy
import sqlite3
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "run-state"


class RunStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.state_home = self.base / "state home"
        self.home = self.base / "home"
        self.home.mkdir()
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "XDG_STATE_HOME": str(self.state_home),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        self.inputs = self.base / "inputs"
        self.inputs.mkdir()
        self.repo = self.base / "repository with spaces"
        self.repo.mkdir()
        self.revision = 0

    def tearDown(self) -> None:
        self.temp.cleanup()

    @property
    def state_root(self) -> Path:
        return self.state_home / "dotagents" / "skills" / "implement-feature"

    @property
    def database(self) -> Path:
        return self.state_root / "run-state-v1.sqlite3"

    def write_json(self, name: str, value: object) -> Path:
        path = self.inputs / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def invoke(self, *args: str, expected: int = 0) -> dict[str, object]:
        result = subprocess.run(
            [str(TOOL), "--json", *args],
            env=self.env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, expected, result.stderr + result.stdout)
        payload = json.loads(result.stdout)
        if payload.get("ok") and isinstance(payload.get("revision"), int):
            self.revision = payload["revision"]
        return payload

    def manifest(self, *, run_id: str = "run-one", assignments: int = 1) -> dict[str, object]:
        sources = []
        task_rows = []
        for index in range(1, assignments + 1):
            source_ref = f"https://github.com/example/project/issues/{index}"
            sources.append(
                {
                    "kind": "github-issue",
                    "ref": source_ref,
                    "sha256": hashlib.sha256(f"spec-{index}".encode()).hexdigest(),
                }
            )
            task_rows.append(
                {
                    "assignment_id": f"spec-{index:02d}",
                    "source_ref": source_ref,
                    "title": f"🛠️ Feature {index}",
                    "repository_claim": "repository:github:example/project",
                    "target_branch_name": f"feature/example-{index}",
                    "allowed_paths": [f"src/feature-{index}/**"],
                    "acceptance_criteria": [f"Feature {index} works"],
                    "validation_commands": ["python3 -m unittest -q"],
                    "integration_gates": [],
                    "domain_closeout": None,
                }
            )
        return {
            "schema_version": 1,
            "run_id": run_id,
            "root_task_id": "root-thread",
            "goal_objective": "Implement the dependency-ready Feature Spec frontier",
            "sources": sources,
            "repositories": [
                {
                    "repository_claim": "repository:github:example/project",
                    "repository_path": str(self.repo),
                    "project_id": "project-one",
                    "default_branch_name": "main",
                    "git_common_dir": str(self.repo),
                }
            ],
            "assignments": task_rows,
        }

    def start(self, *, run_id: str = "run-one", assignments: int = 1) -> dict[str, object]:
        path = self.write_json(f"{run_id}-manifest.json", self.manifest(run_id=run_id, assignments=assignments))
        return self.invoke("run", "start", "--manifest", str(path))

    def operation(
        self,
        *,
        key: str,
        action: str,
        subject: str,
        result: dict[str, object],
        owner: str = "app",
        status: str = "succeeded",
        run_id: str = "run-one",
        head_sha: str | None = None,
    ) -> None:
        request = self.write_json(f"{key}-request.json", {"action": action, "subject": subject})
        begin_args = [
            "operation",
            "begin",
            "--run-id",
            run_id,
            "--expected-revision",
            str(self.revision),
            "--operation-key",
            key,
            "--owner",
            owner,
            "--action",
            action,
            "--subject-id",
            subject,
        ]
        if head_sha is not None:
            begin_args.extend(["--head-sha", head_sha])
        begin_args.extend(["--request", str(request)])
        self.invoke(*begin_args)
        result_path = self.write_json(f"{key}-{status}.json", result)
        self.invoke(
            "operation",
            "finish",
            "--run-id",
            run_id,
            "--expected-revision",
            str(self.revision),
            "--operation-key",
            key,
            "--status",
            status,
            "--result",
            str(result_path),
        )

    def bind_goal(self, *, source: str = "adopted", run_id: str = "run-one") -> str:
        digest = hashlib.sha256(
            "Implement the dependency-ready Feature Spec frontier".encode()
        ).hexdigest()
        if source == "created":
            self.operation(
                key="create-goal",
                action="create-goal",
                subject="root-thread",
                result={"status": "active", "objective_sha256": digest},
                run_id=run_id,
            )
        self.invoke(
            "goal",
            "bind",
            "--run-id",
            run_id,
            "--expected-revision",
            str(self.revision),
            "--source",
            source,
            "--objective-sha256",
            digest,
        )
        return digest

    def bind_task(self, assignment: int, *, run_id: str = "run-one") -> str:
        assignment_id = f"spec-{assignment:02d}"
        thread_id = f"thread-{assignment}"
        self.operation(
            key=f"create-task-{assignment}",
            action="create-task",
            subject=assignment_id,
            result={"thread_id": thread_id},
            run_id=run_id,
        )
        self.operation(
            key=f"title-task-{assignment}",
            action="set-task-title",
            subject=assignment_id,
            result={"thread_id": thread_id, "title": f"🛠️ Feature {assignment}"},
            run_id=run_id,
        )
        checkout = self.base / f"checkout {assignment}"
        checkout.mkdir(exist_ok=True)
        observation = self.write_json(
            f"task-{assignment}-bind.json",
            {
                "schema_version": 1,
                "assignment_id": assignment_id,
                "thread_id": thread_id,
                "observed_title": f"🛠️ Feature {assignment}",
                "project_id": "project-one",
                "repository_claim": "repository:github:example/project",
                "git_common_dir": str(self.repo),
                "checkout_path": str(checkout),
                "git_top_level": str(checkout),
                "checkout_branch": f"codex/work-{assignment}",
                "baseline_head": f"{assignment:040x}",
            },
        )
        self.invoke(
            "task",
            "bind",
            "--run-id",
            run_id,
            "--expected-revision",
            str(self.revision),
            "--observation",
            str(observation),
        )
        return thread_id

    def pass_baseline(self, assignment: int, *, run_id: str = "run-one") -> None:
        assignment_id = f"spec-{assignment:02d}"
        thread_id = f"thread-{assignment}"
        self.operation(
            key=f"bootstrap-{assignment}",
            action="send-worker-bootstrap",
            subject=assignment_id,
            result={"thread_id": thread_id},
            run_id=run_id,
        )
        observation = self.write_json(
            f"baseline-{assignment}.json",
            {
                "schema_version": 1,
                "assignment_id": assignment_id,
                "thread_id": thread_id,
                "head_sha": f"{assignment:040x}",
                "status": "passed",
            },
        )
        self.invoke(
            "task",
            "baseline",
            "--run-id",
            run_id,
            "--expected-revision",
            str(self.revision),
            "--observation",
            str(observation),
        )

    def authorize_task(self, assignment: int, *, run_id: str = "run-one") -> None:
        assignment_id = f"spec-{assignment:02d}"
        self.operation(
            key=f"authorize-{assignment}",
            action="authorize-implementation",
            subject=assignment_id,
            result={"thread_id": f"thread-{assignment}"},
            run_id=run_id,
        )
        self.invoke(
            "task",
            "authorize",
            "--run-id",
            run_id,
            "--expected-revision",
            str(self.revision),
            "--assignment-id",
            assignment_id,
        )

    def ready_task(self, assignment: int, *, run_id: str = "run-one") -> None:
        head_sha = f"{assignment + 100:040x}"
        ready_result = {
            "pr_url": f"https://github.com/example/project/pull/{assignment}",
            "head_sha": head_sha,
            "head_branch_name": f"feature/example-{assignment}",
            "base_branch_name": "main",
            "default_branch_name": "main",
            "status": "ready-for-review",
        }
        self.operation(
            key=f"ensure-pr-ready-{assignment}",
            action="ensure-pull-request-ready",
            subject=f"spec-{assignment:02d}",
            result=ready_result,
            owner="gitstack",
            run_id=run_id,
            head_sha=head_sha,
        )
        observation = self.write_json(
            f"ready-{assignment}.json",
            {
                "schema_version": 1,
                "assignment_id": f"spec-{assignment:02d}",
                "thread_id": f"thread-{assignment}",
                "head_sha": head_sha,
                "head_branch_name": f"feature/example-{assignment}",
                "base_branch_name": "main",
                "default_branch_name": "main",
                "pr_url": f"https://github.com/example/project/pull/{assignment}",
                "status": "ready-for-merge",
            },
        )
        self.invoke(
            "task",
            "ready",
            "--run-id",
            run_id,
            "--expected-revision",
            str(self.revision),
            "--observation",
            str(observation),
        )

    def complete_one_task(self, assignment: int = 1) -> None:
        self.bind_task(assignment)
        self.pass_baseline(assignment)
        self.authorize_task(assignment)
        self.ready_task(assignment)

    def test_doctor_is_read_only_and_reports_fresh_schema(self) -> None:
        payload = self.invoke("doctor")
        self.assertEqual(payload["state"], "uninitialized")
        self.assertEqual(payload["state_schema_version"], 1)
        self.assertEqual(payload["tool_version"], "1.0.0")
        self.assertFalse(self.state_root.exists())

    def test_reader_treats_an_unpublished_empty_schema_as_uninitialized(self) -> None:
        self.state_root.mkdir(mode=0o700, parents=True)
        descriptor = os.open(self.database, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(descriptor)

        doctor = self.invoke("doctor")
        self.assertEqual(doctor["state"], "uninitialized")
        self.assertFalse(doctor["writes_performed"])
        error = self.invoke("run", "list", "--status", "all", expected=3)
        self.assertEqual(error["error"]["code"], "state-uninitialized")
        started = self.start()
        self.assertTrue(started["start_authorized"])

    def test_start_persists_typed_sources_projects_and_assignments(self) -> None:
        start = self.start(assignments=2)
        self.assertTrue(start["start_authorized"])
        shown = self.invoke("run", "show", "--run-id", "run-one")
        self.assertEqual(shown["goal"]["status"], "unbound")
        self.assertEqual(shown["unbound_assignment_ids"], ["spec-01", "spec-02"])
        self.assertEqual(shown["assignments"][0]["project_id"], "project-one")
        self.assertEqual(shown["manifest"]["sources"][0]["sha256"], hashlib.sha256(b"spec-1").hexdigest())

    def test_sqlite_is_the_only_lock_and_bootstrap_returns_a_write_transaction(self) -> None:
        namespace = runpy.run_path(str(TOOL), run_name="run_state_test")
        with mock.patch.dict(os.environ, self.env, clear=True):
            connection = namespace["connect"](write=True)
            try:
                self.assertTrue(connection.in_transaction)
                connection.execute(
                    "INSERT INTO metadata(key, value) VALUES ('rollback-probe', 'present')"
                )
                connection.rollback()
            finally:
                connection.close()

        self.assertFalse((self.state_root / "run-state-v1.lock").exists())
        with contextlib.closing(sqlite3.connect(self.database)) as connection:
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 1)
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM metadata WHERE key = 'rollback-probe'"
                ).fetchone()[0],
                0,
            )
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0], 0)

    def test_busy_writer_returns_a_bounded_structured_error(self) -> None:
        namespace = runpy.run_path(str(TOOL), run_name="run_state_busy_test")
        manifest = self.write_json("busy-manifest.json", self.manifest())
        with mock.patch.dict(os.environ, self.env, clear=True):
            connection = namespace["connect"](write=True)
            connection.rollback()
            connection.close()

            blocker = sqlite3.connect(self.database, isolation_level=None)
            blocker.execute("BEGIN IMMEDIATE")
            namespace["connect"].__globals__["SQLITE_BUSY_TIMEOUT_MS"] = 1
            output = io.StringIO()
            try:
                with contextlib.redirect_stdout(output):
                    exit_code = namespace["main"](
                        ["--json", "run", "start", "--manifest", str(manifest)]
                    )
            finally:
                blocker.rollback()
                blocker.close()

        self.assertEqual(exit_code, 4)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["error"]["code"], "state-busy")

    def test_local_source_digest_is_verified_and_claimed_by_path_and_identity(self) -> None:
        source = self.base / "feature spec.md"
        source.write_text("accepted", encoding="utf-8")
        manifest = self.manifest()
        manifest["sources"] = [
            {
                "kind": "local-file",
                "ref": str(source),
                "sha256": hashlib.sha256(b"accepted").hexdigest(),
            }
        ]
        manifest["assignments"][0]["source_ref"] = str(source.resolve())
        path = self.write_json("local.json", manifest)
        payload = self.invoke("run", "start", "--manifest", str(path))
        self.assertTrue(any(item.startswith("source:path:") for item in payload["claim_keys"]))
        self.assertTrue(any(item.startswith("source:local:") for item in payload["claim_keys"]))

        source.write_text("drift", encoding="utf-8")
        changed = self.manifest(run_id="run-two")
        changed["sources"] = manifest["sources"]
        changed["assignments"][0]["source_ref"] = str(source.resolve())
        error = self.invoke(
            "run", "start", "--manifest", str(self.write_json("drift.json", changed)), expected=4
        )
        self.assertEqual(error["error"]["code"], "source-drift")

    def test_local_source_is_reobserved_inside_the_start_transaction(self) -> None:
        source = self.base / "replaced feature spec.md"
        source.write_text("accepted", encoding="utf-8")
        original_identity = source.stat().st_ino
        manifest = self.manifest()
        manifest["sources"] = [
            {
                "kind": "local-file",
                "ref": str(source),
                "sha256": hashlib.sha256(b"accepted").hexdigest(),
            }
        ]
        manifest["assignments"][0]["source_ref"] = str(source.resolve())
        manifest_path = self.write_json("replaced-source.json", manifest)
        namespace = runpy.run_path(str(TOOL), run_name="run_state_source_race_test")
        real_connect = namespace["connect"]

        def replace_after_transaction_is_acquired(*, write: bool) -> sqlite3.Connection:
            connection = real_connect(write=write)
            replacement = self.base / "source replacement.tmp"
            replacement.write_text("accepted", encoding="utf-8")
            os.replace(replacement, source)
            return connection

        namespace["command_run_start"].__globals__["connect"] = replace_after_transaction_is_acquired
        output = io.StringIO()
        with mock.patch.dict(os.environ, self.env, clear=True), contextlib.redirect_stdout(output):
            exit_code = namespace["main"](
                ["--json", "run", "start", "--manifest", str(manifest_path)]
            )

        self.assertEqual(exit_code, 0, output.getvalue())
        new_identity = source.stat().st_ino
        self.assertNotEqual(original_identity, new_identity)
        payload = json.loads(output.getvalue())
        old_claim = f"source:local:{source.stat().st_dev}:{original_identity}"
        new_claim = f"source:local:{source.stat().st_dev}:{new_identity}"
        self.assertNotIn(old_claim, payload["claim_keys"])
        self.assertIn(new_claim, payload["claim_keys"])
        with contextlib.closing(sqlite3.connect(self.database)) as connection:
            stored_claims = json.loads(
                connection.execute(
                    "SELECT claim_keys_json FROM sources WHERE run_id = 'run-one'"
                ).fetchone()[0]
            )
        self.assertEqual(stored_claims, [f"source:path:{source.resolve()}", new_claim])

    def test_same_spec_cannot_create_two_repository_tasks(self) -> None:
        second_repo = self.base / "second repo"
        second_repo.mkdir()
        manifest = self.manifest()
        manifest["repositories"].append(
            {
                "repository_claim": "repository:github:example/second",
                "repository_path": str(second_repo),
                "project_id": "project-two",
                "default_branch_name": "main",
                "git_common_dir": str(second_repo),
            }
        )
        duplicate = dict(manifest["assignments"][0])
        duplicate["assignment_id"] = "spec-02"
        duplicate["repository_claim"] = "repository:github:example/second"
        duplicate["target_branch_name"] = "feature/second"
        manifest["assignments"].append(duplicate)
        error = self.invoke(
            "run", "start", "--manifest", str(self.write_json("multi-repo-spec.json", manifest)), expected=2
        )
        self.assertEqual(error["error"]["code"], "invalid-input")
        self.assertIn("one Feature Spec source", error["error"]["message"])

    def test_repository_claims_require_distinct_physical_identities(self) -> None:
        second_repo = self.base / "second repository"
        second_repo.mkdir()
        manifest = self.manifest()
        manifest["repositories"].append(
            {
                "repository_claim": "repository:github:example/second",
                "repository_path": str(second_repo),
                "project_id": "project-two",
                "default_branch_name": "main",
                "git_common_dir": str(self.repo),
            }
        )
        error = self.invoke(
            "run",
            "start",
            "--manifest",
            str(self.write_json("duplicate-common-dir.json", manifest)),
            expected=2,
        )
        self.assertEqual(error["error"]["code"], "invalid-input")
        self.assertIn("Git common-directory identity", error["error"]["message"])

        third_common = self.base / "third common"
        third_common.mkdir()
        manifest["repositories"][1]["repository_path"] = str(self.repo)
        manifest["repositories"][1]["git_common_dir"] = str(third_common)
        error = self.invoke(
            "run",
            "start",
            "--manifest",
            str(self.write_json("duplicate-repository-path.json", manifest)),
            expected=2,
        )
        self.assertEqual(error["error"]["code"], "invalid-input")
        self.assertIn("repository_path", error["error"]["message"])

    def test_claim_conflict_is_atomic(self) -> None:
        self.start()
        error = self.invoke(
            "run",
            "start",
            "--manifest",
            str(self.write_json("second.json", self.manifest(run_id="run-two"))),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "claim-conflict")
        listed = self.invoke("run", "list", "--status", "all")
        self.assertEqual([item["run_id"] for item in listed["runs"]], ["run-one"])

    def test_concurrent_starts_have_one_claim_winner(self) -> None:
        paths = [
            self.write_json("race-one.json", self.manifest(run_id="race-one")),
            self.write_json("race-two.json", self.manifest(run_id="race-two")),
        ]

        def launch(path: Path) -> tuple[int, dict[str, object]]:
            result = subprocess.run(
                [str(TOOL), "--json", "run", "start", "--manifest", str(path)],
                env=self.env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            return result.returncode, json.loads(result.stdout)

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(launch, paths))
        self.assertEqual(sorted(code for code, _ in results), [0, 4], results)
        winner = [payload for code, payload in results if code == 0][0]
        loser = [payload for code, payload in results if code == 4][0]
        self.assertTrue(winner["start_authorized"])
        self.assertEqual(loser["error"]["code"], "claim-conflict", loser)

    def test_goal_creation_operation_is_bound_to_exact_objective(self) -> None:
        self.start()
        digest = self.bind_goal(source="created")
        shown = self.invoke("run", "show", "--run-id", "run-one")
        self.assertEqual(shown["goal"], {"source": "created", "status": "active", "objective_sha256": digest})

    def test_task_binding_requires_goal_and_exact_app_operations(self) -> None:
        self.start()
        request = self.write_json("create-without-goal.json", {"task": "spec-01"})
        error = self.invoke(
            "operation",
            "begin",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--operation-key",
            "create-task-1",
            "--owner",
            "app",
            "--action",
            "create-task",
            "--subject-id",
            "spec-01",
            "--request",
            str(request),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "invalid-operation-transition")

    def test_worker_cannot_be_authorized_before_bootstrap_and_baseline(self) -> None:
        self.start()
        self.bind_goal()
        self.bind_task(1)
        error = self.invoke(
            "task",
            "authorize",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--assignment-id",
            "spec-01",
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "invalid-task-transition")

    def test_explicit_go_operation_is_required_after_baseline(self) -> None:
        self.start()
        self.bind_goal()
        self.bind_task(1)
        self.pass_baseline(1)
        error = self.invoke(
            "task",
            "authorize",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--assignment-id",
            "spec-01",
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "missing-app-operation")
        self.authorize_task(1)

    def test_go_launch_waits_for_every_dispatched_baseline(self) -> None:
        self.start(assignments=2)
        self.bind_goal()
        self.bind_task(1)
        self.bind_task(2)
        self.pass_baseline(1)
        request = self.write_json("early-go.json", {"assignment": "spec-01"})
        error = self.invoke(
            "operation",
            "begin",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--operation-key",
            "authorize-1",
            "--owner",
            "app",
            "--action",
            "authorize-implementation",
            "--subject-id",
            "spec-01",
            "--request",
            str(request),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "baseline-fan-in-incomplete")

    def test_task_binding_rejects_project_repository_and_checkout_reuse(self) -> None:
        self.start(assignments=2)
        self.bind_goal()
        self.bind_task(1)
        self.operation(
            key="create-task-2",
            action="create-task",
            subject="spec-02",
            result={"thread_id": "thread-2"},
        )
        self.operation(
            key="title-task-2",
            action="set-task-title",
            subject="spec-02",
            result={"thread_id": "thread-2", "title": "🛠️ Feature 2"},
        )
        checkout = self.base / "checkout 1"
        base_observation = {
            "schema_version": 1,
            "assignment_id": "spec-02",
            "thread_id": "thread-2",
            "observed_title": "🛠️ Feature 2",
            "project_id": "wrong-project",
            "repository_claim": "repository:github:example/project",
            "git_common_dir": str(self.repo),
            "checkout_path": str(checkout),
            "git_top_level": str(checkout),
            "checkout_branch": "codex/work-2",
            "baseline_head": f"{2:040x}",
        }
        wrong_project = self.write_json("task-2-wrong-project.json", base_observation)
        error = self.invoke(
            "task",
            "bind",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--observation",
            str(wrong_project),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "task-repository-drift")

        base_observation["project_id"] = "project-one"
        base_observation["git_common_dir"] = str(self.base)
        wrong_git_identity = self.write_json("task-2-wrong-git-identity.json", base_observation)
        error = self.invoke(
            "task",
            "bind",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--observation",
            str(wrong_git_identity),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "task-repository-drift")

        base_observation["git_common_dir"] = str(self.repo)
        reused_checkout = self.write_json("task-2-reused-checkout.json", base_observation)
        error = self.invoke(
            "task",
            "bind",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--observation",
            str(reused_checkout),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "checkout-conflict")

    def test_ready_requires_target_branch_and_assignment_repository_pr(self) -> None:
        self.start()
        self.bind_goal()
        self.bind_task(1)
        self.pass_baseline(1)
        self.authorize_task(1)
        observation = {
            "schema_version": 1,
            "assignment_id": "spec-01",
            "thread_id": "thread-1",
            "head_sha": f"{101:040x}",
            "head_branch_name": "feature/wrong",
            "base_branch_name": "main",
            "default_branch_name": "main",
            "pr_url": "https://github.com/example/project/pull/1",
            "status": "ready-for-merge",
        }
        wrong_branch = self.write_json("ready-wrong-branch.json", observation)
        error = self.invoke(
            "task",
            "ready",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--observation",
            str(wrong_branch),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "target-branch-drift")

        observation["head_branch_name"] = "feature/example-1"
        observation["pr_url"] = "https://github.com/example/other/pull/1"
        wrong_repository = self.write_json("ready-wrong-repository.json", observation)
        error = self.invoke(
            "task",
            "ready",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--observation",
            str(wrong_repository),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "pull-request-repository-drift")

        observation["pr_url"] = "https://github.com/example/project/pull/1"
        observation["base_branch_name"] = "release"
        wrong_base = self.write_json("ready-wrong-base.json", observation)
        error = self.invoke(
            "task",
            "ready",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--observation",
            str(wrong_base),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "pull-request-base-drift")

        observation["default_branch_name"] = "release"
        wrong_default = self.write_json("ready-wrong-default.json", observation)
        error = self.invoke(
            "task",
            "ready",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--observation",
            str(wrong_default),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "pull-request-base-drift")

        observation["base_branch_name"] = "main"
        observation["default_branch_name"] = "main"
        missing_provider_result = self.write_json("ready-missing-provider-result.json", observation)
        error = self.invoke(
            "task",
            "ready",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--observation",
            str(missing_provider_result),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "missing-owner-operation")

    def test_fourth_task_refills_only_after_a_live_slot_finishes(self) -> None:
        self.start(assignments=4)
        self.bind_goal()
        for assignment in (1, 2, 3):
            self.bind_task(assignment)

        request = self.write_json("create-task-4-request.json", {"task": "spec-04"})
        blocked = self.invoke(
            "operation",
            "begin",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--operation-key",
            "create-task-4",
            "--owner",
            "app",
            "--action",
            "create-task",
            "--subject-id",
            "spec-04",
            "--request",
            str(request),
            expected=4,
        )
        self.assertEqual(blocked["error"]["code"], "task-capacity-reached")

        checkout = self.base / "checkout 4"
        checkout.mkdir()
        observation = self.write_json(
            "task-4-bind.json",
            {
                "schema_version": 1,
                "assignment_id": "spec-04",
                "thread_id": "thread-4",
                "observed_title": "🛠️ Feature 4",
                "project_id": "project-one",
                "repository_claim": "repository:github:example/project",
                "git_common_dir": str(self.repo),
                "checkout_path": str(checkout),
                "git_top_level": str(checkout),
                "checkout_branch": "codex/work-4",
                "baseline_head": f"{4:040x}",
            },
        )
        for assignment in (1, 2, 3):
            self.pass_baseline(assignment)
        self.authorize_task(1)
        self.ready_task(1)
        self.operation(
            key="create-task-4",
            action="create-task",
            subject="spec-04",
            result={"thread_id": "thread-4"},
        )
        self.operation(
            key="title-task-4",
            action="set-task-title",
            subject="spec-04",
            result={"thread_id": "thread-4", "title": "🛠️ Feature 4"},
        )
        self.invoke(
            "task",
            "bind",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--observation",
            str(observation),
        )
        shown = self.invoke("run", "show", "--run-id", "run-one")
        self.assertEqual(shown["live_task_count"], 3)
        self.assertEqual(shown["unbound_assignment_ids"], [])

    def test_goal_completion_operation_can_precede_goal_observation_and_finish(self) -> None:
        self.start()
        digest = self.bind_goal(source="created")
        self.complete_one_task()
        self.operation(
            key="complete-goal",
            action="complete-goal",
            subject="root-thread",
            result={"status": "complete", "objective_sha256": digest},
        )
        self.invoke(
            "goal",
            "complete",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--objective-sha256",
            digest,
        )
        finished = self.invoke(
            "run",
            "finish",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--outcome",
            "completed",
        )
        self.assertTrue(finished["claims_released"])
        self.assertEqual(finished["goal_status"], "completed")

    def test_goal_cannot_complete_with_unready_tasks(self) -> None:
        self.start()
        self.bind_goal()
        request = self.write_json("complete-request.json", {"goal": "root-thread"})
        error = self.invoke(
            "operation",
            "begin",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--operation-key",
            "complete-goal",
            "--owner",
            "app",
            "--action",
            "complete-goal",
            "--subject-id",
            "root-thread",
            "--request",
            str(request),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "run-not-ready")

    def test_abort_requires_exact_terminal_task_identity(self) -> None:
        self.start()
        self.bind_goal()
        self.bind_task(1)
        error = self.invoke(
            "run",
            "finish",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--outcome",
            "preimplementation-aborted",
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "tasks-not-reconciled")
        self.operation(
            key="archive-task-1",
            action="archive-task",
            subject="spec-01",
            result={"thread_id": "thread-1", "status": "archived"},
        )
        observation = self.write_json(
            "abort-task.json",
            {
                "schema_version": 1,
                "assignment_id": "spec-01",
                "thread_id": "thread-1",
                "app_status": "archived",
                "observation_ref": "codex-task://thread-1/readback",
            },
        )
        self.invoke(
            "task",
            "abort",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--observation",
            str(observation),
        )
        shown = self.invoke("run", "show", "--run-id", "run-one")
        self.assertEqual(shown["assignments"][0]["terminal_app_status"], "archived")
        self.assertEqual(
            shown["assignments"][0]["terminal_observation_ref"],
            "codex-task://thread-1/readback",
        )
        self.invoke(
            "run",
            "finish",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--outcome",
            "preimplementation-aborted",
        )
        restarted = self.invoke(
            "run",
            "start",
            "--manifest",
            str(self.write_json("restart.json", self.manifest(run_id="run-two"))),
        )
        self.assertTrue(restarted["start_authorized"])

    def test_authorized_task_cannot_use_preimplementation_start_over(self) -> None:
        self.start()
        self.bind_goal()
        self.bind_task(1)
        self.pass_baseline(1)
        self.authorize_task(1)
        observation = self.write_json(
            "unsafe-abort.json",
            {
                "schema_version": 1,
                "assignment_id": "spec-01",
                "thread_id": "thread-1",
                "app_status": "archived",
                "observation_ref": "codex-task://thread-1/readback",
            },
        )
        error = self.invoke(
            "task",
            "abort",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--observation",
            str(observation),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "implementation-already-started")

    def test_operation_journal_is_pageable_for_recovery(self) -> None:
        self.start()
        for index in range(3):
            self.operation(
                key=f"provider-{index}",
                action="readback-marker",
                subject=f"subject-{index}",
                result={"index": index},
                owner="gitstack",
            )
        first = self.invoke(
            "operation", "list", "--run-id", "run-one", "--limit", "2"
        )
        self.assertTrue(first["has_more"])
        second = self.invoke(
            "operation",
            "list",
            "--run-id",
            "run-one",
            "--after-sequence",
            str(first["next_after_sequence"]),
            "--limit",
            "2",
        )
        self.assertFalse(second["has_more"])
        self.assertEqual(len(first["operations"]) + len(second["operations"]), 3)

    def test_unknown_operation_reconciles_same_identity_without_relaunch(self) -> None:
        self.start()
        request = self.write_json("unknown-request.json", {"action": "publish"})
        self.invoke(
            "operation",
            "begin",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--operation-key",
            "publish-one",
            "--owner",
            "gitstack",
            "--action",
            "publish-delivery",
            "--subject-id",
            "spec-01",
            "--request",
            str(request),
        )
        unknown = self.write_json("unknown-result.json", {"delivery": "ambiguous"})
        self.invoke(
            "operation",
            "finish",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--operation-key",
            "publish-one",
            "--status",
            "unknown",
            "--result",
            str(unknown),
        )
        duplicate = self.invoke(
            "operation",
            "begin",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--operation-key",
            "publish-one",
            "--owner",
            "gitstack",
            "--action",
            "publish-delivery",
            "--subject-id",
            "spec-01",
            "--request",
            str(request),
            expected=4,
        )
        self.assertEqual(duplicate["error"]["code"], "operation-already-started")
        reconciled = self.write_json("reconciled-result.json", {"pr_url": "https://github.com/example/project/pull/1"})
        self.invoke(
            "operation",
            "finish",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--operation-key",
            "publish-one",
            "--status",
            "succeeded",
            "--result",
            str(reconciled),
        )
        shown = self.invoke(
            "operation", "show", "--run-id", "run-one", "--operation-key", "publish-one"
        )
        self.assertEqual([item["status"] for item in shown["operation"]["results"]], ["unknown", "succeeded"])

    def test_protected_app_action_cannot_use_a_second_key(self) -> None:
        self.start()
        self.bind_goal()
        self.operation(
            key="create-task-one",
            action="create-task",
            subject="spec-01",
            result={"thread_id": "thread-1"},
        )
        request = self.write_json("duplicate-create.json", {"task": "again"})
        error = self.invoke(
            "operation",
            "begin",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--operation-key",
            "create-task-two",
            "--owner",
            "app",
            "--action",
            "create-task",
            "--subject-id",
            "spec-01",
            "--request",
            str(request),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "protected-operation-already-started")

    def test_completed_operation_replay_is_a_noop(self) -> None:
        self.start()
        self.operation(
            key="provider-readback",
            action="provider-marker",
            subject="spec-01",
            result={"ok": True},
            owner="gitstack",
        )
        before = self.revision
        result = self.write_json("provider-replay.json", {"ok": True})
        replay = self.invoke(
            "operation",
            "finish",
            "--run-id",
            "run-one",
            "--expected-revision",
            str(self.revision),
            "--operation-key",
            "provider-readback",
            "--status",
            "succeeded",
            "--result",
            str(result),
        )
        self.assertTrue(replay["replayed"])
        self.assertEqual(replay["revision"], before)

    def test_unsupported_database_schema_has_no_migration_path(self) -> None:
        self.state_root.mkdir(parents=True)
        connection = sqlite3.connect(self.database)
        connection.execute("CREATE TABLE incompatible_state(value TEXT)")
        connection.close()
        os.chmod(self.database, 0o600)
        error = self.invoke("doctor", expected=4)
        self.assertEqual(error["error"]["code"], "unsupported-state-schema")


if __name__ == "__main__":
    unittest.main()
