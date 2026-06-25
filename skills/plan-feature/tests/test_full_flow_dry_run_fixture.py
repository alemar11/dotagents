from __future__ import annotations

import unittest
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (SKILLS_ROOT / relative).read_text(encoding="utf-8")


class FullFlowDryRunFixtureTests(unittest.TestCase):
    def test_fixture_covers_pipeline_and_draft_source_prd(self) -> None:
        fixture = read("plan-feature/references/full-flow-dry-run.md")

        for skill in ("$plan-feature", "$grill-me-with-context", "$to-prd", "$to-issues", "$codex-orchestrator"):
            self.assertIn(skill, fixture)

        self.assertIn("effective_target: draft-publish-commands", fixture)
        self.assertIn("external_tracker_mutation: disallowed", fixture)
        self.assertIn("source_prd_ref: draft-prd:account-settings-export", fixture)
        self.assertIn("Replace every issue body line", fixture)
        self.assertIn("must not dispatch implementation workers", fixture)

    def test_shared_contract_documents_draft_publish_handoff(self) -> None:
        contract = read("setup-project-memory/references/tracker-publishing.md")

        self.assertIn("source_prd_ref", contract)
        self.assertIn("draft-prd:<feature-slug>", contract)
        self.assertIn("Create or update the PRD first", contract)
        self.assertIn("Replace `Source PRD: draft-prd:<...>`", contract)
        self.assertIn("Do not dispatch implementation workers", contract)

    def test_skills_reference_shared_contract_and_extracted_template(self) -> None:
        plan_feature = read("plan-feature/SKILL.md")
        to_prd = read("to-prd/SKILL.md")
        to_issues = read("to-issues/SKILL.md")
        template = read("to-issues/references/issue-body-template.md")
        prd_delivery = read("codex-orchestrator/references/prd-backed-delivery.md")

        self.assertIn("references/full-flow-dry-run.md", plan_feature)
        self.assertIn("tracker-publishing.md", to_prd)
        self.assertIn("tracker-publishing.md", to_issues)
        self.assertIn("references/issue-body-template.md", to_issues)
        self.assertNotIn("# <feature-slug>: <NN> <vertical outcome>", to_issues)
        self.assertIn("# <feature-slug>: <NN> <vertical outcome>", template)
        self.assertIn("Source PRD: [path, issue number, or stable draft ref]", template)
        self.assertIn("draft-prd:<...>", prd_delivery)


if __name__ == "__main__":
    unittest.main()
