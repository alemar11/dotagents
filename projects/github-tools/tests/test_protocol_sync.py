from __future__ import annotations

import hashlib
import runpy
import subprocess
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SYNC = ROOT / "projects" / "github-tools" / "scripts" / "sync-provider-protocol"
PROTOCOL = ROOT / "projects" / "github-tools" / "src" / "github_provider_protocol"
MANIFEST = ["common.py", "repository.py", "integrity.py", "provider_text.py"]
TARGETS = [
    ROOT / "skills" / "yeet" / "scripts" / "publish_lib",
    ROOT / "skills" / "github-review-threads" / "scripts" / "reviews_lib",
]


def _load_sync_module():
    return types.SimpleNamespace(**runpy.run_path(str(SYNC)))

class SyncRootAndCheckTests(unittest.TestCase):
    def test_repository_root_is_anchored_not_parent_depth(self) -> None:
        module = _load_sync_module()
        resolved = module.repository_root(SYNC)
        self.assertEqual(resolved, ROOT)
        # parents[2] from the script is projects/, which must not be treated as root.
        wrong = SYNC.resolve().parents[2]
        self.assertEqual(wrong.name, "projects")
        self.assertNotEqual(wrong, resolved)
        self.assertTrue((resolved / "skills").is_dir())
        self.assertTrue((resolved / "projects" / "github-tools").is_dir())

    def test_check_passes_for_current_copies(self) -> None:
        completed = subprocess.run(
            [str(SYNC), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("provider-protocol copies match canonical source", completed.stdout)

    def test_check_fails_when_a_copy_drifts(self) -> None:
        target = TARGETS[0] / "common.py"
        original = target.read_bytes()
        try:
            target.write_bytes(original + b"\n# drift\n")
            completed = subprocess.run(
                [str(SYNC), "--check"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 1)
            self.assertIn("drift:", completed.stderr)
        finally:
            target.write_bytes(original)

    def test_check_fails_when_root_would_point_at_projects(self) -> None:
        """A parents[2]-style root cannot see protocol or skill copies."""

        wrong_root = SYNC.resolve().parents[2]
        missing_protocol = wrong_root / "projects" / "github-tools" / "src" / "github_provider_protocol"
        self.assertFalse(missing_protocol.is_dir())
        for target in TARGETS:
            self.assertFalse((wrong_root / target.relative_to(ROOT)).exists())


class ProtocolByteIdentityTests(unittest.TestCase):
    def test_skill_copies_match_canonical_bytes(self) -> None:
        for name in MANIFEST:
            canonical = hashlib.sha256((PROTOCOL / name).read_bytes()).hexdigest()
            for target in TARGETS:
                copied = hashlib.sha256((target / name).read_bytes()).hexdigest()
                self.assertEqual(copied, canonical, f"{target / name} drifted")


if __name__ == "__main__":
    unittest.main()
