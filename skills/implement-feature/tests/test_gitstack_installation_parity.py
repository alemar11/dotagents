from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
TOOL = ROOT / "scripts/gitstack-installation-parity"
LOADER = importlib.machinery.SourceFileLoader("gitstack_installation_parity", str(TOOL))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
PARITY = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(PARITY)


class GitStackInstallationParityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.root = self.home / ".codex/plugins/cache/alemar11/gitstack/6.0.0"
        source = REPO / "plugins/gitstack"
        for relative in (".codex-plugin/plugin.json", "projects/gitstack/pyproject.toml", "scripts/gitstack", "skills/github-review-threads/SKILL.md"):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / relative, target)
        self.skill = self.root / "skills/github-review-threads/SKILL.md"

    def verify(self) -> dict:
        return PARITY.verify(str(self.skill), home=self.home)

    def test_exact_installed_600_passes_deterministically(self) -> None:
        self.assertEqual(self.verify(), self.verify())
        self.assertEqual(self.verify()["cli_version"], "6.0.0")

    def test_old_411_and_fake_600_hash_mismatch_reject(self) -> None:
        manifest = self.root / ".codex-plugin/plugin.json"
        manifest.write_text(manifest.read_text().replace('"6.0.0"', '"4.1.1"', 1))
        with self.assertRaisesRegex(PARITY.ParityError, "required 6.0.0"):
            self.verify()
        manifest.write_text((REPO / "plugins/gitstack/.codex-plugin/plugin.json").read_text())
        (self.root / "scripts/gitstack").write_bytes(b"fake")
        with self.assertRaisesRegex(PARITY.ParityError, "cannot report|required 6.0.0"):
            self.verify()

    def test_manifest_cli_disagreement_source_substitution_and_missing_provenance_reject(self) -> None:
        package = self.root / "projects/gitstack/pyproject.toml"
        package.write_text(package.read_text().replace('version = "6.0.0"', 'version = "4.1.1"'))
        with self.assertRaises(PARITY.ParityError):
            self.verify()
        with self.assertRaises(PARITY.ParityError):
            PARITY.verify(str(REPO / "plugins/gitstack/skills/github-review-threads/SKILL.md"), home=self.home)
        with self.assertRaisesRegex(PARITY.ParityError, "App did not provide"):
            PARITY.verify(None, home=self.home)

    def test_symlink_escape_rejects(self) -> None:
        self.skill.unlink()
        self.skill.symlink_to(REPO / "plugins/gitstack/skills/github-review-threads/SKILL.md")
        with self.assertRaisesRegex(PARITY.ParityError, "symlink"):
            self.verify()
