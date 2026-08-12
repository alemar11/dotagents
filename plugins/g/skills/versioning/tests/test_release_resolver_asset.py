from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from types import ModuleType


SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSET = SKILL_ROOT / "assets" / "resolve_release_version.py"
REFERENCE = SKILL_ROOT / "references" / "github-actions.md"
SKILL = SKILL_ROOT / "SKILL.md"


def load_resolver() -> ModuleType:
    module_name = "g_versioning_release_resolver_asset"
    spec = importlib.util.spec_from_file_location(module_name, ASSET)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {ASSET}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class ReleaseResolverAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.resolver = load_resolver()

    def resolve(
        self,
        *,
        operation: str,
        tags: list[str],
        ref_name: str = "main",
        confirmed_tag: str | None = None,
    ) -> dict[str, object]:
        return self.resolver.resolve(
            ref_name=ref_name,
            default_branch="main",
            operation=operation,
            raw_tags=tags,
            confirmed_tag=confirmed_tag,
        )

    def test_asset_reports_clean_semver_version(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ASSET), "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(self.resolver.RESOLVER_VERSION, "0.2.2")
        self.assertEqual(completed.stdout.strip(), "0.2.2")
        self.assertEqual(completed.stderr, "")

    def test_final_tag_classification_requires_canonical_stable_form(self) -> None:
        self.assertTrue(self.resolver.is_final_tag("v1.2.3"))
        self.assertFalse(self.resolver.is_final_tag("v1.2.3-rc.1"))
        self.assertFalse(self.resolver.is_final_tag("1.2.3"))
        self.assertFalse(self.resolver.is_final_tag("v1.2.3-beta"))

    def test_asset_help_is_available_without_workflow_arguments(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ASSET), "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("--version", completed.stdout)
        self.assertIn("--confirmed-tag", completed.stdout)

    def test_default_branch_uses_highest_stable_baseline(self) -> None:
        result = self.resolve(
            operation="patch",
            tags=["v1.0.0", "v2.0.0-rc.1", "v3.0.0-rc.2"],
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["tag"], "v1.0.1-rc.1")
        self.assertFalse(result["is_final"])

    def test_same_line_must_continue_from_release_branch(self) -> None:
        result = self.resolve(
            operation="patch",
            tags=["v1.0.0", "v1.0.1-rc.1"],
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "blocked-release-in-progress")
        self.assertEqual(result["release_branch"], "release/v1.0.1")

    def test_final_does_not_require_a_candidate(self) -> None:
        result = self.resolve(
            operation="final",
            tags=["v1.0.0"],
            ref_name="release/v2.0.0",
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["tag"], "v2.0.0")
        self.assertTrue(result["is_final"])

    def test_noncanonical_confirmation_is_never_normalized(self) -> None:
        for confirmed_tag in (
            "1.0.1-rc.1",
            "v1.0.1-beta",
            "v1.0.1-rc01",
            "v1.0.1-rc.01",
            "v1.0.1+build.1",
        ):
            with self.subTest(confirmed_tag=confirmed_tag):
                result = self.resolve(
                    operation="patch",
                    tags=["v1.0.0"],
                    confirmed_tag=confirmed_tag,
                )
                self.assertFalse(result["ok"])
                self.assertEqual(result["status"], "blocked-noncanonical")

    def test_existing_final_can_only_reconcile_its_pr(self) -> None:
        result = self.resolve(
            operation="final",
            tags=["v1.0.0", "v2.0.0"],
            ref_name="release/v2.0.0",
            confirmed_tag="v2.0.0",
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "reconcile-existing-final")
        self.assertEqual(result["tag_state"], "existing-final")
        self.assertTrue(result["is_final"])

    def test_asset_has_no_project_or_network_dependency(self) -> None:
        source = ASSET.read_text(encoding="utf-8")
        self.assertNotIn("package.json", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("urllib", source)
        self.assertNotIn("requests", source)

    def test_plan_summary_is_independent_of_workflow_display_names(self) -> None:
        source = ASSET.read_text(encoding="utf-8")
        self.assertIn("Review the exact resolved tag above", source)
        self.assertNotIn("Run **Release version", source)

    def test_reference_defines_one_approval_gated_controller(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        self.assertIn("`.github/workflows/release-version.yml`", reference)
        self.assertNotIn("release-version-dry-run.yml", reference)
        self.assertNotIn("release-version-apply.yml", reference)
        self.assertIn("name: Create release tag", reference)
        self.assertIn("resolver API 0.2.2", reference)
        self.assertIn(
            "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",
            reference,
        )
        self.assertIn('EXPECTED_RESOLVER_VERSION: "0.2.2"', reference)
        self.assertIn("name: release-tag-approval", reference)
        self.assertIn("deployment: false", reference)
        self.assertIn("Approve ${{ needs.plan.outputs.tag }}", reference)
        self.assertIn("final mutation job separately exposes", reference)
        self.assertIn("pull-requests: write", reference)
        self.assertIn("controller is application-code blind", reference)
        self.assertIn("fresh provider state", reference)

    def test_reference_defines_reusable_publisher_and_manual_recovery(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("## Reusable publisher contract", reference)
        self.assertIn("workflow_call:", reference)
        self.assertIn("workflow_dispatch:", reference)
        self.assertIn("tag:", reference)
        self.assertIn("source_sha:", reference)
        self.assertIn("uses: ./.github/workflows/release.yml", reference)
        self.assertIn("source_sha: ${{ needs.final.outputs.source_sha }}", reference)
        self.assertIn("name: Publish tagged release", reference)
        self.assertIn("ref: ${{ needs.resolve.outputs.tag }}", reference)
        self.assertIn("existing-final", reference)
        self.assertIn("Do not add `on.push.tags`", reference)
        self.assertIn("Do not invoke the publisher with `gh workflow run`", reference)
        self.assertIn("Do not grant `actions: write`", reference)
        self.assertNotIn("gh workflow run <publish-workflow>.yml", reference)
        self.assertIn("reusable-publisher and", skill)
        self.assertIn("manual-recovery contracts", skill)


if __name__ == "__main__":
    unittest.main()
