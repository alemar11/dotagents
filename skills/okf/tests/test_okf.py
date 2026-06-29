from __future__ import annotations

import contextlib
import datetime as dt
import importlib.machinery
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "okf"


def load_okf_module():
    loader = importlib.machinery.SourceFileLoader("okf_script", str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise RuntimeError("failed to build okf script import spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


class OkfCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.okf = load_okf_module()

    def test_script_is_executable(self) -> None:
        self.assertTrue(os.access(SCRIPT, os.X_OK))
        self.assertEqual(SCRIPT.read_text(encoding="utf-8").splitlines()[0], "#!/usr/bin/env python3")

    def test_version(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as raised:
                self.okf.main(["--version"])
        self.assertEqual(raised.exception.code, 0)
        self.assertEqual(stdout.getvalue().strip(), "1.0.0")

    def test_doctor_json_shape(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = self.okf.main(["doctor", "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["version"], "1.0.0")
        self.assertIn("pyyaml", payload["checks"])

    def test_valid_spec_minimal_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "concept.md").write_text("---\ntype: Reference\n---\n\nBody.\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["validate", str(bundle), "--mode", "spec", "--json"])
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["concepts_checked"], 1)

    def test_block_list_frontmatter_does_not_crash_without_pyyaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "concept.md").write_text(
                "---\n"
                "type: Reference\n"
                "tags:\n"
                "  - sales\n"
                "  - metrics\n"
                "---\n\nBody.\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["validate", str(bundle), "--mode", "spec", "--json"])
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertTrue(payload["ok"])

    def test_valid_reference_agent_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "concept.md").write_text(
                "---\n"
                "type: Reference\n"
                "title: Concept\n"
                "description: A concept.\n"
                "timestamp: 2026-06-29T00:00:00Z\n"
                "---\n\nBody.\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["validate", str(bundle), "--mode", "reference-agent"])
            self.assertEqual(code, 0)

    def test_reference_agent_accepts_pyyaml_datetime_timestamp(self) -> None:
        class FakeYaml:
            @staticmethod
            def safe_load(_text):
                return {
                    "type": "Reference",
                    "title": "Concept",
                    "description": "A concept.",
                    "timestamp": dt.datetime(2026, 6, 29, tzinfo=dt.timezone.utc),
                }

        original_yaml = self.okf.yaml
        self.okf.yaml = FakeYaml
        try:
            with tempfile.TemporaryDirectory() as tmp:
                bundle = Path(tmp)
                (bundle / "concept.md").write_text(
                    "---\ntype: Reference\ntitle: Concept\ndescription: A concept.\ntimestamp: 2026-06-29T00:00:00Z\n---\n\nBody.\n",
                    encoding="utf-8",
                )
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    code = self.okf.main(["validate", str(bundle), "--mode", "reference-agent", "--json"])
                self.assertEqual(code, 0)
                self.assertTrue(json.loads(stdout.getvalue())["ok"])
        finally:
            self.okf.yaml = original_yaml

    def test_missing_type_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "concept.md").write_text("---\ntitle: Missing type\n---\n\nBody.\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["validate", str(bundle), "--json"])
            self.assertEqual(code, 65)
            payload = json.loads(stdout.getvalue())
            self.assertFalse(payload["ok"])
            self.assertIn("type", payload["errors"][0]["message"])

    def test_non_string_type_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "concept.md").write_text("---\ntype: [Reference]\n---\n\nBody.\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["validate", str(bundle), "--json"])
            self.assertEqual(code, 65)
            payload = json.loads(stdout.getvalue())
            self.assertFalse(payload["ok"])
            self.assertIn("non-empty strings", payload["errors"][0]["message"])

    def test_malformed_frontmatter_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "concept.md").write_text("---\ntype Reference\n---\n\nBody.\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["validate", str(bundle)])
            self.assertEqual(code, 65)

    def test_reserved_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "index.md").write_text("# Index\n\n* [Concept](concept.md)\n", encoding="utf-8")
            (bundle / "log.md").write_text("# Log\n\n## 2026-06-29\n* **Creation**: Start.\n", encoding="utf-8")
            (bundle / "concept.md").write_text("---\ntype: Reference\n---\n\nBody.\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(self.okf.main(["validate", str(bundle)]), 0)

    def test_invalid_log_heading_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "log.md").write_text("# Log\n\n## June 29\n* Bad.\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["validate", str(bundle)])
            self.assertEqual(code, 65)

    def test_invalid_reserved_index_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "index.md").write_text("This is arbitrary prose, not an index.\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["validate", str(bundle)])
            self.assertEqual(code, 65)

    def test_log_without_date_group_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "log.md").write_text("# Log\n\n* Missing date group.\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["validate", str(bundle)])
            self.assertEqual(code, 65)

    def test_strict_links_reject_targets_outside_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            bundle.mkdir()
            (root / "outside.md").write_text("---\ntype: Reference\n---\n", encoding="utf-8")
            (bundle / "concept.md").write_text(
                "---\ntype: Reference\n---\n\nSee [outside](../outside.md).\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["validate", str(bundle), "--strict-links", "--json"])
            self.assertEqual(code, 65)
            payload = json.loads(stdout.getvalue())
            self.assertFalse(payload["ok"])
            self.assertIn("Broken local markdown link", payload["errors"][0]["message"])

    def test_invalid_utf8_reports_validation_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "concept.md").write_bytes(b"\xff\xfe\x00")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["validate", str(bundle), "--json"])
            self.assertEqual(code, 65)
            payload = json.loads(stdout.getvalue())
            self.assertFalse(payload["ok"])
            self.assertIn("valid UTF-8", payload["errors"][0]["message"])

    def test_scaffold_overwrite_refusal_and_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            args = [
                "scaffold",
                str(bundle),
                "refs/example",
                "--type",
                "Reference",
                "--title",
                "Example",
            ]
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(self.okf.main(args), 0)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                self.assertEqual(self.okf.main(args), 73)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(self.okf.main(args + ["--force"]), 0)
            self.assertTrue((bundle / "refs" / "example.md").exists())

    def test_scaffold_quotes_yaml_sensitive_scalars(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(
                    [
                        "scaffold",
                        str(bundle),
                        "refs/api",
                        "--type",
                        "API Endpoint",
                        "--title",
                        "API: Create Order",
                        "--description",
                        "Creates an order # checkout",
                        "--timestamp",
                        "2026-06-29T00:00:00Z",
                        "--mode",
                        "reference-agent",
                    ]
                )
            self.assertEqual(code, 0)
            content = (bundle / "refs" / "api.md").read_text(encoding="utf-8")
            self.assertIn('title: "API: Create Order"', content)
            self.assertIn('description: "Creates an order # checkout"', content)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(self.okf.main(["validate", str(bundle), "--mode", "reference-agent"]), 0)

    def test_scaffold_rejects_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            outside = root / "outside"
            bundle.mkdir()
            outside.mkdir()
            try:
                os.symlink(outside, bundle / "refs")
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = self.okf.main(["scaffold", str(bundle), "refs/new", "--type", "Reference"])
            self.assertEqual(code, 64)
            self.assertFalse((outside / "new.md").exists())

    def test_reference_agent_scaffold_requires_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = self.okf.main(
                    ["scaffold", tmp, "refs/example", "--type", "Reference", "--mode", "reference-agent"]
                )
            self.assertEqual(code, 64)


if __name__ == "__main__":
    unittest.main()
