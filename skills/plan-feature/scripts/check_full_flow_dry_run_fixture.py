from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
DOC_PATHS = [
    SKILL_ROOT / "SKILL.md",
    SKILL_ROOT / "agents/openai.yaml",
    *sorted((SKILL_ROOT / "references").glob("*.md")),
]


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
        value = cells[0]
        if value.startswith("`") and value.endswith("`"):
            value = value[1:-1]
        fields.append(value)
    return fields


def key_lines(contents: str) -> list[str]:
    return re.findall(r"^- ([a-z][a-z0-9_]*):", contents, re.MULTILINE)


REMOVED_FIELDS = (
    "execution" + "_profile",
    "effective" + "_target",
    "no_mutation" + "_override",
    "no_mutation" + "_output",
    "local" + "_mirror",
    "local" + "_mirror_path",
    "partial" + "_output",
    "change_delivery" + "_target",
    "change_delivery" + "_permission",
    "issue_update" + "_permission",
    "codex_review" + "_requirement",
    "pull_request_count" + "_strategy",
    "delivery_decision" + "_origin",
    "issue_repository" + "_layout",
    "parallel" + "ization",
    "blocked_issue" + "_ids",
    "issue_completion" + "_method",
    "domain" + "_closeout",
    "dependency_start" + "_condition",
    "option_rows" + "_finger" + "print",
    "issue_option_rows" + "_finger" + "print",
    "option" + "_resolution",
    "domain_knowledge" + "_delta",
)
REMOVED_VALUE = "upstream-merge-ready" + "-head"
REMOVED_HEADINGS = (
    "## " + "Delivery",
    "## " + "Orchestrator Handoff",
    "## " + "Option Resolution",
)


