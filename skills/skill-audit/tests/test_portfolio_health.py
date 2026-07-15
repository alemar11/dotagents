from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


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
                "--no-live",
                "--no-logs",
                "--root",
                str(root),
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        data = payload["data"]
        skills = {item["name"]: item for item in data["skills"]}

        self.assertEqual(data["entrypoint_policy"]["estimator"], "ceil(utf8_bytes/4)")
        self.assertFalse(data["entrypoint_policy"]["size_alone_fails_health"])
        self.assertEqual(skills["normal-skill"]["entrypoint_size_band"], "normal")
        self.assertEqual(skills["review-skill"]["entrypoint_size_band"], "review")
        self.assertEqual(skills["high-density-skill"]["entrypoint_size_band"], "high-density")
        self.assertEqual(skills["over-guideline-skill"]["entrypoint_size_band"], "over-guideline")
        self.assertEqual(skills["line-precedence-skill"]["entrypoint_lines"], 500)
        self.assertEqual(skills["line-precedence-skill"]["entrypoint_size_band"], "over-guideline")

        for field in (
            "generated_at",
            "version",
            "inventory_source",
            "live_error",
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
                "--no-live",
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
        self.assertEqual(version.stdout.strip(), "portfolio-health 0.2.0")

        doctor = run_script("--json", "doctor")
        self.assertEqual(doctor.returncode, 0, doctor.stderr)
        payload = json.loads(doctor.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["version"], "0.2.0")
        self.assertFalse(payload["data"]["network_required"])


if __name__ == "__main__":
    unittest.main()
