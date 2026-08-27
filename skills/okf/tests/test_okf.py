from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock
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
        self.assertEqual(stdout.getvalue().strip(), "3.0.0")

    def test_doctor_json_shape(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = self.okf.main(["--json", "doctor"])
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["version"], "3.0.0")
        self.assertEqual(payload["spec_version"], "0.2")
        self.assertIn("pyyaml", payload["checks"])
        self.assertTrue(payload["checks"]["anchored_io"])

    def test_doctor_reports_missing_anchored_io(self) -> None:
        original_support = self.okf.ANCHORED_IO_SUPPORTED
        self.okf.ANCHORED_IO_SUPPORTED = False
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["--json", "doctor"])
            self.assertEqual(code, 69)
            payload = json.loads(stdout.getvalue())
            self.assertFalse(payload["ok"])
            self.assertFalse(payload["checks"]["anchored_io"])
        finally:
            self.okf.ANCHORED_IO_SUPPORTED = original_support

    def test_valid_spec_minimal_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "concept.md").write_text("---\ntype: Reference\n---\n\nBody.\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["--json", "validate", str(bundle)])
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["concepts_checked"], 1)
            self.assertNotIn("mode", payload)

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
                code = self.okf.main(["--json", "validate", str(bundle)])
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertTrue(payload["ok"])

    def test_indentationless_block_list_is_accepted_without_pyyaml(self) -> None:
        original_yaml = self.okf.yaml
        self.okf.yaml = None
        try:
            with tempfile.TemporaryDirectory() as tmp:
                bundle = Path(tmp)
                (bundle / "concept.md").write_text(
                    "---\n"
                    "type: Reference\n"
                    "tags:\n"
                    "- sales\n"
                    "- metrics\n"
                    "---\n\nBody.\n",
                    encoding="utf-8",
                )
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    code = self.okf.main(["--json", "validate", str(bundle)])
                self.assertEqual(code, 0)
                self.assertTrue(json.loads(stdout.getvalue())["ok"])
        finally:
            self.okf.yaml = original_yaml

    def test_valid_v02_provenance_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "concept.md").write_text(
                "---\n"
                "type: Reference\n"
                "title: Concept\n"
                "description: A concept.\n"
                'generated: {"by": "process:catalog-refresh", "at": "2026-06-29T00:00:00Z"}\n'
                "---\n\nBody.\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["validate", str(bundle)])
            self.assertEqual(code, 0)

    def test_noncanonical_timestamp_values_warn(self) -> None:
        class FakeYaml:
            @staticmethod
            def safe_load(_text):
                return {
                    "type": "Reference",
                    "timestamp": "2026-05-28",
                    "generated": {"at": "2026-06-29T10:00:00"},
                    "verified": [{"at": "2026-06-29"}],
                    "stale_after": "2026-09-29",
                    "sources": [
                        {
                            "last_modified": "2026-06-15",
                            "usage_window": {
                                "from": "2026-06-01",
                                "to": "2026-06-30",
                            },
                        }
                    ],
                    "usage_window": {
                        "from": "2026-06-01",
                        "to": "2026-06-30",
                    },
                }

        original_yaml = self.okf.yaml
        self.okf.yaml = FakeYaml
        try:
            with tempfile.TemporaryDirectory() as tmp:
                bundle = Path(tmp)
                (bundle / "concept.md").write_text(
                    "---\ntype: Reference\n---\n\nBody.\n",
                    encoding="utf-8",
                )
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    code = self.okf.main(["--json", "validate", str(bundle)])
                self.assertEqual(code, 0)
                messages = [
                    warning["message"]
                    for warning in json.loads(stdout.getvalue())["warnings"]
                ]
                for field_name in (
                    "timestamp",
                    "generated.at",
                    "verified[0].at",
                    "stale_after",
                    "sources[0].last_modified",
                    "sources[0].usage_window.from",
                    "sources[0].usage_window.to",
                    "usage_window.from",
                    "usage_window.to",
                ):
                    self.assertTrue(
                        any(message.startswith(field_name) for message in messages),
                        field_name,
                    )
        finally:
            self.okf.yaml = original_yaml

    def test_pyyaml_timestamp_validation_preserves_authored_spelling(self) -> None:
        if self.okf.yaml is None:
            self.skipTest("PyYAML is not installed")

        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            for name, value in (
                ("unquoted", "2026-06-29 12:00:00+00:00"),
                ("quoted", '"2026-06-29 12:00:00+00:00"'),
            ):
                (bundle / f"{name}.md").write_text(
                    f"---\ntype: Reference\nstale_after: {value}\n---\n\nBody.\n",
                    encoding="utf-8",
                )

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["--json", "validate", str(bundle)])
            self.assertEqual(code, 0)
            warnings = [
                warning
                for warning in json.loads(stdout.getvalue())["warnings"]
                if warning["message"].startswith("stale_after")
            ]
            self.assertEqual(
                [warning["path"] for warning in warnings],
                ["quoted.md", "unquoted.md"],
            )
            self.assertTrue(
                all(warning["message"].startswith("stale_after") for warning in warnings)
            )

    def test_pyyaml_nested_v02_frontmatter_is_accepted(self) -> None:
        class FakeYaml:
            @staticmethod
            def safe_load(_text):
                return {
                    "type": "Reference",
                    "title": "Concept",
                    "description": "A concept.",
                    "generated": {
                        "by": "process:catalog-refresh",
                        "at": "2026-06-29T00:00:00Z",
                    },
                    "sources": [{"resource": "https://example.com/source"}],
                }

        original_yaml = self.okf.yaml
        self.okf.yaml = FakeYaml
        try:
            with tempfile.TemporaryDirectory() as tmp:
                bundle = Path(tmp)
                (bundle / "concept.md").write_text(
                    "---\ntype: Reference\ntitle: Concept\ndescription: A concept.\n"
                    "generated:\n  by: process:catalog-refresh\n  at: 2026-06-29T00:00:00Z\n"
                    "sources:\n  - resource: https://example.com/source\n---\n\nBody.\n",
                    encoding="utf-8",
                )
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    code = self.okf.main(["--json", "validate", str(bundle)])
                self.assertEqual(code, 0)
                self.assertTrue(json.loads(stdout.getvalue())["ok"])
        finally:
            self.okf.yaml = original_yaml

    def test_limited_parser_fails_closed_on_nested_yaml(self) -> None:
        original_yaml = self.okf.yaml
        self.okf.yaml = None
        try:
            with tempfile.TemporaryDirectory() as tmp:
                bundle = Path(tmp)
                (bundle / "concept.md").write_text(
                    "---\n"
                    "type: Reference\n"
                    "generated:\n"
                    "  by: process:catalog-refresh\n"
                    "  at: 2026-06-29T00:00:00Z\n"
                    "---\n\nBody.\n",
                    encoding="utf-8",
                )
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    code = self.okf.main(["--json", "validate", str(bundle)])
                self.assertEqual(code, 65)
                payload = json.loads(stdout.getvalue())
                self.assertFalse(payload["ok"])
                self.assertIn("nested YAML", payload["errors"][0]["message"])
        finally:
            self.okf.yaml = original_yaml

    def test_limited_parser_rejects_block_mapping_with_empty_value(self) -> None:
        original_yaml = self.okf.yaml
        self.okf.yaml = None
        try:
            with tempfile.TemporaryDirectory() as tmp:
                bundle = Path(tmp)
                (bundle / "concept.md").write_text(
                    "---\n"
                    "type: Reference\n"
                    "sources:\n"
                    "- resource:\n"
                    "---\n\nBody.\n",
                    encoding="utf-8",
                )
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    code = self.okf.main(["--json", "validate", str(bundle)])
                self.assertEqual(code, 65)
                payload = json.loads(stdout.getvalue())
                self.assertIn("nested mappings", payload["errors"][0]["message"])
        finally:
            self.okf.yaml = original_yaml

    def test_missing_type_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "concept.md").write_text("---\ntitle: Missing type\n---\n\nBody.\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["--json", "validate", str(bundle)])
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
                code = self.okf.main(["--json", "validate", str(bundle)])
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
                code = self.okf.main(["--json", "validate", str(bundle), "--strict-links"])
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
                code = self.okf.main(["--json", "validate", str(bundle)])
            self.assertEqual(code, 65)
            payload = json.loads(stdout.getvalue())
            self.assertFalse(payload["ok"])
            self.assertIn("valid UTF-8", payload["errors"][0]["message"])

    def test_validate_rejects_markdown_symlink_escape_without_reading_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            bundle.mkdir()
            outside = root / "outside.md"
            outside.write_text("outside-secret\n", encoding="utf-8")
            try:
                os.symlink(outside, bundle / "concept.md")
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["--json", "validate", str(bundle)])
            self.assertEqual(code, 65)
            payload = json.loads(stdout.getvalue())
            self.assertFalse(payload["ok"])
            self.assertIn("symlink", payload["errors"][0]["message"].lower())
            self.assertNotIn("outside-secret", stdout.getvalue())

    def test_validate_rejects_symlinked_directory_without_traversing_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            outside = root / "outside"
            bundle.mkdir()
            outside.mkdir()
            (outside / "concept.md").write_text(
                "---\ntype: Reference\n---\n\noutside-secret\n",
                encoding="utf-8",
            )
            try:
                os.symlink(outside, bundle / "refs")
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["--json", "validate", str(bundle)])
            self.assertEqual(code, 65)
            payload = json.loads(stdout.getvalue())
            self.assertFalse(payload["ok"])
            self.assertIn("symlinks", payload["errors"][0]["message"])
            self.assertNotIn("outside-secret", stdout.getvalue())

    def test_validate_rejects_symlinked_bundle_root_without_traversing_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside"
            bundle = root / "bundle"
            outside.mkdir()
            (outside / "concept.md").write_text(
                "---\ntype: Reference\n---\n\noutside-secret\n",
                encoding="utf-8",
            )
            try:
                os.symlink(outside, bundle)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(["--json", "validate", str(bundle)])
            self.assertEqual(code, 65)
            payload = json.loads(stdout.getvalue())
            self.assertFalse(payload["ok"])
            self.assertIn("Bundle root", payload["errors"][0]["message"])
            self.assertNotIn("outside-secret", stdout.getvalue())

    def test_validate_read_stays_anchored_during_parent_swap(self) -> None:
        if not self.okf.supports_anchored_io():
            self.skipTest("directory-relative file descriptors are unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            refs = bundle / "refs"
            moved = bundle / "refs-moved"
            outside = root / "outside"
            refs.mkdir(parents=True)
            outside.mkdir()
            (refs / "concept.md").write_text(
                "---\ntype: Reference\n---\n\nSafe body.\n",
                encoding="utf-8",
            )
            (outside / "concept.md").write_text("outside-secret\n", encoding="utf-8")
            original_open = os.open
            swapped = False

            def swapping_open(file, flags, mode=0o777, *, dir_fd=None):
                nonlocal swapped
                if file == "concept.md" and dir_fd is not None and not swapped:
                    swapped = True
                    os.rename(refs, moved)
                    os.symlink(outside, refs)
                return original_open(file, flags, mode, dir_fd=dir_fd)

            stdout = io.StringIO()
            with mock.patch.object(self.okf.os, "open", side_effect=swapping_open):
                with contextlib.redirect_stdout(stdout):
                    code = self.okf.main(["--json", "validate", str(bundle)])
            self.assertEqual(code, 0)
            self.assertTrue(swapped)
            self.assertNotIn("outside-secret", stdout.getvalue())

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
                        "--generated-by",
                        "process:catalog-refresh",
                        "--generated-at",
                        "2026-06-29T00:00:00Z",
                    ]
                )
            self.assertEqual(code, 0)
            content = (bundle / "refs" / "api.md").read_text(encoding="utf-8")
            self.assertIn('title: "API: Create Order"', content)
            self.assertIn('description: "Creates an order # checkout"', content)
            self.assertIn(
                'generated: {"by": "process:catalog-refresh", "at": "2026-06-29T00:00:00Z"}',
                content,
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(self.okf.main(["validate", str(bundle)]), 0)

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

    def test_scaffold_rejects_symlinked_bundle_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside"
            bundle = root / "bundle"
            outside.mkdir()
            try:
                os.symlink(outside, bundle)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(
                    [
                        "--json",
                        "scaffold",
                        str(bundle),
                        "concept",
                        "--type",
                        "Reference",
                    ]
                )
            self.assertEqual(code, 64)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["error"]["code"], "unsafe_path")
            self.assertFalse((outside / "concept.md").exists())

    def test_scaffold_force_rejects_existing_leaf_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            bundle.mkdir()
            outside = root / "outside.md"
            outside.write_text("preserve\n", encoding="utf-8")
            try:
                os.symlink(outside, bundle / "concept.md")
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(
                    [
                        "--json",
                        "scaffold",
                        str(bundle),
                        "concept",
                        "--type",
                        "Reference",
                        "--force",
                    ]
                )
            self.assertEqual(code, 64)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["error"]["code"], "unsafe_path")
            self.assertEqual(outside.read_text(encoding="utf-8"), "preserve\n")

    def test_scaffold_rejects_dangling_leaf_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            bundle.mkdir()
            outside = root / "missing.md"
            try:
                os.symlink(outside, bundle / "concept.md")
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not available on this filesystem")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(
                    [
                        "--json",
                        "scaffold",
                        str(bundle),
                        "concept",
                        "--type",
                        "Reference",
                    ]
                )
            self.assertEqual(code, 64)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["error"]["code"], "unsafe_path")
            self.assertFalse(outside.exists())

    def test_scaffold_write_stays_anchored_during_parent_swap(self) -> None:
        if not self.okf.supports_anchored_io():
            self.skipTest("directory-relative file descriptors are unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            refs = bundle / "refs"
            moved = bundle / "refs-moved"
            outside = root / "outside"
            refs.mkdir(parents=True)
            outside.mkdir()
            original_open = os.open
            swapped = False

            def swapping_open(file, flags, mode=0o777, *, dir_fd=None):
                nonlocal swapped
                if file == "example.md" and dir_fd is not None and not swapped:
                    swapped = True
                    os.rename(refs, moved)
                    os.symlink(outside, refs)
                return original_open(file, flags, mode, dir_fd=dir_fd)

            stdout = io.StringIO()
            with mock.patch.object(self.okf.os, "open", side_effect=swapping_open):
                with contextlib.redirect_stdout(stdout):
                    code = self.okf.main(
                        [
                            "--json",
                            "scaffold",
                            str(bundle),
                            "refs/example",
                            "--type",
                            "Reference",
                        ]
                    )
            self.assertEqual(code, 0)
            self.assertTrue(swapped)
            self.assertFalse((outside / "example.md").exists())
            self.assertTrue((moved / "example.md").exists())

    def test_scaffold_generation_fields_must_be_paired(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = self.okf.main(
                    [
                        "--json",
                        "scaffold",
                        tmp,
                        "refs/example",
                        "--type",
                        "Reference",
                        "--generated-by",
                        "process:catalog-refresh",
                    ]
                )
            self.assertEqual(code, 64)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["error"]["code"], "invalid_generation")
            self.assertEqual(payload["error"]["exit_code"], 64)
            self.assertEqual(stderr.getvalue(), "")

    def test_scaffold_rejects_invalid_generated_at(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(
                    [
                        "--json",
                        "scaffold",
                        tmp,
                        "refs/example",
                        "--type",
                        "Reference",
                        "--generated-by",
                        "process:catalog-refresh",
                        "--generated-at",
                        "yesterday",
                    ]
                )
            self.assertEqual(code, 64)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["error"]["code"], "invalid_generation")
            self.assertFalse((Path(tmp) / "refs" / "example.md").exists())

    def test_scaffold_rejects_generated_at_without_offset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(
                    [
                        "--json",
                        "scaffold",
                        tmp,
                        "refs/example",
                        "--type",
                        "Reference",
                        "--generated-by",
                        "process:catalog-refresh",
                        "--generated-at",
                        "2026-06-29T12:00:00",
                    ]
                )
            self.assertEqual(code, 64)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["error"]["code"], "invalid_generation")
            self.assertIn("explicit UTC offset", payload["error"]["message"])
            self.assertFalse((Path(tmp) / "refs" / "example.md").exists())

    def test_scaffold_invalid_utf8_body_is_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            body_file = root / "body.md"
            bundle = root / "bundle"
            body_file.write_bytes(b"\xff\xfe")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = self.okf.main(
                    [
                        "--json",
                        "scaffold",
                        str(bundle),
                        "refs/example",
                        "--type",
                        "Reference",
                        "--body-file",
                        str(body_file),
                    ]
                )
            self.assertEqual(code, 65)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["error"]["code"], "invalid_utf8")
            self.assertEqual(stderr.getvalue(), "")
            self.assertFalse((bundle / "refs" / "example.md").exists())

    def test_scaffold_json_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = self.okf.main(
                    ["--json", "scaffold", tmp, "refs/example", "--type", "Reference"]
                )
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["version"], "3.0.0")
            self.assertEqual(payload["spec_version"], "0.2")
            self.assertTrue(Path(payload["path"]).exists())

    def test_retired_mode_is_rejected_as_json(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                self.okf.main(["--json", "validate", ".", "--mode", "reference-agent"])
        self.assertEqual(raised.exception.code, 2)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "invalid_arguments")
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
