from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def run_app_preclaim_fixture(
    *, surface_available: bool, permission: str, bundle_ready: bool
) -> tuple[str, list[str], list[str]]:
    observations = ["surface"]
    mutations: list[str] = []
    if not surface_available:
        return "unsupported-runtime", observations, mutations
    observations.append("permission")
    if permission != "granted-by-authorized-user":
        return "permission-denied", observations, mutations
    observations.append("intake")
    if not bundle_ready:
        return "planning-required", observations, mutations
    mutations.extend(["atomic-claim", "ledger-projection", "portfolio-goal"])
    return "accepted", observations, mutations


def permission_contract_conflicts(text: str) -> list[str]:
    normalized = " ".join(text.split()).lower()
    conflicts: list[str] = []
    patterns = {
        "permission-before-surface": (
            r"resolve it before all other runtime work",
            r"first resolve visible-task permission",
            r"(?:ask|request|resolve).{0,80}(?:consent|permission).{0,80}before.{0,80}(?:verify|check|inspect).{0,80}(?:app|runtime).{0,80}(?:capabilit|surface)",
        ),
        "broad-task-creation-grant": (
            r"if the instruction grants task creation",
            r"generic delegation (?:grants?|authorizes?).{0,120}visible (?:app )?task",
            r"subagent authority (?:grants?|authorizes?).{0,120}visible (?:app )?task",
            r"delegation(?!.{0,100}does not grant).{0,80}(?:includes|covers|grants?|authorizes?).{0,80}visible.{0,40}tasks?",
            r"task creation permission.{0,80}(?:inherited|derived).{0,80}(?:worker|subagent|delegation) authority",
        ),
    }
    for label, candidates in patterns.items():
        if any(re.search(candidate, normalized) for candidate in candidates):
            conflicts.append(label)
    return conflicts


class AppOrchestratorContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text()

    def runtime_paths(self) -> list[Path]:
        files = [ROOT / "SKILL.md", ROOT / "agents/openai.yaml"]
        files.extend(sorted((ROOT / "references").rglob("*.md")))
        return files

    def runtime_text(self) -> str:
        return "\n".join(path.read_text() for path in self.runtime_paths())

    def test_required_package_files_exist(self) -> None:
        required = {
            "SKILL.md",
            "agents/openai.yaml",
            "scripts/orchestrator-claim",
            "references/options.md",
            "references/core/options.md",
            "references/core/merge-authorization.md",
            "references/ledger.md",
            "references/ledger-template.md",
            "references/worker.md",
            "references/gates.md",
            "references/spec-backed-delivery.md",
            "references/stacked-feature-specs.md",
            "references/codex-review-closeout.md",
            "references/recovery-validation.md",
            "references/multi-repo-workspace.md",
        }
        self.assertTrue(all((ROOT / path).is_file() for path in required))

    def test_app_surface_is_visible_task_only(self) -> None:
        text = self.runtime_text()
        for required in (
            "visible_app_task_permission=granted-by-authorized-user",
            "exactly one visible task per Feature Spec",
            "App-managed worktrees",
            "root_implementation_fallback",
            "forbidden",
            "assignment-scoped Goal",
            "feature_spec_task_cap",
            "`3`",
        ):
            self.assertIn(required, text)
        self.assertIn("abort as blocked", text)
        self.assertIn("## Mandatory Permission Gate", text)
        self.assertIn("ask the user once", text)
        self.assertIn("abort the run without implementation or runtime", text)
        self.assertIn("never invokes, routes to, or recommends", text)
        self.assertIn("explicitly grants creation of visible Codex App tasks", text)
        self.assertIn("Generic delegation, subagent, background-worker", text)
        self.assertIn("does not grant visible App task creation", text)

    def test_runtime_surface_gate_precedes_permission_and_all_work(self) -> None:
        skill = self.read("SKILL.md")
        metadata = self.read("agents/openai.yaml")
        options = self.read("references/options.md")
        surface = skill.index("## Mandatory Runtime Surface Gate")
        permission = skill.index("## Mandatory Permission Gate")
        controller = skill.index("## Controller Loop")

        self.assertLess(surface, permission)
        self.assertLess(permission, controller)
        self.assertIn("This is the first runtime step", skill[surface:permission])
        self.assertIn("visible Codex App task\n  creation", skill[surface:permission])
        self.assertIn("App-managed worktree binding", skill[surface:permission])
        self.assertIn("generic/background subagent tools", skill[surface:permission])
        self.assertIn("Do not ask for visible-task\n  permission", skill[surface:permission])
        self.assertIn("0. **SURFACE**", skill[controller:])
        self.assertLess(skill.index("0. **SURFACE**"), skill.index("1. **PERMISSION**"))
        self.assertIn("First verify that the current runtime exposes", metadata)
        self.assertIn("abort before asking permission", metadata)
        self.assertIn("Resolve it only after\nthe mandatory runtime surface gate", options)
        self.assertIn("App-managed worktree binding", options)
        self.assertNotIn("Resolve it before all\nother runtime work", options)

        recovery = self.read("references/recovery-validation.md")
        recovery_surface = recovery.index("## Mandatory App Runtime Surface Revalidation")
        recovery_validation = recovery.index("## Shared Validation")
        self.assertLess(recovery_surface, recovery_validation)
        recovery_gate = recovery[recovery_surface:recovery_validation]
        self.assertIn("before reading the Recovery Packet", recovery_gate)
        self.assertIn("visible Codex App task creation", recovery_gate)
        self.assertIn("App-managed\nworktree binding", recovery_gate)
        self.assertIn("without asking permission", recovery_gate)
        self.assertIn("Only after this gate passes", recovery_gate)

        for path in self.runtime_paths():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual(permission_contract_conflicts(path.read_text()), [])

        contradictory_fixtures = {
            "permission-first": "First resolve visible-task permission from the invocation.",
            "legacy-order": "Resolve it before all other runtime work.",
            "generic-delegation": (
                "Generic delegation grants visible App task creation for this run."
            ),
            "generic-subagent": (
                "Subagent authority authorizes visible task permission for this run."
            ),
            "consent-before-capabilities": (
                "Ask for consent before verifying App capabilities."
            ),
            "delegation-includes-visible-tasks": (
                "Delegation includes visible App tasks for this run."
            ),
            "worker-authority-inheritance": (
                "Task creation permission is inherited from worker authority."
            ),
        }
        for label, fixture in contradictory_fixtures.items():
            with self.subTest(fixture=label):
                self.assertTrue(permission_contract_conflicts(fixture))

    def test_app_surface_has_no_cli_or_manual_checkout_machinery(self) -> None:
        text = self.runtime_text().lower()
        forbidden = (
            "tmux",
            "codex exec",
            "git worktree add",
            "git worktree remove",
            "serial-caller-checkout",
            "unmanaged_git_worktree_fallback_permission",
            "implementation_checkout_strategy",
            "cli-only sessions",
            "current-orchestrator-session",
            "background-codex-subagent",
        )
        for token in forbidden:
            self.assertNotIn(token, text, token)
        self.assertNotIn("recommend `$codex-cli-orchestrator`", text)
        self.assertNotIn("route to `$codex-cli-orchestrator`", text)

    def test_app_has_one_fixed_successful_implementation_conclusion(self) -> None:
        skill = self.read("SKILL.md")
        options = self.read("references/options.md")
        worker = self.read("references/worker.md")
        metadata = self.read("agents/openai.yaml")
        fixed = "pull-request-ready-for-merge-but-not-merged"
        for text in (skill, options, worker, metadata):
            self.assertIn(fixed, text)
        self.assertIn("The only successful App implementation conclusion", skill)
        self.assertIn("## Fixed App Delivery", options)
        self.assertIn("## Fixed Implementation Conclusion", skill)
        self.assertIn("PR-PREFLIGHT", skill)
        self.assertIn("never downgrade", skill)
        self.assertNotIn("target-complete", worker)
        self.assertLess(skill.index("2. **INTAKE**"), skill.index("3. **CLAIM**"))
        self.assertLess(skill.index("3. **CLAIM**"), skill.index("4. **REGISTER**"))
        claim_step = skill.split("3. **CLAIM**", 1)[1].split("4. **REGISTER**", 1)[0]
        normalized_claim_step = " ".join(claim_step.split())
        self.assertLess(
            normalized_claim_step.index("acquire the common active-root claim atomically"),
            normalized_claim_step.index("create the portfolio Goal or exact fallback"),
        )
        self.assertLess(skill.index("4. **REGISTER**"), skill.index("5. **PR-PREFLIGHT**"))
        self.assertLess(skill.index("5. **PR-PREFLIGHT**"), skill.index("6. **DISPATCH**"))

    def test_app_accepts_only_execution_ready_bundles_and_never_plans(self) -> None:
        skill = self.read("SKILL.md")
        delivery = self.read("references/spec-backed-delivery.md")
        metadata = self.read("agents/openai.yaml")
        runtime = self.runtime_text()
        normalized_skill = " ".join(skill.split())
        normalized_delivery = " ".join(delivery.split())

        self.assertIn("## Execution-Ready Intake", skill)
        self.assertIn("one read-only intake", normalized_skill)
        self.assertIn("planning-required", skill)
        self.assertIn("unsupported-app-delivery-target", skill)
        self.assertIn("pr-preflight-failed", skill)
        self.assertIn("Do not continue to CLAIM", normalized_skill)
        self.assertIn("no runtime artifact or mutation was created", normalized_skill)
        self.assertIn("Do not fabricate ledger-derived status", normalized_skill)
        self.assertIn("durable Feature Spec", delivery)
        self.assertIn("complete generated implementation issue graph", normalized_delivery)
        self.assertIn(
            "never creates, repairs, regenerates, or publishes planning artifacts",
            normalized_delivery,
        )
        self.assertIn(
            "Merge authority is not an execution-ready handoff field",
            normalized_delivery,
        )
        self.assertIn(
            "Keep `pull_request_merge_permission` and `pull_request_merge_confirmation` unresolved during CLAIM",
            normalized_skill,
        )
        self.assertIn("post-conclusion root authorization step", normalized_skill)
        self.assertIn("Do not load `references/core/merge-authorization.md`", skill)
        self.assertIn(
            "The root validates and preserves that tuple; it never selects, rewrites, or widens it",
            normalized_delivery,
        )
        self.assertNotIn("The root owns target selection", delivery)
        self.assertIn("planning-required", metadata)
        self.assertNotIn("$plan-feature", runtime)
        self.assertNotIn("## Source Routing", skill)
        self.assertNotIn("Rough intent without a Feature Spec", skill)
        self.assertNotIn("Ad-hoc implementation source", skill)
        self.assertNotIn("Missing implementation detail may be regenerated", runtime)
        self.assertNotIn("safe-default-for-ad-hoc-work", runtime)
        self.assertNotIn("temporary_source_execution_permission", runtime)

        readme_dependency = next(
            line
            for line in (REPO / "README.md").read_text().splitlines()
            if line.startswith("- `codex-orchestrator` requires")
        )
        agents_dependency = next(
            line
            for line in (REPO / "AGENTS.md").read_text().splitlines()
            if line.startswith("- Treat `codex-orchestrator` as Codex-dependent")
        )
        self.assertNotIn("$plan-feature", readme_dependency)
        self.assertNotIn("$plan-feature", agents_dependency)

    def test_preclaim_fixture_has_zero_mutations_on_every_early_abort(self) -> None:
        cases = (
            (False, "not-requested", False, "unsupported-runtime", ["surface"]),
            (
                True,
                "denied-by-authorized-user",
                True,
                "permission-denied",
                ["surface", "permission"],
            ),
            (
                True,
                "granted-by-authorized-user",
                False,
                "planning-required",
                ["surface", "permission", "intake"],
            ),
        )
        for surface, permission, ready, expected, observations in cases:
            with self.subTest(expected=expected):
                outcome, observed, mutations = run_app_preclaim_fixture(
                    surface_available=surface,
                    permission=permission,
                    bundle_ready=ready,
                )
                self.assertEqual(outcome, expected)
                self.assertEqual(observed, observations)
                self.assertEqual(mutations, [])

        outcome, observations, mutations = run_app_preclaim_fixture(
            surface_available=True,
            permission="granted-by-authorized-user",
            bundle_ready=True,
        )
        self.assertEqual(outcome, "accepted")
        self.assertEqual(observations, ["surface", "permission", "intake"])
        self.assertEqual(
            mutations,
            ["atomic-claim", "ledger-projection", "portfolio-goal"],
        )

    def test_shared_registry_is_adapter_neutral(self) -> None:
        ledger = self.read("references/ledger.md")
        template = self.read("references/ledger-template.md")
        for text in (ledger, template):
            self.assertIn("Feature Spec Execution Registry", text)
            self.assertIn("execution_adapter", text)
            self.assertIn("adapter_evidence_ref", text)
            self.assertIn("codex-app-task", text)
            self.assertIn("codex-cli-session", text)
        self.assertNotIn("Feature Spec Task Registry", ledger)

    def test_multi_repo_requires_managed_child_checkouts(self) -> None:
        text = " ".join(self.read("references/multi-repo-workspace.md").split())
        self.assertIn("one visible App task per Feature Spec", text)
        self.assertIn("isolated checkout for every required child repository", text)
        self.assertIn("Do not invoke another orchestrator or use owner checkouts", text)

    def test_options_use_canonical_syntax_and_retire_mixed_surface_fields(self) -> None:
        text = self.read("references/options.md")
        shared = self.read("references/core/options.md")
        merge = self.read("references/core/merge-authorization.md")
        fields = re.findall(r"\| `([a-z][a-z0-9_]*)` \|", text)
        self.assertTrue(fields)
        self.assertTrue(all(re.fullmatch(r"[a-z][a-z0-9_]*", field) for field in fields))
        self.assertIn("Retired mixed-surface fields", text)
        self.assertIn("shared non-merge authority", text)
        self.assertIn("Merge\nfields live only in `core/merge-authorization.md`", text)
        self.assertIn("`granted-for-selected-target`", shared)
        self.assertIn("`pull-request-closing-keyword-only`", shared)
        self.assertIn("`not-needed-for-selected-delivery-target`", shared)
        self.assertIn("`delivery_decision_origin`", shared)
        self.assertIn("`pull_request_count_strategy`", shared)
        self.assertIn("`issue_completion_method`", shared)
        self.assertNotIn("pull_request_merge_permission", shared)
        self.assertNotIn("pull_request_merge_confirmation", shared)
        self.assertIn("These fields have no pre-conclusion defaults", merge)
        self.assertIn("`pull_request_merge_permission`", merge)
        self.assertIn("`pull_request_merge_confirmation`", merge)

    def test_metadata_is_manual_app_entrypoint(self) -> None:
        metadata = self.read("agents/openai.yaml")
        self.assertIn('display_name: "Codex App Orchestrator"', metadata)
        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertIn("Use only App-managed worktrees", metadata)

    def test_review_freshness_uses_full_revision_tuple(self) -> None:
        closeout = self.read("references/codex-review-closeout.md")
        gates = self.read("references/gates.md")
        for token in ("head SHA", "base ref", "merge-base SHA"):
            self.assertIn(token, closeout)
        self.assertIn("entire tuple matches", closeout)
        self.assertIn("merge-base changes invalidate", gates)
        for token in (
            "Codex Review Wait Registry",
            "15-minute standard",
            "30-minute extended",
            "exactly one row keyed by",
            "idempotent per full revision tuple",
            "wait_started_at",
            "wait_deadline",
            "monitoring-required",
        ):
            self.assertIn(token, closeout)

    def test_cli_companion_and_shared_dependency_exist(self) -> None:
        cli = REPO / "skills/codex-cli-orchestrator"
        self.assertTrue((cli / "SKILL.md").is_file())
        self.assertTrue((cli / "scripts/codex-session").is_file())
        self.assertIn("requires the sibling `codex-orchestrator`", (cli / "SKILL.md").read_text())


if __name__ == "__main__":
    unittest.main()
