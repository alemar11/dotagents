import json
import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


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
        """Validate machine-consumed metadata fields and values."""
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
        """Validate canonical reference paths and their filesystem targets."""
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

    def test_official_urls_are_bounded_to_primary_sources(self) -> None:
        """Validate the external-source allowlist used by the guidance."""
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


if __name__ == "__main__":
    unittest.main()
