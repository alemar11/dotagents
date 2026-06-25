from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "reviews"
loader = importlib.machinery.SourceFileLoader("reviews_script", str(SCRIPT_PATH))
spec = importlib.util.spec_from_loader(loader.name, loader)
assert spec is not None
cli = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = cli
loader.exec_module(cli)


class ReviewsContractTests(unittest.TestCase):
    def test_version(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(["--version"])
        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), "1.1.0")

    def test_json_doctor_shape(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.main(["--json", "doctor"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["version"], "1.1.0")
        self.assertIn("git", payload["checks"])
        self.assertIn("gh", payload["checks"])

    def test_positive_int(self) -> None:
        self.assertEqual(cli.positive_int("12", "pr"), 12)
        with self.assertRaises(cli.ReviewError):
            cli.positive_int("0", "pr")

    def test_comment_dry_run_json_shape(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(
                [
                    "--json",
                    "comment",
                    "--repo",
                    "owner/repo",
                    "--pr",
                    "12",
                    "--body",
                    "@codex please review this PR.",
                    "--dry-run",
                ]
            )
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["version"], "1.1.0")
        self.assertEqual(payload["command"], ["comment"])
        self.assertEqual(payload["data"]["repo"], "owner/repo")
        self.assertEqual(payload["data"]["pr"], 12)
        self.assertEqual(payload["data"]["action"]["status"], "dry-run")
        self.assertEqual(payload["data"]["action"]["type"], "conversation_comment")

    def test_read_body_from_file(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as handle:
            handle.write("hello from file")
            handle.flush()
            self.assertEqual(cli.read_body(None, handle.name), "hello from file")

    def test_read_body_rejects_ambiguous_input(self) -> None:
        with self.assertRaises(cli.ReviewError):
            cli.read_body("body", "message.md")


if __name__ == "__main__":
    unittest.main()
