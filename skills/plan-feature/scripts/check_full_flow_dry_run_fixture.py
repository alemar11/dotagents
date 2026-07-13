from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = SKILLS_ROOT.parent
REMOVED_PRD_SKILL = "$to" + "-prd"
REMOVED_ISSUE_SKILL = "$to" + "-issues"
REMOVED_PRD_PATH = "skills/to" + "-prd"
REMOVED_ISSUE_PATH = "skills/to" + "-issues"
LEGACY_WORKER_AUTH_KEY = "default" + "_worker_authorization"
LEGACY_WORKER_AUTH_HEADING = "Worker " + "Authorization Defaults"
LEGACY_DEFAULT_WORKER_AUTH = "Default worker " + "authorization"
ORCHESTRATION_POLICY_PATH = "project-memory/agents/orchestration" + "-policy.md"
STALE_NO_GATES_REMAIN = "no " + "gates remain"
STALE_GATES_RESOLVED = "gates " + "resolved or deferred"
STALE_REPO_PR_PLACEHOLDERS = "repo PR links " + "or placeholders"
AUTO_DISPATCH_KEY = "auto" + "_dispatch"
WORKER_SURFACES_KEY = "worker" + "_surfaces"
MAX_ACTIVE_DELEGATED_WORKERS_KEY = "max" + "_active_delegated_workers"
MAX_ACTIVE_CLI_SUBAGENTS_KEY = "max" + "_active_cli_subagents"
MAX_ACTIVE_CODEX_APP_THREADS_KEY = "max" + "_active_codex_app_threads"
SESSION_WIDE_DELEGATED_WORKER_CAP_KEY = "session" + "_wide_delegated_worker_cap"
AUTHORIZATION_CEILING_KEY = "authorization" + "_ceiling"
RUNTIME_POLICY_FIELDS = (
    AUTO_DISPATCH_KEY + ":",
    WORKER_SURFACES_KEY + ":",
    MAX_ACTIVE_DELEGATED_WORKERS_KEY + ":",
    MAX_ACTIVE_CLI_SUBAGENTS_KEY + ":",
    MAX_ACTIVE_CODEX_APP_THREADS_KEY + ":",
    SESSION_WIDE_DELEGATED_WORKER_CAP_KEY + ":",
    AUTHORIZATION_CEILING_KEY + ":",
)
ACTIVE_TEXT_SUFFIXES = {".json", ".md", ".py", ".sh", ".toml", ".yaml", ".yml"}


def read(relative: str) -> str:
    return (SKILLS_ROOT / relative).read_text(encoding="utf-8")


def read_repo(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def option_row_evidence_is_valid(rows: list[list[str]]) -> bool:
    return all(
        source == "default" or evidence not in {"", "none"}
        for _, _, _, _, source, evidence in rows
    )


def iter_active_text_files() -> list[Path]:
    roots = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "AGENTS.md",
        SKILLS_ROOT,
        REPO_ROOT / ".agents",
    ]
    files: list[Path] = []

    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            files.append(root)
            continue
        for path in root.rglob("*"):
            if (
                path.is_file()
                and path.suffix in ACTIVE_TEXT_SUFFIXES
                and "__pycache__" not in path.parts
            ):
                files.append(path)

    return sorted(set(files))


