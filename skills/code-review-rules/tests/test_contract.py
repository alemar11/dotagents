import json
import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]


def read(relative_path: str) -> str:
    return (SKILL_ROOT / relative_path).read_text(encoding="utf-8")


def parse_metadata(contents: str) -> dict[tuple[str, str], object]:
    values: dict[tuple[str, str], object] = {}
    section = ""
    for line_number, line in enumerate(contents.splitlines(), start=1):
        if not line:
            continue
        section_match = re.fullmatch(r"([a-z_]+):", line)
        if section_match:
            section = section_match.group(1)
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
            values[target] = scalar == "true"
        else:
            raise ValueError(f"invalid metadata scalar on line {line_number}")
    return values


class CodeReviewRulesContractTests(unittest.TestCase):
    def test_metadata_is_manual_only(self) -> None:
        metadata = parse_metadata(read("agents/openai.yaml"))

        self.assertEqual(
            metadata[("interface", "display_name")], "Code Review Rules"
        )
        self.assertEqual(metadata[("interface", "brand_color")], "#7C3AED")
        self.assertIn(
            "$code-review-rules", metadata[("interface", "default_prompt")]
        )
        self.assertFalse(metadata[("policy", "allow_implicit_invocation")])

    def test_all_local_reference_links_resolve(self) -> None:
        skill = read("SKILL.md")
        links = re.findall(r"\[[^]]+\]\((references/[^)]+\.md)\)", skill)

        self.assertEqual(
            set(links),
            {
                "references/evidence-mining.md",
                "references/official-docs.md",
                "references/rule-evaluation.md",
            },
        )
        for link in links:
            self.assertTrue((SKILL_ROOT / link).is_file(), link)

    def test_external_heading_and_manual_write_boundary_are_explicit(self) -> None:
        skill = read("SKILL.md")
        ownership = skill.split("## Runtime And Ownership", 1)[1].split(
            "## Reference Routing", 1
        )[0]
        workflow = skill.split("## Workflow", 1)[1]

        self.assertIn("exact `## Code Review Rules`", skill)
        self.assertIn("`$learn` is the only writer", ownership)
        self.assertLess(
            workflow.index("### 5. Hand The Exact Proposal To Learn And Pause"),
            workflow.index("### 6. Apply Through Learn And Verify"),
        )
        self.assertIn(
            "Never propose and write in the same turn", " ".join(ownership.split())
        )
        self.assertIn("never introduce a second approval prompt", ownership)

    def test_bootstrap_refuses_unsupported_generic_rules(self) -> None:
        mining = read("references/evidence-mining.md")
        skill = read("SKILL.md")

        self.assertIn("Do not manufacture \"basic\" rules", mining)
        self.assertIn("An evidence-poor repository returns a no-op", skill)
        self.assertIn("Never create an empty file", skill)

    def test_official_urls_are_bounded_to_primary_sources(self) -> None:
        docs = read("references/official-docs.md")
        urls = re.findall(r"https://[^ |)]+", docs)

        self.assertGreaterEqual(len(urls), 6)
        for url in urls:
            self.assertTrue(
                url.startswith("https://developers.openai.com/")
                or url.startswith("https://learn.chatgpt.com/")
                or url.startswith("https://github.com/openai/"),
                url,
            )

    def test_repository_registration_and_dependency_are_present(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("| `code-review-rules` |", readme)
        self.assertIn("`code-review-rules` requires `$learn`", readme)
        self.assertIn("`code-review-rules`", agents)


if __name__ == "__main__":
    unittest.main()