class PlanFeatureReductionTests(unittest.TestCase):
    def test_run_registry_has_only_mode_and_write_mode(self) -> None:
        options = read("references/options.md")
        registry = section(options, "## Run Registry", "## Project Memory Facts")

        self.assertEqual(["mode", "write_mode"], table_fields(registry))
        self.assertIn("`full-flow`, `spec-only`, `issues-from-existing-spec`", registry)
        self.assertIn("`apply`, `propose`", registry)
        self.assertIn("explicit Plan Feature request to create durable", registry)
        self.assertIn("Project Memory resolves its own write authority", registry)

    def test_tracker_and_topology_are_project_memory_facts(self) -> None:
        options = read("references/options.md")
        facts = section(options, "## Project Memory Facts", "## Execution Data")
        registry = section(options, "## Run Registry", "## Project Memory Facts")

        self.assertIn("`tracker_backend`", facts)
        self.assertIn("`repository_layout`", facts)
        self.assertNotIn("`tracker_backend`", registry)
        self.assertNotIn("`repository_layout`", registry)

    def test_retired_contract_is_absent_from_plan_feature_docs(self) -> None:
        for path in DOC_PATHS:
            contents = path.read_text(encoding="utf-8")
            for field in REMOVED_FIELDS:
                self.assertNotIn(field, contents, f"{field} remains in {path}")
            self.assertNotIn(REMOVED_VALUE, contents, f"early stack remains in {path}")
            for heading in REMOVED_HEADINGS:
                self.assertNotIn(heading, contents, f"{heading} remains in {path}")
            self.assertNotIn("finger" + "print", contents, f"digest field remains in {path}")

    def test_normal_execution_contract_has_exactly_six_fields(self) -> None:
        template = read("references/issue-body-template.md")
        contract = section(template, "## Execution Contract", "## Goal")
        fields = table_fields(contract)

        self.assertEqual(
            [
                "source_spec_ref",
                "feature_slug",
                "affected_repositories",
                "allowed_paths",
                "target_branch_name",
                "dependency_ids",
            ],
            fields,
        )

        fixture = read("references/full-flow-dry-run.md")
        emitted = section(fixture, "## Execution Contract", "## Goal")
        self.assertEqual(
            [
                "source_spec_ref",
                "feature_slug",
                "affected_repositories",
                "allowed_paths",
                "target_branch_name",
                "dependency_ids",
            ],
            table_fields(emitted),
        )

    def test_execution_contract_is_single_projection(self) -> None:
        template = read("references/issue-body-template.md")
        issue_phase = read("references/issue-phase.md")

        self.assertEqual(1, template.count("## Execution Contract"))
        before_contract = template.split("## Execution Contract", 1)[0]
        self.assertNotIn("source_spec_ref:", before_contract)
        self.assertNotIn("## Dependencies", template)
        self.assertNotIn("## Dependencies", read("references/full-flow-dry-run.md"))
        self.assertIn("exactly one", issue_phase)
        self.assertIn("no duplicate delivery or handoff", issue_phase)

    def test_reverse_edges_are_derived(self) -> None:
        options = read("references/options.md")
        issue_phase = read("references/issue-phase.md")
        vertical = read("references/vertical-slices.md")

        for contents in (options, issue_phase, vertical):
            self.assertIn("reverse", contents.lower())
            self.assertIn("derive", contents.lower())
        self.assertIn("store only `dependency_ids`", issue_phase)

    def test_feature_dependencies_have_no_start_choice(self) -> None:
        options = read("references/options.md")
        spec_template = read("references/spec-template.md")
        spec_phase = read("references/spec-phase.md")

        expected = "| upstream_feature_spec_ref | dependency_reason |"
        self.assertIn(expected, spec_template)
        contract = section(
            options,
            "## Feature Dependency Contract",
            "## Canonical Input Requirement",
        )
        self.assertEqual(
            ["upstream_feature_spec_ref", "dependency_reason"],
            table_fields(contract),
        )
        self.assertIn("waiting for upstream merge and integration proof", spec_phase)

    def test_non_app_exception_is_conditional_and_app_incompatible(self) -> None:
        skill = read("SKILL.md")
        options = read("references/options.md")
        reference = read("references/non-app-delivery.md")
        issue_phase = read("references/issue-phase.md")
        spec_template = read("references/spec-template.md")

        self.assertIn("current request and any\ndurable source Feature Spec", skill)
        self.assertIn("incompatible with", skill)
        self.assertIn("`$codex-orchestrator`", skill)
        self.assertIn("Before validating selectable fields", skill)
        self.assertIn("before structured option validation", options)
        self.assertIn("default-path run registry", skill)
        for contents in (skill, options, reference, issue_phase, spec_template):
            self.assertIn("canonical", contents)
            self.assertIn("explicit_instruction_ref", contents)
        self.assertIn("`non_app_delivery_target`", reference)
        self.assertIn("evidence data, not an option", reference)
        self.assertIn("record exactly one line for\neach datum", reference)
        self.assertIn("Reject free-form quotes", reference)
        self.assertIn("unresolved refs", reference)
        self.assertIn("Add only `non_app_delivery_target`", reference)
        base_contract = section(
            read("references/issue-body-template.md"),
            "## Execution Contract",
            "## Goal",
        )
        registry = section(reference, "## Registry", "## Canonical Evidence Data")
        self.assertNotIn("explicit_instruction_ref", registry)
        self.assertNotIn("explicit_instruction_ref", base_contract)
        self.assertEqual(spec_template.count("non_app_delivery_target:"), 1)
        self.assertEqual(spec_template.count("explicit_instruction_ref:"), 1)
        self.assertIn("current-request-or-durable-source predicate", options)
        self.assertIn("canonical durable-source carry-forward", reference)
        self.assertNotIn("explicit-request predicate", options)
        self.assertNotIn("explicit user selection is required", reference)
        for value in (
            "local-commit-created-without-pushing",
            "changes-pushed-to-target-branch-without-pull-request",
            "validated-draft-pull-request-published",
        ):
            self.assertIn(value, reference)
        self.assertIn("does not grant", reference)
        self.assertIn("eventual non-App executor", reference)

    def test_write_mode_propose_is_non_mutating_and_command_free(self) -> None:
        options = read("references/options.md")
        skill = read("SKILL.md")
        spec_phase = read("references/spec-phase.md")
        issue_phase = read("references/issue-phase.md")
        fixture = read("references/full-flow-dry-run.md")

        for contents in (options, skill, spec_phase, issue_phase):
            self.assertIn("`write_mode=propose`", contents)
            self.assertRegex(
                contents,
                r"(?i)(perform|performs|write) no writes?|write nothing",
            )
        self.assertIn("mode: full-flow", fixture)
        self.assertIn("write_mode: propose", fixture)
        self.assertIn(
            "Return no executable publication command", " ".join(fixture.split())
        )
        self.assertNotIn("gh issue " + "create", fixture)
        self.assertNotIn("gh issue " + "edit", fixture)
        proposed_body = section(
            fixture,
            "## Representative Proposed Issue",
            "## Expected Pipeline",
        )
        self.assertNotIn("workflow_state:", proposed_body)
        self.assertIn("proposed-issue:account-settings-export/01", fixture)

    def test_apply_routes_to_local_and_github_trackers(self) -> None:
        spec_phase = read("references/spec-phase.md")
        issue_phase = read("references/issue-phase.md")

        for contents in (spec_phase, issue_phase):
            self.assertIn("`write_mode=apply`, GitHub", contents)
            self.assertIn("`write_mode=apply`, local", contents)
        self.assertIn("$gitstack:github-issues", issue_phase)
        self.assertIn("`mutation_mode=apply`", issue_phase)
        self.assertIn("`issue_operation`", issue_phase)
        self.assertIn("`write_mode=propose` never invokes GitStack", issue_phase)
        self.assertIn("planning/features/<feature-slug>/issues/", issue_phase)

    def test_incomplete_artifacts_are_withheld(self) -> None:
        skill = read("SKILL.md")
        options = read("references/options.md")
        issue_phase = read("references/issue-phase.md")

        for contents in (skill, options, issue_phase):
            self.assertIn("Withhold", contents)
            self.assertIn("blocker", contents.lower())

    def test_domain_handoff_remains_deferred_to_final_integration_issue(self) -> None:
        skill = read("SKILL.md")
        spec_template = read("references/spec-template.md")
        issue_template = read("references/issue-body-template.md")
        issue_phase = read("references/issue-phase.md")

        self.assertNotIn("knowledge_delta:", spec_template)
        self.assertNotIn("## Domain Knowledge Handoff", spec_template)
        for key in ("decisions:", "target_surfaces:", "evidence:"):
            self.assertIn(key, issue_template)
        for fixed_field in (
            "capture_outcome",
            "capture_mode",
            "memory_slice",
            "domain_operation",
        ):
            self.assertNotIn(fixed_field, spec_template)
        for contents in (skill, issue_template, issue_phase):
            self.assertIn("domain-memory", contents)
            self.assertIn("implementation-closeout", contents)
            self.assertIn("$project-memory", contents)
        self.assertIn("only on one final", skill)
        self.assertIn("Never generate a docs-only", issue_phase)

    def test_knowledge_delta_is_optional_data_and_capture_is_report_only(self) -> None:
        options = read("references/options.md")
        skill = read("SKILL.md")
        spec_phase = read("references/spec-phase.md")
        issue_phase = read("references/issue-phase.md")
        fixture = read("references/full-flow-dry-run.md")

        self.assertIn("optional `knowledge_delta` object", options)
        self.assertIn("Absence of `knowledge_delta`", options)
        self.assertIn("separate `planning_blockers`", options)
        self.assertIn("knowledge_delta:\n  decisions:", fixture)
        self.assertIn("planning_blockers: []", fixture)
        self.assertNotIn("  un" + "resolved:", fixture)
        for contents in (options, skill, spec_phase, issue_phase):
            self.assertIn("capture_outcome", contents)
            self.assertIn("report", contents.lower())
        for template in (
            read("references/spec-template.md"),
            read("references/issue-body-template.md"),
        ):
            self.assertNotRegex(template, r"(?m)^\s*capture_outcome:")
        self.assertNotIn("capture_outcome", read("references/spec-template.md"))
        self.assertIn(
            "capture_outcome=captured",
            read("references/issue-body-template.md"),
        )
        for value in (
            "knowledge_delta=" + "none",
            "knowledge_delta=" + "required",
        ):
            for path in DOC_PATHS:
                self.assertNotIn(value, path.read_text(encoding="utf-8"))

    def test_cross_spec_and_issue_dependencies_stay_separate(self) -> None:
        skill = read("SKILL.md")
        options = read("references/options.md")
        issue_phase = read("references/issue-phase.md")

        for contents in (skill, options, issue_phase):
            self.assertIn("cross-Spec", contents)
            self.assertIn("dependency_ids", contents)
        self.assertIn(
            "never copies those\nrefs into issue `dependency_ids`",
            read("references/spec-phase.md"),
        )

    def test_fixture_uses_proposed_refs_and_publication_order(self) -> None:
        fixture = read("references/full-flow-dry-run.md")
        options = read("references/options.md")

        self.assertIn("source_spec_ref: proposed-spec:account-settings-export", fixture)
        self.assertIn(
            "`proposed-spec:<project_slug>/<feature_slug>`",
            options,
        )
        self.assertIn("## Expected Publication Order", fixture)
        self.assertIn("`proposed-issue:<feature_slug>/<NN>`", options)
        self.assertIn("non-executable", fixture)
        self.assertIn("## Domain Knowledge Closeout", fixture)

    def test_multi_repo_proposed_refs_include_owning_repository(self) -> None:
        fixture = read("references/full-flow-dry-run.md")
        options = read("references/options.md")
        spec_phase = read("references/spec-phase.md")

        expected = (
            ("  api: ", "proposed-spec:account-platform/account-settings-export/api"),
            ("  web: ", "proposed-spec:account-platform/account-settings-export/web"),
            ("  api: ", "proposed-issue:account-platform/account-settings-export/api/01"),
            ("  web: ", "proposed-issue:account-platform/account-settings-export/web/01"),
            (
                "integration_source_spec_ref: ",
                "proposed-spec:account-platform/account-settings-export/web/integration",
            ),
            (
                "integration_issue_ref: ",
                "proposed-issue:account-platform/account-settings-export/web/integration/01",
            ),
        )
        refs = [ref for _, ref in expected]
        for prefix, ref in expected:
            self.assertEqual(fixture.count(f"{prefix}{ref}"), 1)
        self.assertEqual(len(set(refs)), len(refs))
        self.assertIn("<repository_slug>", options)
        self.assertIn("<repository_slug>", spec_phase)
        self.assertIn("<repository_slug>", read("references/issue-phase.md"))
        self.assertIn("coordination artifact", options)
        self.assertIn("/integration", options)
        self.assertNotIn(
            "proposed-issue:<project_slug>/<feature_slug>/<NN>",
            read("references/issue-phase.md"),
        )

    def test_every_multi_repo_bundle_uses_merge_gated_integration_partial(self) -> None:
        fixture = read("references/full-flow-dry-run.md")
        skill = read("SKILL.md")
        spec_phase = read("references/spec-phase.md")
        issue_phase = read("references/issue-phase.md")
        vertical = read("references/vertical-slices.md")

        for contents in (skill, spec_phase, issue_phase, vertical):
            self.assertIn("dedicated", contents)
            self.assertIn("integration partial", contents)
        self.assertIn("wait for every implementation partial to merge", skill)
        self.assertIn(
            "Feature Dependencies to cover every implementation partial",
            " ".join(issue_phase.split()),
        )
        self.assertIn("issue dependencies local", skill)
        self.assertIn("whether or not a knowledge delta", skill)
        self.assertIn("bounded repository/path change", skill)
        self.assertIn("exactly one dedicated repo-owned integration", issue_phase)
        self.assertIn("whether or not\n`knowledge_delta` exists", issue_phase)
        self.assertIn(
            "Feature Spec: <Feature Name> - Integration",
            spec_phase,
        )
        self.assertIn(
            "planning/features/<feature-slug>/integration/SPEC.md",
            spec_phase,
        )
        self.assertIn("Partial role: integration", spec_phase)
        self.assertIn(
            "does not require or create a coordination repository",
            " ".join(spec_phase.split()),
        )
        self.assertIn(
            "planning/features/<feature-slug>/integration/issues/<NN>-<slug>.md",
            issue_phase,
        )
        probe = section(
            fixture,
            "## Multi-Repository Identity Probe",
            "## Expected Pipeline",
        )
        self.assertIn(
            "integration_source_spec_ref: proposed-spec:account-platform/account-settings-export/web/integration",
            probe,
        )
        for upstream in (
            "proposed-spec:account-platform/account-settings-export/api",
            "proposed-spec:account-platform/account-settings-export/web",
        ):
            self.assertIn(f"upstream_feature_spec_ref: {upstream}", probe)
        self.assertIn("integration_issue_dependency_ids: none", probe)
        self.assertIn("no sibling-partial issue ID", probe)
        self.assertIn("remain mandatory without one", probe)
        self.assertIn("produce a real PR", probe)

    def test_applied_multi_repo_refs_remain_globally_unambiguous(self) -> None:
        fixture = read("references/full-flow-dry-run.md")
        spec_phase = read("references/spec-phase.md")
        options = read("references/options.md")
        projection = section(
            fixture,
            "### Expected Applied Multi-Repository Identity Projection",
            "## Expected Pipeline",
        )

        for ref in (
            "acme/account-api#241",
            "acme/account-web#118",
            "acme/account-web#119",
            "api/planning/features/account-settings-export/SPEC.md",
            "web/planning/features/account-settings-export/SPEC.md",
            "web/planning/features/account-settings-export/integration/SPEC.md",
        ):
            self.assertIn(ref, projection)
        self.assertIn("owner/repository#<number>", spec_phase)
        self.assertIn("<repository_slug>/<repo-relative-spec-path>", spec_phase)
        self.assertIn("same globally unambiguous refs", options)
        self.assertIn("Bare `#<number>`", projection)
        self.assertIn("does\nnot publish or enqueue", projection)
        self.assertIn("globally unambiguous durable ref", fixture)
        self.assertIn("same qualified refs", fixture)

    def test_existing_spec_requires_canonical_dependency_section(self) -> None:
        options = read("references/options.md")
        skill = read("SKILL.md")
        spec_phase = read("references/spec-phase.md")
        issue_phase = read("references/issue-phase.md")
        normalized = " ".join(spec_phase.split())

        self.assertIn("Existing Feature Specs", options)
        self.assertIn("Always run the canonical source-contract validation", skill)
        self.assertIn("return its original body and ref", skill)
        self.assertIn("do not switch\nmodes", skill)
        self.assertIn("`mode=issues-from-existing-spec`", spec_phase)
        self.assertIn("incompatible structured input", normalized)
        self.assertIn("Never interpret absence as an empty edge set", normalized)
        self.assertIn("do not draft or update the source", spec_phase)
        self.assertIn("return that exact source", spec_phase)
        self.assertIn("skip Apply Or Propose", spec_phase)
        self.assertIn("separate explicitly authorized Feature Spec update", spec_phase)
        self.assertIn("This step does not run for `mode=issues-from-existing-spec`", spec_phase)
        self.assertIn("exact existing section without adding, removing, or rewriting", spec_phase)
        self.assertIn("validate without modifying the body", spec_phase)
        self.assertNotIn("legacy Feature\nSpec without the section is read as", spec_phase)
        self.assertIn("exactly one `## Feature Dependencies` section", issue_phase)
        self.assertIn("even\n  for `mode=issues-from-existing-spec`", issue_phase)
        self.assertIn("reject absence, duplicates, extra\n  columns", issue_phase)

    def test_local_integration_completion_stays_in_integration_subtree(self) -> None:
        template = read("references/issue-body-template.md")
        issue_phase = read("references/issue-phase.md")
        fixture = read("references/full-flow-dry-run.md")

        expected = (
            "planning/features/<feature-slug>/integration/issues/done/"
            "<NN>-<slug>.md"
        )
        self.assertIn(expected, template)
        self.assertIn(
            "planning/features/<feature-slug>/integration/issues/done/",
            issue_phase,
        )
        self.assertIn(
            "local_integration_completion_path: "
            "web/planning/features/account-settings-export/integration/issues/done/"
            "01-prove-integrated-export.md",
            fixture,
        )

    def test_fixture_renders_complete_proposed_feature_spec(self) -> None:
        fixture = read("references/full-flow-dry-run.md")
        proposed_spec = section(
            fixture,
            "## Proposed Feature Spec",
            "## Representative Proposed Issue",
        )

        self.assertIn("# Feature Spec: Account Settings Export", proposed_spec)
        for heading in (
            "## Problem",
            "## Goals",
            "## Non-Goals",
            "## Requirements",
            "## Product / Repository Scope",
            "## Feature Dependencies",
            "## Acceptance Criteria",
            "## Validation Expectations",
        ):
            self.assertIn(heading, proposed_spec)
        dependencies = section(
            proposed_spec,
            "## Feature Dependencies",
            "## Acceptance Criteria",
        ).strip()
        self.assertEqual(
            "| upstream_feature_spec_ref | dependency_reason |\n| --- | --- |",
            dependencies,
        )
        self.assertNotIn("## Domain Knowledge Handoff", proposed_spec)
        self.assertNotIn("knowledge_delta:", proposed_spec)
        self.assertNotIn("workflow_state:", proposed_spec)
        self.assertNotIn("issue_type:", proposed_spec)
        for field in REMOVED_FIELDS:
            self.assertNotIn(field, proposed_spec)

    def test_fixture_renders_complete_final_integration_issue(self) -> None:
        fixture = read("references/full-flow-dry-run.md")
        final_issue = section(
            fixture,
            "## Final Proposed Integration Issue",
            "## Multi-Repository Identity Probe",
        )

        self.assertIn("proposed-issue:account-settings-export/02", final_issue)
        self.assertEqual(final_issue.count("## Execution Contract"), 1)
        contract = section(final_issue, "## Execution Contract", "## Goal")
        self.assertEqual(
            [
                "source_spec_ref",
                "feature_slug",
                "affected_repositories",
                "allowed_paths",
                "target_branch_name",
                "dependency_ids",
            ],
            table_fields(contract),
        )
        self.assertIn("| `dependency_ids` | `01` |", final_issue)
        self.assertIn("## Non-Goals", final_issue)
        self.assertIn("## Domain Knowledge Closeout", final_issue)
        self.assertIn("memory_slice=domain-memory", final_issue)
        self.assertIn("domain_operation=implementation-closeout", final_issue)
        self.assertIn("knowledge_delta:\n  decisions:", final_issue)
        self.assertIn("capture_outcome=captured", final_issue)
        self.assertIn("required named target", final_issue)
        self.assertIn("complete documentation diff", final_issue)
        self.assertIn("`deferred` or `no-durable-change`", final_issue)
        self.assertIn("prove the\nintegrated behavior", final_issue)

        ordinary_issue = section(
            fixture,
            "## Representative Proposed Issue",
            "## Final Proposed Integration Issue",
        )
        self.assertIn("## Non-Goals", ordinary_issue)
        self.assertNotIn("## Domain Knowledge Closeout", ordinary_issue)

    def test_spec_only_reports_delta_without_persisting_or_enabling_app(self) -> None:
        skill = " ".join(read("SKILL.md").split())
        spec_phase = " ".join(read("references/spec-phase.md").split())
        spec_template = read("references/spec-template.md")

        for contents in (skill, spec_phase):
            self.assertIn("exact delta as non-persisted report data", contents)
            self.assertIn("not App-executable until", contents)
        self.assertNotIn("knowledge_delta:", spec_template)
        self.assertNotIn("## Domain Knowledge Handoff", spec_template)

    def test_existing_spec_accepts_delta_only_as_explicit_invocation_data(self) -> None:
        skill = " ".join(read("SKILL.md").split())
        spec_phase = " ".join(read("references/spec-phase.md").split())
        issue_phase = " ".join(read("references/issue-phase.md").split())

        for contents in (skill, spec_phase, issue_phase):
            self.assertIn("explicit accepted invocation data", contents)
        self.assertIn("never infer it from the Feature Spec", skill)
        self.assertIn("Reject a source containing `knowledge_delta`", spec_phase)
        self.assertIn("Never infer it from Feature Spec prose", issue_phase)

    def test_knowledge_targets_are_contained_by_final_issue_scope(self) -> None:
        skill = " ".join(read("SKILL.md").split())
        options = " ".join(read("references/options.md").split())
        spec_phase = " ".join(read("references/spec-phase.md").split())
        issue_phase = " ".join(read("references/issue-phase.md").split())
        template = " ".join(read("references/issue-body-template.md").split())

        for contents in (skill, options, issue_phase, template):
            self.assertIn("`affected_repositories`", contents)
            self.assertIn("`allowed_paths`", contents)
        self.assertIn("unchanged Feature Spec repository/path scope", options)
        self.assertIn("reject the delta instead of widening", skill)
        self.assertIn("never widen the immutable source", spec_phase)
        self.assertIn("Never rely on Project Memory to write outside", issue_phase)

        fixture = read("references/full-flow-dry-run.md")
        final_issue = section(
            fixture,
            "## Final Proposed Integration Issue",
            "## Multi-Repository Identity Probe",
        )
        contract = section(final_issue, "## Execution Contract", "## Goal")
        allowed_match = re.search(
            r"^\| `allowed_paths` \| (.+) \|$", contract, re.MULTILINE
        )
        self.assertIsNotNone(allowed_match)
        allowed_paths = [
            value.strip().strip("`")
            for value in allowed_match.group(1).split(",")
        ]
        closeout = section(
            final_issue, "## Domain Knowledge Closeout", "## Completion"
        )
        target_block = closeout.split("  target_surfaces:", 1)[1].split(
            "  evidence:", 1
        )[0]
        targets = re.findall(
            r"^    - current-repository/(.+)$", target_block, re.MULTILINE
        )
        self.assertTrue(targets)
        for target in targets:
            self.assertTrue(
                any(
                    target == scope
                    or (scope.endswith("/**") and target.startswith(scope[:-3]))
                    for scope in allowed_paths
                ),
                f"{target} is outside final issue allowed_paths",
            )
        self.assertIn(
            "| `affected_repositories` | `current-repository` |", contract
        )

        planning_delta = section(
            fixture, "## Resolved Run", "## Proposed Feature Spec Result"
        ).split("knowledge_delta:\n", 1)[1].split("planning_blockers:", 1)[0]
        persisted_delta = closeout.split(
            "knowledge_delta:\n", 1
        )[1].split("- Closeout proof:", 1)[0]
        normalize_payload = lambda payload: "\n".join(
            line.strip() for line in payload.strip().splitlines()
        )
        self.assertEqual(
            normalize_payload(planning_delta),
            normalize_payload(persisted_delta),
        )

    def test_knowledge_owner_uses_executable_remaining_graph_rule(self) -> None:
        skill = " ".join(read("SKILL.md").split())
        issue_phase = " ".join(read("references/issue-phase.md").split())
        vertical = " ".join(read("references/vertical-slices.md").split())

        self.assertIn("exclude that owner and its own `dependency_ids`", skill)
        self.assertIn(
            "remove that owner and its outgoing `dependency_ids`",
            issue_phase,
        )
        self.assertIn("nodes with no dependents in the remaining", issue_phase)
        self.assertIn("another issue depends on the owner", issue_phase)
        self.assertIn("owner-excluded terminal algorithm", issue_phase)
        self.assertIn("owner-excluded terminal rule", vertical)
        self.assertIn("Freeze stable IDs only after", issue_phase)
        self.assertIn("topologically last", issue_phase)
        self.assertIn("append a new owner", issue_phase)
        self.assertIn("strictly earlier generated ID", issue_phase)

        template = " ".join(read("references/issue-body-template.md").split())
        for contents in (issue_phase, template):
            self.assertIn("capture_outcome=captured", contents)
            self.assertIn("required named target", contents)
            self.assertIn("deferred", contents)
            self.assertIn("no-durable-change", contents)
            self.assertIn("block", contents)
            self.assertIn("contradicted", contents)
            self.assertIn("owner decision", contents)

    def test_spec_only_multi_repo_delta_targets_integration_partial(self) -> None:
        spec_phase = " ".join(read("references/spec-phase.md").split())

        self.assertIn(
            "future_closeout_issue_source_spec_ref: <source_spec_ref>", spec_phase
        )
        self.assertIn(
            "future_closeout_issue_source_spec_ref: <integration_source_spec_ref>",
            spec_phase,
        )
        self.assertIn("dedicated integration partial's ref", spec_phase)
        self.assertIn("never the parent or an ordinary partial ref", spec_phase)
        self.assertIn("not a task ref or selectable field", spec_phase)
        self.assertNotIn("final-implementation-task-from", spec_phase)

    def test_spec_only_delta_cannot_be_lost_between_invocations(self) -> None:
        skill = " ".join(read("SKILL.md").split())
        options = " ".join(read("references/options.md").split())
        spec_phase = " ".join(read("references/spec-phase.md").split())
        spec_template = " ".join(read("references/spec-template.md").split())
        fixture = read("references/full-flow-dry-run.md")

        for contents in (skill, options, spec_phase, spec_template):
            self.assertIn("spec-only", contents)
            self.assertIn("nonempty `knowledge_delta`", contents)
            self.assertIn("withhold", contents)
            self.assertIn("full-flow", contents)
        self.assertIn("Do not silently downgrade `write_mode`", spec_phase)
        self.assertIn("no durable source exists", spec_phase)
        self.assertIn("no durable Feature Spec source exists", spec_template)
        self.assertIn("must never consume the preview", spec_template)
        self.assertIn("no final issue ref exists", skill)
        self.assertIn("future_closeout_issue_source_spec_ref", skill)
        self.assertIn("## Spec-Only Delta Persistence Probe", fixture)
        self.assertIn("durable_source_created: false", fixture)
        self.assertIn("issues_from_existing_spec: impossible", fixture)

    def test_local_issue_scope_covers_move_and_final_head_sequence(self) -> None:
        issue_phase = " ".join(read("references/issue-phase.md").split())
        template = " ".join(read("references/issue-body-template.md").split())
        fixture = read("references/full-flow-dry-run.md")

        for token in (
            "tracker-owning repository",
            "exact active path",
            "`done/` destination",
            "inside that affected Git repository",
            "never invent a tracker-owning repository",
        ):
            self.assertIn(token, issue_phase)
        self.assertIn("Commit and push the move", template)
        self.assertIn("rerun every final gate", template)
        self.assertIn("prepared, not globally completed", template)
        self.assertIn(
            "web/planning/features/account-settings-export/integration/issues/"
            "01-prove-integrated-export.md",
            fixture,
        )
        self.assertIn(
            "web/planning/features/account-settings-export/integration/issues/done/"
            "01-prove-integrated-export.md",
            fixture,
        )
        self.assertIn(
            "web/src/account-settings/export-integration/**",
            fixture,
        )

    def test_github_completion_is_always_armed_for_app_delivery(self) -> None:
        template = " ".join(
            read("references/issue-body-template.md").split()
        )

        self.assertIn("closing keyword", template)
        self.assertIn("owner/repository#<number>", template)
        self.assertIn("repository's default branch", template)
        self.assertIn("withhold the App-compatible issue or bundle as blocked", template)
        self.assertIn("a non-closing link is not completion proof", template)

    def test_hardening_keeps_only_the_final_stable_pass(self) -> None:
        skill = " ".join(read("SKILL.md").split())
        issue_phase = " ".join(read("references/issue-phase.md").split())
        template = read("references/issue-body-template.md")
        fixture = read("references/full-flow-dry-run.md")
        provenance = (
            "Plan-hardening: final stable $plan-harder issue-hardening pass "
            "completed for this issue."
        )

        self.assertIn("one or more times per generated issue", skill)
        self.assertIn("after vertical boundaries", skill)
        self.assertIn("at least once for each candidate issue", issue_phase)
        self.assertIn("persist only the final stable result", issue_phase)
        self.assertEqual(template.count(provenance), 1)
        self.assertEqual(fixture.count(provenance), 2)

    def test_integration_partial_uses_a_distinct_derived_branch(self) -> None:
        skill = " ".join(read("SKILL.md").split())
        options = " ".join(read("references/options.md").split())
        issue_phase = " ".join(read("references/issue-phase.md").split())
        fixture = read("references/full-flow-dry-run.md")

        self.assertIn("feature/<feature_slug>-integration", skill)
        self.assertIn("appending `-integration` to the resolved ordinary partial branch", skill)
        self.assertIn("never reuse the ordinary partial's branch", skill)
        self.assertIn("Branch sharing is per Feature Spec", options)
        self.assertIn("distinct derived branch", options)
        self.assertIn("<ordinary_target_branch_name>-integration", options)
        self.assertIn("Never reuse the ordinary partial's branch", issue_phase)
        self.assertIn(
            "integration_target_branch: feature/account-settings-export-integration",
            fixture,
        )
        self.assertIn("web: feature/account-settings-export", fixture)

    def test_produced_bundle_has_unique_repository_branch_owners(self) -> None:
        skill = " ".join(read("SKILL.md").split())
        options = " ".join(read("references/options.md").split())
        spec_phase = " ".join(read("references/spec-phase.md").split())

        for contents in (skill, options, spec_phase):
            self.assertIn("(affected_repository, target_branch_name)", contents)
            self.assertIn("exactly one Feature Spec owner", contents)
            self.assertIn("different repositories", contents)
            self.assertIn("paths are disjoint", contents)
            self.assertIn("immutable existing source", contents)
        self.assertIn("stop instead of renaming", skill)
        self.assertIn("stop rather than rename", options)

    def test_metadata_remains_manual_only_and_matches_workflow(self) -> None:
        metadata = read("agents/openai.yaml")

        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertIn("choose a mode and apply or propose", metadata)
        self.assertIn("defer any knowledge delta", metadata)

    def test_all_reference_names_are_lowercase(self) -> None:
        for path in (SKILL_ROOT / "references").glob("*.md"):
            self.assertEqual(path.name, path.name.lower())

    def test_docs_do_not_publish_machine_local_paths(self) -> None:
        for path in DOC_PATHS:
            contents = path.read_text(encoding="utf-8")
            self.assertNotRegex(contents, r"/Users/[A-Za-z0-9._-]+/")
            self.assertNotRegex(contents, r"/home/[A-Za-z0-9._-]+/")


if __name__ == "__main__":
    unittest.main()
