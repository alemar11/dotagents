from __future__ import annotations

import json
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[3]


def read(relative: str) -> str:
    return (PLUGIN_ROOT / relative).read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    start = text.index(f"## {heading}")
    remainder = text[start + len(f"## {heading}") :]
    end = remainder.find("\n## ")
    return remainder if end == -1 else remainder[:end]


class GitStackSkillContractTests(unittest.TestCase):
    def test_github_connector_is_declared_and_runtime_required(self) -> None:
        manifest = json.loads(read(".app.json"))

        github = manifest["apps"]["github"]
        self.assertEqual(set(github), {"id"})
        self.assertTrue(github["id"].startswith("connector_"))
        self.assertIn(
            "required GitHub connector",
            read("skills/github/SKILL.md"),
        )

    def test_issue_composers_normalize_provider_boundary(self) -> None:
        paths = (
            "skills/github-triage/SKILL.md",
            "skills/github-triage/references/workflows.md",
            "skills/github-deep-review/SKILL.md",
            "skills/yeet/SKILL.md",
            "skills/yeet/references/workflows.md",
        )

        for relative in paths:
            text = read(relative)
            with self.subTest(relative=relative):
                self.assertIn("mutation_mode=apply", text)
                self.assertIn("issue_operation", text)
                self.assertIn("exact", text.lower())

    def test_review_composers_supply_exact_pr_and_one_operation(self) -> None:
        routes = {
            "skills/github-triage/references/workflows.md": "review_operation=reply",
            "skills/github-deep-review/SKILL.md": "review_operation=check|wait",
            "skills/yeet/SKILL.md": "review_operation=request",
            "skills/yeet/references/workflows.md": "`review_operation`",
        }

        for relative, operation in routes.items():
            text = read(relative)
            with self.subTest(relative=relative):
                self.assertIn(operation, text)
                normalized = " ".join(text.lower().split()).replace(",", "")
                self.assertRegex(normalized, r"exact (repository and pr|pr)")

        yeet = read("skills/yeet/SKILL.md")
        self.assertIn("review_operation=wait", yeet)
        self.assertIn("one operation per", yeet)

    def test_invocation_registry_excludes_result_and_judgment_fields(self) -> None:
        options = read("references/options.md")

        self.assertIn("protocol inputs, not", options)
        self.assertNotIn("`review_state`", options)
        self.assertNotIn("`refactor_disposition`", options)
        self.assertIn(
            "`review_state` is factual CLI result state, not an invocation",
            read("skills/github-review-threads/references/script-summary.md"),
        )
        self.assertIn(
            "`refactor_disposition` is a judgment returned by",
            read("skills/github-deep-review/SKILL.md"),
        )

    def test_pure_reads_omit_mutation_mode(self) -> None:
        options = read("references/options.md")
        triage = read("skills/github-triage/SKILL.md")
        releases = read("skills/github-releases/SKILL.md")

        self.assertIn("Omit `mutation_mode`", options)
        self.assertIn("Pure queue reads omit both fields", " ".join(triage.split()))
        self.assertIn("Omit `mutation_mode` for `inspect`", releases)

    def test_github_triage_owns_only_queue_grouping(self) -> None:
        triage = read("skills/github-triage/SKILL.md")
        metadata = read("skills/github-triage/agents/openai.yaml")

        self.assertIn("Route evidence-backed issue disposition", triage)
        self.assertIn("$gitstack:github-deep-review", triage)
        self.assertIn("routing disposition judgment", metadata)
        self.assertFalse(
            (PLUGIN_ROOT / "skills/github-triage/references/issue-workflows.md").exists()
        )

    def test_triage_transports_are_strictly_read_only(self) -> None:
        for relative in (
            "skills/github-triage/SKILL.md",
            "skills/github-portfolio-triage/SKILL.md",
        ):
            transport = section(read(relative), "Transport")
            normalized = " ".join(transport.split())
            with self.subTest(relative=relative):
                self.assertIn("supported remote reads", normalized)
                self.assertIn(
                    "This skill never performs GitHub writes or automatically "
                    "falls back between write transports",
                    normalized,
                )
                self.assertNotIn("supported remote reads and writes", normalized)
                self.assertNotIn(
                    "An authorized connector write may fall back", normalized
                )

    def test_github_triage_links_canonical_handoff_registry(self) -> None:
        triage = read("skills/github-triage/SKILL.md")

        self.assertIn("`../../references/options.md`", triage)
        self.assertIn("canonical GitStack invocation fields", triage)


if __name__ == "__main__":
    unittest.main()
