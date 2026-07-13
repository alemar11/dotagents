from __future__ import annotations

import hashlib
import re
import shlex
import subprocess
import tempfile
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
        self.assertIn("authority_reused=<authority", ledger)

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
            self.assertIn("domain_closeout", text)
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
            if line.startswith("- worker_authorization:")
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
        self.assertIn("Option resolution refs: session_rows=", ledger)
        self.assertIn("rows_fingerprint=<sha256", ledger)
        self.assertIn("Workstream checkpoints:", ledger)
        self.assertIn("scope_transfer_ref=<issue:<NN>|not-applicable>", ledger)
        self.assertIn("delivery_evidence_fingerprint=<sha256 or not-applicable>", ledger)
        self.assertIn("issue_mutation_evidence_fingerprint=<sha256 or not-applicable>", ledger)
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
        self.assertIn("Workstream checkpoint IDs to equal every authoritative workstream", efficiency)
        self.assertIn("re-read that\n   generated issue's current `## Orchestrator Handoff`", efficiency)
        self.assertIn("match `delivery_evidence_fingerprint`", efficiency)
        self.assertIn("`issue_mutation_evidence_fingerprint`", efficiency)
        self.assertIn("`scope_transfer_ref` and\n   `issue_mutation_transfer_ref` rows", efficiency)
        self.assertIn("Require every listed `workstream_ids` assignment", efficiency)
        self.assertIn("assigned_worker[workstream]", efficiency)
        self.assertIn("reject missing or extra checkpoints", efficiency)
        self.assertIn(
            "exact\n   session and scoped `## Option Resolution` row IDs",
            efficiency,
        )
        self.assertIn("require it to match `rows_fingerprint`", efficiency)
        self.assertIn("PACKET_OPTION_ROWS_FINGERPRINT=", efficiency)
        self.assertIn("COMPUTED_OPTION_ROWS_FINGERPRINT=", efficiency)
        self.assertIn("row_id,scope_id,field,value,source,evidence", efficiency)
        self.assertIn("LC_ALL=C sort", efficiency)
        self.assertIn("shasum -a 256", efficiency)
        self.assertIn('substr(value, 1, 1) == "`"', efficiency)
        self.assertIn("OPTION_ROW_IDS=", efficiency)
        self.assertIn("OPTION_SOURCE_SCOPE_IDS=", efficiency)
        self.assertIn("OPTION_WORKSTREAM_SCOPE_IDS=", efficiency)
        self.assertIn("derive discovery-source scope IDs", efficiency)
        self.assertIn("Registered source-item\n   checkpoints are freshness evidence", efficiency)
        self.assertIn("OPTION_SCOPE_IDS=", efficiency)
        self.assertIn("if (is_applicable) {", efficiency)
        self.assertIn("applicable[row_id]++", efficiency)
        self.assertIn("expected_session", efficiency)
        self.assertIn("expected_source", efficiency)
        self.assertIn("expected_workstream", efficiency)
        self.assertIn("allowed_value", efficiency)
        self.assertIn("allowed_source", efficiency)
        self.assertIn("!(row_id in selected)", efficiency)
        self.assertIn("if (!(row_id in selected)) next", efficiency)
        self.assertIn("repo checkpoint realpaths to equal the complete canonical", efficiency)
        self.assertIn("from `## Scope` and `## Active Root`", efficiency)
        self.assertIn("reject\n   missing or extra repos", efficiency)
        self.assertIn("Projection fingerprint, which now binds that content fingerprint", efficiency)
        self.assertIn("If any check differs, mark it `stale` or `invalid`", efficiency)
        self.assertIn("do not mutate or dispatch\n   from it", efficiency)
        self.assertIn("never bypasses claims,\ncapabilities, authority", efficiency)

    def test_recovery_option_hash_rejects_omitted_applicable_row(self) -> None:
        efficiency = self.read("references/runtime-efficiency.md")
        marker = efficiency.index("OPTION_ROW_IDS=")
        block_start = efficiency.rfind("```bash", 0, marker) + len("```bash")
        block_end = efficiency.index("```", marker)
        script = efficiency[block_start:block_end].strip()

        session_values = {
            "delegation_mode": ("auto", "default", "none"),
            "worker_surface": ("auto", "default", "none"),
            "worker_limit": ("unbounded", "default", "none"),
            "app_thread_consent": ("not-requested", "default", "none"),
            "app_thread_limit": ("unspecified", "default", "none"),
            "raw_worktree_fallback": ("forbidden", "default", "none"),
            "active_root_takeover_policy": ("owner-approval", "default", "none"),
        }
        scoped_values = {
            "source_mutation_authority": ("none", "default", "none"),
            "publication_authority": ("prd-backed-pull-request", "source-contract", "issue-1"),
            "issue_mutation_authority": ("pr-body-closeout-only", "source-contract", "issue-1"),
            "merge_authority": ("none", "default", "none"),
            "merge_policy": ("owner-approval", "default", "none"),
            "caller_checkout_policy": ("preserve-current-branch", "default", "none"),
            "automation_authority": ("none", "default", "none"),
            "temporary_source_execution": ("forbidden", "default", "none"),
            "completion_proof_policy": ("live-required", "default", "none"),
            "delivery_mode": ("pull-request", "source-contract", "issue-1"),
            "delivery_source": ("feature-level-inherited", "source-contract", "issue-1"),
            "branch_name": ("feature/example", "source-contract", "issue-1"),
            "scope_transfer_ref": ("not-applicable", "default", "none"),
            "issue_mutation_transfer_ref": ("not-applicable", "default", "none"),
            "pr_closeout": ("merge-ready", "source-contract", "issue-1"),
            "pr_shape": ("single-pr", "source-contract", "issue-1"),
            "closeout_mode": ("feature-pr-closes-issue", "source-contract", "issue-1"),
            "integration_mode": ("single-repo-pr", "source-contract", "issue-1"),
        }
        scopes = ("workstream:a", "workstream:b", "workstream:repo:123")

        def row(scope: str, field: str, triple: tuple[str, str, str]) -> str:
            value, source, evidence = triple
            return (
                f"| `{scope}:{field}` | `{scope}` | `{field}` | `{value}` | "
                f"`{source}` | `{evidence}` |"
            )

        session_rows = [row("session", field, triple) for field, triple in session_values.items()]
        scoped_rows = [
            row(scope, field, triple)
            for scope in scopes
            for field, triple in scoped_values.items()
        ]
        ledger_fixture = "\n".join(
            [
                "## Option Resolution",
                "",
                "### Session Rows",
                "",
                "| row_id | scope_id | field | value | source | evidence |",
                "| --- | --- | --- | --- | --- | --- |",
                *session_rows,
                "",
                "### Scoped Rows",
                "",
                "| row_id | scope_id | field | value | source | evidence |",
                "| --- | --- | --- | --- | --- | --- |",
                *scoped_rows,
                "",
                "## Discovery Sources",
                "",
                "## Workstreams",
                "",
                "### active",
                "",
                "#### a: Active work",
                "",
                "| Field | Value |",
                "| --- | --- |",
                "| Source | issue-1 |",
                "",
                "#### repo:123: Colon-scoped work",
                "",
                "| Field | Value |",
                "| --- | --- |",
                "| Source | issue-1 |",
                "",
                "### ready-next",
                "",
                "- workstream_id=b; source_id=issue-1; <next work>",
                "",
                "## Wave Reports",
                "",
                "## Recovery Packet",
                "",
                "Root: root-1; claim=claimed; goal=test; active_workers=none; parent_closeout_watch=not-applicable",
                "Option resolution refs: session_rows=fixture; scoped_rows=fixture; rows_fingerprint=auto",
                "",
                "## Worker And Delivery References",
                "",
            ]
        )
        complete_ids = [f"session:{field}" for field in session_values]
        complete_ids.extend(
            f"{scope}:{field}" for scope in scopes for field in scoped_values
        )

        with tempfile.TemporaryDirectory() as directory:
            ledger_path = Path(directory) / "ledger.md"
            ledger_path.write_text(ledger_fixture, encoding="utf-8")

            def run(selected: list[str], contents: str = ledger_fixture) -> subprocess.CompletedProcess[str]:
                selected_set = set(selected)
                normalized_rows: list[list[str]] = []
                for line in contents.split("## Discovery Sources", 1)[0].splitlines():
                    if not line.startswith("|"):
                        continue
                    cells = [cell.strip() for cell in line.strip("|").split("|")]
                    if len(cells) != 6:
                        continue
                    normalized = [
                        cell[1:-1]
                        if len(cell) >= 2 and cell.startswith("`") and cell.endswith("`")
                        else cell
                        for cell in cells
                    ]
                    if normalized[0] in selected_set:
                        normalized_rows.append(normalized)
                serialized = "".join(
                    "\t".join(row_values) + "\n"
                    for row_values in sorted(normalized_rows, key=lambda values: values[0])
                )
                packet_fingerprint = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
                configured_contents = contents.replace(
                    "rows_fingerprint=auto",
                    f"rows_fingerprint={packet_fingerprint}",
                )
                ledger_path.write_text(configured_contents, encoding="utf-8")
                configured = re.sub(
                    r"OPTION_ROW_IDS='[^']*'",
                    f"OPTION_ROW_IDS={shlex.quote(','.join(selected))}",
                    script,
                )
                configured = f"ledger={shlex.quote(str(ledger_path))}\n{configured}"
                return subprocess.run(
                    ["bash", "-c", configured],
                    check=False,
                    capture_output=True,
                    text=True,
                )

            def with_active_workers(contents: str, rows: list[str]) -> str:
                projected = contents
                pattern = re.compile(
                    r"^- worker_id=([A-Za-z0-9:_-]+); "
                    r"actual_workstream_surface=(cli-subagent|codex-app-thread); "
                    r"workstream_ids=([A-Za-z0-9,:_-]+)$"
                )
                for worker_row in rows:
                    match = pattern.match(worker_row)
                    if match is None:
                        raise AssertionError(f"invalid worker fixture row: {worker_row}")
                    worker_id, surface, assignments = match.groups()
                    for workstream_id in assignments.split(","):
                        marker = f"#### {workstream_id}:"
                        start = projected.index(marker)
                        next_heading = projected.find("\n#### ", start + len(marker))
                        next_bucket = projected.find("\n### ready-next", start + len(marker))
                        ends = [value for value in (next_heading, next_bucket) if value >= 0]
                        end = min(ends) if ends else len(projected)
                        block = projected[start:end]
                        source_row = "| Source | issue-1 |"
                        evidence_rows = (
                            f"{source_row}\n"
                            f"| Repo / surface | repo; {surface}; worker={worker_id} |\n"
                            "| Worker evidence | worker_surface=auto; "
                            f"actual_workstream_surface={surface}; status=used |"
                        )
                        block = block.replace(source_row, evidence_rows, 1)
                        projected = projected[:start] + block + projected[end:]
                registry = "\n".join(
                    [
                        "## Active Root",
                        "",
                        "Active workers:",
                        *rows,
                        "Takeover history:",
                        "",
                    ]
                )
                active_ids = sorted(pattern.match(worker_row).group(1) for worker_row in rows)
                projected = projected.replace(
                    "active_workers=none",
                    f"active_workers={','.join(active_ids)}",
                )
                return projected.replace("## Workstreams", f"{registry}\n## Workstreams")

            complete = run(complete_ids)
            self.assertEqual(complete.returncode, 0, complete.stderr)

            mismatched_packet_fingerprint = run(
                complete_ids,
                ledger_fixture.replace(
                    "rows_fingerprint=auto",
                    f"rows_fingerprint={'0' * 64}",
                ),
            )
            self.assertNotEqual(mismatched_packet_fingerprint.returncode, 0)

            inflated_default_worker_limit = run(
                complete_ids,
                ledger_fixture.replace(
                    row(
                        "session",
                        "worker_limit",
                        session_values["worker_limit"],
                    ),
                    row("session", "worker_limit", ("100", "default", "none")),
                ),
            )
            self.assertNotEqual(inflated_default_worker_limit.returncode, 0)

            positive_auto_worker_limit = run(
                complete_ids,
                ledger_fixture.replace(
                    row(
                        "session",
                        "worker_limit",
                        session_values["worker_limit"],
                    ),
                    row(
                        "session",
                        "worker_limit",
                        (
                            "2",
                            "owner-instruction",
                            "owner-ref=request-1;scope-ref=session;"
                            "target-ref=delegation:workers",
                        ),
                    ),
                ),
            )
            self.assertNotEqual(positive_auto_worker_limit.returncode, 0)

            inflated_default_app_limit = run(
                complete_ids,
                ledger_fixture.replace(
                    row(
                        "session",
                        "app_thread_limit",
                        session_values["app_thread_limit"],
                    ),
                    row("session", "app_thread_limit", ("100", "default", "none")),
                ),
            )
            self.assertNotEqual(inflated_default_app_limit.returncode, 0)

            bounded_evidence = (
                "owner-ref=request-1;scope-ref=session;"
                "target-ref=delegation:workers"
            )
            bounded_fixture = ledger_fixture.replace(
                row(
                    "session",
                    "delegation_mode",
                    session_values["delegation_mode"],
                ),
                row(
                    "session",
                    "delegation_mode",
                    ("bounded", "owner-instruction", bounded_evidence),
                ),
            ).replace(
                row(
                    "session",
                    "worker_limit",
                    session_values["worker_limit"],
                ),
                row(
                    "session",
                    "worker_limit",
                    ("2", "owner-instruction", bounded_evidence),
                ),
            )
            bounded = run(complete_ids, bounded_fixture)
            self.assertEqual(bounded.returncode, 0, bounded.stderr)

            bounded_live_workers = with_active_workers(
                bounded_fixture,
                [
                    "- worker_id=w1; actual_workstream_surface=cli-subagent; workstream_ids=a",
                    "- worker_id=w2; actual_workstream_surface=cli-subagent; workstream_ids=repo:123",
                ],
            )
            bounded_at_limit = run(complete_ids, bounded_live_workers)
            self.assertEqual(bounded_at_limit.returncode, 0, bounded_at_limit.stderr)

            bounded_over_limit = run(
                complete_ids,
                bounded_live_workers.replace(
                    row(
                        "session",
                        "worker_limit",
                        ("2", "owner-instruction", bounded_evidence),
                    ),
                    row(
                        "session",
                        "worker_limit",
                        ("1", "owner-instruction", bounded_evidence),
                    ),
                ),
            )
            self.assertNotEqual(bounded_over_limit.returncode, 0)

            mismatched_bounded_limit = run(
                complete_ids,
                bounded_fixture.replace(
                    row(
                        "session",
                        "worker_limit",
                        ("2", "owner-instruction", bounded_evidence),
                    ),
                    row(
                        "session",
                        "worker_limit",
                        (
                            "2",
                            "owner-instruction",
                            bounded_evidence.replace("request-1", "request-2"),
                        ),
                    ),
                ),
            )
            self.assertNotEqual(mismatched_bounded_limit.returncode, 0)

            app_evidence = (
                "owner-ref=request-1;scope-ref=session;"
                "target-ref=visible-app-workers"
            )
            app_fixture = ledger_fixture.replace(
                row(
                    "session",
                    "app_thread_consent",
                    session_values["app_thread_consent"],
                ),
                row(
                    "session",
                    "app_thread_consent",
                    ("granted", "owner-instruction", app_evidence),
                ),
            ).replace(
                row(
                    "session",
                    "app_thread_limit",
                    session_values["app_thread_limit"],
                ),
                row(
                    "session",
                    "app_thread_limit",
                    ("1", "owner-instruction", app_evidence),
                ),
            )
            app_threads = run(complete_ids, app_fixture)
            self.assertEqual(app_threads.returncode, 0, app_threads.stderr)

            one_app_worker = with_active_workers(
                app_fixture,
                [
                    "- worker_id=app1; actual_workstream_surface=codex-app-thread; workstream_ids=a",
                ],
            )
            app_at_limit = run(complete_ids, one_app_worker)
            self.assertEqual(app_at_limit.returncode, 0, app_at_limit.stderr)

            stale_packet_worker_ids = run(
                complete_ids,
                one_app_worker.replace("active_workers=app1", "active_workers=none"),
            )
            self.assertNotEqual(stale_packet_worker_ids.returncode, 0)

            stale_worker_assignment = run(
                complete_ids,
                one_app_worker.replace("workstream_ids=a", "workstream_ids=b"),
            )
            self.assertNotEqual(stale_worker_assignment.returncode, 0)

            mismatched_worker_surface_evidence = run(
                complete_ids,
                one_app_worker.replace(
                    "actual_workstream_surface=codex-app-thread; status=used",
                    "actual_workstream_surface=cli-subagent; status=used",
                ),
            )
            self.assertNotEqual(mismatched_worker_surface_evidence.returncode, 0)

            app_over_limit = run(
                complete_ids,
                with_active_workers(
                    app_fixture,
                    [
                        "- worker_id=app1; actual_workstream_surface=codex-app-thread; workstream_ids=a",
                        "- worker_id=app2; actual_workstream_surface=codex-app-thread; workstream_ids=repo:123",
                    ],
                ),
            )
            self.assertNotEqual(app_over_limit.returncode, 0)

            cli_surface_with_app_worker = run(
                complete_ids,
                one_app_worker.replace(
                    row(
                        "session",
                        "worker_surface",
                        session_values["worker_surface"],
                    ),
                    row(
                        "session",
                        "worker_surface",
                        ("cli-subagent", "owner-instruction", "request-1"),
                    ),
                ),
            )
            self.assertNotEqual(cli_surface_with_app_worker.returncode, 0)

            root_surface_with_cli_worker = run(
                complete_ids,
                with_active_workers(
                    ledger_fixture.replace(
                        row(
                            "session",
                            "worker_surface",
                            session_values["worker_surface"],
                        ),
                        row(
                            "session",
                            "worker_surface",
                            ("root-thread", "runtime-capability", "no-delegation"),
                        ),
                    ),
                    [
                        "- worker_id=w1; actual_workstream_surface=cli-subagent; workstream_ids=a",
                    ],
                ),
            )
            self.assertNotEqual(root_surface_with_cli_worker.returncode, 0)

            unbounded_app_consent = run(
                complete_ids,
                ledger_fixture.replace(
                    row(
                        "session",
                        "app_thread_consent",
                        session_values["app_thread_consent"],
                    ),
                    row(
                        "session",
                        "app_thread_consent",
                        ("granted", "owner-instruction", app_evidence),
                    ),
                ),
            )
            self.assertNotEqual(unbounded_app_consent.returncode, 0)

            discovery_option_row = row(
                "source:ds-001",
                "source_mutation_authority",
                ("none", "default", "none"),
            )
            discovery_source_row = (
                "| ds-001 | github-issue | owner/repo | now | sha | "
                "number | none | none |"
            )
            discovery_fixture = ledger_fixture.replace(
                "\n## Discovery Sources",
                f"\n{discovery_option_row}\n\n## Discovery Sources\n\n"
                "| Source ID | Kind | Path/Query/URL | Last Checked | "
                "Cursor/Fingerprint | Item Key Rule | "
                "source_mutation_authority | Suppression Rule |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                + discovery_source_row,
            )
            discovery_scope = run(
                [*complete_ids, "source:ds-001:source_mutation_authority"],
                discovery_fixture,
            )
            self.assertEqual(discovery_scope.returncode, 0, discovery_scope.stderr)

            unselected_discovery_scope = run(complete_ids, discovery_fixture)
            self.assertNotEqual(unselected_discovery_scope.returncode, 0)

            duplicate_discovery_scope = run(
                [*complete_ids, "source:ds-001:source_mutation_authority"],
                discovery_fixture.replace(
                    discovery_source_row,
                    f"{discovery_source_row}\n{discovery_source_row}",
                ),
            )
            self.assertNotEqual(duplicate_discovery_scope.returncode, 0)

            duplicate_workstream_scope = run(
                complete_ids,
                ledger_fixture.replace(
                    "- workstream_id=b; source_id=issue-1; <next work>",
                    "- workstream_id=b; source_id=issue-1; <next work>\n"
                    "- workstream_id=b; source_id=issue-1; <duplicate>",
                ),
            )
            self.assertNotEqual(duplicate_workstream_scope.returncode, 0)

            mismatched_app_limit = run(
                complete_ids,
                app_fixture.replace(
                    row(
                        "session",
                        "app_thread_limit",
                        ("1", "owner-instruction", app_evidence),
                    ),
                    row(
                        "session",
                        "app_thread_limit",
                        (
                            "1",
                            "owner-instruction",
                            app_evidence.replace("request-1", "request-2"),
                        ),
                    ),
                ),
            )
            self.assertNotEqual(mismatched_app_limit.returncode, 0)

            special_branch = run(
                complete_ids,
                ledger_fixture.replace(
                    row(
                        "workstream:b",
                        "branch_name",
                        scoped_values["branch_name"],
                    ),
                    row(
                        "workstream:b",
                        "branch_name",
                        ("_release", "source-contract", "issue-1"),
                    ),
                ),
            )
            self.assertEqual(special_branch.returncode, 0, special_branch.stderr)

            omitted_scope = run(
                [row_id for row_id in complete_ids if not row_id.startswith("workstream:repo:123:")]
            )
            self.assertNotEqual(omitted_scope.returncode, 0)

            stale_scope_row = row(
                "workstream:removed",
                "merge_authority",
                ("explicit-owner-authorization", "owner-instruction", "request-1"),
            )
            stale_scope = run(
                complete_ids,
                ledger_fixture.replace(
                    "\n## Discovery Sources",
                    f"\n{stale_scope_row}\n\n## Discovery Sources",
                ),
            )
            self.assertNotEqual(stale_scope.returncode, 0)

            malformed_stale_scope = run(
                complete_ids,
                ledger_fixture.replace(
                    "\n## Discovery Sources",
                    "\n| row_id | workstream:removed | merge_authority | "
                    "explicit-owner-authorization | owner-instruction | "
                    "owner-ref=request-1;scope-ref=workstream:removed;target-ref=pr-9 |"
                    "\n\n## Discovery Sources",
                ),
            )
            self.assertNotEqual(malformed_stale_scope.returncode, 0)

            valid_branch_row = row(
                "workstream:b",
                "branch_name",
                scoped_values["branch_name"],
            )
            extra_column = run(
                complete_ids,
                ledger_fixture.replace(
                    valid_branch_row,
                    valid_branch_row[:-1] + " `unencoded|data` |",
                ),
            )
            self.assertNotEqual(extra_column.returncode, 0)

            missing_id = "workstream:b:publication_authority"
            missing_row = row(
                "workstream:b",
                "publication_authority",
                scoped_values["publication_authority"],
            )
            missing_from_both = run(
                [row_id for row_id in complete_ids if row_id != missing_id],
                ledger_fixture.replace(f"{missing_row}\n", ""),
            )
            self.assertNotEqual(missing_from_both.returncode, 0)

            missing_session_id = "session:raw_worktree_fallback"
            missing_session_row = row(
                "session",
                "raw_worktree_fallback",
                session_values["raw_worktree_fallback"],
            )
            missing_required_session = run(
                [row_id for row_id in complete_ids if row_id != missing_session_id],
                ledger_fixture.replace(f"{missing_session_row}\n", ""),
            )
            self.assertNotEqual(missing_required_session.returncode, 0)

            valid_publication = row(
                "workstream:a",
                "publication_authority",
                scoped_values["publication_authority"],
            )
            invalid_publication = row(
                "workstream:a",
                "publication_authority",
                ("prd-backed-pull-request", "default", "none"),
            )
            invalid_source = run(
                complete_ids,
                ledger_fixture.replace(valid_publication, invalid_publication),
            )
            self.assertNotEqual(invalid_source.returncode, 0)

            empty_evidence_publication = row(
                "workstream:a",
                "publication_authority",
                ("prd-backed-pull-request", "source-contract", ""),
            )
            empty_evidence = run(
                complete_ids,
                ledger_fixture.replace(
                    valid_publication,
                    empty_evidence_publication,
                ),
            )
            self.assertNotEqual(empty_evidence.returncode, 0)

            direct_evidence = (
                "owner-ref=request-1;scope-ref=workstream:a;"
                "target-ref=issue-1;target-branch=main"
            )
            direct_values = {
                "publication_authority": (
                    "explicit-owner-authorization",
                    "owner-instruction",
                    direct_evidence,
                ),
                "issue_mutation_authority": (
                    "explicit-direct-mutation",
                    "owner-instruction",
                    direct_evidence,
                ),
                "delivery_mode": ("direct-commit", "owner-instruction", direct_evidence),
                "delivery_source": ("owner-instruction", "owner-instruction", direct_evidence),
                "branch_name": ("main", "owner-instruction", direct_evidence),
                "pr_closeout": ("not-applicable", "runtime-derived", "none"),
                "pr_shape": ("none", "runtime-derived", "none"),
                "closeout_mode": (
                    "direct-commit-closes-issue",
                    "runtime-derived",
                    "none",
                ),
                "integration_mode": ("direct-commit", "runtime-derived", "none"),
            }
            direct_fixture = ledger_fixture
            for field, triple in direct_values.items():
                direct_fixture = direct_fixture.replace(
                    row("workstream:a", field, scoped_values[field]),
                    row("workstream:a", field, triple),
                )
            direct_commit = run(complete_ids, direct_fixture)
            self.assertEqual(direct_commit.returncode, 0, direct_commit.stderr)

            runtime_default_direct = run(
                complete_ids,
                direct_fixture.replace(
                    row(
                        "workstream:a",
                        "delivery_source",
                        direct_values["delivery_source"],
                    ),
                    row(
                        "workstream:a",
                        "delivery_source",
                        ("runtime-default", "default", "none"),
                    ),
                ),
            )
            self.assertNotEqual(runtime_default_direct.returncode, 0)

            direct_without_issue_mutation = run(
                complete_ids,
                direct_fixture.replace(
                    row(
                        "workstream:a",
                        "issue_mutation_authority",
                        direct_values["issue_mutation_authority"],
                    ),
                    row(
                        "workstream:a",
                        "issue_mutation_authority",
                        ("none", "default", "none"),
                    ),
                ),
            )
            self.assertNotEqual(direct_without_issue_mutation.returncode, 0)

            mismatched_delivery_source_evidence = run(
                complete_ids,
                direct_fixture.replace(
                    row(
                        "workstream:a",
                        "delivery_source",
                        direct_values["delivery_source"],
                    ),
                    row(
                        "workstream:a",
                        "delivery_source",
                        (
                            "owner-instruction",
                            "owner-instruction",
                            direct_evidence.replace("target-ref=issue-1", "target-ref=issue-2"),
                        ),
                    ),
                ),
            )
            self.assertNotEqual(mismatched_delivery_source_evidence.returncode, 0)

            issue_transfer_evidence = (
                "owner-ref=request-1;scope-ref=issue:01;"
                "target-ref=feature:example;target-branch=main;"
                "scope-transfer-ref=run"
            )
            workstream_transfer_evidence = (
                "owner-ref=request-1;scope-ref=workstream:a;"
                "target-ref=feature:example;target-branch=main;"
                "scope-transfer-ref=issue:01"
            )
            issue_mutation_transfer_evidence = (
                "owner-ref=closeout-request-2;scope-ref=issue:01;"
                "target-ref=feature:example;target-branch=main;"
                "scope-transfer-ref=run"
            )
            workstream_issue_mutation_evidence = (
                "owner-ref=closeout-request-2;scope-ref=workstream:a;"
                "target-ref=feature:example;target-branch=main;"
                "scope-transfer-ref=issue:01"
            )
            inherited_direct_values = {
                "publication_authority": (
                    "explicit-owner-authorization",
                    "source-contract",
                    workstream_transfer_evidence,
                ),
                "issue_mutation_authority": (
                    "explicit-direct-mutation",
                    "source-contract",
                    workstream_issue_mutation_evidence,
                ),
                "delivery_mode": (
                    "direct-commit",
                    "source-contract",
                    workstream_transfer_evidence,
                ),
                "delivery_source": (
                    "feature-level-inherited",
                    "source-contract",
                    workstream_transfer_evidence,
                ),
                "branch_name": (
                    "main",
                    "source-contract",
                    workstream_transfer_evidence,
                ),
                "scope_transfer_ref": (
                    "issue:01",
                    "source-contract",
                    issue_transfer_evidence,
                ),
                "issue_mutation_transfer_ref": (
                    "issue:01",
                    "source-contract",
                    issue_mutation_transfer_evidence,
                ),
                "pr_closeout": ("not-applicable", "runtime-derived", "none"),
                "pr_shape": ("none", "runtime-derived", "none"),
                "closeout_mode": (
                    "direct-commit-closes-issue",
                    "runtime-derived",
                    "none",
                ),
                "integration_mode": ("direct-commit", "runtime-derived", "none"),
            }
            inherited_direct_fixture = ledger_fixture
            for field, triple in inherited_direct_values.items():
                inherited_direct_fixture = inherited_direct_fixture.replace(
                    row("workstream:a", field, scoped_values[field]),
                    row("workstream:a", field, triple),
                )
            inherited_direct = run(complete_ids, inherited_direct_fixture)
            self.assertEqual(
                inherited_direct.returncode,
                0,
                inherited_direct.stderr,
            )

            invented_transfer_evidence = run(
                complete_ids,
                inherited_direct_fixture.replace(
                    issue_transfer_evidence,
                    issue_transfer_evidence.replace(
                        "target-ref=feature:example",
                        "target-ref=feature:invented",
                    ),
                ),
            )
            self.assertNotEqual(invented_transfer_evidence.returncode, 0)

            mismatched_transfer_ref = run(
                complete_ids,
                inherited_direct_fixture.replace(
                    "scope-transfer-ref=issue:01",
                    "scope-transfer-ref=issue:02",
                ),
            )
            self.assertNotEqual(mismatched_transfer_ref.returncode, 0)

            missing_branch_id = "workstream:a:branch_name"
            direct_branch_row = row(
                "workstream:a",
                "branch_name",
                direct_values["branch_name"],
            )
            missing_direct_branch = run(
                [row_id for row_id in complete_ids if row_id != missing_branch_id],
                direct_fixture.replace(f"{direct_branch_row}\n", ""),
            )
            self.assertNotEqual(missing_direct_branch.returncode, 0)

            mismatched_direct_branch = run(
                complete_ids,
                direct_fixture.replace(
                    direct_branch_row,
                    row(
                        "workstream:a",
                        "branch_name",
                        ("release", "owner-instruction", direct_evidence),
                    ),
                ),
            )
            self.assertNotEqual(mismatched_direct_branch.returncode, 0)

            missing_owner_ref = run(
                complete_ids,
                direct_fixture.replace(
                    direct_evidence,
                    "scope-ref=workstream:a;target-branch=main",
                ),
            )
            self.assertNotEqual(missing_owner_ref.returncode, 0)

            invalid_branch_evidence = run(
                complete_ids,
                direct_fixture.replace(
                    direct_branch_row,
                    row(
                        "workstream:a",
                        "branch_name",
                        (
                    "main",
                    "owner-instruction",
                    "owner-ref=request-2;scope-ref=workstream:a;"
                    "target-ref=issue-1;target-branch=main",
                        ),
                    ),
                ),
            )
            self.assertNotEqual(invalid_branch_evidence.returncode, 0)

            missing_publication_authority = run(
                complete_ids,
                direct_fixture.replace(
                    row(
                        "workstream:a",
                        "publication_authority",
                        direct_values["publication_authority"],
                    ),
                    row(
                        "workstream:a",
                        "publication_authority",
                        ("none", "default", "none"),
                    ),
                ),
            )
            self.assertNotEqual(missing_publication_authority.returncode, 0)

            mismatched_publication_target = run(
                complete_ids,
                direct_fixture.replace(
                    row(
                        "workstream:a",
                        "publication_authority",
                        direct_values["publication_authority"],
                    ),
                    row(
                        "workstream:a",
                        "publication_authority",
                        (
                            "explicit-owner-authorization",
                            "owner-instruction",
                            direct_evidence.replace(
                                "target-ref=issue-1",
                                "target-ref=issue-2",
                            ),
                        ),
                    ),
                ),
            )
            self.assertNotEqual(mismatched_publication_target.returncode, 0)

            invalid_ref_evidence = direct_evidence.replace(
                "target-branch=main",
                "target-branch=feature..x",
            )
            invalid_ref_fixture = direct_fixture.replace(
                direct_evidence,
                invalid_ref_evidence,
            ).replace(
                row(
                    "workstream:a",
                    "branch_name",
                    ("main", "owner-instruction", invalid_ref_evidence),
                ),
                row(
                    "workstream:a",
                    "branch_name",
                    ("feature..x", "owner-instruction", invalid_ref_evidence),
                ),
            )
            invalid_branch_ref = run(complete_ids, invalid_ref_fixture)
            self.assertNotEqual(invalid_branch_ref.returncode, 0)

            generic_merge_grant = run(
                complete_ids,
                ledger_fixture.replace(
                    row(
                        "workstream:a",
                        "merge_authority",
                        scoped_values["merge_authority"],
                    ),
                    row(
                        "workstream:a",
                        "merge_authority",
                        ("explicit-owner-authorization", "owner-instruction", "request-1"),
                    ),
                ),
            )
            self.assertNotEqual(generic_merge_grant.returncode, 0)

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

    def test_option_registries_use_snake_fields_and_kebab_values(self) -> None:
        skill = self.read("SKILL.md")
        plan_skill = (ROOT / "skills/plan-feature/SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("references/options.md", skill)
        self.assertIn("references/options.md", plan_skill)

        registries = (
            (SKILL_ROOT / "references/options.md", "## Session Registry"),
            (
                SKILL_ROOT / "references/options.md",
                "## Per-Workstream Authority And Delivery Registry",
            ),
            (ROOT / "skills/plan-feature/references/options.md", "## Registry"),
            (ROOT / "skills/plan-feature/references/options.md", "## Per-Issue Registry"),
        )
        for path, heading in registries:
            relative = path.relative_to(SKILL_ROOT) if path.is_relative_to(SKILL_ROOT) else None
            if relative is not None:
                rows = self.table_rows(str(relative), heading)
            else:
                text = path.read_text(encoding="utf-8")
                section = text.split(heading, 1)[1]
                rows = []
                for line in section.splitlines():
                    if not line.startswith("|"):
                        if rows:
                            break
                        continue
                    cells = [cell.strip() for cell in line.strip("|").split("|")]
                    if all(set(cell) <= {"-", ":", " "} for cell in cells):
                        continue
                    rows.append(cells)
                rows = rows[1:]
            for row in rows:
                field = row[0].strip("`")
                self.assertRegex(field, r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
                for value in re.findall(r"`([^`]+)`", row[1]):
                    self.assertRegex(value, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    def test_pr_closeout_branches_only_on_canonical_values(self) -> None:
        gates = self.read("references/gates.md")
        rows = self.table_rows(
            "references/prd-backed-delivery.md",
            "## Canonical PR Closeout Resolution",
        )

        merge_ready = next(row for row in rows if row[:3] == [
            "`pull-request`", "`prd-backed-pull-request`", "`merge-ready`"
        ])
        self.assertIn("Codex review", merge_ready[4])

        draft_only = next(row for row in rows if row[:3] == [
            "`pull-request`", "`prd-backed-pull-request`", "`draft-only`"
        ])
        self.assertIn("do not mark ready", draft_only[4])
        self.assertNotIn(
            "| `delivery_mode` | `no_mutation_override` |",
            self.read("references/prd-backed-delivery.md"),
        )
        self.assertIn(
            "Draft-only makes downstream ready/review/merge-ready\n"
            "gates `not-applicable`",
            gates,
        )

    def test_runtime_contract_has_no_phrase_choice_matrix(self) -> None:
        delivery = self.read("references/prd-backed-delivery.md")
        worker = self.read("references/worker.md")

        self.assertNotIn("## PR Closeout Resolution Matrix", delivery)
        self.assertIn("## Canonical PR Closeout Resolution", delivery)
        self.assertNotIn("keep the PR in draft", delivery)
        self.assertNotIn("do not merge automatically", delivery)
        self.assertNotIn("Session CLI subagents consented", worker)
        self.assertNotIn("Session Codex App threads consented", worker)
        self.assertIn("option-resolution row", delivery)
        self.assertIn("Missing `pr_closeout` becomes `merge-ready` for", delivery)

    def test_legacy_handoff_is_normalized_before_prd_routing(self) -> None:
        skill = self.read("SKILL.md")
        delivery = self.read("references/prd-backed-delivery.md")
        rows = self.table_rows(
            "references/prd-backed-delivery.md",
            "### Legacy Handoff Migration",
        )

        self.assertIn("legacy `Source PRD` data field", skill)
        source_prd = self.row_containing(rows, "`Source PRD`")
        self.assertEqual(source_prd[1], "`source_prd_ref`")

        pr_shape = self.row_containing(rows, "`PR shape`")
        self.assertEqual(pr_shape[1], "`pr_shape`")

        depends_on = self.row_containing(rows, "`Start rule: depends-on <ids>`")
        self.assertIn("`parallelization=depends-on`", depends_on[1])
        self.assertIn("`dependency_ids`", depends_on[1])

        domain_closeout = self.row_containing(rows, "`Domain closeout`")
        self.assertIn("`domain_closeout`", domain_closeout[1])
        self.assertIn("`domain_closeout_data`", domain_closeout[1])

        omitted_integration = self.row_containing(
            rows,
            "`Integration mode: omitted`",
        )
        self.assertEqual(omitted_integration[1], "`integration_mode=not-applicable`")
        legacy_feature_pr = self.row_containing(
            rows,
            "`Issue integration shape: feature-pr`",
        )
        self.assertEqual(legacy_feature_pr[1], "`integration_mode=single-repo-pr`")

        self.assertIn("`merge-ready` for `pull-request`", delivery)
        self.assertIn("`not-applicable` for `direct-commit`", delivery)
        self.assertIn("derive `single-pr` for one-repo", delivery)
        self.assertIn("`per-repo-pr` for multi-repo", delivery)
        self.assertIn("If repo scope is ambiguous, stop as `needs-owner`", delivery)
        self.assertIn("predates `integration_mode`", delivery)
        self.assertIn("ordinary inherited case to `not-applicable`", delivery)

    def test_legacy_none_worker_surface_normalizes_to_root(self) -> None:
        rows = self.table_rows(
            "references/options.md",
            "## Legacy Input Normalization",
        )

        legacy_none = self.row_containing(rows, "`delegated_worker_surface=none`")
        self.assertIn("`worker_surface=root-thread`", legacy_none[1])
        self.assertNotIn("actual_workstream_surface", legacy_none[1])

        legacy_cli = self.row_containing(
            rows,
            "`delegated_worker_surface=cli-subagent`",
        )
        self.assertIn("`worker_surface=auto`", legacy_cli[1])
        self.assertIn("explicit owner selection evidence", legacy_cli[1])

        actual_root = self.row_containing(
            rows,
            "`actual_workstream_surface=no-delegation`",
        )
        self.assertIn("`actual_workstream_surface=root-thread`", actual_root[1])

        legacy_app_limit = self.row_containing(
            rows,
            "`Session Codex App threads consented: true; max=<positive integer>`",
        )
        self.assertIn("preserve the numeric `app_thread_limit`", legacy_app_limit[1])
        legacy_app_default = self.row_containing(
            rows,
            "`Session Codex App threads consented: true; max=unspecified`",
        )
        self.assertIn("`app_thread_limit=1`", legacy_app_default[1])

        takeover = self.row_containing(rows, "`Takeover policy:")
        self.assertIn("`active_root_takeover_policy=", takeover[1])
        ambiguous_merge = self.row_containing(rows, "Global or ambiguous")
        self.assertIn("`merge_authority=none`", ambiguous_merge[1])
        self.assertIn("`needs-owner`", ambiguous_merge[1])

    def test_mutation_and_merge_grants_require_owner_scoped_evidence(self) -> None:
        options = self.read("references/options.md")
        ledger = self.read("references/ledger.md")
        gates = self.read("references/gates.md")

        self.assertIn("## Resolution Source Constraints", options)
        self.assertIn("Record exactly one row per Session Registry field", options)
        self.assertIn("exactly one row per Per-Workstream Registry field", options)
        self.assertIn(
            "`merge_authority=explicit-owner-authorization` | `owner-instruction`",
            options,
        )
        self.assertIn(
            "`publication_authority=explicit-owner-authorization` | `owner-instruction`, or `source-contract`",
            options,
        )
        self.assertIn(
            "`issue_mutation_authority=explicit-direct-mutation` | `owner-instruction`",
            options,
        )
        self.assertIn("never grants mutation, publication", options)
        self.assertIn("owner-instruction` naming the exact source/workstream target", options)
        self.assertIn("`runtime-capability`, `runtime-derived`, or", ledger)
        self.assertIn("automation_target=<source/workstream ref|none>", ledger)
        self.assertIn("`raw_worktree_fallback=owner-approved`", ledger)
        self.assertNotIn("owner explicitly authorized that fallback", ledger)
        self.assertIn(
            "`delivery_mode=direct-commit` | `owner-instruction` naming the exact instruction, workstream scope, and target branch",
            options,
        )
        active_root = ledger.split("## Active Root", 1)[1].split(
            "## Parent Closeout Watch", 1
        )[0]
        self.assertIn("Scoped merge option refs", active_root)
        self.assertNotIn("merge_authority:", active_root)
        self.assertNotIn("merge_policy:", active_root)
        self.assertIn("Evidence text is recorded for audit\nbut is never reparsed", gates)
        self.assertNotIn("authorizing instruction explicitly says", gates)

    def test_pr_shape_and_dependency_ids_reach_current_worker_contract(self) -> None:
        worker = self.read("references/worker.md")
        ledger = self.read("references/ledger.md")
        options = self.read("references/options.md")
        gates = self.read("references/gates.md")
        delivery = self.read("references/prd-backed-delivery.md")

        self.assertIn("- pr_shape: <single-pr|per-repo-pr|none>", worker)
        self.assertIn("pr_shape=<single-pr|per-repo-pr|none>", ledger)
        self.assertIn("separately recorded `dependency_ids` entry", worker)
        self.assertNotIn("separately recorded `dependency_id` entry", worker)
        self.assertIn("| parallelization | dependency_ids |", worker)
        self.assertNotIn("| Start rule |", worker)
        self.assertNotIn("depends-on proof", worker)
        self.assertIn("- dependency_reason: <reason or none>", worker)
        self.assertIn(
            "- integration_mode: <single-repo-pr|repo-pr|direct-commit|not-applicable>",
            worker,
        )
        self.assertNotIn("issue_integration_shape", worker)
        self.assertIn("dependency_reason=<reason|none>", ledger)
        self.assertIn(
            "integration_mode=<single-repo-pr|repo-pr|direct-commit|not-applicable>",
            ledger,
        )
        self.assertIn("delivery_source=<runtime-default|feature-level-inherited", ledger)
        self.assertIn("delivery_source_evidence=<scoped-option-row/source-ref|none>", ledger)
        self.assertIn("`temporary_source_execution`", options)
        self.assertIn("`completion_proof_policy`", options)
        self.assertIn("`closeout_mode`", options)
        self.assertIn("`branch_name` is required scoped data", options)
        self.assertIn(
            "scope-ref=<scope_id>;target-ref=<source-or-mutation-target>;target-branch=<branch_name>",
            options,
        )
        self.assertIn("- temporary_source_execution: <forbidden|owner-approved>", worker)
        self.assertIn("- completion_proof_policy: <live-required|synthetic-accepted>", worker)
        self.assertIn("- closeout_mode: <feature-pr-closes-issue|repo-pr-closes-issue|", worker)
        self.assertIn("- branch_name: <exact branch or not-applicable>", worker)
        self.assertIn("- scope_transfer_ref: <issue:<NN>|not-applicable>", worker)
        self.assertIn("- issue_mutation_transfer_ref: <issue:<NN>|not-applicable>", worker)
        self.assertIn("temporary_source_execution=<forbidden|owner-approved>", ledger)
        self.assertIn("completion_proof_policy=<live-required|synthetic-accepted>", ledger)
        self.assertIn("closeout_mode=<feature-pr-closes-issue|repo-pr-closes-issue|", ledger)
        self.assertIn("branch_name=<exact branch|not-applicable>", ledger)
        self.assertIn("`completion_proof_policy=synthetic-accepted`", gates)
        self.assertIn("`caller_checkout_policy=caller-checkout-approved`", gates)
        self.assertNotIn("record the explicit approval that allowed it", gates)
        self.assertIn("`temporary_source_execution=owner-approved`", delivery)
        self.assertNotIn("owner explicitly authorizes temporary-source execution", delivery)
        self.assertIn("`scope-transfer-ref=run`", delivery)
        self.assertIn("changing only `scope-ref` to that workstream", delivery)
        self.assertIn("A PRD-backed scope transfer is valid only", options)

    def test_requested_and_actual_worker_surfaces_use_distinct_canonical_fields(self) -> None:
        worker = self.read("references/worker.md")
        ledger = self.read("references/ledger.md")

        self.assertIn("- worker_surface: <auto|root-thread|codex-app-thread|cli-subagent>", worker)
        self.assertIn("- actual_workstream_surface: <root-thread|codex-app-thread|cli-subagent>", worker)
        self.assertIn("actual_workstream_surface=<root-thread|cli-subagent|codex-app-thread>", ledger)
        for stale in ("requested_surface", "actual_surface"):
            self.assertNotIn(stale, worker)
            self.assertNotIn(stale, ledger)

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
        self.assertIn("publication_authority=prd-backed-pull-request", ledger)
        self.assertIn("default it to `merge-ready`", ledger)

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
        self.assertIn("- pr_shape: `single-pr`, `per-repo-pr`, or `none`", prd_template)
        self.assertIn("- pr_closeout: [merge-ready | draft-only | not-applicable]", issue_template)
        self.assertIn(
            "`pr_closeout=draft-only` with `source=owner-instruction` or `source-prd`",
            (ROOT / "skills/plan-feature/references/prd-phase.md").read_text(
                encoding="utf-8"
            ),
        )
        plan_skill = (ROOT / "skills/plan-feature/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("canonical\n  option-resolution row selects it", plan_skill)
        self.assertIn("separate `no_mutation_override` value", plan_skill)

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
                "GitStack `not-requested`",
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
                "Only through a proven `stale` or `not-requested` row.",
                "Record that the comment was rejected as evidence.",
            ],
        ]
        self.assertEqual(rows, expected_rows)

        self.assertIn(
            "reviews check --provider codex --repo <owner/repo>\n"
            "--pr <number> --head <current-sha>",
            gates,
        )
        self.assertIn("request_head=<sha|none>", ledger)
        self.assertIn("result_kind=<formal-review|provider-comment|clean-reaction|none>", ledger)
        self.assertIn(
            "authenticated Codex clean reaction that GitStack binds",
            gates,
        )
        self.assertIn("reports as `clean` with\n  `head_is_current=true`", gates)
        self.assertIn("worker must rerun `reviews check`", worker)
        self.assertIn("for that refreshed SHA", worker)
        self.assertIn(
            "same-SHA check returns `not-requested` or `stale` with\n"
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

    def test_parent_prd_closeout_follows_successful_current_head_review(self) -> None:
        skill = self.read("SKILL.md")
        delivery = self.read("references/prd-backed-delivery.md")
        gates = self.read("references/gates.md")
        ledger = self.read("references/ledger.md")
        worker = self.read("references/worker.md")
        issue_phase = (
            ROOT / "skills/plan-feature/references/issue-phase.md"
        ).read_text(encoding="utf-8")
        issue_template = (
            ROOT / "skills/plan-feature/references/issue-body-template.md"
        ).read_text(encoding="utf-8")
        tracker = (
            ROOT / "skills/project-memory/references/issue-tracker-github.md"
        ).read_text(encoding="utf-8")
        normalized_skill = " ".join(skill.split())
        normalized_gates = " ".join(gates.split())

        state_section = gates.split(
            "Use this closeout state order for merge-ready PR work:", 1
        )[1].split("Do not final-answer", 1)[0]
        states = [
            match.group(1)
            for line in state_section.splitlines()
            if (match := re.match(r"\d+\. `([^`]+)`", line))
        ]

        self.assertLess(
            states.index("fresh-current-head-result-current"),
            states.index("parent-prd-closeout-resolved"),
        )
        self.assertLess(
            states.index("parent-prd-closeout-resolved"),
            states.index("post-closeout-head-current"),
        )
        self.assertLess(
            states.index("post-closeout-head-current"),
            states.index("parent-closeout-watch-established"),
        )
        self.assertLess(
            states.index("parent-closeout-watch-established"),
            states.index("merge-ready-report"),
        )
        self.assertIn("current-head Codex review gate passes", normalized_skill)
        self.assertIn("`Closes #<PRD-number>`", delivery)
        self.assertIn("`Closes owner/repo#<PRD-number>`", delivery)
        self.assertIn("all PRD closeout proof is satisfied", gates)
        self.assertIn(
            "parent_prd_closeout=<not-applicable|pending-review|pending-closeout|deferred-to-default-branch|armed|closed|blocked>",
            ledger,
        )
        self.assertIn(
            "parent_prd_applicability=<required|deferred-vehicle|not-applicable>",
            ledger,
        )
        self.assertIn("parent_prd_applicability_reason=", ledger)
        self.assertIn("parent_closeout_head=<sha|none>", ledger)
        self.assertIn("parent_closeout_base=<branch|none>", ledger)
        self.assertIn("parent_closeout_vehicle=<pr-ref|pending|none>", ledger)
        self.assertIn(
            "parent_closeout_watch=<not-applicable|root-monitoring|owner-handoff|automation-handoff|complete>",
            ledger,
        )
        self.assertIn("default_branch=<branch|none>", ledger)
        self.assertIn("none of\nthose proof fields may be `none`", ledger)
        self.assertIn("requires\n`parent_prd_closeout=not-applicable`", ledger)
        closeout_hygiene = ledger.split("## Closeout Hygiene", 1)[1]
        self.assertIn(
            "merge-ready reporting requires `parent_prd_closeout=armed`",
            " ".join(closeout_hygiene.split()),
        )
        self.assertIn(
            "`parent_closeout_head` equal to the current reviewed SHA",
            closeout_hygiene,
        )
        self.assertIn("PR-body evidence", closeout_hygiene)
        self.assertIn(
            "excluded workstreams must record `not-applicable`", closeout_hygiene
        )
        self.assertIn("A worker must not add or remove the parent PRD", worker)
        self.assertIn("post-review mutation", worker)
        self.assertIn("Immediately before the root updates the PR body", gates)
        self.assertIn("immediately before the merge-ready report", normalized_gates)
        self.assertIn("set\n`parent_prd_closeout=pending-review`", gates)
        self.assertIn("current PR body after the body update", normalized_gates)
        self.assertIn("live body or its fingerprint", normalized_gates)
        self.assertIn(
            "`merge_authority=explicit-owner-authorization`", gates
        )
        self.assertIn(
            "required when `merge_authority=none`", gates
        )
        self.assertIn("real event-driven monitor", normalized_gates)
        self.assertIn(
            "record parent closeout as `not-applicable`", normalized_gates
        )
        self.assertIn(
            "Reconcile the PR body before current-head review preflight", gates
        )
        self.assertIn(
            "must remove it or replace it with a non-closing reference", gates
        )
        self.assertIn("A pre-existing keyword is\nnever proof", delivery)
        self.assertIn("current default branch", delivery)
        self.assertIn("require the PR base to match it", gates)
        self.assertIn(
            "select or create a linked later default-branch PR", normalized_gates
        )
        self.assertIn("current PR may report merge-ready", normalized_gates)
        self.assertIn("state `deferred-to-default-branch`", ledger)
        self.assertIn("reason `draft-only`", closeout_hygiene)
        self.assertIn(
            "no `armed` unmerged PR or `deferred-to-default-branch` vehicle remains outstanding",
            " ".join(ledger.split()),
        )
        self.assertIn("## Parent Closeout Watch", ledger)
        self.assertIn("Do not mark the ledger `complete` while a parent PRD is only `armed`", ledger)
        self.assertIn("watch `complete`, parent closeout `closed`", ledger)
        self.assertIn("`armed` is not terminal parent closure", gates)
        self.assertIn("durable watch packet", gates)
        self.assertIn("parent closeout to `closed`", gates)
        self.assertIn("Treat `armed` as a monitored pre-merge state", delivery)
        self.assertIn(
            "`parent_closeout_base` equal to the current `default_branch`",
            closeout_hygiene,
        )
        for producer in (issue_phase, issue_template, tracker):
            normalized = " ".join(producer.split())
            self.assertIn("Do not add the parent PRD", normalized)
            self.assertIn("all PRD closeout gates pass", normalized)
            self.assertNotIn(
                "unless the maintainer says the whole PRD is complete", producer
            )
        for plan_producer in (issue_phase, issue_template):
            normalized = " ".join(plan_producer.split())
            self.assertIn("root delivery orchestrator", normalized)
            self.assertIn("final current-head review", normalized)
        self.assertIn("root delivery orchestrator", " ".join(tracker.split()))


if __name__ == "__main__":
    unittest.main()
