import json
import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (SKILL_ROOT / relative_path).read_text(encoding="utf-8")


def normalized(contents: str) -> str:
    return " ".join(contents.split())


def parse_top_level_yaml_sections(contents: str) -> dict[tuple[str, str], str]:
    values: dict[tuple[str, str], str] = {}
    sections: set[str] = set()
    section = ""
    for line_number, line in enumerate(contents.splitlines(), start=1):
        if not line or line.lstrip().startswith("#"):
            continue
        section_match = re.fullmatch(r"([a-z_]+):", line)
        if section_match:
            section = section_match.group(1)
            if section in sections:
                raise ValueError(f"duplicate metadata section: {section}")
            sections.add(section)
            continue
        match = re.fullmatch(r"  ([a-z_]+):\s*(.*)", line)
        if not match or not section:
            raise ValueError(f"invalid metadata line {line_number}: {line}")
        key, scalar = match.groups()
        target = (section, key)
        if target in values:
            raise ValueError(f"duplicate metadata key: {section}.{key}")
        scalar = scalar.strip()
        if re.fullmatch(r'"(?:[^"\\]|\\.)*"', scalar):
            values[target] = json.loads(scalar)
        elif scalar in ("true", "false"):
            values[target] = scalar
        else:
            raise ValueError(f"invalid metadata scalar on line {line_number}")
    return values


