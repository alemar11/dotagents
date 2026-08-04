import unittest
from pathlib import Path


REFERENCE = Path(__file__).resolve().parents[1] / "references/review-delivery.md"
SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


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


if __name__ == "__main__":
    unittest.main()
