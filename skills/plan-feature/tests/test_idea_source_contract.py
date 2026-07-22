from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


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
    def test_run_registry_contains_only_write_mode(self) -> None:
        options = read("references/options.md")
        registry = options.split("## Run Registry", 1)[1].split(
            "## Derived Source Route", 1
        )[0]
        fields = re.findall(r"^\| `([a-z_]+)` \|", registry, flags=re.MULTILINE)

        self.assertEqual(["write_mode"], fields)
        self.assertNotIn("source_idea_refs", fields)
        self.assertNotIn("idea_discovery", fields)

    def test_idea_refs_are_kept_out_of_issue_execution_contracts(self) -> None:
        spec_template = read("references/spec-template.md")
        issue_template = read("references/issue-body-template.md")

        self.assertIn("- Source Idea:", spec_template)
        self.assertNotIn("source_idea_refs", issue_template)
        self.assertNotIn("Source Idea", issue_template)

    def test_state_transition_fixtures_are_executable(self) -> None:
        fixture_path = SKILL_ROOT / "tests" / "idea-source-state-fixtures.json"
        cases = json.loads(fixture_path.read_text(encoding="utf-8"))

        self.assertEqual(len(cases), len({case["name"] for case in cases}))
        for case in cases:
            with self.subTest(case=case["name"]):
                self.assertEqual(case["expected"], evaluate_state_fixture(case))


if __name__ == "__main__":
    unittest.main()
