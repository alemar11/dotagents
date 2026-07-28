from __future__ import annotations

import base64
import contextlib
import gc
import gzip
import hashlib
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
CLI_VERSION = "4.1.0"
RUNTIME_CONTRACT_VERSION = "4.1.0"
DATABASE_SCHEMA_VERSION = 3
HISTORICAL_RUNTIME_FIXTURES = {
    "2.0.0": {
        "commit": "52991ddca22cf358503a7572b5716dadbed4ccd4",
        "file": "run-state-2.0.0.py.gz.b64",
        "sha256": "af1ed9c8d8c685e954dd411f929b762dabee3f1052e2377d630557eb93153d7d",
    },
    "3.0.0": {
        "commit": "8c34c213b4ce8de70b56d0b7f30b7d3da7c0b156",
        "file": "run-state-3.0.0.py.gz.b64",
        "sha256": "8e54d2926bba5aab3d39f79248e351db8f886dcaf24d5bfa31deb80940749068",
    },
}
PROTOCOLS = {
    "cli": {
        "schema": "implement-feature/cli-envelope",
        "schema_version": "3.0.0",
    },
    "manifest": {
        "schema": "implement-feature/run-manifest",
        "schema_version": "3.0.0",
    },
    "feature_spec_set_input": {
        "schema": "implement-feature/feature-spec-set-input",
        "schema_version": "1.0.0",
    },
    "operation": {
        "schema": "implement-feature/app-operation-observation",
        "schema_version": "2.0.0",
    },
    "ready": {
        "schema": "implement-feature/delivery-ready-observation",
        "schema_version": "2.0.0",
    },
    "recovery": {
        "schema": "implement-feature/recovery-observation",
        "schema_version": "2.0.0",
    },
    "resume": {
        "schema": "implement-feature/assignment-resume-observation",
        "schema_version": "2.0.0",
    },
}

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
        self.invoke("state", "prepare")

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
        return self.invoke_tool(TOOL, *args, expected=expected)

    def invoke_tool(
        self, tool: Path, *args: str, expected: int = 0
    ) -> dict[str, object]:
        result = subprocess.run(
            [str(tool), "--json", *args], env=self.env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        self.assertEqual(result.returncode, expected, result.stderr + result.stdout)
        payload = json.loads(result.stdout)
        if isinstance(payload.get("run_id"), str) and isinstance(payload.get("revision"), int):
            self.revisions[payload["run_id"]] = payload["revision"]
        return payload

    @staticmethod
    def protocol(name: str) -> dict[str, str]:
        return dict(PROTOCOLS[name])

    def replace_with_schema_one(self, *, active: bool = False) -> None:
        """Replace the prepared database with a structurally valid legacy schema."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            namespace = runpy.run_path(str(TOOL), run_name="schema_one_fixture")
        self.database.unlink()
        self.database.with_name(f"{self.database.name}-wal").unlink(missing_ok=True)
        self.database.with_name(f"{self.database.name}-shm").unlink(missing_ok=True)
        connection = sqlite3.connect(self.database)
        try:
            namespace["create_schema"](connection, schema_version=1)
            if active:
                connection.execute(
                    """INSERT INTO runs(
                           run_id,root_task_id,status,revision,implementation_started,
                           created_at,updated_at
                       ) VALUES (?,?,?,?,?,?,?)""",
                    (
                        "legacy-active",
                        "root-legacy-active",
                        "active",
                        0,
                        0,
                        "2026-01-01T00:00:00Z",
                        "2026-01-01T00:00:00Z",
                    ),
                )
            connection.commit()
        finally:
            connection.close()
        self.database.chmod(0o600)
        del namespace
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            gc.collect()

    def historical_runtime(
        self,
        version: str,
        *,
        name: str | None = None,
        append_bytes: bytes = b"",
    ) -> tuple[Path, tuple[str, str, str]]:
        """Materialize one byte-exact shipped schema-2 runtime fixture."""
        fixture = HISTORICAL_RUNTIME_FIXTURES[version]
        encoded = (
            ROOT
            / "tests"
            / "fixtures"
            / str(fixture["file"])
        ).read_bytes()
        artifact = gzip.decompress(base64.b64decode(encoded))
        self.assertEqual(
            hashlib.sha256(artifact).hexdigest(),
            fixture["sha256"],
            f"historical fixture drifted from commit {fixture['commit']}",
        )
        path = self.base / (name or f"run-state-{version}")
        path.write_bytes(artifact + append_bytes)
        path.chmod(0o700)
        return (
            path,
            (
                version,
                version,
                hashlib.sha256(path.read_bytes()).hexdigest(),
            ),
        )

    def initialize_historical_schema_two(self, runtime: Path) -> None:
        """Use the retained public CLI to create its own authentic schema."""
        self.database.unlink(missing_ok=True)
        self.database.with_name(f"{self.database.name}-wal").unlink(
            missing_ok=True
        )
        self.database.with_name(f"{self.database.name}-shm").unlink(
            missing_ok=True
        )
        prepared = self.invoke_tool(runtime, "state", "prepare")
        self.assertEqual(prepared["database_schema_version"], 2)

    def start_historical_run(
        self,
        runtime: Path,
        version: str,
        run_id: str,
    ) -> dict[str, object]:
        """Create a real active owner through the historical public run API."""
        repository = f"github:example/{run_id}"
        manifest = {
            "schema": "implement-feature/run-manifest",
            "schema_version": "2.0.0",
            "runtime_contract_version": version,
            "run_id": run_id,
            "root_task_id": f"root-{run_id}",
            "repositories": [
                {
                    "repository_identity": repository,
                    "git_common_dir": str(self.common_a),
                }
            ],
            "assignments": [
                {
                    "assignment_id": "spec-01",
                    "source_spec_ref": f"example/{run_id}#1",
                    "repository_identity": repository,
                    "tracker_backend": "github",
                    "delivery_type": "github-pr",
                    "project_id": f"project-{run_id}",
                    "title": f"Historical {version} run",
                    "target_branch_name": f"feature/{run_id}",
                    "prerequisite_assignment_ids": [],
                }
            ],
        }
        return self.invoke_tool(
            runtime,
            "run",
            "start",
            "--manifest",
            str(self.write_json(f"{run_id}-historical.json", manifest)),
        )

    def finish_historical_run(self, runtime: Path, run_id: str) -> dict[str, object]:
        """Drain one owner through the retained runtime's public finish command."""
        return self.invoke_tool(
            runtime,
            "run",
            "finish",
            "--run-id",
            run_id,
            "--expected-revision",
            self.revision(run_id),
            "--outcome",
            "preimplementation-aborted",
        )

    def revision(self, run_id: str) -> str:
        return str(self.revisions[run_id])

    @staticmethod
    def local_identity(path: Path) -> str:
        resolved = str(path.resolve())
        info = path.stat()
        return f"local:git-common-dir:{info.st_dev}:{info.st_ino}:{quote(resolved, safe='')}"

    def feature_spec_member(
        self,
        name: str,
        *,
        feature_id: str,
        repository_key: str,
        table_rows: list[tuple[str, str, str]],
        criterion_id: str,
        proof_id: str | None = None,
    ) -> Path:
        table = "\n".join(
            (
                "| feature_spec_ref | affected_repository | responsibility |",
                "| --- | --- | --- |",
                *(
                    f"| {source_ref} | {repository} | {responsibility} |"
                    for source_ref, repository, responsibility in table_rows
                ),
            )
        )
        integration = (
            "\n".join(
                (
                    "",
                    "## Integration Execution Contract",
                    "",
                    f"- Proof ID: `{proof_id}`.",
                )
            )
            if proof_id is not None
            else ""
        )
        body = "\n".join(
            (
                f"# {name}",
                "",
                "## Planning Identity",
                "",
                f"- Feature ID: `{feature_id}`.",
                f"- Repository key: `{repository_key}`.",
                "",
                "## Feature Spec Set",
                "",
                table,
                "",
                "## Acceptance Criteria",
                "",
                f"- [ ] `{criterion_id}` is satisfied.",
                integration,
                "",
            )
        )
        path = self.inputs / f"{name}.md"
        path.write_text(body, encoding="utf-8")
        return path

    def feature_spec_set_input(
        self,
        *,
        feature_id: str = "123e4567-e89b-42d3-a456-426614174000",
    ) -> tuple[dict[str, object], Path, Path]:
        table_rows = [
            ("example/api#1", "github:example/api", "`api:ac-01`"),
            (
                "example/web#2",
                "github:example/web",
                "`web:ac-01` and `web:proof-api-web`",
            ),
        ]
        api = self.feature_spec_member(
            "api-spec",
            feature_id=feature_id,
            repository_key="api",
            table_rows=table_rows,
            criterion_id="api:ac-01",
        )
        web = self.feature_spec_member(
            "web-spec",
            feature_id=feature_id,
            repository_key="web",
            table_rows=table_rows,
            criterion_id="web:ac-01",
            proof_id="web:proof-api-web",
        )
        return (
            {
                **self.protocol("feature_spec_set_input"),
                "members": [
                    {
                        "source_spec_ref": "example/web#2",
                        "affected_repository": "github:example/web",
                        "body_file": str(web),
                    },
                    {
                        "source_spec_ref": "example/api#1",
                        "affected_repository": "github:example/api",
                        "body_file": str(api),
                    },
                ],
            },
            api,
            web,
        )

    def manifest(
        self,
        run_id: str,
        *,
        repositories: list[tuple[str, Path]] | None = None,
        assignment_count: int = 1,
        project_prefix: str = "project",
        tracker_backend: str | None = None,
        delivery_type: str | None = None,
    ) -> dict[str, object]:
        repositories = repositories or [("github:example/project", self.common_a)]
        repo_rows = [
            {
                "repository_identity": identity,
                "git_common_dir": str(common),
                "project_id": f"{project_prefix}-{index + 1}",
            }
            for index, (identity, common) in enumerate(repositories)
        ]
        assignments = []
        for index in range(assignment_count):
            identity, _ = repositories[index % len(repositories)]
            assignment_tracker = tracker_backend or (
                "github" if identity.startswith("github:") else "local"
            )
            assignment_delivery = delivery_type or (
                "github-pr" if assignment_tracker == "github" else "local-branch"
            )
            if assignment_tracker == "github":
                owner_repository = identity.removeprefix("github:")
                source_spec_ref = f"https://github.com/{owner_repository}/issues/{index + 1}"
            else:
                source_spec_ref = f"project/planning/features/feature-{index + 1}/SPEC.md"
            assignments.append(
                {
                    "assignment_id": f"spec-{index + 1:02d}",
                    "source_spec_ref": source_spec_ref,
                    "repository_identity": identity,
                    "tracker_backend": assignment_tracker,
                    "delivery_type": assignment_delivery,
                    "title": f"🛠️ Feature {index + 1}",
                    "target_branch_name": f"feature/example-{index + 1}",
                    "prerequisite_assignment_ids": [],
                }
            )
        return {
            **self.protocol("manifest"),
            "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
            "run_id": run_id,
            "root_task_id": f"root-{run_id}",
            "controller_project_id": f"controller-{run_id}",
            "repositories": repo_rows,
            "assignments": assignments,
            "feature_sets": [],
        }

    def start(self, run_id: str, **kwargs: object) -> dict[str, object]:
        if not self.database.exists():
            self.invoke("state", "prepare")
        manifest = self.manifest(run_id, **kwargs)
        return self.invoke("run", "start", "--manifest", str(self.write_json(f"{run_id}.json", manifest)))

    def operation(
        self,
        run_id: str,
        label: str,
        action: str,
        subject: str,
        extra: dict[str, object],
        *,
        status: str = "succeeded",
        review_owner: str | None = None,
    ) -> dict[str, object]:
        begun = self.begin_operation(
            run_id,
            action,
            subject,
            review_owner=(
                review_owner
                if review_owner is not None
                else ("worker" if action == "send-bootstrap" else None)
            ),
        )
        observation = self.operation_observation(begun, status=status, values=extra)
        if status == "succeeded":
            observation.setdefault("receipt_ref", f"receipt:{label}")
            observation.setdefault("readback_ref", f"readback:{label}")
        elif status == "failed":
            observation.setdefault("readback_ref", f"readback:{label}")
        return self.invoke(
            "app-operation", "finish", "--run-id", run_id,
            "--expected-revision", self.revision(run_id),
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(self.write_json(f"{label}-{status}.json", observation)),
        )

    def begin_operation(
        self,
        run_id: str,
        action: str,
        subject: str,
        *,
        expected: int = 0,
        review_owner: str | None = None,
    ) -> dict[str, object]:
        args = [
            "app-operation", "begin", "--run-id", run_id,
            "--expected-revision", self.revision(run_id),
            "--action", action, "--subject-id", subject,
        ]
        if review_owner is not None:
            args.extend(("--review-owner", review_owner))
        return self.invoke(*args, expected=expected)

    def operation_observation(
        self,
        begun: dict[str, object],
        *,
        status: str,
        values: dict[str, object] | None = None,
    ) -> dict[str, object]:
        observation: dict[str, object] = {
            **self.protocol("operation"),
            "operation_id": begun["operation_id"],
            "launch_count": begun["launch_count"],
            "status": status,
            **(values or {}),
        }
        if "bootstrap_id" in begun:
            observation["bootstrap_id"] = begun["bootstrap_id"]
        return observation

    def resume_observation(
        self,
        run_id: str,
        assignment_id: str,
        blocked_state: str,
        recovered_state: str,
        readback_ref: str,
        *,
        observed_run_id: str | None = None,
        run_revision: int | None = None,
    ) -> Path:
        return self.write_json(
            f"{run_id}-{assignment_id}-resume.json",
            {
                **self.protocol("resume"),
                "run_id": observed_run_id or run_id,
                "assignment_id": assignment_id,
                "run_revision": (
                    run_revision
                    if run_revision is not None
                    else int(self.revision(run_id))
                ),
                "blocked_state": blocked_state,
                "recovered_state": recovered_state,
                "readback_ref": readback_ref,
            },
        )

    def create_worker(
        self,
        run_id: str,
        number: int = 1,
        *,
        observed_state: str = "active",
        review_owner: str = "worker",
    ) -> None:
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
                "observed_state": observed_state,
            },
        )
        self.operation(
            run_id, f"title-{run_id}-{number}", "set-worker-title", assignment,
            {"thread_id": thread, "observed_title": f"🛠️ Feature {number}"},
        )
        self.operation(
            run_id, f"bootstrap-{run_id}-{number}", "send-bootstrap", assignment,
            {"thread_id": thread},
            review_owner=review_owner,
        )

    def ready_worker(
        self,
        run_id: str,
        number: int = 1,
        *,
        readiness_mode: str = "terminal",
        protocol_version: str = "2.0.0",
        review_profile: str = "standard",
        review_candidate_head_sha: str | None = None,
        codex_review_head_sha: str | None = None,
        expected: int = 0,
    ) -> dict[str, object]:
        sha = f"{100 + number:040x}"
        observation = {
            "schema": PROTOCOLS["ready"]["schema"],
            "schema_version": protocol_version,
            "assignment_id": f"spec-{number:02d}",
            "thread_id": f"thread-{run_id}-{number}",
            "repository_identity": "github:example/project",
            "delivery_type": "github-pr",
            "readiness_mode": readiness_mode,
            "head_sha": sha,
            "head_branch_name": f"feature/example-{number}",
            "base_branch_name": "main",
            "base_sha": f"{10:040x}",
            "checkout_path": str(self.base / f"checkout {run_id} {number}"),
            "worktree_clean": True,
            "base_is_ancestor": True,
            "validation_head_sha": sha,
            "autoreview_head_sha": sha,
            "review_candidate_head_sha": review_candidate_head_sha or sha,
            "review_profile": review_profile,
            "codex_review_head_sha": (
                (review_candidate_head_sha or sha)
                if review_profile == "high-risk" and codex_review_head_sha is None
                else codex_review_head_sha
            ),
            "tracker_readback_ref": f"tracker:{run_id}:{number}",
            "prerequisite_heads": {},
            "default_branch_name": "main",
            "pr_url": f"https://github.com/example/project/pull/{number}",
            "provider_observation_ref": f"provider:pr:{number}:head:{100 + number}",
            "status": "pr-ready-for-merge-but-not-merged",
        }
        return self.invoke(
            "assignment", "ready", "--run-id", run_id,
            "--expected-revision", self.revision(run_id),
            "--observation", str(self.write_json(f"ready-{run_id}-{number}.json", observation)),
            expected=expected,
        )

    def ready_local_worker(
        self,
        run_id: str,
        *,
        number: int = 1,
        repository_identity: str | None = None,
        readiness_mode: str = "terminal",
        prerequisite_heads: dict[str, str] | None = None,
        expected: int = 0,
        worktree_clean: bool = True,
        head_branch_name: str | None = None,
        head_sha: str | None = None,
        review_profile: str = "standard",
        review_candidate_head_sha: str | None = None,
        codex_review_head_sha: str | None = None,
    ) -> dict[str, object]:
        sha = head_sha or f"{200 + number:040x}"
        observation = {
            **self.protocol("ready"),
            "assignment_id": f"spec-{number:02d}",
            "thread_id": f"thread-{run_id}-{number}",
            "repository_identity": repository_identity or self.local_identity(self.common_a),
            "delivery_type": "local-branch",
            "readiness_mode": readiness_mode,
            "head_sha": sha,
            "head_branch_name": head_branch_name or f"feature/example-{number}",
            "base_branch_name": "main",
            "base_sha": f"{20:040x}",
            "checkout_path": str(self.base / f"checkout {run_id} {number}"),
            "worktree_clean": worktree_clean,
            "base_is_ancestor": True,
            "validation_head_sha": sha,
            "autoreview_head_sha": sha,
            "review_candidate_head_sha": review_candidate_head_sha or sha,
            "review_profile": review_profile,
            "codex_review_head_sha": (
                (review_candidate_head_sha or sha)
                if review_profile == "high-risk" and codex_review_head_sha is None
                else codex_review_head_sha
            ),
            "tracker_readback_ref": f"tracker:{run_id}:{number}",
            "prerequisite_heads": prerequisite_heads or {},
            "status": "local-branch-ready",
        }
        arguments = [
            "assignment", "ready", "--run-id", run_id,
            "--expected-revision", self.revision(run_id),
            "--observation", str(self.write_json(f"local-ready-{run_id}-{number}.json", observation)),
        ]
        return self.invoke(*arguments, expected=expected)

    def finish_pr_ready(self, run_id: str) -> None:
        self.invoke(
            "run", "finish", "--run-id", run_id,
            "--expected-revision", self.revision(run_id), "--outcome", "pr-ready",
        )

    def finish_local_ready(self, run_id: str) -> None:
        self.invoke(
            "run", "finish", "--run-id", run_id,
            "--expected-revision", self.revision(run_id), "--outcome", "local-branch-ready",
        )

    def test_given_fresh_user_when_doctor_runs_then_it_is_read_only(self) -> None:
        """Given no DB, doctor reports schema 3 without creating cache state."""
        self.database.unlink()
        result = self.invoke("doctor")
        self.assertEqual(result["cli_version"], CLI_VERSION)
        self.assertEqual(result["runtime_contract_version"], RUNTIME_CONTRACT_VERSION)
        self.assertEqual(result["database_schema_version"], DATABASE_SCHEMA_VERSION)
        self.assertEqual(result["runtime_artifact_sha256"], hashlib.sha256(TOOL.read_bytes()).hexdigest())
        self.assertEqual(
            result["protocols"]["feature_spec_set_input"],
            {
                "schema": PROTOCOLS["feature_spec_set_input"]["schema"],
                "version": PROTOCOLS["feature_spec_set_input"]["schema_version"],
            },
        )
        self.assertEqual(result["active_owner_runs"], 0)
        self.assertEqual(result["busy_timeout_ms"], 5000)
        self.assertFalse(self.database.exists())
        self.assertFalse(self.database.with_name("run-state.lock").exists())

    def test_given_json_mode_when_argparse_rejects_retired_ready_flag_then_typed_envelope_is_emitted(self) -> None:
        """CLI syntax errors remain machine-readable and cannot reintroduce out-of-band readiness mode."""
        error = self.invoke(
            "assignment", "ready",
            "--run-id", "unused",
            "--expected-revision", "0",
            "--observation", str(self.inputs / "unused.json"),
            "--peer-input",
            expected=2,
        )
        self.assertFalse(error["ok"])
        self.assertEqual(error["schema"], PROTOCOLS["cli"]["schema"])
        self.assertEqual(
            error["schema_version"],
            PROTOCOLS["cli"]["schema_version"],
        )
        self.assertEqual(error["cli_version"], CLI_VERSION)
        self.assertEqual(
            error["runtime_contract_version"],
            RUNTIME_CONTRACT_VERSION,
        )
        self.assertEqual(error["error"]["code"], "invalid-command-line")

    def test_given_fresh_user_when_state_prepares_then_schema_and_metadata_are_created(self) -> None:
        """Given no DB, explicit preparation creates the fresh schema-3 claim domain."""
        self.database.unlink()
        prepared = self.invoke("state", "prepare")
        self.assertEqual(prepared["state"], "initialized")
        self.assertEqual(prepared["database_schema_version"], DATABASE_SCHEMA_VERSION)
        self.assertTrue(prepared["regenerated"])
        self.assertTrue(prepared["writes_performed"])
        self.assertTrue(self.database.is_file())
        self.assertFalse(self.database.with_name("run-state.lock").exists())
        with sqlite3.connect(self.database) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT singleton,schema_version,target_schema_version FROM runtime_metadata"
                ).fetchall(),
                [(1, DATABASE_SCHEMA_VERSION, None)],
            )
        started = self.start("prepared-fresh")
        self.assertEqual(started["status"], "active")

    def test_given_linked_feature_specs_when_validated_then_membership_is_canonical_and_read_only(self) -> None:
        """Linked bodies produce one canonical manifest fragment without touching SQLite."""
        input_payload, _, _ = self.feature_spec_set_input()
        before = self.database.read_bytes()
        input_path = self.write_json("feature-spec-set.json", input_payload)

        validated = self.invoke(
            "feature-spec-set",
            "validate",
            "--input",
            str(input_path),
        )

        feature_id = "123e4567-e89b-42d3-a456-426614174000"
        self.assertEqual(validated["feature_id"], feature_id)
        self.assertEqual(validated["member_count"], 2)
        self.assertFalse(validated["writes_performed"])
        self.assertEqual(self.database.read_bytes(), before)
        self.assertEqual(
            validated["manifest_feature_set"],
            {
                "feature_id": feature_id,
                "members": [
                    {
                        "source_spec_ref": "example/api#1",
                        "repository_identity": "github:example/api",
                        "repository_key": "api",
                    },
                    {
                        "source_spec_ref": "example/web#2",
                        "repository_identity": "github:example/web",
                        "repository_key": "web",
                    },
                ],
            },
        )
        self.assertEqual(
            [member["repository_key"] for member in validated["members"]],
            ["api", "web"],
        )

        manifest = self.manifest(
            "linked-feature",
            repositories=[
                ("github:example/api", self.common_a),
                ("github:example/web", self.common_b),
            ],
            assignment_count=2,
        )
        manifest["assignments"][0]["source_spec_ref"] = "example/api#1"
        manifest["assignments"][1]["source_spec_ref"] = "example/web#2"
        manifest["feature_sets"] = [validated["manifest_feature_set"]]
        self.invoke(
            "run",
            "start",
            "--manifest",
            str(self.write_json("linked-feature-manifest.json", manifest)),
            "--feature-spec-set-input",
            str(input_path),
        )
        shown = self.invoke("run", "show", "--run-id", "linked-feature")
        self.assertEqual(
            {assignment["feature_id"] for assignment in shown["assignments"]},
            {feature_id},
        )

    def test_given_local_or_mixed_linked_sets_when_started_then_qualified_refs_decode_inside_the_owner(self) -> None:
        """All-local and mixed sets bind each portable ref to its owning repo-relative file."""
        feature_id = "123e4567-e89b-42d3-a456-426614174000"
        local_api = self.local_identity(self.common_a)
        local_web = self.local_identity(self.common_b)
        cases = (
            (
                "all-local",
                [
                    (
                        f"{feature_id}--api/planning/features/export/SPEC.md",
                        local_api,
                        "api",
                    ),
                    (
                        f"{feature_id}--web/planning/features/export/SPEC.md",
                        local_web,
                        "web",
                    ),
                ],
            ),
            (
                "mixed",
                [
                    ("example/api#1", "github:example/api", "api"),
                    (
                        f"{feature_id}--web/planning/features/export/SPEC.md",
                        local_web,
                        "web",
                    ),
                ],
            ),
        )
        for case_name, members in cases:
            with self.subTest(case=case_name):
                table_rows = sorted(
                    [
                        (
                            source_ref,
                            repository,
                            f"`{repository_key}:ac-01`",
                        )
                        for source_ref, repository, repository_key in members
                    ],
                    key=lambda row: row[1].encode("utf-8"),
                )
                body_paths = {
                    repository_key: self.feature_spec_member(
                        f"{case_name}-{repository_key}",
                        feature_id=feature_id,
                        repository_key=repository_key,
                        table_rows=table_rows,
                        criterion_id=f"{repository_key}:ac-01",
                    )
                    for _, _, repository_key in members
                }
                input_payload = {
                    **self.protocol("feature_spec_set_input"),
                    "members": [
                        {
                            "source_spec_ref": source_ref,
                            "affected_repository": repository,
                            "body_file": str(body_paths[repository_key]),
                        }
                        for source_ref, repository, repository_key in reversed(members)
                    ],
                }
                input_path = self.write_json(
                    f"{case_name}-feature-spec-set.json",
                    input_payload,
                )
                validated = self.invoke(
                    "feature-spec-set",
                    "validate",
                    "--input",
                    str(input_path),
                )
                projections = {
                    member["repository_key"]: member[
                        "repository_relative_spec_path"
                    ]
                    for member in validated["members"]
                }
                self.assertEqual(
                    projections,
                    {
                        "api": (
                            "planning/features/export/SPEC.md"
                            if case_name == "all-local"
                            else None
                        ),
                        "web": "planning/features/export/SPEC.md",
                    },
                )

                manifest = self.manifest(
                    f"{case_name}-linked",
                    repositories=[
                        (repository, self.common_a if index == 0 else self.common_b)
                        for index, (_, repository, _) in enumerate(members)
                    ],
                    assignment_count=2,
                )
                for assignment, (source_ref, _, _) in zip(
                    manifest["assignments"],
                    members,
                    strict=True,
                ):
                    assignment["source_spec_ref"] = source_ref
                manifest["feature_sets"] = [validated["manifest_feature_set"]]
                self.invoke(
                    "run",
                    "start",
                    "--manifest",
                    str(
                        self.write_json(
                            f"{case_name}-linked-manifest.json",
                            manifest,
                        )
                    ),
                    "--feature-spec-set-input",
                    str(input_path),
                )
                shown = self.invoke(
                    "run",
                    "show",
                    "--run-id",
                    f"{case_name}-linked",
                )
                self.assertEqual(
                    {assignment["feature_id"] for assignment in shown["assignments"]},
                    {feature_id},
                )

    def test_given_mismatched_local_ref_qualifier_when_validated_then_member_binding_is_rejected(self) -> None:
        """The UUID/key identity prefix cannot select or masquerade as another member."""
        feature_id = "123e4567-e89b-42d3-a456-426614174000"
        api_identity = self.local_identity(self.common_a)
        web_identity = self.local_identity(self.common_b)
        api_ref = (
            f"{feature_id}--wrong/planning/features/export/SPEC.md"
        )
        web_ref = f"{feature_id}--web/planning/features/export/SPEC.md"
        table_rows = sorted(
            [
                (api_ref, api_identity, "`api:ac-01`"),
                (web_ref, web_identity, "`web:ac-01`"),
            ],
            key=lambda row: row[1].encode("utf-8"),
        )
        api = self.feature_spec_member(
            "wrong-local-api",
            feature_id=feature_id,
            repository_key="api",
            table_rows=table_rows,
            criterion_id="api:ac-01",
        )
        web = self.feature_spec_member(
            "wrong-local-web",
            feature_id=feature_id,
            repository_key="web",
            table_rows=table_rows,
            criterion_id="web:ac-01",
        )
        error = self.invoke(
            "feature-spec-set",
            "validate",
            "--input",
            str(
                self.write_json(
                    "wrong-local-qualifier.json",
                    {
                        **self.protocol("feature_spec_set_input"),
                        "members": [
                            {
                                "source_spec_ref": api_ref,
                                "affected_repository": api_identity,
                                "body_file": str(api),
                            },
                            {
                                "source_spec_ref": web_ref,
                                "affected_repository": web_identity,
                                "body_file": str(web),
                            },
                        ],
                    },
                )
            ),
            expected=2,
        )
        self.assertEqual(error["error"]["code"], "invalid-feature-spec-set")

    def test_given_drifted_linked_feature_specs_when_validated_then_each_failure_is_closed(self) -> None:
        """Membership, table, ownership, ordering, and UUID drift are all rejected."""
        cases = (
            (
                "planning-identity-shape",
                lambda payload, api, web: api.write_text(
                    api.read_text(encoding="utf-8").replace(
                        "- Repository key: `api`.",
                        "- Repository key: `api`",
                    ),
                    encoding="utf-8",
                ),
            ),
            (
                "criterion-shape",
                lambda payload, api, web: api.write_text(
                    api.read_text(encoding="utf-8").replace(
                        "- [ ] `api:ac-01` is satisfied.",
                        "- [ ] api:ac-01 is satisfied.",
                    ),
                    encoding="utf-8",
                ),
            ),
            (
                "proof-shape",
                lambda payload, api, web: web.write_text(
                    web.read_text(encoding="utf-8").replace(
                        "- Proof ID: `web:proof-api-web`.",
                        "- Proof ID: `web:proof-api-web`",
                    ),
                    encoding="utf-8",
                ),
            ),
            (
                "feature-id-mismatch",
                lambda payload, api, web: web.write_text(
                    web.read_text(encoding="utf-8").replace(
                        "123e4567-e89b-42d3-a456-426614174000",
                        "223e4567-e89b-42d3-a456-426614174000",
                    ),
                    encoding="utf-8",
                ),
            ),
            (
                "table-mismatch",
                lambda payload, api, web: web.write_text(
                    web.read_text(encoding="utf-8").replace(
                        "`api:ac-01` |",
                        "`api:ac-01` and `api:proof-drift` |",
                    ),
                    encoding="utf-8",
                ),
            ),
            (
                "unowned-checklist-item",
                lambda payload, api, web: api.write_text(
                    api.read_text(encoding="utf-8").replace(
                        "- [ ] `api:ac-01` is satisfied.",
                        "- [ ] `api:ac-01` is satisfied.\n"
                        "- [ ] This checklist item has no stable ID.",
                    ),
                    encoding="utf-8",
                ),
            ),
            (
                "integration-without-proof-id",
                lambda payload, api, web: (
                    api.write_text(
                        api.read_text(encoding="utf-8").replace(
                            "`web:ac-01` and `web:proof-api-web`",
                            "`web:ac-01`",
                        ),
                        encoding="utf-8",
                    ),
                    web.write_text(
                        web.read_text(encoding="utf-8")
                        .replace(
                            "`web:ac-01` and `web:proof-api-web`",
                            "`web:ac-01`",
                        )
                        .replace(
                            "- Proof ID: `web:proof-api-web`.",
                            "The proof owner is not identified.",
                        ),
                        encoding="utf-8",
                    ),
                ),
            ),
            (
                "criterion-responsibility-suffix",
                lambda payload, api, web: (
                    api.write_text(
                        api.read_text(encoding="utf-8").replace(
                            "| example/api#1 | github:example/api | `api:ac-01` |",
                            "| example/api#1 | github:example/api | "
                            "`api:ac-01bogus` |",
                        ),
                        encoding="utf-8",
                    ),
                    web.write_text(
                        web.read_text(encoding="utf-8").replace(
                            "| example/api#1 | github:example/api | `api:ac-01` |",
                            "| example/api#1 | github:example/api | "
                            "`api:ac-01bogus` |",
                        ),
                        encoding="utf-8",
                    ),
                ),
            ),
            (
                "proof-responsibility-suffix",
                lambda payload, api, web: (
                    api.write_text(
                        api.read_text(encoding="utf-8").replace(
                            "`web:proof-api-web`",
                            "`web:proof-api-web.extra`",
                        ),
                        encoding="utf-8",
                    ),
                    web.write_text(
                        web.read_text(encoding="utf-8").replace(
                            "`web:ac-01` and `web:proof-api-web`",
                            "`web:ac-01` and `web:proof-api-web.extra`",
                        ),
                        encoding="utf-8",
                    ),
                ),
            ),
            (
                "duplicate-ref",
                lambda payload, api, web: payload["members"][0].__setitem__(
                    "source_spec_ref",
                    "example/api#1",
                ),
            ),
            (
                "missing-self",
                lambda payload, api, web: payload["members"][0].__setitem__(
                    "affected_repository",
                    "github:example/other",
                ),
            ),
            (
                "proposed-ref",
                lambda payload, api, web: payload["members"][0].__setitem__(
                    "source_spec_ref",
                    "proposed-spec:123e4567-e89b-42d3-a456-426614174000/web",
                ),
            ),
            (
                "reordered-table",
                lambda payload, api, web: (
                    api.write_text(
                        api.read_text(encoding="utf-8").replace(
                            "| example/api#1 | github:example/api | `api:ac-01` |\n"
                            "| example/web#2 | github:example/web | "
                            "`web:ac-01` and `web:proof-api-web` |",
                            "| example/web#2 | github:example/web | "
                            "`web:ac-01` and `web:proof-api-web` |\n"
                            "| example/api#1 | github:example/api | `api:ac-01` |",
                        ),
                        encoding="utf-8",
                    ),
                    web.write_text(
                        web.read_text(encoding="utf-8").replace(
                            "| example/api#1 | github:example/api | `api:ac-01` |\n"
                            "| example/web#2 | github:example/web | "
                            "`web:ac-01` and `web:proof-api-web` |",
                            "| example/web#2 | github:example/web | "
                            "`web:ac-01` and `web:proof-api-web` |\n"
                            "| example/api#1 | github:example/api | `api:ac-01` |",
                        ),
                        encoding="utf-8",
                    ),
                ),
            ),
            (
                "foreign-owned-id",
                lambda payload, api, web: web.write_text(
                    web.read_text(encoding="utf-8").replace(
                        "`web:ac-01` is satisfied.",
                        "`api:ac-02` is satisfied.",
                    ),
                    encoding="utf-8",
                ),
            ),
        )
        for name, mutate in cases:
            with self.subTest(name=name):
                payload, api, web = self.feature_spec_set_input()
                mutate(payload, api, web)
                error = self.invoke(
                    "feature-spec-set",
                    "validate",
                    "--input",
                    str(self.write_json(f"{name}.json", payload)),
                    expected=2,
                )
                self.assertEqual(error["error"]["code"], "invalid-feature-spec-set")

    def test_given_invalid_manifest_feature_sets_when_run_starts_then_grouping_is_rejected(self) -> None:
        """Run manifests cannot invent, duplicate, or ambiguously group linked members."""
        base = self.manifest(
            "bad-feature-set",
            repositories=[
                ("github:example/api", self.common_a),
                ("github:example/web", self.common_b),
            ],
            assignment_count=2,
        )
        base["assignments"][0]["source_spec_ref"] = "example/api#1"
        base["assignments"][1]["source_spec_ref"] = "example/web#2"
        feature_id = "123e4567-e89b-42d3-a456-426614174000"
        members = [
            {
                "source_spec_ref": "example/api#1",
                "repository_identity": "github:example/api",
                "repository_key": "api",
            },
            {
                "source_spec_ref": "example/web#2",
                "repository_identity": "github:example/web",
                "repository_key": "web",
            },
        ]
        invalid_sets = {
            "bad-uuid": [{"feature_id": "FEATURE-1", "members": members}],
            "one-member": [{"feature_id": feature_id, "members": members[:1]}],
            "unknown-member": [
                {
                    "feature_id": feature_id,
                    "members": [
                        members[0],
                        {
                            "source_spec_ref": "example/web#99",
                            "repository_identity": "github:example/web",
                            "repository_key": "web",
                        },
                    ],
                }
            ],
            "duplicate-membership": [
                {"feature_id": feature_id, "members": members},
                {
                    "feature_id": "223e4567-e89b-42d3-a456-426614174000",
                    "members": members,
                },
            ],
        }
        for name, feature_sets in invalid_sets.items():
            with self.subTest(name=name):
                manifest = dict(base)
                manifest["run_id"] = f"bad-feature-set-{name}"
                manifest["root_task_id"] = f"root-bad-feature-set-{name}"
                manifest["feature_sets"] = feature_sets
                error = self.invoke(
                    "run",
                    "start",
                    "--manifest",
                    str(self.write_json(f"bad-feature-set-{name}.json", manifest)),
                    expected=2,
                )
                self.assertEqual(error["error"]["code"], "invalid-input")

    def test_given_hand_composed_linked_membership_when_run_starts_then_evidence_is_required(self) -> None:
        """A structurally valid fragment cannot bypass current complete-body validation."""
        manifest = self.manifest(
            "unproven-feature-set",
            repositories=[
                ("github:example/api", self.common_a),
                ("github:example/web", self.common_b),
            ],
            assignment_count=2,
        )
        manifest["assignments"][0]["source_spec_ref"] = "example/api#1"
        manifest["assignments"][1]["source_spec_ref"] = "example/web#2"
        manifest["feature_sets"] = [
            {
                "feature_id": "123e4567-e89b-42d3-a456-426614174000",
                "members": [
                    {
                        "source_spec_ref": "example/api#1",
                        "repository_identity": "github:example/api",
                        "repository_key": "api",
                    },
                    {
                        "source_spec_ref": "example/web#2",
                        "repository_identity": "github:example/web",
                        "repository_key": "web",
                    },
                ],
            }
        ]
        self.database.unlink()
        error = self.invoke(
            "run",
            "start",
            "--manifest",
            str(self.write_json("unproven-feature-set.json", manifest)),
            expected=2,
        )
        self.assertEqual(
            error["error"]["code"],
            "invalid-feature-spec-set-evidence",
        )
        self.assertFalse(self.database.exists())

    def test_given_validator_projection_drift_when_run_starts_then_no_claim_is_created(self) -> None:
        """Run start revalidates current bodies and rejects a changed membership projection."""
        payload, api, web = self.feature_spec_set_input()
        input_path = self.write_json("drifted-start-input.json", payload)
        validated = self.invoke(
            "feature-spec-set",
            "validate",
            "--input",
            str(input_path),
        )
        manifest = self.manifest(
            "drifted-start",
            repositories=[
                ("github:example/api", self.common_a),
                ("github:example/web", self.common_b),
            ],
            assignment_count=2,
        )
        manifest["assignments"][0]["source_spec_ref"] = "example/api#1"
        manifest["assignments"][1]["source_spec_ref"] = "example/web#2"
        manifest["feature_sets"] = [validated["manifest_feature_set"]]
        manifest_path = self.write_json("drifted-start-manifest.json", manifest)

        for body in (api, web):
            body.write_text(
                body.read_text(encoding="utf-8").replace(
                    "123e4567-e89b-42d3-a456-426614174000",
                    "223e4567-e89b-42d3-a456-426614174000",
                ),
                encoding="utf-8",
            )

        error = self.invoke(
            "run",
            "start",
            "--manifest",
            str(manifest_path),
            "--feature-spec-set-input",
            str(input_path),
            expected=2,
        )
        self.assertEqual(
            error["error"]["code"],
            "invalid-feature-spec-set-evidence",
        )
        with sqlite3.connect(self.database) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM runs WHERE run_id='drifted-start'"
                ).fetchone(),
                (0,),
            )

    def test_given_unversioned_manifest_when_run_starts_then_payload_is_rejected_before_state(self) -> None:
        """Given an unversioned protocol payload, startup fails closed without creating the database."""
        self.database.unlink()
        manifest = self.manifest("unversioned-manifest")
        del manifest["schema"]
        error = self.invoke(
            "run", "start", "--manifest",
            str(self.write_json("unversioned-manifest.json", manifest)),
            expected=2,
        )
        self.assertEqual(error["schema"], PROTOCOLS["cli"]["schema"])
        self.assertEqual(error["schema_version"], PROTOCOLS["cli"]["schema_version"])
        self.assertEqual(error["error"]["code"], "invalid-input")
        self.assertFalse(self.database.exists())

    def test_given_retired_manifest_when_run_starts_then_payload_is_rejected_before_state(self) -> None:
        """Given the retired integer protocol payload, startup performs no compatibility conversion."""
        self.database.unlink()
        manifest = self.manifest("retired-manifest")
        manifest["schema_version"] = 1
        error = self.invoke(
            "run", "start", "--manifest",
            str(self.write_json("retired-manifest.json", manifest)),
            expected=2,
        )
        self.assertEqual(error["schema_version"], PROTOCOLS["cli"]["schema_version"])
        self.assertEqual(error["error"]["code"], "unsupported-input-protocol")
        self.assertFalse(self.database.exists())

    def test_given_newer_task_observation_when_reconciled_then_operation_remains_pending(self) -> None:
        """Given a newer task payload, reconciliation rejects it without advancing durable state."""
        self.start("v1-operation")
        begun = self.invoke(
            "app-operation", "begin", "--run-id", "v1-operation",
            "--expected-revision", self.revision("v1-operation"),
            "--action", "set-root-title",
            "--subject-id", "root-v1-operation",
        )
        revision = self.revision("v1-operation")
        observation = {
            "schema": PROTOCOLS["operation"]["schema"],
            "schema_version": "3.0.0",
            "operation_id": begun["operation_id"],
            "launch_count": begun["launch_count"],
            "status": "succeeded",
            "receipt_ref": "receipt:v1-title",
            "readback_ref": "readback:v1-title",
            "observed_title": "Feature Orchestrator",
        }
        error = self.invoke(
            "app-operation", "finish", "--run-id", "v1-operation",
            "--expected-revision", revision,
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(self.write_json("v1-operation.json", observation)),
            expected=2,
        )
        self.assertEqual(error["error"]["code"], "unsupported-input-protocol")
        shown = self.invoke("run", "show", "--run-id", "v1-operation")
        self.assertEqual(shown["revision"], int(revision))
        self.assertEqual(shown["unresolved_app_operations"][0]["status"], "pending")

    def test_given_app_operation_begin_when_authorized_then_runtime_generates_opaque_identity(self) -> None:
        """The controller allocates identity before the external effect and never accepts a caller key."""
        self.start("generated-operation")
        begun = self.begin_operation(
            "generated-operation", "set-root-title", "root-generated-operation",
        )
        self.assertRegex(str(begun["operation_id"]), r"^op-[0-9a-f]{32}$")
        self.assertEqual(begun["launch_count"], 1)
        self.assertTrue(begun["launch_authorized"])
        operations = self.invoke(
            "app-operation", "list", "--run-id", "generated-operation",
        )
        self.assertEqual(
            operations["operations"][0]["operation_id"],
            begun["operation_id"],
        )
        self.assertNotIn("operation_key", operations["operations"][0])

    def test_given_unknown_or_failed_bootstrap_with_readback_when_replayed_then_identity_is_stable(self) -> None:
        """A retry is a new launch of one logical bootstrap, not a second logical operation."""
        for status in ("unknown", "failed"):
            with self.subTest(status=status):
                run_id = f"replay-{status}"
                self.start(
                    run_id,
                    repositories=[
                        (f"github:example/replay-{status}", self.common_a),
                    ],
                )
                assignment = "spec-01"
                thread = f"thread-{run_id}-1"
                checkout = self.base / f"checkout {run_id}"
                checkout.mkdir()
                self.operation(
                    run_id, f"create-{run_id}", "create-worker", assignment,
                    {
                        "thread_id": thread,
                        "project_id": "project-1",
                        "checkout_path": str(checkout),
                        "git_common_dir": str(self.common_a),
                        "observed_state": "active",
                    },
                )
                self.operation(
                    run_id, f"title-{run_id}", "set-worker-title", assignment,
                    {"thread_id": thread, "observed_title": "🛠️ Feature 1"},
                )
                begun = self.begin_operation(
                    run_id, "send-bootstrap", assignment,
                    review_owner="worker",
                )
                observation = self.operation_observation(
                    begun,
                    status=status,
                    values={
                        "readback_ref": f"task-read:{run_id}",
                        "thread_id": thread,
                    },
                )
                finish_revision = self.revision(run_id)
                observation_path = self.write_json(
                    f"{run_id}-{status}.json", observation,
                )
                finished = self.invoke(
                    "app-operation", "finish", "--run-id", run_id,
                    "--expected-revision", finish_revision,
                    "--operation-id", str(begun["operation_id"]),
                    "--observation", str(observation_path),
                )
                self.assertTrue(finished["replay_authorized"])
                repeated = self.invoke(
                    "app-operation", "finish", "--run-id", run_id,
                    "--expected-revision", finish_revision,
                    "--operation-id", str(begun["operation_id"]),
                    "--observation", str(observation_path),
                )
                self.assertTrue(repeated["already_applied"])
                self.assertTrue(repeated["replay_authorized"])
                self.assertEqual(repeated["revision"], finished["revision"])
                replayed = self.invoke(
                    "app-operation", "replay", "--run-id", run_id,
                    "--expected-revision", self.revision(run_id),
                    "--operation-id", str(begun["operation_id"]),
                )
                self.assertEqual(replayed["operation_id"], begun["operation_id"])
                self.assertEqual(replayed["bootstrap_id"], begun["bootstrap_id"])
                self.assertEqual(replayed["review_owner"], "worker")
                self.assertEqual(replayed["launch_count"], 2)
                self.assertTrue(replayed["launch_authorized"])

    def test_given_replayed_bootstrap_when_first_launch_observation_arrives_late_then_it_is_rejected(self) -> None:
        """Delayed launch-1 evidence cannot resolve or mutate the pending launch-2 operation."""
        self.start("delayed-bootstrap")
        assignment = "spec-01"
        thread = "thread-delayed-bootstrap-1"
        checkout = self.base / "checkout delayed bootstrap"
        checkout.mkdir()
        self.operation(
            "delayed-bootstrap", "create-delayed-bootstrap",
            "create-worker", assignment,
            {
                "thread_id": thread,
                "project_id": "project-1",
                "checkout_path": str(checkout),
                "git_common_dir": str(self.common_a),
                "observed_state": "active",
            },
        )
        self.operation(
            "delayed-bootstrap", "title-delayed-bootstrap",
            "set-worker-title", assignment,
            {"thread_id": thread, "observed_title": "🛠️ Feature 1"},
        )
        first_launch = self.begin_operation(
            "delayed-bootstrap", "send-bootstrap", assignment,
            review_owner="worker",
        )
        first_unknown = self.operation_observation(
            first_launch,
            status="unknown",
            values={
                "readback_ref": "readback:delayed-bootstrap:first",
                "thread_id": thread,
            },
        )
        self.invoke(
            "app-operation", "finish", "--run-id", "delayed-bootstrap",
            "--expected-revision", self.revision("delayed-bootstrap"),
            "--operation-id", str(first_launch["operation_id"]),
            "--observation",
            str(self.write_json("delayed-bootstrap-first.json", first_unknown)),
        )
        second_launch = self.invoke(
            "app-operation", "replay", "--run-id", "delayed-bootstrap",
            "--expected-revision", self.revision("delayed-bootstrap"),
            "--operation-id", str(first_launch["operation_id"]),
        )
        self.assertEqual(second_launch["launch_count"], 2)

        stale_output = self.base / "stale-bootstrap-observation.json"
        stale_builder = self.invoke(
            "app-operation", "observation", "create",
            "--run-id", "delayed-bootstrap",
            "--expected-revision", self.revision("delayed-bootstrap"),
            "--operation-id", str(first_launch["operation_id"]),
            "--launch-count", "1",
            "--status", "unknown",
            "--readback-ref", "readback:delayed-bootstrap:first",
            "--thread-id", thread,
            "--output", str(stale_output),
            expected=4,
        )
        self.assertEqual(
            stale_builder["error"]["code"], "stale-operation-launch",
        )
        self.assertFalse(stale_output.exists())

        stale_unknown = self.invoke(
            "app-operation", "finish", "--run-id", "delayed-bootstrap",
            "--expected-revision", self.revision("delayed-bootstrap"),
            "--operation-id", str(first_launch["operation_id"]),
            "--observation",
            str(self.write_json("delayed-bootstrap-late-unknown.json", first_unknown)),
            expected=4,
        )
        self.assertEqual(
            stale_unknown["error"]["code"], "stale-operation-launch",
        )
        delayed_success = self.operation_observation(
            first_launch,
            status="succeeded",
            values={
                "receipt_ref": "receipt:delayed-bootstrap:first",
                "readback_ref": "readback:delayed-bootstrap:first",
                "thread_id": thread,
            },
        )
        stale_succeeded = self.invoke(
            "app-operation", "finish", "--run-id", "delayed-bootstrap",
            "--expected-revision", self.revision("delayed-bootstrap"),
            "--operation-id", str(first_launch["operation_id"]),
            "--observation",
            str(self.write_json(
                "delayed-bootstrap-late-succeeded.json",
                delayed_success,
            )),
            expected=4,
        )
        self.assertEqual(
            stale_succeeded["error"]["code"], "stale-operation-launch",
        )
        operation = next(
            row
            for row in self.invoke(
                "app-operation", "list", "--run-id", "delayed-bootstrap",
            )["operations"]
            if row["operation_id"] == first_launch["operation_id"]
        )
        self.assertEqual(operation["status"], "pending")
        self.assertEqual(operation["launch_count"], 2)

    def test_given_bootstrap_without_readback_or_protected_unknown_when_replayed_then_launch_is_rejected(self) -> None:
        """Replay requires authoritative readback and a status allowed for that action."""
        self.start("replay-guards")
        assignment = "spec-01"
        thread = "thread-replay-guards-1"
        checkout = self.base / "checkout replay guards"
        checkout.mkdir()
        self.operation(
            "replay-guards", "create-replay-guards", "create-worker", assignment,
            {
                "thread_id": thread,
                "project_id": "project-1",
                "checkout_path": str(checkout),
                "git_common_dir": str(self.common_a),
                "observed_state": "active",
            },
        )
        self.operation(
            "replay-guards", "title-replay-guards", "set-worker-title", assignment,
            {"thread_id": thread, "observed_title": "🛠️ Feature 1"},
        )
        bootstrap = self.begin_operation(
            "replay-guards", "send-bootstrap", assignment,
            review_owner="worker",
        )
        no_readback = self.operation_observation(
            bootstrap, status="unknown", values={"thread_id": thread},
        )
        self.invoke(
            "app-operation", "finish", "--run-id", "replay-guards",
            "--expected-revision", self.revision("replay-guards"),
            "--operation-id", str(bootstrap["operation_id"]),
            "--observation", str(self.write_json("bootstrap-no-readback.json", no_readback)),
        )
        blocked = self.invoke(
            "app-operation", "replay", "--run-id", "replay-guards",
            "--expected-revision", self.revision("replay-guards"),
            "--operation-id", str(bootstrap["operation_id"]), expected=4,
        )
        self.assertEqual(
            blocked["error"]["code"], "operation-reconciliation-required",
        )

        self.start(
            "nonbootstrap-replay",
            repositories=[("github:example/nonbootstrap-replay", self.common_a)],
        )
        ordinary = self.begin_operation(
            "nonbootstrap-replay", "set-root-title", "root-nonbootstrap-replay",
        )
        ordinary_observation = self.operation_observation(
            ordinary,
            status="unknown",
            values={"readback_ref": "task-read:nonbootstrap-replay"},
        )
        self.invoke(
            "app-operation", "finish", "--run-id", "nonbootstrap-replay",
            "--expected-revision", self.revision("nonbootstrap-replay"),
            "--operation-id", str(ordinary["operation_id"]),
            "--observation",
            str(self.write_json("nonbootstrap-unknown.json", ordinary_observation)),
        )
        blocked_status = self.invoke(
            "app-operation", "replay", "--run-id", "nonbootstrap-replay",
            "--expected-revision", self.revision("nonbootstrap-replay"),
            "--operation-id", str(ordinary["operation_id"]), expected=4,
        )
        self.assertEqual(
            blocked_status["error"]["code"],
            "operation-reconciliation-required",
        )

    def test_given_terminal_observation_when_finished_again_then_exact_replay_is_idempotent_and_drift_conflicts(self) -> None:
        """Repeated identical reconciliation is a no-op; changed terminal evidence never rewrites history."""
        self.start("idempotent-finish")
        begun = self.begin_operation(
            "idempotent-finish", "set-root-title", "root-idempotent-finish",
        )
        observation = self.operation_observation(
            begun,
            status="succeeded",
            values={
                "receipt_ref": "receipt:idempotent-finish",
                "readback_ref": "readback:idempotent-finish",
                "observed_title": "🤖 Feature Orchestrator",
            },
        )
        observation_path = self.write_json("idempotent-finish.json", observation)
        first = self.invoke(
            "app-operation", "finish", "--run-id", "idempotent-finish",
            "--expected-revision", self.revision("idempotent-finish"),
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(observation_path),
        )
        repeated = self.invoke(
            "app-operation", "finish", "--run-id", "idempotent-finish",
            "--expected-revision", self.revision("idempotent-finish"),
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(observation_path),
        )
        self.assertTrue(repeated["already_applied"])
        self.assertEqual(repeated["revision"], first["revision"])

        conflicting = {
            **observation,
            "readback_ref": "readback:conflicting-terminal-evidence",
        }
        error = self.invoke(
            "app-operation", "finish", "--run-id", "idempotent-finish",
            "--expected-revision", self.revision("idempotent-finish"),
            "--operation-id", str(begun["operation_id"]),
            "--observation",
            str(self.write_json("idempotent-finish-conflict.json", conflicting)),
            expected=4,
        )
        self.assertEqual(
            error["error"]["code"], "operation-observation-conflict",
        )

    def test_given_unknown_operation_with_recorded_facts_when_terminalized_then_facts_cannot_be_removed_or_substituted(self) -> None:
        """Reconciliation is monotonic: a later terminal result must preserve every known fact."""
        self.start("monotonic-observation")
        begun = self.begin_operation(
            "monotonic-observation",
            "set-root-title",
            "root-monotonic-observation",
        )
        unknown = self.operation_observation(
            begun,
            status="unknown",
            values={
                "receipt_ref": "receipt:monotonic-observation",
                "readback_ref": "readback:monotonic-observation",
                "observed_title": "🤖 Feature Orchestrator",
            },
        )
        self.invoke(
            "app-operation", "finish", "--run-id", "monotonic-observation",
            "--expected-revision", self.revision("monotonic-observation"),
            "--operation-id", str(begun["operation_id"]),
            "--observation",
            str(self.write_json("monotonic-unknown.json", unknown)),
        )

        removed = self.operation_observation(
            begun,
            status="failed",
            values={"readback_ref": "readback:monotonic-observation"},
        )
        removal_error = self.invoke(
            "app-operation", "finish", "--run-id", "monotonic-observation",
            "--expected-revision", self.revision("monotonic-observation"),
            "--operation-id", str(begun["operation_id"]),
            "--observation",
            str(self.write_json("monotonic-removed.json", removed)),
            expected=4,
        )
        self.assertEqual(
            removal_error["error"]["code"],
            "operation-observation-conflict",
        )

        substituted = self.operation_observation(
            begun,
            status="succeeded",
            values={
                "receipt_ref": "receipt:monotonic-observation",
                "readback_ref": "readback:substituted",
                "observed_title": "🤖 Feature Orchestrator",
            },
        )
        substitution_error = self.invoke(
            "app-operation", "finish", "--run-id", "monotonic-observation",
            "--expected-revision", self.revision("monotonic-observation"),
            "--operation-id", str(begun["operation_id"]),
            "--observation",
            str(self.write_json("monotonic-substituted.json", substituted)),
            expected=4,
        )
        self.assertEqual(
            substitution_error["error"]["code"],
            "operation-observation-conflict",
        )
        operation = self.invoke(
            "app-operation", "list", "--run-id", "monotonic-observation",
        )["operations"][0]
        self.assertEqual(operation["status"], "unknown")
        self.assertEqual(
            operation["readback_ref"],
            "readback:monotonic-observation",
        )
        self.assertEqual(
            operation["receipt_ref"],
            "receipt:monotonic-observation",
        )

    def test_given_succeeded_create_worker_when_finished_identically_after_paths_disappear_then_it_is_idempotent(self) -> None:
        """Idempotent finish compares durable evidence before any live path revalidation."""
        self.start("idempotent-create-worker")
        checkout = self.base / "idempotent create checkout"
        checkout.mkdir()
        begun = self.begin_operation(
            "idempotent-create-worker", "create-worker", "spec-01",
        )
        observation = self.operation_observation(
            begun,
            status="succeeded",
            values={
                "receipt_ref": "receipt:idempotent-create-worker",
                "readback_ref": "readback:idempotent-create-worker",
                "thread_id": "thread-idempotent-create-worker-1",
                "project_id": "project-1",
                "checkout_path": str(checkout),
                "git_common_dir": str(self.common_a),
                "observed_state": "active",
            },
        )
        observation_path = self.write_json(
            "idempotent-create-worker.json", observation,
        )
        finish_revision = self.revision("idempotent-create-worker")
        first = self.invoke(
            "app-operation", "finish", "--run-id", "idempotent-create-worker",
            "--expected-revision", finish_revision,
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(observation_path),
        )
        checkout.rmdir()
        self.common_a.rmdir()
        repeated = self.invoke(
            "app-operation", "finish", "--run-id", "idempotent-create-worker",
            "--expected-revision", finish_revision,
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(observation_path),
        )
        self.assertTrue(repeated["already_applied"])
        self.assertEqual(repeated["revision"], first["revision"])

    def test_given_operation_template_and_builder_when_rendered_then_descriptor_is_typed_and_output_never_overwrites(self) -> None:
        """The template describes fields; the builder emits one private validated payload atomically."""
        descriptor = self.invoke(
            "app-operation", "observation", "template",
            "--action", "set-root-title", "--status", "succeeded",
        )
        self.assertEqual(descriptor["observation_kind"], "app-operation")
        self.assertEqual(
            descriptor["constants"]["schema"],
            PROTOCOLS["operation"]["schema"],
        )
        self.assertIn("launch_count", descriptor["required_fields"])
        self.assertIn("observed_title", descriptor["required_fields"])
        self.assertFalse(descriptor["additional_fields"])

        worker_descriptor = self.invoke(
            "app-operation", "observation", "template",
            "--action", "create-worker", "--status", "succeeded",
        )
        self.assertEqual(
            worker_descriptor["field_constraints"]["observed_state"][
                "allowed_values"
            ],
            ["active", "idle"],
        )
        owner_descriptor = self.invoke(
            "app-operation", "observation", "template",
            "--action", "set-review-owner", "--status", "succeeded",
        )
        self.assertEqual(
            owner_descriptor["field_constraints"]["observed_state"][
                "allowed_values"
            ],
            ["root"],
        )

        self.start("operation-builder")
        begun = self.begin_operation(
            "operation-builder", "set-root-title", "root-operation-builder",
        )
        revision = self.revision("operation-builder")
        output = self.base / "operation-observation.json"
        created = self.invoke(
            "app-operation", "observation", "create",
            "--run-id", "operation-builder",
            "--expected-revision", revision,
            "--operation-id", str(begun["operation_id"]),
            "--launch-count", str(begun["launch_count"]),
            "--status", "succeeded",
            "--receipt-ref", "receipt:operation-builder",
            "--readback-ref", "readback:operation-builder",
            "--observed-title", "🤖 Feature Orchestrator",
            "--output", str(output),
        )
        self.assertEqual(created["output"], str(output))
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)
        payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["operation_id"], begun["operation_id"])
        self.assertEqual(payload["launch_count"], begun["launch_count"])
        self.assertEqual(payload["schema_version"], "2.0.0")
        shown = self.invoke("run", "show", "--run-id", "operation-builder")
        self.assertEqual(str(shown["revision"]), revision)

        before = output.read_bytes()
        duplicate = self.invoke(
            "app-operation", "observation", "create",
            "--run-id", "operation-builder",
            "--expected-revision", revision,
            "--operation-id", str(begun["operation_id"]),
            "--launch-count", str(begun["launch_count"]),
            "--status", "succeeded",
            "--receipt-ref", "receipt:operation-builder",
            "--readback-ref", "readback:operation-builder",
            "--observed-title", "🤖 Feature Orchestrator",
            "--output", str(output),
            expected=4,
        )
        self.assertEqual(duplicate["error"]["code"], "output-already-exists")
        self.assertEqual(output.read_bytes(), before)

    def test_given_bootstrap_builder_when_created_without_id_flag_then_it_derives_begin_identity(self) -> None:
        """The bootstrap descriptor and file bind the generated logical ID without caller input."""
        descriptor = self.invoke(
            "app-operation", "observation", "template",
            "--action", "send-bootstrap", "--status", "succeeded",
        )
        self.assertEqual(
            descriptor["constants"]["bootstrap_id"],
            "derived-from-operation-id",
        )
        self.assertNotIn("bootstrap_id", descriptor["required_fields"])

        self.start("bootstrap-builder")
        assignment = "spec-01"
        thread = "thread-bootstrap-builder-1"
        checkout = self.base / "checkout bootstrap builder"
        checkout.mkdir()
        self.operation(
            "bootstrap-builder", "create-bootstrap-builder",
            "create-worker", assignment,
            {
                "thread_id": thread,
                "project_id": "project-1",
                "checkout_path": str(checkout),
                "git_common_dir": str(self.common_a),
                "observed_state": "active",
            },
        )
        self.operation(
            "bootstrap-builder", "title-bootstrap-builder",
            "set-worker-title", assignment,
            {"thread_id": thread, "observed_title": "🛠️ Feature 1"},
        )
        begun = self.begin_operation(
            "bootstrap-builder", "send-bootstrap", assignment,
            review_owner="worker",
        )
        revision = self.revision("bootstrap-builder")
        output = self.base / "bootstrap-observation.json"
        self.invoke(
            "app-operation", "observation", "create",
            "--run-id", "bootstrap-builder",
            "--expected-revision", revision,
            "--operation-id", str(begun["operation_id"]),
            "--launch-count", str(begun["launch_count"]),
            "--status", "succeeded",
            "--receipt-ref", "receipt:bootstrap-builder",
            "--readback-ref", "readback:bootstrap-builder",
            "--thread-id", thread,
            "--output", str(output),
        )
        payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["operation_id"], begun["operation_id"])
        self.assertEqual(payload["launch_count"], begun["launch_count"])
        self.assertEqual(payload["bootstrap_id"], begun["bootstrap_id"])
        self.assertEqual(str(self.invoke(
            "run", "show", "--run-id", "bootstrap-builder",
        )["revision"]), revision)

    def test_given_one_assignment_when_root_title_is_verified_then_static_title_succeeds(self) -> None:
        """Given one assignment, its root title is the exact static orchestrator title."""
        self.start("single-root-title")
        result = self.operation(
            "single-root-title", "single-root-title-op", "set-root-title",
            "root-single-root-title",
            {"observed_title": "🤖 Feature Orchestrator"},
        )
        self.assertEqual(result["status"], "succeeded")

    def test_given_multiple_assignments_when_root_title_is_verified_then_total_is_static(self) -> None:
        """Given one waiting sibling, the immutable total still includes every assignment."""
        self.start("multi-root-title-owner")
        self.start("multi-root-title", assignment_count=2)
        shown = self.invoke("run", "show", "--run-id", "multi-root-title")
        self.assertEqual(
            [row["state"] for row in shown["assignments"]],
            ["waiting-for-spec", "planned"],
        )
        result = self.operation(
            "multi-root-title", "multi-root-title-op", "set-root-title",
            "root-multi-root-title",
            {"observed_title": "🤖 Feature Orchestrator · 2 Features"},
        )
        self.assertEqual(result["status"], "succeeded")

    def test_given_wrong_root_title_when_read_back_then_operation_remains_pending(self) -> None:
        """Given a wrong emoji or count, exact root-title verification fails closed."""
        self.start("wrong-root-title", assignment_count=2)
        begun = self.begin_operation(
            "wrong-root-title", "set-root-title", "root-wrong-root-title",
        )
        observation = self.operation_observation(
            begun,
            status="succeeded",
            values={
                "receipt_ref": "receipt:wrong-root-title",
                "readback_ref": "readback:wrong-root-title",
                "observed_title": "🤖 Feature Orchestrator · 1 Features",
            },
        )
        error = self.invoke(
            "app-operation", "finish", "--run-id", "wrong-root-title",
            "--expected-revision", self.revision("wrong-root-title"),
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(self.write_json("wrong-root-title.json", observation)),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "root-title-drift")
        operations = self.invoke("app-operation", "list", "--run-id", "wrong-root-title")
        self.assertEqual(operations["operations"][0]["status"], "pending")

    def test_given_verified_root_title_when_second_title_begins_then_it_is_rejected(self) -> None:
        """Given an immutable root title, another root-title mutation cannot launch."""
        self.start("repeat-root-title")
        self.operation(
            "repeat-root-title", "repeat-root-title-first", "set-root-title",
            "root-repeat-root-title",
            {"observed_title": "🤖 Feature Orchestrator"},
        )
        error = self.begin_operation(
            "repeat-root-title", "set-root-title", "root-repeat-root-title",
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "protected-operation-already-started")

    def test_given_newer_ready_observation_when_recorded_then_assignment_and_claim_remain_active(self) -> None:
        """Given newer delivery evidence, readiness rejects it without releasing ownership."""
        self.start("v1-ready")
        self.create_worker("v1-ready")
        error = self.ready_worker("v1-ready", protocol_version="3.0.0", expected=2)
        self.assertEqual(error["error"]["code"], "unsupported-input-protocol")
        shown = self.invoke("run", "show", "--run-id", "v1-ready")
        self.assertEqual(shown["assignments"][0]["state"], "active")
        self.assertEqual(shown["spec_claims"][0]["active"], 1)

    def test_given_standard_review_profile_when_ready_is_recorded_then_native_review_must_be_absent(self) -> None:
        """Given standard AutoReview, native Codex review evidence is rejected rather than treated as another gate."""
        self.start("standard-review")
        self.create_worker("standard-review")
        error = self.ready_worker(
            "standard-review",
            review_profile="standard",
            codex_review_head_sha=f"{101:040x}",
            expected=2,
        )
        self.assertEqual(error["error"]["code"], "invalid-ready-observation")
        ready = self.ready_worker("standard-review", review_profile="standard")
        self.assertEqual(ready["state"], "pr-ready")

    def test_given_high_risk_review_profile_when_ready_is_recorded_then_native_review_must_bind_head(self) -> None:
        """Given high-risk AutoReview, the one native Codex review must bind the exact candidate HEAD."""
        self.start("high-risk-review")
        self.create_worker("high-risk-review")
        error = self.ready_worker(
            "high-risk-review",
            review_profile="high-risk",
            codex_review_head_sha=f"{999:040x}",
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "stale-ready-evidence")
        ready = self.ready_worker(
            "high-risk-review",
            review_profile="high-risk",
            review_candidate_head_sha=f"{777:040x}",
        )
        self.assertEqual(ready["state"], "pr-ready")

    def test_given_unknown_review_profile_when_ready_is_recorded_then_it_fails_closed(self) -> None:
        """Given a noncanonical profile, readiness rejects it before releasing the claim."""
        self.start("unknown-review")
        self.create_worker("unknown-review")
        error = self.ready_worker(
            "unknown-review",
            review_profile="critical",
            expected=2,
        )
        self.assertEqual(error["error"]["code"], "invalid-ready-observation")

    def test_given_ready_template_and_builder_when_used_then_payload_is_derived_without_mutating_assignment(self) -> None:
        """The builder derives delivery/status from state while preserving independent readback facts."""
        descriptor = self.invoke(
            "assignment", "ready-observation", "template",
            "--delivery-type", "github-pr",
            "--review-profile", "standard",
            "--readiness-mode", "terminal",
        )
        self.assertEqual(descriptor["observation_kind"], "delivery-ready")
        self.assertEqual(
            descriptor["constants"]["schema"],
            PROTOCOLS["ready"]["schema"],
        )
        self.assertEqual(descriptor["constants"]["codex_review_head_sha"], None)
        self.assertEqual(descriptor["constants"]["readiness_mode"], "terminal")
        self.assertIn("provider_observation_ref", descriptor["required_fields"])

        self.start("ready-builder")
        self.create_worker("ready-builder")
        sha = f"{101:040x}"
        revision = self.revision("ready-builder")
        output = self.base / "ready-observation.json"
        created = self.invoke(
            "assignment", "ready-observation", "create",
            "--run-id", "ready-builder",
            "--expected-revision", revision,
            "--assignment-id", "spec-01",
            "--thread-id", "thread-ready-builder-1",
            "--repository-identity", "github:example/project",
            "--head-sha", sha,
            "--head-branch-name", "feature/example-1",
            "--base-branch-name", "main",
            "--base-sha", f"{10:040x}",
            "--checkout-path", str(self.base / "checkout ready-builder 1"),
            "--worktree-clean",
            "--base-is-ancestor",
            "--validation-head-sha", sha,
            "--autoreview-head-sha", sha,
            "--review-candidate-head-sha", sha,
            "--review-profile", "standard",
            "--readiness-mode", "terminal",
            "--tracker-readback-ref", "tracker:ready-builder:1",
            "--default-branch-name", "main",
            "--pr-url", "https://github.com/example/project/pull/1",
            "--provider-observation-ref", "provider:ready-builder:1",
            "--output", str(output),
        )
        self.assertEqual(created["output"], str(output))
        payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["delivery_type"], "github-pr")
        self.assertEqual(payload["readiness_mode"], "terminal")
        self.assertEqual(payload["status"], "pr-ready-for-merge-but-not-merged")
        self.assertIsNone(payload["codex_review_head_sha"])
        shown = self.invoke("run", "show", "--run-id", "ready-builder")
        self.assertEqual(str(shown["revision"]), revision)
        self.assertEqual(shown["assignments"][0]["state"], "active")

        ready = self.invoke(
            "assignment", "ready", "--run-id", "ready-builder",
            "--expected-revision", revision,
            "--observation", str(output),
        )
        self.assertEqual(ready["state"], "pr-ready")

    def test_given_peer_input_readiness_payload_when_consumed_then_mode_cannot_diverge_and_claim_is_retained(self) -> None:
        """The payload is the sole mode authority for both builder validation and ready mutation."""
        identity = self.local_identity(self.common_a)
        manifest = self.manifest(
            "readiness-mode",
            repositories=[(identity, self.common_a)],
            assignment_count=2,
        )
        manifest["assignments"][1]["prerequisite_assignment_ids"] = ["spec-01"]
        self.invoke(
            "run", "start", "--manifest",
            str(self.write_json("readiness-mode.json", manifest)),
        )
        self.create_worker("readiness-mode", 1)
        sha = f"{201:040x}"
        revision = self.revision("readiness-mode")
        output = self.base / "peer-input-ready-observation.json"
        self.invoke(
            "assignment", "ready-observation", "create",
            "--run-id", "readiness-mode",
            "--expected-revision", revision,
            "--assignment-id", "spec-01",
            "--thread-id", "thread-readiness-mode-1",
            "--repository-identity", identity,
            "--head-sha", sha,
            "--head-branch-name", "feature/example-1",
            "--base-branch-name", "main",
            "--base-sha", f"{20:040x}",
            "--checkout-path", str(self.base / "checkout readiness-mode 1"),
            "--worktree-clean",
            "--base-is-ancestor",
            "--validation-head-sha", sha,
            "--autoreview-head-sha", sha,
            "--review-candidate-head-sha", sha,
            "--review-profile", "standard",
            "--readiness-mode", "peer-input",
            "--tracker-readback-ref", "tracker:readiness-mode:1",
            "--output", str(output),
        )
        payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["readiness_mode"], "peer-input")

        ready = self.invoke(
            "assignment", "ready", "--run-id", "readiness-mode",
            "--expected-revision", revision,
            "--observation", str(output),
        )
        self.assertEqual(ready["state"], "peer-input-ready")
        self.assertFalse(ready["claim_released"])
        shown = self.invoke("run", "show", "--run-id", "readiness-mode")
        self.assertEqual(shown["assignments"][0]["state"], "peer-input-ready")
        self.assertEqual(shown["spec_claims"][0]["active"], 1)

    def test_given_local_only_repository_when_local_delivery_finishes_then_named_branch_is_durable(self) -> None:
        """Given no remote, when local delivery closes, then exact branch/head evidence reaches local-branch-ready."""
        identity = self.local_identity(self.common_a)
        manifest = self.manifest("local-only", repositories=[(identity, self.common_a)])
        manifest["assignments"][0]["source_spec_ref"] = "planning/features/feature-1/SPEC.md"
        self.invoke("run", "start", "--manifest", str(self.write_json("local-only.json", manifest)))
        self.create_worker("local-only")
        ready = self.ready_local_worker("local-only", repository_identity=identity)
        self.assertEqual(ready["state"], "local-branch-ready")
        self.finish_local_ready("local-only")
        shown = self.invoke("run", "show", "--run-id", "local-only")
        self.assertEqual(shown["status"], "local-branch-ready")
        self.assertEqual(shown["assignments"][0]["target_branch_name"], "feature/example-1")

    def test_given_github_identity_when_tracker_and_delivery_are_local_then_source_validation_stays_local(self) -> None:
        """Given a GitHub remote identity, when the contract is local/local, then a local Spec path remains valid."""
        self.start(
            "github-identity-local",
            tracker_backend="local",
            delivery_type="local-branch",
        )
        shown = self.invoke("run", "show", "--run-id", "github-identity-local")
        assignment = shown["assignments"][0]
        self.assertEqual(assignment["source_spec_ref"], "project/planning/features/feature-1/SPEC.md")
        self.assertEqual(assignment["delivery_type"], "local-branch")

    def test_given_retired_integration_source_ref_when_run_starts_then_it_is_rejected(self) -> None:
        """Given the removed dedicated-integration path, startup rejects it instead of treating it as a Spec."""
        manifest = self.manifest("retired-integration-ref", tracker_backend="local")
        manifest["assignments"][0]["source_spec_ref"] = (
            "project/planning/features/feature-1/integration/SPEC.md"
        )
        error = self.invoke(
            "run", "start", "--manifest",
            str(self.write_json("retired-integration-ref.json", manifest)),
            expected=2,
        )
        self.assertEqual(error["error"]["code"], "invalid-input")

    def test_given_local_tracker_when_delivery_is_github_pr_then_provider_closeout_remains_supported(self) -> None:
        """Given local Markdown tracking, when delivery is github-pr, then source and PR transports stay independent."""
        self.start("local-tracker-pr", tracker_backend="local", delivery_type="github-pr")
        self.create_worker("local-tracker-pr")
        self.ready_worker("local-tracker-pr")
        self.finish_pr_ready("local-tracker-pr")
        shown = self.invoke("run", "show", "--run-id", "local-tracker-pr")
        self.assertEqual(shown["status"], "pr-ready")
        self.assertTrue(shown["assignments"][0]["source_spec_ref"].endswith("/SPEC.md"))

    def test_given_local_only_repository_when_github_pr_is_requested_then_start_rejects_it(self) -> None:
        """Given no GitHub identity, when github-pr delivery is requested, then provider authority fails before state."""
        self.database.unlink()
        identity = self.local_identity(self.common_a)
        manifest = self.manifest(
            "local-only-pr",
            repositories=[(identity, self.common_a)],
            delivery_type="github-pr",
        )
        error = self.invoke(
            "run", "start", "--manifest", str(self.write_json("local-only-pr.json", manifest)),
            expected=2,
        )
        self.assertEqual(error["error"]["code"], "invalid-input")
        self.assertFalse(self.database.exists())

    def test_given_delivery_mismatch_when_ready_is_recorded_then_it_fails_closed(self) -> None:
        """Given local-branch authority, when GitHub-ready evidence is supplied, then the typed mismatch is rejected."""
        identity = self.local_identity(self.common_a)
        self.start("delivery-mismatch", repositories=[(identity, self.common_a)])
        self.create_worker("delivery-mismatch")
        observation = {
            **self.protocol("ready"),
            "assignment_id": "spec-01",
            "thread_id": "thread-delivery-mismatch-1",
            "repository_identity": identity,
            "delivery_type": "github-pr",
            "readiness_mode": "terminal",
            "head_sha": f"{101:040x}",
            "head_branch_name": "feature/example-1",
            "base_branch_name": "main",
            "base_sha": f"{10:040x}",
            "checkout_path": str(self.base / "checkout delivery-mismatch 1"),
            "worktree_clean": True,
            "base_is_ancestor": True,
            "validation_head_sha": f"{101:040x}",
            "autoreview_head_sha": f"{101:040x}",
            "review_candidate_head_sha": f"{101:040x}",
            "review_profile": "high-risk",
            "codex_review_head_sha": f"{101:040x}",
            "tracker_readback_ref": "tracker:mismatch",
            "prerequisite_heads": {},
            "default_branch_name": "main",
            "pr_url": "https://github.com/example/project/pull/1",
            "provider_observation_ref": "provider:mismatch",
            "status": "pr-ready-for-merge-but-not-merged",
        }
        error = self.invoke(
            "assignment", "ready", "--run-id", "delivery-mismatch",
            "--expected-revision", self.revision("delivery-mismatch"),
            "--observation", str(self.write_json("delivery-mismatch.json", observation)),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "delivery-type-drift")

    def test_given_dirty_or_detached_local_checkout_when_ready_is_recorded_then_it_is_rejected(self) -> None:
        """Given local delivery, when the branch is dirty or detached, then no terminal claim release occurs."""
        identity = self.local_identity(self.common_a)
        self.start("dirty-local", repositories=[(identity, self.common_a)])
        self.create_worker("dirty-local")
        dirty = self.ready_local_worker(
            "dirty-local", repository_identity=identity,
            worktree_clean=False, expected=2,
        )
        self.assertEqual(dirty["error"]["code"], "invalid-ready-observation")
        self.ready_local_worker("dirty-local", repository_identity=identity)
        self.finish_local_ready("dirty-local")

        self.start("detached-local", repositories=[(identity, self.common_a)])
        self.create_worker("detached-local")
        detached = self.ready_local_worker(
            "detached-local", repository_identity=identity,
            head_branch_name="HEAD", expected=4,
        )
        self.assertEqual(detached["error"]["code"], "target-branch-drift")

    def test_given_peer_assignments_when_inputs_stabilize_then_early_dispatch_and_sha_vector_are_enforced(self) -> None:
        """Given dependent peers, both may start early while combined proof binds the exact prerequisite HEADs."""
        identity = self.local_identity(self.common_a)
        manifest = self.manifest(
            "integration-vector",
            repositories=[(identity, self.common_a)],
            assignment_count=3,
        )
        manifest["assignments"][1]["prerequisite_assignment_ids"] = ["spec-01"]
        manifest["assignments"][2]["prerequisite_assignment_ids"] = ["spec-02"]
        self.invoke("run", "start", "--manifest", str(self.write_json("integration-vector.json", manifest)))
        for number in (2, 1, 3):
            self.create_worker("integration-vector", number)
        partial = self.ready_local_worker(
            "integration-vector", number=1, repository_identity=identity,
            readiness_mode="peer-input",
        )
        self.assertEqual(partial["state"], "peer-input-ready")
        exact_head = f"{201:040x}"
        proof_owner = self.ready_local_worker(
            "integration-vector", number=2, repository_identity=identity,
            prerequisite_heads={"spec-01": exact_head},
            readiness_mode="peer-input",
        )
        self.assertEqual(proof_owner["state"], "peer-input-ready")

        replacement_head = f"{777:040x}"
        self.ready_local_worker(
            "integration-vector", number=1, repository_identity=identity,
            readiness_mode="peer-input", head_sha=replacement_head,
        )
        replaced = self.invoke("run", "show", "--run-id", "integration-vector")
        upstream = next(
            row for row in replaced["assignments"] if row["assignment_id"] == "spec-01"
        )
        self.assertEqual(upstream["head_sha"], replacement_head)
        stale = self.ready_local_worker(
            "integration-vector", number=2, repository_identity=identity,
            prerequisite_heads={"spec-01": exact_head},
            expected=4,
        )
        self.assertEqual(stale["error"]["code"], "prerequisite-head-drift")
        ready = self.ready_local_worker(
            "integration-vector", number=2, repository_identity=identity,
            prerequisite_heads={"spec-01": replacement_head},
        )
        self.assertEqual(ready["state"], "local-branch-ready")

    def test_given_peer_input_ready_worker_when_contract_drifts_then_it_can_block(self) -> None:
        """Given a parked peer, durable drift still records a terminal block and retains its claim."""
        identity = self.local_identity(self.common_a)
        manifest = self.manifest(
            "peer-block", repositories=[(identity, self.common_a)], assignment_count=2,
        )
        manifest["assignments"][1]["prerequisite_assignment_ids"] = ["spec-01"]
        self.invoke("run", "start", "--manifest", str(self.write_json("peer-block.json", manifest)))
        self.create_worker("peer-block", 1)
        self.ready_local_worker(
            "peer-block", number=1, repository_identity=identity,
            readiness_mode="peer-input",
        )
        blocked = self.invoke(
            "assignment", "block", "--run-id", "peer-block",
            "--expected-revision", self.revision("peer-block"),
            "--assignment-id", "spec-01",
        )
        self.assertEqual(blocked["state"], "blocked-durable-contract")
        self.assertTrue(blocked["claim_retained"])
        revision = self.revision("peer-block")
        missing_evidence = self.invoke(
            "assignment", "resume", "--run-id", "peer-block",
            "--expected-revision", revision,
            "--assignment-id", "spec-01",
            expected=2,
        )
        self.assertEqual(
            missing_evidence["error"]["code"],
            "invalid-command-line",
        )
        self.assertEqual(self.revision("peer-block"), revision)
        stale_observation = self.resume_observation(
            "peer-block",
            "spec-01",
            "blocked-durable-contract",
            "durable-contract-restored",
            "tracker-read:stale-peer-block",
            run_revision=int(revision) - 1,
        )
        stale = self.invoke(
            "assignment", "resume", "--run-id", "peer-block",
            "--expected-revision", revision,
            "--assignment-id", "spec-01",
            "--observation", str(stale_observation),
            expected=4,
        )
        self.assertEqual(stale["error"]["code"], "recovery-observation-drift")
        self.assertEqual(self.revision("peer-block"), revision)
        observation = self.resume_observation(
            "peer-block",
            "spec-01",
            "blocked-durable-contract",
            "durable-contract-restored",
            "tracker-read:peer-block-restored",
        )
        resumed = self.invoke(
            "assignment", "resume", "--run-id", "peer-block",
            "--expected-revision", self.revision("peer-block"),
            "--assignment-id", "spec-01",
            "--observation", str(observation),
        )
        self.assertEqual(resumed["state"], "peer-input-ready")
        self.assertEqual(resumed["run_status"], "active")
        self.assertTrue(resumed["claim_retained"])
        self.assertEqual(
            resumed["recovery_kind"],
            "durable-contract-restored",
        )
        shown = self.invoke("run", "show", "--run-id", "peer-block")
        self.assertEqual(
            shown["spec_claims"][0]["recovery_readback_ref"],
            "tracker-read:peer-block-restored",
        )

    def test_given_runtime_topology_is_unavailable_when_worker_blocks_then_capability_is_distinct(self) -> None:
        """Given post-bootstrap App limitations, capability blocking is not misclassified as contract drift."""
        self.start("capability-block")
        self.create_worker("capability-block")
        blocked = self.invoke(
            "assignment", "capability-block", "--run-id", "capability-block",
            "--expected-revision", self.revision("capability-block"),
            "--assignment-id", "spec-01",
        )
        self.assertEqual(blocked["state"], "blocked-app-capability")
        self.assertEqual(blocked["run_status"], "blocked")
        self.assertTrue(blocked["claim_retained"])
        observation = self.resume_observation(
            "capability-block",
            "spec-01",
            "blocked-app-capability",
            "app-capability-restored",
            "app-read:capability-restored",
        )
        resumed = self.invoke(
            "assignment", "resume", "--run-id", "capability-block",
            "--expected-revision", self.revision("capability-block"),
            "--assignment-id", "spec-01",
            "--observation", str(observation),
        )
        self.assertEqual(resumed["state"], "active")
        self.assertEqual(resumed["run_status"], "active")
        self.assertEqual(
            resumed["recovery_kind"],
            "app-capability-restored",
        )
        self.assertEqual(
            resumed["recovery_readback_ref"],
            "app-read:capability-restored",
        )
        blocked_again = self.invoke(
            "assignment", "capability-block", "--run-id", "capability-block",
            "--expected-revision", self.revision("capability-block"),
            "--assignment-id", "spec-01",
        )
        self.assertEqual(blocked_again["state"], "blocked-app-capability")
        shown = self.invoke(
            "run", "show", "--run-id", "capability-block"
        )
        self.assertIsNone(
            shown["spec_claims"][0]["recovery_readback_ref"]
        )

    def test_given_bootstrap_when_review_owner_is_not_reconciled_then_authority_is_rejected(self) -> None:
        """Bootstrap begin requires and atomically persists one canonical owner."""
        self.start("review-owner-required")
        checkout = self.base / "review owner required checkout"
        checkout.mkdir()
        self.operation(
            "review-owner-required",
            "create-review-owner-required",
            "create-worker",
            "spec-01",
            {
                "thread_id": "thread-review-owner-required-1",
                "project_id": "project-1",
                "checkout_path": str(checkout),
                "git_common_dir": str(self.common_a),
                "observed_state": "active",
            },
        )
        self.operation(
            "review-owner-required",
            "title-review-owner-required",
            "set-worker-title",
            "spec-01",
            {
                "thread_id": "thread-review-owner-required-1",
                "observed_title": "🛠️ Feature 1",
            },
        )
        missing = self.begin_operation(
            "review-owner-required",
            "send-bootstrap",
            "spec-01",
            expected=2,
        )
        self.assertEqual(missing["error"]["code"], "invalid-input")
        begun = self.begin_operation(
            "review-owner-required",
            "send-bootstrap",
            "spec-01",
            review_owner="root",
        )
        self.assertEqual(begun["review_owner"], "root")
        observation = self.operation_observation(
            begun,
            status="succeeded",
            values={
                "receipt_ref": "receipt:review-owner-required",
                "readback_ref": "readback:review-owner-required",
                "thread_id": "thread-review-owner-required-1",
            },
        )
        self.invoke(
            "app-operation", "finish",
            "--run-id", "review-owner-required",
            "--expected-revision", self.revision("review-owner-required"),
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(
                self.write_json("review-owner-required-bootstrap.json", observation)
            ),
        )
        shown = self.invoke("run", "show", "--run-id", "review-owner-required")
        self.assertEqual(shown["assignments"][0]["review_owner"], "root")

    def test_given_worker_review_owner_when_reroute_replays_then_one_root_owner_is_canonical(self) -> None:
        """One failed reroute can replay by operation id; duplicate/conflicting owners cannot apply."""
        self.start("review-owner-reroute")
        self.create_worker("review-owner-reroute")
        begun = self.begin_operation(
            "review-owner-reroute",
            "set-review-owner",
            "spec-01",
        )
        failed_observation = self.operation_observation(
            begun,
            status="failed",
            values={"readback_ref": "app-read:reroute-not-delivered"},
        )
        self.invoke(
            "app-operation", "finish",
            "--run-id", "review-owner-reroute",
            "--expected-revision", self.revision("review-owner-reroute"),
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(
                self.write_json("review-owner-reroute-failed.json", failed_observation)
            ),
        )
        replayed = self.invoke(
            "app-operation", "replay",
            "--run-id", "review-owner-reroute",
            "--expected-revision", self.revision("review-owner-reroute"),
            "--operation-id", str(begun["operation_id"]),
        )
        self.assertEqual(replayed["operation_id"], begun["operation_id"])
        self.assertEqual(replayed["launch_count"], 2)
        succeeded_observation = self.operation_observation(
            replayed,
            status="succeeded",
            values={
                "receipt_ref": "receipt:review-owner-reroute",
                "readback_ref": "app-read:review-owner-root",
                "thread_id": "thread-review-owner-reroute-1",
                "observed_state": "root",
            },
        )
        observation_path = self.write_json(
            "review-owner-reroute-succeeded.json",
            succeeded_observation,
        )
        applied = self.invoke(
            "app-operation", "finish",
            "--run-id", "review-owner-reroute",
            "--expected-revision", self.revision("review-owner-reroute"),
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(observation_path),
        )
        self.assertFalse(applied["already_applied"])
        revision = self.revision("review-owner-reroute")
        duplicate = self.invoke(
            "app-operation", "finish",
            "--run-id", "review-owner-reroute",
            "--expected-revision", revision,
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(observation_path),
        )
        self.assertTrue(duplicate["already_applied"])
        self.assertEqual(str(duplicate["revision"]), revision)
        conflict = self.begin_operation(
            "review-owner-reroute",
            "set-review-owner",
            "spec-01",
            expected=4,
        )
        self.assertEqual(conflict["error"]["code"], "review-owner-conflict")
        shown = self.invoke("run", "show", "--run-id", "review-owner-reroute")
        self.assertEqual(shown["assignments"][0]["review_owner"], "root")
        bootstrap = next(
            row
            for row in self.invoke(
                "app-operation", "list", "--run-id", "review-owner-reroute"
            )["operations"]
            if row["action"] == "send-bootstrap"
        )
        self.assertEqual(bootstrap["review_owner"], "worker")

    def test_given_created_task_is_idle_when_observed_then_worker_binding_is_accepted(self) -> None:
        """A created task may be idle in the UI without losing its exact project/worktree binding."""
        self.start("idle-worker")
        self.create_worker("idle-worker", observed_state="idle")
        shown = self.invoke("run", "show", "--run-id", "idle-worker")
        self.assertEqual(shown["assignments"][0]["state"], "active")
        operation = next(
            row
            for row in self.invoke(
                "app-operation", "list", "--run-id", "idle-worker"
            )["operations"]
            if row["action"] == "create-worker"
        )
        self.assertEqual(operation["observed_state"], "idle")

    def test_given_created_task_has_terminal_ui_state_when_observed_then_binding_is_rejected(self) -> None:
        """Only active or idle can prove a newly created task binding."""
        self.start("invalid-worker-state")
        begun = self.begin_operation(
            "invalid-worker-state", "create-worker", "spec-01"
        )
        checkout = self.base / "invalid worker state checkout"
        checkout.mkdir()
        observation = self.operation_observation(
            begun,
            status="succeeded",
            values={
                "receipt_ref": "receipt:invalid-worker-state",
                "readback_ref": "readback:invalid-worker-state",
                "thread_id": "thread-invalid-worker-state-1",
                "project_id": "project-1",
                "checkout_path": str(checkout),
                "git_common_dir": str(self.common_a),
                "observed_state": "completed",
            },
        )
        error = self.invoke(
            "app-operation", "finish",
            "--run-id", "invalid-worker-state",
            "--expected-revision", self.revision("invalid-worker-state"),
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(
                self.write_json(
                    "invalid-worker-state-observation.json",
                    observation,
                )
            ),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "worker-project-drift")

    def test_given_two_app_projects_when_runs_are_disjoint_then_they_share_one_database(self) -> None:
        """Given disjoint repositories in separate App projects, when both start, then one per-user DB owns both."""
        self.start("run-a", repositories=[("github:example/a", self.common_a)], project_prefix="alpha")
        self.start("run-b", repositories=[("github:example/b", self.common_b)], project_prefix="beta")
        listing = self.invoke("run", "list", "--status", "active")
        self.assertEqual({row["run_id"] for row in listing["runs"]}, {"run-a", "run-b"})
        self.assertEqual(list(self.database.parent.glob("*.sqlite3")), [self.database])

    def test_given_one_root_task_when_second_unfinished_run_starts_then_it_is_rejected(self) -> None:
        """Given a root task owns an active run, when it starts another disjoint run, then one controller is preserved."""
        self.start("first-root", repositories=[("github:example/a", self.common_a)])
        second = self.manifest("second-root", repositories=[("github:example/b", self.common_b)])
        second["root_task_id"] = "root-first-root"
        error = self.invoke(
            "run", "start", "--manifest", str(self.write_json("same-root.json", second)), expected=4,
        )
        self.assertEqual(error["error"]["code"], "root-task-already-active")

    def test_given_one_saved_project_for_two_repositories_when_manifest_is_validated_then_start_is_rejected(self) -> None:
        """One saved project cannot stand in for two affected Git repositories."""
        manifest = self.manifest(
            "bad-project",
            repositories=[("github:example/a", self.common_a), ("github:example/b", self.common_b)],
            assignment_count=2,
        )
        manifest["repositories"][1]["project_id"] = manifest["repositories"][0]["project_id"]
        result = self.invoke(
            "run", "start", "--manifest", str(self.write_json("workspace-project.json", manifest)),
            expected=2,
        )
        self.assertEqual(result["error"]["code"], "invalid-input")

    def test_given_two_repository_projects_when_run_starts_then_assignments_inherit_exact_bindings(self) -> None:
        """Repository project bindings are normalized once and inherited by workers."""
        manifest = self.manifest(
            "repository-projects",
            repositories=[
                ("github:example/a", self.common_a),
                ("github:example/b", self.common_b),
            ],
            assignment_count=2,
        )
        self.invoke(
            "run",
            "start",
            "--manifest",
            str(self.write_json("repository-projects.json", manifest)),
        )
        shown = self.invoke("run", "show", "--run-id", "repository-projects")
        self.assertEqual(
            {
                row["repository_identity"]: row["project_id"]
                for row in shown["repositories"]
            },
            {
                "github:example/a": "project-1",
                "github:example/b": "project-2",
            },
        )
        self.assertEqual(
            {
                row["repository_identity"]: row["project_id"]
                for row in shown["assignments"]
            },
            {
                "github:example/a": "project-1",
                "github:example/b": "project-2",
            },
        )

        begun = self.begin_operation(
            "repository-projects",
            "create-worker",
            "spec-02",
        )
        checkout = self.base / "repository projects checkout"
        checkout.mkdir()
        observation = self.operation_observation(
            begun,
            status="succeeded",
            values={
                "receipt_ref": "receipt:repository-projects",
                "readback_ref": "readback:repository-projects",
                "thread_id": "thread-repository-projects-2",
                "project_id": "project-2",
                "checkout_path": str(checkout),
                "git_common_dir": str(self.common_b),
                "observed_state": "active",
            },
        )
        result = self.invoke(
            "app-operation",
            "finish",
            "--run-id",
            "repository-projects",
            "--expected-revision",
            self.revision("repository-projects"),
            "--operation-id",
            str(begun["operation_id"]),
            "--observation",
            str(self.write_json("repository-projects-worker.json", observation)),
        )
        self.assertEqual(result["status"], "succeeded")

    def test_given_controller_task_project_is_affected_when_run_starts_then_controller_stays_control_plane_only(self) -> None:
        """The controller may share a saved project with one affected repository."""
        manifest = self.manifest("affected-primary")
        manifest["controller_project_id"] = manifest["repositories"][0]["project_id"]
        self.invoke(
            "run",
            "start",
            "--manifest",
            str(self.write_json("affected-primary.json", manifest)),
        )
        shown = self.invoke("run", "show", "--run-id", "affected-primary")
        self.assertEqual(shown["controller_project_id"], "project-1")
        self.assertEqual(shown["repositories"][0]["project_id"], "project-1")
        self.assertEqual(shown["assignments"][0]["state"], "planned")

    def test_given_assignment_embeds_retired_project_id_when_run_starts_then_manifest_is_rejected(self) -> None:
        """Project identity belongs only to the repository map in manifest 3."""
        manifest = self.manifest("retired-assignment-project")
        manifest["assignments"][0]["project_id"] = "project-1"
        result = self.invoke(
            "run",
            "start",
            "--manifest",
            str(self.write_json("retired-assignment-project.json", manifest)),
            expected=2,
        )
        self.assertEqual(result["error"]["code"], "invalid-input")

    def test_given_state_writes_when_inspected_then_sqlite_coordinates_them_without_lockfile(self) -> None:
        """Given a writer, SQLite owns the transaction and no filesystem lock is created."""
        self.invoke("state", "prepare")
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
        self.assertFalse(self.database.with_name("run-state.lock").exists())

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
        self.assertTrue(second["may_create_worker"])
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
        self.assertTrue(result["may_create_worker"])
        shown = self.invoke("run", "show", "--run-id", "multi")
        self.assertEqual([row["active"] for row in shown["spec_claims"]], [1, 0])

    def test_given_three_same_repo_specs_when_bootstrapped_then_each_has_its_own_claim(self) -> None:
        """Given three disjoint Specs in one repo, when dispatched, then each worker has one Spec claim."""
        self.start("three", assignment_count=3)
        for number in (1, 2, 3):
            self.create_worker("three", number)
        shown = self.invoke("run", "show", "--run-id", "three")
        self.assertEqual(len(shown["spec_claims"]), 3)
        self.assertTrue(all(row["active"] == 1 for row in shown["spec_claims"]))
        self.assertEqual([row["state"] for row in shown["assignments"]], ["active"] * 3)

    def test_given_three_live_workers_when_fourth_is_created_then_no_numeric_cap_blocks_it(self) -> None:
        """Given three live workers, a fourth disjoint assignment can create and bootstrap its worker."""
        self.start("four", assignment_count=4)
        for number in (1, 2, 3):
            self.create_worker("four", number)
        self.create_worker("four", 4)
        shown = self.invoke("run", "show", "--run-id", "four")
        self.assertEqual(
            [row["state"] for row in shown["assignments"]],
            ["active"] * 4,
        )

    def test_given_one_worker_is_parked_for_peers_when_another_worker_starts_then_repair_access_is_preserved(self) -> None:
        """Input-ready parking preserves peer repair access while another assignment starts."""
        identity = self.local_identity(self.common_a)
        manifest = self.manifest(
            "parked-peer",
            repositories=[(identity, self.common_a)],
            assignment_count=4,
        )
        manifest["assignments"][3]["prerequisite_assignment_ids"] = ["spec-01"]
        self.invoke("run", "start", "--manifest", str(self.write_json("parked-peer.json", manifest)))
        for number in (1, 2, 3):
            self.create_worker("parked-peer", number)
        parked = self.ready_local_worker(
            "parked-peer", number=1, repository_identity=identity,
            readiness_mode="peer-input",
        )
        self.assertEqual(parked["state"], "peer-input-ready")
        self.create_worker("parked-peer", 4)
        shown = self.invoke("run", "show", "--run-id", "parked-peer")
        states = {row["assignment_id"]: row["state"] for row in shown["assignments"]}
        self.assertEqual(states["spec-01"], "peer-input-ready")
        self.assertEqual(states["spec-04"], "active")

    def test_given_active_run_and_claim_when_worker_creation_begins_then_controller_authorizes_it(self) -> None:
        """Given claimed state, when worker creation begins, then the unfinished run provides authority."""
        self.start("worker-ready")
        result = self.begin_operation("worker-ready", "create-worker", "spec-01")
        self.assertTrue(result["launch_authorized"])

    def test_given_planned_preimplementation_state_when_run_aborts_then_claim_releases_directly(self) -> None:
        """Given only planned work, when the run aborts, then no artificial lifecycle step is required."""
        self.start("planned-abort")
        result = self.invoke(
            "run", "finish", "--run-id", "planned-abort",
            "--expected-revision", self.revision("planned-abort"),
            "--outcome", "preimplementation-aborted",
        )
        self.assertEqual(result["outcome"], "preimplementation-aborted")
        self.assertTrue(result["claims_released"])

    def test_given_unresolved_app_effect_when_run_finishes_then_controller_rejects_it(self) -> None:
        """Given PR-ready delivery and an unknown App effect, when the run finishes, then reconciliation comes first."""
        self.start("unresolved")
        self.create_worker("unresolved")
        self.ready_worker("unresolved")
        self.operation(
            "unresolved", "root-title-unknown", "set-root-title", "root-unresolved",
            {"observed_title": "Implementing"}, status="unknown",
        )
        error = self.invoke(
            "run", "finish", "--run-id", "unresolved",
            "--expected-revision", self.revision("unresolved"),
            "--outcome", "pr-ready", expected=4,
        )
        self.assertEqual(error["error"]["code"], "unresolved-app-operations")

    def test_given_incomplete_assignment_when_run_finishes_then_controller_rejects_it(self) -> None:
        """Given a claimed planned assignment, delivery finish cannot bypass worker readiness."""
        self.start("incomplete-finish")
        error = self.invoke(
            "run", "finish", "--run-id", "incomplete-finish",
            "--expected-revision", self.revision("incomplete-finish"),
            "--outcome", "pr-ready", expected=4,
        )
        self.assertEqual(error["error"]["code"], "run-incomplete")

    def test_given_delivery_ready_assignment_with_active_claim_when_run_finishes_then_controller_rejects_it(self) -> None:
        """Given terminal evidence but an unreleased claim, aggregate closeout remains blocked."""
        self.start("active-claim-finish")
        self.create_worker("active-claim-finish")
        self.ready_worker("active-claim-finish")
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                """UPDATE spec_claims
                   SET active=1,released_at=NULL,release_reason=NULL
                   WHERE run_id='active-claim-finish' AND assignment_id='spec-01'"""
            )
        error = self.invoke(
            "run", "finish", "--run-id", "active-claim-finish",
            "--expected-revision", self.revision("active-claim-finish"),
            "--outcome", "pr-ready", expected=4,
        )
        self.assertEqual(error["error"]["code"], "claims-not-released")

    def test_given_ambiguous_worker_creation_when_reconciled_then_it_is_not_relaunched(self) -> None:
        """Given an unknown create-worker effect, only the same operation may resolve its identity."""
        self.start("ambiguous-worker")
        begun = self.begin_operation(
            "ambiguous-worker", "create-worker", "spec-01",
        )
        unknown = self.operation_observation(begun, status="unknown")
        self.invoke(
            "app-operation", "finish", "--run-id", "ambiguous-worker",
            "--expected-revision", self.revision("ambiguous-worker"),
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(self.write_json("create-ambiguous-unknown.json", unknown)),
        )
        blocked = self.begin_operation(
            "ambiguous-worker", "create-worker", "spec-01", expected=4,
        )
        self.assertEqual(blocked["error"]["code"], "protected-operation-already-started")
        checkout = self.base / "checkout ambiguous worker"
        checkout.mkdir()
        succeeded = self.operation_observation(
            begun,
            status="succeeded",
            values={
                "receipt_ref": "receipt:create-ambiguous",
                "readback_ref": "readback:create-ambiguous",
                "thread_id": "thread-ambiguous-worker-1",
                "project_id": "project-1",
                "checkout_path": str(checkout),
                "git_common_dir": str(self.common_a),
                "observed_state": "active",
            },
        )
        self.invoke(
            "app-operation", "finish", "--run-id", "ambiguous-worker",
            "--expected-revision", self.revision("ambiguous-worker"),
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(self.write_json("create-ambiguous-succeeded.json", succeeded)),
        )
        shown = self.invoke("run", "show", "--run-id", "ambiguous-worker")
        operations = self.invoke("app-operation", "list", "--run-id", "ambiguous-worker")
        self.assertEqual(shown["assignments"][0]["state"], "worker-created")
        self.assertEqual(
            [row["operation_id"] for row in operations["operations"]],
            [begun["operation_id"]],
        )

    def test_given_existing_worker_identity_when_stale_readback_reuses_it_then_binding_fails(self) -> None:
        """Given one worker/worktree binding, when another assignment receives the same readback, then it cannot alias."""
        self.start("alias", assignment_count=2)
        self.create_worker("alias", 1)
        begun = self.begin_operation(
            "alias", "create-worker", "spec-02",
        )
        stale = self.operation_observation(
            begun,
            status="succeeded",
            values={
                "receipt_ref": "receipt:create-alias-2",
                "readback_ref": "readback:create-alias-2",
                "thread_id": "thread-alias-1",
                "project_id": "project-1",
                "checkout_path": str(self.base / "checkout alias 1"),
                "git_common_dir": str(self.common_a),
                "observed_state": "active",
            },
        )
        error = self.invoke(
            "app-operation", "finish", "--run-id", "alias",
            "--expected-revision", self.revision("alias"),
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(self.write_json("stale-alias.json", stale)), expected=4,
        )
        self.assertEqual(error["error"]["code"], "worker-identity-conflict")

    def test_given_nondefault_pr_base_when_ready_is_recorded_then_controller_rejects_it(self) -> None:
        """Given provider default main but PR base release, when root records ready, then claims cannot release."""
        self.start("wrong-base")
        self.create_worker("wrong-base")
        observation = {
            **self.protocol("ready"), "assignment_id": "spec-01",
            "thread_id": "thread-wrong-base-1",
            "repository_identity": "github:example/project",
            "delivery_type": "github-pr", "readiness_mode": "terminal",
            "head_sha": f"{101:040x}",
            "head_branch_name": "feature/example-1", "base_branch_name": "release",
            "base_sha": f"{10:040x}",
            "checkout_path": str(self.base / "checkout wrong-base 1"),
            "worktree_clean": True, "base_is_ancestor": True,
            "validation_head_sha": f"{101:040x}",
            "autoreview_head_sha": f"{101:040x}",
            "review_candidate_head_sha": f"{101:040x}",
            "review_profile": "high-risk",
            "codex_review_head_sha": f"{101:040x}",
            "tracker_readback_ref": "tracker:wrong-base",
            "prerequisite_heads": {},
            "default_branch_name": "main",
            "pr_url": "https://github.com/example/project/pull/1",
            "provider_observation_ref": "provider:wrong-base", "status": "pr-ready-for-merge-but-not-merged",
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
        """Given an active owner, when three unchanged sweeps pass, then waiter terminates before any visible task."""
        self.start("owner")
        self.start("waiter")
        for _ in range(3):
            result = self.invoke("run", "wait-sweep", "--run-id", "waiter", "--assignment-id", "spec-01", "--expected-revision", self.revision("waiter"))
        self.assertEqual(result["state"], "blocked-by-active-spec")
        shown = self.invoke("run", "show", "--run-id", "waiter")
        self.assertNotIn("goal_state", shown)
        self.assertTrue(all(row["thread_id"] is None for row in shown["assignments"]))
        self.assertEqual(shown["unresolved_app_operations"], [])
        self.assertEqual(result["conflicting_owner"]["root_task_id"], "root-owner")
        self.invoke(
            "run", "finish", "--run-id", "owner",
            "--expected-revision", self.revision("owner"),
            "--outcome", "preimplementation-aborted",
        )
        resumed = self.invoke(
            "run", "wait-sweep", "--run-id", "waiter",
            "--assignment-id", "spec-01",
            "--expected-revision", self.revision("waiter"),
        )
        self.assertEqual(resumed["state"], "planned")
        self.assertTrue(resumed["claim_acquired"])

    def test_given_same_owner_adds_worker_when_wait_sweeps_continue_then_bound_does_not_reset(self) -> None:
        """Given one Spec owner, when its worker list changes, then stable owner identity keeps the wait bounded."""
        self.start("churn-owner", assignment_count=2)
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
        """Given a worker without bootstrap authority, when it reconciles terminal, then the claim releases."""
        self.start("abort")
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
        result = self.invoke("run", "finish", "--run-id", "abort", "--expected-revision", self.revision("abort"), "--outcome", "preimplementation-aborted")
        self.assertTrue(result["claims_released"])
        owner = self.invoke("claim", "find", "--repository-identity", "github:example/project", "--tracker-backend", "github", "--source-spec-ref", "example/project#1")
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
            **self.protocol("recovery"),
            "owner_run_id": "missing-owner",
            "owner_assignment_id": "spec-01",
            "owner_expected_revision": int(self.revision("missing-owner")),
            "repository_identity": "github:example/project",
            "tracker_backend": "github",
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

    def test_given_newer_recovery_observation_when_claim_reconciles_then_owners_are_unchanged(self) -> None:
        """Given newer recovery evidence, reconciliation rejects it without transferring the claim."""
        self.start("v1-recovery-owner")
        self.start("v1-recovery-waiter")
        observation = {
            "schema": PROTOCOLS["recovery"]["schema"],
            "schema_version": "3.0.0",
            "owner_run_id": "v1-recovery-owner",
            "owner_assignment_id": "spec-01",
            "owner_expected_revision": int(self.revision("v1-recovery-owner")),
            "repository_identity": "github:example/project",
            "tracker_backend": "github",
            "source_spec_ref": "example/project#1",
            "worker_state": "not-found",
            "checkout_state": "not-found",
            "readback_ref": "app-read:v1-recovery",
        }
        error = self.invoke(
            "claim", "reconcile", "--run-id", "v1-recovery-waiter",
            "--assignment-id", "spec-01",
            "--expected-revision", self.revision("v1-recovery-waiter"),
            "--observation", str(self.write_json("v1-recovery.json", observation)),
            expected=2,
        )
        self.assertEqual(error["error"]["code"], "unsupported-input-protocol")
        owner = self.invoke(
            "claim", "find", "--repository-identity", "github:example/project",
            "--tracker-backend", "github", "--source-spec-ref", "example/project#1",
        )
        self.assertEqual(owner["owner"]["run_id"], "v1-recovery-owner")

    def test_given_terminal_missing_owner_without_waiter_when_recovered_then_same_root_can_finish_abandoned(self) -> None:
        """Given a lost post-bootstrap worker, typed owner recovery releases its claim and terminalizes the run."""
        self.start("owner-recovery")
        self.create_worker("owner-recovery")
        observation = {
            **self.protocol("recovery"),
            "owner_run_id": "owner-recovery",
            "owner_assignment_id": "spec-01",
            "owner_expected_revision": int(self.revision("owner-recovery")),
            "repository_identity": "github:example/project",
            "tracker_backend": "github",
            "source_spec_ref": "example/project#1",
            "worker_state": "completed",
            "checkout_state": "released",
            "readback_ref": "app-read:owner-recovery-terminal",
        }
        recovered = self.invoke(
            "assignment", "recover", "--run-id", "owner-recovery",
            "--expected-revision", self.revision("owner-recovery"),
            "--assignment-id", "spec-01",
            "--observation", str(self.write_json("owner-recovery.json", observation)),
        )
        self.assertEqual(recovered["state"], "abandoned")
        self.assertTrue(recovered["claim_released"])
        finished = self.invoke(
            "run", "finish", "--run-id", "owner-recovery",
            "--expected-revision", self.revision("owner-recovery"),
            "--outcome", "abandoned",
        )
        self.assertEqual(finished["outcome"], "abandoned")
        self.assertTrue(finished["claims_released"])
        shown = self.invoke("run", "show", "--run-id", "owner-recovery")
        self.assertEqual(shown["status"], "abandoned")
        self.assertEqual(shown["spec_claims"][0]["active"], 0)

    def test_given_active_owner_without_waiter_when_recovered_then_claim_is_preserved(self) -> None:
        """Given an authoritative live owner, owner-side recovery performs no terminal mutation."""
        self.start("active-owner-recovery")
        self.create_worker("active-owner-recovery")
        revision = self.revision("active-owner-recovery")
        observation = {
            **self.protocol("recovery"),
            "owner_run_id": "active-owner-recovery",
            "owner_assignment_id": "spec-01",
            "owner_expected_revision": int(revision),
            "repository_identity": "github:example/project",
            "tracker_backend": "github",
            "source_spec_ref": "example/project#1",
            "worker_state": "active",
            "checkout_state": "present",
            "readback_ref": "app-read:active-owner-recovery",
        }
        recovered = self.invoke(
            "assignment", "recover", "--run-id", "active-owner-recovery",
            "--expected-revision", revision, "--assignment-id", "spec-01",
            "--observation", str(self.write_json("active-owner-recovery.json", observation)),
        )
        self.assertEqual(recovered["outcome"], "owner-active")
        self.assertFalse(recovered["claim_released"])
        self.assertEqual(recovered["revision"], int(revision))

    def test_given_recovery_required_waiter_when_owner_is_later_active_then_bounded_wait_can_resume(self) -> None:
        """Given newer authoritative evidence, a failed recovery returns to the ordinary blocked wait."""
        self.start("retry-recovery-owner")
        self.create_worker("retry-recovery-owner")
        self.start("retry-recovery-waiter")
        base = {
            **self.protocol("recovery"),
            "owner_run_id": "retry-recovery-owner",
            "owner_assignment_id": "spec-01",
            "owner_expected_revision": int(self.revision("retry-recovery-owner")),
            "repository_identity": "github:example/project",
            "tracker_backend": "github",
            "source_spec_ref": "example/project#1",
        }
        unknown = {
            **base,
            "worker_state": "unknown",
            "checkout_state": "unknown",
            "readback_ref": "app-read:retry-recovery-unknown",
        }
        first = self.invoke(
            "claim", "reconcile", "--run-id", "retry-recovery-waiter",
            "--assignment-id", "spec-01",
            "--expected-revision", self.revision("retry-recovery-waiter"),
            "--observation", str(self.write_json("retry-recovery-unknown.json", unknown)),
        )
        self.assertEqual(first["state"], "abandoned-recovery-required")
        active = {
            **base,
            "worker_state": "active",
            "checkout_state": "present",
            "readback_ref": "app-read:retry-recovery-active",
        }
        second = self.invoke(
            "claim", "reconcile", "--run-id", "retry-recovery-waiter",
            "--assignment-id", "spec-01",
            "--expected-revision", self.revision("retry-recovery-waiter"),
            "--observation", str(self.write_json("retry-recovery-active.json", active)),
        )
        self.assertEqual(second["state"], "blocked-by-active-spec")
        self.assertEqual(second["outcome"], "owner-active")
        self.assertFalse(second["claim_acquired"])

    def test_given_failed_create_worker_when_replayed_then_same_operation_can_succeed_without_duplicate_identity(self) -> None:
        """A failed protected effect retries by incrementing its launch, never by allocating another operation."""
        self.start("retry")
        failed = self.operation(
            "retry", "worker-failed", "create-worker", "spec-01", {}, status="failed"
        )
        self.assertTrue(failed["replay_authorized"])
        duplicate = self.begin_operation(
            "retry", "create-worker", "spec-01", expected=4,
        )
        self.assertEqual(
            duplicate["error"]["code"], "protected-operation-already-started",
        )
        replayed = self.invoke(
            "app-operation", "replay", "--run-id", "retry",
            "--expected-revision", self.revision("retry"),
            "--operation-id", str(failed["operation_id"]),
        )
        self.assertEqual(replayed["operation_id"], failed["operation_id"])
        self.assertEqual(replayed["launch_count"], 2)
        checkout = self.base / "checkout retry 1"
        checkout.mkdir()
        succeeded = self.operation_observation(
            replayed,
            status="succeeded",
            values={
                "receipt_ref": "receipt:worker-retry",
                "readback_ref": "readback:worker-retry",
                "thread_id": "thread-retry-1",
                "project_id": "project-1",
                "checkout_path": str(checkout),
                "git_common_dir": str(self.common_a),
                "observed_state": "active",
            },
        )
        finished = self.invoke(
            "app-operation", "finish", "--run-id", "retry",
            "--expected-revision", self.revision("retry"),
            "--operation-id", str(failed["operation_id"]),
            "--observation",
            str(self.write_json("worker-retry-succeeded.json", succeeded)),
        )
        self.assertEqual(finished["status"], "succeeded")
        self.assertEqual(finished["launch_count"], 2)
        shown = self.invoke("run", "show", "--run-id", "retry")
        self.assertEqual(shown["assignments"][0]["state"], "worker-created")

    def test_given_failed_protected_action_or_worker_message_when_replay_is_requested_then_only_protected_action_relaunches(self) -> None:
        """Failed single-use actions replay in place; repeatable follow-up messages remain non-replayable."""
        self.start("protected-replay")
        self.create_worker("protected-replay")
        failed_title = self.operation(
            "protected-replay",
            "root-title-failed",
            "set-root-title",
            "root-protected-replay",
            {},
            status="failed",
        )
        self.assertTrue(failed_title["replay_authorized"])
        replayed_title = self.invoke(
            "app-operation", "replay", "--run-id", "protected-replay",
            "--expected-revision", self.revision("protected-replay"),
            "--operation-id", str(failed_title["operation_id"]),
        )
        self.assertEqual(
            replayed_title["operation_id"], failed_title["operation_id"],
        )
        self.assertEqual(replayed_title["launch_count"], 2)
        title_succeeded = self.operation_observation(
            replayed_title,
            status="succeeded",
            values={
                "receipt_ref": "receipt:root-title-replay",
                "readback_ref": "readback:root-title-replay",
                "observed_title": "🤖 Feature Orchestrator",
            },
        )
        self.invoke(
            "app-operation", "finish", "--run-id", "protected-replay",
            "--expected-revision", self.revision("protected-replay"),
            "--operation-id", str(failed_title["operation_id"]),
            "--observation",
            str(self.write_json("root-title-replayed.json", title_succeeded)),
        )

        failed_message = self.operation(
            "protected-replay",
            "worker-message-failed",
            "send-worker-message",
            "spec-01",
            {"thread_id": "thread-protected-replay-1"},
            status="failed",
        )
        self.assertFalse(failed_message["replay_authorized"])
        unsupported = self.invoke(
            "app-operation", "replay", "--run-id", "protected-replay",
            "--expected-revision", self.revision("protected-replay"),
            "--operation-id", str(failed_message["operation_id"]),
            expected=4,
        )
        self.assertEqual(
            unsupported["error"]["code"], "operation-replay-unsupported",
        )

    def test_given_pr_ready_release_when_independent_root_starts_then_it_acquires(self) -> None:
        """Given an independent Spec after PR-ready release, when it starts, then merge is not required for ownership."""
        self.start("first")
        self.create_worker("first")
        self.ready_worker("first")
        self.finish_pr_ready("first")
        second = self.start("second")
        self.assertEqual(second["acquired_assignment_ids"], ["spec-01"])

    def test_given_one_assignment_ready_when_sibling_remains_active_then_only_ready_claim_releases(self) -> None:
        """Given two workers, when one becomes PR-ready, then its Spec claim releases without ending the run."""
        self.start("partial-ready", assignment_count=2)
        self.create_worker("partial-ready", 1)
        self.create_worker("partial-ready", 2)
        result = self.ready_worker("partial-ready", 1)
        self.assertTrue(result["claim_released"])
        shown = self.invoke("run", "show", "--run-id", "partial-ready")
        self.assertEqual([row["active"] for row in shown["spec_claims"]], [0, 1])
        self.assertEqual(shown["status"], "active")
        self.assertNotIn("goal_state", shown)

    def test_given_terminal_postbootstrap_owner_when_waiter_reconciles_then_claim_transfers_atomically(self) -> None:
        """Given authoritative terminal worker proof, when waiter reconciles, then old work is abandoned and the Spec acquires."""
        self.start("terminal-owner")
        self.create_worker("terminal-owner")
        self.start("terminal-waiter")
        observation = {
            **self.protocol("recovery"),
            "owner_run_id": "terminal-owner",
            "owner_assignment_id": "spec-01",
            "owner_expected_revision": int(self.revision("terminal-owner")),
            "repository_identity": "github:example/project",
            "tracker_backend": "github",
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
        self.create_worker("active-owner")
        self.start("active-waiter")
        observation = {
            **self.protocol("recovery"),
            "owner_run_id": "active-owner",
            "owner_assignment_id": "spec-01",
            "owner_expected_revision": int(self.revision("active-owner")),
            "repository_identity": "github:example/project",
            "tracker_backend": "github",
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
        self.create_worker("bound-owner")
        self.start("bound-waiter")
        observation = {
            **self.protocol("recovery"),
            "owner_run_id": "bound-owner",
            "owner_assignment_id": "spec-01",
            "owner_expected_revision": int(self.revision("bound-owner")),
            "repository_identity": "github:example/project",
            "tracker_backend": "github",
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
        self.create_worker("unknown-owner")
        self.start("unknown-waiter")
        observation = {
            **self.protocol("recovery"),
            "owner_run_id": "unknown-owner",
            "owner_assignment_id": "spec-01",
            "owner_expected_revision": int(self.revision("unknown-owner")),
            "repository_identity": "github:example/project",
            "tracker_backend": "github",
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

    def test_given_unknown_bootstrap_effect_when_readback_arrives_then_same_id_reconciles(self) -> None:
        """Given ambiguous App delivery, receipt readback resolves the same operation and bootstrap IDs."""
        self.start("recover")
        assignment = "spec-01"
        thread = "thread-recover-1"
        checkout = self.base / "recover checkout"
        checkout.mkdir()
        self.operation("recover", "create-recover", "create-worker", assignment, {"thread_id": thread, "project_id": "project-1", "checkout_path": str(checkout), "git_common_dir": str(self.common_a), "observed_state": "active"})
        self.operation("recover", "title-recover", "set-worker-title", assignment, {"thread_id": thread, "observed_title": "🛠️ Feature 1"})
        unknown = self.operation(
            "recover", "bootstrap-recover", "send-bootstrap", assignment,
            {"thread_id": thread}, status="unknown",
        )
        operations = self.invoke("app-operation", "list", "--run-id", "recover")
        bootstrap = next(row for row in operations["operations"] if row["action"] == "send-bootstrap")
        relaunch = self.begin_operation(
            "recover", "send-bootstrap", assignment,
            expected=4,
            review_owner="worker",
        )
        self.assertEqual(relaunch["error"]["code"], "protected-operation-already-started")
        observed = {
            **self.protocol("operation"),
            "operation_id": unknown["operation_id"],
            "launch_count": unknown["launch_count"],
            "bootstrap_id": bootstrap["bootstrap_id"],
            "status": "succeeded",
            "receipt_ref": "receipt:bootstrap-recover",
            "readback_ref": "thread-read:recover",
            "thread_id": thread,
        }
        result = self.invoke(
            "app-operation", "finish", "--run-id", "recover", "--expected-revision", self.revision("recover"),
            "--operation-id", str(unknown["operation_id"]),
            "--observation", str(self.write_json("reconciled.json", observed)),
        )
        self.assertEqual(result["status"], "succeeded")
        with sqlite3.connect(self.database) as connection:
            columns = [row[1] for row in connection.execute("PRAGMA table_info(app_operations)")]
        self.assertFalse(any("hash" in column for column in columns))

    def test_given_unknown_bootstrap_when_archive_begins_then_worker_is_preserved(self) -> None:
        """Given bootstrap may have delivered, when preimplementation archive begins, then reconciliation is mandatory."""
        self.start("archive-unknown")
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
        error = self.begin_operation(
            "archive-unknown", "archive-worker", assignment, expected=4,
        )
        self.assertEqual(error["error"]["code"], "bootstrap-reconciliation-required")

    def test_given_unknown_app_effect_before_receipt_when_recorded_then_no_reference_is_fabricated(self) -> None:
        """Given transport ambiguity before any receipt, when unknown is recorded, then nullable typed facts preserve truth."""
        self.start("no-receipt")
        begun = self.begin_operation(
            "no-receipt", "set-root-title", "root-no-receipt",
        )
        observation = self.operation_observation(begun, status="unknown")
        result = self.invoke(
            "app-operation", "finish", "--run-id", "no-receipt",
            "--expected-revision", self.revision("no-receipt"),
            "--operation-id", str(begun["operation_id"]),
            "--observation", str(self.write_json("unknown-no-receipt.json", observation)),
        )
        self.assertEqual(result["status"], "unknown")
        operations = self.invoke("app-operation", "list", "--run-id", "no-receipt")
        self.assertIsNone(operations["operations"][0]["receipt_ref"])
        self.assertIsNone(operations["operations"][0]["readback_ref"])

    def test_given_post_bootstrap_worker_when_preimplementation_finish_is_attempted_then_release_fails(self) -> None:
        """Given worker authority has started, when root requests preimplementation release, then the claim remains."""
        self.start("started")
        self.create_worker("started")
        error = self.invoke("run", "finish", "--run-id", "started", "--expected-revision", self.revision("started"), "--outcome", "preimplementation-aborted", expected=4)
        self.assertEqual(error["error"]["code"], "implementation-already-started")
        owner = self.invoke("claim", "find", "--repository-identity", "github:example/project", "--tracker-backend", "github", "--source-spec-ref", "example/project#1")
        self.assertEqual(owner["owner"]["run_id"], "started")

    def test_given_schema_when_inspected_then_state_is_narrow_and_run_pins_exact_runtime(self) -> None:
        """Schema 3 separates project bindings while pinning the exact runtime."""
        self.start("schema")
        with sqlite3.connect(self.database) as connection:
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
            columns = [row[1] for table in tables for row in connection.execute(f"PRAGMA table_info({table})")]
            metadata = connection.execute(
                "SELECT singleton,schema_version,target_schema_version FROM runtime_metadata"
            ).fetchall()
        self.assertEqual(
            tables,
            {
                "runtime_metadata",
                "runs",
                "run_repositories",
                "assignments",
                "spec_claims",
                "app_operations",
            },
        )
        self.assertEqual(metadata, [(1, DATABASE_SCHEMA_VERSION, None)])
        self.assertNotIn("goal_state", columns)
        self.assertIn("runtime_artifact_sha256", columns)
        self.assertIn("feature_id", columns)
        self.assertFalse(any("body" in column or "checklist" in column or "attempt" in column for column in columns))
        self.assertFalse(
            any(
                "responsibility" in column or "feature_spec_set" in column
                for column in columns
            )
        )
        shown = self.invoke("run", "show", "--run-id", "schema")
        self.assertEqual(shown["controller_project_id"], "controller-schema")
        self.assertEqual(
            shown["repositories"][0]["project_id"],
            "project-1",
        )
        self.assertEqual(
            shown["assignments"][0]["project_id"],
            "project-1",
        )
        self.assertEqual(shown["runtime_contract_version"], RUNTIME_CONTRACT_VERSION)
        self.assertEqual(shown["runtime_cli_version"], CLI_VERSION)
        self.assertEqual(shown["runtime_artifact_sha256"], hashlib.sha256(TOOL.read_bytes()).hexdigest())
        before = self.database.read_bytes()
        diagnosis = self.invoke("doctor")
        self.assertFalse(diagnosis["writes_performed"])
        self.assertEqual(self.database.read_bytes(), before)
        with sqlite3.connect(self.database) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO runtime_metadata(singleton,schema_version) VALUES (2,2)"
                )

    def test_given_run_artifact_pin_drift_when_mutation_is_attempted_then_retained_runtime_is_required(self) -> None:
        """A same-version but different executable cannot mutate an existing run."""
        self.start("artifact-pin-drift")
        revision = self.revision("artifact-pin-drift")
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                """UPDATE runs
                   SET runtime_artifact_sha256=?
                   WHERE run_id='artifact-pin-drift'""",
                ("0" * 64,),
            )
        error = self.invoke(
            "app-operation", "begin",
            "--run-id", "artifact-pin-drift",
            "--expected-revision", revision,
            "--action", "set-root-title",
            "--subject-id", "root-artifact-pin-drift",
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "retained-runtime-required")
        shown = self.invoke("run", "show", "--run-id", "artifact-pin-drift")
        self.assertEqual(str(shown["revision"]), revision)
        self.assertEqual(shown["runtime_artifact_sha256"], "0" * 64)

    def test_given_drained_schema_one_when_schema_three_prepares_then_state_is_regenerated_without_carry_forward(self) -> None:
        """With no legacy owners, schema 3 replaces schema 1 without copying rows."""
        self.replace_with_schema_one()

        diagnosis = self.invoke("doctor")
        self.assertEqual(diagnosis["state"], "rebuild-ready")
        self.assertFalse(diagnosis["ready"])
        self.assertEqual(diagnosis["observed_database_schema_version"], 1)
        prepared = self.invoke("state", "prepare")
        self.assertEqual(prepared["state"], "regenerated")
        self.assertEqual(prepared["previous_schema_version"], 1)
        self.assertTrue(prepared["regenerated"])

        with sqlite3.connect(self.database) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT singleton,schema_version,target_schema_version FROM runtime_metadata"
                ).fetchone(),
                (1, DATABASE_SCHEMA_VERSION, None),
            )
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0], 0)
        self.assertFalse(self.database.with_name("run-state.lock").exists())

    def test_given_active_schema_one_when_schema_three_prepares_then_it_fails_closed_without_runtime_identity(self) -> None:
        """Schema 3 cannot guess exact runtime identity for active schema-1 owners."""
        self.replace_with_schema_one(active=True)
        diagnosis = self.invoke("doctor")
        self.assertEqual(diagnosis["state"], "waiting-for-schema-drain")
        self.assertEqual(diagnosis["active_owner_runs"], 1)
        unavailable = self.invoke("state", "prepare", expected=4)
        self.assertEqual(
            unavailable["error"]["code"],
            "legacy-runtime-identity-unknown",
        )
        with_runtime = self.invoke(
            "state",
            "prepare",
            "--retained-runtime",
            str(TOOL),
            expected=4,
        )
        self.assertEqual(with_runtime["error"]["code"], "legacy-runtime-identity-unknown")
        with sqlite3.connect(self.database) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT schema_version,target_schema_version FROM runtime_metadata"
                ).fetchone(),
                (1, None),
            )

    def test_given_active_schema_two_when_exact_runtime_is_retained_then_cutover_waits_for_drain(self) -> None:
        """A real 2.0 owner drains through its byte-exact public runtime API."""
        retained, retained_identity = self.historical_runtime("2.0.0")
        self.initialize_historical_schema_two(retained)
        started = self.start_historical_run(
            retained,
            "2.0.0",
            "schema-two-active",
        )
        self.assertEqual(started["status"], "active")

        diagnosis = self.invoke("doctor")
        self.assertEqual(diagnosis["state"], "waiting-for-schema-drain")
        self.assertEqual(diagnosis["observed_database_schema_version"], 2)
        waiting = self.invoke(
            "state",
            "prepare",
            "--retained-runtime",
            str(retained),
        )
        self.assertEqual(waiting["state"], "waiting-for-schema-drain")
        self.assertEqual(waiting["active_owner_runs"], 1)
        self.assertFalse(waiting["regenerated"])
        with sqlite3.connect(self.database) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT schema_version,target_schema_version FROM runtime_metadata"
                ).fetchone(),
                (2, DATABASE_SCHEMA_VERSION),
            )
            self.assertEqual(
                connection.execute(
                    "SELECT runtime_artifact_sha256 FROM runs"
                ).fetchone(),
                (retained_identity[2],),
            )

        drained = self.finish_historical_run(
            retained,
            "schema-two-active",
        )
        self.assertEqual(drained["outcome"], "preimplementation-aborted")
        self.assertTrue(drained["claims_released"])
        with sqlite3.connect(self.database) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT state FROM assignments WHERE run_id=?",
                    ("schema-two-active",),
                ).fetchone(),
                ("preimplementation-aborted",),
            )
            self.assertEqual(
                connection.execute(
                    "SELECT active,release_reason FROM spec_claims WHERE run_id=?",
                    ("schema-two-active",),
                ).fetchone(),
                (0, "preimplementation-aborted"),
            )

        prepared = self.invoke("state", "prepare")
        self.assertEqual(prepared["state"], "regenerated")
        self.assertEqual(prepared["previous_schema_version"], 2)
        with sqlite3.connect(self.database) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT schema_version,target_schema_version FROM runtime_metadata"
                ).fetchone(),
                (DATABASE_SCHEMA_VERSION, None),
            )
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0],
                0,
            )

    def test_given_schema_two_owner_when_only_a_lookalike_runtime_is_retained_then_hash_mismatch_fails(self) -> None:
        """Matching version strings cannot substitute for the pinned executable bytes."""
        pinned, _ = self.historical_runtime(
            "2.0.0",
            name="pinned-runtime",
        )
        lookalike, _ = self.historical_runtime(
            "2.0.0",
            name="lookalike-runtime",
            append_bytes=b"\n",
        )
        self.initialize_historical_schema_two(pinned)
        self.start_historical_run(
            pinned,
            "2.0.0",
            "schema-two-lookalike",
        )

        error = self.invoke(
            "state",
            "prepare",
            "--retained-runtime",
            str(lookalike),
            expected=4,
        )

        self.assertEqual(error["error"]["code"], "retained-runtime-unavailable")
        with sqlite3.connect(self.database) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT schema_version,target_schema_version FROM runtime_metadata"
                ).fetchone(),
                (2, None),
            )

    def test_given_mixed_schema_two_owners_when_all_exact_runtimes_are_retained_then_each_drains_before_cutover(self) -> None:
        """Authentic 2.0 and 3.0 owners each drain through their own public CLI."""
        retained_two, _ = self.historical_runtime(
            "2.0.0",
            name="retained-runtime-2",
        )
        retained_three, _ = self.historical_runtime(
            "3.0.0",
            name="retained-runtime-3",
        )
        self.initialize_historical_schema_two(retained_two)
        self.start_historical_run(
            retained_two,
            "2.0.0",
            "schema-two-active-1",
        )
        self.start_historical_run(
            retained_three,
            "3.0.0",
            "schema-two-active-2",
        )

        missing = self.invoke(
            "state",
            "prepare",
            "--retained-runtime",
            str(retained_two),
            expected=4,
        )
        self.assertEqual(
            missing["error"]["code"],
            "retained-runtime-unavailable",
        )

        waiting = self.invoke(
            "state",
            "prepare",
            "--retained-runtime",
            str(retained_two),
            "--retained-runtime",
            str(retained_three),
        )
        self.assertEqual(waiting["state"], "waiting-for-schema-drain")
        self.assertEqual(waiting["active_owner_runs"], 2)

        for runtime, run_id in (
            (retained_two, "schema-two-active-1"),
            (retained_three, "schema-two-active-2"),
        ):
            drained = self.finish_historical_run(runtime, run_id)
            self.assertEqual(drained["outcome"], "preimplementation-aborted")
            self.assertTrue(drained["claims_released"])

        prepared = self.invoke("state", "prepare")
        self.assertEqual(prepared["state"], "regenerated")
        self.assertEqual(prepared["previous_schema_version"], 2)

    def test_given_injected_recreate_failure_when_cutover_rolls_back_then_old_state_is_exact(self) -> None:
        """Given DROP has begun, a creation failure rolls back both schema and rows."""
        self.replace_with_schema_one()
        before_bytes = self.database.read_bytes()
        with sqlite3.connect(self.database) as connection:
            before_dump = tuple(connection.iterdump())

        namespace = runpy.run_path(str(TOOL), run_name="schema_two_rollback_test")
        original_create = namespace["create_schema"]

        def fail_create(*_: object, **__: object) -> None:
            raise sqlite3.OperationalError("injected schema creation failure")

        namespace["recreate_schema_in_place"].__globals__["create_schema"] = fail_create
        try:
            with mock.patch.dict(os.environ, self.env, clear=True):
                connection = namespace["open_database"](self.database, write=True)
                try:
                    connection.execute("BEGIN EXCLUSIVE")
                    connection.execute(
                        "UPDATE runtime_metadata SET target_schema_version=3 WHERE singleton=1"
                    )
                    with self.assertRaises(sqlite3.OperationalError):
                        namespace["recreate_schema_in_place"](connection)
                    connection.rollback()
                finally:
                    connection.close()
        finally:
            namespace["recreate_schema_in_place"].__globals__["create_schema"] = original_create
        del original_create
        del namespace
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            gc.collect()

        with sqlite3.connect(self.database) as connection:
            self.assertEqual(tuple(connection.iterdump()), before_dump)
        self.assertEqual(self.database.read_bytes(), before_bytes)

    def test_given_newer_schema_when_old_runtime_prepares_then_it_fails_closed(self) -> None:
        """A schema-3 runtime never destroys or downgrades a newer database."""
        self.start("newer-schema")
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "UPDATE runtime_metadata SET schema_version=4 WHERE singleton=1"
            )
        before = self.database.read_bytes()
        doctor = self.invoke("doctor", expected=4)
        self.assertEqual(doctor["error"]["code"], "unsupported-state-schema")
        prepared = self.invoke("state", "prepare", expected=4)
        self.assertEqual(prepared["error"]["code"], "unsupported-state-schema")
        self.assertEqual(self.database.read_bytes(), before)

    def test_given_future_cutover_fence_when_new_run_starts_then_existing_state_remains_readable(self) -> None:
        """A later cutover fence keeps schema-3 owners readable but blocks new runs."""
        self.start("fenced-owner")
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "UPDATE runtime_metadata SET target_schema_version=4 WHERE singleton=1"
            )
        error = self.invoke(
            "run", "start", "--manifest",
            str(self.write_json("fenced-new.json", self.manifest("fenced-new"))),
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "state-cutover-in-progress")
        shown = self.invoke("run", "show", "--run-id", "fenced-owner")
        self.assertEqual(shown["status"], "active")
        diagnosis = self.invoke("doctor")
        self.assertEqual(diagnosis["state"], "cutover-in-progress")
        self.assertFalse(diagnosis["ready"])

    def test_given_unversioned_database_when_read_then_runtime_rejects_it_byte_for_byte(self) -> None:
        """Schema 3 rejects unversioned tables without destructive preparation."""
        self.start("unversioned")
        with sqlite3.connect(self.database) as connection:
            connection.execute("DROP TABLE runtime_metadata")
        before = self.database.read_bytes()
        error = self.invoke("doctor", expected=4)
        self.assertEqual(error["error"]["code"], "unsupported-state-schema")
        self.assertEqual(self.database.read_bytes(), before)
        manifest = self.manifest("unversioned-write")
        write_error = self.invoke(
            "run", "start", "--manifest",
            str(self.write_json("unversioned-write.json", manifest)),
            expected=4,
        )
        self.assertEqual(write_error["error"]["code"], "unsupported-state-schema")
        self.assertEqual(self.database.read_bytes(), before)

    def test_given_corrupt_database_when_doctor_runs_then_it_fails_closed_without_rewrite(self) -> None:
        """Given corrupt bytes, read-only diagnosis reports failure and preserves them."""
        self.database.write_bytes(b"not a sqlite database")
        before = self.database.read_bytes()
        error = self.invoke("doctor", expected=4)
        self.assertEqual(error["error"]["code"], "state-database-error")
        self.assertEqual(self.database.read_bytes(), before)

    def test_given_same_number_schema_with_stale_columns_when_read_then_runtime_rejects_without_deleting_it(self) -> None:
        """A stale schema-3 database fails closed and remains preserved."""
        self.start("stale-columns")
        with sqlite3.connect(self.database) as connection:
            connection.execute("ALTER TABLE assignments ADD COLUMN retired_delivery_mode TEXT")
        error = self.invoke("doctor", expected=4)
        self.assertEqual(error["error"]["code"], "invalid-state-schema")
        self.assertTrue(self.database.exists())

    def test_given_schema_three_with_invalid_metadata_when_read_then_runtime_rejects_without_rewriting_it(self) -> None:
        """Given protocol metadata drift, doctor fails closed and preserves the database bytes."""
        self.start("stale-metadata")
        with sqlite3.connect(self.database) as connection:
            connection.execute("DELETE FROM runtime_metadata")
        before = self.database.read_bytes()
        error = self.invoke("doctor", expected=4)
        self.assertEqual(error["error"]["code"], "invalid-state-schema")
        self.assertEqual(self.database.read_bytes(), before)

    def test_given_schema_three_without_claim_index_when_read_then_runtime_rejects_it(self) -> None:
        """Given a missing uniqueness constraint, exact schema validation prevents unsafe coordination."""
        self.start("missing-claim-index")
        with sqlite3.connect(self.database) as connection:
            connection.execute("DROP INDEX one_active_spec_owner")
        error = self.invoke("doctor", expected=4)
        self.assertEqual(error["error"]["code"], "invalid-state-schema")
        self.assertTrue(self.database.exists())

    def test_given_schema_three_with_extra_trigger_when_read_then_runtime_rejects_it(self) -> None:
        """Given an unexpected state mutation hook, exact schema validation rejects the database."""
        self.start("extra-trigger")
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                """CREATE TRIGGER unexpected_claim_release
                   AFTER UPDATE ON spec_claims
                   BEGIN
                     UPDATE runs SET updated_at=updated_at WHERE run_id=NEW.run_id;
                   END"""
            )
        error = self.invoke("doctor", expected=4)
        self.assertEqual(error["error"]["code"], "invalid-state-schema")

    def test_given_same_number_schema_with_retired_input_state_when_read_then_runtime_fails_closed(self) -> None:
        """Schema 3 rejects the former integration-only state constraint."""
        self.start("stale-state-constraint")
        with sqlite3.connect(self.database) as connection:
            connection.execute("PRAGMA writable_schema=ON")
            connection.execute(
                "UPDATE sqlite_master SET sql=replace(sql, 'peer-input-ready', 'integration-input-ready') "
                "WHERE type='table' AND name='assignments'"
            )
            connection.execute("PRAGMA writable_schema=OFF")
        error = self.invoke("doctor", expected=4)
        self.assertEqual(error["error"]["code"], "invalid-state-schema")
        self.assertTrue(self.database.exists())

    def test_given_schema_three_without_capability_block_state_when_read_then_runtime_fails_closed(self) -> None:
        """A stale schema-3 constraint is rejected without migration or deletion."""
        self.start("stale-capability-state")
        with sqlite3.connect(self.database) as connection:
            connection.execute("PRAGMA writable_schema=ON")
            connection.execute(
                "UPDATE sqlite_master SET sql=replace(sql, 'blocked-app-capability', 'retired-app-capability') "
                "WHERE type='table' AND name='assignments'"
            )
            connection.execute("PRAGMA writable_schema=OFF")
        error = self.invoke("doctor", expected=4)
        self.assertEqual(error["error"]["code"], "invalid-state-schema")
        self.assertTrue(self.database.exists())


if __name__ == "__main__":
    unittest.main()
