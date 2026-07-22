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

    def test_given_startup_when_permission_is_resolved_then_it_is_the_only_user_question(self) -> None:
        """Given startup, when permission is granted, then no later authority question is allowed."""
        options = self.text("references/options.md")
        skill = self.text("SKILL.md")
        self.assertIn("Ask once", options)
        self.assertIn("do not ask another user question", options)
        self.assertIn("Never ask another authority, recovery", skill)
        self.assertEqual(re.findall(r"`visible_app_task_permission`", options).count("`visible_app_task_permission`"), 1)

    def test_given_compatible_operational_edits_when_worker_rereads_then_it_continues(self) -> None:
        """Given compatible design or test edits, when reread occurs, then worker accepts them autonomously."""
        spec = self.text("references/feature-spec-contract.md")
        worker = self.text("references/worker-execution.md")
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

    def test_given_worker_handoff_when_root_closes_then_root_is_read_only(self) -> None:
        """Given PR-ready worker evidence, when root verifies, then it never judges or edits criteria."""
        gates = self.text("references/final-verification.md")
        tracker = self.text("references/tracker-checklists.md")
        self.assertIn("performs read-only verification", gates)
        self.assertIn("does not edit code", gates)
        self.assertIn("must not edit, check, uncheck, reinterpret, or adjudicate", tracker)

    def test_given_bootstrap_recovery_when_state_is_ambiguous_then_actual_task_state_prevents_duplicates(self) -> None:
        """Given ambiguous delivery, when recovering, then root inspects the task before repeating and stores no body hash."""
        orchestration = self.text("references/chatgpt-task-orchestration.md")
        recovery = self.text("references/claim-waits-and-recovery.md")
        normalized = self.normalized(orchestration)
        self.assertIn("record the intended operation in SQLite before changing", normalized)
        self.assertIn("after an interruption, inspect the actual object first", normalized)
        self.assertIn("repeat the change only when authoritative evidence proves it had no effect", normalized)
        self.assertIn("never infer delivery from a stored body or hash", recovery)

    def test_given_same_repo_assignments_when_paths_overlap_then_root_serializes_them(self) -> None:
        """Given overlap in one repository, when scheduling, then root serializes while disjoint work may reach three."""
        skill = self.text("SKILL.md")
        orchestration = self.text("references/chatgpt-task-orchestration.md")
        self.assertIn("Schedule up to three path-disjoint", skill)
        self.assertIn("overlapping paths or issue dependencies serialize", self.text("references/feature-spec-contract.md"))
        self.assertIn("At most three workers may be live", orchestration)

    def test_given_root_assignments_when_title_is_set_then_it_uses_exact_coarse_progress(self) -> None:
        """Given one or many Specs, when root title changes, then exact ready/total UI evidence is used."""
        orchestration = self.normalized(self.text("references/chatgpt-task-orchestration.md"))
        self.assertIn("`👨🏻‍💻 Feature Orchestrator`", orchestration)
        self.assertIn("`👨🏻‍💻 Multi-Feature Orchestrator (R/N)`", orchestration)
        self.assertIn("`N` is the immutable total", orchestration)
        self.assertIn("`R` counts assignments", orchestration)
        self.assertIn("Start at `0/N`", orchestration)
        self.assertIn("The title is UI evidence, never identity or durable state", orchestration)

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
        worker = self.text("references/worker-execution.md")
        gates = self.text("references/final-verification.md")
        self.assertIn("local Markdown plus\n`local-branch`", spec)
        self.assertIn("`local-branch` owns no push or provider", spec)
        self.assertIn("performs none of those\nprovider operations", worker)
        self.assertIn("for `local-branch`: absence of push/PR/provider operations", gates)

    def test_given_multi_repo_integration_when_scheduled_then_it_is_a_visible_worker_with_exact_inputs(self) -> None:
        """Given a dedicated Integration Spec, when prerequisites stabilize, then another visible App task owns proof."""
        orchestration = self.normalized(self.text("references/chatgpt-task-orchestration.md"))
        worker = self.text("references/worker-execution.md")
        spec = self.text("references/feature-spec-contract.md")
        self.assertIn("dedicated integration Spec counts as another visible Codex worker task", orchestration)
        self.assertIn("exact vector", orchestration)
        self.assertIn("Dedicated Integration Worker", worker)
        self.assertIn("ChatGPT-created worktree evidence", spec)
        self.assertIn("blocks the whole local cross-repository bundle", spec)

    def test_given_final_gate_mismatch_when_root_follows_up_then_message_is_evidence_only(self) -> None:
        """Given repairable final evidence mismatch, when root messages, then worker autonomy and App reconciliation remain intact."""
        orchestration = self.normalized(self.text("references/chatgpt-task-orchestration.md"))
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

    def test_given_cli_when_structurally_inspected_then_it_is_one_executable_schema_one_artifact(self) -> None:
        """Given the package, when CLI structure is inspected, then one executable owns fresh schema 1."""
        scripts = sorted(path.name for path in (ROOT / "scripts").iterdir() if path.is_file())
        source = self.text("scripts/run-state")
        self.assertEqual(scripts, ["run-state"])
        self.assertTrue(os.access(ROOT / "scripts" / "run-state", os.X_OK))
        self.assertIn('CLI_VERSION = "1.0.0"', source)
        self.assertIn("STATE_SCHEMA_VERSION = 1", source)
        self.assertIn("BEGIN IMMEDIATE", source)
        self.assertNotIn(".lock", source)
        self.assertNotIn("migrate", source.lower())

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
        self.assertIn("One startup permission", readme)

    def test_given_runtime_contract_when_state_boundary_is_read_then_text_content_stays_authoritative_elsewhere(self) -> None:
        """Given generic coordinator docs, when state ownership is read, then raw delivery content is excluded structurally."""
        state = self.text("references/run-state.md")
        self.assertIn("Stored Data Allowlist", state)
        self.assertIn("typed ChatGPT task-operation reconciliation facts", state)
        self.assertIn("must not store raw Spec or issue bodies", state)
        self.assertIn("Normal Git\nhead SHAs remain valid evidence", state)

    def test_given_runtime_docs_when_product_and_worktrees_are_described_then_language_is_public_and_concrete(self) -> None:
        """Given runtime documentation, when read by an operator, then product, task, and worktree actions are explicit."""
        runtime = self.runtime_text()
        orchestration = self.normalized(self.text("references/chatgpt-task-orchestration.md"))
        self.assertIn("ChatGPT desktop app", runtime)
        self.assertNotIn("Codex App", runtime)
        self.assertIsNone(re.search(r"(?<![a-z-])\bApp\b", runtime))
        self.assertIn("visible Codex worker task", orchestration)
        self.assertIn("ChatGPT desktop app creates the worktree and assigns it to the task", orchestration)
        self.assertIn("root never runs `git worktree add`", orchestration)


if __name__ == "__main__":
    unittest.main()
