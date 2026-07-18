from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]


def read(relative: str) -> str:
    return (SKILL_ROOT / relative).read_text(encoding="utf-8")


def evaluate_state_fixture(case: dict[str, object]) -> dict[str, object]:
    kind = case["kind"]

    if kind == "routing":
        recovery = bool(case["planning_result_durable"]) and (
            case["latest_outcome"] == "full" or bool(case["missing_operations"])
        )
        return {
            "route": "reconciliation-only" if recovery else "ordinary-validation",
            "ordinary_validation": not recovery,
            "operations": list(case["missing_operations"]),
        }

    if kind == "proposal":
        blocked = int(case["blocked"])
        deferred = int(case["deferred"])
        planned = int(case["proposed_spec_sections"]) + int(
            case["proposed_non_goals"]
        )
        intended = None
        if not blocked and planned:
            intended = "partial" if deferred else "full"
        return {
            "intended_coverage": intended,
            "durable_coverage_changed": False,
            "canonical_outcome_written": False,
        }

    if kind == "comments":
        refs = {
            ref
            for page in case["comment_pages"]
            for comment in page
            if comment["marker"]
            for ref in comment["feature_spec_refs"]
        }
        return {"feature_spec_refs": sorted(refs)}

    if kind == "successor":
        prior = case["prior"]
        candidate = case["candidate"]
        if prior == candidate:
            classification = "idempotent"
        else:
            prior_refs = set(prior["feature_spec_refs"])
            candidate_refs = set(candidate["feature_spec_refs"])
            prior_covered = set(prior["covered_scope"])
            candidate_covered = set(candidate["covered_scope"])
            candidate_remaining = {
                item for item in candidate["remaining_scope"] if item != "none"
            }
            prior_remaining = {
                item for item in prior["remaining_scope"] if item != "none"
            }
            monotonic = (
                prior_refs < candidate_refs
                and prior_covered <= candidate_covered
                and prior_covered.isdisjoint(candidate_remaining)
                and (
                    prior_covered < candidate_covered
                    or candidate_remaining < prior_remaining
                )
            )
            classification = "valid-successor" if monotonic else "conflict"
        return {"classification": classification}

    if kind == "lifecycle":
        answered_failure = (
            case["prior_state"] == "needs-info"
            and bool(case["requester_answer_supplied"])
            and not bool(case["planning_result_durable"])
            and case["terminal_failure"] == "technical"
        )
        return {
            "workflow_state": "needs-triage" if answered_failure else case["prior_state"],
            "canonical_outcome_written": False,
        }

    raise AssertionError(f"unknown fixture kind: {kind}")


