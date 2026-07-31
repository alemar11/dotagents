import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (SKILL_ROOT / relative_path).read_text(encoding="utf-8")


def option_fields(contents: str) -> list[str]:
    registry = contents.split("## Registry", 1)[1].split(
        "## Cross-Field Validation", 1
    )[0]
    return re.findall(r"^\| `([^`]+)` \|", registry, flags=re.MULTILINE)


def caller_template_keys(contents: str) -> set[str]:
    caller_section = contents.split(
        "## Caller-Surface Issue-Hardening Result", 1
    )[1]
    yaml_block = re.search(r"```yaml\n(.*?)\n```", caller_section, flags=re.DOTALL)
    if yaml_block is None:
        raise AssertionError("caller result template is missing")
    return set(
        re.findall(r"^([a-z][a-z_]*):", yaml_block.group(1), flags=re.MULTILINE)
    )


class PlanHarderContractTests(unittest.TestCase):
    def test_canonical_options_have_no_persistence_selector(self) -> None:
        options = read("references/options.md")

        self.assertEqual(
            option_fields(options),
            [
                "planning_mode",
                "output_surface",
                "result_status",
                "estimated_complexity",
            ],
        )
        self.assertNotRegex(
            options,
            r"(?m)^\| `(storage|save|persistence|plan_path|write)_?[a-z_]*` \|",
        )

    def test_standalone_and_caller_surfaces_remain_distinct(self) -> None:
        options = read("references/options.md")
        templates = read("references/templates.md")

        self.assertIn(
            "`output_surface=caller` requires `planning_mode=issue-hardening`.",
            options,
        )
        self.assertIn(
            "`planning_mode=full-plan` requires `output_surface=standalone`",
            options,
        )
        self.assertIn("## Full-Plan Template", templates)
        self.assertIn("## Caller-Surface Issue-Hardening Result", templates)
        self.assertEqual(
            caller_template_keys(templates),
            {
                "result_status",
                "goal",
                "non_goals",
                "resolved_interpretation",
                "implementation_plan",
                "likely_touch_points",
                "dependencies",
                "acceptance_criteria",
                "validation",
                "risks_and_rollback",
                "handoff",
                "blockers",
            },
        )

    def test_metadata_prompt_is_chat_only(self) -> None:
        """Validate machine-consumed metadata without using SKILL.md prose."""
        metadata = read("agents/openai.yaml")
        prompt = re.search(r'^  default_prompt: "(.*)"$', metadata, flags=re.MULTILINE)

        self.assertIsNotNone(prompt)
        assert prompt is not None
        self.assertIn("$plan-harder", prompt.group(1))
        self.assertIn("without coding or writing files", prompt.group(1))
        self.assertNotIn("plans/", prompt.group(1))


if __name__ == "__main__":
    unittest.main()
