import unittest
from pathlib import Path


REFERENCE = Path(__file__).resolve().parents[1] / "references/review-delivery.md"
ORCHESTRATION = Path(__file__).resolve().parents[1] / "references/orchestration.md"
SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
PREFLIGHT = Path(__file__).resolve().parents[3] / "references/codex-dependency-preflight.md"
TASK_PROFILE = Path(__file__).resolve().parents[1] / "references/task-profile.md"
TASK_HANDOFF = Path(__file__).resolve().parents[3] / "references/task-handoff.md"
RUN_STATE = Path(__file__).resolve().parents[1] / "references/run-state.md"
STATES = Path(__file__).resolve().parents[1] / "references/states.md"


class ReviewDeliveryContractTests(unittest.TestCase):
    def test_orchestrator_title_uses_selected_feature_count(self) -> None:
        profile = TASK_PROFILE.read_text(encoding="utf-8")
        handoff = " ".join(TASK_HANDOFF.read_text(encoding="utf-8").split())
        templates = {}
        for line in profile.splitlines():
            key, separator, value = line.strip().partition(": ")
            if separator and key in {"singular", "plural"}:
                templates[key] = value.strip('"')

        self.assertEqual(
            templates,
            {
                "singular": "🤖 Orchestrator · 1 Feature",
                "plural": "🤖 Orchestrator · <feature_count> Features",
            },
        )
        self.assertEqual(templates["singular"], "🤖 Orchestrator · 1 Feature")
        self.assertEqual(
            templates["plural"].replace("<feature_count>", "6"),
            "🤖 Orchestrator · 6 Features",
        )
        self.assertIn(
            "use `1 Feature` for one selected Feature and `<feature_count> Features` for multiple selected Features",
            handoff,
        )
        self.assertNotIn("<feature_set_count>", profile)

    def test_one_feature_worker_owns_each_feature_and_its_single_pr(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        orchestration = ORCHESTRATION.read_text(encoding="utf-8")
        profile = TASK_PROFILE.read_text(encoding="utf-8")
        run_state = RUN_STATE.read_text(encoding="utf-8")

        self.assertIn("one-feature-worker-per-feature", profile)
        self.assertIn('title_template: "🛠️ Feature Worker · <Feature outcome>"', profile)
        self.assertIn("For every Feature member, bootstrap exactly one Feature Worker", orchestration)
        self.assertIn("executes its derived units in deterministic prerequisite order", " ".join(orchestration.split()))
        self.assertIn("selected parent Feature semantic contract are required input", " ".join(skill.split()))
        self.assertIn("one observed Macro projection state", orchestration)
        self.assertIn("Exactly one assignment may exist per claimed Feature", run_state)
        self.assertIn(
            "must not receive an empty commit, empty PR, cosmetic change, or artificial proof",
            " ".join(skill.split()),
        )

    def test_issue_refs_are_the_only_selection_input_and_metadata_is_ignored(self) -> None:
        skill = " ".join(SKILL.read_text(encoding="utf-8").split())
        orchestration = " ".join(ORCHESTRATION.read_text(encoding="utf-8").split())
        states = " ".join(STATES.read_text(encoding="utf-8").split())

        self.assertIn("caller-supplied GitHub parent issue references", skill)
        self.assertIn("selected implementation set is exactly those parent issues", skill)
        self.assertIn("never enlarge the selected implementation set", skill)
        self.assertIn(
            "Do not read, search, infer, validate, mutate, or gate on them",
            skill,
        )
        self.assertIn("resolves only the exact caller-supplied parent issue refs", orchestration)
        self.assertIn("never expand the selected implementation set", orchestration)
        self.assertIn("without GitHub label or Issue Type metadata", states)

    def test_feature_worker_support_delegation_is_optional_and_parent_owned(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        orchestration = ORCHESTRATION.read_text(encoding="utf-8")
        profile = TASK_PROFILE.read_text(encoding="utf-8")
        normalized_skill = " ".join(skill.split())
        normalized_orchestration = " ".join(orchestration.split())

        self.assertIn("role: feature-worker-support", profile)
        self.assertIn("topology: bounded-feature-worker-support", profile)
        self.assertIn(
            "topology: orchestrator-with-feature-workers-and-optional-support",
            profile,
        )
        for responsibility in (
            "code-analyst",
            "execution-assistant",
            "validation-assistant",
            "critic-reviewer",
        ):
            self.assertIn(responsibility, normalized_skill)
            self.assertIn(responsibility, normalized_orchestration)

        for mode in ("delegated-support", "serial-fallback", "unavailable", "unknown"):
            self.assertIn(mode, profile)

        self.assertIn("Delegation is not a required topology gate", normalized_skill)
        self.assertIn("never access the SQLite ledger", normalized_skill)
        self.assertIn("owns the final candidate HEAD", normalized_skill)
        self.assertIn(
            "never creates another Feature Worker or planner task",
            normalized_orchestration,
        )
        self.assertIn("outside the implementation ledger", normalized_orchestration)

    def test_pr_delivery_derives_closure_from_verified_existing_projections(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        normalized = " ".join(reference.split())

        for required in (
            "derive `closing_issue_refs` deterministically from that parent Feature",
            "[this parent Feature issue] + [every verified existing Macro Task child issue owned by this Feature]",
            "There is no per-Task opt-out",
            "no Worker-supplied closure list",
            "The PR declares closure intent",
            "GitHub closes this Feature and its local Macro Tasks only when the PR is merged",
            "`closingIssuesReferences` field is not a stable pre-merge contract for stacked PRs",
        ):
            self.assertIn(required, normalized)

        self.assertIn(
            "never require it to equal `closing_issue_refs`",
            normalized,
        )
        self.assertIn(
            "Verify the PR body carries the exact source-derived closure intent",
            normalized,
        )
        self.assertNotIn(
            "Require the " + "read-back set",
            normalized,
        )
        self.assertIn("available Macro Task contextual coverage evidence", normalized)
        self.assertIn("Never invent closure refs", normalized)

    def test_pr_body_is_minimal_durable_and_free_of_routine_counts(self) -> None:
        reference = " ".join(REFERENCE.read_text(encoding="utf-8").split())

        for required in (
            "The SE-authored PR body is a reviewer-facing summary, not an execution ledger",
            "one short paragraph or at most three bullets",
            "reporting names only rather than counts or output",
            "routine test counts, or pass/fail totals",
            "reconstruct the SE-owned sections from the current candidate",
            "Remove disallowed stale SE-owned content in that same update",
            "Preserve repository-required template fields and unrelated existing author content",
            "minimal durable SE-owned PR-body readback",
        ):
            self.assertIn(required, reference)

        self.assertIn(
            "Exact-HEAD acceptance, validation, review, CI, and topology proof remains",
            reference,
        )

    def test_native_review_uses_a_supported_minimal_invocation(self) -> None:
        reference = " ".join(REFERENCE.read_text(encoding="utf-8").split())

        for required in (
            "Inspect the live review capability's supported invocation modes",
            "smallest supported base-scoped review mode",
            "without optional custom instructions or unrelated strict-configuration overrides",
            "at most one fallback attempt",
            "A rejected or unavailable review is not a clean result",
        ):
            self.assertIn(required, reference)

    def test_native_review_reconciles_interrupted_delivery_before_retry(self) -> None:
        reference = " ".join(REFERENCE.read_text(encoding="utf-8").split())

        for required in (
            "native review result and its delivery or monitoring stream as separate evidence",
            "does not prove that the review failed",
            "independently re-observe the same review lineage",
            "terminal content takes precedence over generic interrupted transport or execution metadata",
            "preserve it as pending and observe it again later without starting a duplicate",
            "at most one replacement minimal review",
            "same Worker against the unchanged exact candidate",
            "fail closed without a replacement review",
            "conflicting terminal artifacts are unavailable review evidence",
        ):
            self.assertIn(required, reference)

        for process_detail in ("PID", "PGID", "stdout", "stderr"):
            self.assertNotIn(process_detail, reference)

    def test_publication_uses_the_verified_feature_worker_worktree(self) -> None:
        reference = " ".join(REFERENCE.read_text(encoding="utf-8").split())

        for required in (
            "Feature Worker's actual implementation worktree",
            "Use that exact verified worktree as the publication execution context",
            "An inherited working directory",
            "temporary title or body artifact",
            "never retry publication from an alternate temporary directory",
        ):
            self.assertIn(required, reference)

    def test_stacked_children_link_separately(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        orchestration = ORCHESTRATION.read_text(encoding="utf-8")
        normalized = " ".join(reference.split())
        orchestration_normalized = " ".join(orchestration.split())

        self.assertIn("separate G-owned pairwise stack-link workflow", normalized)
        self.assertIn("Before bootstrapping a stacked child", orchestration_normalized)
        self.assertIn("`candidate-published` parent branch and exact HEAD", orchestration_normalized)
        self.assertIn("The parent may remain `delivery-pending`", orchestration_normalized)
        self.assertNotIn("Task-only", normalized)
        self.assertIn("this parent Feature and every verified existing associated local Macro Task", normalized)

    def test_stacked_child_blocks_on_confirmed_parent_ci_failure(self) -> None:
        skill = " ".join(SKILL.read_text(encoding="utf-8").split())
        orchestration = " ".join(ORCHESTRATION.read_text(encoding="utf-8").split())
        reference = " ".join(REFERENCE.read_text(encoding="utf-8").split())
        states = " ".join(STATES.read_text(encoding="utf-8").split())
        contract = " ".join((skill, orchestration, reference, states))

        for required in (
            "no applicable CI check on that current parent HEAD is confirmed failing",
            "Pending CI remains non-blocking",
            "confirmed failure blocks the child",
            "G-owned diagnosis",
            "exclusively infrastructure or flaky and unrelated to candidate correctness",
            "binds the failure to that check run",
        ):
            self.assertIn(required, contract)

        self.assertIn(
            "parent delivery readiness is not a worker-bootstrap gate",
            orchestration,
        )

    def test_starting_branch_is_selectable_refreshed_and_frozen_before_bootstrap(self) -> None:
        skill = " ".join(SKILL.read_text(encoding="utf-8").split())
        orchestration = " ".join(ORCHESTRATION.read_text(encoding="utf-8").split())
        reference = " ".join(REFERENCE.read_text(encoding="utf-8").split())
        run_state = " ".join(RUN_STATE.read_text(encoding="utf-8").split())
        states = " ".join(STATES.read_text(encoding="utf-8").split())

        self.assertIn("optional `starting_branch` selection per target repository", skill)
        self.assertIn("authoritative provider default branch", skill)
        self.assertIn("never silently substitute the default branch", skill)
        self.assertIn("Before every standalone or root Feature Worker bootstrap wave", orchestration)
        self.assertIn("refresh the selected branch from its authoritative upstream", orchestration)
        self.assertIn("must be fast-forward-only", orchestration)
        self.assertIn("never mix two starting SHAs inside one bootstrap wave", orchestration)
        self.assertIn("initial HEAD resolves to the frozen `base_sha`", orchestration)
        self.assertIn(
            "detached HEAD at the exact frozen SHA is the normal valid state",
            orchestration,
        )
        self.assertIn(
            "do not require a Feature `head_branch` to exist during the assigned-task bootstrap",
            orchestration,
        )
        self.assertIn(
            "Only that post-bootstrap branch readback may establish the durable",
            orchestration,
        )
        self.assertIn("the recorded `head_branch` is required", orchestration)
        self.assertIn(
            "initial detached HEAD may equal the verified immediate parent candidate SHA",
            orchestration,
        )
        self.assertIn("stacked child instead starts from its verified immediate parent's", orchestration)
        self.assertIn("existing assignment `base_branch` and `base_sha` fields", run_state)
        self.assertIn("requires no table, schema, runtime-contract, envelope, or CLI-behavior change", run_state)
        self.assertIn("selected starting branch", reference)
        self.assertIn("verified exact base", states)
        self.assertIn("initial detached or attached checkout", states)
        self.assertIn("earlier task bootstrap may observe detached HEAD", states)

    def test_feature_plan_set_scheduling_and_per_feature_closure_are_explicit(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        orchestration = ORCHESTRATION.read_text(encoding="utf-8")
        reference = REFERENCE.read_text(encoding="utf-8")

        normalized_skill = " ".join(skill.split())
        normalized_orchestration = " ".join(orchestration.split())
        normalized_reference = " ".join(reference.split())

        for required in (
            "Feature Plan Sets",
            "Feature-level `blocked_by`",
            "same-parent-only",
            "exactly one PR output per implementation-eligible selected Feature",
            "same-repository edge is mandatory stack intent",
            "cross-repository edge as scheduling-only",
        ):
            self.assertIn(required, normalized_skill)

        for required in (
            "Feature Plan Sets",
            "hard outcome dependencies",
            "every same-repository edge is mandatory stack intent",
            "every cross-repository edge is scheduling-only",
            "Sibling Features and their Tasks are never included",
        ):
            self.assertIn(required, normalized_orchestration + normalized_reference)

        self.assertIn("verified existing subset", normalized_reference)
        self.assertIn("cross-parent", normalized_reference)

    def test_native_issue_dependencies_are_diagnostic_and_never_repaired(self) -> None:
        skill = " ".join(SKILL.read_text(encoding="utf-8").split())
        orchestration = " ".join(ORCHESTRATION.read_text(encoding="utf-8").split())

        self.assertIn("never use them as semantic authority or a gate", skill)
        self.assertIn("body-backed graph", skill)
        self.assertIn("Implement never repairs native issue dependencies automatically", skill)
        for drift in ("missing", "failed", "unavailable", "unknown", "extra", "stale"):
            self.assertIn(drift, skill)
            self.assertIn(drift, orchestration)
        self.assertIn("diagnostic projection evidence only", orchestration)
        self.assertIn("without blocking or changing scheduling, stack intent", orchestration)
        self.assertIn("never repair a native dependency during Implement", orchestration)

    def test_parent_feature_contract_allows_degraded_macro_projections(self) -> None:
        skill = " ".join(SKILL.read_text(encoding="utf-8").split())
        orchestration = " ".join(ORCHESTRATION.read_text(encoding="utf-8").split())
        reference = " ".join(REFERENCE.read_text(encoding="utf-8").split())

        for projection_state in ("`complete`", "`partial`", "`absent`"):
            self.assertIn(projection_state, skill)
            self.assertIn(projection_state, orchestration)
            self.assertIn(projection_state, reference)

        self.assertIn("does not block implementation when the parent Feature semantic contract is sufficient", skill)
        self.assertIn("Never invent, repair, or publish a Task issue automatically", skill)
        self.assertIn("does not block PR publication when the parent Feature semantic contract is sufficient", reference)
        self.assertIn("quarantine", orchestration.lower())

    def test_t_ac_specializes_f_ac_and_semantic_conflicts_pause_only_the_assignment(self) -> None:
        skill = " ".join(SKILL.read_text(encoding="utf-8").split())
        orchestration = " ".join(ORCHESTRATION.read_text(encoding="utf-8").split())
        reference = " ".join(REFERENCE.read_text(encoding="utf-8").split())

        self.assertIn("deterministic `T-AC-NN` technical criteria", skill)
        self.assertIn("may only specialize", skill)
        self.assertIn("must never replace, weaken, delete, or reinterpret an F-AC", skill)
        self.assertIn("Every F-AC must have direct exact-HEAD evidence", skill)
        self.assertIn("Implement resolves missing execution decomposition", orchestration)
        self.assertIn("acceptance specificity autonomously", orchestration)
        self.assertIn("F-AC contradict each other or the outcome", orchestration)
        self.assertIn("blocked by an unselected or unfulfilled Feature", orchestration)
        self.assertIn("Keep independent Features moving", orchestration)
        self.assertIn("deterministic T-AC-NN criteria", reference)

    def test_provider_policy_is_not_an_implement_completion_gate(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        orchestration = ORCHESTRATION.read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")

        normalized_reference = " ".join(reference.split())
        normalized_skill = " ".join(skill.split())
        normalized_orchestration = " ".join(orchestration.split())

        self.assertIn("Do not require or invoke $g:github-delivery-status", normalized_skill)
        self.assertIn("Branch protection and rulesets are outside this workflow", normalized_skill)
        self.assertIn("optional provider diagnostics", normalized_skill)
        self.assertIn("Optional provider diagnostics", normalized_reference)
        self.assertIn("cannot block completion", normalized_reference)
        self.assertNotIn("Require $g:github-delivery-status", normalized_skill)
        self.assertNotIn(
            "a complete current-head $g:github-delivery-status certificate",
            normalized_reference,
        )
        self.assertNotIn("$g:github-delivery-status", preflight)
        self.assertNotIn("delivery status", normalized_orchestration)
        self.assertIn("exact published full HEAD", normalized_reference)

    def test_delivery_lifecycle_stops_before_merge(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")
        normalized = " ".join(reference.split())
        lifecycle = (
            "active @ worker-bootstrap -> active @ native-review -> "
            "delivery-pending @ candidate-published -> delivery-ready @ final-verify"
        )

        self.assertIn(lifecycle, normalized)
        self.assertIn(
            "Implement terminates with a PR published and verified on its exact HEAD",
            normalized,
        )
        self.assertIn("The PR may remain open", normalized)
        self.assertIn("They become effective only when GitHub merges the PR", normalized)
        self.assertIn(
            "current PR HEAD, the PR body carrying source-derived closure intent",
            normalized,
        )
        self.assertIn(
            "The delivery lifecycle ends at a published PR verified on its exact HEAD",
            " ".join(skill.split()),
        )

    def test_candidate_publication_hands_monitoring_to_the_orchestrator(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        orchestration = ORCHESTRATION.read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")
        profile = TASK_PROFILE.read_text(encoding="utf-8")
        run_state = RUN_STATE.read_text(encoding="utf-8")

        normalized_reference = " ".join(reference.split())
        normalized_orchestration = " ".join(orchestration.split())
        normalized_skill = " ".join(skill.split())
        normalized_profile = " ".join(profile.split())
        normalized_run_state = " ".join(run_state.split())

        self.assertIn("The orchestrator is the sole delivery monitor", normalized_skill)
        self.assertIn("becomes inactive but resumable", normalized_skill)
        self.assertIn("It does not monitor its own PR", normalized_profile)
        self.assertIn("actionable fix, evidence repair, or rebase", normalized_profile)
        self.assertIn("status=delivery-pending", normalized_reference)
        self.assertIn("checkpoint=candidate-published", normalized_reference)
        self.assertIn("releases the transient active path claim", normalized_reference)
        self.assertIn("Before any repair or rebase resumption, reacquire", normalized_run_state)
        self.assertIn("parent delivery readiness is not a worker-bootstrap gate", normalized_orchestration)
        self.assertIn("Do not wait for hosted review, CI, or provider readiness", normalized_reference)
        self.assertIn("candidate-published --> schedule", skill)
        self.assertIn("delivery-monitor --> implement-validate", skill)
        self.assertNotIn("ready-monitor", skill)

    def test_provider_automation_is_informational_and_implement_never_merges(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")

        normalized = " ".join(reference.split())
        for phrase in (
            "diagnostic only",
            "must still never enable, disable, enqueue, dequeue, bypass, or merge",
        ):
            self.assertIn(phrase, normalized)

        self.assertIn("optional provider diagnostics", " ".join(skill.split()))
        self.assertIn(
            "never merges, bypasses protections, enables or disables auto-merge, or enqueues or dequeues a PR",
            " ".join(skill.split()),
        )


if __name__ == "__main__":
    unittest.main()
