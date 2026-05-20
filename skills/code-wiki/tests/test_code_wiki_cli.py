from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
CMD = SKILL_ROOT / "scripts" / "code-wiki"


class CodeWikiCliTests(unittest.TestCase):
    def run_code_wiki(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(CMD), *args],
            cwd=str(cwd or SKILL_ROOT),
            text=True,
            capture_output=True,
            check=False,
        )

    def create_sample_repo(self, root: Path) -> Path:
        repo = root / "sample-repo"
        (repo / "pkg").mkdir(parents=True)
        (repo / "tests").mkdir()
        (repo / "README.md").write_text("# Sample\n", encoding="utf-8")
        (repo / "pyproject.toml").write_text("[project]\nname = \"sample\"\n", encoding="utf-8")
        (repo / "pkg" / "__init__.py").write_text("", encoding="utf-8")
        (repo / "pkg" / "main.py").write_text("def main():\n    return 'ok'\n", encoding="utf-8")
        (repo / "tests" / "test_main.py").write_text("def test_main():\n    assert True\n", encoding="utf-8")
        return repo

    def test_help_and_version_use_public_launcher(self) -> None:
        version = self.run_code_wiki("--version")
        self.assertEqual(version.returncode, 0, version.stderr)
        self.assertIn("code-wiki 0.4.0", version.stdout)

        help_result = self.run_code_wiki("--help")
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("{inventory,scaffold,validate,evidence-link}", help_result.stdout)

    def test_inventory_writes_expected_repo_metadata_and_roots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = self.create_sample_repo(tmp_path)
            out = tmp_path / "wiki" / "data" / "inventory.json"

            result = self.run_code_wiki("inventory", "--repo", str(repo), "--out", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)

            inventory = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(inventory["repo"]["name"], "sample-repo")
            self.assertEqual(inventory["repo"]["path"], str(repo.resolve()))
            self.assertFalse(inventory["repo"]["is_git_worktree"])
            self.assertIn("pyproject.toml", inventory["manifests"])
            self.assertIn("pkg", inventory["source_roots"])
            self.assertIn("tests", inventory["test_roots"])

    def test_scaffold_creates_required_assets_and_local_source_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"

            result = self.run_code_wiki(
                "scaffold",
                "--out",
                str(wiki),
                "--title",
                "Sample",
                "--local-source-cache",
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            self.assertTrue((wiki / "index.html").is_file())
            self.assertTrue((wiki / "pages" / "overview.html").is_file())
            self.assertTrue((wiki / "assets" / "style.css").is_file())
            self.assertTrue((wiki / "assets" / "app.js").is_file())
            self.assertTrue((wiki / ".cache" / "sources").is_dir())
            self.assertEqual((wiki / ".cache" / ".gitignore").read_text(encoding="utf-8"), "*\n!.gitignore\n")

    @unittest.skipIf(shutil.which("git") is None, "git is required for evidence-link source URL tests")
    def test_evidence_link_rejects_bad_refs_and_renders_github_chip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
            (repo / "README.md").write_text("# Repo\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(["git", "remote", "add", "origin", "https://github.com/acme/demo.git"], cwd=repo, check=True)

            bad = self.run_code_wiki("evidence-link", "--repo", str(repo), "--evidence", "../README.md:1")
            self.assertEqual(bad.returncode, 2)
            self.assertIn("NO_LINK:", bad.stdout)

            chip = self.run_code_wiki(
                "evidence-link",
                "--repo",
                str(repo),
                "--evidence",
                "README.md:1",
                "--html",
            )
            self.assertEqual(chip.returncode, 0, chip.stderr)
            self.assertIn('class="evidence-chip"', chip.stdout)
            self.assertIn("https://github.com/acme/demo/blob/", chip.stdout)
            self.assertIn("README.md#L1", chip.stdout)

    def test_validate_fails_placeholders_and_empty_evidence_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = self.create_sample_repo(tmp_path)
            wiki = tmp_path / "wiki"

            inventory = self.run_code_wiki(
                "inventory",
                "--repo",
                str(repo),
                "--out",
                str(wiki / "data" / "inventory.json"),
            )
            self.assertEqual(inventory.returncode, 0, inventory.stderr)
            scaffold = self.run_code_wiki("scaffold", "--out", str(wiki), "--title", "Sample")
            self.assertEqual(scaffold.returncode, 0, scaffold.stderr)

            untouched = self.run_code_wiki("validate", "--wiki", str(wiki))
            self.assertNotEqual(untouched.returncode, 0)
            self.assertIn("still contains scaffold placeholder text", untouched.stdout)

            overview = wiki / "pages" / "overview.html"
            overview.write_text(
                overview.read_text(encoding="utf-8").replace(
                    "</main>",
                    '<aside class="evidence">README.md:1</aside>\n</main>',
                    1,
                ),
                encoding="utf-8",
            )
            missing_link = self.run_code_wiki("validate", "--wiki", str(wiki))
            self.assertNotEqual(missing_link.returncode, 0)
            self.assertIn("evidence block 1 has no clickable evidence links", missing_link.stdout)


if __name__ == "__main__":
    unittest.main()

