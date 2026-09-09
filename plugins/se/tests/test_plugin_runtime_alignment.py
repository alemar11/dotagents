import json
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]


class PluginRuntimeAlignmentTests(unittest.TestCase):
    def test_plugin_manifests_are_aligned(self) -> None:
        manifest = json.loads(
            (PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        portable = json.loads((PLUGIN / "plugin.json").read_text(encoding="utf-8"))
        default_prompts = manifest["interface"]["defaultPrompt"]

        self.assertEqual(manifest["version"], portable["version"])
        self.assertEqual(manifest["name"], portable["name"])
        self.assertLessEqual(len(default_prompts), 3)
        self.assertTrue(all(len(prompt) <= 128 for prompt in default_prompts))


if __name__ == "__main__":
    unittest.main()
