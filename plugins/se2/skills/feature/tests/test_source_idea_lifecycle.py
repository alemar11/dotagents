import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SourceIdeaLifecycleContractTests(unittest.TestCase):
    def test_publish_closes_only_exact_hosted_source_idea_after_readback(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        publication = (ROOT / "steps/plan-publication.md").read_text(encoding="utf-8")

        self.assertIn("close that source Idea as completed only after", skill)
        self.assertIn(
            "Publish one Feature issue per repository-owned plan member",
            " ".join(publication.split()),
        )
        self.assertIn("authoritative read-after-write evidence", publication)
        self.assertIn("close that Idea with reason", publication)
        self.assertIn(
            "Preview and ambiguous source identity never close an Idea",
            publication,
        )


if __name__ == "__main__":
    unittest.main()