class FullFlowDryRunFixtureTests(unittest.TestCase):
    def test_fixture_covers_pipeline_and_draft_source_prd(self) -> None:
        fixture = read("plan-feature/references/full-flow-dry-run.md")

        for text in (
            "$plan-feature",
            "$grill-me-with-context",
            "The PRD phase",
            "The issue phase",
            "$codex-orchestrator",
        ):
            self.assertIn(text, fixture)

        self.assertNotIn(REMOVED_PRD_SKILL, fixture)
        self.assertNotIn(REMOVED_ISSUE_SKILL, fixture)

        self.assertIn("effective_target: draft-publish-commands", fixture)
        self.assertIn("no_mutation_override: dry-run", fixture)
        self.assertIn("no_mutation_output: publish-commands", fixture)
        self.assertIn("option_rows_fingerprint: sha256:", fixture)
        self.assertIn("local_mirror_path: not-applicable", fixture)
        self.assertIn("branch_name: feature/account-settings-export", fixture)
        self.assertIn("the structured delivery handoff tuple", fixture)
        self.assertIn("`delivery_mode=pull-request`", fixture)
        self.assertIn("`branch_name=feature/account-settings-export`", fixture)
        self.assertIn("`pr_closeout=merge-ready`", fixture)
        self.assertIn("`pr_shape=single-pr`", fixture)
        self.assertIn("`## Orchestrator Handoff` projection carries\n   `branch_name: feature/account-settings-export`", fixture)
        self.assertIn("source_prd_ref: draft-prd:account-settings-export", fixture)
        self.assertIn("prd_body_fingerprint: sha256:7f4a9c21d003", fixture)
        self.assertIn("capture_mode: defer-to-caller", fixture)
        self.assertIn("domain_knowledge_delta", fixture)
        self.assertIn("status: required", fixture)
        self.assertIn("target_surfaces:", fixture)
        self.assertIn("evidence:", fixture)
        self.assertIn("current-repository/src/account-settings/export.ts", fixture)

        option_rows_section = fixture.split("## Canonical Run Option Rows", 1)[1].split(
            "## Expected Pipeline", 1
        )[0]
        option_rows: list[list[str]] = []
        for line in option_rows_section.splitlines():
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if cells[0] == "row_id" or all(set(cell) <= {"-", ":", " "} for cell in cells):
                continue
            self.assertEqual(len(cells), 6)
            normalized = [
                cell[1:-1]
                if len(cell) >= 2 and cell.startswith("`") and cell.endswith("`")
                else cell
                for cell in cells
            ]
            option_rows.append(normalized)

        row_ids = [row[0] for row in option_rows]
        self.assertEqual(len(row_ids), len(set(row_ids)))
        self.assertIn("run:branch_name", row_ids)
        self.assertTrue(option_row_evidence_is_valid(option_rows))
        serialized = "".join(
            "\t".join(row) + "\n" for row in sorted(option_rows, key=lambda row: row[0])
        )
        expected_fingerprint = re.search(
            r"option_rows_fingerprint: sha256:([0-9a-f]{64})",
            fixture,
        )
        self.assertIsNotNone(expected_fingerprint)
        self.assertEqual(
            hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
            expected_fingerprint.group(1),
        )
        self.assertIn("## Domain Knowledge Handoff", fixture)
        self.assertIn("## Domain Knowledge Closeout", fixture)
        self.assertIn("last integration task", fixture)
        self.assertIn("$project-memory domain-memory", fixture)
        self.assertIn("internal domain-modeling workflow", fixture)
        self.assertIn("Replace every issue body line", fixture)
        self.assertIn("must not dispatch implementation workers", fixture)
        self.assertNotIn(LEGACY_WORKER_AUTH_KEY, fixture)
        self.assertIn("project memory, plan-feature output, tracker defaults", fixture)
        self.assertIn("authorization fields or worker capability modes", fixture)
        self.assertIn("## Expected Runtime Efficiency Evidence", fixture)
        self.assertIn("each `issue-hardening:<id>`", fixture)
        self.assertIn("one `tokens=unavailable` result without estimation", fixture)
        self.assertIn("repeatedly emitted between phases", fixture)

    def test_non_default_option_sources_reject_empty_or_none_evidence(self) -> None:
        base = [["run:mode", "run", "mode", "full-flow", "owner-instruction", "request-1"]]
        self.assertTrue(option_row_evidence_is_valid(base))
        for invalid in ("", "none"):
            with self.subTest(evidence=invalid):
                row = [base[0][:-1] + [invalid]]
                self.assertFalse(option_row_evidence_is_valid(row))

        options = read("plan-feature/references/options.md")
        self.assertIn("whose `source` is not `default`", options)
        self.assertIn("neither empty nor `none`", options)

    def test_shared_contract_documents_draft_publish_handoff(self) -> None:
        contract = read("project-memory/references/tracker-publishing.md")

        self.assertIn("source_prd_ref", contract)
        self.assertIn("draft-prd:<feature-slug>", contract)
        self.assertIn("Create or update the PRD first", contract)
        self.assertIn("Replace `source_prd_ref: draft-prd:<...>`", contract)
        self.assertIn("`no_mutation_override=dry-run`", contract)
        self.assertIn("`no_mutation_override=draft-output`", contract)
        self.assertIn("Do not dispatch implementation workers", contract)
        self.assertIn("`temporary_source_execution=owner-approved`", contract)
        self.assertNotIn("explicit owner decision to use the full PRD body", contract)

    def test_project_memory_does_not_own_orchestration_policy_setup(self) -> None:
        project_memory = read("project-memory/SKILL.md")
        setup_workflow = read("project-memory/references/setup-workflow.md")
        orchestrator = read("codex-orchestrator/SKILL.md")
        worker = read("codex-orchestrator/references/worker.md")
        ledger = read("codex-orchestrator/references/ledger.md")

        self.assertNotIn(ORCHESTRATION_POLICY_PATH, project_memory)
        self.assertNotIn("orchestration-policy", setup_workflow)
        self.assertIn("## Structured Configuration", project_memory)
        self.assertNotIn(ORCHESTRATION_POLICY_PATH, orchestrator)
        self.assertIn("## Session Option Resolution", worker)
        self.assertNotIn("policy-auto-dispatched", worker)
        self.assertNotIn("policy-auto-dispatched", ledger)
        self.assertIn("delegation_mode: auto|disabled|bounded", ledger)
        self.assertIn("app_thread_consent: not-requested|granted|denied", ledger)
        self.assertIn("## Wave Reports", ledger)
        self.assertIn("Execution Report", ledger)
        self.assertNotIn("## Wave Checkpoints", ledger)

    def test_issue_tracker_templates_stay_tracker_focused(self) -> None:
        for relative in (
            "project-memory/references/issue-tracker-github.md",
            "project-memory/references/issue-tracker-local.md",
        ):
            contents = read(relative)
            normalized = " ".join(contents.split())
            with self.subTest(file=relative):
                self.assertIn("## Configuration", contents)
                self.assertIn("| Key | Type | Value | Allowed values | Meaning |", contents)
                self.assertNotIn(ORCHESTRATION_POLICY_PATH, contents)
                self.assertIn("Tracker setup records artifact routing", contents)
                self.assertIn("Branch only on the canonical `effective_target`", normalized)
                self.assertIn("`source_prd_ref`", contents)
                self.assertIn("`Source PRD` is a read-only legacy migration alias", contents)
                self.assertNotIn("current request explicitly asks for dry-run", contents)
                self.assertNotIn("current-run no-mutation override is active", contents)
                for field in RUNTIME_POLICY_FIELDS:
                    self.assertNotIn(field, contents)

        github_contract = read("project-memory/references/issue-tracker-github.md")
        self.assertIn("`source_prd_ref`, delivery metadata", github_contract)
        self.assertIn("`Source PRD` is a read-only legacy migration alias", github_contract)
        self.assertIn("`local_mirror=requested`", github_contract)
        self.assertNotIn("explicitly asks to keep a local mirror", github_contract)

        local_contract = read("project-memory/references/issue-tracker-local.md")
        self.assertIn("`effective_target=local-dry-run`", local_contract)
        self.assertNotIn("explicitly asks to keep completed issue", local_contract)

    def test_plan_feature_references_internal_phase_templates(self) -> None:
        plan_feature = read("plan-feature/SKILL.md")
        prd_phase = read("plan-feature/references/prd-phase.md")
        issue_phase = read("plan-feature/references/issue-phase.md")
        prd_template = read("plan-feature/references/prd-template.md")
        issue_template = read("plan-feature/references/issue-body-template.md")
        vertical_slices = read("plan-feature/references/vertical-slices.md")
        options = read("plan-feature/references/options.md")
        prd_delivery = read("codex-orchestrator/references/prd-backed-delivery.md")

        self.assertIn("references/full-flow-dry-run.md", plan_feature)
        self.assertIn("`tracker_backend`", plan_feature)
        self.assertIn("keyed `option_resolution` rows", plan_feature)
        self.assertIn("`branch_name`, `pr_closeout`, and `pr_shape`", plan_feature)
        self.assertIn("Keep worker surfaces, worker counts", plan_feature)
        self.assertNotIn(ORCHESTRATION_POLICY_PATH, plan_feature)
        self.assertIn("`tracker_backend` as planning-artifact write authority", plan_feature)
        self.assertIn("Planning blockers", plan_feature)
        self.assertIn("Include exactly one domain outcome", plan_feature)
        self.assertNotIn("Domain knowledge: captured in <path or durable surface>", plan_feature)
        self.assertIn("Domain knowledge: deferred to <final task ref>", plan_feature)
        self.assertIn("Domain knowledge: no durable change", plan_feature)
        self.assertIn("for required `prd-only` deltas", plan_feature)
        self.assertIn("never reports domain knowledge as captured", plan_feature)
        self.assertIn("issue lifecycle mutations belong to", plan_feature)
        self.assertNotIn(STALE_NO_GATES_REMAIN, plan_feature)
        self.assertNotIn(STALE_GATES_RESOLVED, plan_feature)
        self.assertIn("references/prd-phase.md", plan_feature)
        self.assertIn("references/issue-phase.md", plan_feature)
        self.assertIn("tracker-publishing.md", prd_phase)
        self.assertIn("## PRD Target Model", prd_phase)
        self.assertIn("PRD body fingerprint", prd_phase)
        self.assertIn("PRD planning-artifact publication", prd_phase)
        self.assertIn("tracker_backend` is the planning-artifact write authority", prd_phase)
        self.assertIn("`effective_target=configured-tracker`", prd_phase)
        self.assertIn("`local_mirror=requested`", prd_phase)
        self.assertIn("local_mirror_path: <repo-relative mirror root", prd_phase)
        self.assertIn("local_mirror_path: <repo-relative mirror root", issue_phase)
        self.assertIn("branch_name: <feature branch or exact authorized direct-commit target branch>", prd_phase)
        self.assertIn("branch_name: <feature branch or exact authorized direct-commit target branch>", issue_phase)
        self.assertIn("For `effective_target=local-dry-run`", prd_phase)
        self.assertIn("exact owner\n  instruction, feature scope, and authorized target branch", prd_phase)
        self.assertIn("the structured delivery handoff tuple: `delivery_mode`,", prd_phase)
        self.assertIn("`issue_mutation_authority`, `issue_mutation_authority_evidence`", prd_phase)
        self.assertIn("exact target branch named by\n  `delivery_mode_evidence`", prd_template)
        self.assertIn("separate `branch_name` data must equal the exact target", options)
        self.assertIn("- branch_name: [inherited feature branch or exact authorized", issue_template)
        self.assertIn("- branch_name: [same effective branch data as `## Delivery`]", issue_template)
        self.assertIn("every effective\n  direct-commit issue uses", issue_template)
        self.assertIn("scope-transfer-ref=run", issue_template)
        self.assertIn("- issue_mutation_authority: [none | pr-body-closeout-only |", issue_template)
        self.assertIn("`issue_mutation_authority=explicit-direct-mutation`", issue_phase)
        self.assertIn("Direct-commit publication wording alone cannot select", prd_phase)
        self.assertIn("delivery\nauthority alone cannot select it", options)
        self.assertIn("`scope-ref=issue:<NN>`", issue_phase)
        self.assertIn("preserve the PRD `target-ref` verbatim", issue_phase)
        self.assertIn("preserves the PRD owner, `target-ref`, and target branch verbatim", options)
        self.assertIn("`closeout_mode=direct-commit-closes-issue`,\n  `issue_mutation_authority=explicit-direct-mutation`", issue_template)
        self.assertNotIn("`direct-commit` or another explicit authorization", issue_template)
        self.assertNotIn("`direct-commit` or another explicit authorization", issue_phase)
        self.assertIn("label the ref\nnon-executable", issue_phase)
        for identity_field in (
            "feature_slug",
            "product_slug",
            "workspace_path",
            "context_file",
            "project_slug",
        ):
            self.assertIn(f"{identity_field}: <", issue_phase)
        self.assertNotIn("run explicitly requested no-mutation output", prd_phase)
        self.assertNotIn("explicitly asked for a local mirror", prd_phase)
        self.assertIn("## Effective Target Resolution", options)
        self.assertIn("## Per-Issue Registry", options)
        self.assertIn("Records the issue-effective value", options)
        self.assertIn("complete effective delivery", options)
        self.assertIn("## Row Serialization And Fingerprint", options)
        self.assertIn("Record exactly one row per Run Registry field", options)
        self.assertIn("plus issue-effective `branch_name`", options)
        self.assertIn(
            "owner-ref=<ref>;scope-ref=<run-or-issue-scope>;target-ref=<feature-or-source-ref>;target-branch=<branch_name>",
            options,
        )
        self.assertIn("row_id`, `scope_id`, `field`, `value`, `source`, and", options)
        self.assertIn("option_rows_fingerprint=sha256:", options)
        self.assertIn("`issue:<NN>:<field>`", options)
        self.assertIn("`local-artifacts` | `local-dry-run`", options)
        self.assertIn("`closeout_mode=local-done-move-after-proof`", options)
        self.assertIn("`closeout_mode=direct-commit-closes-issue`", options)
        self.assertIn("after the issue graph exists and\nbefore emitting", options)
        self.assertIn("`parallelization=depends-on` requires", options)
        self.assertIn("one or more `dependency_ids`", options)
        self.assertIn("atomically resolves", options)
        self.assertIn("Any non-`none` registry value", options)
        self.assertIn("Reject any other combination", options)
        self.assertIn("tracker-publishing.md", issue_phase)
        self.assertIn("Do not add worker authorization defaults", issue_phase)
        self.assertNotIn(ORCHESTRATION_POLICY_PATH, issue_phase)
        self.assertIn("final hardened issue bodies", issue_phase)
        self.assertIn("`pr_shape`: required", issue_phase)
        self.assertIn("atomically resolve the", issue_phase)
        self.assertIn("complete delivery tuple", issue_phase)
        self.assertIn("- pr_shape: single-pr", issue_phase)
        self.assertIn("`partial_output=allow-non-agent-ready`", issue_phase)
        self.assertNotIn("explicitly requested partial backlog output", issue_phase)
        self.assertNotIn("unless it explicitly permits partial output", issue_phase)
        self.assertNotIn("current run explicitly requested\nno-mutation", issue_phase)
        self.assertNotIn("user explicitly requested one", issue_phase)
        self.assertIn("machine-local absolute paths", issue_phase)
        self.assertIn("planning issue publication", issue_phase)
        self.assertIn("tracker_backend` as planning-artifact write authority", issue_phase)
        self.assertIn("Run The Verticality Gate", issue_phase)
        self.assertIn("re-run `$plan-harder`", issue_phase)
        self.assertNotIn(STALE_REPO_PR_PLACEHOLDERS, issue_phase)
        self.assertIn("references/issue-body-template.md", issue_phase)
        self.assertIn("## Orchestrator Handoff", issue_phase)
        self.assertIn("must not contain worker authorization", issue_phase)
        self.assertNotIn("# <feature-slug>: <NN> <vertical outcome>", issue_phase)
        self.assertIn("# PRD: [Feature Name]", prd_template)
        self.assertIn("## Delivery Mode", prd_template)
        self.assertIn("## Domain Knowledge Handoff", prd_template)
        self.assertIn("# <feature-slug>: <NN> <vertical outcome>", issue_template)
        self.assertIn("Type: [mapped issue type", issue_template)
        self.assertIn("Status: [mapped triage state", issue_template)
        self.assertNotIn("\ntype:", issue_template)
        self.assertNotIn("\nstatus:", issue_template)
        self.assertIn("- pr_shape: [single-pr | per-repo-pr | none]", issue_template)
        self.assertIn(
            "- pr_shape: [same effective value as `## Delivery`]",
            issue_template,
        )
        self.assertIn("## Orchestrator Handoff", issue_template)
        self.assertIn("## Domain Knowledge Closeout", issue_template)
        self.assertIn("Do not include worker authorization modes", issue_template)
        self.assertNotIn(ORCHESTRATION_POLICY_PATH, issue_template)
        self.assertIn("source_prd_ref: [path, issue number, or stable draft ref;", issue_template)
        self.assertIn("draft refs are valid", issue_template)
        self.assertIn("portable references", issue_template)
        self.assertIn("Placeholders are scheduling expectations", issue_template)
        self.assertIn("## Dependency Rules", vertical_slices)
        self.assertIn("## Verticality Gate", vertical_slices)
        self.assertIn("blocking gate", vertical_slices)
        self.assertIn("circular dependencies", vertical_slices)
        self.assertIn("final integration and domain-knowledge closeout task", vertical_slices)
        self.assertIn("orchestrator closeout", vertical_slices)
        self.assertIn("## Orchestrator Handoff", vertical_slices)
        self.assertIn("draft-prd:<...>", prd_delivery)
        self.assertIn("canonical issue-level dispatch contract", prd_delivery)
        self.assertIn("`delivery_source_evidence`", prd_delivery)
        self.assertIn("resolved per workstream", prd_delivery)
        self.assertIn("source lifecycle and closeout mutations are orchestrator-owned", prd_delivery)
        self.assertIn("Repo PR placeholders copied from PRDs", prd_delivery)
        self.assertIn("direct-commit` proves delivery", prd_delivery)
        self.assertIn("issues/done/", prd_delivery)
        self.assertIn("Validation Commands", issue_phase)
        self.assertIn("equivalent fallback", issue_phase)
        self.assertIn("local-done-move-after-proof", issue_phase)
        self.assertIn("Fallback:", issue_template)
        self.assertIn("commit/proof is recorded", issue_template)

    def test_plan_feature_defers_domain_capture_to_final_integration_task(self) -> None:
        plan_feature = read("plan-feature/SKILL.md")
        grill_with_context = read("grill-me-with-context/SKILL.md")
        prd_phase = read("plan-feature/references/prd-phase.md")
        issue_phase = read("plan-feature/references/issue-phase.md")
        issue_template = read("plan-feature/references/issue-body-template.md")
        fixture = read("plan-feature/references/full-flow-dry-run.md")

        self.assertIn("capture_mode: defer-to-caller", plan_feature)
        self.assertIn("domain_knowledge_delta", plan_feature)
        self.assertIn("Initialize every run with a structured", plan_feature)
        self.assertIn("Empty all lists when status is `none`", plan_feature)
        self.assertIn("must not update `CONTEXT.md`", plan_feature)
        self.assertIn("final implementation/integration issue", plan_feature)
        self.assertIn("is never docs-only", plan_feature)
        self.assertIn("preserve it in the PRD handoff", plan_feature)
        self.assertIn("Plan Feature never invokes `domain-memory`", plan_feature)

        self.assertIn("## Capture Modes", grill_with_context)
        self.assertIn("`inline` is the default for direct invocation", grill_with_context)
        self.assertIn("### Mode Resolution", grill_with_context)
        self.assertIn("Direct `$grill-me-with-context` invocation uses `inline`", grill_with_context)
        self.assertIn("Do not infer deferred mode merely because", grill_with_context)
        self.assertIn("preserves the original inline capture behavior", grill_with_context)
        self.assertIn("`defer-to-caller`", grill_with_context)
        self.assertIn("Never write `CONTEXT.md`", grill_with_context)
        self.assertIn("domain_knowledge_delta:", grill_with_context)
        self.assertIn("<repo-slug>/<repo-relative-path>", grill_with_context)
        self.assertIn("The `unresolved` list is independent of capture status", grill_with_context)
        self.assertIn("record remaining product-shaping questions there", grill_with_context)
        self.assertIn("For a direct user request, add a", grill_with_context)

        self.assertIn("## Domain Knowledge Handoff", prd_phase)
        self.assertIn("deferred-work carrier", prd_phase)
        self.assertIn("<repo-slug>/<repo-relative-path>", prd_phase)
        self.assertIn("\n  status: <required|none>", prd_phase)
        self.assertNotIn("\n- status: <required|none>", prd_phase)
        self.assertIn("choose its final owner", issue_phase)
        self.assertIn("append the last generated issue", issue_phase)
        self.assertIn("depend directly\n   on every other terminal issue", issue_phase)
        self.assertIn("Never append a documentation-only task", issue_phase)
        self.assertIn("publish or write it last", issue_phase)
        self.assertIn("Normalize each dependency edge from prerequisite", issue_phase)
        self.assertIn("pre-closeout nodes with no\n  downstream consumers", issue_phase)
        self.assertIn("exclude it from the terminal prerequisites", issue_phase)
        self.assertIn("explicit `$project-memory domain-memory` implementation step", issue_phase)
        self.assertIn("directly is not a substitute", issue_template)
        self.assertIn("internal domain-modeling workflow completion", issue_template)

        self.assertIn("performs no documentation", fixture)
        self.assertIn("last integration task", fixture)
        self.assertIn("placed in a docs-only task", fixture)
        self.assertIn("pre-closeout terminals are `02` and `03`", fixture)
        self.assertIn("do not\n   replace these generated dependency IDs", fixture)
        self.assertIn("does not run that capture during planning", fixture)

    def test_planning_entrypoints_have_unambiguous_output_contracts(self) -> None:
        plan_feature = read("plan-feature/SKILL.md")
        plan_feature_metadata = read("plan-feature/agents/openai.yaml")
        issue_phase = read("plan-feature/references/issue-phase.md")
        plan_harder = read("plan-harder/SKILL.md")
        plan_harder_options = read("plan-harder/references/options.md")
        plan_harder_templates = read("plan-harder/references/templates.md")
        triage = read("triage/SKILL.md")
        triage_agent_brief = read("triage/references/agent-brief.md")

        self.assertIn("default for new feature intent after input normalization", plan_feature)
        self.assertIn("branch only on that canonical value", plan_feature)
        self.assertIn("Select full-flow for new intent", plan_feature_metadata)
        self.assertNotIn("split it into hardened vertical issues when requested", plan_feature_metadata)
        self.assertIn("`partial_output=allow-non-agent-ready` permits", plan_feature)
        self.assertIn("`planning_mode=issue-hardening`", plan_feature)
        self.assertIn("`output_surface=caller`", plan_feature)
        self.assertIn("output_surface=caller", issue_phase)
        self.assertIn("require `result_status`", issue_phase)
        self.assertIn("`result_status: blocked`", issue_phase)
        self.assertNotIn("require `status`, `implementation_plan`", issue_phase)
        self.assertNotIn("`status: blocked`", issue_phase)
        self.assertIn("result_status: ready | blocked", plan_harder_templates)
        self.assertIn("estimated_complexity: <low|medium|high>", plan_harder_templates)
        self.assertIn("`planning_mode` | `full-plan`, `issue-hardening`", plan_harder_options)
        self.assertIn("`result_status` | `ready`, `blocked`", plan_harder_options)
        self.assertNotIn("issue-hardening caller mode", triage)
        self.assertIn("`planning_mode=issue-hardening`", triage)
        self.assertIn("`output_surface=caller`", triage)
        self.assertIn("`planning_mode=issue-hardening`", triage_agent_brief)
        self.assertIn("`output_surface=caller`", triage_agent_brief)
        self.assertIn("Do not auto-select this skill merely because an implementation request", plan_harder)
        self.assertIn(
            "return only the structured issue-hardening result", plan_harder
        )
        self.assertIn("instead of starting a separate user-facing question loop", plan_harder)

    def test_lean_profiles_reduce_discovery_without_skipping_gates(self) -> None:
        plan_feature = read("plan-feature/SKILL.md")
        prd_phase = read("plan-feature/references/prd-phase.md")
        issue_phase = read("plan-feature/references/issue-phase.md")

        self.assertIn("## Execution Profiles", plan_feature)
        self.assertIn("`lean-prd`", plan_feature)
        self.assertIn("`lean-issues`", plan_feature)
        self.assertIn("Lean profiles reduce discovery and repeated output only", plan_feature)
        for required_gate in (
            "`$plan-harder`",
            "verticality",
            "graph",
            "publication",
            "domain-closeout",
        ):
            self.assertIn(required_gate, plan_feature)

        self.assertIn("For `lean-prd`, begin with only", prd_phase)
        self.assertIn("project-memory/agents/domain.md", prd_phase)
        self.assertIn("`CONTEXT-MAP.md` when either exists", prd_phase)
        self.assertIn("Widen to\n`standard`", prd_phase)
        self.assertIn("For `lean-issues`, read the durable PRD once", issue_phase)
        self.assertIn("The lean profile does not weaken any hardening or output gate", issue_phase)
        self.assertIn("at most two candidate vertical", plan_feature)

    def test_planning_uses_delta_evidence_and_exact_optional_metrics(self) -> None:
        plan_feature = read("plan-feature/SKILL.md")
        prd_phase = read("plan-feature/references/prd-phase.md")
        issue_phase = read("plan-feature/references/issue-phase.md")

        self.assertIn("Snapshot each source or artifact in full at most once", plan_feature)
        self.assertIn("Label\n  interleaved cumulative deltas `exact-interval`", plan_feature)
        self.assertIn("Never estimate or make metrics a completion gate", plan_feature)
        self.assertIn("## Evidence And Phase Metrics", prd_phase)
        self.assertIn("phase=prd", prd_phase)
        self.assertIn("completion output should identify the\nPRD and its fingerprint", prd_phase)
        self.assertIn("## Evidence And Phase Metrics", issue_phase)
        self.assertIn("phase=issue-hardening:<issue-id>", issue_phase)
        self.assertIn("Do not repeat unchanged\nPRD or issue bodies", issue_phase)
        self.assertIn("never estimate, reread session\narchives", issue_phase)
        self.assertIn("do not attribute it to an\nissue phase", issue_phase)

    def test_project_memory_triage_and_learn_keep_narrow_authority(self) -> None:
        project_memory = read("project-memory/SKILL.md")
        domain_modeling = read("project-memory/references/domain-modeling.md")
        setup_workflow = read("project-memory/references/setup-workflow.md")
        triage = read("triage/SKILL.md")
        architecture = read("improve-codebase-architecture/SKILL.md")
        learn = read("learn/SKILL.md")

        self.assertIn("Use the smallest requested slice", project_memory)
        self.assertIn("only the requested slice", project_memory)
        self.assertIn("single public entry point", project_memory)
        self.assertIn("`implementation-closeout`", project_memory)
        self.assertIn("`inline-update`", project_memory)
        self.assertIn("explicitly invoked composed workflow", project_memory)
        self.assertIn("durable domain-memory write authority", project_memory)
        self.assertIn("ready implementation-closeout task", project_memory)
        self.assertIn("internal semantic workflow", domain_modeling)
        self.assertIn("`$project-memory domain-memory` is the public invocation", domain_modeling)
        self.assertFalse((SKILLS_ROOT / "domain-modeling/SKILL.md").exists())
        self.assertIn("Ask only when the target or behavior-affecting value is materially", project_memory)
        self.assertIn("proceed without a second confirmation", setup_workflow)
        self.assertIn("## One-Issue Best-Effort Fallback", triage)
        self.assertIn("`capture_mode: inline`", triage)
        self.assertIn("`capture_mode: defer-to-caller`", triage)
        self.assertIn("Tracker mutation\n  authority alone does not authorize", triage)
        self.assertIn("operation:", triage)
        self.assertIn("inline-update", triage)
        self.assertIn("`capture_mode: inline`", architecture)
        self.assertIn("`operation: inline-update`", architecture)
        self.assertIn("do not apply `ready-for-agent`", triage)
        self.assertIn("wait for\n  an affirmative user reply", learn)
        self.assertIn("Never fall back or redirect to global", learn)

    def test_plan_feature_outputs_do_not_define_runtime_policy(self) -> None:
        for relative in (
            "plan-feature/references/prd-template.md",
            "plan-feature/references/issue-body-template.md",
            "plan-feature/references/issue-phase.md",
            "plan-feature/references/vertical-slices.md",
            "plan-feature/references/full-flow-dry-run.md",
        ):
            contents = read(relative)
            with self.subTest(file=relative):
                for field in RUNTIME_POLICY_FIELDS:
                    self.assertNotIn(field, contents)

    def test_worker_authorization_is_orchestrator_owned(self) -> None:
        ledger = read("codex-orchestrator/references/ledger.md")
        worker = read("codex-orchestrator/references/worker.md")
        orchestrator = read("codex-orchestrator/SKILL.md")

        self.assertIn("authorization_resolution: per-workstream", ledger)
        self.assertIn("per workstream and session", worker)
        self.assertIn("The root resolves worker authorization per workstream", orchestrator)
        self.assertIn("worker_authorization:", worker)
        self.assertIn("Worker evidence", ledger)
        self.assertIn("Worker evidence", worker)
        self.assertIn("parallelism=<parallel|sequential|root-owned|simulated>", ledger)
        self.assertIn("fallback reason", orchestrator)

    def test_project_memory_no_longer_defines_worker_auth_defaults(self) -> None:
        for path in iter_active_text_files():
            contents = path.read_text(encoding="utf-8")
            with self.subTest(file=str(path.relative_to(REPO_ROOT))):
                self.assertNotIn(LEGACY_WORKER_AUTH_KEY, contents)
                self.assertNotIn(LEGACY_WORKER_AUTH_HEADING, contents)
                self.assertNotIn(LEGACY_DEFAULT_WORKER_AUTH, contents)

    def test_removed_public_phase_skills_are_not_referenced(self) -> None:
        for path in iter_active_text_files():
            contents = path.read_text(encoding="utf-8")
            with self.subTest(file=str(path.relative_to(REPO_ROOT))):
                self.assertNotIn(REMOVED_PRD_SKILL, contents)
                self.assertNotIn(REMOVED_ISSUE_SKILL, contents)
                self.assertNotIn(REMOVED_PRD_PATH, contents)
                self.assertNotIn(REMOVED_ISSUE_PATH, contents)


if __name__ == "__main__":
    unittest.main()
