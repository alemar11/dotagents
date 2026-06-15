from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "portfolio-scan"
loader = importlib.machinery.SourceFileLoader("portfolio_scan_script", str(SCRIPT_PATH))
spec = importlib.util.spec_from_loader(loader.name, loader)
assert spec is not None
cli = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = cli
loader.exec_module(cli)


class PortfolioScanContractTests(unittest.TestCase):
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

    def test_validate_repo(self) -> None:
        self.assertEqual(cli.validate_repo("owner/repo"), "owner/repo")
        with self.assertRaises(cli.PortfolioError):
            cli.validate_repo("bad")


if __name__ == "__main__":
    unittest.main()
