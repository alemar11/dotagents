import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
HANDOFF = PLUGIN / "references/task-handoff.md"
PREFLIGHT = PLUGIN / "references/task-preflight.md"
IMPLEMENT = PLUGIN / "skills/implement/SKILL.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class TaskPromptHygieneContractTests(unittest.TestCase):
    def test_prompts_are_flat_semantic_assignments(self) -> None:
        handoff = normalized(HANDOFF)
        implement = normalized(IMPLEMENT)

        for required in (
            "one flat semantic assignment",
            "raw task/delegation transport envelope",
            "discard the wrapper and any escaped wrapper markup",
            "Never nest one handoff envelope inside another",
            "must not drop a user constraint",
        ):
            self.assertIn(required, handoff)

        self.assertIn("shared flat prompt projection", implement)
        self.assertIn("never forward a raw parent prompt or transport envelope", implement)

    def test_canonical_title_prompt_hint_is_best_effort_only(self) -> None:
        handoff = normalized(HANDOFF)
        preflight = normalized(PREFLIGHT)

        for required in (
            "Canonical display title: <canonical display title>",
            "best-effort first-render hint",
            "never authoritative metadata, identity, or verification evidence",
            "bounded title reconciliation below remains mandatory",
            "prompt_hint_included: true",
        ):
            self.assertIn(required, handoff)

        self.assertIn(
            "plain-text title hint does not make title initialization available",
            preflight,
        )


if __name__ == "__main__":
    unittest.main()
