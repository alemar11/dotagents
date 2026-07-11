from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = ROOT / "skills" / "codex-orchestrator"


class OrchestratorContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (SKILL_ROOT / relative).read_text(encoding="utf-8")

    def test_standalone_github_is_primary_and_plugin_is_fallback_only(self) -> None:
        skill = self.read("SKILL.md")
        ledger = self.read("references/ledger.md")
        normalized_skill = " ".join(skill.split())

        self.assertIn("Standalone companion skills are always the primary", skill)
        self.assertIn(
            "GitHub plugin may be used only as an automatic, logged fallback",
            normalized_skill,
        )
        self.assertIn("GitHub primary surface: standalone", ledger)
        self.assertIn("authority-reused=<authority", ledger)

    def test_merge_is_root_owned_and_explicit(self) -> None:
        worker = self.read("references/worker.md")
        delivery = self.read("references/prd-backed-delivery.md")
        gates = self.read("references/gates.md")

        authorization_row = next(
            line for line in worker.splitlines() if "`worker_authorization`" in line
        )
        prompt_modes = next(
            line
            for line in worker.splitlines()
            if line.startswith("- Authorization modes:")
        )
        self.assertNotIn("merge-close", authorization_row)
        self.assertNotIn("merge-close", prompt_modes)
        self.assertIn("`merge_authority`: `none` is the default", delivery)
        self.assertIn("### Merge Authorization Gate", gates)

    def test_capability_and_reconciliation_contracts_are_required(self) -> None:
        worker = self.read("references/worker.md")
        ledger = self.read("references/ledger.md")

        self.assertIn("## Capability Snapshots", worker)
        self.assertIn("created, resumed, or\nforked", worker)
        self.assertIn("Reconciliation updates the current projection", ledger)
        self.assertIn("Stale Values Removed", ledger)


if __name__ == "__main__":
    unittest.main()
