import unittest
from pathlib import Path


REFERENCE = Path(__file__).resolve().parents[1] / "references/review-delivery.md"
ORCHESTRATION = Path(__file__).resolve().parents[1] / "references/orchestration.md"
SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
PREFLIGHT = Path(__file__).resolve().parents[3] / "references/codex-dependency-preflight.md"
TASK_PROFILE = Path(__file__).resolve().parents[1] / "references/task-profile.md"
RUN_STATE = Path(__file__).resolve().parents[1] / "references/run-state.md"


class ReviewDeliveryContractTests(unittest.TestCase):
    def test_one_feature_worker_owns_each_plan_member_and_its_single_pr(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        orchestration = ORCHESTRATION.read_text(encoding="utf-8")
        profile = TASK_PROFILE.read_text(encoding="utf-8")
        run_state = RUN_STATE.read_text(encoding="utf-8")

        self.assertIn("one-feature-worker-per-plan-member", profile)
        self.assertIn('title_template: "🛠️ Feature Worker · <Feature outcome>"', profile)
        self.assertIn("For every plan member, bootstrap exactly one Feature Worker", orchestration)
        self.assertIn("executes its derived units in deterministic prerequisite order", " ".join(orchestration.split()))
        self.assertIn("An authoritative hosted Task issue set, Task dependency graph, T-AC identifiers", skill)
        self.assertIn("Exactly one assignment may exist per claimed Feature Plan member", run_state)
        self.assertIn(
            "must not receive an empty commit, empty PR, cosmetic change, or artificial proof",
            " ".join(skill.split()),
        )

    def test_pr_delivery_preserves_plan_and_allows_only_explicit_closures(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")

        for required in (
            "default closing_issue_refs set for a Feature Plan implementation is empty",
            "published Feature Plan remains open",
            "closingIssuesReferences set",
            "never invent hosted Task refs",
            "An empty set is a valid default",
        ):
            self.assertIn(required, reference)

    def test_stacked_children_link_separately(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        orchestration = ORCHESTRATION.read_text(encoding="utf-8")
        normalized = " ".join(reference.split())
        orchestration_normalized = " ".join(orchestration.split())

        self.assertIn("separate G-owned pairwise stack-link workflow", normalized)
        self.assertIn("Before bootstrapping a stacked child", orchestration_normalized)
        self.assertNotIn("Task-only", normalized)
        self.assertNotIn("Task closure set", normalized)

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
