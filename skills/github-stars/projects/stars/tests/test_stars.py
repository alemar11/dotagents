from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from github_stars_cli import cli  # noqa: E402


class StarsContractTests(unittest.TestCase):
    def test_version(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(["--version"])
        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), "1.0.0")

    def test_json_doctor_shape(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.main(["--json", "doctor"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["version"], "1.0.0")
        self.assertIn("gh", payload["checks"])

    def test_invalid_command_json(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(["--json", "nope"])
        self.assertEqual(code, 64)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["ok"])


if __name__ == "__main__":
    unittest.main()
