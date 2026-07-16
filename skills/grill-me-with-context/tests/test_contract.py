from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class GrillMeWithContextContractTests(unittest.TestCase):
    def test_deferred_handoff_uses_optional_knowledge_data(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("optional structured `knowledge_delta`", skill)
        self.assertIn("planning_blockers: []", skill)
        self.assertIn("omit `knowledge_delta` entirely", skill)
        self.assertNotIn("domain_knowledge_delta", skill)
        self.assertNotIn("knowledge_delta: required", skill)
        self.assertNotIn("knowledge_delta: none", skill)

    def test_explicit_no_write_and_parent_modes_precede_direct_default(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        resolution = skill.split("### Mode Resolution", 1)[1].split(
            "## Trigger Rules", 1
        )[0]

        no_write = resolution.index("1. An explicit user request")
        parent = resolution.index("2. Otherwise, a parent workflow")
        direct = resolution.index("3. Otherwise, direct")

        self.assertLess(no_write, parent)
        self.assertLess(parent, direct)
        self.assertIn("no-write instruction wins", resolution)


if __name__ == "__main__":
    unittest.main()
