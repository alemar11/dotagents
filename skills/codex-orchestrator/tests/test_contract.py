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

CURRENT_LEDGER_HEADINGS = (
    "## Scope",
    "## Option Resolution",
    "### Session Rows",
    "### Scoped Rows",
    "## Discovery Sources",
    "## Active Root",
    "## Codex Review Wait Registry",
    "## Feature Spec Thread Registry",
    "## Parent Closeout Watch",
    "## Recovery Packet",
    "## Worker And Delivery References",
    "## Gate Policy",
    "## Workstreams",
    "### active",
    "### autonomous",
    "### needs-owner",
    "### ready-next",
    "### blocked",
    "### ignored-or-suppressed",
    "### deferred",
    "### completed",
    "### released",
    "## Wave Reports",
    "## Runtime Metrics",
    "## Notes",
)

CURRENT_LEDGER_STATUSES = {
    "active",
    "paused",
    "blocked",
    "complete",
    "released",
    "archived",
}


class OrchestratorContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (SKILL_ROOT / relative).read_text(encoding="utf-8")

    def ledger_template_body(self) -> str:
        template = self.read("references/ledger-template.md")
        return template.split("```md\n", 1)[1].rsplit("\n```", 1)[0]

    def is_current_ledger(self, contents: str) -> bool:
        structural_lines: list[str] = []
        headings: list[tuple[int, str]] = []
        fence_char: str | None = None
        fence_length = 0
        for raw_line in contents.splitlines():
            line = raw_line.rstrip()
            if fence_char is not None:
                closing = re.fullmatch(
                    rf" {{0,3}}{re.escape(fence_char)}{{{fence_length},}}[ \t]*",
                    line,
                )
                if closing:
                    fence_char = None
                    fence_length = 0
                continue

            opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
            if opening and not (
                opening.group(1).startswith("`") and "`" in opening.group(2)
            ):
                fence_char = opening.group(1)[0]
                fence_length = len(opening.group(1))
                continue
            if "<!--" in line or "-->" in line or line.lstrip().startswith("<"):
                return False
            if re.fullmatch(r" {0,3}(?:=+|-+)[ \t]*", line):
                return False
            line = re.sub(r"^ {1,3}(?=#)", "", line)
            atx = re.fullmatch(r"(?P<marks>#{1,6})(?:[ \t]+(?P<title>.*))?", line)
            if atx:
                title = (atx.group("title") or "").strip()
                title = re.sub(r"[ \t]+#+[ \t]*$", "", title).rstrip()
                level = len(atx.group("marks"))
                line = f"{'#' * level} {title}"
                headings.append((level, line))
            structural_lines.append(line)
        if fence_char is not None:
            return False

        nonblank = [line for line in structural_lines if line.strip()]
        if not nonblank:
            return False
        title = re.fullmatch(r"# (?P<name>.+) Maintainer Ledger", nonblank[0])
        if title is None or not title.group("name").strip():
            return False

        h1 = [line for level, line in headings if level == 1]
        expected_h2 = [
            heading for heading in CURRENT_LEDGER_HEADINGS if heading.startswith("## ")
        ]
        expected_h3 = [
            heading for heading in CURRENT_LEDGER_HEADINGS if heading.startswith("### ")
        ]
        h2 = [line for level, line in headings if level == 2]
        h3 = [line for level, line in headings if level == 3]
        if h1 != [nonblank[0]] or h2 != expected_h2 or h3 != expected_h3:
            return False

        positions: list[int] = []
        for heading in CURRENT_LEDGER_HEADINGS:
            matches = [
                index for index, line in enumerate(structural_lines) if line == heading
            ]
            if len(matches) != 1:
                return False
            positions.append(matches[0])
        if positions != sorted(positions):
            return False

        option_start = structural_lines.index("## Option Resolution")
        option_end = structural_lines.index("## Discovery Sources")
        if [
            line
            for line in structural_lines[option_start:option_end]
            if re.match(r"^### [^#]", line)
        ] != ["### Session Rows", "### Scoped Rows"]:
            return False

        workstreams_start = structural_lines.index("## Workstreams")
        workstreams_end = structural_lines.index("## Wave Reports")
        if [
            line
            for line in structural_lines[workstreams_start:workstreams_end]
            if re.match(r"^### [^#]", line)
        ] != [heading for heading in expected_h3 if heading not in {
            "### Session Rows",
            "### Scoped Rows",
        }]:
            return False

        scope_index = structural_lines.index("## Scope")
        header = structural_lines[:scope_index]
        for prefix in ("Last updated:", "Owner:", "Status:"):
            matches = [line for line in header if line.startswith(prefix)]
            if len(matches) != 1 or not matches[0][len(prefix) :].strip():
                return False
        status = next(line for line in header if line.startswith("Status:"))
        if status.removeprefix("Status:").strip() not in CURRENT_LEDGER_STATUSES:
            return False

        recovery_start = structural_lines.index("## Recovery Packet")
        recovery_end = structural_lines.index("## Worker And Delivery References")
        recovery = structural_lines[recovery_start:recovery_end]
        packet_versions = [
            (index, line)
            for index, line in enumerate(recovery)
            if line.startswith("Packet version:")
        ]
        if len(packet_versions) != 1 or packet_versions[0][1] != "Packet version: 1":
            return False
        marker_positions = [packet_versions[0][0]]
        for prefix in ("Option resolution refs:", "References to load next:"):
            matches = [
                index
                for index, line in enumerate(recovery)
                if line.startswith(prefix)
            ]
            if len(matches) != 1:
                return False
            marker_positions.append(matches[0])
        if marker_positions != sorted(marker_positions):
            return False
        return True

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
        ledger_template = self.read("references/ledger-template.md")

        self.assertIn("Within GitStack, use the official GitHub\nconnector first", skill)
        self.assertIn("GitHub workflow skill", ledger_template)
        self.assertIn("GitHub primary transport: connector", ledger_template)
        self.assertNotIn("primary=standalone", ledger_template)
        self.assertNotIn("github-plugin", ledger_template)
        self.assertIn("authority_reused=<authority", ledger_template)

    def test_worker_actions_are_independent_and_non_cumulative(self) -> None:
        worker = self.read("references/worker.md")
        action_section = worker.split("## Worker Allowed Actions", 1)[1].split(
            "## Prompt Template", 1
        )[0]

        for action in (
            "inspect-files",
            "edit-files",
            "run-validation",
            "create-local-commit",
            "push-target-branch",
            "create-or-update-pull-request",
            "mark-pull-request-ready",
            "request-codex-review",
            "poll-codex-review",
        ):
            self.assertIn(f"`{action}`", action_section)
        self.assertIn("Actions\nare not a cumulative ladder", worker)
        self.assertIn("Merge, direct issue updates", action_section)
        self.assertNotIn("`merge-pull-request`", action_section)

    def test_gate_selection_includes_follow_up_risk_and_access(self) -> None:
        gates = self.read("references/gates.md")
        universal = gates.split("## Gate Lenses", 1)[0]

        for gate in ("`follow-up`", "`risk-follow-up`", "`credential-and-access`"):
            self.assertIn(gate, universal)

    def test_domain_closeout_survives_issue_to_worker_handoff(self) -> None:
        issue_template = (
            ROOT / "skills/plan-feature/references/issue-body-template.md"
        ).read_text(encoding="utf-8")
        delivery = self.read("references/spec-backed-delivery.md")
        worker = self.read("references/worker.md")

        for text in (issue_template, delivery, worker):
            self.assertIn("domain_closeout", text)
            self.assertIn("implementation-closeout", text)

    def test_merge_is_root_owned_and_explicit(self) -> None:
        worker = self.read("references/worker.md")
        delivery = self.read("references/spec-backed-delivery.md")
        gates = self.read("references/gates.md")

        action_section = worker.split("## Worker Allowed Actions", 1)[1].split(
            "## Prompt Template", 1
        )[0]
        self.assertNotIn("`merge-pull-request`", action_section)
        self.assertIn("pull_request_merge_permission=not-granted", delivery)
        self.assertIn("pull_request_merge_confirmation=ask-authorized-user-after-checks", delivery)
        self.assertIn("### Merge Authorization Gate", gates)

    def test_capability_and_reconciliation_contracts_are_required(self) -> None:
        worker = self.read("references/worker.md")
        ledger = self.read("references/ledger.md")

        self.assertIn("## Capability Snapshots", worker)
        self.assertIn("created, resumed, or\nforked", worker)
        self.assertIn("Reconciliation updates the current projection", ledger)
        self.assertIn("Stale Values Removed", ledger)

    def test_current_existing_ledger_skips_template_loading(self) -> None:
        ledger = self.read("references/ledger.md")
        current = self.ledger_template_body().replace(
            "Status: active|paused|blocked|complete|released|archived",
            "Status: active",
            1,
        )

        self.assertTrue(self.is_current_ledger(current))
        self.assertTrue(
            self.is_current_ledger(
                f"{current}\n   ~~~markdown\n## Scope\n# Fake Maintainer Ledger\n   ~~~\n"
            )
        )
        self.assertTrue(
            self.is_current_ledger(
                f"{current}\n```markdown\n## Scope\n# Fake Maintainer Ledger\n```\n"
            )
        )
        self.assertIn("Do not load the template for an existing\nledger that passes", ledger)

    def test_invalid_ledger_stops_before_new_template_loading(self) -> None:
        ledger = self.read("references/ledger.md")
        ledger_template = self.read("references/ledger-template.md")
        current = self.ledger_template_body().replace(
            "Status: active|paused|blocked|complete|released|archived",
            "Status: active",
            1,
        )
        malformed = (
            current.replace("## Discovery Sources\n", "", 1),
            f"{current}\n## Scope\n",
            current.replace("## Scope", "## TEMP", 1)
            .replace("## Option Resolution", "## Scope", 1)
            .replace("## TEMP", "## Option Resolution", 1),
            current.replace("Owner: <person or team>\n", "", 1),
            current.replace("Status: active", "Status: unknown", 1),
            current.replace("## Scope", "# Other Maintainer Ledger\n## Scope", 1),
            current.replace("### active", "## Other\n### active", 1),
            current.replace(
                "# <Portfolio Name> Maintainer Ledger",
                "#   Maintainer Ledger",
                1,
            ),
            current.replace("Packet version: 1", "Packet version: 10", 1),
            current.replace("Packet version: 1", "Packet version: 1-invalid", 1),
            current.replace("Packet version: 1", "__PACKET_MARKER__", 1)
            .replace("References to load next:", "Packet version: 1", 1)
            .replace("__PACKET_MARKER__", "References to load next:", 1),
            f"<!--\n{current}\n-->",
            f"{current}\n-->\n",
            f"<div>\n{current}\n</div>",
            f"{current}\n   ## Scope\n",
            f"{current}\n  ### unexpected\n",
            f"{current}\n##\tScope\n",
            f"{current}\n##\n",
            f"{current}\nUnexpected\n---\n",
            f"{current}\nUnexpected\n===\n",
        )

        for contents in malformed:
            self.assertFalse(self.is_current_ledger(contents))
        normalized_ledger = " ".join(ledger.split())
        self.assertIn("missing, duplicate, out-of-order, or wrongly nested marker", normalized_ledger)
        self.assertIn("stop as `needs-owner`", normalized_ledger)
        self.assertIn("Do not\nload `ledger-template.md`", ledger)
        self.assertIn(
            "Never use it to reinterpret or overwrite an existing invalid ledger",
            " ".join(ledger_template.split()),
        )

    def test_missing_ledger_loads_template_for_creation(self) -> None:
        ledger = self.read("references/ledger.md")
        normalized_ledger = " ".join(ledger.split())

        self.assertIn("If the resolved ledger file does not exist", normalized_ledger)
        self.assertIn("load `ledger-template.md` and create it", normalized_ledger)
        self.assertIn("set `Status: active`", normalized_ledger)
        self.assertIn("add a dated note", normalized_ledger)

    def test_current_ledger_marker_set_matches_template_structure(self) -> None:
        ledger = self.read("references/ledger.md")
        ledger_template = self.read("references/ledger-template.md")
        normalized_ledger = " ".join(ledger.split())

        for marker in CURRENT_LEDGER_HEADINGS + (
            "Packet version: 1",
            "Option resolution refs:",
            "References to load next:",
        ):
            self.assertIn(marker, ledger)
            self.assertIn(marker, ledger_template)
        self.assertIn("parsing Markdown structure,\nnot by substring search", ledger)
        self.assertIn("exactly one non-empty `Last updated:`", normalized_ledger)
        self.assertIn("Text copied into `## Notes` never satisfies", ledger)
        self.assertIn("any HTML comment marker", normalized_ledger)
        self.assertIn("makes the ledger invalid", normalized_ledger)
        self.assertIn("normalize up to three leading spaces", normalized_ledger)
        self.assertIn("use ATX headings only", normalized_ledger)
        self.assertIn("any Setext underline syntax", normalized_ledger)
        displayed_markers = (
            "## Recovery Packet",
            "Packet version: 1",
            "Option resolution refs:",
            "References to load next:",
            "## Worker And Delivery References",
            "## Notes",
        )
        marker_block = ledger.split("```text\n", 1)[1].split("\n```", 1)[0]
        positions = [marker_block.index(marker) for marker in displayed_markers]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(
            "## Ledger Resolution And Validation",
            ledger,
        )

    def test_recovery_packet_is_compact_derived_and_freshness_gated(self) -> None:
        skill = self.read("SKILL.md")
        ledger_template = self.read("references/ledger-template.md")
        recovery = self.read("references/recovery-validation.md")

        for marker in (
            "## Recovery Packet",
            "Projection fingerprint",
            "Content fingerprint",
            "Option resolution refs: session_rows=",
            "rows_fingerprint=<sha256",
            "Workstream checkpoints:",
        ):
            self.assertIn(marker, ledger_template)
        self.assertIn("compact derived projection, never\n  as authority", skill)
        self.assertIn("Read only the ledger `## Recovery Packet`", recovery)
        self.assertIn("Recompute the packet Content fingerprint", recovery)
        self.assertIn("Recompute the packet's Projection fingerprint", recovery)
        self.assertIn("re-read that generated issue's\n   current `## Orchestrator Handoff`", recovery)
        self.assertIn("OPTION_ROW_IDS=", recovery)
        self.assertIn("OPTION_SOURCE_SCOPE_IDS=", recovery)
        self.assertIn("OPTION_WORKSTREAM_SCOPE_IDS=", recovery)
        self.assertIn("PACKET_OPTION_ROWS_FINGERPRINT=", recovery)
        self.assertIn("COMPUTED_OPTION_ROWS_FINGERPRINT=", recovery)
        self.assertIn("background-codex-subagent", recovery)
        self.assertIn("visible-codex-app-task", recovery)
        self.assertIn("Reject duplicate, omitted, extra, invalid", recovery)
        self.assertIn("If any check differs, mark it `stale` or `invalid`", recovery)
        self.assertIn("never bypasses claims,\ncapabilities, permissions", recovery)

    def test_recovery_option_hash_enforces_current_schema(self) -> None:
        efficiency = self.read("references/recovery-validation.md")
        marker = efficiency.index("OPTION_ROW_IDS=")
        block_start = efficiency.rfind("```bash", 0, marker) + len("```bash")
        block_end = efficiency.index("```", marker)
        script = efficiency[block_start:block_end].strip()

        session_values = {
            "visible_app_task_permission": ("not-requested", "default", "none"),
            "unmanaged_git_worktree_fallback_permission": (
                "not-granted",
                "default",
                "none",
            ),
            "existing_orchestrator_session_takeover_policy": (
                "ask-authorized-user-before-takeover",
                "default",
                "none",
            ),
            "repository_layout": (
                "single-repository",
                "project-layout-config",
                "project-memory/config/project-layout.md",
            ),
        }
        scoped_values = {
            "tracked_work_item_update_permission": ("read-only", "default", "none"),
            "change_delivery_permission": (
                "not-required-for-uncommitted-changes",
                "default",
                "none",
            ),
            "issue_update_permission": ("no-issue-changes", "default", "none"),
            "pull_request_merge_permission": ("not-granted", "default", "none"),
            "pull_request_merge_confirmation": (
                "ask-authorized-user-after-checks",
                "default",
                "none",
            ),
            "starting_checkout_branch_handling": (
                "keep-current-branch-checked-out",
                "default",
                "none",
            ),
            "scheduled_automation_change_permission": (
                "not-granted",
                "default",
                "none",
            ),
            "temporary_source_execution_permission": (
                "not-granted",
                "default",
                "none",
            ),
            "completion_evidence_policy": (
                "require-live-system-evidence",
                "default",
                "none",
            ),
            "change_delivery_target": (
                "validated-changes-left-uncommitted",
                "default",
                "none",
            ),
            "delivery_decision_origin": (
                "safe-default-for-ad-hoc-work",
                "default",
                "none",
            ),
            "workstream_repository_layout": (
                "single-repository",
                "runtime-derived",
                "none",
            ),
            "codex_review_requirement": (
                "not-needed-for-selected-delivery-target",
                "runtime-derived",
                "none",
            ),
            "pull_request_count_strategy": (
                "no-pull-request",
                "runtime-derived",
                "none",
            ),
            "issue_completion_method": (
                "no-issue-completion",
                "runtime-derived",
                "none",
            ),
            "feature_spec_ref": (
                "not-applicable",
                "runtime-derived",
                "none",
            ),
            "feature_spec_title": (
                "not-applicable",
                "runtime-derived",
                "none",
            ),
            "target_branch_name": (
                "not-applicable",
                "runtime-derived",
                "none",
            ),
            "target_pull_request_ref": (
                "not-applicable",
                "runtime-derived",
                "none",
            ),
            "delivery_permission_source_issue_ref": (
                "not-applicable",
                "runtime-derived",
                "none",
            ),
            "issue_update_permission_source_issue_ref": (
                "not-applicable",
                "runtime-derived",
                "none",
            ),
        }
        scopes = ("workstream:a", "workstream:b")

        def row(scope: str, field: str, triple: tuple[str, str, str]) -> str:
            value, source_name, evidence = triple
            return (
                f"| `{scope}:{field}` | `{scope}` | `{field}` | `{value}` | "
                f"`{source_name}` | `{evidence}` |"
            )

        session_rows = [
            row("session", field, triple)
            for field, triple in session_values.items()
        ]
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
                "## Active Root",
                "",
                "Next Root Check: action=none; target=none; due_at=none",
                "Active workers:",
                "- none",
                "Takeover history:",
                "",
                "## Codex Review Wait Registry",
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
                "| Feature Spec thread | feature_spec_ref=not-applicable; "
                "feature_spec_title=not-applicable; "
                "feature_spec_thread_assignment=not-applicable; "
                "thread_goal_mode=not-applicable; "
                "thread_goal_status=not-applicable; "
                "thread_goal_dispatch_objective_sha256=not-applicable; "
                "thread_goal_reported_objective_sha256=not-applicable; "
                "thread_goal_evidence=not-applicable; "
                "thread_goal_missing_tool=not-applicable |",
                "| Repo / execution location | repo; "
                "current-orchestrator-session; worker=root |",
                "| Worker evidence | "
                "actual_execution_location=current-orchestrator-session |",
                "| Delivery | target_pull_request_ref=not-applicable |",
                "",
                "### ready-next",
                "",
                "- workstream_id=b; source_id=issue-1; next work",
                "",
                "## Wave Reports",
                "",
                "## Recovery Packet",
                "",
                "Root: root-1; claim=claimed; goal=test; active_workers=none; parent_closeout_watch=not-applicable",
                "Current wave: idle; current_workstreams=a,b; next_action=none; next_target=none; next_due_at=none",
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

            def run(
                selected: list[str],
                contents: str = ledger_fixture,
                live_thread_evidence: str = "",
            ) -> subprocess.CompletedProcess[str]:
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
                        if len(cell) >= 2
                        and cell.startswith("`")
                        and cell.endswith("`")
                        else cell
                        for cell in cells
                    ]
                    if normalized[0] in selected_set:
                        normalized_rows.append(normalized)
                serialized = "".join(
                    "\t".join(row_values) + "\n"
                    for row_values in sorted(
                        normalized_rows,
                        key=lambda values: values[0],
                    )
                )
                packet_fingerprint = hashlib.sha256(
                    serialized.encode("utf-8")
                ).hexdigest()
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
                configured = (
                    f"ledger={shlex.quote(str(ledger_path))}\n"
                    f"LIVE_THREAD_EVIDENCE_ROWS={shlex.quote(live_thread_evidence)}\n"
                    f"{configured}"
                )
                return subprocess.run(
                    ["bash", "-c", configured],
                    check=False,
                    capture_output=True,
                    text=True,
                )

            complete = run(complete_ids)
            self.assertEqual(complete.returncode, 0, complete.stderr)

            def with_session_values(
                values: dict[str, tuple[str, str, str]],
            ) -> str:
                replacement = [
                    row("session", field, triple)
                    for field, triple in values.items()
                ]
                return ledger_fixture.replace(
                    "\n".join(session_rows),
                    "\n".join(replacement),
                )

            visible_task_evidence = (
                "permission-source-ref=authorized-user:request-3;"
                "scope-ref=session;target-ref=visible-app-tasks"
            )
            visible_session = dict(session_values)
            visible_session.update(
                {
                    "visible_app_task_permission": (
                        "granted-by-authorized-user",
                        "authorized-user-instruction",
                        visible_task_evidence,
                    ),
                }
            )
            visible = run(complete_ids, with_session_values(visible_session))
            self.assertEqual(visible.returncode, 0, visible.stderr)

            def with_visible_worker(contents: str) -> str:
                configured = contents.replace(
                    "Active workers:\n"
                    "- none\n"
                    "Takeover history:",
                    "Active workers:\n"
                    "- worker_id=worker-1; "
                    "actual_execution_location=visible-codex-app-task; "
                    "workstream_ids=a\n"
                    "Takeover history:",
                )
                configured = configured.replace(
                    "| Repo / execution location | repo; "
                    "current-orchestrator-session; worker=root |\n"
                    "| Worker evidence | "
                    "actual_execution_location=current-orchestrator-session |",
                    "| Repo / execution location | repo; "
                    "visible-codex-app-task; worker=worker-1 |\n"
                    "| Worker evidence | "
                    "actual_execution_location=visible-codex-app-task |",
                )
                configured = configured.replace(
                    "feature_spec_thread_assignment=not-applicable; "
                    "thread_goal_mode=not-applicable; "
                    "thread_goal_status=not-applicable; "
                    "thread_goal_dispatch_objective_sha256=not-applicable; "
                    "thread_goal_reported_objective_sha256=not-applicable; "
                    "thread_goal_evidence=not-applicable; "
                    "thread_goal_missing_tool=not-applicable |",
                    "feature_spec_thread_assignment=not-applicable; "
                    "thread_goal_mode=active; "
                    "thread_goal_status=active; "
                    "thread_goal_dispatch_objective_sha256="
                    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb; "
                    "thread_goal_reported_objective_sha256="
                    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb; "
                    "thread_goal_evidence=goal-read:worker-1@goal-ad-hoc; "
                    "thread_goal_missing_tool=not-applicable |",
                )
                return configured.replace(
                    "active_workers=none",
                    "active_workers=worker-1",
                )

            visible_without_consent = run(
                complete_ids,
                with_visible_worker(ledger_fixture),
            )
            self.assertNotEqual(visible_without_consent.returncode, 0)
            live_ad_hoc_active = (
                "worker-1\tDemo: Ad hoc\tactive\trepo\tnot-applicable\t"
                "active\tactive\t"
                "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\t"
                "goal-read:worker-1@goal-ad-hoc\tnot-applicable\t"
                "thread-read:worker-1@ad-hoc"
            )
            live_ad_hoc_pending = (
                "worker-1\tDemo: Ad hoc\tactive\trepo\tnot-applicable\t"
                "pending\tpending\t"
                "pending\t"
                "thread-message:worker-1\tnot-applicable\t"
                "thread-read:worker-1@ad-hoc"
            )
            visible_with_consent = run(
                complete_ids,
                with_visible_worker(with_session_values(visible_session)),
                live_ad_hoc_active,
            )
            self.assertEqual(
                visible_with_consent.returncode,
                0,
                visible_with_consent.stderr,
            )
            terminal_ad_hoc_goal = run(
                complete_ids,
                with_visible_worker(with_session_values(visible_session)).replace(
                    "thread_goal_status=active;",
                    "thread_goal_status=complete;",
                ),
                live_ad_hoc_active.replace(
                    "active\tactive\t",
                    "active\tcomplete\t",
                ),
            )
            self.assertNotEqual(terminal_ad_hoc_goal.returncode, 0)
            pending_visible_goal_contents = with_visible_worker(
                with_session_values(visible_session)
            ).replace(
                    "thread_goal_mode=active; thread_goal_status=active; "
                    "thread_goal_dispatch_objective_sha256="
                    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb; "
                    "thread_goal_reported_objective_sha256="
                    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb; "
                    "thread_goal_evidence=goal-read:worker-1@goal-ad-hoc; "
                    "thread_goal_missing_tool=not-applicable",
                    "thread_goal_mode=pending; thread_goal_status=pending; "
                    "thread_goal_dispatch_objective_sha256="
                    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb; "
                    "thread_goal_reported_objective_sha256=pending; "
                    "thread_goal_evidence=thread-message:worker-1; "
                    "thread_goal_missing_tool=not-applicable",
                )
            pending_visible_goal = run(
                complete_ids,
                pending_visible_goal_contents,
                live_ad_hoc_pending,
            )
            self.assertNotEqual(pending_visible_goal.returncode, 0)
            monitored_pending_visible_goal = run(
                complete_ids,
                pending_visible_goal_contents.replace(
                    "Next Root Check: action=none; target=none; due_at=none",
                    "Next Root Check: action=monitor-thread; "
                    "target=worker-1; due_at=now",
                ).replace(
                    "next_action=none; next_target=none; next_due_at=none",
                    "next_action=monitor-thread; next_target=worker-1; "
                    "next_due_at=now",
                ),
                live_ad_hoc_pending,
            )
            self.assertEqual(
                monitored_pending_visible_goal.returncode,
                0,
                monitored_pending_visible_goal.stderr,
            )

            retired_session_fields = {
                "work_delegation_policy": "orchestrator-decides-for-each-implementation-workstream",
                "delegated_worker_visibility": "background-codex-subagents-only",
                "max_concurrent_delegated_workers": "2",
                "max_visible_app_tasks": "2",
            }
            for field, value in retired_session_fields.items():
                stale_row = row("session", field, (value, "default", "none"))
                stale_contents = ledger_fixture.replace(
                    "\n".join(session_rows),
                    "\n".join([*session_rows, stale_row]),
                )
                stale = run(complete_ids, stale_contents)
                self.assertNotEqual(stale.returncode, 0, field)

            def feature_spec_contract(scope: str) -> dict[str, tuple[str, str, str]]:
                values = dict(scoped_values)
                permission_evidence = (
                    "permission-source-ref=feature-spec-default:demo;"
                    f"scope-ref={scope};target-ref=issue:01;"
                    "target-branch=feature/demo"
                )
                values.update(
                    {
                        "change_delivery_permission": (
                            "granted-for-selected-target",
                            "source-contract",
                            permission_evidence,
                        ),
                        "issue_update_permission": (
                            "pull-request-closing-keyword-only",
                            "source-contract",
                            permission_evidence,
                        ),
                        "change_delivery_target": (
                            "pull-request-ready-for-merge-but-not-merged",
                            "source-contract",
                            "issue:01",
                        ),
                        "delivery_decision_origin": (
                            "inherited-from-feature-spec",
                            "source-contract",
                            "issue:01",
                        ),
                        "codex_review_requirement": (
                            "required-on-current-pull-request-head",
                            "source-contract",
                            "issue:01",
                        ),
                        "pull_request_count_strategy": (
                            "one-pull-request-total",
                            "source-contract",
                            "issue:01",
                        ),
                        "issue_completion_method": (
                            "feature-pull-request-closing-keyword",
                            "source-contract",
                            "issue:01",
                        ),
                        "feature_spec_ref": (
                            "spec:demo",
                            "source-contract",
                            "issue:01#source_spec_ref",
                        ),
                        "feature_spec_title": (
                            "Feature Spec: Demo",
                            "source-contract",
                            "issue:01#source_spec_ref",
                        ),
                        "target_branch_name": (
                            "feature/demo",
                            "source-contract",
                            "issue:01",
                        ),
                        "target_pull_request_ref": (
                            "pending",
                            "runtime-derived",
                            "none",
                        ),
                        "delivery_permission_source_issue_ref": (
                            "issue:01",
                            "source-contract",
                            "issue:01",
                        ),
                        "issue_update_permission_source_issue_ref": (
                            "issue:01",
                            "source-contract",
                            "issue:01",
                        ),
                    }
                )
                return values

            feature_spec_rows = [
                row(scope, field, triple)
                for scope in scopes
                for field, triple in feature_spec_contract(scope).items()
            ]
            feature_spec_fixture = ledger_fixture.replace(
                "\n".join(scoped_rows),
                "\n".join(feature_spec_rows),
            ).replace(
                "| Feature Spec thread | feature_spec_ref=not-applicable; "
                "feature_spec_title=not-applicable; "
                "feature_spec_thread_assignment=not-applicable; "
                "thread_goal_mode=not-applicable; "
                "thread_goal_status=not-applicable; "
                "thread_goal_dispatch_objective_sha256=not-applicable; "
                "thread_goal_reported_objective_sha256=not-applicable; "
                "thread_goal_evidence=not-applicable; "
                "thread_goal_missing_tool=not-applicable |",
                "| Feature Spec thread | feature_spec_ref=spec:demo; "
                "feature_spec_title=Feature Spec: Demo; "
                "feature_spec_thread_assignment=not-applicable; "
                "thread_goal_mode=not-applicable; "
                "thread_goal_status=not-applicable; "
                "thread_goal_dispatch_objective_sha256=not-applicable; "
                "thread_goal_reported_objective_sha256=not-applicable; "
                "thread_goal_evidence=not-applicable; "
                "thread_goal_missing_tool=not-applicable |",
            ).replace(
                "| Delivery | target_pull_request_ref=not-applicable |",
                "| Delivery | target_pull_request_ref=pending |",
            )
            default_feature_spec = run(complete_ids, feature_spec_fixture)
            self.assertEqual(
                default_feature_spec.returncode,
                0,
                default_feature_spec.stderr,
            )

            visible_feature_spec_fixture = feature_spec_fixture.replace(
                "\n".join(session_rows),
                "\n".join(
                    row("session", field, triple)
                    for field, triple in visible_session.items()
                ),
            )
            root_owned_feature_spec = visible_feature_spec_fixture
            root_takeover = run(complete_ids, root_owned_feature_spec)
            self.assertNotEqual(root_takeover.returncode, 0)

            visible_feature_thread = visible_feature_spec_fixture.replace(
                "## Workstreams",
                "## Feature Spec Thread Registry\n\n"
                "| feature_spec_ref | feature_spec_title | visible_thread_id | "
                "live_thread_title | workstream_ids | repository_refs | "
                "pull_request_refs | lifecycle_owner | codex_review_poll_owner | "
                "state | last_read | drift | corrective_message_evidence | "
                "thread_state_evidence | thread_goal_mode | thread_goal_status | "
                "thread_goal_dispatch_objective_sha256 | "
                "thread_goal_reported_objective_sha256 | thread_goal_evidence | "
                "thread_goal_missing_tool |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| spec:demo | Feature Spec: Demo | worker-1 | "
                "Feature Spec: Demo | a | repo | pending | "
                "visible-feature-spec-thread | visible-feature-spec-thread | "
                "implementing | now | none | none | thread-read:worker-1@abc | "
                "active | active | "
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | "
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | "
                "goal-read:worker-1@goal-abc | not-applicable |\n\n"
                "## Workstreams",
            )
            visible_feature_thread = visible_feature_thread.replace(
                "Active workers:\n"
                "- none\n"
                "Takeover history:",
                "Active workers:\n"
                "- worker_id=worker-1; "
                "actual_execution_location=visible-codex-app-task; "
                "workstream_ids=a\n"
                "Takeover history:",
            )
            visible_feature_thread = visible_feature_thread.replace(
                "| Feature Spec thread | feature_spec_ref=spec:demo; "
                "feature_spec_title=Feature Spec: Demo; "
                "feature_spec_thread_assignment=not-applicable; "
                "thread_goal_mode=not-applicable; "
                "thread_goal_status=not-applicable; "
                "thread_goal_dispatch_objective_sha256=not-applicable; "
                "thread_goal_reported_objective_sha256=not-applicable; "
                "thread_goal_evidence=not-applicable; "
                "thread_goal_missing_tool=not-applicable |\n"
                "| Repo / execution location | repo; "
                "current-orchestrator-session; worker=root |\n"
                "| Worker evidence | "
                "actual_execution_location=current-orchestrator-session |",
                "| Feature Spec thread | feature_spec_ref=spec:demo; "
                "feature_spec_title=Feature Spec: Demo; "
                "feature_spec_thread_assignment=required; "
                "thread_goal_mode=active; "
                "thread_goal_status=active; "
                "thread_goal_dispatch_objective_sha256="
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; "
                "thread_goal_reported_objective_sha256="
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; "
                "thread_goal_evidence=goal-read:worker-1@goal-abc; "
                "thread_goal_missing_tool=not-applicable |\n"
                "| Repo / execution location | repo; "
                "visible-codex-app-task; worker=worker-1 |\n"
                "| Worker evidence | "
                "actual_execution_location=visible-codex-app-task |",
            ).replace("active_workers=none", "active_workers=worker-1")
            live_demo = (
                "worker-1\tFeature Spec: Demo\tactive\trepo\tpending\t"
                "active\tactive\t"
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\t"
                "goal-read:worker-1@goal-abc\tnot-applicable\t"
                "thread-read:worker-1@abc"
            )
            live_demo_pending = (
                "worker-1\tFeature Spec: Demo\tactive\trepo\tpending\t"
                "pending\tpending\t"
                "pending\t"
                "goal-create-message:worker-1\tnot-applicable\t"
                "thread-read:worker-1@abc"
            )
            live_demo_unavailable = (
                "worker-1\tFeature Spec: Demo\tactive\trepo\tpending\t"
                "unavailable\tnot-applicable\t"
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\t"
                "thread-read:worker-1@goal-unavailable\truntime-goal-tool\t"
                "thread-read:worker-1@abc"
            )
            assigned_feature_thread = run(
                complete_ids,
                visible_feature_thread,
                live_demo,
            )
            self.assertEqual(
                assigned_feature_thread.returncode,
                0,
                assigned_feature_thread.stderr,
            )
            missing_live_thread = run(complete_ids, visible_feature_thread)
            self.assertNotEqual(missing_live_thread.returncode, 0)
            live_repo_drift = run(
                complete_ids,
                visible_feature_thread,
                "worker-1\tFeature Spec: Demo\tactive\tother-repo\tpending\t"
                "active\tactive\t"
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\t"
                "goal-read:worker-1@goal-abc\tnot-applicable\t"
                "thread-read:worker-1@abc",
            )
            self.assertNotEqual(live_repo_drift.returncode, 0)
            encoded_title_thread = run(
                complete_ids,
                visible_feature_thread.replace(
                    "Feature Spec: Demo",
                    "Feature Spec: Import %7C Export",
                ),
                "worker-1\tFeature Spec: Import %7C Export\tactive\trepo\tpending\t"
                "active\tactive\t"
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\t"
                "goal-read:worker-1@goal-abc\tnot-applicable\t"
                "thread-read:worker-1@abc",
            )
            self.assertEqual(
                encoded_title_thread.returncode,
                0,
                encoded_title_thread.stderr,
            )
            unencoded_title_thread = run(
                complete_ids,
                visible_feature_thread.replace(
                    "Feature Spec: Demo",
                    "Feature Spec: Import | Export",
                ),
                "worker-1\tFeature Spec: Import | Export\tactive\trepo\tpending\t"
                "active\tactive\t"
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\t"
                "goal-read:worker-1@goal-abc\tnot-applicable\t"
                "thread-read:worker-1@abc",
            )
            self.assertNotEqual(unencoded_title_thread.returncode, 0)
            title_drift = run(
                complete_ids,
                visible_feature_thread.replace(
                    "| spec:demo | Feature Spec: Demo | worker-1 | "
                    "Feature Spec: Demo |",
                    "| spec:demo | Feature Spec: Demo | worker-1 | "
                    "Wrong title |",
                ),
                live_demo,
            )
            self.assertNotEqual(title_drift.returncode, 0)
            root_review_polling = run(
                complete_ids,
                visible_feature_thread.replace(
                    "visible-feature-spec-thread | visible-feature-spec-thread | "
                    "implementing",
                    "visible-feature-spec-thread | root | implementing",
                ),
                live_demo,
            )
            self.assertNotEqual(root_review_polling.returncode, 0)

            pending_goal_after_dispatch = run(
                complete_ids,
                visible_feature_thread.replace(
                    "active | active | "
                    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | "
                    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | "
                    "goal-read:worker-1@goal-abc | not-applicable",
                    "pending | pending | "
                    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | "
                    "pending | "
                    "goal-create-message:worker-1 | not-applicable",
                ),
                live_demo,
            )
            self.assertNotEqual(pending_goal_after_dispatch.returncode, 0)
            recoverable_created_pending_goal = visible_feature_thread.replace(
                "implementing | now | none | none |",
                "created | now | none | none |",
            ).replace(
                "active | active | "
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | "
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | "
                "goal-read:worker-1@goal-abc | not-applicable",
                "pending | pending | "
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | "
                "pending | "
                "goal-create-message:worker-1 | not-applicable",
            ).replace(
                "thread_goal_mode=active; thread_goal_status=active; "
                "thread_goal_dispatch_objective_sha256="
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; "
                "thread_goal_reported_objective_sha256="
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; "
                "thread_goal_evidence=goal-read:worker-1@goal-abc; "
                "thread_goal_missing_tool=not-applicable",
                "thread_goal_mode=pending; thread_goal_status=pending; "
                "thread_goal_dispatch_objective_sha256="
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; "
                "thread_goal_reported_objective_sha256=pending; "
                "thread_goal_evidence=goal-create-message:worker-1; "
                "thread_goal_missing_tool=not-applicable",
            ).replace(
                "Next Root Check: action=none; target=none; due_at=none",
                "Next Root Check: action=monitor-thread; target=worker-1; "
                "due_at=now",
            ).replace(
                "next_action=none; next_target=none; next_due_at=none",
                "next_action=monitor-thread; next_target=worker-1; "
                "next_due_at=now",
            )
            recovered_created_pending_goal = run(
                complete_ids,
                recoverable_created_pending_goal,
                live_demo_pending,
            )
            self.assertEqual(
                recovered_created_pending_goal.returncode,
                0,
                recovered_created_pending_goal.stderr,
            )
            missing_goal_evidence = run(
                complete_ids,
                visible_feature_thread.replace(
                    "goal-read:worker-1@goal-abc",
                    "none",
                ),
                live_demo,
            )
            self.assertNotEqual(missing_goal_evidence.returncode, 0)
            unavailable_goal = visible_feature_thread.replace(
                "active | active | "
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | "
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | "
                "goal-read:worker-1@goal-abc | not-applicable",
                "unavailable | not-applicable | "
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | "
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | "
                "thread-read:worker-1@goal-unavailable | runtime-goal-tool",
            ).replace(
                "thread_goal_mode=active; thread_goal_status=active; "
                "thread_goal_dispatch_objective_sha256="
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; "
                "thread_goal_reported_objective_sha256="
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; "
                "thread_goal_evidence=goal-read:worker-1@goal-abc; "
                "thread_goal_missing_tool=not-applicable",
                "thread_goal_mode=unavailable; "
                "thread_goal_status=not-applicable; "
                "thread_goal_dispatch_objective_sha256="
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; "
                "thread_goal_reported_objective_sha256="
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; "
                "thread_goal_evidence=thread-read:worker-1@goal-unavailable; "
                "thread_goal_missing_tool=runtime-goal-tool",
            )
            accepted_unavailable_goal = run(
                complete_ids,
                unavailable_goal,
                live_demo_unavailable,
            )
            self.assertEqual(
                accepted_unavailable_goal.returncode,
                0,
                accepted_unavailable_goal.stderr,
            )
            incomplete_unavailable_goal = run(
                complete_ids,
                unavailable_goal.replace(
                    "runtime-goal-tool",
                    "not-applicable",
                ),
                live_demo_unavailable,
            )
            self.assertNotEqual(incomplete_unavailable_goal.returncode, 0)
            stale_unavailable_goal_evidence = run(
                complete_ids,
                unavailable_goal.replace(
                    "thread-read:worker-1@goal-unavailable",
                    "pending",
                ),
                live_demo_unavailable,
            )
            self.assertNotEqual(
                stale_unavailable_goal_evidence.returncode,
                0,
            )
            invalid_goal_objective_fingerprint = run(
                complete_ids,
                visible_feature_thread.replace(
                    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                    "bad-fingerprint",
                ),
                live_demo,
            )
            self.assertNotEqual(
                invalid_goal_objective_fingerprint.returncode,
                0,
            )
            live_goal_objective_mismatch = run(
                complete_ids,
                visible_feature_thread,
                live_demo.replace(
                    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                    "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                ),
            )
            self.assertNotEqual(live_goal_objective_mismatch.returncode, 0)
            dispatch_and_reported_goal_mismatch = run(
                complete_ids,
                visible_feature_thread.replace(
                    "active | active | "
                    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | "
                    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |",
                    "active | active | "
                    "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd | "
                    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |",
                ).replace(
                    "thread_goal_dispatch_objective_sha256="
                    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; "
                    "thread_goal_reported_objective_sha256="
                    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa;",
                    "thread_goal_dispatch_objective_sha256="
                    "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd; "
                    "thread_goal_reported_objective_sha256="
                    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa;",
                ),
                live_demo,
            )
            self.assertNotEqual(
                dispatch_and_reported_goal_mismatch.returncode,
                0,
            )
            contradictory_complete_goal = visible_feature_thread.replace(
                "active | active | "
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |",
                "active | complete | "
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |",
            ).replace(
                "thread_goal_mode=active; thread_goal_status=active;",
                "thread_goal_mode=active; thread_goal_status=complete;",
            )
            live_demo_complete = live_demo.replace(
                "active\tactive\t",
                "active\tcomplete\t",
            )
            rejected_early_complete_goal = run(
                complete_ids,
                contradictory_complete_goal,
                live_demo_complete,
            )
            self.assertNotEqual(rejected_early_complete_goal.returncode, 0)
            accepted_terminal_goal = run(
                complete_ids,
                contradictory_complete_goal.replace(
                    "implementing | now | none | none |",
                    "target-complete | now | none | none |",
                ),
                live_demo_complete,
            )
            self.assertEqual(
                accepted_terminal_goal.returncode,
                0,
                accepted_terminal_goal.stderr,
            )

            monitored_feature_thread = visible_feature_thread.replace(
                "Next Root Check: action=none; target=none; due_at=none",
                "Next Root Check: action=monitor-thread; target=worker-1; due_at=now",
            ).replace(
                "next_action=none; next_target=none; next_due_at=none",
                "next_action=monitor-thread; next_target=worker-1; next_due_at=now",
            )
            monitored = run(complete_ids, monitored_feature_thread, live_demo)
            self.assertEqual(monitored.returncode, 0, monitored.stderr)
            split_brain_action = run(
                complete_ids,
                monitored_feature_thread.replace(
                    "next_action=monitor-thread; next_target=worker-1; next_due_at=now",
                    "next_action=none; next_target=none; next_due_at=none",
                ),
                live_demo,
            )
            self.assertNotEqual(split_brain_action.returncode, 0)
            correction_without_drift = run(
                complete_ids,
                monitored_feature_thread.replace(
                    "action=monitor-thread; target=worker-1",
                    "action=send-correction; target=worker-1",
                ).replace(
                    "next_action=monitor-thread; next_target=worker-1; next_due_at=now",
                    "next_action=send-correction; next_target=worker-1; next_due_at=now",
                ),
                live_demo,
            )
            self.assertNotEqual(correction_without_drift.returncode, 0)

            observation = "a" * 64
            terminal_wait_fixture = ledger_fixture.replace(
                "## Codex Review Wait Registry\n\n",
                "## Codex Review Wait Registry\n\n"
                "| wait_record | wait_profile_pr | request_head | request_object | "
                "wait_profile | wait_budget_minutes | wait_started_at | "
                "wait_deadline | wait_state | observation_fingerprint | "
                "last_transition_at |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                f"| owner/repo#1@abc123 | owner/repo#1 | abc123 | comment:1 | "
                f"standard | 15 | t0 | t1 | terminal | {observation} | t2 |\n\n",
            ).replace(
                "| Delivery | target_pull_request_ref=not-applicable |",
                "| Delivery | target_pull_request_ref=not-applicable |\n"
                "| Codex review evidence | request_head=abc123; "
                "request_object=comment:1; checker_status=clean; "
                "wait_record=owner/repo#1@abc123; wait_profile_pr=owner/repo#1; "
                "wait_profile=standard; wait_budget_minutes=15; "
                "wait_started_at=t0; wait_deadline=t1; wait_state=terminal; "
                f"observation_fingerprint={observation}; "
                "last_transition_at=t2; terminal=clean |",
            )
            terminal_wait = run(complete_ids, terminal_wait_fixture)
            self.assertEqual(terminal_wait.returncode, 0, terminal_wait.stderr)
            contradictory_wait = run(
                complete_ids,
                terminal_wait_fixture.replace(
                    "checker_status=clean;",
                    "checker_status=pending;",
                ).replace(
                    "wait_state=terminal;",
                    "wait_state=active;",
                ).replace("last_transition_at=t2; terminal=clean", "last_transition_at=t2; terminal=none"),
            )
            self.assertNotEqual(contradictory_wait.returncode, 0)
            mismatched_terminal_outcome = run(
                complete_ids,
                terminal_wait_fixture.replace(
                    "last_transition_at=t2; terminal=clean",
                    "last_transition_at=t2; terminal=findings",
                ),
            )
            self.assertNotEqual(mismatched_terminal_outcome.returncode, 0)
            orphaned_wait = run(
                complete_ids,
                re.sub(
                    r"\n\| Codex review evidence \|[^\n]+\|",
                    "",
                    terminal_wait_fixture,
                ),
            )
            self.assertNotEqual(orphaned_wait.returncode, 0)
            deadline_drift = run(
                complete_ids,
                terminal_wait_fixture.replace(
                    "wait_started_at=t0; wait_deadline=t1;",
                    "wait_started_at=t0; wait_deadline=t9;",
                ),
            )
            self.assertNotEqual(deadline_drift.returncode, 0)

            missing_permission_source = run(
                complete_ids,
                feature_spec_fixture.replace(
                    "permission-source-ref=feature-spec-default:demo;",
                    "permission-source-ref=;",
                    1,
                ),
            )
            self.assertNotEqual(missing_permission_source.returncode, 0)

            missing_id = "workstream:a:change_delivery_target"
            missing_row = row(
                "workstream:a",
                "change_delivery_target",
                scoped_values["change_delivery_target"],
            )
            omitted = run(
                [row_id for row_id in complete_ids if row_id != missing_id],
                ledger_fixture.replace(f"{missing_row}\n", ""),
            )
            self.assertNotEqual(omitted.returncode, 0)

            duplicated = run(
                complete_ids,
                ledger_fixture.replace(missing_row, f"{missing_row}\n{missing_row}"),
            )
            self.assertNotEqual(duplicated.returncode, 0)

            retired_value = run(
                complete_ids,
                ledger_fixture.replace(
                    missing_row,
                    row(
                        "workstream:a",
                        "change_delivery_target",
                        ("local-only", "default", "none"),
                    ),
                ),
            )
            self.assertNotEqual(retired_value.returncode, 0)

            retired_field = run(
                complete_ids,
                ledger_fixture.replace(
                    missing_row,
                    row(
                        "workstream:a",
                        "delivery_mode",
                        scoped_values["change_delivery_target"],
                    ),
                ),
            )
            self.assertNotEqual(retired_field.returncode, 0)

            mismatched_fingerprint = run(
                complete_ids,
                ledger_fixture.replace(
                    "rows_fingerprint=auto",
                    f"rows_fingerprint={'0' * 64}",
                ),
            )
            self.assertNotEqual(mismatched_fingerprint.returncode, 0)

    def test_runtime_evidence_is_delta_based_and_metrics_are_exact_or_unavailable(self) -> None:
        skill = self.read("SKILL.md")
        ledger_template = self.read("references/ledger-template.md")
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
        self.assertIn("## Runtime Metrics", ledger_template)
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
        recovery = self.read("references/recovery-validation.md")
        efficiency = self.read("references/runtime-efficiency.md")

        self.assertIn("references/recovery-validation.md", skill)
        self.assertIn("only when resuming from a packet", skill)
        self.assertIn("references/runtime-efficiency.md", skill)
        self.assertIn("before entering a second wave or recording\nexact counters", skill)
        self.assertIn("a simple first wave need not load either reference", skill)
        self.assertIn("Load this reference only when resuming", recovery)
        self.assertIn("On resume, load `recovery-validation.md` first", efficiency)


    def test_option_registries_use_snake_fields_and_kebab_values(self) -> None:
        skill = self.read("SKILL.md")
        plan_skill = (ROOT / "skills/plan-feature/SKILL.md").read_text(
            encoding="utf-8"
        )
        options = self.read("references/options.md")
        recovery = self.read("references/recovery-validation.md")

        self.assertIn("references/options.md", skill)
        self.assertIn("references/options.md", plan_skill)
        self.assertIn("This section owns the exact six-column schema", options)
        self.assertIn("encode a literal `|` in evidence as `%7C`", options)
        self.assertNotIn("runtime-efficiency.md", options)
        self.assertIn("`options.md` owns the option-row schema", recovery)

        registries = (
            (SKILL_ROOT / "references/options.md", "## Primary Human Choices"),
            (SKILL_ROOT / "references/options.md", "## Session Permissions And Context"),
            (SKILL_ROOT / "references/options.md", "## Per-Workstream Permissions And Delivery"),
            (ROOT / "skills/plan-feature/references/options.md", "## Run Registry"),
            (ROOT / "skills/plan-feature/references/options.md", "## Per-Issue Registry"),
        )
        for path, heading in registries:
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
            for row in rows[1:]:
                field = row[0].strip("`")
                self.assertRegex(field, r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
                for value in re.findall(r"`([^`]+)`", row[1]):
                    self.assertRegex(value, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


    def test_delivery_target_branches_only_on_canonical_values(self) -> None:
        gates = self.read("references/gates.md")
        rows = self.table_rows(
            "references/spec-backed-delivery.md",
            "## Canonical Target Resolution",
        )

        expected_targets = [
            "validated-changes-left-uncommitted",
            "local-commit-created-without-pushing",
            "changes-pushed-to-target-branch-without-pull-request",
            "validated-draft-pull-request-published",
            "pull-request-ready-for-merge-but-not-merged",
        ]
        self.assertEqual([row[0].strip("`") for row in rows], expected_targets)

        uncommitted = rows[0]
        self.assertEqual(uncommitted[1], "`not-required-for-uncommitted-changes`")
        self.assertEqual(uncommitted[2], "`no-pull-request`")
        self.assertIn("no commit, push, or PR", uncommitted[4])

        draft = rows[3]
        self.assertEqual(draft[3], "`not-needed-for-selected-delivery-target`")
        self.assertIn("do not mark ready or request review", draft[4])

        merge_ready = rows[4]
        self.assertIn("Required on current head or explicitly skipped", merge_ready[3])
        self.assertIn("do not merge without separate permission", merge_ready[4])
        self.assertIn(
            "`change_delivery_target=pull-request-ready-for-merge-but-not-merged`",
            gates,
        )
        self.assertIn(
            "`selected-delivery-target-does-not-require-merge-ready-review`",
            gates,
        )

    def test_runtime_contract_uses_hard_cut_without_phrase_aliases(self) -> None:
        delivery = self.read("references/spec-backed-delivery.md")
        worker = self.read("references/worker.md")
        options = self.read("references/options.md")

        self.assertIn("## Applicability And Hard Cut", delivery)
        self.assertIn("Retired delivery", delivery)
        self.assertIn("Do not normalize them at runtime", delivery)
        self.assertIn("Retired surface and capability values\nare invalid input", worker)
        self.assertIn("Unknown or retired\n  orchestration fields and values are invalid input", options)
        self.assertNotIn("## Legacy Input Normalization", options)
        self.assertNotIn("## Canonical PR Closeout Resolution", delivery)


    def test_codex_review_requirement_is_target_scoped(self) -> None:
        options = self.read("references/options.md")
        delivery = self.read("references/spec-backed-delivery.md")
        gates = self.read("references/codex-review-closeout.md")
        ledger_template = self.read("references/ledger-template.md")
        worker = self.read("references/worker.md")

        rows = self.table_rows(
            "references/options.md",
            "## Per-Workstream Permissions And Delivery",
        )
        requirement = self.row_containing(rows, "`codex_review_requirement`")
        for value in (
            "`required-on-current-pull-request-head`",
            "`explicitly-skipped-by-authorized-user`",
            "`not-needed-for-selected-delivery-target`",
        ):
            self.assertIn(value, requirement[1])
        self.assertIn("Required only for a merge-ready pull request", requirement[2])
        self.assertIn(
            "`codex_review_requirement=explicitly-skipped-by-authorized-user` requires",
            options,
        )
        self.assertIn(
            "Do not wait for pending or later feedback",
            " ".join(gates.split()),
        )
        self.assertIn("codex_review=skipped", gates)
        self.assertIn("A review skip bypasses only request and wait", delivery)
        self.assertIn(
            "codex_review_requirement=<required-on-current-pull-request-head|explicitly-skipped-by-authorized-user|not-needed-for-selected-delivery-target>",
            ledger_template,
        )
        self.assertIn(
            "- codex_review_requirement: <required-on-current-pull-request-head|explicitly-skipped-by-authorized-user|not-needed-for-selected-delivery-target>",
            worker,
        )
        self.assertIn(
            "`request-codex-review` and\n`poll-codex-review` are valid only with",
            worker,
        )

    def test_retired_handoff_fields_are_rejected_before_routing(self) -> None:
        skill = self.read("SKILL.md")
        delivery = self.read("references/spec-backed-delivery.md")

        self.assertIn("reject retired vocabulary before registration", skill)
        self.assertIn("Retired delivery", delivery)
        self.assertIn("invalid. Do not normalize them at runtime", delivery)
        self.assertIn(
            "`repository_integration_method` and `pr_closeout` are not handoff fields",
            delivery,
        )
        self.assertNotIn("### Legacy Handoff Migration", delivery)


    def test_retired_worker_surface_aliases_are_rejected(self) -> None:
        options = self.read("references/options.md")
        worker = self.read("references/worker.md")
        ledger_template = self.read("references/ledger-template.md")
        skill = self.read("SKILL.md")
        recovery = self.read("references/recovery-validation.md")
        rows = self.table_rows("references/options.md", "## Derived Runtime Fields")

        actual = self.row_containing(rows, "`actual_execution_location`")
        for value in (
            "`current-orchestrator-session`",
            "`background-codex-subagent`",
            "`visible-codex-app-task`",
        ):
            self.assertIn(value, actual[1])

        self.assertNotIn("## Legacy Input Normalization", options)
        self.assertIn("Unknown or retired\n  orchestration fields and values are invalid input", options)
        self.assertIn("Retired surface and capability values\nare invalid input", worker)
        self.assertIn(
            "| `actual_execution_location` | `current-orchestrator-session`, `background-codex-subagent`, `visible-codex-app-task` |",
            worker,
        )
        for retired in (
            "work_delegation_policy",
            "delegated_worker_visibility",
            "max_concurrent_delegated_workers",
            "max_visible_app_tasks",
        ):
            self.assertNotIn(retired, options)
            self.assertNotIn(retired, worker)
            self.assertNotIn(retired, ledger_template)
            self.assertNotIn(retired, recovery)
            self.assertNotIn(retired, skill)


    def test_mutation_and_merge_grants_require_owner_scoped_evidence(self) -> None:
        options = self.read("references/options.md")
        ledger_template = self.read("references/ledger-template.md")
        gates = self.read("references/gates.md")

        self.assertIn("## Resolution Source Constraints", options)
        self.assertIn("record exactly one row for every session field", options)
        self.assertIn("record exactly one row for every per-workstream", options)
        self.assertIn(
            "Every permission-bearing value requires non-empty `permission-source-ref`,\n"
            "exact `scope-ref`, and non-empty `target-ref` tokens",
            options,
        )
        self.assertIn("require `target-branch=<target_branch_name>`", options)
        self.assertIn(
            "`pull_request_merge_permission=granted-for-named-pull-request`",
            options,
        )
        self.assertIn(
            "`change_delivery_permission=granted-for-selected-target`",
            options,
        )
        self.assertIn(
            "`issue_update_permission=direct-issue-updates-explicitly-authorized`",
            options,
        )
        self.assertIn(
            "`runtime-capability`, or `runtime-derived`",
            ledger_template,
        )
        self.assertIn(
            "unmanaged_git_worktree_fallback_permission: not-granted|granted-by-authorized-user",
            ledger_template,
        )
        active_root = ledger_template.split("## Active Root", 1)[1].split(
            "## Parent Closeout Watch", 1
        )[0]
        self.assertIn("Scoped merge option refs", active_root)
        self.assertNotIn("pull_request_merge_permission:", active_root)
        self.assertNotIn("pull_request_merge_confirmation:", active_root)
        self.assertIn("Evidence text is recorded for audit\nbut is never reparsed", gates)


    def test_pr_count_and_dependency_ids_reach_current_worker_contract(self) -> None:
        worker = self.read("references/worker.md")
        ledger_template = self.read("references/ledger-template.md")
        options = self.read("references/options.md")
        skill = self.read("SKILL.md")

        self.assertIn(
            "- pull_request_count_strategy: <one-pull-request-total|one-pull-request-per-repository|no-pull-request>",
            worker,
        )
        self.assertIn(
            "pull_request_count_strategy: one-pull-request-total|one-pull-request-per-repository|no-pull-request",
            ledger_template,
        )
        self.assertIn("separately recorded `dependency_ids` entry", worker)
        self.assertNotIn("separately recorded `dependency_id` entry", worker)
        self.assertIn("| parallelization | dependency_ids |", worker)
        self.assertIn("- dependency_reason: <reason or none>", worker)
        self.assertNotIn("repository_integration_method:", worker)
        self.assertNotIn("repository_integration_method=", ledger_template)
        self.assertIn("`repository_layout`", skill)
        self.assertIn("`repository_layout`", options)
        self.assertIn(
            "repository_layout: single-repository|monorepo|multi-repository-workspace",
            ledger_template,
        )
        self.assertIn(
            "workstream_repository_layout: single-repository|monorepo|multi-repository-workspace",
            ledger_template,
        )
        self.assertIn("`temporary_source_execution_permission`", options)
        self.assertIn("`completion_evidence_policy`", options)
        self.assertIn("`issue_completion_method`", options)
        self.assertIn("`target_branch_name`: exact branch", options)
        self.assertIn(
            "- temporary_source_execution_permission: <not-granted|granted-by-authorized-user>",
            worker,
        )
        self.assertIn(
            "- completion_evidence_policy: <require-live-system-evidence|allow-simulated-evidence-by-authorized-user-exception>",
            worker,
        )


    def test_multi_repo_workspace_flow_is_layout_gated(self) -> None:
        skill = self.read("SKILL.md")
        options = self.read("references/options.md")
        worker = self.read("references/worker.md")
        ledger_template = self.read("references/ledger-template.md")
        gates = self.read("references/gates.md")
        delivery = self.read("references/spec-backed-delivery.md")
        workspace = self.read("references/multi-repo-workspace.md")

        self.assertIn("`repository_layout=multi-repository-workspace`", skill)
        self.assertIn(
            "`multi-repository-workspace` requires loading\n"
            "  `references/multi-repo-workspace.md` before dispatch",
            options,
        )
        self.assertIn(
            "`repository_layout=multi-repository-workspace` or a\n"
            "registered source/handoff has `workspace_context=multi-repository-workspace`",
            workspace,
        )
        self.assertIn(
            "Do not load it for ordinary `single-repository` or `monorepo`",
            workspace,
        )
        self.assertIn("parent/global Feature Specs", workspace)
        self.assertIn("Repo-scoped partial Feature Specs are owned by the child repository", workspace)
        self.assertIn(
            "<workspace-parent>/.worktrees/<repo-name>/<spec-or-issue-slug>/",
            workspace,
        )
        self.assertIn("`(repo, branch, worktree)` tuple", workspace)
        self.assertIn(
            "There is no separate workspace execution mode",
            " ".join(worker.split()),
        )
        self.assertIn(
            "`repository_layout`, `issue_repository_layout`, `workspace_context`",
            delivery,
        )
        self.assertIn(
            "repository_layout: single-repository|monorepo|multi-repository-workspace",
            ledger_template,
        )
        self.assertIn(
            "temporary_source_execution_permission=<not-granted|granted-by-authorized-user>",
            ledger_template,
        )
        self.assertIn(
            "completion_evidence_policy=<require-live-system-evidence|allow-simulated-evidence-by-authorized-user-exception>",
            ledger_template,
        )
        self.assertIn(
            "`completion_evidence_policy=allow-simulated-evidence-by-authorized-user-exception`",
            gates,
        )
        self.assertIn(
            "`temporary_source_execution_permission=granted-by-authorized-user`",
            delivery,
        )
        self.assertIn("`delivery_permission_source_issue_ref`", delivery)
        self.assertIn("`issue_update_permission_source_issue_ref`", delivery)


    def test_visible_task_consent_is_distinct_from_actual_execution(self) -> None:
        options = self.read("references/options.md")
        worker = self.read("references/worker.md")
        ledger_template = self.read("references/ledger-template.md")
        skill = self.read("SKILL.md")

        self.assertIn(
            "| `visible_app_task_permission` | `not-requested`, `granted-by-authorized-user`, `denied-by-authorized-user` |",
            worker,
        )
        self.assertIn(
            "| `actual_execution_location` | `current-orchestrator-session`, `background-codex-subagent`, `visible-codex-app-task` |",
            worker,
        )
        self.assertIn(
            "visible_app_task_permission=<not-requested|granted-by-authorized-user|denied-by-authorized-user>",
            ledger_template,
        )
        self.assertIn(
            "actual_execution_location=<current-orchestrator-session|background-codex-subagent|visible-codex-app-task>",
            ledger_template,
        )
        self.assertIn(
            "internal_subdelegation: allowed-within-assigned-scope",
            ledger_template,
        )
        self.assertIn(
            "They may create and manage internal background subagents",
            worker,
        )
        self.assertIn(
            "The root and every spawned Codex thread may create internal "
            "background subagents",
            " ".join(options.split()),
        )
        self.assertIn(
            "Any worker may create and manage internal background subagents "
            "within its assigned scope and action set",
            " ".join(skill.split()),
        )
        for stale in ("requested_surface", "actual_surface", "root-thread"):
            self.assertNotIn(stale, worker)
            self.assertNotIn(stale, ledger_template)

    def test_granted_visible_threads_are_mandatory_one_per_feature_spec(self) -> None:
        skill = self.read("SKILL.md")
        options = self.read("references/options.md")
        worker = self.read("references/worker.md")
        gates = self.read("references/gates.md")
        closeout = self.read("references/codex-review-closeout.md")
        ledger_template = self.read("references/ledger-template.md")
        recovery = self.read("references/recovery-validation.md")
        multi_repo = self.read("references/multi-repo-workspace.md")

        normalized = {
            name: " ".join(value.split())
            for name, value in {
                "skill": skill,
                "options": options,
                "worker": worker,
                "gates": gates,
                "closeout": closeout,
                "ledger": ledger_template,
                "recovery": recovery,
                "multi_repo": multi_repo,
            }.items()
        }

        self.assertIn(
            "exactly one visible thread per implementation-eligible Feature Spec",
            normalized["skill"],
        )
        self.assertIn(
            "both authorizes the surface and requires its use for Feature Spec implementation",
            normalized["options"],
        )
        self.assertIn(
            "Create exactly one active visible Codex App thread for each implementation-eligible Feature Spec",
            normalized["worker"],
        )
        self.assertIn(
            "title it with the exact Feature Spec title",
            normalized["options"],
        )
        self.assertIn(
            "Do not split one Feature Spec across multiple active visible threads",
            normalized["worker"],
        )
        self.assertIn(
            "do not reuse one visible thread for multiple Feature Specs",
            normalized["worker"],
        )
        self.assertIn(
            "A multi-repository Spec still has one thread",
            normalized["worker"],
        )
        self.assertIn(
            "Every visible Codex App thread created by the orchestrator must establish its own assignment-scoped Goal before it starts",
            normalized["worker"],
        )
        self.assertIn(
            "The root cannot create or complete a Goal on another thread's behalf",
            normalized["worker"],
        )
        self.assertIn(
            "Internal background subagents are exempt",
            normalized["worker"],
        )
        self.assertIn(
            "create one visible thread per Feature Spec, not per repository",
            normalized["multi_repo"],
        )

        self.assertIn(
            "The root is orchestration-only",
            normalized["worker"],
        )
        self.assertIn(
            "must not invoke the review check/wait workflow, poll the PR review, fix findings, mutate the PR, or mark it ready",
            normalized["closeout"],
        )
        self.assertIn(
            "assigned thread is the algorithm's execution and polling owner",
            normalized["gates"],
        )
        self.assertIn(
            "Never fall back to root-owned or background-only implementation",
            normalized["worker"],
        )
        self.assertIn(
            "Inside mandatory mode, that value still means the work must integrate as one unit, but the assigned Feature Spec thread is the integration surface",
            normalized["worker"],
        )
        self.assertIn(
            "root_implementation_fallback: <forbidden|not-applicable>",
            worker,
        )

        self.assertIn("## Feature Spec Thread Registry", ledger_template)
        self.assertIn("encode `%` as `%25`, then `|` as `%7C`", ledger_template)
        self.assertIn("`feature_spec_ref`: canonical Feature Spec", options)
        self.assertIn("`feature_spec_title`: title transport", options)
        self.assertIn("codex_review_poll_owner", ledger_template)
        self.assertIn("corrective_message_evidence", ledger_template)
        self.assertIn("thread_state_evidence", ledger_template)
        self.assertIn("thread_goal_mode", ledger_template)
        self.assertIn("thread_goal_status", ledger_template)
        self.assertIn("thread_goal_dispatch_objective_sha256", ledger_template)
        self.assertIn("thread_goal_reported_objective_sha256", ledger_template)
        self.assertIn("thread_goal_evidence", ledger_template)
        self.assertIn("thread_goal_missing_tool", ledger_template)
        self.assertIn(
            "complete `## Feature Spec Thread Registry`",
            recovery,
        )
        self.assertIn(
            'feature_spec_backed=(canonical_spec_ref != "not-applicable")',
            recovery,
        )
        self.assertNotIn(
            'feature_spec_backed=(matches(origin',
            recovery,
        )
        self.assertIn(
            "Without visible-task consent, the viable App default is root or background subagent execution inside an existing owner-supplied checkout",
            normalized["worker"],
        )
        self.assertIn("LIVE_THREAD_EVIDENCE_ROWS", recovery)
        self.assertIn("`list_threads`/`read_thread` equivalents", recovery)
        self.assertIn("`post-review-disposition`", worker)
        self.assertNotIn("post-root-provided-review-response", worker)

    def test_retired_publication_authority_aliases_are_not_supported(self) -> None:
        ledger_template = self.read("references/ledger-template.md")
        delivery = self.read("references/spec-backed-delivery.md")
        retired_suffixes = ("backed-merge-ready-pr", "backed-branch-plus-draft-pr")

        for retired_suffix in retired_suffixes:
            self.assertNotIn(retired_suffix, ledger_template)
            self.assertNotIn(retired_suffix, delivery)
        self.assertNotIn("### Legacy Authority Migration", delivery)


    def test_plan_feature_and_orchestrator_share_delivery_target_contract(self) -> None:
        delivery = self.read("references/spec-backed-delivery.md")
        options = (
            ROOT / "skills/plan-feature/references/options.md"
        ).read_text(encoding="utf-8")
        spec_template = (
            ROOT / "skills/plan-feature/references/spec-template.md"
        ).read_text(encoding="utf-8")
        issue_template = (
            ROOT / "skills/plan-feature/references/issue-body-template.md"
        ).read_text(encoding="utf-8")

        targets = (
            "local-commit-created-without-pushing",
            "changes-pushed-to-target-branch-without-pull-request",
            "validated-draft-pull-request-published",
            "pull-request-ready-for-merge-but-not-merged",
        )
        for value in targets:
            self.assertIn(value, delivery)
            self.assertIn(value, options)
        for template in (spec_template, issue_template):
            self.assertIn("change_delivery_target", template)
            self.assertIn("change_delivery_permission", template)
            self.assertIn("codex_review_requirement", template)
            self.assertIn("pull_request_count_strategy", template)
            self.assertNotIn("pr_closeout:", template)
            self.assertNotIn("repository_integration_method:", template)
        self.assertIn(
            "- pull_request_count_strategy: [verified `pull_request_count_strategy` row value]",
            spec_template,
        )
        self.assertIn(
            "- issue_repository_layout: [verified `issue_repository_layout` row value]",
            issue_template,
        )
        self.assertIn(
            "`pull-request-ready-for-merge-but-not-merged`",
            options,
        )
        self.assertIn("do not resolve or override\noptions here", spec_template)


    def test_codex_review_requests_are_idempotent_per_current_head(self) -> None:
        gates = self.read("references/codex-review-closeout.md")
        ledger_template = self.read("references/ledger-template.md")
        worker = self.read("references/worker.md")
        rows = self.table_rows(
            "references/codex-review-closeout.md",
            "### Codex Review Request Matrix",
        )

        by_status = {row[0]: row for row in rows}
        self.assertEqual(by_status["GitStack `clean`"][3], "No.")
        self.assertEqual(by_status["GitStack `findings`"][3], "No for this head.")
        self.assertEqual(
            by_status["GitStack `acknowledged` or `pending`"][3],
            "No.",
        )
        for status in ("GitStack `stale`", "GitStack `not-requested`"):
            self.assertEqual(
                by_status[status][3],
                "Yes, exactly once for that SHA.",
            )
            self.assertIn("Post one request", by_status[status][2])
        self.assertEqual(
            by_status["GitStack API, authentication, or configuration error"][3],
            "No.",
        )
        self.assertIn(
            "`request-codex-review` is idempotent per PR head",
            gates,
        )
        self.assertIn("provider-authored terminal comments", gates)
        self.assertIn(
            "A normal `acknowledged` or `pending` result never activates the fallback",
            gates,
        )
        self.assertIn(
            "A new\ncommit that changes the PR head invalidates the old result and permits exactly\none new request",
            gates,
        )
        self.assertIn("request_head=<sha|none>", ledger_template)
        self.assertIn(
            "`request-codex-review` and\n`poll-codex-review` are valid only with",
            worker,
        )
        self.assertIn("Actions\nare not a cumulative ladder", worker)

    def test_required_codex_review_keeps_pr_draft_until_current_head_is_dispositioned(
        self,
    ) -> None:
        closeout = self.read("references/codex-review-closeout.md")
        delivery = self.read("references/spec-backed-delivery.md")
        options = self.read("references/options.md")
        worker = self.read("references/worker.md")
        normalized_closeout = " ".join(closeout.split())
        normalized_delivery = " ".join(delivery.split())
        normalized_options = " ".join(options.split())
        normalized_worker = " ".join(worker.split())

        state_section = closeout.split(
            "Use this closeout state order for merge-ready PR work:", 1
        )[1].split("Do not final-answer", 1)[0]
        states = [
            match.group(1)
            for line in state_section.splitlines()
            if (match := re.match(r"\d+\. `([^`]+)`", line))
        ]

        self.assertLess(
            states.index("codex-review-requested-or-reused"),
            states.index("ready-for-review"),
        )
        self.assertLess(
            states.index("current-head-terminal-result-received"),
            states.index("ready-for-review"),
        )
        self.assertLess(
            states.index("closeout-head-current"),
            states.index("ready-for-review"),
        )
        self.assertLess(
            states.index("ready-for-review"),
            states.index("post-ready-head-and-ci-current"),
        )
        self.assertIn(
            "keep it draft through the policy-specific review",
            normalized_closeout,
        )
        self.assertIn(
            "This flow uses the manual top-level PR-comment trigger `@codex review`. Automatic reviews are a separate repository setting",
            normalized_closeout,
        )
        self.assertIn(
            "Never mark a draft PR ready while required review is pending",
            normalized_closeout,
        )
        self.assertIn(
            "verified terminal current-head Codex result, fully dispositioned "
            "feedback, and no unresolved actionable findings",
            normalized_closeout,
        )
        self.assertIn(
            "keep it draft through required current-head Codex review",
            normalized_delivery,
        )
        self.assertIn(
            "then `mark-pull-request-ready` only after",
            normalized_options,
        )
        self.assertIn(
            "keep the PR draft while request and polling actions run",
            normalized_worker,
        )

    def test_codex_review_wait_budget_is_total_capped_and_pr_scoped(self) -> None:
        gates = self.read("references/codex-review-closeout.md")
        ledger_template = self.read("references/ledger-template.md")
        options = self.read("references/options.md")
        normalized_gates = " ".join(gates.split())
        wait_contract = gates.split("### Codex Review Wait Budget", 1)[1].split(
            "\n\n1. Verify the PR exists",
            1,
        )[0]
        normalized_wait_contract = " ".join(wait_contract.split())

        def duration_seconds(value: str) -> float:
            match = re.fullmatch(r"(\d+(?:\.\d+)?)([smh])", value)
            self.assertIsNotNone(match, value)
            assert match is not None
            scale = {"s": 1, "m": 60, "h": 3600}[match.group(2)]
            return float(match.group(1)) * scale

        def command_option(command: str, option: str) -> str:
            args = shlex.split(command)
            for index, value in enumerate(args):
                if value == option:
                    self.assertLess(index + 1, len(args), command)
                    return args[index + 1]
                prefix = f"{option}="
                if value.startswith(prefix):
                    return value[len(prefix) :]
            self.fail(f"{option} missing from {command}")

        self.assertIn(
            "15-minute standard or 30-minute extended total active-wait budget",
            normalized_gates,
        )
        wait_code_spans = [
            span
            for span in re.findall(r"`([^`]*reviews wait[^`]*)`", gates)
            if "--" in span
        ]
        self.assertTrue(
            all(
                span.startswith("<plugin-root>/scripts/gitstack --json reviews wait ")
                for span in wait_code_spans
            )
        )
        wait_commands = wait_code_spans
        self.assertEqual(len(wait_commands), 3)
        for command in wait_commands:
            self.assertEqual(
                shlex.split(command)[:4],
                ["<plugin-root>/scripts/gitstack", "--json", "reviews", "wait"],
            )
            self.assertEqual(command_option(command, "--provider"), "codex")
            self.assertEqual(command_option(command, "--repo"), "<owner/repo>")
            self.assertEqual(command_option(command, "--pr"), "<number>")
            self.assertEqual(command_option(command, "--head"), "<current-sha>")
        timeout_values = [command_option(command, "--timeout") for command in wait_commands]
        self.assertEqual(
            [
                duration_seconds(value)
                for value in timeout_values
                if value != "<remaining-seconds>s"
            ],
            [900, 1800],
        )
        self.assertEqual(timeout_values.count("<remaining-seconds>s"), 1)
        self.assertEqual(
            [duration_seconds(command_option(command, "--interval")) for command in wait_commands],
            [10, 10, 10],
        )
        max_intervals = [
            duration_seconds(command_option(command, "--max-interval"))
            for command in wait_commands
        ]
        self.assertEqual(max_intervals, [30, 30, 30])
        self.assertTrue(all(value <= 30 for value in max_intervals))
        check_commands = [
            span
            for span in re.findall(r"`([^`]*reviews check[^`]*)`", gates)
            if "--" in span
        ]
        self.assertEqual(len(check_commands), 1)
        check_command = check_commands[0]
        self.assertEqual(
            shlex.split(check_command)[:4],
            ["<plugin-root>/scripts/gitstack", "--json", "reviews", "check"],
        )
        self.assertEqual(command_option(check_command, "--provider"), "codex")
        self.assertEqual(command_option(check_command, "--repo"), "<owner/repo>")
        self.assertEqual(command_option(check_command, "--pr"), "<number>")
        self.assertEqual(command_option(check_command, "--head"), "<current-sha>")
        minute_values = {
            value
            for match in re.findall(
                r"\b(\d+)-minute\b|\b(\d+) minutes?\b",
                wait_contract,
            )
            for value in match
            if value
        }
        self.assertEqual(minute_values, {"15", "30"})
        self.assertIn("30 minutes after the original `wait_started_at`", gates)
        self.assertIn("never start a fresh 30-minute wait", gates)
        self.assertIn("round down to positive integer seconds", normalized_wait_contract)
        self.assertIn("When less than one second remains, do not invoke GitStack", gates)
        self.assertIn("same round-down rule and remaining-budget command", gates)
        self.assertIn("subsequent heads of that same PR", gates)
        self.assertIn("exact `wait_profile_pr`", wait_contract)
        self.assertIn(
            "If the live PR identity differs from `wait_profile_pr`",
            normalized_wait_contract,
        )
        self.assertIn("never carry an extended profile", normalized_wait_contract)
        self.assertIn(
            "partial prior wait never creates a third budget tier",
            normalized_wait_contract,
        )
        self.assertIn("`wait_state=monitoring-required`", gates)
        self.assertIn("A still-pollable review is not a blocker", gates)
        self.assertIn("preserve the request", wait_contract)
        self.assertIn("`## Codex Review Wait Registry` is the sole timing authority", wait_contract)
        self.assertIn("exactly one row keyed by", wait_contract)
        self.assertIn("reuse that row's earliest", wait_contract)
        self.assertIn("must never initialize or extend an independent window", wait_contract)
        self.assertIn(
            "no workstream may calculate a later replacement deadline",
            normalized_wait_contract,
        )
        self.assertIn(
            "`not-applicable`; do not start or resume a waiter",
            normalized_wait_contract,
        )
        self.assertNotIn("--max-interval 45s", gates)
        self.assertNotIn("--interval 15s", gates)

        self.assertIn(
            "wait_profile_pr=<pr-ref|none|not-applicable>; "
            "wait_profile=<standard|extended|not-applicable>; "
            "wait_budget_minutes=<15|30|not-applicable>",
            ledger_template,
        )
        self.assertIn("## Codex Review Wait Registry", ledger_template)
        self.assertIn("sole authority for review wait timing", ledger_template)
        self.assertIn("exactly one row for", ledger_template)
        self.assertIn("every one must carry\nthe same `wait_record`", ledger_template)
        self.assertIn("wait_record=<pr-ref@head|none|not-applicable>", ledger_template)
        self.assertIn("wait_started_at=<timestamp|none|not-applicable>", ledger_template)
        self.assertIn("wait_deadline=<timestamp|none|not-applicable>", ledger_template)
        self.assertIn(
            "observation_fingerprint=<sha256|none|not-applicable>",
            ledger_template,
        )
        self.assertIn(
            "last_transition_at=<timestamp|none|not-applicable>",
            ledger_template,
        )
        self.assertNotIn("wait_elapsed_seconds", ledger_template)
        self.assertIn(
            "wait_state=<not-started|active|monitoring-required|terminal|not-applicable>",
            ledger_template,
        )
        self.assertIn("single bounded waiter", wait_contract)
        self.assertIn("do not replace it with a caller loop", wait_contract.lower())
        self.assertIn(
            "Repeated polls\nwith the same fingerprint inside one bounded waiter perform no ledger write",
            wait_contract,
        )
        self.assertIn("write the next scheduled\n`due_at` once", wait_contract)
        self.assertNotIn("wait_profile", options)


    def test_parent_spec_closeout_follows_resolved_review_requirement(self) -> None:
        delivery = self.read("references/spec-backed-delivery.md")
        gates = self.read("references/codex-review-closeout.md")
        gate_router = self.read("references/gates.md")
        ledger = self.read("references/ledger.md")
        ledger_template = self.read("references/ledger-template.md")
        issue_phase = (
            ROOT / "skills/plan-feature/references/issue-phase.md"
        ).read_text(encoding="utf-8")
        issue_template = (
            ROOT / "skills/plan-feature/references/issue-body-template.md"
        ).read_text(encoding="utf-8")
        tracker = (
            ROOT / "skills/project-memory/references/issue-tracker-github.md"
        ).read_text(encoding="utf-8")

        state_section = gates.split(
            "Use this closeout state order for merge-ready PR work:", 1
        )[1].split("Do not final-answer", 1)[0]
        states = [
            match.group(1)
            for line in state_section.splitlines()
            if (match := re.match(r"\d+\. `([^`]+)`", line))
        ]

        self.assertLess(
            states.index("closeout-head-current"),
            states.index("parent-spec-closeout-resolved"),
        )
        self.assertLess(
            states.index("parent-spec-closeout-resolved"),
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
        self.assertIn(
            "`change_delivery_target=pull-request-ready-for-merge-but-not-merged`",
            gate_router,
        )
        self.assertIn("For every other target, do not load that reference", gate_router)
        self.assertIn("`Closes #<spec-number>`", gates)
        self.assertIn("`Closes owner/repo#<spec-number>`", gates)
        self.assertIn(
            "parent_spec_closeout=<not-applicable|pending-review|pending-closeout|deferred-to-default-branch|armed|closed|blocked>",
            ledger_template,
        )
        self.assertIn("`armed` is not terminal parent closure", gates)
        self.assertIn(
            "Completion requires `parent_spec_closeout=closed`",
            " ".join(ledger.split()),
        )
        self.assertIn("A parent Feature Spec is not complete while closeout is `armed`", ledger)
        for producer in (issue_phase, issue_template, tracker):
            normalized = " ".join(producer.split())
            self.assertIn("root delivery orchestrator", normalized)
            self.assertIn("resolved review policy", normalized)
            self.assertIn("all Feature Spec closeout gates pass", normalized)


if __name__ == "__main__":
    unittest.main()
