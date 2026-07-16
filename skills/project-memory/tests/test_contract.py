from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]


class ProjectMemoryContractTests(unittest.TestCase):
    def test_option_registry_has_only_runtime_controls(self) -> None:
        options = (SKILL_ROOT / "references" / "options.md").read_text(
            encoding="utf-8"
        )
        registry = options.split("## Registry", 1)[1].split("## Derived Context", 1)[0]
        fields = re.findall(r"^\| `([a-z_]+)` \|", registry, flags=re.MULTILINE)

        self.assertEqual(
            fields,
            ["memory_slice", "domain_operation", "write_mode", "capture_mode"],
        )
        self.assertIn("not an input option", options)
        self.assertIn("optional input data", options)
        self.assertIn("closeout result", options)

    def test_implementation_closeout_requires_complete_capture(self) -> None:
        options = " ".join(
            (SKILL_ROOT / "references" / "options.md")
            .read_text(encoding="utf-8")
            .split()
        )
        modeling = " ".join(
            (SKILL_ROOT / "references" / "domain-modeling.md")
            .read_text(encoding="utf-8")
            .split()
        )
        skill = " ".join((SKILL_ROOT / "SKILL.md").read_text().split())

        for contents in (options, modeling, skill):
            self.assertIn("every", contents)
            self.assertIn("required named target", contents)
            self.assertIn("capture_outcome=deferred", contents)
            self.assertIn("no-durable-change", contents)
        self.assertIn("One successful destination never masks", options)
        self.assertIn("complete documentation diff is verified", modeling)
        for contents in (options, modeling, skill):
            self.assertIn("contradict", contents)
            self.assertIn("deferred", contents)
            self.assertIn("owner decision", contents)

    def test_execution_context_uses_deterministic_precedence(self) -> None:
        options = (SKILL_ROOT / "references" / "options.md").read_text(
            encoding="utf-8"
        )
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        setup = (SKILL_ROOT / "references" / "setup-workflow.md").read_text(
            encoding="utf-8"
        )
        derived = options.split("## Derived Context", 1)[1].split(
            "## Domain Data And Results", 1
        )[0]

        self.assertIn("mutually exclusive rules in order", derived)
        positions = [
            derived.index(f"{index}. `{value}`")
            for index, value in enumerate(
                (
                    "orchestrator-workspace",
                    "fresh-setup",
                    "existing-project-bootstrap",
                    "current-project",
                ),
                start=1,
            )
        ]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("wins even when root memory files are\n   missing", derived)
        self.assertIn("Existing source code alone does not", derived)
        self.assertIn("Project Memory\n   identity/routing already exists", derived)
        self.assertIn("exact ordered precedence in\n`references/options.md`", skill)
        self.assertNotIn("selected files are missing", skill)
        for value in (
            "orchestrator-workspace",
            "fresh-setup",
            "existing-project-bootstrap",
            "current-project",
        ):
            self.assertIn(f"`{value}`", setup)
        self.assertIn("execution context", setup)
        self.assertNotIn("- setup flow;", setup)
        self.assertIn("`workflow-state-mapping`", setup)
        self.assertNotIn("triage-state-mapping", setup)
        self.assertIn("workflow-state mapping", setup)

    def test_proposed_ref_terminology_has_no_draft_alias(self) -> None:
        for name in (
            "issue-tracker-github.md",
            "issue-tracker-local.md",
            "tracker-publishing.md",
        ):
            text = (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")
            self.assertNotIn("draft ref", text.lower())
            self.assertIn("proposed", text.lower())

        publishing = (
            SKILL_ROOT / "references" / "tracker-publishing.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "proposed-spec:<project-slug>/<feature-slug>/<repository-slug>",
            publishing,
        )
        self.assertIn(
            "proposed-spec:<project-slug>/<feature-slug>/<repository-slug>/integration",
            publishing,
        )

    def test_integration_partial_has_distinct_applied_backend_identity(self) -> None:
        github = (
            SKILL_ROOT / "references" / "issue-tracker-github.md"
        ).read_text(encoding="utf-8")
        local = (
            SKILL_ROOT / "references" / "issue-tracker-local.md"
        ).read_text(encoding="utf-8")
        publishing = (
            SKILL_ROOT / "references" / "tracker-publishing.md"
        ).read_text(encoding="utf-8")
        github_normalized = " ".join(github.split())
        local_normalized = " ".join(local.split())

        self.assertIn("Feature Spec: <Feature Name> - Integration", github)
        self.assertIn("Partial role: integration", github)
        self.assertIn("its own hosted issue number", github_normalized)
        self.assertIn(
            "planning/features/<feature-slug>/integration/SPEC.md",
            local,
        )
        self.assertIn(
            "planning/features/<feature-slug>/integration/issues/<NN>-<slug>.md",
            local,
        )
        self.assertIn("does not require a coordination", local_normalized)
        self.assertIn("#<integration-spec-number>", publishing)
        self.assertIn("owner/repository#<integration-spec-number>", publishing)
        self.assertIn(
            "<repository-slug>/planning/features/<feature-slug>/integration/SPEC.md",
            publishing,
        )

    def test_applied_multi_repo_refs_are_globally_unambiguous(self) -> None:
        github = (
            SKILL_ROOT / "references" / "issue-tracker-github.md"
        ).read_text(encoding="utf-8")
        local = (
            SKILL_ROOT / "references" / "issue-tracker-local.md"
        ).read_text(encoding="utf-8")
        publishing = (
            SKILL_ROOT / "references" / "tracker-publishing.md"
        ).read_text(encoding="utf-8")

        for text in (github, publishing):
            self.assertIn("owner/repository#<spec-number>", text)
            self.assertIn("canonical hosted URL", text)
        for text in (local, publishing):
            self.assertIn("<repository-slug>/<repo-relative-spec-path>", text)
            self.assertIn("Feature Dependencies", text)
        self.assertIn("Bare issue numbers", publishing)
        self.assertIn("bare repo-relative paths", publishing)

    def test_retired_tracker_policy_is_absent_from_project_memory_docs(self) -> None:
        markdown = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(SKILL_ROOT.rglob("*.md"))
        )
        retired = (
            "change_" + "delivery_target",
            "effective_" + "target",
            "no_mutation_" + "override",
            "no_mutation_" + "output",
            "local_" + "mirror",
            "delivery-" + "target",
            "Delivery " + "Defaults",
        )

        for field in retired:
            with self.subTest(field=field):
                self.assertNotIn(field, markdown)

    def test_tracker_publication_branches_only_on_write_mode(self) -> None:
        publishing = (
            SKILL_ROOT / "references" / "tracker-publishing.md"
        ).read_text(encoding="utf-8")

        self.assertIn("`write_mode`", publishing)
        self.assertIn("| `apply` |", publishing)
        self.assertIn("| `propose` |", publishing)
        self.assertIn("without mutating GitHub or returning executable commands", publishing)

        for tracker in ("github", "local"):
            text = (
                SKILL_ROOT / "references" / f"issue-tracker-{tracker}.md"
            ).read_text(encoding="utf-8")
            configuration = text.split("## Configuration", 1)[1].split("## ", 1)[0]
            keys = re.findall(r"^\| `([a-z_]+)` \|", configuration, flags=re.MULTILINE)
            self.assertEqual(keys, ["tracker_backend"])
            self.assertIn("`write_mode=apply`", text)
            self.assertIn("`write_mode=propose`", text)

    def test_generated_configuration_uses_config_directory(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        setup = (SKILL_ROOT / "references" / "setup-workflow.md").read_text(
            encoding="utf-8"
        )

        for relative_path in (
            "project-memory/config/issue-tracker.md",
            "project-memory/config/project-layout.md",
            "project-memory/config/triage-labels.md",
            "project-memory/config/domain.md",
        ):
            self.assertIn(relative_path, skill)
            self.assertIn(relative_path, setup)

    def test_project_memory_owns_issue_type_and_workflow_state_registry(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        labels = (SKILL_ROOT / "references" / "triage-labels.md").read_text(
            encoding="utf-8"
        )
        github = (SKILL_ROOT / "references" / "issue-tracker-github.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("sole reusable registry", skill)
        self.assertIn("sole reusable owner", labels)
        self.assertIn("project-memory/config/triage-labels.md", labels)
        for value in (
            "`bug`",
            "`feature`",
            "`task`",
            "`needs-triage`",
            "`needs-info`",
            "`ready-for-agent`",
            "`ready-for-human`",
            "`wontfix`",
        ):
            self.assertIn(value, labels)

        self.assertIn(
            "Require exactly one `issue_type` and one `workflow_state`", labels
        )
        self.assertIn("`proposed-spec:`", labels)
        self.assertIn("only from\n`references/triage-labels.md`", github)
        self.assertIn("does not repeat\nthat registry", github)
        self.assertNotIn("default GitHub issue types", github)
        self.assertNotIn("default GitHub workflow-state labels", github)
        for canonical_value in (
            "bug",
            "feature",
            "task",
            "needs-triage",
            "needs-info",
            "ready-for-agent",
            "ready-for-human",
            "wontfix",
        ):
            with self.subTest(canonical_value=canonical_value):
                self.assertNotIn(f"`{canonical_value}`", github)

        local = (SKILL_ROOT / "references" / "issue-tracker-local.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("canonical `bug`, `feature`, or `task`", local)
        self.assertEqual(local.count("loaded from `triage-labels.md`"), 2)

        plan_feature = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (REPO_ROOT / "skills" / "plan-feature").rglob("*.md")
        )
        self.assertIn("project-memory/config/triage-labels.md", plan_feature)
        self.assertFalse((REPO_ROOT / "skills" / "triage").exists())

        for options_path in REPO_ROOT.glob("skills/**/references/options.md"):
            options = options_path.read_text(encoding="utf-8")
            with self.subTest(options_path=options_path):
                self.assertNotRegex(
                    options, r"(?m)^\| `(?:issue_type|workflow_state)` \|"
                )

    def test_local_integration_completion_uses_matching_subtree(self) -> None:
        local = (SKILL_ROOT / "references" / "issue-tracker-local.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "planning/features/<feature-slug>/integration/issues/done/"
            "<NN>-<slug>.md",
            local,
        )
        self.assertIn("Derive the completion target from the owning issue subtree", local)
        self.assertIn(
            "never move an\nintegration issue into the ordinary feature's "
            "`issues/done/` directory",
            local,
        )
        normalized = " ".join(local.split())
        self.assertIn("tracker file in `affected_repositories`", normalized)
        self.assertIn("exact active issue path", normalized)
        self.assertIn("exact derived `done/` path", normalized)
        self.assertIn("inside that repository", normalized)
        self.assertIn("non-App-executable", normalized)
        self.assertIn("Commit and push the move", normalized)
        self.assertIn("rerun final validation, review, and CI", normalized)
        self.assertIn("prepared rather than globally completed", normalized)

    def test_project_layout_is_owned_separately_from_tracker_routing(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        options = (SKILL_ROOT / "references" / "options.md").read_text(
            encoding="utf-8"
        )
        layout = (SKILL_ROOT / "references" / "project-layout.md").read_text(
            encoding="utf-8"
        )
        setup = (SKILL_ROOT / "references" / "setup-workflow.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("`project-layout`", options)
        self.assertIn("`repository_layout`", skill)
        self.assertIn("`repository_layout`", setup)
        for value in ("`single-repository`", "`monorepo`", "`multi-repository-workspace`"):
            self.assertIn(value, layout)
            self.assertIn(value, skill)
        self.assertIn("Keep `project-layout.md` limited to `repository_layout`", setup)
        self.assertIn("`tracker_backend`", skill)
        self.assertIn("Keep tracker routing in `project-memory/config/issue-tracker.md`", layout)

    def test_runtime_contracts_do_not_reference_legacy_agents_directory(self) -> None:
        roots = [
            REPO_ROOT / "AGENTS.md",
            REPO_ROOT / "skills" / "project-memory",
            REPO_ROOT / "skills" / "plan-feature",
            REPO_ROOT / "skills" / "grill-me-with-context",
            REPO_ROOT / "skills" / "improve-codebase-architecture",
        ]
        candidates: list[Path] = []
        for root in roots:
            if root.is_file():
                candidates.append(root)
                continue
            candidates.extend(
                path
                for path in root.rglob("*")
                if path.is_file() and path.suffix in {".md", ".py", ".yaml"}
            )

        legacy_path = "project-memory/" + "agents/"
        stale = [
            str(path.relative_to(REPO_ROOT))
            for path in candidates
            if legacy_path in path.read_text(encoding="utf-8")
        ]
        self.assertEqual(stale, [])

    def test_skill_metadata_remains_in_agents_directory(self) -> None:
        self.assertTrue((SKILL_ROOT / "agents" / "openai.yaml").is_file())


if __name__ == "__main__":
    unittest.main()
