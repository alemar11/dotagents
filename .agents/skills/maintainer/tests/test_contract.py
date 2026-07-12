from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]


def read(relative: str) -> str:
    return (SKILL_ROOT / relative).read_text(encoding="utf-8")


class MaintainerContractTests(unittest.TestCase):
    def test_package_identity_is_lowercase_and_aligned(self) -> None:
        self.assertEqual(SKILL_ROOT.name, "maintainer")
        skill = read("SKILL.md")
        self.assertRegex(skill, r"(?m)^name: maintainer$")
        self.assertIn("display_name: \"Maintainer\"", read("agents/openai.yaml"))

    def test_all_entrypoint_references_exist(self) -> None:
        references = set(re.findall(r"references/([a-z0-9_-]+\.md)", read("SKILL.md")))
        self.assertGreater(len(references), 10)
        missing = sorted(name for name in references if not (SKILL_ROOT / "references" / name).is_file())
        self.assertEqual(missing, [])

    def test_router_and_menu_expose_new_tasks(self) -> None:
        router = read("references/maintenance-router.md")
        menu = read("references/task-menu.md")
        for term in ("workflow-hardening", "package-lifecycle"):
            self.assertIn(term, router)
        self.assertLess(router.index("classify as `workflow-hardening`"), router.index("use `skill-upgrade.md`"))
        self.assertLess(router.index("classify as `package-lifecycle`"), router.index("use `skill-upgrade.md`"))
        for task in ("harden workflow family", "migrate or retire package"):
            self.assertIn(task, menu)

    def test_generic_maintenance_cannot_expand_strategically(self) -> None:
        runbook = read("references/run-maintenance.md")
        router = read("references/maintenance-router.md")
        for term in ("workflow-family hardening", "package migration/retirement", "substantial reshapes"):
            self.assertIn(term, runbook)
        self.assertIn("Do not silently expand generic maintenance", router)

    def test_substantial_reshapes_are_creator_first(self) -> None:
        lifecycle = read("references/package-lifecycle.md")
        upgrade = read("references/skill-upgrade.md")
        for contract in ("$skill-creator", "$plugin-creator"):
            self.assertIn(contract, lifecycle)
            self.assertIn(contract, upgrade)

    def test_runtime_evidence_stays_read_only_until_accepted(self) -> None:
        hardening = read("references/workflow-family-hardening.md")
        normalized = " ".join(hardening.split())
        self.assertIn("$skill-audit", hardening)
        self.assertIn("read-only", hardening)
        self.assertIn("after the finding is accepted", hardening)
        self.assertIn("representative raw session", hardening)
        self.assertIn("reproducible test failure", hardening)
        self.assertIn("may be sufficient", normalized)

    def test_validation_matrix_covers_runtime_and_package_surfaces(self) -> None:
        matrix = read("references/validation-matrix.md")
        for lane in (
            "Runtime skill contract",
            "Composed workflow",
            "Embedded CLI",
            "Plugin",
            "Migration or removal",
            "Non-trivial implementation",
        ):
            self.assertIn(lane, matrix)
        for proof in ("--help", "--version", "--json doctor", "$autoreview"):
            self.assertIn(proof, matrix)
        normalized = " ".join(matrix.split())
        self.assertIn("before/after status", normalized)
        self.assertIn("reinstall introduced no checkout changes", normalized)

    def test_git_mutations_require_explicit_authorization(self) -> None:
        checklist = read("references/release-checklist.md")
        normalized = " ".join(checklist.split())
        self.assertIn("Resolve commit, push, PR, and other publication authority independently", normalized)
        self.assertIn("Otherwise stop after validation", normalized)
        self.assertIn("With explicit commit authority", normalized)
        self.assertIn("With push-only authority, do not stage or commit", normalized)
        self.assertIn("Do not infer commit authority from a bare PR request", normalized)
        self.assertIn("Direct scoped `git` is", normalized)
        self.assertIn("when GitStack is unavailable", normalized)
        self.assertIn("authorized paths plus the staged set are clean", normalized)
        self.assertIn("unrelated pre-existing changes remain unchanged", normalized)
        self.assertIn("global worktree cleanliness is not required", normalized)

    def test_instruction_density_is_a_pre_mutation_mixed_route_gate(self) -> None:
        router = read("references/maintenance-router.md")
        mixed = router.partition("If a request mixes categories")[2]
        density = mixed.index("`instruction-density`")
        hardening = mixed.index("`workflow-hardening`")
        lifecycle = mixed.index("`package-lifecycle`")
        maintain = mixed.index("`maintain`")
        self.assertLess(density, hardening)
        self.assertLess(density, lifecycle)
        self.assertLess(density, maintain)
        self.assertIn("stop before any mutation", mixed)

    def test_lifecycle_commit_split_is_authority_gated(self) -> None:
        lifecycle = " ".join(read("references/package-lifecycle.md").split())
        self.assertIn("When the user explicitly authorizes commits", lifecycle)
        self.assertIn("Without commit authority, report the recommended split", lifecycle)
        self.assertIn("without staging or changing Git history", lifecycle)

    def test_codex_dependencies_are_explicit_and_registered(self) -> None:
        skill = read("SKILL.md")
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        for dependency in ("$skill-audit", "$skill-creator", "$plugin-creator", "$autoreview"):
            self.assertIn(dependency, skill)
            self.assertIn(dependency, readme)
        self.assertIn("`maintainer`", agents.partition("### Codex Dependency Classification")[2])

    def test_no_stale_uppercase_identity_remains(self) -> None:
        candidates = [REPO_ROOT / "AGENTS.md", REPO_ROOT / "README.md"]
        candidates.extend((REPO_ROOT / ".agents" / "skills").rglob("*"))
        stale_patterns = (
            ".agents/skills/" + "Maintainer",
            "$" + "Maintainer",
            "name: " + "Maintainer",
        )
        findings: list[str] = []
        for path in candidates:
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in stale_patterns:
                if pattern in text:
                    findings.append(f"{path.relative_to(REPO_ROOT)}: {pattern}")
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
