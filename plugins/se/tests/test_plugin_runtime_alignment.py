import json
import subprocess
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
REPOSITORY_CLAIMS = PLUGIN / "skills/deliver-features/scripts/repository-claims"


class PluginRuntimeAlignmentTests(unittest.TestCase):
    def test_plugin_cli_version_is_aligned(self) -> None:
        manifest = json.loads(
            (PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        repository_claims_version = subprocess.run(
            [str(REPOSITORY_CLAIMS), "--version"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        default_prompts = manifest["interface"]["defaultPrompt"]

        self.assertEqual(manifest["version"], repository_claims_version)
        self.assertLessEqual(len(default_prompts), 3)
        self.assertTrue(all(len(prompt) <= 128 for prompt in default_prompts))


if __name__ == "__main__":
    unittest.main()