class IdeaSourceContractTests(unittest.TestCase):
    def test_source_idea_refs_and_discovery_are_data_not_options(self) -> None:
        options = read("references/options.md")
        registry = options.split("## Run Registry", 1)[1].split(
            "## Project Memory Facts", 1
        )[0]
        fields = re.findall(r"^\| `([a-z_]+)` \|", registry, flags=re.MULTILINE)

        self.assertEqual(["mode", "write_mode"], fields)
        self.assertIn("`source_idea_refs`", options)
        self.assertIn("explicit Idea-discovery intent", options)
        self.assertIn("invocation evidence, not a field", options)
        self.assertNotIn("source_idea_refs", registry)
        self.assertNotIn("idea_discovery", registry)

    def test_eligibility_and_durable_ref_shapes_are_explicit(self) -> None:
        contract = read("references/idea-source.md")

        for mode in ("mode=full-flow", "mode=spec-only"):
            self.assertIn(mode, contract)
        self.assertIn("mode=issues-from-existing-spec", contract)
        self.assertIn("Reject Idea input", contract)
        self.assertIn("proposed-idea:", contract)
        self.assertIn("owner/repository#<number>", contract)
        self.assertIn("planning/ideas/<idea-slug>.md", contract)
        self.assertIn(
            "<repository-slug>/planning/ideas/<idea-slug>.md", contract
        )

    def test_discovery_is_explicit_read_only_and_selection_gated(self) -> None:
        contract = read("references/idea-discovery.md")
        source_contract = read("references/idea-source.md")
        skill = read("SKILL.md")
        normalized = " ".join(contract.split())

        for phrase in (
            "Run discovery only when the user explicitly asks",
            "Never scan an Idea backlog during an ordinary planning request",
            "Discovery itself never changes labels, files, comments, or issue state",
            "Require an explicit selection before drafting",
            "The selected durable refs become the existing `source_idea_refs`",
            "require separate Plan Feature runs",
        ):
            self.assertIn(phrase, normalized)
        self.assertIn("optional Idea discovery and source validation", skill)
        self.assertIn("If the user only asked to inspect the backlog", normalized)
        self.assertIn("Load `idea-source.md` in validation-only mode", contract)
        self.assertIn("from `idea-discovery.md` for validation-only", source_contract)
        self.assertIn("reconciliation-pending rather than a planning candidate", normalized)
        self.assertNotIn("list open issues", source_contract)

    def test_backend_validation_keeps_idea_out_of_type_registry(self) -> None:
        contract = read("references/idea-source.md")
        normalized = " ".join(contract.split())

        self.assertIn("artifact_marker=idea", contract)
        self.assertIn("has no native Issue Type", contract)
        self.assertIn("no other mapped canonical workflow-state label", normalized)
        self.assertIn("`artifact_marker: idea`", contract)
        self.assertIn("no `issue_type`", contract)
        self.assertIn("`needs-triage` or `needs-info`", contract)
        self.assertIn("workflow states are mutually exclusive", normalized)
        self.assertIn("Read the complete body and the complete comment history", normalized)
        self.assertIn("following pagination", normalized)

    def test_all_idea_sections_have_a_tentative_planning_mapping(self) -> None:
        contract = read("references/idea-source.md")
        template = (SKILL_ROOT.parent / "capture-idea" / "references" / "idea-template.md").read_text(
            encoding="utf-8"
        )

        for heading in (
            "Summary",
            "Problem or Opportunity",
            "Proposed Direction",
            "Expected Value",
            "Known Context and Constraints",
            "Open Questions",
            "Source",
        ):
            self.assertIn(f"## {heading}", template)
            self.assertIn(f"`{heading}`", contract)
        self.assertIn("Do not silently promote tentative direction", contract)
        self.assertIn("never acceptance criteria by itself", contract)

    def test_coverage_states_and_terminal_derivation_are_deterministic(self) -> None:
        contract = read("references/idea-source.md")
        normalized = " ".join(contract.split())

        for state in ("covered", "excluded", "deferred", "blocked"):
            self.assertRegex(contract, rf"\| `{state}` \|")
        self.assertIn("`full`: every material element is `covered` or `excluded`", normalized)
        self.assertIn("`partial`: at least one material element", normalized)
        self.assertIn("at least one element is `blocked`", normalized)
        self.assertIn("`covered_scope` and `remaining_scope`", normalized)
        self.assertIn("Do not persist the internal map", contract)
        self.assertIn("report-only intended projection", normalized)
        self.assertIn("intended_coverage=partial|full", contract)
        self.assertIn("never satisfy durable `covered` or `excluded`", normalized)

    def test_projection_uses_only_feature_spec_source(self) -> None:
        contract = read("references/idea-source.md")
        template = read("references/spec-template.md")
        phase = read("references/spec-phase.md")
        normalized_phase = " ".join(phase.split())
        issue_template = read("references/issue-body-template.md")

        self.assertIn("- Source Idea: <durable-ref>", contract)
        self.assertIn("Source Idea:", template)
        self.assertIn("every parent or partial", contract)
        self.assertIn("Keep Idea refs and coverage maps out of generated", contract)
        self.assertIn("trace every material accepted element", normalized_phase)
        self.assertNotIn("source_idea_refs", issue_template)
        self.assertNotIn("Source Idea", issue_template)

    def test_prior_partial_outcomes_are_loaded_and_coverage_is_cumulative(self) -> None:
        contract = read("references/idea-source.md")
        normalized = " ".join(contract.split())

        self.assertIn("With one or more `coverage: partial` records", normalized)
        self.assertIn("load and validate every listed durable Feature Spec", normalized)
        self.assertIn("plan only the remaining scope", normalized)
        self.assertIn("cumulatively across verified prior Specs", normalized)
        self.assertIn("use cumulative refs and scope", normalized)
        self.assertIn("Missing, malformed, ambiguous, or unrelated prior refs block", normalized)
        self.assertIn("monotonic cumulative history", normalized)
        self.assertIn("must not return previously covered scope", normalized)

    def test_canonical_outcome_is_exact_cumulative_and_append_only(self) -> None:
        contract = read("references/idea-source.md")
        normalized = " ".join(contract.split())
        block = (
            "## Planning Outcome\n"
            "<!-- plan-feature:idea-outcome -->\n"
            "coverage: <partial|full>\n"
            "feature_spec_refs:\n"
            "- <globally unambiguous durable ref>\n"
            "covered_scope:\n"
            "- <concise cumulative covered outcome>\n"
            "remaining_scope:\n"
        )

        self.assertIn(block, contract)
        self.assertIn("`### Planning Outcome` subsection", contract)
        self.assertIn("one append-only\n`## Planning Outcomes` section", contract)
        self.assertIn("order them lexicographically", contract)
        self.assertIn("single `remaining_scope` item `none` for `full`", contract)
        self.assertIn("exact latest block as already applied", contract)
        self.assertIn("strict superset", contract)
        self.assertIn("same cumulative ref set with different coverage or scope", normalized)
        self.assertIn("retired\n  one-line outcome syntax", contract)
        self.assertNotIn("- coverage: <partial|full>; feature_spec_refs:", contract)

    def test_lifecycle_is_terminal_apply_only_and_answer_aware(self) -> None:
        contract = read("references/idea-source.md")
        skill = read("SKILL.md")
        normalized = " ".join(contract.split())

        for phrase in (
            "determine durable coverage independently for each selected Idea",
            "Waiting for one specific requester answer",
            "Failure after a supplied answer resolved `needs-info`",
            "replace stale `needs-info` with `needs-triage`",
            "Cumulative durable planning covers only part",
            "Cumulative durable planning fully covers",
            "leave durable coverage unchanged and request no GitStack mutation",
            "Do not add or remove workflow labels while an interactive",
        ):
            self.assertIn(phrase, normalized)
        self.assertIn("Reconcile Selected Idea Sources", skill)
        self.assertIn("after the complete requested result", skill)

    def test_github_lifecycle_provisions_required_state_labels(self) -> None:
        contract = read("references/idea-source.md")
        normalized = " ".join(contract.split())

        self.assertIn("reconciliation that adds a workflow state", normalized)
        self.assertIn("issue_operation=create-label", contract)
        self.assertIn("before mutating any affected Idea", normalized)
        self.assertIn("preserve current hosted state", normalized)
        self.assertIn("Do not provision a label merely to clear", normalized)
        self.assertIn("request no mutation", normalized)

    def test_proposal_allows_github_reads_but_forbids_mutation(self) -> None:
        contract = read("references/idea-source.md")
        phase = read("references/spec-phase.md")
        skill = read("SKILL.md")
        canonical_outcome = contract.split("```markdown", 1)[1].split("```", 1)[0]

        self.assertIn("through `$gitstack:github-issues` in both write", contract)
        self.assertIn("omitting mutation fields", contract)
        self.assertIn("keep the durable map unchanged", contract)
        self.assertIn("do not render a canonical planning", phase)
        for field in (
            "intended_coverage",
            "intended_covered_scope",
            "intended_remaining_scope",
        ):
            self.assertIn(field, contract)
            self.assertIn(field, phase)
            self.assertIn(field, skill)
            self.assertNotIn(field, canonical_outcome)
        self.assertIn("never invokes GitStack for publication or mutation", phase)
        self.assertIn("may still use read-only GitStack", phase)
        self.assertNotIn("`write_mode=propose` never invokes GitStack.", phase)
        self.assertIn("Proposal mode never requests dry-run mutations", skill)

    def test_reconciliation_recovery_precedes_ordinary_validation(self) -> None:
        contract = read("references/idea-source.md")
        skill = read("SKILL.md")
        normalized_skill = " ".join(skill.split())
        phase = read("references/spec-phase.md")
        normalized = " ".join(contract.split())

        self.assertIn("Reconciliation-Only Recovery", contract)
        self.assertIn("before ordinary source validation", normalized)
        self.assertIn("Do not draft, republish, or rewrite Feature Specs", normalized)
        self.assertIn("Accept an already-closed GitHub Idea only", normalized)
        self.assertIn("skip verified completed sources", normalized)
        self.assertIn("run its reconciliation-only recovery branch first", normalized_skill)
        self.assertIn("route reconciliation-only recovery before this phase", phase)
        recovery = skill.index("Before ordinary Idea validation or discovery")
        ordinary = skill.index("Otherwise, when the invocation supplies `source_idea_refs`")
        discovery = skill.index("When exact refs are absent but the user explicitly asks")
        self.assertLess(recovery, ordinary)
        self.assertLess(recovery, discovery)
        self.assertIn("An open GitHub Idea in that state, or a local full-outcome Idea", normalized)
        self.assertIn("is reconciliation-pending", normalized)

    def test_consumed_sources_require_recovery_or_explicit_replan(self) -> None:
        contract = read("references/idea-source.md")
        normalized = " ".join(contract.split())

        self.assertIn("latest canonical record is `coverage: full`", normalized)
        self.assertIn("not valid ordinary planning input", normalized)
        self.assertIn("explicitly asks to plan it again", normalized)
        self.assertIn("execution data, not selectable options", normalized)
        self.assertIn("separately authorized reopening", normalized)

    def test_missing_marker_mapping_is_a_narrow_prerequisite(self) -> None:
        contract = read("references/idea-source.md")
        options = read("references/options.md")
        normalized_options = " ".join(options.split())

        for contents in (contract, options):
            self.assertIn("blocks only", contents)
        self.assertIn("Idea capture, discovery, or consumption", normalized_options)
        self.assertIn("Idea capture, discovery, or consumption", read("SKILL.md"))
        self.assertIn(
            "do not invalidate an unrelated Plan Feature run",
            " ".join(contract.split()),
        )

    def test_forward_scenarios_cover_the_refined_paths(self) -> None:
        fixture = read("tests/idea-source-scenarios.md")
        headings = re.findall(r"^## (.+)$", fixture, flags=re.MULTILINE)

        self.assertEqual(
            [
                "Explicit Local Idea To Spec-Only Full Coverage",
                "Explicit GitHub Discovery Without Selection",
                "Proposal Mode Reads Without Mutation",
                "Multiple Ideas Stay Bounded",
                "Repeated Partial Planning Becomes Cumulative Full Coverage",
                "Conflicting Cumulative Outcome Is Rejected",
                "Reconciliation-Only Recovery",
                "Answered Needs-Info Does Not Stay Stale",
                "Full-Flow Completion Precedes PR Delivery",
            ],
            headings,
        )
        for phrase in (
            "all seven canonical Idea sections",
            "perform no comment, label, type, close, Feature Spec, or issue mutation",
            "mutation fields omitted",
            "read the complete paginated comment history",
            "render no canonical planning outcome block",
            "require a separate Plan Feature run",
            "derive cumulative full coverage from both Specs",
            "strict superset",
            "retry only the missing close operation",
            "replace stale `needs-info` with `needs-triage`",
            "do not wait for a future implementation PR or PR merge",
        ):
            self.assertIn(phrase, " ".join(fixture.split()))

    def test_state_transition_fixtures_are_executable(self) -> None:
        fixture_path = SKILL_ROOT / "tests" / "idea-source-state-fixtures.json"
        cases = json.loads(fixture_path.read_text(encoding="utf-8"))

        self.assertEqual(7, len(cases))
        self.assertEqual(len(cases), len({case["name"] for case in cases}))
        for case in cases:
            with self.subTest(case=case["name"]):
                self.assertEqual(case["expected"], evaluate_state_fixture(case))

    def test_repo_guidance_keeps_idea_as_planning_not_delivery_lifecycle(self) -> None:
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        normalized = " ".join(agents.split())

        self.assertIn("Allow backlog discovery only from an explicit", normalized)
        self.assertIn("monotonic cumulative covered and remaining scope", normalized)
        self.assertIn("An Idea tracks planning completion", normalized)
        self.assertIn("later PR merge does not own its closure", normalized)


if __name__ == "__main__":
    unittest.main()
