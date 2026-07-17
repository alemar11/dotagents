from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def run_app_preclaim_fixture(
    *,
    surface_available: bool,
    permission: str,
    bundle_ready: bool,
    goal_surface_available: bool = True,
) -> tuple[str, list[str], list[str]]:
    observations = ["surface"]
    mutations: list[str] = []
    if not surface_available or not goal_surface_available:
        return "unsupported-runtime", observations, mutations
    observations.append("authorization")
    if permission != "granted-by-authorized-user":
        return "permission-denied", observations, mutations
    observations.append("intake")
    if not bundle_ready:
        return "planning-required", observations, mutations
    mutations.extend(
        ["atomic-claim", "cache-retention", "ledger-projection", "portfolio-goal"]
    )
    return "accepted", observations, mutations


class ImplementFeatureContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text()

    def runtime_paths(self) -> list[Path]:
        files = [ROOT / "SKILL.md", ROOT / "agents/openai.yaml"]
        files.extend(sorted((ROOT / "references").rglob("*.md")))
        return files

    def runtime_text(self) -> str:
        return "\n".join(path.read_text() for path in self.runtime_paths())

    def test_required_package_files_and_removed_stack_reference(self) -> None:
        required = {
            "SKILL.md",
            "agents/openai.yaml",
            "scripts/active-root-claim",
            "scripts/ledger-cache",
            "references/options.md",
            "references/task-model-policy.md",
            "references/cache-lifecycle.md",
            "references/ledger.md",
            "references/ledger-template.md",
            "references/worker.md",
            "references/gates.md",
            "references/spec-backed-delivery.md",
            "references/codex-review-closeout.md",
            "references/recovery-validation.md",
            "references/multi-repo-workspace.md",
        }
        self.assertTrue(all((ROOT / path).is_file() for path in required))
        self.assertFalse((ROOT / "references/stacked-feature-specs.md").exists())

    def test_runtime_surface_gate_precedes_authorization_and_intake(self) -> None:
        skill = self.read("SKILL.md")
        surface = skill.index("## Mandatory Runtime Surface Gate")
        authorization = skill.index("## Mandatory Run Authorization")
        intake = skill.index("## Execution-Ready Intake")
        controller = skill.index("## Controller Loop")

        self.assertLess(surface, authorization)
        self.assertLess(authorization, intake)
        self.assertLess(intake, controller)
        surface_text = " ".join(skill[surface:authorization].split())
        self.assertIn("This is the first runtime step", surface_text)
        self.assertIn("visible ChatGPT desktop app task creation", surface_text)
        self.assertIn("App-managed worktree binding", surface_text)
        self.assertIn("without asking permission", surface_text)
        self.assertIn("0. **SURFACE**", skill[controller:])
        self.assertLess(skill.index("0. **SURFACE**"), skill.index("1. **AUTHORIZE**"))

        recovery = " ".join(
            self.read("references/recovery-validation.md").split()
        )
        self.assertIn("Before reading the packet", recovery)
        self.assertIn("visible ChatGPT desktop app task creation", recovery)
        self.assertIn("App-managed worktree binding", recovery)
        self.assertIn("without asking permission", recovery)

    def test_option_registry_contains_only_two_run_permissions(self) -> None:
        options = self.read("references/options.md")
        fields = re.findall(r"^\| `([a-z][a-z0-9_]*)` \|", options, re.MULTILINE)
        self.assertEqual(
            fields,
            ["visible_app_task_permission", "stale_claim_takeover_permission"],
        )
        for field in fields:
            row = next(line for line in options.splitlines() if line.startswith(f"| `{field}`"))
            for value in (
                "not-requested",
                "granted-by-authorized-user",
                "denied-by-authorized-user",
            ):
                self.assertIn(value, row)
        self.assertIn("This file owns every user-controlled App orchestration field", options)

    def test_visible_task_model_policy_is_canonical_bounded_and_recoverable(self) -> None:
        skill = self.read("SKILL.md")
        policy = self.read("references/task-model-policy.md")
        options = self.read("references/options.md")
        worker = self.read("references/worker.md")
        ledger = self.read("references/ledger.md")
        template = self.read("references/ledger-template.md")
        recovery = self.read("references/recovery-validation.md")

        def values(field: str) -> list[str]:
            row = next(
                line
                for line in policy.splitlines()
                if line.startswith(f"| `{field}` |")
            )
            return re.findall(r"`([^`]+)`", row)[1:]

        self.assertEqual(values("model"), ["gpt-5.6-sol"])
        self.assertEqual(values("thinking_default"), ["high"])
        self.assertEqual(
            values("thinking_allowed"), ["medium", "high", "xhigh"]
        )
        for excluded in ("none", "minimal", "low", "max", "ultra"):
            self.assertIn(f"`{excluded}`", policy)
        self.assertIn("Never pass", policy)

        authorization = " ".join(
            skill.split("## Mandatory Run Authorization", 1)[1]
            .split("## Fixed Implementation Contract", 1)[0]
            .split()
        )
        self.assertIn("references/task-model-policy.md", authorization)
        self.assertIn("exact visible-task model", authorization)
        self.assertIn("bounded adaptive thinking policy", authorization)
        self.assertIn("not another user-controlled field", options)

        for text in (policy, worker):
            self.assertIn("codex_app__create_thread", text)
            self.assertIn("codex_app__send_message_to_thread", text)
        self.assertIn("Never omit", policy)
        self.assertIn("never reclassify", policy)
        self.assertIn("`planning-required`", policy)

        for text in (ledger, template):
            for field in ("task_model", "task_thinking", "thinking_reason"):
                self.assertIn(field, text)
        self.assertIn("recorded per-Spec task profile", recovery)
        self.assertIn("Use the recorded profile", recovery)

    def test_visible_task_title_is_required_semantic_and_recoverable(self) -> None:
        skill = self.read("SKILL.md")
        worker = self.read("references/worker.md")
        ledger = self.read("references/ledger.md")
        template = self.read("references/ledger-template.md")
        recovery = self.read("references/recovery-validation.md")
        options = self.read("references/options.md")
        claim_helper = self.read("scripts/active-root-claim")
        compact_ledger = " ".join(ledger.split())

        surface = " ".join(
            skill.split("## Mandatory Runtime Surface Gate", 1)[1]
            .split("## Mandatory Run Authorization", 1)[0]
            .split()
        )
        for token in (
            "codex_app__set_thread_title",
            "live task-title observation",
            "`create_goal`",
            "`get_goal`",
            "`update_goal`",
            "Before asking permission",
            "unsupported-runtime",
        ):
            self.assertIn(token, surface)

        title_contract = worker.split("## Task Display Title", 1)[1].split(
            "## Fixed Actions", 1
        )[0]
        compact_title_contract = " ".join(title_contract.split())
        for token in (
            "semantically relevant emoji",
            "dominant user-facing goal",
            "`🛠️`",
            "<emoji> <exact authored Feature Spec title>",
            "one emoji grapheme followed by one space",
            "not a user option",
            "clientThreadId",
            "threadId",
            "codex_app__set_thread_title",
            "never create another task",
        ):
            self.assertIn(token, title_contract)
        self.assertLess(
            compact_title_contract.index("Resolve and persist `task_title`"),
            compact_title_contract.index("codex_app__create_thread"),
        )
        self.assertLess(
            compact_title_contract.index("codex_app__create_thread"),
            compact_title_contract.index("codex_app__set_thread_title"),
        )
        self.assertLess(
            compact_title_contract.index("codex_app__set_thread_title"),
            compact_title_contract.index("observe the exact live title"),
        )

        for text in (ledger, template):
            self.assertIn("task_title", text)
        self.assertIn("Missing `task_title` alone", compact_ledger)
        self.assertIn("derived UI evidence, not ownership evidence", recovery)
        self.assertIn("Record task-title drift without mutating it", recovery)
        self.assertIn("Only after the complete freshness pass", recovery)
        self.assertIn("never accept an arbitrary emoji", recovery)
        self.assertIn("same task", recovery)
        self.assertNotIn("task_title", options)
        self.assertNotIn('"task_title"', claim_helper)

    def test_one_consent_covers_the_complete_fixed_flow(self) -> None:
        skill = " ".join(self.read("SKILL.md").split())
        options = " ".join(self.read("references/options.md").split())
        for token in (
            "inspect",
            "edit",
            "validate",
            "commit",
            "push",
            "publish or update pull requests",
            "current-revision Codex review",
            "fix findings",
            "wait for CI",
            "prepare tracker closeout",
            "move completed local Markdown issue files",
            "convert draft pull requests to ready-for-review",
        ):
            self.assertIn(token, skill)
        self.assertIn(
            "visible_app_task_permission=granted-by-authorized-user", skill
        )
        self.assertIn("fixed execution flow", options)
        self.assertIn("Generic delegation or subagent authority never supplies this grant", skill)

    def test_cache_maintenance_is_root_owned_bounded_and_after_claim(self) -> None:
        skill = self.read("SKILL.md")
        lifecycle = self.read("references/cache-lifecycle.md")
        normalized_lifecycle = " ".join(lifecycle.split())
        ledger = self.read("references/ledger.md")
        normalized_ledger = " ".join(ledger.split())
        controller = skill.split("## Controller Loop", 1)[1]

        authorization = " ".join(
            skill.split("## Mandatory Run Authorization", 1)[1]
            .split("## Fixed Implementation Contract", 1)[0]
            .split()
        )
        self.assertIn(
            "automatic deletion of valid archived ledgers older than 180 days after CLAIM",
            authorization,
        )
        self.assertLess(controller.index("3. **CLAIM**"), controller.index("4. **CACHE-MAINTENANCE**"))
        self.assertLess(controller.index("4. **CACHE-MAINTENANCE**"), controller.index("5. **REGISTER**"))
        self.assertLess(controller.index("5. **REGISTER**"), controller.index("7. **DISPATCH**"))

        for command in (
            "scripts/ledger-cache --json doctor",
            "scripts/ledger-cache --json archive prune --older-than-days 180 --apply",
        ):
            self.assertIn(command, lifecycle)
        self.assertIn("The root owns cache maintenance", lifecycle)
        self.assertIn("Never create a visible task, internal subagent", lifecycle)
        self.assertIn("Run once per controller entry", lifecycle)
        self.assertIn("strict 180-day TTL", lifecycle)
        self.assertIn("there is no last-N exception", lifecycle)
        self.assertIn("warning is nonblocking", normalized_lifecycle)
        self.assertIn("Archive only after terminal reconciliation and exact claim release", lifecycle)
        self.assertIn("Monitoring handoffs", normalized_lifecycle)
        self.assertIn("claim release --release-reason terminal", lifecycle)
        self.assertIn("claim release --release-reason durable-handoff", lifecycle)
        self.assertIn("durable receipt binds", normalized_lifecycle)
        self.assertIn("A durable-handoff receipt never authorizes archival", lifecycle)
        self.assertIn("Archived ledgers live below `ledgers/archive/` as cold evidence", normalized_ledger)
        self.assertIn("After terminal release only", normalized_ledger)

    def test_fixed_worker_actions_are_not_an_option(self) -> None:
        worker = self.read("references/worker.md")
        options = self.read("references/options.md")
        self.assertIn("## Fixed Actions", worker)
        for action in (
            "inspect",
            "edit",
            "validate",
            "commit",
            "push",
            "complete-domain-closeout",
            "publish-or-update-pull-request",
            "run-autoreview",
            "mark-ready-for-review",
            "request-review",
            "poll-review",
            "fix-review",
            "run-ci",
            "prepare-tracker-closeout",
            "move-local-issues-to-done",
            "check-mergeability",
            "report",
        ):
            self.assertIn(action, worker)
        self.assertNotIn("worker_allowed_actions", worker)
        self.assertNotIn("worker_allowed_actions", options)

    def test_review_fixes_use_target_repo_fixup_policy_without_autosquash(self) -> None:
        worker = " ".join(self.read("references/worker.md").split())

        self.assertIn("use `$gitstack:git-commit`", worker)
        self.assertIn("keep `commit_kind=regular`", worker)
        self.assertIn("target-repository instructions require a targeted fixup", worker)
        self.assertIn("feedback alone never selects a fixup", worker)
        self.assertIn("one exact `target_commit`", worker)
        self.assertIn("Never autosquash or rewrite the published branch", worker)
        self.assertIn("invalidates current-revision review and CI evidence", worker)

    def test_app_has_one_fixed_successful_conclusion_and_never_merges(self) -> None:
        runtime = self.runtime_text()
        skill = " ".join(self.read("SKILL.md").split())
        fixed = "pull-request-ready-for-merge-but-not-merged"
        for relative in (
            "SKILL.md",
            "references/options.md",
            "references/worker.md",
            "agents/openai.yaml",
        ):
            self.assertIn(fixed, self.read(relative))
        self.assertIn("only successful App result", skill)
        self.assertIn("This skill never merges a pull request", skill)
        self.assertIn("A later merge request must start a separate GitHub workflow", skill)
        self.assertNotIn("pull_request_merge_permission", runtime)
        self.assertNotIn("pull_request_merge_confirmation", runtime)

    def test_intake_uses_one_execution_contract_and_root_fingerprints(self) -> None:
        delivery = self.read("references/spec-backed-delivery.md")
        skill = " ".join(self.read("SKILL.md").split())
        self.assertIn("exactly one `## Execution Contract`", delivery)
        fields = re.findall(r"^\| `([a-z][a-z0-9_]*)` \|", delivery, re.MULTILINE)
        self.assertEqual(
            fields,
            [
                "source_spec_ref",
                "feature_slug",
                "affected_repositories",
                "allowed_paths",
                "target_branch_name",
                "dependency_ids",
            ],
        )
        self.assertIn("computes its own fingerprints", " ".join(delivery.split()))
        self.assertIn("Earlier generated issue ids within this Feature Spec", delivery)
        self.assertIn("`## Feature Dependencies` table", delivery)
        self.assertIn("`upstream_feature_spec_ref`", delivery)
        self.assertIn("`dependency_reason`", delivery)
        self.assertIn("`proposed-spec:<...>` refs", delivery)
        self.assertIn("one read-only intake", skill)
        self.assertIn("planning-required", skill)
        self.assertIn("unsupported-app-delivery-target", skill)
        self.assertIn("no claim, ledger, Goal, task, tracker write, or source mutation", skill)
        self.assertNotIn("$plan-feature", self.runtime_text())
        self.assertIn("mandatory `## Feature Dependencies` table", delivery)
        self.assertIn("Never interpret absence as an empty edge set", delivery)
        self.assertNotIn("legacy Feature Spec", delivery)

    def test_plan_feature_execution_contract_matches_app_consumer(self) -> None:
        producer = (
            REPO / "skills/plan-feature/references/issue-body-template.md"
        ).read_text()
        base_contract = producer.split("## Execution Contract", 1)[1].split(
            "## Goal", 1
        )[0]
        producer_fields = re.findall(
            r"^\| `([a-z][a-z0-9_]*)` \|", base_contract, re.MULTILINE
        )
        consumer_fields = re.findall(
            r"^\| `([a-z][a-z0-9_]*)` \|",
            self.read("references/spec-backed-delivery.md"),
            re.MULTILINE,
        )
        self.assertEqual(producer_fields, consumer_fields)
        self.assertEqual(len(consumer_fields), 6)
        self.assertNotIn("non_app_delivery_target", base_contract)

    def test_retired_structured_fields_are_a_hard_cut(self) -> None:
        runtime = self.runtime_text()
        for field in (
            "existing_orchestrator_session_takeover_policy",
            "change_delivery_permission",
            "codex_review_requirement",
            "delivery_decision_origin",
            "issue_repository_layout",
            "pull_request_count_strategy",
            "issue_completion_method",
            "domain_closeout",
            "starting_checkout_branch_handling",
            "worker_allowed_actions",
            "execution_adapter",
            "lifecycle_owner",
        ):
            self.assertNotIn(field, runtime, field)

    def test_scheduling_is_deterministic_path_disjoint_and_merge_gated(self) -> None:
        skill = " ".join(self.read("SKILL.md").split())
        self.assertIn("Sort ready candidates by canonical claim/task source id ascending", skill)
        self.assertIn("`## Feature Dependencies` table", skill)
        self.assertIn("Greedily select", skill)
        self.assertIn("remaining three-task capacity", skill)
        self.assertIn("pairwise disjoint", skill)
        self.assertIn("ancestor/descendant path scopes as overlapping", skill)
        self.assertIn(
            "every upstream ref in its parent `## Feature Dependencies` table is merged",
            skill,
        )
        self.assertIn("merge-ready but unmerged upstream does not make a downstream ready", skill)
        for token in (
            "upstream-merge-ready-head",
            "intermediate-upstream-merge-handoff",
            "pre-promotion",
            "awaiting-upstream-merge",
            "resyncing",
        ):
            self.assertNotIn(token, self.runtime_text())

    def test_app_surface_is_one_managed_task_per_spec(self) -> None:
        runtime = self.runtime_text()
        normalized = runtime.lower()
        self.assertIn("exactly one visible app task", normalized)
        self.assertIn("app-managed worktrees", normalized)
        self.assertIn("assignment-scoped goal", normalized)
        self.assertIn("at most three nonterminal", normalized)
        for token in (
            "tmux",
            "codex exec",
            "git worktree add",
            "git worktree remove",
            "serial-caller-checkout",
            "unmanaged_git_worktree_fallback_permission",
            "implementation_checkout_strategy",
            "current-orchestrator-session",
            "background-codex-subagent",
        ):
            self.assertNotIn(token, normalized)

        recovery = " ".join(
            self.read("references/recovery-validation.md").split()
        )
        worker = " ".join(self.read("references/worker.md").split())
        self.assertIn("Resume only the original visible task", recovery)
        self.assertIn("never create a replacement", recovery)
        self.assertIn("resumed in the same visible task", worker)
        self.assertNotIn("resumed or replaced", normalized)
        self.assertNotIn("`replaced`", self.read("references/worker.md"))

    def test_goal_tools_are_mandatory_without_objective_fallback(self) -> None:
        skill = self.read("SKILL.md")
        worker = self.read("references/worker.md")
        ledger = self.read("references/ledger.md")
        template = self.read("references/ledger-template.md")
        recovery = self.read("references/recovery-validation.md")
        normalized_recovery = " ".join(recovery.split())

        for text in (skill, worker, ledger, recovery):
            for tool in ("`create_goal`", "`get_goal`", "`update_goal`"):
                self.assertIn(tool, text)

        self.assertIn("Never set", skill)
        self.assertIn("Do not pass", worker)
        self.assertIn("`token_budget`", skill)
        self.assertIn("`token_budget`", worker)
        self.assertIn("exact Feature Spec", worker)
        self.assertIn("repositories and allowed paths", worker)
        self.assertIn("acceptance criteria", worker)
        self.assertIn("validation", worker)
        self.assertIn("pull-request-ready-for-merge-but-not-merged", worker)
        self.assertIn("Objective fingerprint", template)
        self.assertIn("portfolio_goal_state", template)
        self.assertIn("portfolio_goal_evidence_ref", template)
        self.assertIn('goal_evidence_ref: "none"', recovery)
        self.assertIn("read only the packet and ledger fields", normalized_recovery)
        self.assertIn(
            "Before any mutation, read each exact task", normalized_recovery
        )
        self.assertIn("portfolio_goal_state=pending", recovery)
        self.assertIn("portfolio_goal_state=complete", recovery)
        self.assertIn("Do not persist adoption or call `create_goal`", normalized_recovery)
        self.assertIn("Only after the complete freshness pass", normalized_recovery)
        self.assertIn("complete `pending` Goal registration", normalized_recovery)
        self.assertIn("never repair or resume implementation", normalized_recovery)
        self.assertIn("idempotently release it", normalized_recovery)
        self.assertIn("if it is not already archived", normalized_recovery)
        self.assertIn("active matching Goal evidence", normalized_recovery)
        self.assertIn("completed matching Goal evidence", normalized_recovery)
        self.assertIn("interrupted completion transition", normalized_recovery)
        self.assertIn("terminal-closeout recovery mutations", normalized_recovery)
        self.assertIn("persist the matching completion evidence", normalized_recovery)
        normalized_worker = " ".join(worker.split())
        self.assertIn("already recorded at the fixed terminal result", normalized_worker)
        self.assertIn("must not resume implementation", normalized_worker)
        self.assertIn("finish that transition only", normalized_worker)

        surface = " ".join(
            skill.split("## Mandatory Runtime Surface Gate", 1)[1]
            .split("## Mandatory Run Authorization", 1)[0]
            .split()
        )
        self.assertIn("general visible-task Goal-tool support", surface)
        self.assertIn("does not create a task to inspect task-local tools", surface)
        dispatch = " ".join(
            skill.split("7. **DISPATCH**", 1)[1].split("8. **MONITOR**", 1)[0].split()
        )
        self.assertIn("verify that exact task's Goal tools", dispatch)
        self.assertIn("before advancing beyond `created`", dispatch)

        register = " ".join(
            skill.split("5. **REGISTER**", 1)[1].split("6. **PR-PREFLIGHT**", 1)[0].split()
        )
        self.assertLess(
            register.index("portfolio_goal_state=pending"),
            register.index("otherwise call `create_goal`"),
        )

        delivery = " ".join(skill.split("## Delivery And Final Report", 1)[1].split())
        self.assertLess(
            delivery.index("`update_goal`"),
            delivery.index("portfolio_goal_state=complete"),
        )
        self.assertLess(
            delivery.index("portfolio_goal_state=complete"),
            delivery.index("`--release-reason terminal`"),
        )
        self.assertLess(
            delivery.index("`--release-reason terminal`"),
            delivery.index("`scripts/ledger-cache`"),
        )

        runtime = self.runtime_text()
        for retired in (
            "create the portfolio Goal or exact fallback",
            "Record an exact objective fallback only if",
            "or recorded unavailable fallback",
        ):
            self.assertNotIn(retired, runtime)

    def test_review_is_mandatory_with_one_fixed_thirty_minute_deadline(self) -> None:
        closeout = self.read("references/codex-review-closeout.md")
        gates = self.read("references/gates.md")
        for token in ("head SHA", "base ref", "merge-base SHA"):
            self.assertIn(token, closeout)
        self.assertIn("entire tuple matches", closeout)
        self.assertIn("one 30-minute total active-wait deadline", closeout)
        self.assertIn("monitoring-required", closeout)
        self.assertIn("Do not extend the deadline", " ".join(closeout.split()))
        self.assertIn("`review_operation`", closeout)
        self.assertIn("`mutation_mode=apply`", closeout)
        self.assertIn("never expose the translation as a user option", closeout)
        self.assertIn("Review has no skip", gates)
        self.assertNotIn("15-minute", closeout)
        self.assertNotIn("extended profile", closeout)
        self.assertNotIn("explicitly-skipped-by-authorized-user", self.runtime_text())

    def test_ci_requires_current_head_evidence_and_cannot_pass_empty(self) -> None:
        skill = " ".join(self.read("SKILL.md").split())
        gates = " ".join(self.read("references/gates.md").split())

        self.assertIn("expected to produce at least one applicable result", skill)
        self.assertIn("exact head SHA", gates)
        self.assertIn("Zero applicable CI results", gates)
        self.assertIn("`ci-unavailable` blocker", gates)

    def test_closeout_arms_issues_partials_and_global_parent_without_merging(self) -> None:
        closeout = " ".join(
            self.read("references/codex-review-closeout.md").split()
        )
        gates = " ".join(self.read("references/gates.md").split())
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )

        for text in (closeout, gates, delivery):
            self.assertIn("generated implementation issue", text)
            self.assertIn("implementation-eligible Feature Spec", text)
            self.assertIn("parent/global Feature Spec", text)
            self.assertIn("final integration partial", text)
            self.assertIn("every partial gate", text)
            self.assertIn("fully qualified", text)
        self.assertIn("default-branch closeout PR", closeout)
        self.assertIn("hosted issues stay open until merge", delivery)
        for text in (closeout, gates, delivery):
            self.assertIn("default branch", text)

    def test_ledger_is_a_compact_evidence_projection(self) -> None:
        ledger = self.read("references/ledger.md")
        template = self.read("references/ledger-template.md")
        for text in (ledger, template):
            for heading in (
                "## Authorization",
                "## Source Snapshots",
                "## Active Root",
                "## Feature Spec Task Registry",
                "## Codex Review Wait Registry",
                "## Recovery Packet",
                "## External Handoff",
            ):
                self.assertIn(heading, text)
            self.assertNotIn("## Option Resolution", text)
            self.assertNotIn("Runtime Metrics", text)
            self.assertNotIn("fallback_reason", text)

    def test_takeover_contract_uses_renamed_permission(self) -> None:
        runtime = self.runtime_text()
        compact_runtime = " ".join(runtime.split())
        self.assertIn("stale_claim_takeover_permission", runtime)
        self.assertIn("--takeover-permission granted-by-authorized-user", runtime)
        self.assertIn("--expected-task-termination", runtime)
        self.assertIn("--expected-task-adoption", runtime)
        self.assertIn("claim recover-takeover", runtime)
        self.assertIn("stale heartbeat alone", runtime.lower())
        self.assertIn("accepts only current schema-5 claims", runtime)
        self.assertIn("without migration, retirement, or deletion", compact_runtime)
        self.assertNotIn("claim retire-legacy", runtime)
        self.assertNotIn("schema-3 and schema-4", runtime)
        self.assertNotIn("--takeover-policy", runtime)
        self.assertNotIn("takeover-authorized", runtime)

    def test_takeover_permission_precedes_task_stop_and_preserves_task_identity(self) -> None:
        skill = " ".join(self.read("SKILL.md").split())
        options = " ".join(self.read("references/options.md").split())
        worker = " ".join(self.read("references/worker.md").split())

        discovery = skill.index("perform read-only discovery first")
        permission = skill.index("Then resolve `stale_claim_takeover_permission`")
        stop = skill.index("may the root stop the tasks through the App runtime")
        takeover = skill.index("scripts/active-root-claim --json claim takeover")
        self.assertLess(discovery, permission)
        self.assertLess(permission, stop)
        self.assertLess(stop, takeover)

        self.assertIn("Denial creates no task mutation", skill)
        self.assertIn("complete repository/source scopes", skill)
        self.assertIn("partial-root takeover is invalid", skill)
        self.assertIn("adopt those exact tasks", skill)
        self.assertIn(
            "Never create a new task for a Spec that has recorded or embedded task evidence",
            skill,
        )
        self.assertIn("before stopping a task", options)
        self.assertIn("same-task adoption", options)
        self.assertIn("adopt the exact original task ref", worker.lower())
        self.assertIn("inability to adopt or resume it is a blocker", worker)

    def test_takeover_is_prepared_recoverable_and_self_contained(self) -> None:
        skill = " ".join(self.read("SKILL.md").split())
        ledger = " ".join(self.read("references/ledger.md").split())
        recovery = " ".join(
            self.read("references/recovery-validation.md").split()
        )
        worker = " ".join(self.read("references/worker.md").split())
        options = self.read("references/options.md")

        self.assertIn("prepared-takeover journal before it deletes any prior claim", skill)
        self.assertIn("journal remains an ownership record", skill)
        self.assertIn("full replaced-claim snapshot", skill)
        self.assertIn("validated per-Spec adoption data", skill)
        self.assertIn("claim recover-takeover", skill)
        self.assertIn("<candidate-root>.takeover", ledger)
        self.assertIn("journal itself owns the union scope", ledger)
        self.assertIn("Every mutating helper command first replays", ledger)
        self.assertIn("one `specs` entry for every claimed source exactly once", ledger)
        self.assertIn("task_state: \"no-task\"", ledger)
        self.assertIn("exact already-resolved `task_model`", ledger)
        self.assertIn("no-task mapping preserves the profile", ledger)
        self.assertIn("one owner across the complete takeover candidate", ledger)
        self.assertIn("current branch to equal `target_branch_name`", ledger)
        self.assertIn("`baseline_revision` resolves as a commit", ledger)
        self.assertIn("candidate recovery root", ledger)
        for field in (
            '"source_spec_ref"',
            '"task_ref"',
            '"goal_evidence_ref"',
            '"managed_checkouts"',
        ):
            self.assertIn(field, ledger)
        self.assertIn("`ledger_ref`", ledger)
        self.assertIn("rebuild only that exact projection", recovery)
        self.assertIn("candidate claim's validated embedded adoption mapping", worker)
        self.assertIn("prepared-takeover transaction ids", options)
        self.assertNotIn("expected_task_adoption", options)

    def test_preclaim_fixture_has_zero_mutations_on_early_abort(self) -> None:
        cases = (
            (
                False,
                True,
                "not-requested",
                False,
                "unsupported-runtime",
                ["surface"],
            ),
            (
                True,
                False,
                "not-requested",
                False,
                "unsupported-runtime",
                ["surface"],
            ),
            (
                True,
                True,
                "denied-by-authorized-user",
                True,
                "permission-denied",
                ["surface", "authorization"],
            ),
            (
                True,
                True,
                "granted-by-authorized-user",
                False,
                "planning-required",
                ["surface", "authorization", "intake"],
            ),
        )
        for surface, goal_surface, permission, ready, expected, observations in cases:
            with self.subTest(expected=expected):
                outcome, observed, mutations = run_app_preclaim_fixture(
                    surface_available=surface,
                    goal_surface_available=goal_surface,
                    permission=permission,
                    bundle_ready=ready,
                )
                self.assertEqual(outcome, expected)
                self.assertEqual(observed, observations)
                self.assertEqual(mutations, [])

        outcome, observations, mutations = run_app_preclaim_fixture(
            surface_available=True,
            permission="granted-by-authorized-user",
            bundle_ready=True,
        )
        self.assertEqual(outcome, "accepted")
        self.assertEqual(observations, ["surface", "authorization", "intake"])
        self.assertEqual(
            mutations,
            ["atomic-claim", "cache-retention", "ledger-projection", "portfolio-goal"],
        )

    def test_multi_repo_requires_one_task_and_all_managed_checkouts(self) -> None:
        text = " ".join(self.read("references/multi-repo-workspace.md").split())
        self.assertIn("one visible App task per Feature Spec", text)
        self.assertIn("distinct isolated checkout for every required repository", text)
        self.assertIn("one real, non-draft, reviewed, CI-clean", text)
        self.assertIn("Each task uses its Feature Spec's target branch name", text)
        self.assertIn("exactly one distinct repo-owned integration Feature Spec", text)
        self.assertIn("bounded path change", text)
        self.assertIn("validation-only or no-op", text)
        self.assertIn("feature/<feature_slug>-integration", text)
        self.assertIn("<ordinary_target_branch_name>-integration", text)
        self.assertIn("must equal `<ordinary_target_branch_name>-integration`", text)

    def test_knowledge_payload_exists_only_on_the_final_issue(self) -> None:
        delivery = self.read("references/spec-backed-delivery.md")
        skill = self.read("SKILL.md")
        spec_template = (
            REPO / "skills/plan-feature/references/spec-template.md"
        ).read_text()
        issue_template = (
            REPO / "skills/plan-feature/references/issue-body-template.md"
        ).read_text()

        self.assertNotIn("knowledge_delta:", spec_template)
        self.assertNotIn("## Domain Knowledge Handoff", spec_template)
        self.assertIn("## Domain Knowledge Closeout", issue_template)
        self.assertIn("knowledge_delta:", issue_template)
        self.assertIn("A Feature Spec containing", delivery)
        self.assertIn("is incompatible", delivery)
        self.assertIn("only in the final issue's `## Domain Knowledge Closeout`", skill)

    def test_knowledge_targets_must_fit_final_issue_execution_scope(self) -> None:
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        skill = " ".join(self.read("SKILL.md").split())

        for contents in (delivery, skill):
            self.assertIn("repository", contents)
            self.assertIn("repo-relative path", contents)
            self.assertIn("`affected_repositories`", contents)
            self.assertIn("`allowed_paths`", contents)
            self.assertIn("`planning-required`", contents)
        self.assertIn("every `target_surfaces` entry", delivery)
        self.assertIn("intake must not widen the Execution Contract", delivery)
        self.assertIn("intake never widens execution scope", skill)

    def test_knowledge_closeout_owner_is_graph_final_and_self_contained(self) -> None:
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        skill = " ".join(self.read("SKILL.md").split())

        for contents in (delivery, skill):
            self.assertIn("remaining", contents)
            self.assertIn("dedicated integration partial", contents)
            self.assertIn("memory_slice=domain-memory", contents)
            self.assertIn("domain_operation=implementation-closeout", contents)
            self.assertIn("after integrated behavior", contents)
            self.assertIn("planning-required", contents)
        self.assertIn("exclude it and its own `dependency_ids`", skill)
        self.assertIn("no-dependent", skill)
        self.assertIn("nodes with no dependents", delivery)
        self.assertIn("Require exactly one `## Domain Knowledge Closeout` owner", delivery)
        self.assertIn("temporarily remove the owner and its outgoing `dependency_ids`", delivery)
        self.assertIn("No issue may depend on the owner", delivery)
        self.assertIn("must not infer or add it from worker instructions", delivery)

    def test_nonempty_knowledge_closeout_requires_captured_result(self) -> None:
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        skill = " ".join(self.read("SKILL.md").split())
        gates = " ".join(self.read("references/gates.md").split())
        worker = " ".join(self.read("references/worker.md").split())

        for contents in (delivery, skill, gates, worker):
            self.assertIn("capture_outcome=captured", contents)
            self.assertIn("every", contents)
            self.assertIn("named target", contents)
            self.assertIn("documentation-diff", contents)
            self.assertIn("deferred", contents)
            self.assertIn("no-durable-change", contents)
            self.assertIn("blocks", contents)
            self.assertIn("contradicted", contents)
            self.assertIn("owner decision", contents)
        self.assertIn("Domain Knowledge Closeout Gate", gates)
        self.assertIn("blocks domain closeout and terminal `merge-ready`", gates)

    def test_domain_closeout_evidence_is_revision_bound_and_recoverable(self) -> None:
        ledger = " ".join(self.read("references/ledger.md").split())
        template = " ".join(self.read("references/ledger-template.md").split())
        recovery = " ".join(self.read("references/recovery-validation.md").split())
        review = " ".join(self.read("references/codex-review-closeout.md").split())

        for token in (
            "knowledge_delta` fingerprint",
            "verified named destination",
            "documentation-diff fingerprint",
            "implementation revision tuples",
        ):
            self.assertIn(token, ledger)
        self.assertIn("gate=domain-knowledge-closeout", ledger)
        self.assertIn("Domain closeout evidence", template)
        self.assertIn("recompute the delta fingerprint", recovery)
        self.assertIn("requires the exact Project Memory closeout again", recovery)
        self.assertIn("invalidates captured domain-closeout evidence", review)
        self.assertIn("persist fresh delta", review)

    def test_intake_rejects_non_forward_generated_dependencies(self) -> None:
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        skill = " ".join(self.read("SKILL.md").split())

        self.assertIn("strictly-earlier intra-Spec dependency IDs", skill)
        self.assertIn("strictly earlier generated issue", delivery)
        self.assertIn("reject self, same-ID, and later-ID dependencies", delivery)

    def test_github_shorthand_is_normalized_for_claim_and_task_identity(self) -> None:
        skill = " ".join(self.read("SKILL.md").split())
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        ledger = self.read("references/ledger.md")
        template = self.read("references/ledger-template.md")

        for text in (skill, delivery, ledger):
            self.assertIn("owner/repository#N", text)
            self.assertIn("https://github.com/owner/repository/issues/N", text)
        self.assertIn("use the URL as the claim/task source id", skill)
        self.assertIn("Preserve the shorthand as the authoritative artifact ref", delivery)
        for text in (ledger, template):
            self.assertIn("authoritative_source_ref", text)
            self.assertIn("canonical_source_id", text)
        self.assertIn("Never pass GitHub shorthand directly to the helper", skill)

    def test_local_move_is_scoped_and_revalidated_at_the_resulting_head(self) -> None:
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        gates = " ".join(self.read("references/gates.md").split())
        recovery = " ".join(
            self.read("references/recovery-validation.md").split()
        )
        ledger = " ".join(self.read("references/ledger.md").split())

        for token in (
            "tracker-owning Git repository",
            "exact active",
            "derived `done/`",
            "inside that affected Git repository",
        ):
            self.assertIn(token, delivery)
        self.assertIn("outside all affected Git repositories is non-App-executable", delivery)
        self.assertLess(gates.index("move each issue"), gates.index("commit and push"))
        self.assertLess(gates.index("commit and push"), gates.index("current-revision review"))
        self.assertLess(
            gates.index("current-revision review"),
            gates.index("terminal merge-ready state"),
        )
        self.assertIn("prepared", gates)
        self.assertIn("planned_done_ref", ledger)
        self.assertIn("source_state=active", ledger)
        self.assertIn("source_state=done", ledger)
        self.assertIn("accept a missing active path only when", recovery)
        self.assertIn("do not classify it as external drift", recovery)
        self.assertIn("Both paths, neither path", recovery)

    def test_terminal_pr_base_is_derived_default_branch(self) -> None:
        skill = " ".join(self.read("SKILL.md").split())
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        gates = " ".join(self.read("references/gates.md").split())
        closeout = " ".join(
            self.read("references/codex-review-closeout.md").split()
        )

        self.assertIn("Every terminal PR targets", skill)
        self.assertIn("discovered default branch", skill)
        self.assertIn("derived and verified, never selected", skill)
        self.assertIn("verified during preflight and current-head review", delivery)
        self.assertIn("base equal to that repository's currently discovered default branch", gates)
        self.assertIn("closing keywords cannot take effect", closeout)

    def test_terminal_pr_requires_current_mergeability_and_repo_rules(self) -> None:
        skill = " ".join(self.read("SKILL.md").split())
        gates = " ".join(self.read("references/gates.md").split())
        worker = " ".join(self.read("references/worker.md").split())
        ledger = " ".join(self.read("references/ledger.md").split())
        closeout = " ".join(
            self.read("references/codex-review-closeout.md").split()
        )

        for contents in (skill, gates, worker, closeout):
            self.assertIn("`OPEN`", contents)
            self.assertIn("mergeability", contents)
            self.assertIn("conflict", contents)
            self.assertIn("approval", contents)
            self.assertIn("merge-queue eligibility", contents)
            self.assertIn("unknown", contents.lower())
            self.assertIn("never enqueue", contents.lower())
        self.assertIn("gate=pr-mergeability", ledger)
        self.assertIn("`isDraft=false`", ledger)
        self.assertIn("exact PR/head/base/merge-base tuple", ledger)
        self.assertIn("current-head mergeability and repository-rule evidence", skill)

        report = " ".join(self.read("references/worker.md").split())
        for token in (
            "actual `capture_outcome`",
            "delta fingerprint",
            "verified named destination",
            "documentation-diff fingerprint",
            "implementation revision tuples",
        ):
            self.assertIn(token, report)
        self.assertIn("convert it to ready-for-review", skill)
        self.assertIn("transition is not the terminal result", skill)
        self.assertIn("Do not make draft status a circular prerequisite", gates)
        self.assertIn("ready-for-review with `isDraft=false`", gates)
        self.assertIn("convert any draft to ready-for-review", worker)
        self.assertIn("After that nonterminal transition", worker)
        self.assertLess(
            worker.index("convert any draft to ready-for-review"),
            worker.index("current GitHub mergeability"),
        )
        states = worker.split("Canonical states are", 1)[1].split(".\n", 1)[0]
        self.assertLess(
            states.index("`marking-ready-for-review`"),
            states.index("`review-polling`"),
        )
        self.assertLess(
            states.index("`preparing-tracker-closeout`"),
            states.index("`checking-mergeability`"),
        )
        self.assertNotIn("`marking-ready`", states)
        self.assertIn("captured domain-closeout evidence", skill)
        self.assertIn("read access to PR lifecycle", skill)
        self.assertIn("mergeability/conflicts", skill)
        for token in (
            "current PR lifecycle/conflict/mergeability state",
            "required base-freshness",
            "approval state",
            "merge-queue eligibility",
            "observation tuple/time",
        ):
            self.assertIn(token, report)

    def test_integration_partial_uses_a_distinct_per_spec_branch(self) -> None:
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        plan_options = " ".join(
            (
                REPO / "skills/plan-feature/references/options.md"
            ).read_text().split()
        )
        fixture = (
            REPO / "skills/plan-feature/references/full-flow-dry-run.md"
        ).read_text()

        self.assertIn("shared inside each Feature Spec", delivery)
        self.assertIn("<ordinary_target_branch_name>-integration", delivery)
        self.assertIn("feature/<feature_slug>-integration", plan_options)
        self.assertIn("<ordinary_target_branch_name>-integration", plan_options)
        self.assertIn("Branch sharing is per Feature Spec", plan_options)
        self.assertIn(
            "integration_target_branch: feature/account-settings-export-integration",
            fixture,
        )

    def test_portfolio_rejects_same_repository_branch_collisions(self) -> None:
        skill = " ".join(self.read("SKILL.md").split())
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        workspace = " ".join(
            self.read("references/multi-repo-workspace.md").split()
        )

        for contents in (skill, delivery, workspace):
            self.assertIn("(repository, target_branch_name)", contents)
            self.assertIn("implementation-eligible", contents)
            self.assertIn("coordination-only parent/global", contents)
            self.assertIn("no task", contents)
            self.assertIn("App-managed worktree", contents)
            self.assertIn("same branch name", contents)
            self.assertIn("different repositories", contents)
            self.assertIn("paths are disjoint", contents)
            self.assertIn("`planning-required` before CLAIM", contents)
        self.assertIn("Never serialize around it", skill)
        self.assertIn("force-bind", skill)
        self.assertIn("schedule around the collision", workspace)

    def test_local_closeout_uses_one_ready_for_review_sequence(self) -> None:
        clauses = {
            "SKILL.md": "For a local source, after substantive acceptance",
            "references/gates.md": "For local Markdown, complete substantive acceptance",
            "references/codex-review-closeout.md": "For a local Markdown source, first finish",
            "references/spec-backed-delivery.md": "For local Markdown, after substantive acceptance",
            "references/worker.md": "For local tracker artifacts",
            "../plan-feature/references/issue-body-template.md": "Local tracker: after implementation",
        }

        for path, start in clauses.items():
            contents = " ".join(self.read(path).split())
            self.assertIn(start, contents, path)
            segment = contents.split(start, 1)[1][:900]
            self.assertLess(segment.index("$autoreview"), segment.index("ready-for-review"), path)
            self.assertLess(
                segment.index("ready-for-review"),
                segment.index("current-revision review"),
                path,
            )
            self.assertLess(segment.index("current-revision review"), segment.index("CI"), path)
            self.assertLess(segment.index("CI"), segment.index("terminal merge-ready"), path)

    def test_metadata_is_manual_and_compact(self) -> None:
        skill = self.read("SKILL.md")
        metadata = self.read("agents/openai.yaml")
        self.assertEqual(ROOT.name, "implement-feature")
        self.assertIn("name: implement-feature", skill)
        self.assertIn("explicitly invokes $implement-feature", skill)
        self.assertIn("merge-ready-but-unmerged pull requests", skill)
        self.assertIn('display_name: "Implement Feature"', metadata)
        self.assertIn("allow_implicit_invocation: false", metadata)
        short_description = re.search(
            r'^  short_description: "(.+)"$', metadata, re.MULTILINE
        )
        self.assertIsNotNone(short_description)
        assert short_description is not None
        self.assertGreaterEqual(len(short_description.group(1)), 25)
        self.assertLessEqual(len(short_description.group(1)), 64)
        prompt = re.search(r'^  default_prompt: "(.+)"$', metadata, re.MULTILINE)
        self.assertIsNotNone(prompt)
        assert prompt is not None
        self.assertEqual(prompt.group(1).count("."), 1)
        self.assertLess(len(prompt.group(1)), 240)

    def test_implement_feature_is_the_only_app_feature_executor(self) -> None:
        app_feature_executors = []
        for path in (REPO / "skills").iterdir():
            skill_path = path / "SKILL.md"
            metadata_path = path / "agents/openai.yaml"
            if not path.is_dir() or not skill_path.is_file() or not metadata_path.is_file():
                continue
            skill = skill_path.read_text(encoding="utf-8")
            metadata = metadata_path.read_text(encoding="utf-8")
            if (
                "single App-only implementation adapter" in skill
                and "Feature Spec" in skill
                and "allow_implicit_invocation: false" in metadata
            ):
                app_feature_executors.append(path.name)
        self.assertEqual(sorted(app_feature_executors), ["implement-feature"])

    def test_retired_package_facing_names_are_absent(self) -> None:
        retired = (
            "codex" + "-orchestrator",
            "Codex App " + "Orchestrator",
            "Codex " + "Orchestrator",
            "orchestrator" + "-claim",
            "orchestrator" + "-cache",
            "App" + "OrchestratorContractTests",
            "# App " + "Orchestrator Authorization Contract",
            "# Codex App " + "Orchestration Ledger",
            "# Codex App " + "Orchestration Gates",
            "# " + "Orchestration Cache Lifecycle",
        )
        findings = []
        for root in (REPO / "AGENTS.md", REPO / "README.md", REPO / ".agents", REPO / "skills"):
            paths = [root] if root.is_file() else root.rglob("*")
            for path in paths:
                if not path.is_file() or "__pycache__" in path.parts:
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                for token in retired:
                    if token in text:
                        findings.append(f"{path.relative_to(REPO)}: {token}")
        self.assertEqual(findings, [])
        self.assertFalse((ROOT / ("scripts/orchestrator" + "-claim")).exists())
        self.assertFalse((ROOT / ("scripts/orchestrator" + "-cache")).exists())


if __name__ == "__main__":
    unittest.main()
