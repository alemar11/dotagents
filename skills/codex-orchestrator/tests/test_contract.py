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

        self.assertIn("Within GitStack, use the official GitHub\nconnector first", skill)
        self.assertIn("GitHub workflow skill", ledger)
        self.assertIn("GitHub primary transport: connector", ledger)
        self.assertNotIn("primary=standalone", ledger)
        self.assertNotIn("github-plugin", ledger)
        self.assertIn("authority-reused=<authority", ledger)

    def test_worker_capabilities_cannot_be_bypassed_by_allowed_surfaces(self) -> None:
        worker = self.read("references/worker.md")

        inspect_mode = next(
            line for line in worker.splitlines() if line.startswith("- `inspect`:")
        )
        implement_mode = next(
            line for line in worker.splitlines() if line.startswith("- `implement`:")
        )
        self.assertIn("read-only", inspect_mode)
        self.assertIn("never permits", worker)
        self.assertIn("cannot grant another capability mode", worker)
        self.assertNotIn("unless explicitly listed in allowed surfaces", inspect_mode)
        self.assertNotIn("unless explicitly listed in allowed surfaces", implement_mode)

    def test_gate_selection_includes_follow_up_risk_and_access(self) -> None:
        gates = self.read("references/gates.md")
        universal = gates.split("## Gate Lenses", 1)[0]

        for gate in ("`follow-up`", "`risk-follow-up`", "`credential-and-access`"):
            self.assertIn(gate, universal)

    def test_domain_closeout_survives_issue_to_worker_handoff(self) -> None:
        issue_template = (
            ROOT / "skills/plan-feature/references/issue-body-template.md"
        ).read_text(encoding="utf-8")
        delivery = self.read("references/prd-backed-delivery.md")
        worker = self.read("references/worker.md")

        for text in (issue_template, delivery, worker):
            self.assertIn("Domain closeout", text)
            self.assertIn("implementation-closeout", text)

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

    def test_recovery_packet_is_compact_derived_and_freshness_gated(self) -> None:
        skill = self.read("SKILL.md")
        ledger = self.read("references/ledger.md")
        efficiency = self.read("references/runtime-efficiency.md")

        self.assertIn("## Recovery Packet", ledger)
        self.assertIn("Projection fingerprint", ledger)
        self.assertIn("Content fingerprint", ledger)
        self.assertIn("Recovery packet content fingerprint", ledger)
        self.assertIn("References to load next", ledger)
        self.assertIn("compact derived projection, never\n  as authority", skill)
        self.assertIn("Read only the ledger `## Recovery Packet`", efficiency)
        self.assertIn("Recompute the packet's Projection fingerprint", efficiency)
        self.assertIn("Recompute the packet Content fingerprint", efficiency)
        self.assertIn("match both the packet value", efficiency)
        self.assertIn("stored under authoritative\n   `## Active Root`", efficiency)
        self.assertIn("require an exact match", efficiency)
        self.assertIn("shasum -a 256", efficiency)
        self.assertIn("checkpoint IDs to equal the complete current set", efficiency)
        self.assertIn("in-scope registered source item IDs", efficiency)
        self.assertIn("every current\n   `## Workstreams` status bucket", efficiency)
        self.assertIn("reject missing or extra checkpoints", efficiency)
        self.assertIn("repo checkpoint realpaths to equal the complete canonical", efficiency)
        self.assertIn("from `## Scope` and `## Active Root`", efficiency)
        self.assertIn("reject\n   missing or extra repos", efficiency)
        self.assertIn("Projection fingerprint, which now binds that content fingerprint", efficiency)
        self.assertIn("If any check differs, mark it `stale` or `invalid`", efficiency)
        self.assertIn("do not mutate or dispatch\n   from it", efficiency)
        self.assertIn("never bypasses claims,\ncapabilities, authority", efficiency)

    def test_runtime_evidence_is_delta_based_and_metrics_are_exact_or_unavailable(self) -> None:
        skill = self.read("SKILL.md")
        ledger = self.read("references/ledger.md")
        efficiency = self.read("references/runtime-efficiency.md")

        self.assertIn("Do not re-emit\n  complete unchanged ledgers or diffs", skill)
        for command in (
            "git status --short",
            "git diff --stat",
            "git diff --name-only",
            "git diff --check",
        ):
            self.assertIn(command, efficiency)
        self.assertIn("before `$autoreview`, commit/publication", efficiency)
        self.assertIn("## Runtime Metrics", ledger)
        self.assertIn("claim-register-route", efficiency)
        self.assertIn("dispatch-integrate:<wave>", efficiency)
        self.assertIn("gate-reconcile:<wave>", efficiency)
        self.assertIn("recovery:<packet-version>", efficiency)
        self.assertIn("counters are scoped to this root", efficiency)
        self.assertIn("no concurrent worker, tool, or other-phase", efficiency)
        self.assertIn("label it `exact-interval`", efficiency)
        self.assertIn("Never infer usage", efficiency)
        self.assertIn("metrics are diagnostic, not gate or closeout proof", efficiency)

    def test_runtime_efficiency_reference_is_conditionally_loaded(self) -> None:
        skill = self.read("SKILL.md")

        self.assertIn("references/runtime-efficiency.md", skill)
        self.assertIn("before resuming from a packet, entering\na second wave", skill)
        self.assertIn("a simple first wave need not load it", skill)

    def test_pull_request_defaults_to_merge_ready_closeout(self) -> None:
        skill = self.read("SKILL.md")
        gates = self.read("references/gates.md")
        rows = self.table_rows(
            "references/prd-backed-delivery.md",
            "## PR Closeout Resolution Matrix",
        )

        self.assertIn("Pull-request delivery defaults to\n`merge-ready`", skill)
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

        no_mutation = self.row_containing(rows, "`draft-output`")
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
        plan_skill = (ROOT / "skills/plan-feature/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("structured PRD value", plan_skill)
        self.assertIn("`draft-output` do not select it", plan_skill)

    def test_codex_review_requests_are_idempotent_per_current_head(self) -> None:
        gates = self.read("references/gates.md")
        ledger = self.read("references/ledger.md")
        worker = self.read("references/worker.md")
        rows = self.table_rows(
            "references/gates.md",
            "#### Codex Review Request Matrix",
        )

        expected_rows = [
            [
                "GitStack `clean`",
                "`head_is_current=true`",
                "Reuse the result and pass the review-result portion of the gate.",
                "No.",
                "Record the terminal result and object for this head.",
            ],
            [
                "GitStack `findings`",
                "`head_is_current=true`",
                "Evaluate and disposition findings; fix accepted findings before closeout.",
                "No for this head.",
                "Record findings and disposition; a fix may create a new head with a new preflight.",
            ],
            [
                "GitStack `acknowledged` or `pending`",
                "`head_is_current=true`",
                "Run bounded `reviews wait` for the same head and preserve the existing request.",
                "No.",
                "Keep the existing request object and next poll.",
            ],
            [
                "GitStack `stale`",
                "Refresh the assigned SHA, rerun `reviews check`, require `head_is_current=true`, re-read the PR head immediately before mutation, and require no request object for that SHA.",
                "Post one request naming the proven current head.",
                "Yes, exactly once for that SHA.",
                "Record the request before polling.",
            ],
            [
                "GitStack `not_requested`",
                "Require `head_is_current=true`, re-read the PR head immediately before mutation, and require no request object for that SHA.",
                "Post one request naming the proven current head.",
                "Yes, exactly once for that SHA.",
                "Record the request before polling.",
            ],
            [
                "GitStack API, authentication, or configuration error",
                "Current head or request state is unproven.",
                "Record the blocker and use the documented read-only fallback.",
                "No.",
                "Preserve any known request evidence; do not mutate from uncertainty.",
            ],
            [
                "Verified terminal clean provider-authored comment not represented by GitStack",
                "Authenticated provider plus unambiguous current-head SHA or prefix.",
                "Record supplemental evidence and pass the review-result portion of the gate.",
                "No.",
                "Record the result kind, object, provider, and head.",
            ],
            [
                "Verified terminal findings in a provider-authored comment not represented by GitStack",
                "Authenticated provider plus unambiguous current-head SHA or prefix.",
                "Record supplemental evidence and disposition findings.",
                "No for this head.",
                "Record findings and disposition.",
            ],
            [
                "Terminal provider error for the current-head request",
                "Existing request object and current head are recorded.",
                "Record the error and follow recovery without another request for the unchanged head.",
                "No.",
                "Block or wait until a new head or external recovery exists.",
            ],
            [
                "Unverified or human-authored comment claiming success",
                "No verified result; use the GitStack status for the proven current head.",
                "Ignore the comment and follow the matching GitStack row.",
                "Only through a proven `stale` or `not_requested` row.",
                "Record that the comment was rejected as evidence.",
            ],
        ]
        self.assertEqual(rows, expected_rows)

        self.assertIn(
            "reviews check --provider codex --repo <owner/repo>\n"
            "--pr <number> --head <current-sha>",
            gates,
        )
        self.assertIn("request-head=<sha|none>", ledger)
        self.assertIn("result-kind=<formal-review|provider-comment|clean-reaction|none>", ledger)
        self.assertIn(
            "authenticated Codex clean reaction that GitStack binds",
            gates,
        )
        self.assertIn("reports as `clean` with\n  `head_is_current=true`", gates)
        self.assertIn("worker must rerun `reviews check`", worker)
        self.assertIn("for that refreshed SHA", worker)
        self.assertIn(
            "same-SHA check returns `not_requested` or `stale` with\n"
            "  `head_is_current=true`",
            worker,
        )
        self.assertIn("cannot bypass the refreshed check", worker)
        self.assertIn("re-read the PR head and\n  stop if it changed", worker)
        self.assertIn(
            "Reuse `clean`/`findings` and poll\n"
            "  `acknowledged`/`pending`",
            worker,
        )
        self.assertIn(
            "immediately re-read the PR head and verify\n"
            "   it still equals the checked SHA",
            gates,
        )
        self.assertIn(
            "Reuse the request across `acknowledged`, `pending`, and timeouts",
            gates,
        )


if __name__ == "__main__":
    unittest.main()
