import unittest
from pathlib import Path


REFERENCE = Path(__file__).resolve().parents[1] / "references/review-delivery.md"
ORCHESTRATION = Path(__file__).resolve().parents[1] / "references/orchestration.md"
SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
PREFLIGHT = Path(__file__).resolve().parents[3] / "references/codex-dependency-preflight.md"
TASK_PROFILE = Path(__file__).resolve().parents[1] / "references/task-profile.md"
RUN_STATE = Path(__file__).resolve().parents[1] / "references/run-state.md"


class ReviewDeliveryContractTests(unittest.TestCase):
    def test_one_feature_worker_owns_each_feature_and_its_single_pr(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        orchestration = ORCHESTRATION.read_text(encoding="utf-8")
        profile = TASK_PROFILE.read_text(encoding="utf-8")
        run_state = RUN_STATE.read_text(encoding="utf-8")

        self.assertIn("one-feature-worker-per-feature", profile)
        self.assertIn('title_template: "🛠️ Feature Worker · <Feature outcome>"', profile)
        self.assertIn("For every Feature member, bootstrap exactly one Feature Worker", orchestration)
        self.assertIn("executes its derived units in deterministic prerequisite order", " ".join(orchestration.split()))
        self.assertIn("The hosted Feature Plan Set and every local Macro Task projection are required input", " ".join(skill.split()))
        self.assertIn("one verified child Task issue per stable", skill)
        self.assertIn("Exactly one assignment may exist per claimed Feature", run_state)
        self.assertIn(
            "must not receive an empty commit, empty PR, cosmetic change, or artificial proof",
            " ".join(skill.split()),
        )

    def test_feature_worker_support_delegation_is_optional_and_parent_owned(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        orchestration = ORCHESTRATION.read_text(encoding="utf-8")
        profile = TASK_PROFILE.read_text(encoding="utf-8")
        normalized_skill = " ".join(skill.split())
        normalized_orchestration = " ".join(orchestration.split())

        self.assertIn("role: feature-worker-support", profile)
        self.assertIn("topology: bounded-feature-worker-support", profile)
        self.assertIn(
            "topology: orchestrator-with-feature-workers-and-optional-support",
            profile,
        )
        for responsibility in (
            "code-analyst",
            "execution-assistant",
            "validation-assistant",
            "critic-reviewer",
        ):
            self.assertIn(responsibility, normalized_skill)
            self.assertIn(responsibility, normalized_orchestration)

        for mode in ("delegated-support", "serial-fallback", "unavailable", "unknown"):
            self.assertIn(mode, profile)

        self.assertIn("Delegation is not a required topology gate", normalized_skill)
        self.assertIn("never access the SQLite ledger", normalized_skill)
        self.assertIn("owns the final candidate HEAD", normalized_skill)
        self.assertIn(
            "never creates another Feature Worker or planner task",
            normalized_orchestration,
        )
        self.assertIn("outside the implementation ledger", normalized_orchestration)

    def test_pr_delivery_derives_the_closed_set_from_the_macro_registry(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        normalized = " ".join(reference.split())

        for required in (
            "derive `closing_issue_refs` deterministically from that Feature's verified local hosted registry",
            "[this parent Feature issue] + [every Macro Task child issue owned by this Feature]",
            "There is no per-Task opt-out",
            "no Worker-supplied closure list",
            "The PR declares closure intent",
            "GitHub closes this Feature and its local Macro Tasks only when the PR is merged",
            "`closingIssuesReferences` set",
        ):
            self.assertIn(required, normalized)

        self.assertIn("Require the read-back set to equal `closing_issue_refs` exactly", normalized)
        self.assertIn("Macro Task coverage evidence", normalized)

    def test_stacked_children_link_separately(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        orchestration = ORCHESTRATION.read_text(encoding="utf-8")
        normalized = " ".join(reference.split())
        orchestration_normalized = " ".join(orchestration.split())

        self.assertIn("separate G-owned pairwise stack-link workflow", normalized)
        self.assertIn("Before bootstrapping a stacked child", orchestration_normalized)
        self.assertIn("`candidate-published` parent branch and exact HEAD", orchestration_normalized)
        self.assertIn("The parent may remain `delivery-pending`", orchestration_normalized)
        self.assertNotIn("Task-only", normalized)
        self.assertIn("this parent Feature and every associated local Macro Task", normalized)

    def test_feature_plan_set_scheduling_and_per_feature_closure_are_explicit(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        orchestration = ORCHESTRATION.read_text(encoding="utf-8")
        reference = REFERENCE.read_text(encoding="utf-8")

        normalized_skill = " ".join(skill.split())
        normalized_orchestration = " ".join(orchestration.split())
        normalized_reference = " ".join(reference.split())

        for required in (
            "Feature Plan Sets",
            "Feature-level `blocked_by`",
            "same-parent-only",
            "exactly one PR output per implementation-eligible selected Feature",
            "same-repository edge is mandatory stack intent",
            "cross-repository edge as scheduling-only",
        ):
            self.assertIn(required, normalized_skill)

        for required in (
            "Feature Plan Sets",
            "hard outcome dependencies",
            "every same-repository edge is mandatory stack intent",
            "every cross-repository edge is scheduling-only",
            "Sibling Features and their Tasks are never included",
        ):
            self.assertIn(required, normalized_orchestration + normalized_reference)

        self.assertIn(
            "Require every local registry entry to resolve to one real",
            normalized_reference,
        )
        self.assertIn("cross-parent", normalized_reference)

    def test_delivery_status_is_exact_head_and_has_two_accepted_dispositions(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        orchestration = ORCHESTRATION.read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")

        for document in (reference, orchestration, skill, preflight):
            self.assertIn("$g:github-delivery-status", document)

        for disposition in ("`ready`", "`ready-with-manual-action`"):
            self.assertIn(disposition, reference)
            self.assertIn(disposition, skill)

        for rejected in ("`pending`", "`blocked`", "`conflicting`", "`unknown`"):
            self.assertIn(rejected, reference)

        self.assertIn("merge_boundary=none", reference)
        self.assertIn("merge_boundary=manual", reference)
        self.assertIn("exact published full HEAD", " ".join(reference.split()))

    def test_delivery_lifecycle_stops_before_merge(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")
        normalized = " ".join(reference.split())
        lifecycle = (
            "active @ worker-bootstrap -> active @ native-review -> "
            "delivery-pending @ candidate-published -> delivery-ready @ final-verify"
        )

        self.assertIn(lifecycle, normalized)
        self.assertIn(
            "Implement terminates with a PR published and verified on its exact HEAD",
            normalized,
        )
        self.assertIn("The PR may remain open", normalized)
        self.assertIn("They become effective only when GitHub merges the PR", normalized)
        self.assertIn("current PR HEAD, PR body and closing references", normalized)
        self.assertIn(
            "The delivery lifecycle ends at a published PR verified on its exact HEAD",
            " ".join(skill.split()),
        )

    def test_candidate_publication_hands_monitoring_to_the_orchestrator(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        orchestration = ORCHESTRATION.read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")
        profile = TASK_PROFILE.read_text(encoding="utf-8")
        run_state = RUN_STATE.read_text(encoding="utf-8")

        normalized_reference = " ".join(reference.split())
        normalized_orchestration = " ".join(orchestration.split())
        normalized_skill = " ".join(skill.split())
        normalized_profile = " ".join(profile.split())
        normalized_run_state = " ".join(run_state.split())

        self.assertIn("The orchestrator is the sole delivery monitor", normalized_skill)
        self.assertIn("becomes inactive but resumable", normalized_skill)
        self.assertIn("It does not monitor its own PR", normalized_profile)
        self.assertIn("actionable fix, evidence repair, or rebase", normalized_profile)
        self.assertIn("status=delivery-pending", normalized_reference)
        self.assertIn("checkpoint=candidate-published", normalized_reference)
        self.assertIn("releases the transient active path claim", normalized_reference)
        self.assertIn("Before any repair or rebase resumption, reacquire", normalized_run_state)
        self.assertIn("parent delivery readiness is not a worker-bootstrap gate", normalized_orchestration)
        self.assertIn("Do not wait for hosted review, CI, or provider readiness", normalized_reference)
        self.assertIn("candidate-published --> schedule", skill)
        self.assertIn("delivery-monitor --> implement-validate", skill)
        self.assertNotIn("ready-monitor", skill)

    def test_provider_automation_is_informational_and_implement_never_merges(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")

        normalized = " ".join(reference.split())
        for phrase in (
            "They neither block delivery readiness nor grant authority",
            "must not enable, disable, enqueue, dequeue, bypass, or merge",
        ):
            self.assertIn(phrase, normalized)

        self.assertIn("are not blockers by themselves", skill)
        self.assertIn(
            "never merges, bypasses protections, enables or disables auto-merge, or enqueues or dequeues a PR",
            " ".join(skill.split()),
        )


if __name__ == "__main__":
    unittest.main()
