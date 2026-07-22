from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
CMD = SKILL_ROOT / "scripts" / "code-wiki"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from code_wiki.wiki_contract import REQUIRED_PAGES  # noqa: E402
from code_wiki.validation.diagrams import validate_polished_diagram_images  # noqa: E402
from code_wiki.validation.report import print_report  # noqa: E402
from code_wiki.validation.ui import validate_ui_patterns  # noqa: E402


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
        (repo / "README.md").write_text(
            "# Sample\n" + "\n".join(f"readme line {index}" for index in range(1, 180)) + "\n",
            encoding="utf-8",
        )
        (repo / "pyproject.toml").write_text("[project]\nname = \"sample\"\n", encoding="utf-8")
        (repo / "pkg" / "__init__.py").write_text("", encoding="utf-8")
        (repo / "pkg" / "main.py").write_text("def main():\n    return 'ok'\n", encoding="utf-8")
        (repo / "tests" / "test_main.py").write_text("def test_main():\n    assert True\n", encoding="utf-8")
        return repo

    def test_validation_report_emits_canonical_status_for_every_outcome(self) -> None:
        cases = (
            ([], [], "pass", "PASS"),
            ([], ["warning"], "pass-with-warnings", "PASS WITH WARNINGS"),
            (["error"], [], "fail", "FAIL"),
        )
        for errors, warnings, status, display in cases:
            with self.subTest(status=status), io.StringIO() as output, redirect_stdout(output):
                print_report(errors, warnings)
                self.assertTrue(
                    output.getvalue().startswith(
                        f"validation_status={status}\nValidation: {display}\n"
                    )
                )

    def evidence_blocks(self) -> str:
        anchors = "\n".join(
            f'<a class="evidence-chip" href="#" data-evidence="README.md:{line}" title="README.md:{line}">README.md:{line}</a>'
            for line in range(1, 11)
        )
        return "\n".join(f'<aside class="evidence">{anchors}</aside>' for _ in range(3))

    def valid_page_html(self, title: str) -> str:
        table = """
        <table>
          <tr><th>use case capability scenario user audience surface entry api command package route module constraint responsibility owner license security support public interface header export consumer caller usage file path stability contract internal state carrier lifecycle object store context create initialize allocated mutate update write change observe callback read event cleanup shutdown destroy release trigger failure condition edge detect branch function check handler effect status error recover retry fallback abort rollback task run script when scope source expected signal artifact output compatibility risk breaking validation test backout revert</th></tr>
          <tr><td>pkg tests generated vendor no license no security no support no codeowners absent official upstream docs</td></tr>
        </table>
        """
        paragraph = (
            "This sample page gives a scope mental model with boundary ownership, external out of scope notes, "
            "consumer caller entrypoint example details, public API interface header route command export surfaces, "
            "stable extension internal incidental contract usage binding behavior, component module subsystem "
            "interactions, collaborate call path lifecycle sequence, class struct protocol trait function type "
            "creators, calls, owners, mutations, registration, state context session handle storage lifecycle, "
            "thread lock async callback worker concurrency cache cleanup shutdown, dependency manifest build runtime "
            "package provider target boundaries, pattern convention abstraction layer error configuration extension, "
            "basic request startup flow step output, failure edge retry background integration branch condition cancel "
            "abort timeout overload fallback rollback, validation CI workflow operation deploy observability run command "
            "environment release lint, change modify extend debug add remove risk caveat collaborator first file start in "
            "responsibility directory file source root docs example generated third-party vendor."
        )
        repeated = " ".join([paragraph] * 4)
        return f"""<!doctype html>
<html><head><title>{title}</title></head><body><main>
<header><h1>{title}</h1></header>
<section><h2>Overview</h2><p>{repeated}</p>{table}</section>
<section><h2>Architecture</h2><p>{repeated}</p></section>
<section><h2>Flow</h2><p>{repeated}</p><pre><code>python -m unittest</code></pre></section>
<section><h2>Evidence</h2>{self.evidence_blocks()}</section>
</main></body></html>
"""

    def write_warning_only_wiki(self, wiki: Path) -> None:
        for rel in REQUIRED_PAGES:
            path = wiki / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(self.valid_page_html(rel), encoding="utf-8")

    def test_help_and_version_use_public_launcher(self) -> None:
        version = self.run_code_wiki("--version")
        self.assertEqual(version.returncode, 0, version.stderr)
        self.assertIn("code-wiki 0.8.0", version.stdout)

        help_result = self.run_code_wiki("--help")
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("synthesize", help_result.stdout)
        self.assertIn("evidence-link", help_result.stdout)
        self.assertIn("doctor", help_result.stdout)
        self.assertIn("pilot", help_result.stdout)

        pilot_help = self.run_code_wiki("pilot", "--help")
        self.assertEqual(pilot_help.returncode, 0, pilot_help.stderr)
        self.assertIn("run", pilot_help.stdout)
        self.assertIn("compare", pilot_help.stdout)
        self.assertIn("aggregate", pilot_help.stdout)
        self.assertNotIn("provenance", pilot_help.stdout)

        for invalid_args in (
            ("--json", "pilot", "run", "--mode", "invalid"),
            ("--json", "pilot", "run", "--mode", "baseline"),
        ):
            with self.subTest(invalid_args=invalid_args):
                invalid = self.run_code_wiki(*invalid_args)
                self.assertEqual(invalid.returncode, 2)
                self.assertEqual(invalid.stderr, "")
                payload = json.loads(invalid.stdout)
                self.assertFalse(payload["ok"])
                self.assertIn("argument error", payload["error"])

        validate_help = self.run_code_wiki("validate", "--help")
        self.assertEqual(validate_help.returncode, 0, validate_help.stderr)
        self.assertIn("--strict", validate_help.stdout)

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
            self.assertTrue((wiki / "data" / "claim-matrix.example.json").is_file())
            self.assertTrue((wiki / ".cache" / "sources").is_dir())
            self.assertEqual((wiki / ".cache" / ".gitignore").read_text(encoding="utf-8"), "*\n!.gitignore\n")

    def test_synthesize_writes_claim_matrix_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = self.create_sample_repo(tmp_path)
            inventory_path = tmp_path / "wiki" / "data" / "inventory.json"
            matrix_path = tmp_path / "wiki" / "data" / "claim-matrix.json"

            inventory = self.run_code_wiki("inventory", "--repo", str(repo), "--out", str(inventory_path))
            self.assertEqual(inventory.returncode, 0, inventory.stderr)
            result = self.run_code_wiki(
                "synthesize",
                "--repo",
                str(repo),
                "--inventory",
                str(inventory_path),
                "--out",
                str(matrix_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
            self.assertEqual(matrix["schema_version"], 1)
            self.assertEqual(matrix["repo"]["name"], "sample-repo")
            self.assertEqual(matrix["claims"], [])
            self.assertIn({"page": "pages/overview.html", "min_ready_claims": 2, "status": "pending"}, matrix["page_targets"])
            roots = {(item["root"], item["kind"]) for item in matrix["coverage_roots"]}
            self.assertIn(("pkg", "source"), roots)
            self.assertIn(("tests", "test"), roots)

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

            refs = Path(tmp) / "refs.txt"
            refs.write_text("README.md:1\nmissing.py:1\n", encoding="utf-8")
            batch = self.run_code_wiki(
                "evidence-link",
                "--batch",
                "--repo",
                str(repo),
                "--in",
                str(refs),
                "--html",
            )
            self.assertEqual(batch.returncode, 2)
            self.assertIn('class="evidence-chip"', batch.stdout)
            self.assertIn("NO_LINK: missing.py:1:", batch.stdout)

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

    def test_validate_reports_pass_with_warnings_for_warning_only_output(self) -> None:
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
            self.write_warning_only_wiki(wiki)

            result = self.run_code_wiki("validate", "--wiki", str(wiki))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(
                result.stdout.startswith(
                    "validation_status=pass-with-warnings\nValidation: PASS WITH WARNINGS"
                ),
                result.stdout,
            )

    def test_strict_validation_requires_claim_matrix_and_ready_claims(self) -> None:
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

            missing = self.run_code_wiki("validate", "--wiki", str(wiki), "--strict")
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("strict validation requires data/claim-matrix.json", missing.stdout)

            synthesize = self.run_code_wiki(
                "synthesize",
                "--repo",
                str(repo),
                "--inventory",
                str(wiki / "data" / "inventory.json"),
                "--out",
                str(wiki / "data" / "claim-matrix.json"),
            )
            self.assertEqual(synthesize.returncode, 0, synthesize.stderr)
            empty = self.run_code_wiki("validate", "--wiki", str(wiki), "--strict")
            self.assertNotEqual(empty.returncode, 0)
            self.assertIn("at least 2 ready, non-duplicate claims for pages/overview.html", empty.stdout)

    def test_strict_validation_catches_claim_matrix_quality_failures(self) -> None:
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

            matrix = {
                "schema_version": 1,
                "coverage_roots": [],
                "claims": [
                    {
                        "claim": "The same repeated architecture claim appears on multiple pages.",
                        "page": "pages/overview.html",
                        "evidence": ["README.md:1-150"],
                        "why_it_matters": "Maintainers need narrow evidence.",
                        "status": "ready",
                    },
                    {
                        "claim": "The same repeated architecture claim appears on multiple pages.",
                        "page": "pages/architecture.html",
                        "evidence": ["README.md:1-150"],
                        "why_it_matters": "Maintainers need narrow evidence.",
                        "status": "ready",
                    },
                    {
                        "claim": "A third page reuses the same broad source slice.",
                        "page": "pages/change-guide.html",
                        "evidence": ["README.md:1-150", "missing.py:1"],
                        "why_it_matters": "Maintainers need valid evidence.",
                        "status": "ready",
                    },
                ],
            }
            (wiki / "data" / "claim-matrix.json").write_text(
                json.dumps(matrix, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_code_wiki("validate", "--wiki", str(wiki), "--strict")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("relies only on broad evidence ranges", result.stdout)
            self.assertIn("broad evidence range README.md:1-150 is reused across more than two pages", result.stdout)
            self.assertIn("repeats the same ready claim across pages", result.stdout)
            self.assertIn("evidence path does not exist: missing.py", result.stdout)

    def test_polished_diagram_images_require_deterministic_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            page = wiki / "pages" / "architecture.html"
            (wiki / "pages").mkdir(parents=True)
            (wiki / "assets" / "images").mkdir(parents=True)
            (wiki / "assets" / "diagrams").mkdir(parents=True)
            (wiki / "assets" / "images" / "architecture-overview.png").write_text("fake", encoding="utf-8")
            page.write_text("", encoding="utf-8")

            missing_source = (
                '<img src="../assets/images/architecture-overview.png" '
                'alt="polished architecture diagram">'
            )
            errors: list[str] = []
            warnings: list[str] = []
            validate_polished_diagram_images(page, wiki, missing_source, False, errors, warnings)
            self.assertFalse(errors)
            self.assertIn("missing data-source-diagram", warnings[0])

            errors = []
            warnings = []
            validate_polished_diagram_images(page, wiki, missing_source, True, errors, warnings)
            self.assertIn("missing data-source-diagram", errors[0])

            (wiki / "assets" / "diagrams" / "architecture.svg").write_text(
                "<svg><text>Architecture</text></svg>",
                encoding="utf-8",
            )
            with_source = (
                '<img src="../assets/images/architecture-overview.png" '
                'alt="polished architecture diagram" '
                'data-source-diagram="../assets/diagrams/architecture.svg">'
            )
            errors = []
            warnings = []
            validate_polished_diagram_images(page, wiki, with_source, True, errors, warnings)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_ui_patterns_warn_or_fail_for_dense_non_collapsible_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            page = wiki / "pages" / "overview.html"
            (wiki / "pages").mkdir(parents=True)
            page.write_text("", encoding="utf-8")
            chips = "".join(
                f'<a class="evidence-chip" href="#" data-evidence="README.md:{line}">README.md:{line}</a>'
                for line in range(1, 13)
            )
            html_text = f"<main><section><aside class=\"evidence\">{chips}</aside></section></main>"

            errors: list[str] = []
            warnings: list[str] = []
            validate_ui_patterns(page, wiki, html_text, False, errors, warnings)
            self.assertFalse(errors)
            self.assertIn("no collapsible details.evidence", warnings[0])

            errors = []
            warnings = []
            validate_ui_patterns(page, wiki, html_text, True, errors, warnings)
            self.assertIn("no collapsible details.evidence", errors[0])


if __name__ == "__main__":
    unittest.main()
