from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "portfolio-health"


def load_script_module():
    loader = importlib.machinery.SourceFileLoader("portfolio_health", str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise RuntimeError("could not create portfolio-health module spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


PORTFOLIO_HEALTH = load_script_module()


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SCRIPT), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def write_skill(root: Path, name: str, body: str) -> Path:
    skill = root / name / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        f"---\nname: {name}\ndescription: Fixture for {name}.\n---\n\n{body}\n",
        encoding="utf-8",
    )
    return skill


class PortfolioHealthTests(unittest.TestCase):
    def test_inventory_source_defaults_to_auto(self) -> None:
        args = PORTFOLIO_HEALTH.build_parser().parse_args([])

        self.assertEqual(args.inventory_source, "auto")

    def test_default_roots_follow_the_nearest_git_root(self) -> None:
        with TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            nested = repo / "skills" / "skill-audit"
            (repo / ".git").mkdir(parents=True)
            nested.mkdir(parents=True)

            roots = PORTFOLIO_HEALTH.default_roots(nested)

        self.assertEqual(roots[0], repo.resolve() / "skills")
        self.assertEqual(roots[1], repo.resolve() / ".agents" / "skills")

    def test_default_roots_keep_non_git_cwd_scope(self) -> None:
        with TemporaryDirectory() as temp:
            cwd = Path(temp) / "caller"
            cwd.mkdir()

            roots = PORTFOLIO_HEALTH.default_roots(cwd)

        self.assertEqual(roots[0], cwd / "skills")
        self.assertEqual(roots[1], cwd / ".agents" / "skills")

    def test_explicit_root_forces_filesystem_scope(self) -> None:
        with TemporaryDirectory() as temp:
            base = Path(temp)
            scoped = base / "scoped"
            outside = base / "outside"
            write_skill(scoped, "inside", "inside")
            outside_skill = write_skill(outside, "outside", "outside")
            live_record = PORTFOLIO_HEALTH.read_skill(
                outside_skill,
                "codex-debug-prompt-input",
                root=str(outside),
            )
            assert live_record is not None
            args = PORTFOLIO_HEALTH.build_parser().parse_args(
                ["scan", "--no-logs", "--root", str(scoped)]
            )

            with mock.patch.object(
                PORTFOLIO_HEALTH,
                "live_inventory",
                return_value=PORTFOLIO_HEALTH.InventoryResult(
                    [live_record],
                    "codex-debug-prompt-input",
                    (),
                    (str(outside),),
                ),
            ) as live_inventory:
                data = PORTFOLIO_HEALTH.build_report(args)

        live_inventory.assert_not_called()
        self.assertEqual(data["inventory_source"], "filesystem")
        self.assertEqual(data["requested_roots"], [str(scoped)])
        self.assertEqual(data["effective_roots"], [str(scoped)])
        self.assertEqual([item["name"] for item in data["skills"]], ["inside"])

    def test_partial_live_inventory_falls_back_with_diagnostics(self) -> None:
        with TemporaryDirectory() as temp:
            valid = write_skill(Path(temp), "valid", "live")
            stdout = (
                "<skills_instructions>\n"
                "### Skill roots\n"
                f"- `r0` = `{Path(temp)}`\n"
                "### Available skills\n"
                f"- valid: Live skill (file: {valid})\n"
                "- malformed: Live skill (file: /missing/SKILL.md\n"
                "</skills_instructions>\n"
            )
            completed = subprocess.CompletedProcess(
                ["codex", "debug", "prompt-input"], 0, stdout=stdout, stderr=""
            )

            with mock.patch.object(PORTFOLIO_HEALTH.shutil, "which", return_value="/usr/bin/codex"), mock.patch.object(
                PORTFOLIO_HEALTH.subprocess, "run", return_value=completed
            ):
                result = PORTFOLIO_HEALTH.live_inventory()

        self.assertEqual(result.records, [])
        self.assertEqual(result.fallback_reason, "codex debug prompt-input returned a partial skill inventory")
        self.assertEqual(result.diagnostics[0]["code"], "partial-live-inventory")
        self.assertEqual(result.diagnostics[0]["parse_failures"], 1)

    def test_live_inventory_ignores_file_like_text_outside_catalog(self) -> None:
        with TemporaryDirectory() as temp:
            valid = write_skill(Path(temp), "valid", "live")
            stdout = (
                "<skills_instructions>\n"
                "### Skill roots\n"
                f"- `r0` = `{Path(temp)}`\n"
                "### Available skills\n"
                f"- valid: Live skill (file: {valid})\n"
                "</skills_instructions>\n"
                "- unrelated: User text (file: /missing/SKILL.md)\n"
            )
            completed = subprocess.CompletedProcess(
                ["codex", "debug", "prompt-input"], 0, stdout=stdout, stderr=""
            )

            with mock.patch.object(PORTFOLIO_HEALTH.shutil, "which", return_value="/usr/bin/codex"), mock.patch.object(
                PORTFOLIO_HEALTH.subprocess, "run", return_value=completed
            ):
                result = PORTFOLIO_HEALTH.live_inventory()

        self.assertEqual([record.name for record in result.records], ["valid"])
        self.assertIsNone(result.fallback_reason)
        self.assertEqual(result.diagnostics, ())

    def test_live_inventory_ignores_root_aliases_outside_authoritative_block(self) -> None:
        with TemporaryDirectory() as temp:
            base = Path(temp)
            valid = write_skill(base / "inside", "valid", "live")
            stdout = (
                "<skills_instructions>\n"
                "### Skill roots\n"
                f"- `r0` = `{base / 'inside'}`\n"
                "### Available skills\n"
                "- valid: Live skill (file: r0/valid/SKILL.md)\n"
                "</skills_instructions>\n"
                f"- `r0` = `{base / 'outside'}`\n"
            )
            completed = subprocess.CompletedProcess(
                ["codex", "debug", "prompt-input"], 0, stdout=stdout, stderr=""
            )

            with mock.patch.object(PORTFOLIO_HEALTH.shutil, "which", return_value="/usr/bin/codex"), mock.patch.object(
                PORTFOLIO_HEALTH.subprocess, "run", return_value=completed
            ):
                result = PORTFOLIO_HEALTH.live_inventory()

        self.assertEqual([record.realpath for record in result.records], [str(valid.resolve())])
        self.assertIsNone(result.fallback_reason)

    def test_live_inventory_accepts_concatenated_instruction_boundary(self) -> None:
        with TemporaryDirectory() as temp:
            base = Path(temp)
            valid = write_skill(base, "valid", "live")
            stdout = (
                "</plugins_instructions><skills_instructions>\n"
                "### Skill roots\n"
                f"- `r0` = `{base}`\n"
                "### Available skills\n"
                "- valid: Live skill (file: r0/valid/SKILL.md)\n"
                "</skills_instructions>\n"
            )
            completed = subprocess.CompletedProcess(
                ["codex", "debug", "prompt-input"], 0, stdout=stdout, stderr=""
            )

            with mock.patch.object(PORTFOLIO_HEALTH.shutil, "which", return_value="/usr/bin/codex"), mock.patch.object(
                PORTFOLIO_HEALTH.subprocess, "run", return_value=completed
            ):
                result = PORTFOLIO_HEALTH.live_inventory()

        self.assertEqual([record.name for record in result.records], ["valid"])
        self.assertIsNone(result.fallback_reason)

    def test_live_inventory_decodes_json_prompt_input_envelope(self) -> None:
        with TemporaryDirectory() as temp:
            base = Path(temp)
            write_skill(base, "valid", "live")
            prompt_text = (
                "</plugins_instructions><skills_instructions>\n"
                "### Skill roots\n"
                f"- `r0` = `{base}`\n"
                "### Available skills\n"
                "- valid: Live skill (file: r0/valid/SKILL.md)\n"
                "</skills_instructions>\n"
            )
            stdout = json.dumps({"content": [{"type": "text", "text": prompt_text}]})
            completed = subprocess.CompletedProcess(
                ["codex", "debug", "prompt-input"], 0, stdout=stdout, stderr=""
            )

            with mock.patch.object(PORTFOLIO_HEALTH.shutil, "which", return_value="/usr/bin/codex"), mock.patch.object(
                PORTFOLIO_HEALTH.subprocess, "run", return_value=completed
            ):
                result = PORTFOLIO_HEALTH.live_inventory()

        self.assertEqual([record.name for record in result.records], ["valid"])
        self.assertIsNone(result.fallback_reason)

    def test_live_inventory_rejects_duplicate_root_aliases(self) -> None:
        with TemporaryDirectory() as temp:
            base = Path(temp)
            stdout = (
                "<skills_instructions>\n"
                "### Skill roots\n"
                f"- `r0` = `{base / 'one'}`\n"
                f"- `r0` = `{base / 'two'}`\n"
                "### Available skills\n"
                "</skills_instructions>\n"
            )
            completed = subprocess.CompletedProcess(
                ["codex", "debug", "prompt-input"], 0, stdout=stdout, stderr=""
            )

            with mock.patch.object(PORTFOLIO_HEALTH.shutil, "which", return_value="/usr/bin/codex"), mock.patch.object(
                PORTFOLIO_HEALTH.subprocess, "run", return_value=completed
            ):
                result = PORTFOLIO_HEALTH.live_inventory()

        self.assertEqual(result.fallback_reason, "duplicate skill root alias in authoritative section: r0")
        self.assertEqual(result.diagnostics[0]["code"], "live-root-alias-conflict")

    def test_missing_explicit_root_is_a_structured_error(self) -> None:
        with TemporaryDirectory() as temp:
            missing = Path(temp) / "missing"
            result = run_script(
                "--json",
                "scan",
                "--no-logs",
                "--root",
                str(missing),
            )

        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "invalid-root")

    def test_invalid_numeric_option_is_a_structured_error(self) -> None:
        result = run_script("--json", "scan", "--no-logs", "--limit", "-1")

        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "invalid-option")

    def test_entrypoint_size_band_boundaries(self) -> None:
        classify = PORTFOLIO_HEALTH.entrypoint_size_band

        self.assertEqual(classify(2_500, 499), "normal")
        self.assertEqual(classify(2_501, 499), "review")
        self.assertEqual(classify(4_000, 499), "review")
        self.assertEqual(classify(4_001, 499), "high-density")
        self.assertEqual(classify(5_000, 499), "high-density")
        self.assertEqual(classify(5_001, 499), "over-guideline")
        self.assertEqual(classify(1_000, 500), "over-guideline")

    def test_json_scan_adds_entrypoint_signals_without_removing_body_bytes(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp)
            write_skill(root, "normal-skill", "x" * 1_000)
            write_skill(root, "review-skill", "x" * 10_100)
            write_skill(root, "high-density-skill", "x" * 16_100)
            write_skill(root, "over-guideline-skill", "x" * 20_100)
            write_skill(root, "line-precedence-skill", "\n".join(["x"] * 495))

            result = run_script(
                "--json",
                "scan",
                "--inventory-source",
                "filesystem",
                "--no-logs",
                "--root",
                str(root),
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        data = payload["data"]
        skills = {item["name"]: item for item in data["skills"]}

        self.assertEqual(set(payload), {"ok", "version", "command", "data"})
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["version"], "1.1.1")
        self.assertEqual(payload["command"], ["scan"])
        self.assertNotIn("version", data)
        self.assertEqual(data["entrypoint_policy"]["estimator"], "ceil(utf8_bytes/4)")
        self.assertFalse(data["entrypoint_policy"]["size_alone_fails_health"])
        self.assertEqual(data["usage_scan"]["status"], "skipped")
        self.assertEqual(data["unused_candidates"], [])
        self.assertEqual(data["requested_roots"], [str(root)])
        self.assertEqual(data["effective_roots"], [str(root)])
        self.assertEqual(data["root_summary"], {str(root): 5})
        self.assertEqual(skills["normal-skill"]["entrypoint_size_band"], "normal")
        self.assertEqual(skills["review-skill"]["entrypoint_size_band"], "review")
        self.assertEqual(skills["high-density-skill"]["entrypoint_size_band"], "high-density")
        self.assertEqual(skills["over-guideline-skill"]["entrypoint_size_band"], "over-guideline")
        self.assertEqual(skills["line-precedence-skill"]["entrypoint_lines"], 500)
        self.assertEqual(skills["line-precedence-skill"]["entrypoint_size_band"], "over-guideline")

        for field in (
            "generated_at",
            "inventory_source",
            "live_error",
            "fallback_reason",
            "diagnostics",
            "requested_roots",
            "effective_roots",
            "skill_count",
            "budget",
            "description_candidates",
            "duplicates",
            "unused_candidates",
            "root_summary",
            "usage_scan",
            "skills",
        ):
            self.assertIn(field, data)

        for item in skills.values():
            for field in (
                "name",
                "description",
                "path",
                "source",
                "root",
                "body_bytes",
                "description_bytes",
                "usage",
            ):
                self.assertIn(field, item)
            self.assertEqual(
                item["entrypoint_tokens_estimate"],
                -(-item["body_bytes"] // 4),
            )
            self.assertGreater(item["entrypoint_lines"], 0)

        candidates = {
            item["name"]: item["entrypoint_size_band"]
            for item in data["entrypoint_candidates"]
        }
        self.assertNotIn("normal-skill", candidates)
        self.assertEqual(candidates["review-skill"], "review")
        self.assertEqual(candidates["high-density-skill"], "high-density")
        self.assertEqual(candidates["over-guideline-skill"], "over-guideline")
        self.assertEqual(candidates["line-precedence-skill"], "over-guideline")

    def test_text_scan_prints_entrypoint_candidates(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp)
            write_skill(root, "review-skill", "x" * 10_100)
            result = run_script(
                "scan",
                "--inventory-source",
                "filesystem",
                "--no-logs",
                "--root",
                str(root),
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Entrypoint candidates", result.stdout)
        self.assertIn("review-skill (review, ~", result.stdout)

    def test_version_and_doctor(self) -> None:
        version = run_script("--version")
        self.assertEqual(version.returncode, 0, version.stderr)
        self.assertEqual(version.stdout.strip(), "portfolio-health 1.1.1")

        doctor = run_script("--json", "doctor")
        self.assertEqual(doctor.returncode, 0, doctor.stderr)
        payload = json.loads(doctor.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["version"], "1.1.1")
        self.assertFalse(payload["data"]["network_required"])

    def test_retired_no_live_flag_is_rejected(self) -> None:
        result = run_script("scan", "--no-live", "--no-logs")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments: --no-live", result.stderr)

    def test_usage_budget_skips_large_file_and_continues(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp) / "skills"
            logs = Path(temp) / "logs"
            logs.mkdir()
            write_skill(root, "fixture-skill", "Fixture body")
            (logs / "a-large.jsonl").write_bytes(b"x" * (1024 * 1024 + 1))
            (logs / "b-small.jsonl").write_text(
                '{"message":"Use $fixture-skill"}\n', encoding="utf-8"
            )

            result = run_script(
                "--json",
                "scan",
                "--inventory-source",
                "filesystem",
                "--root",
                str(root),
                "--log-root",
                str(logs),
                "--max-log-mb",
                "1",
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)["data"]
        self.assertEqual(data["usage_scan"]["status"], "completed")
        self.assertEqual(data["usage_scan"]["files_considered"], 2)
        self.assertEqual(data["usage_scan"]["files_scanned"], 1)
        self.assertEqual(data["usage_scan"]["files_skipped_budget"], 1)
        self.assertEqual(data["skills"][0]["usage"]["sessions"], 1)


if __name__ == "__main__":
    unittest.main()
