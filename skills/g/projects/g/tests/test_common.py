from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from g.common import GError, run


class CommonProcessTests(unittest.TestCase):
    def test_run_normalizes_spawn_permission_errors(self) -> None:
        with mock.patch.object(subprocess, "run", side_effect=PermissionError("denied")):
            with self.assertRaises(GError) as raised:
                run(["gh", "stack", "view"])

        self.assertEqual(raised.exception.code, "process_spawn_failed")
        self.assertEqual(raised.exception.exit_code, 126)
        self.assertEqual(raised.exception.details["upstream_command"], ["gh", "stack", "view"])
        self.assertNotIn("denied", str(raised.exception))

    def test_run_normalizes_missing_process(self) -> None:
        with mock.patch.object(subprocess, "run", side_effect=FileNotFoundError("missing")):
            with self.assertRaises(GError) as raised:
                run(["gh", "stack", "view"])

        self.assertEqual(raised.exception.code, "process_spawn_failed")
        self.assertEqual(raised.exception.exit_code, 127)

    def test_safe_diagnostic_redacts_and_bounds_provider_text(self) -> None:
        from g.common import safe_diagnostic

        diagnostic = safe_diagnostic("TOKEN=secret-value " + ("x" * 2500))
        assert diagnostic is not None
        self.assertNotIn("secret-value", diagnostic)
        self.assertLessEqual(len(diagnostic), 2001)


if __name__ == "__main__":
    unittest.main()
