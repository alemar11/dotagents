import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SourceIdeaLifecycleContractTests(unittest.TestCase):
    def test_publish_closes_only_exact_hosted_source_idea_after_readback(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        publish = (ROOT / "steps/publish.md").read_text(encoding="utf-8")
        mutate = (ROOT / "steps/mutate.md").read_text(encoding="utf-8")
        reconcile = (ROOT / "steps/reconcile-verify.md").read_text(encoding="utf-8")

        self.assertIn("closes only that source Idea as completed", skill)
        self.assertIn("final publication operation", publish)
        self.assertIn("after authoritative readback", mutate)
        self.assertIn("closed with reason `completed`", reconcile)
        self.assertIn("Preview and ambiguous source", skill)


if __name__ == "__main__":
    unittest.main()
