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
