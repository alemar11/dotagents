from __future__ import annotations

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
        self.assertIn("source_prd_ref: draft-prd:account-settings-export", fixture)
        self.assertIn("prd_body_fingerprint: sha256:7f4a9c21d003", fixture)
        self.assertIn("capture_mode: defer-to-caller", fixture)
        self.assertIn("domain_knowledge_delta", fixture)
        self.assertIn("status: required", fixture)
        self.assertIn("target_surfaces:", fixture)
        self.assertIn("evidence:", fixture)
        self.assertIn("current-repository/src/account-settings/export.ts", fixture)
        self.assertIn("## Domain Knowledge Handoff", fixture)
        self.assertIn("## Domain Knowledge Closeout", fixture)
        self.assertIn("last integration task", fixture)
        self.assertIn("$project-memory domain-memory", fixture)
        self.assertIn("loads `$domain-modeling`", fixture)
        self.assertIn("Replace every issue body line", fixture)
        self.assertIn("must not dispatch implementation workers", fixture)
        self.assertNotIn(LEGACY_WORKER_AUTH_KEY, fixture)
        self.assertIn("project memory, plan-feature output, tracker defaults", fixture)
        self.assertIn("authorization fields or worker capability modes", fixture)

    def test_shared_contract_documents_draft_publish_handoff(self) -> None:
        contract = read("project-memory/references/tracker-publishing.md")

        self.assertIn("source_prd_ref", contract)
        self.assertIn("draft-prd:<feature-slug>", contract)
        self.assertIn("Create or update the PRD first", contract)
        self.assertIn("Replace `Source PRD: draft-prd:<...>`", contract)
        self.assertIn("Do not dispatch implementation workers", contract)

    def test_project_memory_does_not_own_orchestration_policy_setup(self) -> None:
        project_memory = read("project-memory/SKILL.md")
        setup_workflow = read("project-memory/references/setup-workflow.md")
        orchestrator = read("codex-orchestrator/SKILL.md")
        worker = read("codex-orchestrator/references/worker.md")
        ledger = read("codex-orchestrator/references/ledger.md")

        self.assertNotIn(ORCHESTRATION_POLICY_PATH, project_memory)
        self.assertNotIn("orchestration-policy", setup_workflow)
        self.assertIn("typed configuration tables", project_memory)
        self.assertNotIn(ORCHESTRATION_POLICY_PATH, orchestrator)
        self.assertIn("delegation\nconsent", worker)
        self.assertNotIn("policy-auto-dispatched", worker)
        self.assertNotIn("policy-auto-dispatched", ledger)
        self.assertIn("Session CLI subagents consented", ledger)
        self.assertIn("Session Codex App threads consented", ledger)
        self.assertIn("## Wave Reports", ledger)
        self.assertIn("Execution Report", ledger)
        self.assertNotIn("## Wave Checkpoints", ledger)

    def test_issue_tracker_templates_stay_tracker_focused(self) -> None:
        for relative in (
            "project-memory/references/issue-tracker-github.md",
            "project-memory/references/issue-tracker-local.md",
        ):
            contents = read(relative)
            with self.subTest(file=relative):
                self.assertIn("## Configuration", contents)
                self.assertIn("| Key | Type | Value | Allowed values | Meaning |", contents)
                self.assertNotIn(ORCHESTRATION_POLICY_PATH, contents)
                self.assertIn("Tracker setup records artifact routing", contents)
                for field in RUNTIME_POLICY_FIELDS:
                    self.assertNotIn(field, contents)

    def test_plan_feature_references_internal_phase_templates(self) -> None:
        plan_feature = read("plan-feature/SKILL.md")
        prd_phase = read("plan-feature/references/prd-phase.md")
        issue_phase = read("plan-feature/references/issue-phase.md")
        prd_template = read("plan-feature/references/prd-template.md")
        issue_template = read("plan-feature/references/issue-body-template.md")
        vertical_slices = read("plan-feature/references/vertical-slices.md")
        prd_delivery = read("codex-orchestrator/references/prd-backed-delivery.md")

        self.assertIn("references/full-flow-dry-run.md", plan_feature)
        self.assertIn("Do not include worker authorization defaults", plan_feature)
        self.assertNotIn(ORCHESTRATION_POLICY_PATH, plan_feature)
        self.assertIn("tracker_backend` as planning-artifact write authority", plan_feature)
        self.assertIn("planning blockers", plan_feature)
        self.assertIn("Every completion report, including `prd-only`", plan_feature)
        self.assertNotIn("Domain knowledge: captured in <path or durable surface>", plan_feature)
        self.assertIn("Domain knowledge: deferred to <final task ref>", plan_feature)
        self.assertIn("Domain knowledge: no durable change", plan_feature)
        self.assertIn("In `prd-only` when `domain_knowledge_delta.status` is `required`", plan_feature)
        self.assertIn("including `prd-only` runs whose delta remains", plan_feature)
        self.assertIn("does not by itself count as", plan_feature)
        self.assertIn("issue lifecycle comments, labels, direct closure", plan_feature)
        self.assertNotIn(STALE_NO_GATES_REMAIN, plan_feature)
        self.assertNotIn(STALE_GATES_RESOLVED, plan_feature)
        self.assertIn("references/prd-phase.md", plan_feature)
        self.assertIn("references/issue-phase.md", plan_feature)
        self.assertIn("tracker-publishing.md", prd_phase)
        self.assertIn("## PRD Target Model", prd_phase)
        self.assertIn("PRD body fingerprint", prd_phase)
        self.assertIn("PRD planning-artifact publication", prd_phase)
        self.assertIn("tracker_backend` is the planning-artifact write authority", prd_phase)
        self.assertIn("tracker-publishing.md", issue_phase)
        self.assertIn("Do not add worker authorization defaults", issue_phase)
        self.assertNotIn(ORCHESTRATION_POLICY_PATH, issue_phase)
        self.assertIn("final hardened issue bodies", issue_phase)
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
        self.assertIn("## Orchestrator Handoff", issue_template)
        self.assertIn("## Domain Knowledge Closeout", issue_template)
        self.assertIn("Do not include worker authorization modes", issue_template)
        self.assertNotIn(ORCHESTRATION_POLICY_PATH, issue_template)
        self.assertIn("Source PRD: [path, issue number, or stable draft ref;", issue_template)
        self.assertIn("never for agent-ready", issue_template)
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
        self.assertIn("Initialize every run with a canonical", plan_feature)
        self.assertIn("`status: none` and empty `decisions`", plan_feature)
        self.assertIn("all lists empty", plan_feature)
        self.assertIn("not edit `CONTEXT.md`", plan_feature)
        self.assertIn("final integration and domain-knowledge closeout task", plan_feature)
        self.assertIn("docs-only horizontal ticket", plan_feature)
        self.assertIn("In issue-generating modes", plan_feature)
        self.assertIn("In `prd-only`,\n  preserve a required delta", plan_feature)
        self.assertIn("Plan Feature does not call `$project-memory domain-memory`", plan_feature)

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
        self.assertIn("    status: <required|none>", prd_phase)
        self.assertNotIn("  - status: <required|none>", prd_phase)
        self.assertIn("choose its final owner", issue_phase)
        self.assertIn("append the last generated issue", issue_phase)
        self.assertIn("depend directly\n   on every other terminal issue", issue_phase)
        self.assertIn("Never append a documentation-only task", issue_phase)
        self.assertIn("publish or write it last", issue_phase)
        self.assertIn("Normalize each dependency edge from prerequisite", issue_phase)
        self.assertIn("pre-closeout nodes with no\n  downstream consumers", issue_phase)
        self.assertIn("exclude it from the terminal prerequisites", issue_phase)
        self.assertIn("explicit `$project-memory domain-memory` implementation step", issue_phase)
        self.assertIn("editing the targets directly is not a", issue_template)
        self.assertIn("`$domain-modeling` usage", issue_template)

        self.assertIn("performs no documentation", fixture)
        self.assertIn("last integration task", fixture)
        self.assertIn("placed in a docs-only task", fixture)
        self.assertIn("pre-closeout terminals are `02` and `03`", fixture)
        self.assertIn("do not\n   replace these generated dependency IDs", fixture)
        self.assertIn("Plan Feature does not run that capture", fixture)

    def test_planning_entrypoints_have_unambiguous_output_contracts(self) -> None:
        plan_feature = read("plan-feature/SKILL.md")
        plan_feature_metadata = read("plan-feature/agents/openai.yaml")
        issue_phase = read("plan-feature/references/issue-phase.md")
        plan_harder = read("plan-harder/SKILL.md")
        plan_harder_templates = read("plan-harder/references/templates.md")

        self.assertIn("use `full-flow`; issue splitting is part of that default", plan_feature)
        self.assertIn("in full-flow mode by default", plan_feature_metadata)
        self.assertNotIn("split it into hardened vertical issues when requested", plan_feature_metadata)
        self.assertIn("partial non-agent-ready output is the only exception", plan_feature)
        self.assertIn("caller surface", issue_phase)
        self.assertIn("status: ready | blocked", plan_harder_templates)
        self.assertIn("Do not auto-select this skill merely because an implementation request", plan_harder)
        self.assertIn(
            "return only the structured issue-hardening result", plan_harder
        )
        self.assertIn("instead of starting a separate user-facing question loop", plan_harder)

    def test_project_memory_triage_and_learn_keep_narrow_authority(self) -> None:
        project_memory = read("project-memory/SKILL.md")
        domain_modeling = read("domain-modeling/SKILL.md")
        setup_workflow = read("project-memory/references/setup-workflow.md")
        triage = read("triage/SKILL.md")
        learn = read("learn/SKILL.md")

        self.assertIn("Select the smallest slice needed", project_memory)
        self.assertIn("write authority for the requested slice", project_memory)
        self.assertIn("normal public invocation for durable memory changes", project_memory)
        self.assertIn("`implementation-closeout`", project_memory)
        self.assertIn("ready-for-execution implementation task", project_memory)
        self.assertIn("semantic engine for domain documentation", domain_modeling)
        self.assertIn("`$project-memory domain-memory` is the normal public", domain_modeling)
        self.assertIn("Ask only when the target or a behavior-affecting value is materially", project_memory)
        self.assertIn("proceed without a second confirmation", setup_workflow)
        self.assertIn("## One-Issue Best-Effort Fallback", triage)
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

        self.assertIn("Authorization resolution: per-workstream", ledger)
        self.assertIn("per workstream and session", worker)
        self.assertIn("Worker authorization is resolved only by the root orchestrator", orchestrator)
        self.assertIn("Authorization modes:", worker)
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
