from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = ROOT / "skills" / "codex-orchestrator"


class OrchestratorContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (SKILL_ROOT / relative).read_text(encoding="utf-8")

    def table_rows(self, relative: str, heading: str) -> list[list[str]]:
        section = self.read(relative).split(heading, 1)[1]
        rows: list[list[str]] = []
        for line in section.splitlines():
            if not line.startswith("|"):
                if rows:
                    break
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if all(set(cell) <= {"-", ":", " "} for cell in cells):
                continue
            rows.append(cells)
        return rows[1:]

    def row_containing(self, rows: list[list[str]], needle: str) -> list[str]:
        return next(row for row in rows if needle in row[0])

    def test_gitstack_is_primary_and_fallback_reuses_authority(self) -> None:
        skill = self.read("SKILL.md")
        ledger = self.read("references/ledger.md")

        self.assertIn(
            "GitStack companion skills are the primary Git/GitHub route",
            skill,
        )
        self.assertIn("authority-reused=<authority", ledger)

    def test_merge_is_root_owned_and_explicit(self) -> None:
        worker = self.read("references/worker.md")
        delivery = self.read("references/prd-backed-delivery.md")
        gates = self.read("references/gates.md")

        authorization_row = next(
            line for line in worker.splitlines() if "`worker_authorization`" in line
        )
        prompt_modes = next(
            line
            for line in worker.splitlines()
            if line.startswith("- Authorization modes:")
        )
        self.assertNotIn("merge-close", authorization_row)
        self.assertNotIn("merge-close", prompt_modes)
        self.assertIn("`merge_authority`: `none` is the default", delivery)
        self.assertIn("### Merge Authorization Gate", gates)

    def test_capability_and_reconciliation_contracts_are_required(self) -> None:
        worker = self.read("references/worker.md")
        ledger = self.read("references/ledger.md")

        self.assertIn("## Capability Snapshots", worker)
        self.assertIn("created, resumed, or\nforked", worker)
        self.assertIn("Reconciliation updates the current projection", ledger)
        self.assertIn("Stale Values Removed", ledger)

    def test_pull_request_defaults_to_merge_ready_closeout(self) -> None:
        skill = self.read("SKILL.md")
        gates = self.read("references/gates.md")
        rows = self.table_rows(
            "references/prd-backed-delivery.md",
            "## PR Closeout Resolution Matrix",
        )

        self.assertIn("default\n`pr_closeout=merge-ready`", skill)
        self.assertIn(
            "`publication_authority=prd-backed-pull-request` satisfies authorization",
            gates,
        )
        draft_shape = self.row_containing(rows, "`one draft PR`")
        self.assertEqual(draft_shape[2], "`merge-ready`")
        self.assertIn("Codex review", draft_shape[4])

        do_not_merge = self.row_containing(rows, "`do not merge automatically`")
        self.assertEqual(do_not_merge[2], "`merge-ready`")
        self.assertEqual(do_not_merge[3], "`none`")
        self.assertIn("stop merge-ready", do_not_merge[4])

    def test_draft_only_requires_explicit_user_or_structured_prd_evidence(self) -> None:
        gates = self.read("references/gates.md")
        rows = self.table_rows(
            "references/prd-backed-delivery.md",
            "## PR Closeout Resolution Matrix",
        )

        user_draft_only = self.row_containing(rows, "`keep the PR in draft`")
        self.assertEqual(user_draft_only[2], "`draft-only`")
        self.assertIn("do not mark ready", user_draft_only[4])

        structured_draft_only = self.row_containing(
            rows, "Structured PRD field `PR closeout: draft-only`"
        )
        self.assertEqual(
            structured_draft_only[1], "`prd-backed-pull-request`"
        )
        self.assertEqual(structured_draft_only[2], "`draft-only`")
        self.assertIn("Preserve the structured decision", structured_draft_only[4])

        no_mutation = self.row_containing(rows, "`draft-only output`")
        self.assertEqual(no_mutation[1], "`none` for the planning run")
        self.assertIn("`merge-ready`", no_mutation[2])
        self.assertIn("without persisting", no_mutation[4])
        self.assertIn(
            "Draft-only makes downstream ready/review/merge-ready\n"
            "gates `not-applicable`",
            gates,
        )

    def test_existing_draft_resumes_when_draft_only_is_absent_or_removed(self) -> None:
        rows = self.table_rows(
            "references/prd-backed-delivery.md",
            "## PR Closeout Resolution Matrix",
        )

        existing = self.row_containing(rows, "Existing draft PR")
        self.assertEqual(existing[2], "`merge-ready`")
        self.assertIn("Resume at ready-for-review", existing[4])

        removed = self.row_containing(rows, "removes a previous draft-only")
        self.assertEqual(removed[2], "`merge-ready`")
        self.assertIn("Resume the existing PR", removed[4])

    def test_legacy_handoff_missing_closeout_defaults_and_rewrites(self) -> None:
        rows = self.table_rows(
            "references/prd-backed-delivery.md",
            "## PR Closeout Resolution Matrix",
        )
        legacy_handoff = self.row_containing(rows, "Legacy handoff missing")

        self.assertEqual(legacy_handoff[1], "`prd-backed-pull-request`")
        self.assertEqual(legacy_handoff[2], "`merge-ready`")
        self.assertIn("Rewrite the touched handoff projection", legacy_handoff[4])

    def test_legacy_publication_authority_values_migrate_to_separate_closeout(self) -> None:
        ledger = self.read("references/ledger.md")
        rows = self.table_rows(
            "references/prd-backed-delivery.md",
            "### Legacy Authority Migration",
        )

        merge_ready = self.row_containing(rows, "prd-backed-merge-ready-pr")
        self.assertEqual(merge_ready[1], "`prd-backed-pull-request`")
        self.assertEqual(merge_ready[2], "`merge-ready`")

        draft_named = self.row_containing(rows, "prd-backed-branch-plus-draft-pr")
        self.assertEqual(draft_named[1], "`prd-backed-pull-request`")
        self.assertIn("otherwise `merge-ready`", draft_named[2])

        for legacy in (merge_ready[0].strip("`"), draft_named[0].strip("`")):
            self.assertIn(legacy, ledger)
        self.assertIn("publication=prd-backed-pull-request", ledger)
        self.assertIn("defaulting to `merge-ready`", ledger)

    def test_plan_feature_and_orchestrator_share_pr_closeout_contract(self) -> None:
        delivery = self.read("references/prd-backed-delivery.md")
        prd_template = (
            ROOT / "skills/plan-feature/references/prd-template.md"
        ).read_text(encoding="utf-8")
        issue_template = (
            ROOT / "skills/plan-feature/references/issue-body-template.md"
        ).read_text(encoding="utf-8")

        for value in ("merge-ready", "draft-only"):
            self.assertIn(value, delivery)
            self.assertIn(value, prd_template)
            self.assertIn(value, issue_template)
        self.assertIn("PR shape: one PR opened as draft initially", prd_template)
        self.assertIn("PR closeout: [merge-ready | draft-only]", issue_template)
        self.assertIn(
            "preserving an existing structured PRD\n"
            "  `PR closeout: draft-only` decision",
            (ROOT / "skills/plan-feature/references/prd-phase.md").read_text(
                encoding="utf-8"
            ),
        )
        self.assertIn(
            "preserving an existing structured PRD `PR closeout: draft-only`\n"
            "  decision",
            (ROOT / "skills/plan-feature/SKILL.md").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
