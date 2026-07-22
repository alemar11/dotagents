import json
import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]


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
        if match:
            if not section:
                raise ValueError(f"metadata key before section on line {line_number}")
            key, value = match.groups()
            target = (section, key)
            if target in values:
                raise ValueError(f"duplicate metadata key: {section}.{key}")
            scalar = value.strip()
            if re.fullmatch(r'"(?:[^"\\]|\\.)*"', scalar):
                values[target] = json.loads(scalar)
            elif scalar in ("true", "false"):
                values[target] = scalar
            else:
                raise ValueError(f"invalid metadata scalar on line {line_number}")
            continue
        raise ValueError(f"invalid metadata line {line_number}: {line}")
    return values


def has_crusty_mutation_authorization(contents: str) -> bool:
    normalized = " ".join(contents.split())
    patterns = (
        r"\bCrusty (?:may|can|should|must|will) (?:directly )?"
        r"(?:edit|modify|implement|fix|add|remove|stage|commit|push)",
        r"\b(?:may|can) (?:edit|modify|implement|fix) "
        r"(?:files|code|tests|the implementation)",
        r"\bafter (?:the )?(?:critique|feedback|review)[^.]{0,120}\b"
        r"(?:edit|modify|implement|fix|apply|add|remove)",
        r"\b(?:then|proceed to|continue to|go on to|follow with)[^.]{0,100}\b"
        r"(?:edit|modify|implement|fix|apply|add|remove)",
        r"(?:^|[.!?]\s+)(?!do not )switch to "
        r"(?:an? |the )?(?:ordinary )?implementation",
    )
    return any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in patterns)


class CrustyContractTests(unittest.TestCase):
    def test_skill_is_unconditionally_advisory_only(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        skill_normalized = " ".join(skill.split())

        self.assertIn("This skill is advisory-only", skill)
        self.assertIn("Keep Crusty advisory-only", skill)
        self.assertIn("That is an identity boundary, not a default", skill)
        self.assertIn(
            "do not switch to an implementation workflow", skill_normalized
        )
        self.assertIn("requires a separate non-Crusty workflow", skill)
        self.assertNotIn("advisory " + "by default", skill)
        self.assertNotIn(
            "unless the user separately asks for " + "implementation", skill
        )

    def test_skill_requires_independent_evidence_backed_judgment(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        skill_normalized = " ".join(skill.split())

        self.assertIn("Form an independent judgment", skill)
        self.assertIn(
            "Do not adopt the invoker's preferred conclusion, confidence, or framing",
            skill_normalized,
        )
        self.assertIn("treat it as a claim to examine", skill_normalized)
        self.assertIn("Do not be contrarian for sport", skill)
        self.assertIn(
            "Independent judgment does not authorize ignoring the user's stated goals",
            skill_normalized,
        )

    def test_runtime_docs_do_not_authorize_crusty_mutations(self) -> None:
        runtime_docs = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                SKILL_ROOT / "SKILL.md",
                SKILL_ROOT / "references" / "implementation-evaluation.md",
            )
        )

        self.assertFalse(has_crusty_mutation_authorization(runtime_docs))
        for contradiction in (
            "Crusty may edit files and implement fixes.",
            "After the critique, proceed to edit files when the user confirms.",
            "Return feedback, then fix the tests.",
            "Switch to ordinary implementation after the verdict.",
        ):
            with self.subTest(contradiction=contradiction):
                self.assertTrue(
                    has_crusty_mutation_authorization(
                        f"{runtime_docs}\n{contradiction}"
                    )
                )

    def test_implementation_evaluation_is_explicit_and_feedback_only(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        evaluation = (
            SKILL_ROOT / "references" / "implementation-evaluation.md"
        ).read_text(encoding="utf-8")
        evaluation_normalized = " ".join(evaluation.split())

        self.assertIn(
            "[implementation-evaluation.md](references/implementation-evaluation.md)",
            skill,
        )
        self.assertIn("instead of steps 3-8", skill)
        self.assertIn("return its specialized output, and stop", skill)
        self.assertIn("only when the user explicitly asks Crusty", evaluation)
        self.assertIn("Crusty's advisory-only boundary applies unchanged", evaluation)
        self.assertIn(
            "do not modify the target project or real external state",
            evaluation_normalized,
        )
        self.assertIn(
            "does not authorize changes or a later implementation phase in the same task",
            evaluation_normalized,
        )
        self.assertIn("inspect the command and its fixtures", evaluation_normalized)
        self.assertIn("isolated disposable copy", evaluation_normalized)
        self.assertIn(
            "shared databases, services, networks, home-directory caches",
            evaluation_normalized,
        )
        self.assertIn(
            "Do not add the test or perform the fix as Crusty",
            evaluation_normalized,
        )
        self.assertIn("test-gap matrix", evaluation)
        self.assertIn("instead of the general output shape", evaluation)

    def test_user_facing_metadata_presents_crusty_as_an_advisor(self) -> None:
        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        metadata_values = parse_top_level_yaml_sections(metadata)
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        short_description = metadata_values[("interface", "short_description")]
        default_prompt = metadata_values[("interface", "default_prompt")]

        self.assertGreaterEqual(len(short_description), 25)
        self.assertLessEqual(len(short_description), 64)
        self.assertIn("Independent advisory-only critique", short_description)
        self.assertIn("$crusty", default_prompt)
        self.assertIn("do not adopt my preferred conclusion or framing", default_prompt)
        self.assertIn("local or supplied evidence", default_prompt)
        self.assertIn("without editing project files", default_prompt)
        self.assertEqual(
            metadata_values[("policy", "allow_implicit_invocation")], "false"
        )
        with self.assertRaises(ValueError):
            parse_top_level_yaml_sections(f"{metadata}\ninvalid: [")
        with self.assertRaises(ValueError):
            parse_top_level_yaml_sections(
                metadata.replace(
                    "policy:\n  allow_implicit_invocation: false",
                    "policy:\n  nested:\n    allow_implicit_invocation: false",
                )
            )
        self.assertIn(
            "`crusty` | Direct-only independent advisory critique for decisions, "
            "implementations, architecture, naming, and tradeoffs.",
            readme,
        )
        self.assertIn(
            "advisory critique and implementation-evaluation workflows", agents
        )

    def test_local_markdown_references_resolve_and_use_lowercase_names(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        targets = re.findall(r"\]\((references/[^)]+\.md)\)", skill)

        self.assertTrue(targets)
        for target in targets:
            path = SKILL_ROOT / target
            self.assertTrue(path.is_file(), target)
            self.assertEqual(path.name, path.name.lower())


if __name__ == "__main__":
    unittest.main()
