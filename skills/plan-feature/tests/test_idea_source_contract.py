from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (SKILL_ROOT / relative).read_text(encoding="utf-8")


class IdeaSourceContractTests(unittest.TestCase):
    def test_source_idea_refs_are_data_not_options(self) -> None:
        options = read("references/options.md")
        registry = options.split("## Run Registry", 1)[1].split(
            "## Project Memory Facts", 1
        )[0]
        fields = re.findall(r"^\| `([a-z_]+)` \|", registry, flags=re.MULTILINE)

        self.assertEqual(["mode", "write_mode"], fields)
        self.assertIn("`source_idea_refs`", options)
        self.assertIn("execution data", options.lower())
        self.assertNotIn("source_idea_refs", registry)

    def test_eligibility_and_durable_ref_shapes_are_explicit(self) -> None:
        contract = read("references/idea-source.md")

        for mode in ("mode=full-flow", "mode=spec-only"):
            self.assertIn(mode, contract)
        self.assertIn("mode=issues-from-existing-spec", contract)
        self.assertIn("Reject them", contract)
        self.assertIn("proposed-idea:", contract)
        self.assertIn("owner/repository#<number>", contract)
        self.assertIn("planning/ideas/<idea-slug>.md", contract)
        self.assertIn(
            "<repository-slug>/planning/ideas/<idea-slug>.md", contract
        )

    def test_backend_validation_keeps_idea_out_of_type_registry(self) -> None:
        contract = read("references/idea-source.md")
        normalized = " ".join(contract.split())

        self.assertIn("artifact_marker=idea", contract)
        self.assertIn("no native Issue Type", contract)
        self.assertIn("no other mapped canonical workflow-state label", normalized)
        self.assertIn("`artifact_marker: idea`", contract)
        self.assertIn("no `issue_type`", contract)
        self.assertIn("`needs-triage` or `needs-info`", contract)
        self.assertIn("mutually\nexclusive", contract)

    def test_projection_uses_only_feature_spec_source(self) -> None:
        contract = read("references/idea-source.md")
        template = read("references/spec-template.md")
        issue_template = read("references/issue-body-template.md")

        self.assertIn("- Source Idea: <durable-ref>", contract)
        self.assertIn("Source Idea:", template)
        self.assertIn("every parent or partial", contract)
        self.assertIn("Keep Idea refs out of generated", contract)
        self.assertNotIn("source_idea_refs", issue_template)
        self.assertNotIn("Source Idea", issue_template)

    def test_lifecycle_is_per_idea_terminal_and_apply_only(self) -> None:
        contract = read("references/idea-source.md")
        skill = read("SKILL.md")
        normalized = " ".join(contract.split())

        for phrase in (
            "Determine coverage independently for each selected Idea",
            "Waiting for one specific requester answer",
            "Preserve the Idea's previous state",
            "covers only part of the Idea",
            "fully covers the Idea",
            "perform read validation but request no GitStack mutation",
            "do not add or remove workflow labels while an interactive",
            "`## Planning Outcomes`",
            "retry only missing operations",
        ):
            self.assertIn(phrase, normalized)
        self.assertIn("Reconcile Selected Idea Sources", skill)
        self.assertIn("after the complete requested result", skill)

    def test_github_lifecycle_provisions_required_state_labels(self) -> None:
        contract = read("references/idea-source.md")
        normalized = " ".join(contract.split())

        self.assertIn(
            "A dormant Idea moving to `needs-info` requires the configured "
            "`needs-info` label",
            normalized,
        )
        self.assertIn(
            "a dormant Idea receiving partial coverage requires the configured "
            "`needs-triage` label",
            normalized,
        )
        self.assertIn("issue_operation=create-label", contract)
        self.assertIn("before mutating any affected Idea", normalized)
        self.assertIn("preserve the Idea's prior state", normalized)
        self.assertIn("Do not provision a label merely to clear", normalized)
        self.assertIn("request no mutation", normalized)

    def test_github_reads_are_available_without_proposal_mutation(self) -> None:
        contract = read("references/idea-source.md")
        skill = read("SKILL.md")

        self.assertIn("through `$gitstack:github-issues` in both write", contract)
        self.assertIn("omitting mutation fields", contract)
        self.assertIn("Proposal mode never requests dry-run mutations", skill)

    def test_partial_reconciliation_resume_accepts_completed_sources(self) -> None:
        contract = read("references/idea-source.md")
        skill = read("SKILL.md")
        normalized = " ".join(contract.split())

        self.assertIn("Consumed And Recovery State", contract)
        self.assertIn("closed, marker-valid, untyped Idea", normalized)
        self.assertIn("exact same authoritative `feature_spec_refs`", normalized)
        self.assertIn("Do not reopen it, duplicate the comment", normalized)
        self.assertIn("outcome comment first", normalized)
        self.assertIn("close a fully covered Idea last", normalized)
        self.assertIn("already reconciled only when", skill)

    def test_local_full_outcome_marks_consumed_with_explicit_replan_escape(self) -> None:
        contract = read("references/idea-source.md")
        normalized = " ".join(contract.split())

        self.assertIn("`coverage: full` entry", normalized)
        self.assertIn("not valid input for an ordinary new planning run", normalized)
        self.assertIn("explicitly asks to plan the consumed Idea again", normalized)
        self.assertIn("source data, not another selectable option", normalized)
        self.assertIn("feature_spec_refs: <durable-ref>", contract)

    def test_missing_marker_mapping_is_a_narrow_prerequisite(self) -> None:
        contract = read("references/idea-source.md")
        options = read("references/options.md")

        for contents in (contract, options):
            self.assertIn("blocks only Idea", contents)
        self.assertIn("do not invalidate an unrelated Plan Feature run", contract)


if __name__ == "__main__":
    unittest.main()
