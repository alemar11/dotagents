from __future__ import annotations

import importlib.util
import io
import stat
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_ROOT = REPO_ROOT / ".agents" / "skills" / "maintainer" / "scripts"


def load_script(name: str):
    path = SCRIPT_ROOT / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"maintainer_{name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MaintainerRefreshScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.api = load_script("swift_api_design_refresh")
        cls.docc = load_script("swift_docc_refresh")
        cls.okf = load_script("okf_spec_refresh")

    def test_staleness_can_be_a_strict_gate(self) -> None:
        for module in (self.api, self.docc, self.okf):
            self.assertEqual(module.stale_exit_code([], True), 0)
            self.assertEqual(module.stale_exit_code(["stale"], False), 0)
            self.assertEqual(module.stale_exit_code(["stale"], True), 1)

    def test_atomic_writes_preserve_existing_file_mode(self) -> None:
        for module in (self.api, self.docc, self.okf):
            with tempfile.TemporaryDirectory() as temporary_dir:
                target = Path(temporary_dir) / "asset"
                target.write_text("old", encoding="utf-8")
                target.chmod(0o644)
                module.atomic_write_text(target, "new")
                self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o644)

    def test_docc_rejects_unsafe_archive_members(self) -> None:
        payload = io.BytesIO()
        with tarfile.open(fileobj=payload, mode="w:gz") as archive:
            member = tarfile.TarInfo("../outside.txt")
            member.size = 1
            archive.addfile(member, io.BytesIO(b"x"))
        payload.seek(0)

        with tempfile.TemporaryDirectory() as temporary_dir:
            destination = Path(temporary_dir) / "extract"
            destination.mkdir()
            with tarfile.open(fileobj=payload, mode="r:gz") as archive:
                with self.assertRaises(ValueError):
                    self.docc.safe_extract(archive, destination)

    def test_docc_extracts_regular_archive_members(self) -> None:
        payload = io.BytesIO()
        with tarfile.open(fileobj=payload, mode="w:gz") as archive:
            member = tarfile.TarInfo("root/file.txt")
            member.size = 5
            archive.addfile(member, io.BytesIO(b"hello"))
        payload.seek(0)

        with tempfile.TemporaryDirectory() as temporary_dir:
            destination = Path(temporary_dir) / "extract"
            destination.mkdir()
            with tarfile.open(fileobj=payload, mode="r:gz") as archive:
                self.docc.safe_extract(archive, destination)
            self.assertEqual(
                (destination / "root/file.txt").read_text(encoding="utf-8"),
                "hello",
            )

    def test_docc_staged_commit_restores_previous_outputs_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            target_dir = root / "asset-tree"
            target_dir.mkdir()
            (target_dir / "old.txt").write_text("old", encoding="utf-8")
            target_file = root / "manifest.json"
            target_file.write_text("old-manifest", encoding="utf-8")

            staged_dir = root / "staged-asset-tree"
            staged_dir.mkdir()
            (staged_dir / "new.txt").write_text("new", encoding="utf-8")
            missing_stage = root / "missing-source-map.md"

            with self.assertRaises(FileNotFoundError):
                self.docc.commit_staged_outputs(
                    [
                        (staged_dir, target_dir),
                        (missing_stage, target_file),
                    ]
                )

            self.assertEqual(
                (target_dir / "old.txt").read_text(encoding="utf-8"),
                "old",
            )
            self.assertFalse((target_dir / "new.txt").exists())
            self.assertEqual(target_file.read_text(encoding="utf-8"), "old-manifest")

    def test_api_refresh_downloads_the_resolved_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            assets = root / "assets"
            source = assets / "api-design-guidelines.md"
            manifest = assets / "manifest.json"
            with (
                patch.object(self.api, "ASSETS_DIR", assets),
                patch.object(self.api, "ASSET_SOURCE_PATH", source),
                patch.object(self.api, "ASSET_MANIFEST_PATH", manifest),
                patch.object(self.api, "resolve_commit", return_value="resolved-commit"),
                patch.object(self.api, "load_manifest", return_value={}),
                patch.object(self.api, "download_text", return_value="source") as download,
                patch.object(self.api, "write_manifest"),
                patch.object(sys, "argv", ["swift_api_design_refresh.py", "--force"]),
            ):
                self.assertEqual(self.api.main(), 0)

            self.assertIn(
                "/resolved-commit/",
                download.call_args.args[0],
            )

    def test_docc_refresh_passes_the_resolved_commit_to_archive_download(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            assets = root / "assets"
            references = root / "references"
            with (
                patch.object(self.docc, "ASSETS_DIR", assets),
                patch.object(self.docc, "ASSET_DOCC_DIR", assets / "DocCDocumentation.docc"),
                patch.object(self.docc, "ASSET_MANIFEST_PATH", assets / "manifest.json"),
                patch.object(self.docc, "SOURCE_MAP_PATH", references / "source-map.md"),
                patch.object(self.docc, "resolve_commit", return_value="resolved-commit"),
                patch.object(self.docc, "load_catalog", return_value={"topics": [], "intents": []}),
                patch.object(self.docc, "load_manifest", return_value={}),
                patch.object(
                    self.docc,
                    "refresh_assets",
                    return_value=(root / "staged-assets", 0),
                ) as refresh_assets,
                patch.object(self.docc, "commit_staged_outputs"),
                patch.object(self.docc, "cleanup_legacy_outputs"),
                patch.object(sys, "argv", ["swift_docc_refresh.py", "--force"]),
            ):
                self.assertEqual(self.docc.main(), 0)

            self.assertEqual(refresh_assets.call_args.args[2], "resolved-commit")


if __name__ == "__main__":
    unittest.main()
