import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SourceIdeaLifecycleContractTests(unittest.TestCase):
    def test_publish_closes_only_exact_hosted_source_idea_after_readback(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        publication = (ROOT / "steps/plan-publication.md").read_text(encoding="utf-8")

        normalized_skill = " ".join(skill.split())
        self.assertIn("close that source Idea as completed", normalized_skill)
        self.assertIn("complete Feature Plan Set", normalized_skill)
        self.assertIn(
            "Publish one parent issue of type Feature per Feature member",
            " ".join(publication.split()),
        )
        self.assertIn("authoritative read-after-write evidence", publication)
        self.assertIn("close that Idea with reason", publication)
        self.assertIn(
            "Preview and ambiguous source identity never close an Idea",
            " ".join(publication.split()),
        )

    def test_feature_publication_creates_verified_macro_task_projection(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        publication = (ROOT / "steps/plan-publication.md").read_text(encoding="utf-8")
        validation = (ROOT / "steps/plan-validation.md").read_text(encoding="utf-8")
        template = (ROOT / "templates/plan.md").read_text(encoding="utf-8")

        normalized_skill = " ".join(skill.split())
        normalized_publication = " ".join(publication.split())
        normalized_validation = " ".join(validation.split())

        self.assertIn("closed set of Macro Tasks", normalized_skill)
        self.assertIn("one hosted child Task projection for every Macro Task", normalized_skill)
        self.assertIn("one child issue of type Task per Macro Task", normalized_publication)
        self.assertIn("final set registry", normalized_publication)
        self.assertIn("one or more local Macro Tasks", normalized_validation)
        self.assertIn("cyclic reference", normalized_validation)
        self.assertIn("macro_task_closure_policy", template)
        self.assertIn("parent-feature-and-its-associated-macro-tasks", template)

    def test_feature_plan_set_keeps_feature_and_macro_dependency_scopes_separate(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        convergence = (ROOT / "steps/convergence.md").read_text(encoding="utf-8")
        validation = (ROOT / "steps/plan-validation.md").read_text(encoding="utf-8")
        publication = (ROOT / "steps/plan-publication.md").read_text(encoding="utf-8")
        plan = (ROOT / "templates/plan.md").read_text(encoding="utf-8")
        macro_task = (ROOT / "templates/macro-task.md").read_text(encoding="utf-8")

        normalized_skill = " ".join(skill.split())
        normalized_convergence = " ".join(convergence.split())
        normalized_validation = " ".join(validation.split())
        normalized_publication = " ".join(publication.split())

        for required in (
            "Feature Plan Set",
            "feature_plan_set_id",
            "stable lower-kebab `feature_id`",
            "Feature-level `blocked_by`",
            "same `parent_feature_id`",
            "Cross-Feature Task-to-Task edges are invalid",
            "Do not create a Feature Plan Set container",
        ):
            self.assertIn(required, normalized_skill)

        self.assertIn("one parent issue of type Feature per Feature member", normalized_publication)
        self.assertIn("same `parent_feature_id`", normalized_validation)
        self.assertIn("cross-parent", normalized_validation)
        self.assertIn("Feature-level `blocked_by` relations only between Feature IDs", normalized_convergence)
        self.assertIn("feature_plan_set_id", plan)
        self.assertIn("parent_feature_id", macro_task)
        self.assertIn("Cross-Feature Macro Task references are invalid", macro_task)


if __name__ == "__main__":
    unittest.main()
