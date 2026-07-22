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


class IdeaSourceContractTests(unittest.TestCase):
    def test_run_registry_contains_only_write_mode(self) -> None:
        options = read("references/options.md")
        registry = section(options, "## Run Registry", "## Resolution")

        self.assertEqual(["write_mode"], table_fields(registry))

    def test_source_idea_refs_belong_to_the_spec_source_section(self) -> None:
        spec_template = read("references/spec-template.md")
        issue_template = read("references/issue-body-template.md")
        source = section(spec_template, "## Source", "## Goal")

        self.assertRegex(source, r"(?m)^- Source Idea:")
        self.assertNotRegex(issue_template, r"(?m)^- Source Idea:")
        self.assertNotIn("source_idea_refs", issue_template)

    def test_spec_and_issue_templates_expose_distinct_acceptance_sections(self) -> None:
        spec_template = read("references/spec-template.md")
        issue_template = read("references/issue-body-template.md")
        spec_acceptance = section(
            spec_template, "## Acceptance Criteria", "## Validation Expectations"
        )
        issue_acceptance = section(
            issue_template, "## Acceptance Criteria", "## Validation"
        )

        self.assertRegex(spec_acceptance, r"(?m)^- \[ \] ")
        self.assertRegex(issue_acceptance, r"(?m)^- \[ \] ")
        self.assertNotEqual(spec_acceptance.strip(), issue_acceptance.strip())


if __name__ == "__main__":
    unittest.main()
