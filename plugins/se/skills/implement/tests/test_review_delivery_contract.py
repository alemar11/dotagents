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
OPENAI = Path(__file__).resolve().parents[1] / "agents/openai.yaml"


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
            self.assertIn(responsibility, normalized_orchestration)

        for mode in ("delegated-support", "serial-fallback", "unavailable", "unknown"):
            self.assertIn(mode, profile)

        self.assertIn("dispatching optional support", normalized_skill)
        self.assertIn("never access the SQLite ledger", normalized_orchestration)
        self.assertIn("owns the final candidate commit", normalized_orchestration)
        self.assertIn(
            "these conditions do not block the Feature Worker",
            normalized_orchestration,
        )
        self.assertIn(
            "never creates another Feature Worker or planner task",
            normalized_orchestration,
        )
        self.assertIn("outside the implementation ledger", normalized_orchestration)

    def test_pre_candidate_convergence_batches_risk_without_weakening_review(self) -> None:
        skill = " ".join(SKILL.read_text(encoding="utf-8").split())
        orchestration = " ".join(ORCHESTRATION.read_text(encoding="utf-8").split())
        reference = " ".join(REFERENCE.read_text(encoding="utf-8").split())
        run_state = " ".join(RUN_STATE.read_text(encoding="utf-8").split())
        states = " ".join(STATES.read_text(encoding="utf-8").split())
        openai = " ".join(OPENAI.read_text(encoding="utf-8").split())
        task_profile = " ".join(TASK_PROFILE.read_text(encoding="utf-8").split())

        for required in (
            "converging a first unpublished candidate",
            "implement-validate, plan-question",
        ):
            self.assertIn(required, skill)

        for required in (
            "Pre-candidate convergence",
            "transient Worker behavior under the existing `active @ worker-bootstrap` pair",
            "adds no workflow node, checkpoint, ledger field, task role, or review authority",
            "does not run for a verified published repair governed by hosted review",
            "cheapest deterministic static or focused checks",
            "do not replace complete Feature validation",
            "Do not trigger the pass from Worker reasoning level, diff size, or available helper capacity alone",
            "skip the critic rather than adding a redundant review",
            "existing F-AC/T-AC matrix as the invariant checklist",
            "keep it read-only and advisory",
            "Prefer the existing `critic-reviewer` support responsibility",
            "completed bounded finding set for that pass",
            "not a claim of exhaustive findings",
            "Partial helper relays do not trigger piecemeal repairs",
            "serial challenge without blocking the assignment",
            "triages the whole consolidated set before repairing",
            "focused gap-driven checks",
            "When an actually launched helper produces no usable result, the Feature Worker performs the equivalent support work",
            "never use `unavailable` or `unknown` to reconcile that attempt",
            "mixed helper set remains `delegated-support` when any usable result was integrated",
            "`serial-fallback` applies only when none was integrated and the Feature Worker performed a selected support responsibility",
            "unconsumed current or future helper result is irrevocably outside the candidate",
            "worktree readback that accounts for every residual write",
            "isolated from the candidate worktree and every validation-relevant output, cache, lock, device, database, and external state",
            "assignment's frozen base and prerequisite HEAD vector",
            "bootstrap snapshot for a standalone or stack-root assignment",
            "commit and freeze the coherent source tree",
            "One complete pass is the normal target, not a limit",
            "same frozen candidate and uses isolated outputs, caches, locks, and external state",
        ):
            self.assertIn(required, orchestration)

        for required in (
            "Commit and freeze that coherent tree",
            "complete Feature validation while the worktree remains clean and pinned to that candidate",
            "never satisfy, replace, narrow, or authorize this native-review gate",
            "Any new pre-publication HEAD invalidates the previous validation and native-review evidence",
            "run a new native review cycle in the same Feature Worker session against the new exact SHA",
        ):
            self.assertIn(required, reference)

        self.assertIn(
            "conditional advisory critique, integrated repair, and complete candidate-bound validation",
            states,
        )
        self.assertIn(
            "pre-candidate risk decision, critic pass and findings, cheap or gap-driven checks, and convergence barrier remain transient Worker technical state",
            run_state,
        )
        self.assertIn("risk-gated pre-candidate convergence", openai)
        self.assertIn("integrate actionable findings", openai)
        self.assertIn(
            "bind complete validation and native review to its exact SHA",
            openai,
        )
        self.assertIn(
            "`delegated-support` when at least one bounded helper task and usable result were independently observed and integrated",
            task_profile,
        )
        self.assertIn(
            "`serial-fallback` when no helper result was integrated and the parent performed a selected support responsibility itself",
            task_profile,
        )
        self.assertIn(
            "`unavailable` when the runtime could not provide delegation and no support responsibility was selected or performed",
            task_profile,
        )
        self.assertIn(
            "`unknown` when capability evidence was insufficient, no helper was claimed, and no support responsibility was selected or performed",
            task_profile,
        )
        self.assertIn(
            "At least one bounded helper task and usable result were independently observed and integrated",
            states,
        )
        self.assertIn(
            "record exactly one effective mode using the task-profile precedence",
            orchestration,
        )
        self.assertIn(
            "`delegated-support` when any usable helper result was integrated, otherwise `serial-fallback` when the Feature Worker performed the selected support",
            orchestration,
        )
        prompt_value = next(
            line.partition(": ")[2].strip().strip('"')
            for line in OPENAI.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith("default_prompt: ")
        )
        self.assertLessEqual(len(prompt_value), 1024)

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

    def test_review_authority_hands_off_once_from_native_to_hosted(self) -> None:
        skill = " ".join(SKILL.read_text(encoding="utf-8").split())
        reference = " ".join(REFERENCE.read_text(encoding="utf-8").split())
        orchestration = " ".join(ORCHESTRATION.read_text(encoding="utf-8").split())
        profile = " ".join(TASK_PROFILE.read_text(encoding="utf-8").split())

        for required in (
            "candidate -->|first publication| native-review",
            "candidate -->|published repair| publish-pr",
            "Native review is only the first-publication gate",
            "Exact readback of the first published PR identity and HEAD transfers independent-review authority permanently",
            "without native review",
            "hosted review remains authoritative",
            "repairs hosted findings and republishes without running native review again",
            "published repair candidate after focused validation of the affected invariant",
            "mark complete Feature validation pending",
            "cannot proceed to `final-verify` until complete Feature validation passes",
        ):
            self.assertIn(required, skill + " " + reference + " " + orchestration + " " + profile)

        for obsolete in (
            "candidate, repeats native review, and publishes",
            "A new candidate repeats native review",
            "Any candidate HEAD change repeats validation, native review",
            "current-head validation and native review evidence",
            "reruns the complete validation and review cycle",
        ):
            self.assertNotIn(obsolete, skill + " " + reference + " " + orchestration)

        states = " ".join(STATES.read_text(encoding="utf-8").split())
        self.assertIn(
            "a hosted finding repair is active at checkpoint `candidate-published`",
            states,
        )

    def test_hosted_repairs_invalidate_only_dependent_evidence(self) -> None:
        skill = " ".join(SKILL.read_text(encoding="utf-8").split())
        reference = " ".join(REFERENCE.read_text(encoding="utf-8").split())
        states = " ".join(STATES.read_text(encoding="utf-8").split())
        contract = skill + " " + reference + " " + states

        for required in (
            "repairs the violated invariant",
            "Repair every equivalent path that the same invariant governs",
            "a PR-body-only update invalidates only body and closure-intent readback",
            "preserves the same request and review lineage",
            "an ambiguous external effect invalidates only that effect",
            "complete Feature validation on the exact published HEAD",
            "a clean hosted result for the older SHA cannot carry forward",
            "complete validation is required on the exact final HEAD",
            "implement-validate -->|published HEAD unchanged after complete validation| final-verify",
            "do not republish, request another review, or invalidate the clean hosted result",
        ):
            self.assertIn(required, contract)

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
        self.assertIn("child PR head must equal the exact published candidate HEAD", normalized)
        self.assertIn("Track native or hosted review evidence separately", normalized)
        self.assertIn("reaches `candidate-published` before its hosted re-review", normalized)
        self.assertNotIn("child head must equal the reviewed candidate", normalized)

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
        states = STATES.read_text(encoding="utf-8")

        normalized_reference = " ".join(reference.split())
        normalized_orchestration = " ".join(orchestration.split())
        normalized_skill = " ".join(skill.split())
        normalized_profile = " ".join(profile.split())
        normalized_run_state = " ".join(run_state.split())
        normalized_states = " ".join(states.split())

        self.assertIn("The orchestrator is the sole delivery monitor", normalized_skill)
        self.assertIn("becomes inactive but resumable", normalized_skill)
        self.assertIn("It does not monitor its own PR", normalized_profile)
        self.assertIn("actionable fix, evidence repair, or rebase", normalized_profile)
        self.assertIn("status=delivery-pending", normalized_reference)
        self.assertIn("checkpoint=candidate-published", normalized_reference)
        self.assertIn("releases the transient active path claim", normalized_reference)
        self.assertIn("Before any repair or rebase resumption, reacquire", normalized_run_state)
        self.assertIn("`action=first-pr-publication`", normalized_run_state)
        self.assertIn("`subject_id=<canonical Feature ref>`", normalized_run_state)
        self.assertIn("stable first-publication recovery key", normalized_run_state)
        self.assertIn("candidate SHA changes before publication do not create another reservation", normalized_run_state)
        self.assertIn("later PR updates never reuse it", normalized_run_state)
        self.assertIn("Reusing an existing draft PR follows the same reservation and proof", normalized_run_state)
        self.assertIn("represents obtaining the eventual first PR, not one transport attempt", normalized_run_state)
        self.assertIn("leave the operation `pending`", normalized_run_state)
        self.assertIn("Do not finish that retryable outcome as `not-applied`", normalized_run_state)
        self.assertIn("is terminal for that exact run and prohibits a later publication retry", normalized_run_state)
        self.assertIn("An ambiguous attempt becomes `unknown`", normalized_run_state)
        self.assertIn("reconcile a pending or `unknown` first-publication reservation", normalized_run_state)
        self.assertIn("immutable `applied` receipt and readback", normalized_run_state)
        self.assertIn("Never infer the handoff from a PR URL alone", normalized_run_state)
        self.assertIn("evaluates the first-publication operation before the assignment checkpoint", normalized_run_state)
        self.assertIn("`active @ native-review` may remain the coarse last durable pair", normalized_run_state)
        self.assertIn("routes the assignment to stack reconciliation under hosted authority", normalized_run_state)
        self.assertIn("resume at `stack-reconcile`, never at native review", normalized_reference)
        self.assertIn("this pair is only the coarse pre-stack durable checkpoint", normalized_states)
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
