from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "ci-inspect"
loader = importlib.machinery.SourceFileLoader("ci_inspect_script", str(SCRIPT_PATH))
spec = importlib.util.spec_from_loader(loader.name, loader)
assert spec is not None
cli = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = cli
loader.exec_module(cli)


class CiInspectContractTests(unittest.TestCase):
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
        self.assertIn("git", payload["checks"])
        self.assertIn("gh", payload["checks"])

    def test_invalid_repo_reference(self) -> None:
        with self.assertRaises(cli.InspectionError):
            cli.validate_repo_reference("not-valid")

    def test_json_error_shape(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(["--json", "--repo", "bad", "--allow-non-project"])
        self.assertEqual(code, 64)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["version"], "1.0.0")
        self.assertEqual(payload["command"], ["inspect"])
        self.assertIn("message", payload["error"])


if __name__ == "__main__":
    unittest.main()
