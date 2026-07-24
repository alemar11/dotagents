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
                    "fresh-setup",
                    "existing-project-bootstrap",
                    "current-project",
                ),
                start=1,
            )
        ]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("no established Project Memory surface exists", derived)
        self.assertIn("Existing source code alone does not", derived)
        self.assertIn("Project Memory\n   identity/routing already exists", derived)
        self.assertIn("exact ordered precedence in\n`references/options.md`", skill)
        self.assertNotIn("selected files are missing", skill)
        for value in ("fresh-setup", "existing-project-bootstrap", "current-project"):
            self.assertIn(f"`{value}`", setup)
        self.assertIn("execution context", setup)
        self.assertNotIn("- setup flow;", setup)
        self.assertIn("`workflow-state-mapping`", setup)
        self.assertIn("`artifact-marker-mapping`", setup)
        self.assertNotIn("triage-state-mapping", setup)
        self.assertIn("artifact-marker mapping", setup)
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
            "proposed-spec:<feature-id>/<repository-key>",
            publishing,
        )
        self.assertNotIn("/<repository-slug>/integration", publishing)

    def test_combined_proof_reuses_ordinary_feature_spec_identity(self) -> None:
        github = (
            SKILL_ROOT / "references" / "issue-tracker-github.md"
        ).read_text(encoding="utf-8")
        local = (
            SKILL_ROOT / "references" / "issue-tracker-local.md"
        ).read_text(encoding="utf-8")
        publishing = (
            SKILL_ROOT / "references" / "tracker-publishing.md"
        ).read_text(encoding="utf-8")
        combined = "\n".join((github, local, publishing))
        self.assertIn("Feature Spec: <Feature Name>", github)
        self.assertIn("planning/features/<feature-slug>/SPEC.md", local)
        self.assertNotIn("Feature Spec: <Feature Name> - Integration", combined)
        self.assertNotIn("Partial role: integration", combined)
        self.assertNotIn("planning/features/<feature-slug>/integration/", combined)

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
            self.assertIn(
                "<feature-id>--<repository-key>/planning/features/<feature-slug>/SPEC.md",
                text,
            )
            self.assertIn("Feature Dependencies", text)
        self.assertIn("Bare issue numbers", publishing)
        self.assertIn("bare repo-relative paths", publishing)

    def test_runtime_docs_have_no_retired_coordination_tree(self) -> None:
        roots = (
            REPO_ROOT / "AGENTS.md",
            REPO_ROOT / "skills" / "project-memory",
            REPO_ROOT / "skills" / "plan-feature",
        )
        candidates: list[Path] = []
        for root in roots:
            if root.is_file():
                candidates.append(root)
                continue
            candidates.extend(
                path
                for path in root.rglob("*")
                if path.is_file() and path.suffix in {".md", ".yaml"}
            )

        normalized = {
            path: " ".join(path.read_text(encoding="utf-8").split())
            for path in candidates
        }

        retired = (
            "orchestration/" + "<project",
            "project or feature " + "folders",
            "orchestration runtime " + "config files",
            "local project " + "folders",
            "repo pointer " + "sheets",
            "configured " + "equivalent",
            "configured workspace " + "equivalent",
            "configured local " + "conventions",
            "configured local " + "path",
            "unqualified configured " + "path",
            "configured `planning/" + "features",
            "planning/features/" + "<feature>/",
            "repo-relative-spec-" + "path",
            "repo_relative_spec_" + "path",
            "`/integration/SPEC.md` " + "child",
            "resolved Feature Spec " + "path",
            "resolved feature " + "directory",
            "<repository_" + "slug>/planning",
            "distinct `integration/" + "SPEC.md`",
            "orchestrator workspace "
            + "project, repository, and integration-gate documents",
        )
        stale = {
            token: [
                str(path.relative_to(REPO_ROOT))
                for path in candidates
                if token in normalized[path]
            ]
            for token in retired
        }
        self.assertEqual(stale, {token: [] for token in retired})

        publishing = (
            SKILL_ROOT / "references" / "tracker-publishing.md"
        ).read_text(encoding="utf-8")
        setup = (SKILL_ROOT / "references" / "setup-workflow.md").read_text(
            encoding="utf-8"
        )
        spec_phase = (
            REPO_ROOT
            / "skills"
            / "plan-feature"
            / "references"
            / "spec-phase.md"
        ).read_text(encoding="utf-8")

        self.assertIn("inside each owning repository", publishing)
        self.assertIn(
            "source_spec_ref=planning/features/<feature-slug>/SPEC.md",
            publishing,
        )
        self.assertIn("run setup\nindependently in each selected repository", setup)
        self.assertIn("candidate local Git roots separately", spec_phase)
        self.assertIn("repo-owned linked Feature Specs", spec_phase)
        self.assertIn(
            "`planning/features/<feature-slug>/SPEC.md` inside that repository",
            spec_phase,
        )
        local_apply = spec_phase.split("- `write_mode=apply`, local:", 1)[1].split(
            "- `write_mode=propose`", 1
        )[0]
        for path in (
            "planning/features/<feature-slug>/SPEC.md",
            "<feature-id>--<repository-key>/planning/features/<feature-slug>/SPEC.md",
        ):
            self.assertIn(path, local_apply)
        self.assertNotIn("/integration/", local_apply)

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
            "project-memory/config/triage-labels.md",
        ):
            self.assertIn(relative_path, skill)
            self.assertIn(relative_path, setup)
        self.assertNotIn("project-memory/config/project-layout.md", skill)
        self.assertNotIn("project-memory/config/project-layout.md", setup)

        retired_domain_config = "project-memory/config/" + "domain.md"
        self.assertNotIn(retired_domain_config, skill)
        self.assertNotIn(retired_domain_config, setup)

    def test_context_routing_uses_one_root_entrypoint(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        domain = (SKILL_ROOT / "references" / "domain.md").read_text(
            encoding="utf-8"
        )
        modeling = (SKILL_ROOT / "references" / "domain-modeling.md").read_text(
            encoding="utf-8"
        )
        setup = (SKILL_ROOT / "references" / "setup-workflow.md").read_text(
            encoding="utf-8"
        )
        translation = (SKILL_ROOT / "references" / "translation.md").read_text(
            encoding="utf-8"
        )
        domain_normalized = " ".join(domain.split())

        self.assertIn(
            "root `CONTEXT.md` is the single entry point", domain_normalized
        )
        self.assertIn("supplies candidate local Git roots separately", domain_normalized)
        self.assertIn("## Scoped Contexts", domain)
        self.assertIn("| Scope | Owned paths | Context |", domain)
        self.assertIn("Multiple non-overlapping matches are valid", domain)
        self.assertIn("optional context path", domain)
        self.assertIn("use `—` otherwise", domain_normalized)
        self.assertIn("Rows must be non-overlapping", domain)
        retired_overlap_rule = "explicit " + "precedence"
        self.assertNotIn(retired_overlap_rule, domain)
        self.assertNotIn("## Repository Registry", domain)
        self.assertIn("Explicit user scope or a durable linked Feature Spec Set", domain_normalized)
        self.assertIn("Use exactly one `project-memory/` directory", domain)
        self.assertIn("must not create\n  a nested `project-memory/` directory", domain)
        self.assertIn("read its `CONTEXT.md` first", modeling)
        self.assertIn("Standard Ambiguity Questions", setup)
        for contents in (skill, domain, modeling, setup):
            normalized = " ".join(contents.split())
            self.assertIn("authorized", normalized)
            self.assertIn("setup/bootstrap", normalized)
            self.assertIn("root `CONTEXT.md`", normalized)
        self.assertIn(
            "During authorized domain setup/bootstrap, always create or update it",
            " ".join(setup.split()),
        )
        for contents in (skill, setup):
            normalized = " ".join(contents.split())
            self.assertIn("additional Git repository", normalized)
            self.assertIn("outside that scope remain untouched", normalized)
        retired_setup_terms = (
            "`context-" + "seed`",
            "`seed-" + "context`",
            "`routing-" + "only`",
        )
        for retired in retired_setup_terms:
            self.assertNotIn(retired, setup)
        self.assertIn("minimal entry point", " ".join(setup.split()))
        self.assertIn("scoped monorepo context", translation)

        plan_options = (
            REPO_ROOT / "skills" / "plan-feature" / "references" / "options.md"
        ).read_text(encoding="utf-8")
        spec_phase = (
            REPO_ROOT
            / "skills"
            / "plan-feature"
            / "references"
            / "spec-phase.md"
        ).read_text(encoding="utf-8")
        retired_context_field = "`context_" + "file`"
        self.assertNotIn("`context_files`", plan_options)
        self.assertIn("outside the option registry", plan_options)
        normalized = " ".join(spec_phase.split())
        self.assertIn("`context_files`", spec_phase)
        self.assertNotIn(retired_context_field, spec_phase)
        self.assertIn("applicable available", normalized)
        self.assertIn("root", normalized)
        self.assertIn("scoped context", normalized)
        plan_skill = (
            REPO_ROOT / "skills" / "plan-feature" / "SKILL.md"
        ).read_text(encoding="utf-8")
        for contents in (plan_skill, spec_phase):
            normalized = " ".join(contents.split()).lower()
            self.assertIn("read every available matched context before drafting", normalized)

    def test_setup_questions_are_first_time_user_facing(self) -> None:
        questions = (
            SKILL_ROOT / "references" / "setup-questions.md"
        ).read_text(encoding="utf-8")
        setup = (SKILL_ROOT / "references" / "setup-workflow.md").read_text(
            encoding="utf-8"
        )
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        headings = re.findall(r"^## (.+)$", questions, flags=re.MULTILINE)
        self.assertEqual(
            headings,
            [
                "Setup Target",
                "Issue Location",
                "Separate Project Contexts",
                "Overlapping Project Ownership",
                "Repository Rule Ownership",
                "Localization Conventions",
                "Artifact-Marker Mapping",
                "Issue-Type Mapping",
                "Workflow-State Mapping",
                "Questions Setup Must Not Ask",
            ],
        )
        self.assertIn("Normally ask no questions", questions)
        self.assertIn("ask one question at a time", questions)
        self.assertIn("Never ask the user to judge evidence sufficiency", questions)
        self.assertIn(
            "Root\n`CONTEXT.md` creation remains mandatory",
            questions,
        )
        self.assertIn(
            "[setup-questions.md](setup-questions.md) and use exactly one",
            " ".join(setup.split()),
        )
        self.assertIn(
            "[setup-questions.md](references/setup-questions.md)",
            skill,
        )
        loading_matrix = skill.split("## Reference Loading Matrix", 1)[1].split(
            "## Workflow", 1
        )[0]
        for row_name in ("Domain setup/bootstrap", "Translation"):
            row = next(
                line
                for line in loading_matrix.splitlines()
                if line.startswith(f"| {row_name} |")
            )
            self.assertIn("`setup-workflow.md`", row)
        for reference_name in (
            "translation.md",
            "triage-labels.md",
        ):
            contents = (SKILL_ROOT / "references" / reference_name).read_text(
                encoding="utf-8"
            )
            self.assertIn("[setup-questions.md](setup-questions.md)", contents)

        prompt_text = "\n".join(
            line[2:] for line in questions.splitlines() if line.startswith("> ")
        ).lower()
        for internal_term in (
            "memory-owning root",
            "scoped route",
            "tracker_backend",
            "translation memory",
            "authoritative scope",
            "evidence sufficiency",
        ):
            self.assertNotIn(internal_term, prompt_text)

        retired_setup_terms = (
            "context-" + "seed",
            "seed-" + "context",
            "routing-" + "only",
        )
        for retired in retired_setup_terms:
            self.assertNotIn(retired, questions)

        for prompt_fragment in (
            "Which projects should I set up?",
            "complete Project Memory setup",
            "Where should future Feature Specs",
            "Do they use different product vocabulary",
            "Which project should define the rules",
            "Where does it apply?",
            "Does this project maintain translation",
            "Ideas saved for possible later planning",
            "Is this mapping correct?",
        ):
            self.assertIn(prompt_fragment, questions)

    def test_runtime_consumers_have_no_retired_context_routing(self) -> None:
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
                if path.is_file() and path.suffix in {".md", ".yaml"}
            )

        retired = (
            "CONTEXT-" + "MAP.md",
            "project-memory/config/" + "domain.md",
            "single-" + "context",
            "multi-" + "context",
            "orchestrator-" + "context",
        )
        stale = {
            token: [
                str(path.relative_to(REPO_ROOT))
                for path in candidates
                if token in path.read_text(encoding="utf-8")
            ]
            for token in retired
        }
        self.assertEqual(stale, {token: [] for token in retired})

        for relative_path in (
            "skills/grill-me-with-context/SKILL.md",
            "skills/improve-codebase-architecture/SKILL.md",
            "skills/plan-feature/SKILL.md",
            "skills/plan-feature/references/spec-phase.md",
        ):
            contents = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            normalized = " ".join(contents.split())
            with self.subTest(relative_path=relative_path):
                self.assertIn("root `CONTEXT.md`", normalized)
                self.assertIn("Scoped Contexts", normalized)
                self.assertIn("current Git repository", normalized)
                self.assertIn("available", normalized)
                self.assertNotIn("Repository Registry", normalized)

    def test_project_memory_owns_artifact_issue_type_and_state_registry(self) -> None:
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
            "`artifact_marker`",
            "`idea`",
            "`bug`",
            "`feature`",
            "`task`",
            "`needs-triage`",
            "`needs-info`",
            "`ready-for-agent`",
            "`ready-for-human`",
            "`wontfix`",
            "`native-type`",
            "`label`",
            "`body-field`",
            "`local-header`",
        ):
            self.assertIn(value, labels)

        self.assertIn("| Canonical type | Transport | Tracker value | Meaning |", labels)
        self.assertIn("| Canonical state | Transport | Tracker value | Meaning |", labels)
        self.assertIn("missing transport column", labels)
        self.assertIn(
            "never infer transport from the tracker value",
            " ".join(github.lower().split()),
        )

        self.assertIn(
            "require exactly one `issue_type` and one `workflow_state`",
            " ".join(labels.split()),
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
                    options,
                    r"(?m)^\| `(?:artifact_marker|issue_type|workflow_state)` \|",
                )

    def test_idea_marker_contract_is_orthogonal_and_setup_scoped(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        labels = (SKILL_ROOT / "references" / "triage-labels.md").read_text(
            encoding="utf-8"
        )
        github = (SKILL_ROOT / "references" / "issue-tracker-github.md").read_text(
            encoding="utf-8"
        )
        local = (SKILL_ROOT / "references" / "issue-tracker-local.md").read_text(
            encoding="utf-8"
        )
        setup = (SKILL_ROOT / "references" / "setup-workflow.md").read_text(
            encoding="utf-8"
        )
        options = (SKILL_ROOT / "references" / "options.md").read_text(
            encoding="utf-8"
        )
        labels_normalized = " ".join(labels.split())
        github_normalized = " ".join(github.split())
        local_normalized = " ".join(local.split())
        setup_normalized = " ".join(setup.split())
        skill_normalized = " ".join(skill.split())

        self.assertIn("orthogonal dimensions", labels_normalized)
        self.assertIn("| `idea` | `label` | `idea` |", labels)
        self.assertIn("leave the native GitHub Issue Type unset", labels)
        self.assertIn("missing mapping blocks only Idea capture", labels_normalized)
        self.assertIn(
            "unrelated planning or implementation workflows", labels_normalized
        )
        self.assertIn("`needs-triage` or `needs-info`", labels_normalized)
        self.assertIn("those states are mutually exclusive", labels)

        self.assertIn("`Idea: <Name>`", github)
        self.assertIn("`idea` label", github)
        self.assertIn(
            "leave the native GitHub Issue Type unset", github_normalized
        )
        self.assertIn(
            "Feature Spec and implementation-issue workflows remain valid",
            github_normalized,
        )
        self.assertIn(
            "This implementation-proof convention applies to Feature Specs and implementation issues",
            github_normalized,
        )
        self.assertIn("Plan Feature may close an Idea", github_normalized)
        self.assertIn("A partially covered Idea remains open", github_normalized)

        self.assertIn("`planning/ideas/<idea-slug>.md`", local)
        self.assertIn("exactly one `artifact_marker: idea`", local_normalized)
        self.assertIn("zero `issue_type` lines", local)
        self.assertIn("zero or one `workflow_state` line", local_normalized)

        self.assertIn("`artifact-marker-mapping`", setup)
        self.assertIn("`Transport`, `Tracker value`, and `Meaning` columns", setup)
        self.assertIn(
            "include the canonical `artifact_marker: idea` mapping",
            setup_normalized,
        )
        self.assertIn("do not invalidate or block unrelated workflows", setup)
        self.assertIn("Do not create Idea tracker artifacts", setup_normalized)
        self.assertIn("never creates Idea issues or files", skill_normalized)
        self.assertNotRegex(
            options, r"(?m)^\| `artifact_marker` \|"
        )

    def test_local_completion_uses_the_owning_feature_subtree(self) -> None:
        local = (SKILL_ROOT / "references" / "issue-tracker-local.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "planning/features/<feature-slug>/issues/done/<NN>-<slug>.md",
            local,
        )
        self.assertNotIn("planning/features/<feature-slug>/integration/", local)
        normalized = " ".join(local.split())
        self.assertIn("tracker file in `affected_repositories`", normalized)
        self.assertIn("exact active issue path", normalized)
        self.assertIn("exact derived `done/` path", normalized)
        self.assertIn("inside that repository", normalized)
        self.assertIn("non-App-executable", normalized)
        self.assertIn("Commit the move on the declared delivery branch", normalized)
        self.assertIn("rerun every final validation and review gate", normalized)
        self.assertIn("`local-branch` executor performs no push or PR", normalized)
        self.assertIn("Project Memory does not choose between them", normalized)

    def test_project_layout_configuration_is_retired(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        options = (SKILL_ROOT / "references" / "options.md").read_text(
            encoding="utf-8"
        )
        setup = (SKILL_ROOT / "references" / "setup-workflow.md").read_text(
            encoding="utf-8"
        )

        self.assertFalse((SKILL_ROOT / "references" / "project-layout.md").exists())
        for contents in (skill, options, setup):
            self.assertNotIn("`project-layout`", contents)
            self.assertNotIn("`repository_layout`", contents)
            self.assertNotIn("multi-repository-workspace", contents)
        self.assertIn("`tracker_backend`", skill)
        self.assertIn("project-memory/config/issue-tracker.md", skill)

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
