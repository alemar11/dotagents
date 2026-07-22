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
        spec = self.text("references/spec-backed-delivery.md")
        worker = self.text("references/worker.md")
        self.assertIn("implementation approach or internal technical design", spec)
        self.assertIn("additional or equivalent tests", spec)
        self.assertIn("accept compatible operational changes and continue autonomously", worker)

    def test_given_stable_drift_when_worker_rereads_then_it_blocks_without_asking(self) -> None:
        """Given outcome or acceptance drift, when detected, then worker declaratively blocks."""
        spec = self.text("references/spec-backed-delivery.md")
        self.assertIn("acceptance text", spec)
        self.assertIn("material validation budget/terminal result changes", spec)
        self.assertIn("blocked-durable-contract", spec)
        self.assertIn("without asking", spec)

    def test_given_github_or_local_tracker_when_checkbox_changes_then_readback_and_invalidation_are_required(self) -> None:
        """Given GitHub or local Markdown, when proof changes, then checkboxes update and invalid proof is unchecked."""
        tracker = self.text("references/tracker-proof.md")
        self.assertIn("GitHub or local", tracker)
        self.assertIn("only after that current-head proof exists", tracker)
        self.assertIn("uncheck it immediately", tracker)
        self.assertIn("Read the authoritative issue again", tracker)

    def test_given_worker_handoff_when_root_closes_then_root_is_read_only(self) -> None:
        """Given PR-ready worker evidence, when root verifies, then it never judges or edits criteria."""
        gates = self.text("references/gates.md")
        tracker = self.text("references/tracker-proof.md")
        self.assertIn("performs read-only verification", gates)
        self.assertIn("does not edit code", gates)
        self.assertIn("must not edit, check, uncheck, reinterpret, or adjudicate", tracker)

    def test_given_bootstrap_recovery_when_state_is_ambiguous_then_app_receipts_replace_text_hashes(self) -> None:
        """Given ambiguous delivery, when recovering, then receipt/readback owns identity without text hashes."""
        app = self.text("references/app-orchestration.md")
        recovery = self.text("references/recovery-validation.md")
        self.assertIn("authoritative App receipt", app)
        self.assertRegex(app, r"Fail closed if the exact\s+baseline cannot be\s+recovered")
        self.assertIn("No state row, packet, body, result, or message hash", recovery)

    def test_given_same_repo_assignments_when_paths_overlap_then_root_serializes_them(self) -> None:
        """Given overlap in one repository, when scheduling, then root serializes while disjoint work may reach three."""
        skill = self.text("SKILL.md")
        app = self.text("references/app-orchestration.md")
        self.assertIn("Schedule up to three path-disjoint", skill)
        self.assertIn("overlapping paths or issue dependencies serialize", self.text("references/spec-backed-delivery.md"))
        self.assertIn("At most three workers may be live", app)

    def test_given_root_assignments_when_title_is_set_then_it_uses_exact_coarse_progress(self) -> None:
        """Given one or many Specs, when root title changes, then exact ready/total UI evidence is used."""
        app = self.text("references/app-orchestration.md")
        self.assertIn("`👨🏻‍💻 Feature Orchestrator`", app)
        self.assertIn("`👨🏻‍💻 Multi-Feature Orchestrator (R/N)`", app)
        self.assertIn("`N` is the immutable total", app)
        self.assertIn("`R` is the number currently recorded `ready`", app)
        self.assertIn("Start at\n   `0/N`", app)
        self.assertIn("update the title only when `R` changes", app)
        self.assertIn("UI evidence only, never task\n   identity or durable run state", app)

    def test_given_two_roots_when_specs_and_head_branches_differ_then_same_repo_is_allowed(self) -> None:
        """Given distinct Specs and worktree branches, when roots coordinate, then repository identity alone does not block."""
        spec = self.text("references/spec-backed-delivery.md")
        recovery = self.text("references/recovery-validation.md")
        state = self.text("references/run-state.md")
        self.assertIn("Different roots may therefore execute different Specs in the same repository", spec)
        self.assertIn("Repository identity alone never conflicts", recovery)
        self.assertIn("canonical repository plus\ncanonical Feature Spec identity", state)

    def test_given_orphaned_spec_when_recovery_runs_then_only_terminal_proof_releases(self) -> None:
        """Given an old owner, when recovery classifies it, then active or unknown evidence cannot take over."""
        recovery = self.text("references/recovery-validation.md")
        self.assertIn("`active`, or a terminal worker whose checkout remains present", recovery)
        self.assertIn("a released or absent checkout", recovery)
        self.assertIn("`abandoned-recovery-required`", recovery)
        self.assertIn("There is no TTL, heartbeat lease, implicit takeover", recovery)

    def test_given_dependency_pr_ready_release_when_downstream_is_selected_then_merge_proof_is_still_required(self) -> None:
        """Given upstream claim release, when downstream is considered, then it still waits for merge proof."""
        spec = self.text("references/spec-backed-delivery.md")
        recovery = self.text("references/recovery-validation.md")
        self.assertIn("must already be merged and integration-proven", spec)
        self.assertRegex(spec, r"Never use claim release as\s+merge proof")
        self.assertIn("dependent Specs still wait", recovery)

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
        self.assertIn("typed App-operation reconciliation facts", state)
        self.assertIn("must not store raw Spec or issue bodies", state)
        self.assertIn("Normal Git\nhead SHAs remain valid evidence", state)


if __name__ == "__main__":
    unittest.main()
