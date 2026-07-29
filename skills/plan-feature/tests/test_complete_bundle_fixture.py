from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
IMPLEMENT_RUN_STATE = (
    SKILL_ROOT.parent / "implement-feature" / "scripts" / "run-state"
)


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
        self.assertNotIn("Repository layout:", self.fixture)
        self.assertNotIn("repository_layout", self.fixture)

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

    def test_allowed_path_scope_contract_uses_complete_envelopes_and_exact_exceptions(self) -> None:
        spec_phase = read("references/spec-phase.md")
        contract = section(
            spec_phase,
            "#### Allowed Path Scope Contract",
            "### 3. Gate An Existing Source Or Draft",
        )
        rows: dict[str, str] = {}
        for line in contract.splitlines():
            match = re.fullmatch(r"\| `([^`]+)` \| `([^`]+)` \|", line.strip())
            if match:
                rows[match.group(1)] = match.group(2)

        self.assertEqual(
            {
                "feature-owned-work": "complete-safe-prefixes",
                "exact-file-boundary": "exact-path",
                "local-tracker-lifecycle": "exact-active-and-done-paths",
                "unrelated-pre-existing-failure": "excluded",
            },
            rows,
        )

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
                "proposed-spec:019f930d-6879-7ef2-8570-69b9ed8a35dd/api",
                "proposed-spec:019f930d-6879-7ef2-8570-69b9ed8a35dd/web",
            },
            proposed_refs,
        )
        self.assertIn("feature_id: 019f930d-6879-7ef2-8570-69b9ed8a35dd", probe)
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
            "coordination-only parent",
        ):
            self.assertNotIn(retired, runtime)

    def test_linked_feature_specs_share_feature_id_and_exact_set_shape(self) -> None:
        template = read("references/spec-template.md")
        phase = read("references/spec-phase.md")
        feature_set = section(template, "## Feature Spec Set", "## Feature Dependencies")

        self.assertIn("Feature ID:", template)
        for canonical_shape in (
            "- Feature ID: `<canonical-lowercase-uuid>`.",
            "- Repository key: `<repository-key>`.",
            "- Proof ID: `<repository-key>:proof-<lower-kebab-boundary>`.",
            "- [ ] `<repository-key>:ac-<NN>`",
            "every owned ID as an exact inline-code token",
        ):
            self.assertIn(canonical_shape, template)
        self.assertEqual(
            ["feature_spec_ref", "affected_repository", "responsibility"],
            table_columns(feature_set),
        )
        for phrase in (
            "canonical lowercase UUID `feature_id`",
            "exact normalized equality",
            "including self",
            "whole-set update",
        ):
            self.assertIn(phrase, phase)
        self.assertNotIn("project-memory/config/project-layout.md", phase)

    def test_cross_repository_decision_targets_resolve_to_declared_members(self) -> None:
        """ADR backlinks use the linked-set identity rather than an ambiguous repo slug."""
        issue_template = read("references/issue-body-template.md")
        issue_phase = read("references/issue-phase.md")
        expected = "<feature-id>--<repository-key>/<repo-relative-path>"
        self.assertIn(expected, issue_template)
        self.assertIn(expected, issue_phase)
        self.assertRegex(
            issue_phase,
            r"backlink that copies the exact same\s+canonical target string",
        )
        self.assertNotIn(
            "<repo-slug>/<repo-relative-path>",
            issue_template,
        )

    def test_template_conforming_linked_specs_pass_the_implement_feature_validator(self) -> None:
        """Parser-sensitive generated Markdown stays executable end to end."""
        feature_id = "123e4567-e89b-42d3-a456-426614174000"
        table = "\n".join(
            (
                "| feature_spec_ref | affected_repository | responsibility |",
                "| --- | --- | --- |",
                "| acme/account-api#241 | github:acme/account-api | `api:ac-01` |",
                "| acme/account-web#118 | github:acme/account-web | "
                "`web:ac-01` and `web:proof-api-web` |",
            )
        )

        def body(repository_key: str, criterion_id: str, proof_id: str | None) -> str:
            proof = (
                "\n".join(
                    (
                        "",
                        "## Integration Execution Contract",
                        "",
                        f"- Proof ID: `{proof_id}`.",
                    )
                )
                if proof_id
                else ""
            )
            return "\n".join(
                (
                    "# Feature Spec: Account Settings Export",
                    "",
                    "## Planning Identity",
                    "",
                    f"- Feature ID: `{feature_id}`.",
                    f"- Repository key: `{repository_key}`.",
                    "- Feature slug: account-settings-export.",
                    "",
                    "## Feature Spec Set",
                    "",
                    table,
                    proof,
                    "",
                    "## Acceptance Criteria",
                    "",
                    f"- [ ] `{criterion_id}` is proven.",
                    "",
                )
            )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            api = root / "api.md"
            web = root / "web.md"
            api.write_text(body("api", "api:ac-01", None), encoding="utf-8")
            web.write_text(
                body("web", "web:ac-01", "web:proof-api-web"),
                encoding="utf-8",
            )
            input_path = root / "feature-spec-set.json"
            input_path.write_text(
                json.dumps(
                    {
                        "schema": "implement-feature/feature-spec-set-input",
                        "schema_version": "1.0.0",
                        "members": [
                            {
                                "source_spec_ref": "acme/account-api#241",
                                "affected_repository": "github:acme/account-api",
                                "body_file": str(api),
                            },
                            {
                                "source_spec_ref": "acme/account-web#118",
                                "affected_repository": "github:acme/account-web",
                                "body_file": str(web),
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    str(IMPLEMENT_RUN_STATE),
                    "--json",
                    "feature-spec-set",
                    "validate",
                    "--input",
                    str(input_path),
                ],
                env={
                    **os.environ,
                    "HOME": str(root),
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["feature_id"], feature_id)
        self.assertEqual(payload["member_count"], 2)
        self.assertFalse(payload["writes_performed"])

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
