from __future__ import annotations

import os
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


class ImplementFeatureContractTests(unittest.TestCase):
    def runtime_text(self) -> str:
        return "\n".join(
            path.read_text(encoding="utf-8")
            for path in [ROOT / "SKILL.md", *(ROOT / "references").glob("*.md")]
        )

    def test_one_shipped_cli_owns_state(self) -> None:
        scripts = sorted(path.name for path in (ROOT / "scripts").iterdir() if path.is_file())
        self.assertEqual(scripts, ["run-state"])
        tool = ROOT / "scripts" / "run-state"
        self.assertTrue(os.access(tool, os.X_OK))
        source = tool.read_text(encoding="utf-8")
        self.assertIn('CLI_VERSION = "1.0.0"', source)
        self.assertIn("STATE_SCHEMA_VERSION = 1", source)
        self.assertIn("BEGIN IMMEDIATE", source)
        for retired in ("fcntl", "StateConnection", "executescript", "run-state-v1.lock"):
            self.assertNotIn(retired, source)

    def test_retired_runtime_surfaces_and_controller_are_absent(self) -> None:
        retired_scripts = {
            "active-root-claim",
            "delivery-preflight",
            "execution-manifest",
            "gitstack-installation-parity",
            "ledger-cache",
        }
        retired_references = {
            "app-control-plane-delays.md",
            "cache-lifecycle.md",
            "controller.md",
            "execution-manifest.md",
            "gitstack-installation-parity.md",
            "task-model-policy.md",
        }
        for name in retired_scripts:
            self.assertFalse((ROOT / "scripts" / name).exists())
        for name in retired_references:
            self.assertFalse((ROOT / "references" / name).exists())
        text = self.runtime_text()
        self.assertNotIn("controller next", text)
        self.assertNotIn("stale_run_retirement_permission", text)

    def test_every_reference_is_directly_routed_from_skill(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        routed = set(re.findall(r"`references/([^`]+\.md)`", skill))
        actual = {path.name for path in (ROOT / "references").glob("*.md")}
        self.assertEqual(routed, actual)

    def test_durable_state_is_not_a_cache_and_has_no_migration(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        run_state = (ROOT / "references" / "run-state.md").read_text(encoding="utf-8")
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("run-state-v1.sqlite3", skill)
        self.assertIn("not a cache", skill)
        self.assertIn("never migrates or imports", run_state)
        self.assertIn("SQLite is the sole writer-coordination surface", run_state)
        self.assertNotIn("run-state-v1.lock", run_state)
        self.assertIn("scripts/run-state", readme)
        self.assertIn("scripts/run-state", agents)
        self.assertNotIn("ledgers/archive", skill + run_state + readme)

    def test_only_fresh_state_schema_is_documented(self) -> None:
        joined = self.runtime_text()
        self.assertNotRegex(joined, r"schema[- ](?:[2-9]|1[0-9])")
        self.assertNotRegex(joined, r"schema(?:_version)?[^\n]*\b(?:[2-9]|1[0-9])\.0\.0\b")

    def test_app_contract_maps_projects_and_inherits_model_defaults(self) -> None:
        app = (ROOT / "references" / "app-orchestration.md").read_text(encoding="utf-8")
        for tool in (
            "codex_app__list_projects",
            "codex_app__list_threads",
            "codex_app__create_thread",
            "codex_app__read_thread",
            "codex_app__wait_threads",
            "codex_app__send_message_to_thread",
            "codex_app__set_thread_title",
            "codex_app__set_thread_archived",
            "get_goal",
            "create_goal",
            "update_goal",
        ):
            self.assertIn(tool, app)
        self.assertIn("Do not pass `model` or `thinking`", app)
        self.assertIn("one project and one App-managed worktree", app)

    def test_goal_is_bound_before_tasks_but_does_not_grant_edit_authority(self) -> None:
        bootstrap = (ROOT / "references" / "root-bootstrap.md").read_text(encoding="utf-8")
        app = (ROOT / "references" / "app-orchestration.md").read_text(encoding="utf-8")
        self.assertLess(bootstrap.index("Create or adopt and read back the root Goal"), bootstrap.index("Dispatch up to three"))
        self.assertIn("Its existence does not grant a\nworker edit authority", app)

    def test_explicit_go_follows_wave_baseline_fan_in(self) -> None:
        app = (ROOT / "references" / "app-orchestration.md").read_text(encoding="utf-8")
        baseline = (ROOT / "references" / "baseline-validation.md").read_text(encoding="utf-8")
        self.assertLess(app.index("Accept the complete baseline set"), app.index("implementation_authority=granted"))
        self.assertIn("fan in all wave baselines before authorizing any worker", baseline)
        self.assertIn("task authorize", app)

    def test_frontier_and_single_repository_task_topology_are_explicit(self) -> None:
        multi = (ROOT / "references" / "multi-repo-workspace.md").read_text(encoding="utf-8")
        worker = (ROOT / "references" / "worker.md").read_text(encoding="utf-8")
        self.assertIn("exactly one affected Git\nrepository", multi)
        self.assertIn("blocked downstream and integration Specs", multi)
        self.assertIn("later `$implement-feature`\ninvocation", multi)
        self.assertIn("one repository, one App project/worktree", worker)

    def test_fast_start_defers_publication_checks(self) -> None:
        bootstrap = (ROOT / "references" / "root-bootstrap.md").read_text(encoding="utf-8")
        self.assertIn("Defer CI, review access, rules,\n   approvals, mergeability, and queue eligibility", bootstrap)
        self.assertIn("only when authorization caused\n   a user wait", bootstrap)
        self.assertIn("may fan out to the three-task limit", bootstrap)
        self.assertIn("do not load `run-state.md`\nduring a healthy fresh start", bootstrap)

        normal_path = [
            ROOT / "SKILL.md",
            ROOT / "references" / "root-bootstrap.md",
            ROOT / "references" / "spec-backed-delivery.md",
            ROOT / "references" / "options.md",
            ROOT / "references" / "app-orchestration.md",
        ]
        self.assertLess(sum(len(path.read_text(encoding="utf-8").splitlines()) for path in normal_path), 550)

    def test_state_uses_typed_lifecycle_not_generic_receipts(self) -> None:
        run_state = (ROOT / "references" / "run-state.md").read_text(encoding="utf-8")
        for command in (
            "goal bind",
            "goal complete",
            "task bind",
            "task baseline",
            "task authorize",
            "task ready",
            "task abort",
            "operation list",
        ):
            self.assertIn(command, run_state)
        for retired in ("event record", "event list", "task-set-verified", "evidence_refs"):
            self.assertNotIn(retired, run_state)

    def test_checkout_and_pull_request_identity_are_bound_before_ready(self) -> None:
        bootstrap = (ROOT / "references" / "root-bootstrap.md").read_text(encoding="utf-8")
        run_state = (ROOT / "references" / "run-state.md").read_text(encoding="utf-8")
        publication = (ROOT / "references" / "worker-publication.md").read_text(encoding="utf-8")
        self.assertIn("git_common_dir", bootstrap)
        self.assertIn("Git common-directory path and filesystem\nidentity", run_state)
        self.assertIn("ensure-pull-request-ready", run_state)
        self.assertIn("github_mark_pull_request_ready_for_review", publication)
        self.assertIn("base equal to the observed default branch", run_state)
        tool = (ROOT / "scripts" / "run-state").read_text(encoding="utf-8")
        self.assertIn("git_common_paths", tool)
        self.assertIn("git_common_fs_ids", tool)

    def test_start_over_is_preimplementation_only(self) -> None:
        recovery = (ROOT / "references" / "recovery-validation.md").read_text(encoding="utf-8")
        self.assertIn("Use start over for preimplementation state only", recovery)
        self.assertIn("Once any task received `implementation_authority=granted`", recovery)
        self.assertIn("imports nothing", recovery)


if __name__ == "__main__":
    unittest.main()
