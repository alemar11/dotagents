import json
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "extract_recent_transcript.py"


class ExtractRecentTranscriptTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_help_and_version_are_available(self) -> None:
        help_result = self.run_script("--help")
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("Resolve a Codex session UUID", help_result.stdout)

        version_result = self.run_script("--version")
        self.assertEqual(version_result.returncode, 0)
        self.assertEqual(version_result.stdout.strip(), "1.0.0")

    def test_json_doctor_resolves_an_explicit_rollout_path(self) -> None:
        session_id = str(uuid.uuid4())
        with tempfile.TemporaryDirectory() as temp_dir:
            rollout_path = Path(temp_dir) / f"rollout-test-{session_id}.jsonl"
            rollout_path.write_text("{}\n", encoding="utf-8")

            result = self.run_script("--json", "doctor", "--rollout-path", str(rollout_path))

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["session_id"], session_id)
        self.assertEqual(payload["rollout_path"], str(rollout_path))
        self.assertIn("agents_candidates", payload)
        self.assertIn("agents_suggestions", payload)

    def test_missing_rollout_path_is_nonzero_and_diagnostic(self) -> None:
        result = self.run_script("--rollout-path", "/tmp/project-context-missing-rollout.jsonl")

        self.assertEqual(result.returncode, 1)
        self.assertIn("[project-context]", result.stderr)
        self.assertIn("rollout path not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
