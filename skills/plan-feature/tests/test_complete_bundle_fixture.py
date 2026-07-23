from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (SKILL_ROOT / relative).read_text(encoding="utf-8")


def section(contents: str, heading: str, next_heading: str) -> str:
    start = contents.index(heading) + len(heading)
    end = contents.index(next_heading, start)
    return contents[start:end]


def table_fields(contents: str) -> list[str]:
    fields: list[str] = []
    for line in contents.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or cells[0] in {"Field", "---"}:
            continue
        fields.append(cells[0].strip("`"))
    return fields


def table_columns(contents: str) -> list[str]:
    header = next(line for line in contents.splitlines() if line.startswith("|"))
    return [cell.strip().strip("`") for cell in header.strip("|").split("|")]


def checklist_criteria(contents: str) -> list[str]:
    return re.findall(r"^- \[[ xX]\] (.+)$", contents, re.MULTILINE)


def manifest_list(contents: str, key: str) -> list[str]:
    block = contents.split(f"{key}:\n", 1)[1]
    next_key = re.search(r"(?m)^[a-z_]+:\n", block)
    if next_key:
        block = block[: next_key.start()]
    return re.findall(r"^  - (.+)$", block, re.MULTILINE)


class CompleteBundleFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = read("references/complete-bundle-proposal.md")
        cls.manifest = section(
            cls.fixture,
            "## Proposed Bundle Manifest",
            "## Structural Graph Compression Result",
        )
        cls.spec = section(
            cls.fixture,
            "## Proposed Feature Spec",
            "## Proposed Implementation Issue 01",
        )
        cls.issue_01 = section(
            cls.fixture,
            "## Proposed Implementation Issue 01",
            "## Final Proposed Closeout Issue",
        )
        cls.issue_02 = section(
            cls.fixture,
            "## Final Proposed Closeout Issue",
            "## Expected Publication Order",
        )

    def test_run_registry_contains_only_write_mode(self) -> None:
        options = read("references/options.md")
        registry = section(options, "## Run Registry", "## Resolution")
        self.assertEqual(["write_mode"], table_fields(registry))

    def test_execution_contracts_have_exactly_seven_fields(self) -> None:
        expected = [
            "source_spec_ref",
            "feature_slug",
            "affected_repositories",
            "allowed_paths",
            "target_branch_name",
            "delivery_type",
            "dependency_ids",
        ]
        template = section(
            read("references/issue-body-template.md"),
            "## Execution Contract",
            "## Goal",
        )
        self.assertEqual(expected, table_fields(template))
        for issue in (self.issue_01, self.issue_02):
            self.assertEqual(
                expected,
                table_fields(section(issue, "## Execution Contract", "## Goal")),
            )
            self.assertEqual(1, issue.count("## Execution Contract"))

    def test_delivery_type_is_stable_across_spec_and_issues(self) -> None:
        identity = section(self.spec, "## Planning Identity", "## Problem")
        self.assertIn("Delivery type: `github-pr`", identity)
        for issue in (self.issue_01, self.issue_02):
            contract = section(issue, "## Execution Contract", "## Goal")
            rows = {
                row[0]: row[1]
                for row in (
                    [cell.strip().strip("`") for cell in line.strip("|").split("|")]
                    for line in contract.splitlines()
                    if line.startswith("|")
                )
                if len(row) == 2 and row[0] not in {"Field", "---"}
            }
            self.assertEqual("github-pr", rows["delivery_type"])

    def test_feature_dependency_table_has_exact_columns(self) -> None:
        dependencies = section(
            self.spec, "## Feature Dependencies", "## Acceptance Criteria"
        )
        self.assertEqual(
            ["upstream_feature_spec_ref", "dependency_reason"],
            table_columns(dependencies),
        )

    def test_manifest_has_complete_artifact_graph_and_publication_order(self) -> None:
        refs = re.findall(r"^  - ref: (.+)$", self.manifest, re.MULTILINE)
        children = re.findall(r"^  - child: (.+)$", self.manifest, re.MULTILINE)
        parents = re.findall(r"^    parent: (.+)$", self.manifest, re.MULTILINE)
        publication_order = manifest_list(self.manifest, "publication_order")

        self.assertEqual(
            [
                "proposed-spec:account-settings-export",
                "proposed-issue:account-settings-export/01",
                "proposed-issue:account-settings-export/02",
            ],
            refs,
        )
        self.assertEqual(refs[1:], children)
        self.assertEqual([refs[0], refs[0]], parents)
        self.assertEqual(refs, publication_order)

    def test_issue_dependencies_resolve_and_are_forward_only(self) -> None:
        dependency_values = re.findall(
            r"^    dependency_ids: (.+)$", self.manifest, re.MULTILINE
        )
        self.assertEqual(["none", "01"], dependency_values)
        generated_ids = {"01", "02"}
        for issue_id, raw_dependencies in zip(sorted(generated_ids), dependency_values):
            if raw_dependencies == "none":
                continue
            dependencies = {value.strip() for value in raw_dependencies.split(",")}
            self.assertLessEqual(dependencies, generated_ids)
            self.assertTrue(all(dependency < issue_id for dependency in dependencies))

    def test_spec_and_issue_checklists_are_independent_and_covered(self) -> None:
        spec_criteria = checklist_criteria(self.spec)
        issue_criteria = [
            checklist_criteria(self.issue_01),
            checklist_criteria(self.issue_02),
        ]

        self.assertTrue(spec_criteria)
        self.assertTrue(all(issue_criteria))
        self.assertEqual(len(spec_criteria), len(set(spec_criteria)))
        for criteria in issue_criteria:
            self.assertEqual(len(criteria), len(set(criteria)))
            self.assertNotEqual(spec_criteria, criteria)

        coverage_block = self.manifest.split("acceptance_coverage:\n", 1)[1].split(
            "publication_order:\n", 1
        )[0]
        entries = re.findall(
            r"  - spec_criterion: (.+)\n    issue_refs: (.+)", coverage_block
        )
        coverage = {
            criterion: {ref.strip() for ref in refs.split(",")}
            for criterion, refs in entries
        }
        valid_issue_refs = {
            "proposed-issue:account-settings-export/01",
            "proposed-issue:account-settings-export/02",
        }

        self.assertEqual(set(spec_criteria), set(coverage))
        for refs in coverage.values():
            self.assertTrue(refs)
            self.assertLessEqual(refs, valid_issue_refs)

    def test_proposal_is_non_durable_and_command_free(self) -> None:
        self.assertNotIn("workflow_state:", self.issue_01)
        self.assertNotIn("workflow_state:", self.issue_02)
        self.assertNotRegex(self.fixture, r"\bgh issue (create|edit)\b")
        self.assertTrue(
            all(ref.startswith("proposed-") for ref in manifest_list(self.manifest, "publication_order"))
        )

    def test_local_issue_paths_include_matching_done_destinations(self) -> None:
        done_paths = set(
            re.findall(
                r"[a-z0-9-]+/planning/features/[a-z0-9-]+/issues/done/[a-z0-9-]+\.md",
                self.fixture,
            )
        )
        self.assertTrue(done_paths)
        for done_path in done_paths:
            self.assertIn(done_path.replace("/done/", "/"), self.fixture)

    def test_multi_repository_refs_and_branches_are_unambiguous(self) -> None:
        probe = section(
            self.fixture,
            "## Multi-Repository Identity Probe",
            "## Existing Source Derived-Route Probe",
        )
        proposed_refs = set(re.findall(r"proposed-spec:[a-z0-9_:/-]+", probe))
        self.assertEqual(
            {
                "proposed-spec:account-platform/account-settings-export",
                "proposed-spec:account-platform/account-settings-export/api",
                "proposed-spec:account-platform/account-settings-export/web",
            },
            proposed_refs,
        )
        self.assertIn("feature/account-settings-export", probe)
        self.assertNotIn("feature/account-settings-export-integration", probe)

    def test_multi_repository_runtime_has_no_dedicated_integration_artifact(self) -> None:
        """Combined proof stays on ordinary implementation Specs and retired identities cannot reappear."""
        runtime = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [
                SKILL_ROOT / "SKILL.md",
                *sorted((SKILL_ROOT / "references").glob("*.md")),
            ]
        )
        for retired in (
            "Feature Spec: <Feature Name> - Integration",
            "planning/features/<feature-slug>/integration/SPEC.md",
            "Partial role: integration",
            "proposed-spec:<project_slug>/<feature_slug>/<repository_slug>/integration",
            "exactly one distinct repo-owned integration partial",
        ):
            self.assertNotIn(retired, runtime)

    def test_docs_and_fixture_are_portable(self) -> None:
        contents = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [
                SKILL_ROOT / "SKILL.md",
                *sorted((SKILL_ROOT / "references").glob("*.md")),
            ]
        )
        self.assertNotRegex(contents, r"(?:/Users/|/home/|[A-Za-z]:\\\\)")
        for path in (SKILL_ROOT / "references").glob("*.md"):
            self.assertEqual(path.name, path.name.lower())


if __name__ == "__main__":
    unittest.main()