class CaptureIdeaContractTests(unittest.TestCase):
    def test_metadata_is_manual_only_and_named_consistently(self) -> None:
        metadata = parse_top_level_yaml_sections(read("agents/openai.yaml"))

        self.assertEqual(metadata[("interface", "display_name")], "Capture Idea")
        self.assertEqual(metadata[("interface", "brand_color")], "#D97706")
        self.assertIn("$capture-idea", metadata[("interface", "default_prompt")])
        self.assertEqual(
            metadata[("policy", "allow_implicit_invocation")], "false"
        )

        skill = read("SKILL.md")
        self.assertIn("name: capture-idea", skill)
        self.assertIn("Do not auto-select it", normalized(skill))
        self.assertIn("After reporting the captured Ideas, stop.", normalized(skill))

    def test_option_registry_contains_only_write_mode(self) -> None:
        options = read("references/options.md")
        registry = options.split("## Run Registry", 1)[1].split(
            "## Execution Data", 1
        )[0]

        self.assertIn("`write_mode` | `apply`, `propose`", registry)
        for forbidden in (
            "tracker_backend",
            "repository_layout",
            "queue_intent",
            "artifact_marker",
            "tracker_owner",
            "issue_type",
        ):
            self.assertNotIn(forbidden, registry)
        self.assertIn("Reject every field or value not listed", options)

    def test_capture_is_not_planning_or_implementation(self) -> None:
        skill = read("SKILL.md")
        boundary = skill.split("## Purpose And Invocation", 1)[1].split(
            "## Structured Option Contract", 1
        )[0]

        for phrase in (
            "does not create Feature Specs or implementation issues",
            "plan the\nproposal",
            "modify domain memory",
            "implement\nanything",
        ):
            self.assertIn(phrase, boundary)
        self.assertIn("Planning and source-Idea lifecycle transitions", skill)

    def test_local_artifact_has_marker_without_issue_type(self) -> None:
        template = read("references/idea-template.md")
        local = read("references/local-publishing.md")

        self.assertIn("planning/ideas/<idea-slug>.md", local)
        self.assertIn("<repository-slug>/planning/ideas/<idea-slug>.md", local)
        self.assertIn("exactly one `artifact_marker: idea`", normalized(template))
        self.assertIn("no `issue_type`", normalized(template))
        self.assertIn("no workflow-state line for a dormant Idea", local)
        self.assertIn("workflow_state: needs-triage", local)
        self.assertIn("Never overwrite it", local)

    def test_github_artifact_is_untyped_and_marker_labeled(self) -> None:
        skill = read("SKILL.md")
        github = read("references/github-publishing.md")

        self.assertIn("title `Idea: <Name>`", github)
        self.assertIn("artifact_marker: idea", github)
        self.assertIn("native GitHub Issue Type unset", github)
        self.assertIn("issueType=null", github)
        self.assertIn("Omit `--type`", github)
        self.assertIn("$gitstack:github-issues", github)
        self.assertIn("mutation_mode=apply", github)
        self.assertIn("issue_operation=create-label", github)
        self.assertIn("issue_operation=create", github)
        self.assertIn("Pure preflight reads are allowed in either write mode", skill)
        self.assertIn("allow only\nread-only GitHub inspection", skill)

    def test_fresh_github_queue_preflights_both_required_labels(self) -> None:
        skill = read("SKILL.md")
        github = read("references/github-publishing.md")
        contents = normalized(github)

        self.assertIn("Require `label` for GitHub marker/state rows", skill)
        self.assertIn("`local-header` for local", skill)
        self.assertIn("Require explicit transport `label`", github)
        self.assertIn("Idea-marker label for every candidate", contents)
        self.assertIn("mapped `needs-triage` label", contents)
        self.assertIn("Create and verify every required missing label", contents)
        self.assertIn("need both the configured Idea-marker label", contents)
        self.assertIn("configured `needs-triage` label", contents)

    def test_capture_state_requires_explicit_queue_intent(self) -> None:
        skill = read("SKILL.md")
        template = read("references/idea-template.md")
        github = read("references/github-publishing.md")

        for contents in (skill, template, github):
            self.assertIn("only when the user explicitly", normalized(contents))
        self.assertIn("`needs-triage` is the only allowed workflow state", skill)
        self.assertIn("do not imply `needs-info`", skill)
        self.assertNotIn("ready-for-agent", template)
        self.assertNotIn("ready-for-human", template)

    def test_multiple_idea_questionnaire_has_safe_batching_and_fallback(self) -> None:
        selection = read("references/multi-idea-selection.md")

        self.assertIn("Save idea (Recommended)", selection)
        self.assertIn("Skip idea", selection)
        self.assertIn("client-provided free-form `Other`", selection)
        self.assertIn("at most three candidate questions", normalized(selection))
        self.assertIn("Do not set `autoResolutionMs`", selection)
        self.assertIn("silence is not consent", selection)
        self.assertIn("stable snake_case candidate ID", normalized(selection))
        self.assertIn("header of 12 or fewer characters", normalized(selection))
        self.assertIn("one at a time in plain language", normalized(selection))
        for operation in ("rename", "merge", "split", "queue"):
            self.assertIn(operation, selection)
        self.assertIn("before the first local or GitHub write", selection)
        self.assertIn(
            "exactly one candidate needs no extra confirmation",
            normalized(selection),
        )

    def test_preflight_resolves_owners_duplicates_and_collisions_before_writes(self) -> None:
        skill = read("SKILL.md")
        preflight = skill.split("### 3. Preflight The Entire Accepted Set", 1)[1].split(
            "### 4. Publish Through The Resolved Backend", 1
        )[0]

        self.assertIn("one tracker owner", preflight)
        self.assertIn("exact equivalent", preflight)
        self.assertIn("Reuse that durable ref", preflight)
        self.assertIn("ask whether to reuse, rename, or revise", preflight)
        self.assertIn("Never\n   overwrite an existing local Idea", preflight)
        self.assertIn("Resolve all resulting collisions before publication", preflight)

    def test_missing_project_memory_mapping_never_causes_implicit_setup(self) -> None:
        skill = read("SKILL.md")

        self.assertIn("Require an explicit configured mapping", skill)
        self.assertIn("stop before capture writes", skill)
        self.assertIn("Do not repair configuration unless", skill)
        self.assertIn("never performs implicit setup writes", skill)

    def test_proposals_are_non_durable_and_not_planning_input(self) -> None:
        skill = read("SKILL.md")
        options = read("references/options.md")

        self.assertIn("deterministic `proposed-idea:` refs", skill)
        self.assertIn("non-durable", skill)
        self.assertIn("must never be presented as\n  valid Plan Feature input", skill)
        self.assertIn("proposed-idea:<repository-slug>/<idea-slug>", options)
        self.assertIn("Proposed refs are never\ndurable planning input", options)

    def test_partial_recovery_retries_only_missing_operations(self) -> None:
        skill = read("SKILL.md")
        github = read("references/github-publishing.md")
        local = read("references/local-publishing.md")

        self.assertIn("retry only operations proven absent", skill)
        self.assertIn("never replay the whole batch", github)
        self.assertIn("retry only a file proven absent", local)
        self.assertIn("verified created and reused refs", normalized(github))
        self.assertIn("verified created and reused refs", normalized(local))

    def test_template_has_exact_capture_sections_and_no_outcome_section(self) -> None:
        template = read("references/idea-template.md")
        canonical = template.split("## Canonical Content", 1)[1].split(
            "## Content Boundaries", 1
        )[0]
        headings = re.findall(r"^## (.+)$", canonical, flags=re.MULTILINE)

        self.assertEqual(
            headings,
            [
                "Summary",
                "Problem or Opportunity",
                "Proposed Direction",
                "Expected Value",
                "Known Context and Constraints",
                "Open Questions",
                "Source",
            ],
        )
        self.assertNotIn("## Planning Outcomes", canonical)
        self.assertIn("Do not include `## Planning Outcomes` during capture", template)

    def test_references_resolve_and_use_lowercase_names(self) -> None:
        skill = read("SKILL.md")
        targets = re.findall(r"\]\((references/[^)]+\.md)\)", skill)

        self.assertEqual(
            set(targets),
            {
                "references/options.md",
                "references/idea-template.md",
                "references/multi-idea-selection.md",
                "references/github-publishing.md",
                "references/local-publishing.md",
            },
        )
        for target in targets:
            path = SKILL_ROOT / target
            self.assertTrue(path.is_file(), target)
            self.assertEqual(path.name, path.name.lower())


if __name__ == "__main__":
    unittest.main()
