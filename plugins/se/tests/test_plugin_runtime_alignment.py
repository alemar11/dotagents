import json
import subprocess
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
RUN_STATE = PLUGIN / "skills/implement/scripts/run-state"


class PluginRuntimeAlignmentTests(unittest.TestCase):
    def test_plugin_cli_version_is_aligned_and_runtime_contract_is_stable(self) -> None:
        manifest = json.loads(
            (PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        version = subprocess.run(
            [str(RUN_STATE), "--version"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        capabilities = json.loads(
            subprocess.run(
                [str(RUN_STATE), "--json", "capabilities"],
                text=True,
                capture_output=True,
                check=True,
            ).stdout
        )

        self.assertEqual(manifest["version"], version)
        self.assertEqual(capabilities["runtime_contract_version"], "3.2.0")


if __name__ == "__main__":
    unittest.main()
