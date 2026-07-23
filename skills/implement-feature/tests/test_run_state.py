from __future__ import annotations

import contextlib
import gc
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

    def future_schema_two_tool(self) -> Path:
        path = self.base / "run-state-schema-2"
        source = TOOL.read_text(encoding="utf-8")
        source = source.replace('CLI_VERSION = "1.1.0"', 'CLI_VERSION = "2.0.0"', 1)
        source = source.replace("STATE_SCHEMA_VERSION = 1", "STATE_SCHEMA_VERSION = 2", 1)
        source = source.replace(
            "REBUILDABLE_STATE_SCHEMA_VERSIONS = frozenset()",
            "REBUILDABLE_STATE_SCHEMA_VERSIONS = frozenset({1})",
            1,
        )
        source = source.replace(
            "RETAINED_RUNTIME_SHA256_BY_SCHEMA: dict[int, str] = {}",
            f"RETAINED_RUNTIME_SHA256_BY_SCHEMA: dict[int, str] = "
            f"{{1: {hashlib.sha256(TOOL.read_bytes()).hexdigest()!r}}}",
            1,
        )
        path.write_text(source, encoding="utf-8")
        path.chmod(0o700)
        return path

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
        tracker_backend: str | None = None,
        delivery_type: str | None = None,
    ) -> dict[str, object]:
        repositories = repositories or [("github:example/project", self.common_a)]
        repo_rows = [
            {"repository_identity": identity, "git_common_dir": str(common)}
            for identity, common in repositories
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
                    "project_id": f"{project_prefix}-{index % len(repositories) + 1}",
                    "title": f"🛠️ Feature {index + 1}",
                    "target_branch_name": f"feature/example-{index + 1}",
                    "prerequisite_assignment_ids": [],
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
        if not self.database.exists():
            self.invoke("state", "prepare")
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

    def ready_worker(
        self,
        run_id: str,
        number: int = 1,
        *,
        schema_version: int = 1,
        review_profile: str = "standard",
        review_candidate_head_sha: str | None = None,
        codex_review_head_sha: str | None = None,
        expected: int = 0,
    ) -> dict[str, object]:
        sha = f"{100 + number:040x}"
        observation = {
            "schema_version": schema_version,
            "assignment_id": f"spec-{number:02d}",
            "thread_id": f"thread-{run_id}-{number}",
            "repository_identity": "github:example/project",
            "delivery_type": "github-pr",
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
        peer_input: bool = False,
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
            "schema_version": 1,
            "assignment_id": f"spec-{number:02d}",
            "thread_id": f"thread-{run_id}-{number}",
            "repository_identity": repository_identity or self.local_identity(self.common_a),
            "delivery_type": "local-branch",
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
        if peer_input:
            arguments.append("--peer-input")
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
        """Given no DB, when doctor runs, then it reports schema 1 without creating cache state."""
        self.database.unlink()
        result = self.invoke("doctor")
        self.assertEqual(result["tool_version"], "1.1.0")
        self.assertEqual(result["state_schema_version"], 1)
        self.assertEqual(result["active_owner_runs"], 0)
        self.assertEqual(result["busy_timeout_ms"], 5000)
        self.assertFalse(self.database.exists())
        self.assertFalse(self.database.with_name("run-state.lock").exists())

    def test_given_fresh_user_when_state_prepares_then_schema_and_metadata_are_created(self) -> None:
        """Given no DB, explicit preparation creates the fresh schema-1 claim domain."""
        self.database.unlink()
        prepared = self.invoke("state", "prepare")
        self.assertEqual(prepared["state"], "initialized")
        self.assertEqual(prepared["database_schema_version"], 1)
        self.assertTrue(prepared["regenerated"])
        self.assertTrue(prepared["writes_performed"])
        self.assertTrue(self.database.is_file())
        self.assertFalse(self.database.with_name("run-state.lock").exists())
        with sqlite3.connect(self.database) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT singleton,schema_version,target_schema_version FROM runtime_metadata"
                ).fetchall(),
                [(1, 1, None)],
            )
        started = self.start("prepared-fresh")
        self.assertEqual(started["status"], "active")

    def test_given_unversioned_manifest_when_run_starts_then_payload_is_rejected_before_state(self) -> None:
        """Given an unversioned protocol payload, startup fails closed without creating the database."""
        self.database.unlink()
        manifest = self.manifest("unversioned-manifest")
        manifest["schema_version"] = 0
        error = self.invoke(
            "run", "start", "--manifest",
            str(self.write_json("unversioned-manifest.json", manifest)),
            expected=2,
        )
        self.assertEqual(error["schema_version"], 1)
        self.assertEqual(error["error"]["code"], "unsupported-input-schema")
        self.assertFalse(self.database.exists())

    def test_given_v2_manifest_when_run_starts_then_payload_is_rejected_before_state(self) -> None:
        """Given the immediately retired protocol payload, startup performs no compatibility conversion."""
        self.database.unlink()
        manifest = self.manifest("v2-manifest")
        manifest["schema_version"] = 2
        error = self.invoke(
            "run", "start", "--manifest",
            str(self.write_json("v2-manifest.json", manifest)),
            expected=2,
        )
        self.assertEqual(error["schema_version"], 1)
        self.assertEqual(error["error"]["code"], "unsupported-input-schema")
        self.assertFalse(self.database.exists())

    def test_given_newer_task_observation_when_reconciled_then_operation_remains_pending(self) -> None:
        """Given a newer task payload, reconciliation rejects it without advancing durable state."""
        self.start("v1-operation")
        self.invoke(
            "app-operation", "begin", "--run-id", "v1-operation",
            "--expected-revision", self.revision("v1-operation"),
            "--operation-key", "root-title", "--action", "set-root-title",
            "--subject-id", "root-v1-operation",
        )
        revision = self.revision("v1-operation")
        observation = {
            "schema_version": 2,
            "status": "succeeded",
            "receipt_ref": "receipt:v1-title",
            "readback_ref": "readback:v1-title",
            "observed_title": "Feature Orchestrator",
        }
        error = self.invoke(
            "app-operation", "finish", "--run-id", "v1-operation",
            "--expected-revision", revision, "--operation-key", "root-title",
            "--observation", str(self.write_json("v1-operation.json", observation)),
            expected=2,
        )
        self.assertEqual(error["error"]["code"], "invalid-operation-observation")
        shown = self.invoke("run", "show", "--run-id", "v1-operation")
        self.assertEqual(shown["revision"], int(revision))
        self.assertEqual(shown["unresolved_app_operations"][0]["status"], "pending")

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
        self.invoke(
            "app-operation", "begin", "--run-id", "wrong-root-title",
            "--expected-revision", self.revision("wrong-root-title"),
            "--operation-key", "wrong-root-title-op", "--action", "set-root-title",
            "--subject-id", "root-wrong-root-title",
        )
        observation = {
            "schema_version": 1,
            "status": "succeeded",
            "receipt_ref": "receipt:wrong-root-title",
            "readback_ref": "readback:wrong-root-title",
            "observed_title": "🤖 Feature Orchestrator · 1 Features",
        }
        error = self.invoke(
            "app-operation", "finish", "--run-id", "wrong-root-title",
            "--expected-revision", self.revision("wrong-root-title"),
            "--operation-key", "wrong-root-title-op",
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
        error = self.invoke(
            "app-operation", "begin", "--run-id", "repeat-root-title",
            "--expected-revision", self.revision("repeat-root-title"),
            "--operation-key", "repeat-root-title-second", "--action", "set-root-title",
            "--subject-id", "root-repeat-root-title", expected=4,
        )
        self.assertEqual(error["error"]["code"], "protected-operation-already-started")

    def test_given_newer_ready_observation_when_recorded_then_assignment_and_claim_remain_active(self) -> None:
        """Given newer delivery evidence, readiness rejects it without releasing ownership."""
        self.start("v1-ready")
        self.create_worker("v1-ready")
        error = self.ready_worker("v1-ready", schema_version=2, expected=2)
        self.assertEqual(error["error"]["code"], "invalid-ready-observation")
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
            "schema_version": 1,
            "assignment_id": "spec-01",
            "thread_id": "thread-delivery-mismatch-1",
            "repository_identity": identity,
            "delivery_type": "github-pr",
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
            peer_input=True,
        )
        self.assertEqual(partial["state"], "peer-input-ready")
        exact_head = f"{201:040x}"
        proof_owner = self.ready_local_worker(
            "integration-vector", number=2, repository_identity=identity,
            prerequisite_heads={"spec-01": exact_head}, peer_input=True,
        )
        self.assertEqual(proof_owner["state"], "peer-input-ready")

        replacement_head = f"{777:040x}"
        self.ready_local_worker(
            "integration-vector", number=1, repository_identity=identity,
            peer_input=True, head_sha=replacement_head,
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
            "peer-block", number=1, repository_identity=identity, peer_input=True,
        )
        blocked = self.invoke(
            "assignment", "block", "--run-id", "peer-block",
            "--expected-revision", self.revision("peer-block"),
            "--assignment-id", "spec-01",
        )
        self.assertEqual(blocked["state"], "blocked-durable-contract")
        self.assertTrue(blocked["claim_retained"])
        resumed = self.invoke(
            "assignment", "resume", "--run-id", "peer-block",
            "--expected-revision", self.revision("peer-block"),
            "--assignment-id", "spec-01",
        )
        self.assertEqual(resumed["state"], "peer-input-ready")
        self.assertEqual(resumed["run_status"], "active")
        self.assertTrue(resumed["claim_retained"])

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
        resumed = self.invoke(
            "assignment", "resume", "--run-id", "capability-block",
            "--expected-revision", self.revision("capability-block"),
            "--assignment-id", "spec-01",
        )
        self.assertEqual(resumed["state"], "active")
        self.assertEqual(resumed["run_status"], "active")

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

    def test_given_one_workspace_project_for_two_repositories_when_manifest_is_validated_then_both_assignments_are_allowed(self) -> None:
        """Given a multi-repository project, when start validates exact repos, then the shared project ID is not repository identity."""
        manifest = self.manifest(
            "bad-project",
            repositories=[("github:example/a", self.common_a), ("github:example/b", self.common_b)],
            assignment_count=2,
        )
        manifest["assignments"][1]["project_id"] = manifest["assignments"][0]["project_id"]
        result = self.invoke(
            "run", "start", "--manifest", str(self.write_json("workspace-project.json", manifest)),
        )
        self.assertEqual(result["acquired_assignment_ids"], ["spec-01", "spec-02"])

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

    def test_given_three_live_workers_when_fourth_creation_begins_then_capacity_blocks(self) -> None:
        """Given three live workers, when root tries a fourth, then the generic coordinator serializes it."""
        self.start("four", assignment_count=4)
        for number in (1, 2, 3):
            self.create_worker("four", number)
        error = self.invoke(
            "app-operation", "begin", "--run-id", "four", "--expected-revision", self.revision("four"),
            "--operation-key", "create-fourth", "--action", "create-worker", "--subject-id", "spec-04",
            expected=4,
        )
        self.assertEqual(error["error"]["code"], "worker-capacity-reached")

    def test_given_one_worker_is_parked_for_peers_when_fourth_creation_begins_then_slot_is_reused(self) -> None:
        """Given three created peers, input-ready parking preserves repair access without blocking the next assignment."""
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
            "parked-peer", number=1, repository_identity=identity, peer_input=True,
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
        result = self.invoke(
            "app-operation", "begin", "--run-id", "worker-ready",
            "--expected-revision", self.revision("worker-ready"),
            "--operation-key", "early-worker", "--action", "create-worker",
            "--subject-id", "spec-01",
        )
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
        self.invoke(
            "app-operation", "begin", "--run-id", "ambiguous-worker",
            "--expected-revision", self.revision("ambiguous-worker"),
            "--operation-key", "create-ambiguous", "--action", "create-worker",
            "--subject-id", "spec-01",
        )
        unknown = {"schema_version": 1, "status": "unknown"}
        self.invoke(
            "app-operation", "finish", "--run-id", "ambiguous-worker",
            "--expected-revision", self.revision("ambiguous-worker"),
            "--operation-key", "create-ambiguous",
            "--observation", str(self.write_json("create-ambiguous-unknown.json", unknown)),
        )
        blocked = self.invoke(
            "app-operation", "begin", "--run-id", "ambiguous-worker",
            "--expected-revision", self.revision("ambiguous-worker"),
            "--operation-key", "create-duplicate", "--action", "create-worker",
            "--subject-id", "spec-01", expected=4,
        )
        self.assertEqual(blocked["error"]["code"], "protected-operation-already-started")
        checkout = self.base / "checkout ambiguous worker"
        checkout.mkdir()
        succeeded = {
            "schema_version": 1,
            "status": "succeeded",
            "receipt_ref": "receipt:create-ambiguous",
            "readback_ref": "readback:create-ambiguous",
            "thread_id": "thread-ambiguous-worker-1",
            "project_id": "project-1",
            "checkout_path": str(checkout),
            "git_common_dir": str(self.common_a),
            "observed_state": "active",
        }
        self.invoke(
            "app-operation", "finish", "--run-id", "ambiguous-worker",
            "--expected-revision", self.revision("ambiguous-worker"),
            "--operation-key", "create-ambiguous",
            "--observation", str(self.write_json("create-ambiguous-succeeded.json", succeeded)),
        )
        shown = self.invoke("run", "show", "--run-id", "ambiguous-worker")
        operations = self.invoke("app-operation", "list", "--run-id", "ambiguous-worker")
        self.assertEqual(shown["assignments"][0]["state"], "worker-created")
        self.assertEqual([row["operation_key"] for row in operations["operations"]], ["create-ambiguous"])

    def test_given_existing_worker_identity_when_stale_readback_reuses_it_then_binding_fails(self) -> None:
        """Given one worker/worktree binding, when another assignment receives the same readback, then it cannot alias."""
        self.start("alias", assignment_count=2)
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
        self.create_worker("wrong-base")
        observation = {
            "schema_version": 1, "assignment_id": "spec-01",
            "thread_id": "thread-wrong-base-1",
            "repository_identity": "github:example/project",
            "delivery_type": "github-pr", "head_sha": f"{101:040x}",
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
            "schema_version": 1,
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
            "schema_version": 2,
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
        self.assertEqual(error["error"]["code"], "unsupported-input-schema")
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
            "schema_version": 1,
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
            "schema_version": 1,
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
            "schema_version": 1,
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

    def test_given_confirmed_failed_app_operation_when_retried_then_new_key_is_allowed(self) -> None:
        """Given readback proves no worker was created, when root retries, then a new operation key may launch."""
        self.start("retry")
        self.operation(
            "retry", "worker-failed", "create-worker", "spec-01", {}, status="failed"
        )
        result = self.invoke(
            "app-operation", "begin", "--run-id", "retry",
            "--expected-revision", self.revision("retry"),
            "--operation-key", "worker-retry", "--action", "create-worker",
            "--subject-id", "spec-01",
        )
        self.assertTrue(result["launch_authorized"])

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
            "schema_version": 1,
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
            "schema_version": 1,
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
            "schema_version": 1,
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
            "schema_version": 1,
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

    def test_given_unknown_bootstrap_effect_when_readback_arrives_then_same_key_reconciles(self) -> None:
        """Given ambiguous App delivery, when receipt readback resolves, then the same key succeeds without hashes."""
        self.start("recover")
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
            "--operation-key", "root-title-unknown", "--action", "set-root-title",
            "--subject-id", "root-no-receipt",
        )
        observation = {"schema_version": 1, "status": "unknown"}
        result = self.invoke(
            "app-operation", "finish", "--run-id", "no-receipt",
            "--expected-revision", self.revision("no-receipt"),
            "--operation-key", "root-title-unknown",
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

    def test_given_schema_when_inspected_then_only_allowlisted_state_and_no_text_hashes_exist(self) -> None:
        """Given initialized schema, when tables and columns are inspected, then storage is narrow and hash-free."""
        self.start("schema")
        with sqlite3.connect(self.database) as connection:
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
            columns = [row[1] for table in tables for row in connection.execute(f"PRAGMA table_info({table})")]
            metadata = connection.execute(
                "SELECT singleton,schema_version,target_schema_version FROM runtime_metadata"
            ).fetchall()
        self.assertEqual(tables, {"runtime_metadata", "runs", "assignments", "spec_claims", "app_operations"})
        self.assertEqual(metadata, [(1, 1, None)])
        self.assertNotIn("goal_state", columns)
        self.assertFalse(any("sha256" in column or "body" in column or "checklist" in column or "attempt" in column for column in columns))
        before = self.database.read_bytes()
        diagnosis = self.invoke("doctor")
        self.assertFalse(diagnosis["writes_performed"])
        self.assertEqual(self.database.read_bytes(), before)
        with sqlite3.connect(self.database) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO runtime_metadata(singleton,schema_version) VALUES (2,1)"
                )

    def test_given_future_schema_two_and_drained_schema_one_then_state_is_regenerated_without_carry_forward(self) -> None:
        """Given a future approved runtime and no old owners, it replaces schema 1 with empty schema 2."""
        self.start("drained-v1")
        self.invoke(
            "run", "finish", "--run-id", "drained-v1",
            "--expected-revision", self.revision("drained-v1"),
            "--outcome", "preimplementation-aborted",
        )
        future = self.future_schema_two_tool()

        diagnosis = self.invoke_tool(future, "doctor")
        self.assertEqual(diagnosis["state"], "rebuild-ready")
        self.assertFalse(diagnosis["ready"])
        self.assertEqual(diagnosis["database_schema_version"], 1)
        prepared = self.invoke_tool(future, "state", "prepare")
        self.assertEqual(prepared["state"], "regenerated")
        self.assertEqual(prepared["previous_schema_version"], 1)
        self.assertTrue(prepared["regenerated"])

        with sqlite3.connect(self.database) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT singleton,schema_version,target_schema_version FROM runtime_metadata"
                ).fetchone(),
                (1, 2, None),
            )
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0], 0)
        self.assertFalse(self.database.with_name("run-state.lock").exists())

    def test_given_future_schema_two_and_active_schema_one_then_old_runtime_can_drain_under_fence(self) -> None:
        """Given a future cut, new starts stop while the retained old runtime terminalizes its owner."""
        self.start("active-v1")
        future = self.future_schema_two_tool()
        diagnosis = self.invoke_tool(future, "doctor")
        self.assertEqual(diagnosis["state"], "waiting-for-schema-drain")
        self.assertEqual(diagnosis["active_owner_runs"], 1)
        unavailable = self.invoke_tool(future, "state", "prepare", expected=4)
        self.assertEqual(
            unavailable["error"]["code"],
            "retained-runtime-unavailable",
        )
        counterfeit = self.base / "counterfeit-schema-1"
        counterfeit.write_text(
            TOOL.read_text(encoding="utf-8") + "\n# different executable\n",
            encoding="utf-8",
        )
        counterfeit.chmod(0o700)
        mismatch = self.invoke_tool(
            future,
            "state",
            "prepare",
            "--retained-runtime",
            str(counterfeit),
            expected=4,
        )
        self.assertEqual(mismatch["error"]["code"], "retained-runtime-unavailable")
        prepared = self.invoke_tool(
            future,
            "state",
            "prepare",
            "--retained-runtime",
            str(TOOL),
        )
        self.assertEqual(prepared["state"], "waiting-for-schema-drain")
        self.assertEqual(prepared["active_owner_runs"], 1)
        with sqlite3.connect(self.database) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT schema_version,target_schema_version FROM runtime_metadata"
                ).fetchone(),
                (1, 2),
            )
        blocked = self.invoke(
            "run", "start", "--manifest",
            str(self.write_json("blocked-during-cut.json", self.manifest("blocked-during-cut"))),
            expected=4,
        )
        self.assertEqual(blocked["error"]["code"], "state-cutover-in-progress")

        self.invoke(
            "run", "finish", "--run-id", "active-v1",
            "--expected-revision", self.revision("active-v1"),
            "--outcome", "preimplementation-aborted",
        )
        completed = self.invoke_tool(future, "state", "prepare")
        self.assertEqual(completed["state"], "regenerated")
        self.assertFalse(self.database.with_name("run-state.lock").exists())

    def test_given_injected_recreate_failure_when_cutover_rolls_back_then_old_state_is_exact(self) -> None:
        """Given DROP has begun, a creation failure rolls back both schema and rows."""
        self.start("rollback-v1")
        self.invoke(
            "run", "finish", "--run-id", "rollback-v1",
            "--expected-revision", self.revision("rollback-v1"),
            "--outcome", "preimplementation-aborted",
        )
        future = self.future_schema_two_tool()
        before_bytes = self.database.read_bytes()
        with sqlite3.connect(self.database) as connection:
            before_dump = tuple(connection.iterdump())

        namespace = runpy.run_path(str(future), run_name="future_rollback_test")
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
                        "UPDATE runtime_metadata SET target_schema_version=2 WHERE singleton=1"
                    )
                    with self.assertRaises(sqlite3.OperationalError):
                        namespace["recreate_schema_in_place"](connection)
                    connection.rollback()
                finally:
                    connection.close()
        finally:
            namespace["recreate_schema_in_place"].__globals__["create_schema"] = original_create

        with sqlite3.connect(self.database) as connection:
            self.assertEqual(tuple(connection.iterdump()), before_dump)
        self.assertEqual(self.database.read_bytes(), before_bytes)

    def test_given_newer_schema_when_old_runtime_prepares_then_it_fails_closed(self) -> None:
        """Given a newer DB, schema-1 runtime never destroys or downgrades it."""
        self.start("newer-schema")
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "UPDATE runtime_metadata SET schema_version=2 WHERE singleton=1"
            )
        before = self.database.read_bytes()
        doctor = self.invoke("doctor", expected=4)
        self.assertEqual(doctor["error"]["code"], "unsupported-state-schema")
        prepared = self.invoke("state", "prepare", expected=4)
        self.assertEqual(prepared["error"]["code"], "unsupported-state-schema")
        self.assertEqual(self.database.read_bytes(), before)

    def test_given_future_cutover_fence_when_new_run_starts_then_existing_state_remains_readable(self) -> None:
        """Given a later runtime has fenced starts, schema-1 may inspect owners but cannot create another run."""
        self.start("fenced-owner")
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "UPDATE runtime_metadata SET target_schema_version=2 WHERE singleton=1"
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
        """Given unversioned tables, schema 1 rejects them without destructive preparation."""
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
        """Given a stale schema-1 DB, when opened, then exact structure fails closed and the file is preserved."""
        self.start("stale-columns")
        with sqlite3.connect(self.database) as connection:
            connection.execute("ALTER TABLE assignments ADD COLUMN retired_delivery_mode TEXT")
        error = self.invoke("doctor", expected=4)
        self.assertEqual(error["error"]["code"], "invalid-state-schema")
        self.assertTrue(self.database.exists())

    def test_given_schema_one_with_invalid_metadata_when_read_then_runtime_rejects_without_rewriting_it(self) -> None:
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
        """Given the former integration-only state constraint, schema 1 rejects it before a later write."""
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
        """Given a stale schema-1 constraint, the runtime rejects it without migration or deletion."""
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
