import json
import subprocess
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = ("learn", "idea", "feature", "audit", "implement")
RUN_STATE = PLUGIN / "skills/implement/scripts/run-state"


def workflow_nodes(skill_path: Path) -> list[str]:
    lines = skill_path.read_text(encoding="utf-8").splitlines()
    header = next(
        index for index, line in enumerate(lines)
        if line.lower().startswith("| node_id ")
    )
    nodes: list[str] = []
    for line in lines[header + 2:]:
        if not line.startswith("|"):
            break
        node = line.strip().strip("|").split("|", 1)[0].strip().strip("`")
        nodes.append(node)
    return nodes


class StateReferenceTests(unittest.TestCase):
    def test_every_skill_routes_to_a_complete_human_state_table(self) -> None:
        for skill in SKILLS:
            with self.subTest(skill=skill):
                root = PLUGIN / f"skills/{skill}"
                skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
                states_path = root / "references/states.md"
                self.assertTrue(states_path.is_file())
                self.assertIn("references/states.md", skill_text)

                states = states_path.read_text(encoding="utf-8")
                self.assertIn("## Workflow nodes", states)
                self.assertGreaterEqual(states.count("| ---"), 2)
                for node in workflow_nodes(root / "SKILL.md"):
                    self.assertIn(f"| `{node}` |", states)

    def test_implement_capability_registry_matches_the_human_reference(self) -> None:
        result = subprocess.run(
            [str(RUN_STATE), "--json", "capabilities"],
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        registry = payload["result"]["state_registry"]
        states = (PLUGIN / "skills/implement/references/states.md").read_text(
            encoding="utf-8"
        )

        for family in ("run_pairs", "assignment_pairs"):
            for pair in registry[family]:
                rendered = f"{pair['status']} @ {pair['checkpoint']}"
                if family == "assignment_pairs" and pair["status"] == "blocked":
                    self.assertIn("blocked @ <last-durable-checkpoint>", states)
                    self.assertIn(f"`{pair['checkpoint']}`", states)
                else:
                    self.assertIn(rendered, states)
        for family in ("feature_claim_statuses", "operation_statuses"):
            for value in registry[family]:
                self.assertIn(f"`{value}`", states)

    def test_plugin_cli_and_runtime_contract_versions_are_aligned(self) -> None:
        manifest = json.loads(
            (PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        version = subprocess.run(
            [str(RUN_STATE), "--version"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        capabilities = json.loads(subprocess.run(
            [str(RUN_STATE), "--json", "capabilities"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout)

        self.assertEqual(manifest["version"], version)
        self.assertEqual(capabilities["runtime_contract_version"], version)


if __name__ == "__main__":
    unittest.main()
