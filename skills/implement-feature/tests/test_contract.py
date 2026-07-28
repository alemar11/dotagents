from __future__ import annotations

import os
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


class ImplementFeatureContractScenarios(unittest.TestCase):
    def text(self, name: str) -> str:
        return (ROOT / name).read_text(encoding="utf-8")

    def runtime_text(self) -> str:
        return "\n".join(
            path.read_text(encoding="utf-8")
            for path in [ROOT / "SKILL.md", *(ROOT / "references").glob("*.md")]
        )

    @staticmethod
    def normalized(contents: str) -> str:
        return " ".join(contents.split())

    def test_given_startup_when_authorization_is_resolved_then_it_is_the_only_user_interaction(self) -> None:
        """Given startup, when required fields are granted, then no later authority question is allowed."""
        options_raw = self.text("references/options.md")
        options = self.normalized(options_raw)
        skill = self.text("SKILL.md")
        self.assertIn("same startup authorization interaction", options)
        self.assertIn("do not ask another user question", options)
        self.assertIn("Never ask another authority, recovery", skill)
        self.assertEqual(
            len(re.findall(r"^\| `visible_app_task_permission` \|", options_raw, re.MULTILINE)),
            1,
        )
        self.assertIn("`missing_project_action`", options)
        self.assertIn("`create-projects`, `stop`", options)

    def test_given_missing_saved_projects_when_preflight_runs_then_setup_is_explicit_and_pre_state(self) -> None:
        """Given a missing project mapping, preflight asks once or stops before operational state."""
        skill = self.normalized(self.text("SKILL.md"))
        bootstrap = self.normalized(self.text("references/root-bootstrap.md"))
        options = self.normalized(self.text("references/options.md"))
        orchestration = self.normalized(self.text("references/codex-task-orchestration.md"))
        self.assertIn("exact repository-to-worker-project mapping before state", skill)
        self.assertIn("whose reported primary folder is exactly that repository root", bootstrap)
        self.assertIn("Reject remote, non-Git, duplicate eligible repo-project", bootstrap)
        self.assertIn("before writing the manifest or calling `scripts/run-state`", bootstrap)
        self.assertIn("Project creation is distinct from task creation", options)
        self.assertIn("never treat task permission as project-creation permission", options)
        self.assertIn("worker-project preflight", orchestration)

    def test_given_multifolder_controller_when_workers_are_created_then_repo_projects_remain_separate(self) -> None:
        """Given a multi-folder root, workers still target their repo-specific saved projects."""
        skill = self.normalized(self.text("SKILL.md"))
        bootstrap = self.normalized(self.text("references/root-bootstrap.md"))
        options = self.normalized(self.text("references/options.md"))
        self.assertIn("controller task may be bound to a local Codex multi-folder project", skill)
        self.assertIn("treat every attached folder as read-only coordination context", skill)
        self.assertIn("never use that controller project as a worker target", skill)
        self.assertIn("exclude its project ID from worker mapping", bootstrap)
        self.assertIn("primary and secondary folder memberships are context only", bootstrap)
        self.assertIn("always targets the assignment's recorded repo-specific `project_id`", bootstrap)
        self.assertIn("do not satisfy this worker-project requirement", options)

    def test_given_authorized_project_setup_when_computer_use_selects_then_exact_paths_are_required(self) -> None:
        """Given create-projects authority, Computer Use may create only exact verified Git roots."""
        options = self.normalized(self.text("references/options.md"))
        self.assertIn("authorizes only the exact paths listed in the question", options)
        self.assertIn("require exact equality with the expected Git root", options)
        self.assertIn("read `list_projects` again", options)
        self.assertIn("Never create a broader substitute", options)
        self.assertIn("a parent root or `/private/tmp`", options)

    def test_given_compatible_operational_edits_when_worker_rereads_then_it_continues(self) -> None:
        """Given compatible design or test edits, when reread occurs, then worker accepts them autonomously."""
        spec = self.text("references/feature-spec-contract.md")
        worker = self.normalized(self.text("references/worker-execution.md"))
        self.assertIn("implementation approach or internal technical design", spec)
        self.assertIn("additional or equivalent tests", spec)
        self.assertIn("accept compatible operational changes and continue autonomously", worker)

    def test_given_stable_drift_when_worker_rereads_then_it_blocks_without_asking(self) -> None:
        """Given outcome or acceptance drift, when detected, then worker declaratively blocks."""
        spec = self.text("references/feature-spec-contract.md")
        self.assertIn("acceptance text", spec)
        self.assertIn("material validation budget/terminal result changes", spec)
        self.assertIn("blocked-durable-contract", spec)
        self.assertIn("without asking", spec)

    def test_given_github_or_local_tracker_when_checkbox_changes_then_readback_and_invalidation_are_required(self) -> None:
        """Given GitHub or local Markdown, when proof changes, then checkboxes update and invalid proof is unchecked."""
        tracker = self.text("references/tracker-checklists.md")
        self.assertIn("GitHub or local", tracker)
        self.assertIn("only after that current-head proof exists", tracker)
        self.assertIn("uncheck it immediately", tracker)
        self.assertIn("Read the authoritative issue again", tracker)
        self.assertIn("moving an issue into `issues/done/` is the completion", tracker)
        self.assertIn("never write\n`workflow_state: done`", tracker)

    def test_given_worker_handoff_when_root_closes_then_root_is_read_only(self) -> None:
        """Given PR-ready worker evidence, when root verifies, then it never judges or edits criteria."""
        gates = self.text("references/final-verification.md")
        tracker = self.text("references/tracker-checklists.md")
        self.assertIn("performs read-only verification", gates)
        self.assertIn("does not edit code", gates)
        self.assertIn("must not edit, check, uncheck, reinterpret, or adjudicate", tracker)

    def test_given_review_handoff_when_capability_is_resolved_then_identity_and_owner_are_explicit(self) -> None:
        """The bootstrap field and review command are literal machine-facing contracts."""
        skill = self.text("SKILL.md")
        bootstrap = self.text("references/root-bootstrap.md")
        orchestration = self.text("references/codex-task-orchestration.md")
        worker = self.text("references/worker-execution.md")
        runtime = self.text("scripts/run-state")
        for source in (skill, bootstrap, orchestration, worker):
            self.assertIn("review_owner=worker|root", source)
        self.assertIn("review-candidate", orchestration)
        self.assertIn("review-candidate", worker)
        self.assertIn("--review-phase full", orchestration)
        self.assertIn("--evidence-output", orchestration)
        normalized_worker = self.normalized(worker)
        self.assertIn(
            "With `review_owner=worker`, the worker invokes `$autoreview`.",
            normalized_worker,
        )
        self.assertIn(
            "With `review_owner=root`, the worker sends only the authoritative review-candidate handoff",
            normalized_worker,
        )
        self.assertNotIn("before invoking `$autoreview`", normalized_worker)
        self.assertIn('"set-review-owner"', runtime)
        self.assertIn("def canonical_review_owner", runtime)
        self.assertIn("PROTECTED_REPLAY_ACTIONS", runtime)
        self.assertIn("send-bootstrap requires --review-owner worker|root", runtime)
        self.assertIn("review-owner-conflict", runtime)
        self.assertIn("A root-owned AutoReview result follow-up contains only", orchestration)
        self.assertIn("verbatim structured AutoReview result", orchestration)

    def test_given_bootstrap_recovery_when_state_is_ambiguous_then_actual_task_state_prevents_duplicates(self) -> None:
        """Given ambiguous delivery, when recovering, then root inspects the task before repeating and stores no body hash."""
        orchestration = self.text("references/codex-task-orchestration.md")
        recovery = self.text("references/claim-waits-and-recovery.md")
        normalized = self.normalized(orchestration)
        self.assertIn("record the intended operation in SQLite before changing", normalized)
        self.assertIn("after an interruption, inspect the actual object first", normalized)
        self.assertIn("Bootstrap may replay after `unknown` or `failed` readback", normalized)
        self.assertIn("actions may replay only from `failed` with readback", normalized)
        self.assertIn("retain the same `operation_id`", normalized)
        self.assertIn("retain the same `bootstrap_id`", normalized)
        self.assertIn(
            "never infer delivery from a stored body or hash",
            self.normalized(recovery),
        )

    def test_given_same_repo_assignments_when_paths_overlap_then_root_serializes_them(self) -> None:
        """Given overlap in one repository, root serializes conflicts without numerically capping disjoint work."""
        skill = self.normalized(self.text("SKILL.md"))
        orchestration = self.normalized(self.text("references/codex-task-orchestration.md"))
        self.assertIn("schedule every claimed Feature Spec allowed by path and dependency serialization", skill)
        self.assertIn("overlapping paths or issue dependencies serialize", self.text("references/feature-spec-contract.md"))
        self.assertIn("Do not impose a numeric worker limit", orchestration)
        self.assertIn("`peer-input-ready` is parked", orchestration)

    def test_given_root_assignments_when_title_is_set_then_it_is_exact_and_immutable(self) -> None:
        """Given one or many Specs, when root is titled, then its static total is exact UI evidence."""
        orchestration = self.normalized(self.text("references/codex-task-orchestration.md"))
        self.assertIn("`🤖 Feature Orchestrator`", orchestration)
        self.assertIn("`🤖 Feature Orchestrator · N Features`", orchestration)
        self.assertIn("including waiting or blocked assignments", orchestration)
        self.assertIn("Never update the root title as assignments progress", orchestration)
        self.assertIn("The title is UI evidence, never identity or durable state", orchestration)
        self.assertNotIn("👨🏻‍💻", orchestration)
        self.assertNotIn("Multi-Feature Orchestrator", orchestration)
        self.assertNotIn("R/N", orchestration)

    def test_given_goal_free_controller_when_runtime_is_inspected_then_run_and_task_own_lifecycle(self) -> None:
        """Given the lean controller, runtime state and task liveness replace synthetic lifecycle state."""
        runtime = self.runtime_text()
        source = self.text("scripts/run-state")
        skill = self.normalized(self.text("SKILL.md"))
        orchestration = self.normalized(self.text("references/codex-task-orchestration.md"))
        self.assertIn("unfinished run remains the sole controller", skill)
        self.assertIn("root keeps its current turn open", skill)
        self.assertIn("manual in the exact same root task", orchestration)
        self.assertIn('"may_create_worker"', source)
        self.assertNotIn('"goal_state"', source)
        self.assertIsNone(re.search(r"\bGoal\b", runtime))
        for retired_action in ("create-goal", "update-goal-progress", "complete-goal"):
            self.assertNotIn(retired_action, source)
            self.assertNotIn(retired_action, runtime)

    def test_given_schema_three_lineage_when_runtime_is_inspected_then_versions_and_claim_domain_are_explicit(self) -> None:
        """Given the current runtime, schema-three state stays at one unversioned canonical path."""
        source = self.text("scripts/run-state")
        state = self.normalized(self.text("references/run-state.md"))
        self.assertIn('CLI_VERSION = "4.1.0"', source)
        self.assertIn('RUNTIME_CONTRACT_VERSION = "4.1.0"', source)
        self.assertIn("DATABASE_SCHEMA_VERSION = 3", source)
        self.assertIn('"schema": "implement-feature/run-manifest"', source)
        self.assertIn('"schema_version": "3.0.0"', source)
        self.assertIn(
            '"schema": "implement-feature/feature-spec-set-input"',
            source,
        )
        self.assertIn("SCHEMA_TWO_COLUMNS", source)
        self.assertIn("run_repositories", source)
        self.assertIn('"feature_id"', source)
        self.assertIn("feature-spec-set validate", state)
        self.assertIn("scripts/run-state --json state prepare", state)
        self.assertIn("drops all application tables, indexes, and triggers", state)
        self.assertIn("without carrying any row forward", (REPO / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertIn("requires explicit user consent", (REPO / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertIn("assignment resume", state)
        self.assertIn("assignment recover", state)
        self.assertIn("run finish --outcome abandoned", state)
        self.assertIn("?mode=ro", source)
        self.assertIn("PRAGMA query_only = ON", source)
        self.assertIn("normalized_schema_objects", source)
        self.assertIn('return cache_root() / "run-state.sqlite3"', source)
        self.assertNotRegex(source + state, r"run-state-v[0-9]+\.sqlite3")
        self.assertIn("CREATE TABLE runtime_metadata", source)
        self.assertIn("target_schema_version", source)
        self.assertNotIn("PRAGMA user_version", source)
        self.assertNotIn("run-state.lock", source + state)
        self.assertNotIn("fcntl", source)

    def test_given_two_roots_when_specs_and_head_branches_differ_then_same_repo_is_allowed(self) -> None:
        """Given distinct Specs and worktree branches, when roots coordinate, then repository identity alone does not block."""
        spec = self.text("references/feature-spec-contract.md")
        recovery = self.text("references/claim-waits-and-recovery.md")
        state = self.text("references/run-state.md")
        self.assertIn("Different roots may therefore execute different Specs in the same repository", spec)
        self.assertIn("Repository identity alone never conflicts", recovery)
        self.assertIn("canonical repository plus\ncanonical Feature Spec identity", state)

    def test_given_orphaned_spec_when_recovery_runs_then_only_terminal_proof_releases(self) -> None:
        """Given an old owner, when recovery classifies it, then active or unknown evidence cannot take over."""
        recovery = self.text("references/claim-waits-and-recovery.md")
        normalized = self.normalized(recovery)
        self.assertIn("Active worker or present checkout", recovery)
        self.assertIn("released/absent checkout", normalized)
        self.assertIn("`abandoned-recovery-required`", recovery)
        self.assertIn("There is no TTL, lease, heartbeat takeover", recovery)

    def test_given_dependency_delivery_ready_release_when_downstream_is_selected_then_contract_proof_is_still_required(self) -> None:
        """Given upstream claim release, when downstream is considered, then exact contract proof is still required."""
        spec = self.text("references/feature-spec-contract.md")
        recovery = self.text("references/claim-waits-and-recovery.md")
        self.assertIn("stable dependency contract", spec)
        self.assertRegex(spec, r"Never\s+use claim release alone")
        self.assertIn("exact stable upstream delivery and integration proof", recovery)

    def test_given_local_delivery_when_contract_is_loaded_then_provider_gates_are_excluded(self) -> None:
        """Given local-branch delivery, when final gates run, then GitHub publication is not required."""
        spec = self.text("references/feature-spec-contract.md")
        worker = self.normalized(self.text("references/worker-execution.md"))
        gates = self.text("references/final-verification.md")
        self.assertIn("local Markdown plus\n`local-branch`", spec)
        self.assertIn("`local-branch` owns no push or provider", spec)
        self.assertIn("performs none of those provider operations", worker)
        self.assertIn("for `local-branch`: absence of push/PR/provider operations", gates)

    def test_given_multi_repo_boundaries_when_scheduled_then_existing_workers_collaborate(self) -> None:
        """Given cross-repo behavior, ordinary workers communicate and own exact-revision combined proof."""
        orchestration = self.normalized(self.text("references/codex-task-orchestration.md"))
        worker = self.normalized(self.text("references/worker-execution.md"))
        spec = self.text("references/feature-spec-contract.md")
        self.assertIn("There is no dedicated integration worker or reserved integration slot", orchestration)
        self.assertIn("Workers communicate directly with their named peers", orchestration)
        self.assertIn("a newly created peer's exact task/repository/branch/role/checkout identity", orchestration)
        self.assertIn("A new peer-identity follow-up carries identity only", orchestration)
        self.assertIn("Peer Collaboration And Combined Proof", worker)
        self.assertIn("Each combined boundary has an existing worker as its proof owner", worker)
        self.assertIn("ChatGPT-created worktree evidence", spec)
        self.assertIn("feature-spec-set validate", spec)
        self.assertIn("--feature-spec-set-input", self.text("references/root-bootstrap.md"))
        self.assertIn(
            "requires exact validator-projection equality",
            self.normalized(self.text("SKILL.md")),
        )
        self.assertIn("repository_relative_spec_path", worker)
        self.assertIn("qualifier as a directory", worker)
        self.assertIn("Every worker remains isolated to its own worktree", worker)
        self.assertIn("must not infer a peer HEAD", worker)
        final_verification = self.normalized(self.text("references/final-verification.md"))
        self.assertIn("must not access a peer worktree", final_verification)
        self.assertIn(
            "exactly one independently verified terminal branch or PR for every Feature Spec Set member",
            final_verification,
        )
        self.assertIn("one exact final vector", final_verification)
        self.assertNotIn("direct-worktree execution", worker)
        self.assertIn("`blocked-app-capability`", spec)

    def test_given_final_gate_mismatch_when_root_follows_up_then_message_is_evidence_only(self) -> None:
        """Given repairable final evidence mismatch, when root messages, then worker autonomy and App reconciliation remain intact."""
        orchestration = self.normalized(self.text("references/codex-task-orchestration.md"))
        verification = self.normalized(self.text("references/final-verification.md"))
        self.assertIn("authoritative final-verification mismatch", orchestration)
        self.assertIn("send only the missing or inconsistent evidence", orchestration)
        self.assertIn("no diagnosis, commands, implementation guidance", orchestration)
        self.assertIn("Diagnosis, repair, validation", orchestration)
        self.assertIn("Durable-contract drift", orchestration)
        self.assertIn("record `send-worker-message` in SQLite", orchestration)
        self.assertIn("independently read the exact task conversation", orchestration)
        self.assertIn("worker owns diagnosis, repair, validation", verification)
        self.assertIn("Final verification shows PR HEAD `def`", verification)

    def test_given_clis_when_structurally_inspected_then_state_and_verification_stay_separate(self) -> None:
        """Given the package, when CLIs are inspected, then one helper owns state and one stays read-only."""
        scripts = sorted(path.name for path in (ROOT / "scripts").iterdir() if path.is_file())
        source = self.text("scripts/run-state")
        verifier = self.text("scripts/verify-ready")
        self.assertEqual(scripts, ["run-state", "verify-ready"])
        self.assertTrue(os.access(ROOT / "scripts" / "run-state", os.X_OK))
        self.assertTrue(os.access(ROOT / "scripts" / "verify-ready", os.X_OK))
        self.assertIn('CLI_VERSION = "4.1.0"', source)
        self.assertIn('RUNTIME_CONTRACT_VERSION = "4.1.0"', source)
        self.assertIn("DATABASE_SCHEMA_VERSION = 3", source)
        self.assertIn("command_capabilities", source)
        self.assertIn("runtime_artifact_sha256", source)
        self.assertIn("BEGIN IMMEDIATE", source)
        self.assertIn("BEGIN EXCLUSIVE", source)
        self.assertIn("runtime_metadata", source)
        self.assertNotIn("run-state.lock", source)
        self.assertNotIn("fcntl", source)
        self.assertNotIn("PRAGMA user_version", source)
        self.assertIn("command_state_prepare", source)
        self.assertNotIn("migrate", source.lower())
        self.assertIn('CLI_VERSION = "1.1.0"', verifier)
        self.assertNotIn("sqlite3", verifier)
        self.assertNotIn("run-state.sqlite3", verifier)

    def test_given_delivery_ready_protocol_when_mode_is_selected_then_payload_is_the_single_authority(self) -> None:
        """The builder and consumer share readiness_mode without a divergent ready flag."""
        source = self.text("scripts/run-state")
        self.assertIn('"readiness_mode"', source)
        self.assertIn('"terminal", "peer-input"', source)
        self.assertIn('"--readiness-mode"', source)
        self.assertNotIn('ready.add_argument("--peer-input"', source)
        self.assertIn('"peer-input-ready"', source)

    def test_given_app_operation_replay_when_protocol_is_inspected_then_launch_identity_and_scope_are_explicit(self) -> None:
        """Each launch is observed exactly, while only failed single-use effects may replay beyond bootstrap."""
        source = self.text("scripts/run-state")
        self.assertIn('"launch_count"', source)
        self.assertIn('"--launch-count"', source)
        self.assertIn("stale-operation-launch", source)
        self.assertIn("SINGLE_USE_ACTIONS", source)
        self.assertIn("send-worker-message", source)

    def test_given_runtime_docs_when_references_are_routed_then_every_reference_is_reachable(self) -> None:
        """Given progressive disclosure, when routes are inspected, then every reference is linked by SKILL."""
        skill = self.text("SKILL.md")
        routed = set(re.findall(r"`references/([^`]+\.md)`", skill))
        actual = {path.name for path in (ROOT / "references").glob("*.md")}
        self.assertEqual(routed, actual)

    def test_given_root_policy_when_shared_docs_are_read_then_controller_ownership_is_generic(self) -> None:
        """Given shared docs, when policy is inspected, then root coordinates and workers own end-to-end delivery."""
        agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn("The root coordinates", agents)
        self.assertIn("run-state.sqlite3", readme)
        self.assertIn("the one startup interaction", readme)

    def test_given_runtime_contract_when_state_boundary_is_read_then_text_content_stays_authoritative_elsewhere(self) -> None:
        """Given generic coordinator docs, when state ownership is read, then raw delivery content is excluded structurally."""
        state = self.text("references/run-state.md")
        normalized = self.normalized(state)
        self.assertIn("Stored Data Allowlist", state)
        self.assertIn("typed Codex task-operation reconciliation facts", normalized)
        self.assertIn("must not store raw Spec or issue bodies", state)
        self.assertIn("linked `feature_id` membership", normalized)
        self.assertIn("normalized table", state)
        self.assertIn("Normal Git\nhead SHAs remain valid evidence", state)

    def test_given_runtime_docs_when_product_and_worktrees_are_described_then_language_is_public_and_concrete(self) -> None:
        """Given runtime documentation, when read by an operator, then product, task, and worktree actions are explicit."""
        runtime = self.runtime_text()
        orchestration = self.normalized(self.text("references/codex-task-orchestration.md"))
        self.assertIn("ChatGPT App", runtime)
        self.assertNotIn("Codex App", runtime)
        self.assertIsNone(re.search(r"(?<!ChatGPT )\bApp\b", runtime))
        self.assertIn("visible Codex worker task", orchestration)
        self.assertIn("ChatGPT App creates the worktree and assigns it to the task", orchestration)
        self.assertIn("root never runs `git worktree add`", orchestration)


if __name__ == "__main__":
    unittest.main()
