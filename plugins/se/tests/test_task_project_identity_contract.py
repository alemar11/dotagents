import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]


class TaskProjectIdentityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.preflight = " ".join(
            (PLUGIN / "references/task-preflight.md")
            .read_text(encoding="utf-8")
            .split()
        )
        cls.handoff = " ".join(
            (PLUGIN / "references/task-handoff.md")
            .read_text(encoding="utf-8")
            .split()
        )

    def test_preflight_requires_inventory_backed_project_or_setup_guidance(self) -> None:
        for expected in (
            "live application project inventory",
            "repository-compatible project",
            "add or configure that exact repository as a saved project",
            "Never substitute a neighboring project",
            "project_inventory_evidence_ref",
            "assigned_task_bootstrap",
            "receive_bootstrap_result",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, self.preflight)

    def test_handoff_reconciles_missing_project_on_the_same_task(self) -> None:
        for expected in (
            "exactly one bounded second authoritative self-read",
            "one controller refresh of the live project inventory",
            "blocker: unsupported-runtime",
            "Never create a replacement task",
            "requested_project_identity",
            "project_reconciliation_ref",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, self.handoff)

    def test_handoff_forbids_non_authoritative_project_inference(self) -> None:
        inference_sources = (
            "request payload",
            "creation receipt",
            "working directory",
            "checkout or worktree path",
            "display title",
            "conversation text",
        )
        for source in inference_sources:
            with self.subTest(source=source):
                self.assertIn(source, self.handoff)

    def test_feature_and_implement_route_project_verification_to_shared_contracts(self) -> None:
        feature = " ".join(
            (PLUGIN / "skills/feature/SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        )
        implement = " ".join(
            (PLUGIN / "skills/implement/SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        )

        self.assertIn("inventory-backed project selection", feature)
        self.assertIn("authoritative self-observed project", feature)
        self.assertIn("Inventory-backed project selection", implement)
        self.assertIn("authoritative assigned-task project/profile bootstrap", implement)


if __name__ == "__main__":
    unittest.main()
