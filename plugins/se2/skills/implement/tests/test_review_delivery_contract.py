import unittest
from pathlib import Path


REFERENCE = Path(__file__).resolve().parents[1] / "references/review-delivery.md"
ORCHESTRATION = Path(__file__).resolve().parents[1] / "references/orchestration.md"
SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
PREFLIGHT = Path(__file__).resolve().parents[3] / "references/codex-dependency-preflight.md"


class ReviewDeliveryContractTests(unittest.TestCase):
    def test_pr_delivery_closes_tasks_but_not_features_or_ideas(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")

        for required in (
            "Task-only `closing_issue_refs`",
            "exclude every Feature and Idea issue",
            "one canonical `Closes` line per Task",
            "GitHub `closingIssuesReferences`",
            "`## References` entry as a substitute",
        ):
            self.assertIn(required, reference)

        self.assertIn("exact Task-only\n`closing_issue_refs`", skill)
        self.assertIn("while the Feature remains open", skill)

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
