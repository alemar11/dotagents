from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = SKILL_ROOT / "tests/fixtures/graph-compression-replays.json"


class GraphCompressionReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.cases = {case["id"]: case for case in cls.payload["cases"]}

    def test_catalog_covers_the_structural_replay_patterns(self) -> None:
        self.assertEqual(
            {
                "layered-single-outcome",
                "closeout-terminal-recompute",
                "overlapping-lifecycle-fragments",
                "same-size-independent-outcomes",
                "cross-spec-integration-owner",
                "fragmented-many-candidates",
                "many-independent-outcomes",
            },
            set(self.cases),
        )
        self.assertIn("Counts are observations only", self.payload["purpose"])

    def test_each_replay_has_a_valid_compressed_graph(self) -> None:
        for replay_id, replay in self.cases.items():
            with self.subTest(replay=replay_id):
                candidates = {candidate["id"]: candidate for candidate in replay["candidates"]}
                final_issues = replay["final_issues"]
                final_by_id = {issue["id"]: issue for issue in final_issues}
                expected = replay["expected"]

                self.assertEqual(len(candidates), len(replay["candidates"]))
                self.assertEqual(len(final_by_id), len(final_issues))
                self.assertEqual(expected["candidate_count"], len(candidates))
                self.assertEqual(expected["final_count"], len(final_issues))
                self.assertEqual(expected["minimum_hardening_calls"], len(final_issues))
                self.assertEqual(
                    expected["avoided_initial_hardening_calls"],
                    len(candidates) - len(final_issues),
                )

                sources = [candidate_id for issue in final_issues for candidate_id in issue["from"]]
                self.assertEqual(Counter(sources), Counter(candidates.keys()))

                for candidate in candidates.values():
                    for dependency_id in candidate["depends_on"]:
                        self.assertIn(dependency_id, candidates)
                        self.assertEqual(candidate["spec"], candidates[dependency_id]["spec"])

                source_owner: dict[str, str] = {}
                issue_order = {issue["id"]: index for index, issue in enumerate(final_issues)}
                for issue in final_issues:
                    self.assertTrue(issue["from"])
                    self.assertTrue(issue["why"].strip())
                    self.assertTrue(issue["title"].strip())
                    for candidate_id in issue["from"]:
                        self.assertEqual(issue["spec"], candidates[candidate_id]["spec"])
                        source_owner[candidate_id] = issue["id"]
                    for dependency_id in issue["depends_on"]:
                        self.assertIn(dependency_id, final_by_id)
                        self.assertEqual(issue["spec"], final_by_id[dependency_id]["spec"])
                        self.assertLess(issue_order[dependency_id], issue_order[issue["id"]])

                removed_edges = {
                    (candidate_id, dependency_id)
                    for candidate_id, dependency_id in replay["removed_dependency_edges"]
                }
                declared_edges = {
                    (candidate_id, dependency_id)
                    for candidate_id, candidate in candidates.items()
                    for dependency_id in candidate["depends_on"]
                }
                self.assertLessEqual(removed_edges, declared_edges)
                for candidate_id, candidate in candidates.items():
                    owner = final_by_id[source_owner[candidate_id]]
                    for dependency_id in candidate["depends_on"]:
                        dependency_owner = source_owner[dependency_id]
                        if owner["id"] == dependency_owner:
                            continue
                        if (candidate_id, dependency_id) in removed_edges:
                            self.assertNotIn(dependency_owner, owner["depends_on"])
                        else:
                            self.assertIn(dependency_owner, owner["depends_on"])

    def test_equal_candidate_counts_can_have_opposite_results(self) -> None:
        compressed = self.cases["overlapping-lifecycle-fragments"]["expected"]
        retained = self.cases["same-size-independent-outcomes"]["expected"]

        self.assertEqual(compressed["candidate_count"], retained["candidate_count"])
        self.assertLess(compressed["final_count"], compressed["candidate_count"])
        self.assertEqual(retained["final_count"], retained["candidate_count"])

    def test_large_valid_graph_is_not_compressed_by_count(self) -> None:
        replay = self.cases["many-independent-outcomes"]

        self.assertEqual(
            replay["expected"]["candidate_count"],
            replay["expected"]["final_count"],
        )
        self.assertEqual(0, replay["expected"]["avoided_initial_hardening_calls"])
        self.assertTrue(all(len(issue["from"]) == 1 for issue in replay["final_issues"]))

    def test_cross_spec_ordering_stays_out_of_issue_dependency_ids(self) -> None:
        replay = self.cases["cross-spec-integration-owner"]
        integration_issue = next(
            issue for issue in replay["final_issues"] if issue["role"] == "integration"
        )

        self.assertEqual([], integration_issue["depends_on"])
        self.assertEqual("integration", integration_issue["spec"])
        self.assertEqual(
            {"api", "web"},
            {edge["upstream_spec"] for edge in replay["feature_dependencies"]},
        )
        self.assertTrue(
            all(edge["spec"] == "integration" for edge in replay["feature_dependencies"])
        )

    def test_domain_closeout_owner_survives_as_the_terminal_issue(self) -> None:
        closeout_replays = [
            replay for replay in self.cases.values() if replay["domain_closeout_owner"]
        ]
        for replay in closeout_replays:
            with self.subTest(replay=replay["id"]):
                owner_id = replay["domain_closeout_owner"]
                owner = next(
                    issue for issue in replay["final_issues"] if issue["id"] == owner_id
                )
                remaining = [
                    issue for issue in replay["final_issues"] if issue["id"] != owner_id
                ]
                nodes_with_dependents = {
                    dependency_id
                    for issue in remaining
                    for dependency_id in issue["depends_on"]
                }
                terminals = {
                    issue["id"]
                    for issue in remaining
                    if issue["id"] not in nodes_with_dependents
                }

                self.assertEqual(owner_id, replay["final_issues"][-1]["id"])
                self.assertIn("closeout", owner["role"])
                self.assertEqual(terminals, set(owner["depends_on"]))
                self.assertFalse(
                    any(owner_id in issue["depends_on"] for issue in replay["final_issues"])
                )

if __name__ == "__main__":
    unittest.main()
