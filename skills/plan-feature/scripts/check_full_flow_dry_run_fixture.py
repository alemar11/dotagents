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
ORCHESTRATION_POLICY_PATH = "project-memory/agents/orchestration-policy.md"
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
        self.assertIn("external_tracker_mutation: disallowed", fixture)
        self.assertIn("source_prd_ref: draft-prd:account-settings-export", fixture)
        self.assertIn("prd_body_fingerprint: sha256:7f4a9c21d003", fixture)
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

    def test_project_memory_owns_orchestration_policy_setup(self) -> None:
        project_memory = read("project-memory/SKILL.md")
        setup_workflow = read("project-memory/references/setup-workflow.md")
        policy = read("project-memory/references/orchestration-policy.md")
        orchestrator = read("codex-orchestrator/SKILL.md")
        worker = read("codex-orchestrator/references/worker.md")
        ledger = read("codex-orchestrator/references/ledger.md")

        self.assertIn(ORCHESTRATION_POLICY_PATH, project_memory)
        self.assertIn("orchestration-policy", setup_workflow)
        self.assertIn(AUTO_DISPATCH_KEY + ": `false`", policy)
        self.assertIn(WORKER_SURFACES_KEY, policy)
        self.assertIn(AUTHORIZATION_CEILING_KEY, policy)
        self.assertIn("optional runtime configuration", policy)
        self.assertIn(ORCHESTRATION_POLICY_PATH, orchestrator)
        self.assertIn("policy-auto-dispatched", worker)
        self.assertIn("policy-auto-dispatched", ledger)
        self.assertIn("owner-approved", ledger)

    def test_issue_tracker_templates_stay_tracker_focused(self) -> None:
        for relative in (
            "project-memory/references/issue-tracker-github.md",
            "project-memory/references/issue-tracker-local.md",
            "project-memory/references/issue-tracker-orchestrator-github.md",
            "project-memory/references/issue-tracker-orchestrator-local.md",
        ):
            contents = read(relative)
            with self.subTest(file=relative):
                self.assertIn(ORCHESTRATION_POLICY_PATH, contents)
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
        self.assertIn(ORCHESTRATION_POLICY_PATH, plan_feature)
        self.assertIn("planning blockers", plan_feature)
        self.assertIn("issue lifecycle comments, labels, direct closure", plan_feature)
        self.assertNotIn(STALE_NO_GATES_REMAIN, plan_feature)
        self.assertNotIn(STALE_GATES_RESOLVED, plan_feature)
        self.assertIn("references/prd-phase.md", plan_feature)
        self.assertIn("references/issue-phase.md", plan_feature)
        self.assertIn("tracker-publishing.md", prd_phase)
        self.assertIn("PRD body fingerprint", prd_phase)
        self.assertIn("PRD planning-artifact publication", prd_phase)
        self.assertIn("tracker-publishing.md", issue_phase)
        self.assertIn("Do not add worker authorization defaults", issue_phase)
        self.assertIn(ORCHESTRATION_POLICY_PATH, issue_phase)
        self.assertIn("final hardened issue bodies", issue_phase)
        self.assertIn("machine-local absolute paths", issue_phase)
        self.assertIn("generated planning issue publication", issue_phase)
        self.assertNotIn(STALE_REPO_PR_PLACEHOLDERS, issue_phase)
        self.assertIn("references/issue-body-template.md", issue_phase)
        self.assertIn("## Orchestrator Handoff", issue_phase)
        self.assertIn("must not contain worker authorization", issue_phase)
        self.assertNotIn("# <feature-slug>: <NN> <vertical outcome>", issue_phase)
        self.assertIn("# PRD: [Feature Name]", prd_template)
        self.assertIn("## Delivery Mode", prd_template)
        self.assertIn("# <feature-slug>: <NN> <vertical outcome>", issue_template)
        self.assertIn("## Orchestrator Handoff", issue_template)
        self.assertIn("Do not include worker authorization modes", issue_template)
        self.assertIn(ORCHESTRATION_POLICY_PATH, issue_template)
        self.assertIn("Source PRD: [path, issue number, or stable draft ref;", issue_template)
        self.assertIn("never for agent-ready", issue_template)
        self.assertIn("portable references", issue_template)
        self.assertIn("Placeholders are scheduling expectations", issue_template)
        self.assertIn("## Dependency Rules", vertical_slices)
        self.assertIn("circular dependencies", vertical_slices)
        self.assertIn("orchestrator closeout", vertical_slices)
        self.assertIn("## Orchestrator Handoff", vertical_slices)
        self.assertIn("draft-prd:<...>", prd_delivery)
        self.assertIn("canonical issue-level dispatch contract", prd_delivery)
        self.assertIn("resolved per workstream", prd_delivery)
        self.assertIn("source lifecycle and closeout mutations are orchestrator-owned", prd_delivery)
        self.assertIn("Repo PR placeholders copied from PRDs", prd_delivery)

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
        self.assertIn("Ignore the legacy project-memory worker-authorization", orchestrator)
        self.assertIn("Authorization modes:", worker)

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
