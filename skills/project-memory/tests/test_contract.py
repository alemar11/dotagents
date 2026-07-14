from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]


class ProjectMemoryContractTests(unittest.TestCase):
    def test_generated_configuration_uses_config_directory(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        setup = (SKILL_ROOT / "references" / "setup-workflow.md").read_text(
            encoding="utf-8"
        )

        for relative_path in (
            "project-memory/config/issue-tracker.md",
            "project-memory/config/triage-labels.md",
            "project-memory/config/domain.md",
        ):
            self.assertIn(relative_path, skill)
            self.assertIn(relative_path, setup)

    def test_runtime_contracts_do_not_reference_legacy_agents_directory(self) -> None:
        roots = [
            REPO_ROOT / "AGENTS.md",
            REPO_ROOT / "skills" / "project-memory",
            REPO_ROOT / "skills" / "plan-feature",
            REPO_ROOT / "skills" / "triage",
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
