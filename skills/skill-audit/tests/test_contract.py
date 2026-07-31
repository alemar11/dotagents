from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class SkillAuditContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (SKILL_ROOT / relative).read_text(encoding="utf-8")

    def test_canonical_dag_routes_representative_audit_paths(self) -> None:
        skill = self.read("SKILL.md")
        routing_matrix = (
            ("named standalone", "references/standalone-skills.md"),
            ("plugin", "references/plugins.md"),
            ("cached bundled skill", "references/cache-resolution.md"),
            ("unnamed portfolio", "references/portfolio-hygiene.md"),
            ("writing style", "references/writing-style-review.md"),
            ("named live", "references/live-monitoring.md"),
            ("unnamed live", "references/live-monitoring.md"),
            ("unavailable live evidence", "references/live-monitoring.md"),
            ("self audit", "references/output-format.md"),
        )

        self.assertIn("## Canonical Audit DAG", skill)
        self.assertIn("references/historical-evidence.md", skill)
        for route, pointer in routing_matrix:
            with self.subTest(route=route):
                self.assertIn(pointer, skill)
                self.assertTrue((SKILL_ROOT / pointer).is_file())
        self.assertIn("full-portfolio audit", skill)
        self.assertIn("excludes `skill-audit`", skill)

        live = self.read("references/live-monitoring.md")
        self.assertIn("Prefer task IDs or titles explicitly named by the user", live)
        self.assertIn("unnamed request to monitor current active tasks", live)
        self.assertIn("current evidence unavailable", live)

    def test_historical_pipeline_has_one_canonical_owner(self) -> None:
        historical = self.read("references/historical-evidence.md")
        self.assertIn("## Canonical Order", historical)
        self.assertLess(historical.index("Read the editable target"), historical.index("git log"))
        self.assertLess(historical.index("git log"), historical.index("Search the memory index"))
        self.assertLess(historical.index("Search the memory index"), historical.index("raw session"))
        self.assertIn("<codex-root>/memories/MEMORY.md", historical)
        self.assertIn("<codex-root>/memories/rollout_summaries/", historical)
        self.assertIn("<codex-root>/sessions/", historical)
        self.assertIn("<codex-root>/archived_sessions/", historical)
        self.assertIn(
            "Never report memory as\nabsent after checking only that singular path",
            historical,
        )

        for overlay in (
            "references/standalone-skills.md",
            "references/plugins.md",
            "references/bundled-plugin-skills.md",
        ):
            text = self.read(overlay)
            with self.subTest(overlay=overlay):
                self.assertNotIn("## Evidence Workflow", text)
                self.assertIn("references/historical-evidence.md", text)

    def test_live_monitor_uses_task_local_registry_and_valid_transitions(self) -> None:
        contract = self.read("references/live-monitoring.md")

        for transition in (
            "`provisional -> confirmed -> resolved`",
            "`provisional -> withdrawn`",
            "`confirmed -> withdrawn`",
        ):
            self.assertIn(transition, contract)
        self.assertIn("material nonterminal transition", contract)
        self.assertIn("continue after the task resumes", contract)
        self.assertIn("fresh authoritative task read", contract)
        self.assertIn("complete canonical annotation registry", contract)
        self.assertIn("Do not persist it", contract)
        self.assertIn("Evidence unavailability is a monitor limitation, not a defect.", contract)
        self.assertNotIn("terminal or\n   needs-attention", contract)

    def test_historical_and_live_outputs_remain_distinct(self) -> None:
        output = self.read("references/output-format.md")
        live = self.read("references/live-monitoring.md")
        self.assertIn("## Live Monitor Format", output)
        self.assertIn("Per-target update roadmap", output)
        self.assertIn("complete stable `LIVE-NNN` registry", output)
        for value in ("standalone-skill", "plugin-package", "bundled-plugin-skill"):
            self.assertIn(value, output)
            self.assertIn(value, live)


if __name__ == "__main__":
    unittest.main()
