from __future__ import annotations

import ast
import hashlib
import importlib.machinery
import importlib.util
import re
import statistics
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]

CONTROL_PLANE_BUDGET_SECONDS = {
    "title-or-goal": 60,
    "queued-identity": 120,
}
CONTROL_PLANE_NOTICE_AFTER_SECONDS = 10
CONTROL_PLANE_WAIT_SLICE_SECONDS = 30
TITLE_QUIET_SECONDS = 5
SAFE_CONTROL_PLANE_RETRIES = {"read", "exact-title-write"}
UNSAFE_CONTROL_PLANE_RETRIES = {
    "create-thread",
    "steer-or-message",
    "create-goal",
    "update-goal",
}

VISIBLE_REPORT_FIELDS = (
    "lifecycle",
    "state",
    "outcome",
    "attention_reason",
    "blocker_identity",
    "approval_identity",
    "failure_identity",
    "next_action",
    "deadline_risk",
    "freshness_state",
    "revision_identity",
    "pr_identity",
    "review_identity",
    "ci_identity",
    "mergeability_identity",
    "evidence_identity",
    "claim_loss",
    "monitor_degraded",
    "terminal_state",
    "closeout_state",
)


def visible_report_transcript(
    observations: list[dict[str, object]],
    *,
    cached_fingerprint: tuple[object, ...] | None = None,
) -> tuple[list[str], list[str]]:
    """Model visible dedup separately from durable observation application."""

    last_fingerprint = cached_fingerprint
    pending_cycle: int | None = None
    pending_fingerprint: tuple[object, ...] | None = None
    packets: list[str] = []
    applied_events: list[str] = []
    app_delay_notice = False

    def flush_pending() -> None:
        nonlocal last_fingerprint, pending_cycle, pending_fingerprint
        if pending_fingerprint is not None:
            packets.append("delta")
            last_fingerprint = pending_fingerprint
        pending_cycle = None
        pending_fingerprint = None

    for observation in observations:
        cycle = int(observation["cycle"])
        if pending_cycle is not None and cycle != pending_cycle:
            flush_pending()
        applied_events.append(str(observation["event"]))

        if observation.get("app_delay") and not app_delay_notice:
            packets.append("app-delay")
            app_delay_notice = True

        if observation.get("heartbeat"):
            continue
        if observation.get("freshness") != "fresh":
            if observation.get("freshness_blocker"):
                packets.append("attention")
            continue

        fingerprint = tuple(observation.get(field) for field in VISIBLE_REPORT_FIELDS)
        if observation.get("urgent"):
            flush_pending()
            packets.append("urgent")
            last_fingerprint = fingerprint
        elif last_fingerprint is None:
            flush_pending()
            packets.append("snapshot")
            last_fingerprint = fingerprint
        elif fingerprint != last_fingerprint:
            pending_cycle = cycle
            pending_fingerprint = fingerprint

    flush_pending()
    return packets, applied_events


def progress_observation(
    *, event: str, cycle: int, **changes: object
) -> dict[str, object]:
    observation: dict[str, object] = {
        "event": event,
        "cycle": cycle,
        "freshness": "fresh",
        **{field: None for field in VISIBLE_REPORT_FIELDS},
    }
    observation.update(changes)
    return observation


def within_control_plane_budget(
    *, first_attempt_at: int, observed_at: int, operation: str
) -> bool:
    return observed_at - first_attempt_at <= CONTROL_PLANE_BUDGET_SECONDS[operation]


def clipped_control_plane_wait(
    *, first_attempt_at: int, now: int, operation: str
) -> int:
    remaining = CONTROL_PLANE_BUDGET_SECONDS[operation] - (now - first_attempt_at)
    return min(CONTROL_PLANE_WAIT_SLICE_SECONDS, max(0, remaining))


def control_plane_notice_count(
    *, first_attempt_at: int, observations: list[int]
) -> int:
    return min(
        1,
        sum(
            observed_at - first_attempt_at >= CONTROL_PLANE_NOTICE_AFTER_SECONDS
            for observed_at in observations
        ),
    )


def title_stabilized(
    *, first_attempt_at: int, desired: str, observations: list[tuple[int, str]]
) -> bool:
    previous_match_at: int | None = None
    for observed_at, title in observations:
        if not within_control_plane_budget(
            first_attempt_at=first_attempt_at,
            observed_at=observed_at,
            operation="title-or-goal",
        ):
            return False
        if title != desired:
            previous_match_at = None
            continue
        if (
            previous_match_at is not None
            and observed_at - previous_match_at >= TITLE_QUIET_SECONDS
        ):
            return True
        previous_match_at = observed_at
    return False


def reconcile_ambiguous_goal(
    *, expected_objective: str, expected_state: str, readback: tuple[str, str] | None
) -> str:
    if readback == (expected_objective, expected_state):
        return "matching-readback"
    return "needs-owner"


def resumed_control_plane_budget(*, deadline_origin_available: bool) -> str:
    return "continue-original" if deadline_origin_available else "exhausted"


def resumed_notice_action(*, notice_history: bool | None) -> str:
    return "eligible" if notice_history is False else "suppress"


def recovery_title_route(observation: str) -> tuple[str, bool]:
    return "exact-derived-title", observation in {
        "delayed",
        "ambiguous",
        "overwritten",
    }


def run_app_preclaim_fixture(
    *,
    surface_available: bool,
    permission: str,
    bundle_ready: bool,
    goal_surface_available: bool = True,
    root_goal_state: str | None = None,
) -> tuple[str, list[str], list[str]]:
    observations = ["surface"]
    mutations: list[str] = []
    if not surface_available or not goal_surface_available:
        return "unsupported-runtime", observations, mutations
    if root_goal_state == "blocked":
        return "new-root-required", observations, mutations
    observations.extend(["snapshot", "delivery-preflight", "intake"])
    if not bundle_ready:
        return "planning-required", observations, mutations
    observations.append("authorization")
    if permission != "granted":
        return "permission-denied", observations, mutations
    mutations.extend(
        [
            "atomic-claim",
            "cache-retention",
            "run-state-create",
            "root-task-title",
            "portfolio-goal",
        ]
    )
    return "accepted", observations, mutations


def derive_root_task_title(registry_rows: list[dict[str, bool]]) -> str:
    total_spec_count = sum(
        row["implementation_eligible"] for row in registry_rows
    )
    if total_spec_count == 0:
        raise ValueError("no executable Feature Spec")
    if total_spec_count == 1:
        return "👨🏻‍💻 Feature Orchestrator"
    return "👨🏻‍💻 Multi-Feature Orchestrator"


def derive_provider_timeout_seconds(*, wait_deadline: int, wait_invoked_at: int) -> int:
    remaining = wait_deadline - wait_invoked_at
    return max(0, remaining)


def run_root_title_registration_fixture(
    registry_rows: list[dict[str, bool]],
    *,
    stop_after: str | None = None,
) -> tuple[dict[str, object], list[str]]:
    desired = derive_root_task_title(registry_rows)
    transitions = [
        "claim",
        "cache",
        "run-state-registry",
        "persist-desired-title",
    ]
    state: dict[str, object] = {
        "claim_retained": True,
        "root_task_title": desired,
        "root_task_title_evidence_ref": "pending",
        "live_title": "previous title",
        "portfolio_goal_state": "pending",
        "goal_registered": False,
        "dispatched": False,
    }
    if stop_after == "before-mutation":
        return state, transitions

    transitions.append("set-title")
    state["live_title"] = desired
    if stop_after == "after-mutation":
        return state, transitions
    if stop_after == "observation-failure":
        transitions.append("observe-title-failed")
        return state, transitions
    if stop_after is not None:
        raise ValueError(f"unknown stop_after: {stop_after}")

    transitions.extend(["observe-title", "persist-title-evidence"])
    state["root_task_title_evidence_ref"] = f"observed:{desired}"
    transitions.append("portfolio-goal")
    state["portfolio_goal_state"] = "active"
    state["goal_registered"] = True
    transitions.append("dispatch")
    state["dispatched"] = True
    return state, transitions


def recover_root_title_fixture(
    registry_rows: list[dict[str, bool]],
    *,
    live_title: str,
    portfolio_goal_state: str,
    recorded_title: str | None = None,
    evidence_ref: str | None = None,
) -> tuple[dict[str, object], list[str]]:
    desired = derive_root_task_title(registry_rows)
    expected_evidence = f"observed:{desired}"
    transitions = ["freshness-pass"]
    if (
        recorded_title != desired
        or evidence_ref != expected_evidence
        or live_title != desired
    ):
        transitions.append("persist-desired-title")
        evidence_ref = "pending"
    if live_title != desired:
        transitions.append("set-title")
        live_title = desired
    transitions.extend(["observe-title", "persist-title-evidence"])
    evidence_ref = expected_evidence
    return (
        {
            "claim_retained": True,
            "root_task_title": desired,
            "root_task_title_evidence_ref": evidence_ref,
            "live_title": live_title,
            "portfolio_goal_state": portfolio_goal_state,
        },
        transitions,
    )


def terminal_release_allowed(
    state: dict[str, object],
    *,
    goals_complete: bool,
    gates_complete: bool,
) -> bool:
    desired = state["root_task_title"]
    return (
        goals_complete
        and gates_complete
        and state["portfolio_goal_state"] == "complete"
        and state["live_title"] == desired
        and state["root_task_title_evidence_ref"] == f"observed:{desired}"
    )


class ImplementFeatureContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text()

    def controller_runtime(self):
        loader = importlib.machinery.SourceFileLoader(
            "implement_feature_ledger_cache_contract",
            str(ROOT / "scripts/ledger-cache"),
        )
        spec = importlib.util.spec_from_loader(loader.name, loader)
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        return module

    def test_gitstack_owns_one_shared_review_mutation_protocol(self) -> None:
        helper = self.read("scripts/ledger-cache")
        owner = self.read("../../plugins/gitstack/projects/gitstack/src/gitstack/review_operation.py")
        self.assertIn("gitstack-review-operation-request:v1", owner)
        self.assertIn("validate_result_for_request", owner)
        self.assertIn('"gitstack": Path(', helper)
        self.assertNotIn("review_mutation", helper)
        self.assertNotIn("RESERVATION_FIELDS", helper)
        self.assertNotIn("MUTATION_KINDS", helper)

    def test_worker_action_guard_matrix_names_durable_owners(self) -> None:
        run_state = self.read("references/run-state.md")
        worker = self.read("references/worker.md")
        packets = self.read("references/packets-closeout.md")
        autoreview = self.read("references/autoreview-fix-loop.md")
        authority = self.read("references/review-mutation-authority.md")
        for token in (
            "GitStack 6.0.0",
            "`request`, `wait`, `warning`, `reply`, `resolve`",
            "`owned-operation-started`",
            "single-use",
            "`reconcile-required`",
            "`operation read-start`",
            "opaque evidence",
        ):
            self.assertIn(token, authority)
        self.assertIn("references/review-mutation-authority.md", self.read("scripts/ledger-cache"))
        self.assertIn("task-sealed", packets)
        self.assertIn("AutoReview 3.0.0", autoreview)
        self.assertNotIn("review-provider-mutation-observed", packets)
        self.assertNotIn("autoreview-attempt-observed", packets)

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
            "scripts/delivery-preflight",
            "scripts/ledger-cache",
            "references/options.md",
            "references/task-model-policy.md",
            "references/cache-lifecycle.md",
            "references/run-state.md",
            "references/packets-registration.md",
            "references/packets-task.md",
            "references/packets-gates.md",
            "references/packets-closeout.md",
            "references/worker.md",
            "references/gates.md",
            "references/spec-backed-delivery.md",
            "references/codex-review-closeout.md",
            "references/review-mutation-authority.md",
            "references/review-reconciliation.md",
            "references/recovery-validation.md",
            "references/multi-repo-workspace.md",
            "references/baseline-validation.md",
        }
        self.assertTrue(all((ROOT / path).is_file() for path in required))
        self.assertFalse((ROOT / "references/stacked-feature-specs.md").exists())
        for removed in (
            "references/ledger.md",
            "references/ledger-template.md",
            "references/runtime-efficiency.md",
        ):
            self.assertFalse((ROOT / removed).exists(), removed)

    def test_runtime_surface_then_read_only_intake_precede_authorization(self) -> None:
        skill = self.read("SKILL.md")
        bootstrap = self.read("references/root-bootstrap.md")
        surface = skill.index("Before reading sources or asking permission")
        intake = bootstrap.index("## Snapshot, Preflight, And Intake")
        authorization = bootstrap.index("## Authorization, Claim, And Registration")
        controller = skill.index("## Post-Registration Controller Loop")

        self.assertLess(surface, controller)
        self.assertLess(intake, authorization)
        self.assertLess(authorization, len(bootstrap))
        surface_text = " ".join(skill[:controller].split())
        self.assertIn("Before reading sources or asking permission", surface_text)
        self.assertIn("visible App task creation", surface_text)
        self.assertIn("App-managed worktree binding", surface_text)
        self.assertIn("Before reading sources or asking permission", surface_text)
        self.assertIn("only phase router", " ".join(skill[controller:].split()))
        self.assertLess(surface, controller)
        self.assertLess(intake, authorization)

        recovery = " ".join(
            self.read("references/recovery-validation.md").split()
        )
        self.assertIn("Before reading run state", recovery)
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
                "granted",
                "denied",
            ):
                self.assertIn(value, row)
        self.assertIn("This file owns every user-controlled App orchestration field", options)

    def test_standard_authorization_resolution_and_prompt_are_exact(self) -> None:
        skill = self.read("SKILL.md")
        options = self.read("references/options.md")
        disclosure = (
            "Each executable Feature Spec is one feature; one plan may create "
            "multiple visible tasks. The scope summary immediately below lists "
            "every repository, writable path, and validation command covered by "
            "this one grant. Before any code change, baseline-only tasks run "
            "deterministic read-only validation; the root Goal starts only after "
            "every baseline is accepted together. This run may change and validate code, push "
            "commits, create or update pull requests, address "
            "Codex review, wait for CI when a repository has CI configured, "
            "prepare hosted issue closeout, and move, "
            "commit, and push completed local issue files when used. AutoReview "
            "sends Git status, staged/unstaged diffs, and every non-ignored "
            "untracked file to Codex; no extra authorization. Tasks use "
            "`gpt-5.6-sol`: `medium` by default, `high` for complex multi-part "
            "work, and `xhigh` for risky or cross-system work. Codex waits up to "
            "45 minutes for each requested review. If a review is still pending "
            "at that deadline, it records a persistent warning on the pull request, "
            "reports the warning to you, and continues the remaining gates without "
            "treating the review as clean. A later merge workflow must check for "
            "late findings. After Codex reserves "
            "the work, it automatically deletes valid run-state archives older "
            "than 180 days; it never plans, expands scope, merges, releases, or "
            "deploys."
        )
        prompt = (
            "Start implementation? Codex will create one visible task per feature "
            "and prepare merge-ready pull requests."
        )

        normalized_skill = " ".join(skill.split())
        normalized_options = " ".join(
            line.removeprefix("> ") for line in options.splitlines()
        )
        normalized_options = " ".join(normalized_options.split())
        self.assertIn("exact disclosure and authorization resolution", normalized_skill)
        self.assertIn(
            "imperative owner invocation that explicitly directs `$implement-feature`",
            normalized_skill,
        )
        self.assertIn(disclosure, normalized_options)
        self.assertIn("## Invocation Resolution", options)
        self.assertIn(
            "directly orders it to implement or execute an identified durable "
            "Feature Spec or bundle",
            normalized_options,
        )
        self.assertIn(
            "do not call `request_user_input`; continue to CLAIM",
            normalized_options,
        )
        self.assertIn(
            "merely permits tasks, workers, delegation, or subagents",
            normalized_options,
        )
        self.assertIn("| Header | `Start work?` |", options)
        self.assertIn(
            "| Question id | `visible_app_task_permission` |", options
        )
        self.assertIn(f"| Question | {prompt} |", options)
        self.assertIn(
            "| 1 | `Start implementation (Recommended)` | Use this workflow "
            "for the ready specs found in this run. | "
            "`granted` |",
            options,
        )
        self.assertIn(
            "| 2 | `Cancel` | Stop here without starting implementation or "
            "changing anything. | "
            "`denied` |",
            options,
        )
        fixed_answers = re.findall(r"^\| ([12]) \|", options, re.MULTILINE)
        self.assertEqual(fixed_answers, ["1", "2"])
        self.assertIn("The App owns the free-form", options)
        self.assertIn("never an implicit grant", normalized_options)
        self.assertLessEqual(len(prompt), 140)
        self.assertIn("one visible task per feature", prompt)
        self.assertNotIn("CLAIM", prompt)
        self.assertNotIn("executable", prompt)
        self.assertNotIn("(", prompt)

    def test_visible_task_model_policy_is_canonical_bounded_and_recoverable(self) -> None:
        skill = self.read("SKILL.md") + self.read("references/root-bootstrap.md")
        policy = self.read("references/task-model-policy.md")
        options = self.read("references/options.md")
        worker = self.read("references/worker.md") + self.read("references/worker-implementation.md") + self.read("references/worker-validation.md") + self.read("references/worker-publication.md") + self.read("references/worker-review-fix.md") + self.read("references/worker-closeout.md")
        packets = self.read("references/packets-registration.md")
        recovery = self.read("references/recovery-validation.md")

        def values(field: str) -> list[str]:
            row = next(
                line
                for line in policy.splitlines()
                if line.startswith(f"| `{field}` |")
            )
            return re.findall(r"`([^`]+)`", row)[1:]

        self.assertEqual(values("model"), ["gpt-5.6-sol"])
        self.assertEqual(values("thinking_default"), ["medium"])
        self.assertEqual(
            values("thinking_allowed"), ["medium", "high", "xhigh"]
        )
        for excluded in ("none", "minimal", "low", "max", "ultra"):
            self.assertIn(f"`{excluded}`", policy)
        self.assertIn("Never pass", policy)

        authorization = " ".join(self.read("references/root-bootstrap.md").split())
        self.assertIn("task-model-policy.md", authorization)
        self.assertIn("fixed model profiles", authorization)
        self.assertIn("repository and path scope", authorization)
        self.assertIn("not another user-controlled field", options)

        for text in (policy, worker):
            self.assertIn("codex_app__create_thread", text)
            self.assertIn("codex_app__send_message_to_thread", text)
        self.assertIn("Never omit", policy)
        self.assertIn("never reclassify", policy)
        self.assertIn("`planning-required`", policy)

        for field in ("task_model", "task_thinking", "thinking_reason"):
            self.assertIn(field, packets)
        normalized_recovery = " ".join(recovery.split())
        self.assertIn("every recorded per-Spec profile", normalized_recovery)
        self.assertIn(
            "Resume only the original visible task with its recorded profile",
            normalized_recovery,
        )

    def test_visible_task_title_is_required_semantic_and_recoverable(self) -> None:
        skill = self.read("SKILL.md")
        worker = self.read("references/worker.md") + self.read("references/worker-publication.md") + self.read("references/worker-closeout.md")
        run_state = self.read("references/run-state.md")
        packets = self.read("references/packets-registration.md")
        task_packets = self.read("references/packets-task.md")
        recovery = self.read("references/recovery-validation.md")
        options = self.read("references/options.md")
        claim_helper = self.read("scripts/active-root-claim")
        compact_run_state = " ".join(run_state.split())

        surface = " ".join(skill.split("## Immutable Safety Contract", 1)[0].split())
        for token in (
             "`create_goal`",
            "`get_goal`",
            "`update_goal`",
            "Before reading sources or asking permission",
            "unsupported-runtime",
        ):
            self.assertIn(token, surface)

        self.assertIn("codex_app__set_thread_title", worker)
        self.assertIn("observe the exact live title", " ".join(worker.split()))

        title_contract = worker.split("## Identity And Assignment", 1)[1].split(
            "## Managed Workspace", 1
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
            "Never create another task",
        ):
            self.assertIn(token, compact_title_contract)
        self.assertLess(
            compact_title_contract.index("Derive and persist `task_title`"),
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

        self.assertIn("task_title", task_packets)
        self.assertIn(
            "Source, task, profile, repository, dependency, delivery, and claim scope are immutable",
            " ".join(packets.split()),
        )
        self.assertIn("never display titles", compact_run_state)
        normalized_recovery = " ".join(recovery.split())
        self.assertIn("Record live title drift without repairing it", normalized_recovery)
        self.assertIn("Only after the full pass succeeds", normalized_recovery)
        self.assertIn(
            "require exact source assignment, task ref, exact derived display title",
            normalized_recovery,
        )
        self.assertIn(
            "Only if that exact title or identity observation is delayed",
            normalized_recovery,
        )
        self.assertIn("preserve a later explicit user title", normalized_recovery)
        self.assertNotIn("task_title", options)
        self.assertNotIn('"task_title"', claim_helper)

    def test_app_control_plane_delay_policy_is_bounded_and_fail_closed(self) -> None:
        contract = self.read("references/app-control-plane-delays.md")
        skill = self.read("references/root-bootstrap.md")
        worker = self.read("scripts/ledger-cache")
        recovery = self.read("scripts/ledger-cache")
        options = self.read("references/options.md")
        packets = self.read("references/packets-registration.md")
        cache_helper = self.read("scripts/ledger-cache")

        self.assertLessEqual(len(contract.encode("utf-8")), 4_096)
        for routed in (skill, worker, recovery):
            self.assertIn("app-control-plane-delays.md", routed)

        baseline_accept = " ".join(packets.split())
        goal_route = " ".join((cache_helper + contract).split())
        terminal_goal = " ".join(contract.split())
        self.assertIn("references/app-control-plane-delays.md", goal_route)
        self.assertIn(
            "root Goal evidence is delayed or ambiguous",
            goal_route,
        )
        register = " ".join(skill.split())
        self.assertIn("set and observe the derived root title", register)
        self.assertIn("call `create_goal` once", baseline_accept)
        self.assertIn("verify it through `get_goal`", baseline_accept)
        self.assertIn("Goal objective/state", terminal_goal)

        recovery_cases = (
            ("exact", False),
            ("delayed", True),
            ("ambiguous", True),
            ("overwritten", True),
        )
        for observation, edge_loaded in recovery_cases:
            with self.subTest(recovery_observation=observation):
                title_rule, actual_edge_loaded = recovery_title_route(observation)
                self.assertEqual(title_rule, "exact-derived-title")
                self.assertEqual(actual_edge_loaded, edge_loaded)

        timing_cases = (
            ("title-or-goal", 100, 160, True),
            ("title-or-goal", 100, 161, False),
            ("queued-identity", 100, 220, True),
            ("queued-identity", 100, 221, False),
        )
        for operation, first_attempt, observed_at, expected in timing_cases:
            with self.subTest(operation=operation, observed_at=observed_at):
                self.assertEqual(
                    within_control_plane_budget(
                        first_attempt_at=first_attempt,
                        observed_at=observed_at,
                        operation=operation,
                    ),
                    expected,
                )

        self.assertEqual(
            clipped_control_plane_wait(
                first_attempt_at=100, now=105, operation="title-or-goal"
            ),
            30,
        )
        self.assertEqual(
            clipped_control_plane_wait(
                first_attempt_at=100, now=159, operation="title-or-goal"
            ),
            1,
        )
        self.assertEqual(
            clipped_control_plane_wait(
                first_attempt_at=100, now=161, operation="title-or-goal"
            ),
            0,
        )
        self.assertEqual(
            control_plane_notice_count(
                first_attempt_at=100, observations=[105, 110, 120, 159]
            ),
            1,
        )
        self.assertEqual(
            control_plane_notice_count(first_attempt_at=100, observations=[105, 109]),
            0,
        )
        self.assertEqual(
            resumed_control_plane_budget(deadline_origin_available=True),
            "continue-original",
        )
        self.assertEqual(
            resumed_control_plane_budget(deadline_origin_available=False),
            "exhausted",
        )
        self.assertEqual(resumed_notice_action(notice_history=False), "eligible")
        self.assertEqual(resumed_notice_action(notice_history=True), "suppress")
        self.assertEqual(resumed_notice_action(notice_history=None), "suppress")

        title_cases = (
            ([(0, "generated"), (5, "wanted"), (10, "wanted")], True),
            ([(0, "wanted"), (5, "generated"), (10, "wanted")], False),
            ([(55, "wanted"), (60, "wanted")], True),
            ([(56, "wanted"), (61, "wanted")], False),
        )
        for observations, expected in title_cases:
            with self.subTest(observations=observations):
                self.assertEqual(
                    title_stabilized(
                        first_attempt_at=0,
                        desired="wanted",
                        observations=observations,
                    ),
                    expected,
                )

        self.assertEqual(
            reconcile_ambiguous_goal(
                expected_objective="deliver",
                expected_state="active",
                readback=("deliver", "active"),
            ),
            "matching-readback",
        )
        for readback in (None, ("other", "active"), ("deliver", "complete")):
            with self.subTest(readback=readback):
                self.assertEqual(
                    reconcile_ambiguous_goal(
                        expected_objective="deliver",
                        expected_state="active",
                        readback=readback,
                    ),
                    "needs-owner",
                )

        normalized = " ".join(contract.split())
        for token in (
            "monotonic clock from the first operation attempt",
            "never reset it",
            "at most one concise notice",
            "same live controller or exact durable App/tool history",
            "deadline origin is unavailable, treat the budget as exhausted",
            "notice history is unavailable, suppress another notice",
            "exact creation exposes `(hostId, threadId)`",
            "Titles, timestamps",
            "Only a direct full `read_thread` page chain",
            "never compared",
            "not worker inactivity",
            "call `create_goal` exactly once",
            "never blindly retry",
            "explicit user title, persisted parent title, then generated title",
            "zero workflow mutations",
            "existing `needs-owner` handling",
        ):
            self.assertIn(token, normalized)
        retry_tokens = {
            "read": "Safe retries are limited to reads",
            "exact-title-write": "exact same `(hostId, threadId, persisted_title)` title write",
            "create-thread": "Never retry `create_thread`",
            "steer-or-message": "steering or message calls",
            "create-goal": "`create_goal`",
            "update-goal": "`update_goal`",
        }
        for operation in SAFE_CONTROL_PLANE_RETRIES | UNSAFE_CONTROL_PLANE_RETRIES:
            self.assertIn(retry_tokens[operation], normalized)

        self.assertNotIn("control-plane-delayed", options)
        self.assertNotIn("control-plane-delayed", packets)
        self.assertNotIn("control-plane-delayed", cache_helper)
        self.assertNotIn("control-plane", options)
        self.assertNotIn("control-plane", packets)

        self.assertIn('__version__ = "23.0.0"', cache_helper)
        self.assertIn('LEDGER_SCHEMA_VERSION = "15.0.0"', cache_helper)
        self.assertIn(
            '__version__ = "5.0.0"', self.read("scripts/execution-manifest")
        )
        self.assertIn(
            'VERSION = "3.0.0"',
            (REPO / "skills/autoreview/scripts/autoreview").read_text(),
        )
        self.assertIn(
            'PROTOCOL_VERSION = "2.0.0"',
            (REPO / "skills/autoreview/scripts/autoreview_protocol.py").read_text(),
        )
        self.assertIn(
            '__version__ = "6.0.0"',
            (
                REPO
                / "plugins/gitstack/projects/gitstack/src/gitstack/__init__.py"
            ).read_text(),
        )

    def test_removed_standalone_autoreview_projection_route_has_no_runtime_references(self) -> None:
        runtime_paths = [
            REPO / "skills/implement-feature/SKILL.md",
            REPO / "skills/autoreview/SKILL.md",
            *sorted((REPO / "skills/implement-feature/references").glob("*.md")),
            *sorted((REPO / "skills/autoreview/references").glob("*.md")),
            REPO / "skills/implement-feature/scripts/ledger-cache",
            REPO / "skills/autoreview/scripts/autoreview",
        ]
        for path in runtime_paths:
            content = path.read_text()
            self.assertNotIn("ledger-cache autoreview next", content, str(path))
            self.assertNotIn("autoreview.next", content, str(path))

    def test_owned_operation_hard_cut_has_no_legacy_controller_routes_or_owner_field_registries(self) -> None:
        helper = self.read("scripts/ledger-cache")
        runtime = re.sub(
            r"RETIRED_MANAGED_EVENT_TYPES = \{.*?\}\n",
            "",
            helper,
            flags=re.DOTALL,
        )
        controller = self.read("references/controller.md")
        for retired in (
            '"reserve-autoreview-action"', '"launch-autoreview-action"',
            '"request-codex-review"', '"invoke-review-wait"',
            '"reconcile-review-wait"', '"reconcile-provider-mutation"',
            '"autoreview_projection"', '"reservation_event"',
        ):
            self.assertNotIn(retired, helper)
        self.assertIn('CONTROLLER_PROJECTION_SCHEMA_VERSION = "3.0.0"', helper)
        self.assertIn('CONTROLLER_TEMPLATE_SCHEMA_VERSION = "3.0.0"', helper)
        self.assertIn('LEDGER_SCHEMA_VERSION = "15.0.0"', helper)
        self.assertIn('__version__ = "23.0.0"', helper)
        self.assertIn('REGISTRATION_SCHEMA_VERSION = "10.0.0"', helper)
        self.assertIn("owned-operation-started", helper)
        self.assertIn("validate_owned_artifact", helper)
        for retired_runtime in (
            "review-authority",
            "review_mutation",
            "autoreview_protocol",
            "AUTOREVIEW_PROTOCOL",
            "review_provider_mutations",
            "autoreview_reservation",
            "autoreview_attempts",
            "committed_revision",
            "current_review",
            'if event_type == "review-wait',
            'if event_type == "review-provider-mutation',
            'if event_type == "autoreview-action-reserved',
            'if event_type == "autoreview-attempt-observed',
            'if event_type == "autoreview-observed',
        ):
            self.assertNotIn(retired_runtime, runtime)
        self.assertNotIn("result_event_types", controller.split("## Owned action registry", 1)[0])
        for owner_field in ("request_receipt", "reply_receipt", "resolution_receipt", "attempt_journal", "model_launch_count"):
            self.assertNotIn(owner_field, controller)

    def test_visible_progress_dedup_is_transient_post_reconciliation_and_bounded(
        self,
    ) -> None:
        worker = " ".join(self.read("references/worker.md").split())
        skill = " ".join(self.read("SKILL.md").split())
        for token in (
            "presentation-only:",
            "required full reads",
            "freshness validation",
            "ledger reconciliation",
            "event application",
            "never suppress `task-observed`",
            "transient root fingerprint",
            "cache loss permits one",
            "closed fingerprint",
            "Wording-only changes are not material",
            "Stale/out-of-order/ambiguous input",
            "authoritative observation/reconciliation cycle",
            "never wait",
            "one-shot 10-second App-delay notice",
            "at most one concise liveness line per 60 seconds",
            "no worker packet/event",
            "Claim/execution/provider heartbeats stay internal",
            "Full snapshots retain task assignment evidence",
        ):
            self.assertIn(token, worker)
        self.assertIn("presentation-only", worker)
        self.assertIn("event application", worker)
        self.assertIn("never suppress", worker)

        baseline = progress_observation(
            event="task-observed-1",
            cycle=0,
            lifecycle="active",
            state="waiting",
            next_action="poll",
        )
        repeated = dict(baseline)
        repeated.update(
            event="task-observed-2",
            observed_at="later",
            elapsed_seconds=60,
            poll_count=4,
            pid=123,
            process_cpu=0.1,
            repeated_output="still waiting",
            static_paths=["same/path"],
        )
        packets, applied = visible_report_transcript([baseline, repeated])
        self.assertEqual(packets, ["snapshot"])
        self.assertEqual(applied, ["task-observed-1", "task-observed-2"])

        field_trace = [baseline]
        for index, field in enumerate(VISIBLE_REPORT_FIELDS, start=1):
            field_trace.append(
                progress_observation(
                    event=f"task-observed-{index + 2}",
                    cycle=index,
                    **{field: f"changed-{index}"},
                )
            )
        field_packets, _ = visible_report_transcript(field_trace)
        self.assertEqual(field_packets, ["snapshot"] + ["delta"] * len(VISIBLE_REPORT_FIELDS))

        stale = progress_observation(
            event="task-observed-stale",
            cycle=1,
            freshness="stale",
            state="failed",
        )
        stale_blocker = dict(stale)
        stale_blocker.update(
            event="task-observed-stale-blocker",
            freshness_blocker=True,
            attention_reason="stale evidence",
        )
        stale_packets, _ = visible_report_transcript(
            [baseline, stale, stale_blocker, dict(baseline, event="task-observed-3", cycle=2)]
        )
        self.assertEqual(stale_packets, ["snapshot", "attention"])

        same_cycle = [
            baseline,
            progress_observation(event="task-observed-4", cycle=1, state="running"),
            progress_observation(event="task-observed-5", cycle=1, state="reviewing"),
            progress_observation(event="task-observed-6", cycle=2, state="complete"),
        ]
        same_cycle_packets, _ = visible_report_transcript(same_cycle)
        self.assertEqual(same_cycle_packets, ["snapshot", "delta", "delta"])

        urgent = progress_observation(
            event="task-observed-urgent",
            cycle=1,
            approval_identity="approval-1",
            urgent=True,
        )
        urgent_packets, _ = visible_report_transcript(
            [baseline, progress_observation(event="task-observed-7", cycle=1, state="running"), urgent]
        )
        self.assertEqual(urgent_packets, ["snapshot", "delta", "urgent"])

        cached = tuple(baseline.get(field) for field in VISIBLE_REPORT_FIELDS)
        self.assertEqual(
            visible_report_transcript([baseline], cached_fingerprint=cached)[0],
            [],
        )
        self.assertEqual(visible_report_transcript([baseline])[0], ["snapshot"])

        delay_trace = [
            baseline,
            dict(baseline, event="task-observed-delay-1", app_delay=True),
            dict(baseline, event="task-observed-delay-2", app_delay=True),
        ]
        delay_packets, _ = visible_report_transcript(delay_trace)
        self.assertEqual(delay_packets, ["snapshot", "app-delay"])

        heartbeat_packets, heartbeat_events = visible_report_transcript(
            [baseline, dict(baseline, event="claim-heartbeat", heartbeat=True)]
        )
        self.assertEqual(heartbeat_packets, ["snapshot"])
        self.assertEqual(heartbeat_events, ["task-observed-1", "claim-heartbeat"])

    def test_progress_reporting_preserves_versions_and_loaded_path_ceilings(self) -> None:
        skill = self.read("SKILL.md")
        worker = self.read("references/worker.md")
        prompt_match = re.search(r"## Fixed Task Prompt\n\n(.*?)\n## Report", worker, re.DOTALL)
        self.assertIsNotNone(prompt_match)
        assert prompt_match is not None
        self.assertLessEqual(len(prompt_match.group(1)), 2_033)
        self.assertLessEqual(len(skill.encode("utf-8")), 16_500)

        loaded = (
            "SKILL.md",
            "references/options.md",
            "references/task-model-policy.md",
            "references/spec-backed-delivery.md",
            "references/baseline-validation.md",
            "references/run-state.md",
            "references/packets-registration.md",
            "references/packets-task.md",
            "references/packets-gates.md",
            "references/packets-closeout.md",
            "references/cache-lifecycle.md",
            "references/worker-closeout.md",
            "references/gates.md",
            "references/codex-review-closeout.md",
        )
        sizes = lambda paths: sum(len(self.read(path).encode("utf-8")) for path in paths)
        self.assertLessEqual(sizes(loaded), 115_200)
        self.assertLessEqual(sizes(loaded + ("references/execution-manifest.md",)), 126_600)
        self.assertLessEqual(sizes(loaded + ("references/multi-repo-workspace.md",)), 119_500)
        controller_route = (
            "references/controller.md",
            "references/worker.md",
            "references/autoreview-fix-loop.md",
            "references/review-mutation-authority.md",
        )
        self.assertLess(sizes(controller_route), sizes(loaded))
        self.assertLessEqual(len(controller_route) - 1, 3)

        self.assertIn('__version__ = "23.0.0"', self.read("scripts/ledger-cache"))
        self.assertIn('LEDGER_SCHEMA_VERSION = "15.0.0"', self.read("scripts/ledger-cache"))
        self.assertIn('__version__ = "5.0.0"', self.read("scripts/execution-manifest"))
        self.assertIn('VERSION = "3.0.0"', (REPO / "skills/autoreview/scripts/autoreview").read_text())
        self.assertIn('PROTOCOL_VERSION = "2.0.0"', (REPO / "skills/autoreview/scripts/autoreview_protocol.py").read_text())
        self.assertIn('__version__ = "6.0.0"', (REPO / "plugins/gitstack/projects/gitstack/src/gitstack/__init__.py").read_text())

    def test_root_task_title_is_stable_adaptive_and_recoverable(self) -> None:
        skill = self.read("SKILL.md")
        run_state = self.read("references/run-state.md")
        packets = self.read("references/packets-registration.md")
        recovery = self.read("references/recovery-validation.md")
        worker = self.read("references/worker.md")
        options = self.read("references/options.md")
        claim_helper = self.read("scripts/active-root-claim")
        cache_helper = self.read("scripts/ledger-cache")
        delivery = self.read("references/spec-backed-delivery.md")

        executable = {"implementation_eligible": True}
        coordination_only = {"implementation_eligible": False}
        self.assertEqual(
            derive_root_task_title([executable]),
            "👨🏻‍💻 Feature Orchestrator",
        )
        for registry in (
            [executable, executable],
            [executable, executable, executable],
        ):
            self.assertEqual(
                derive_root_task_title(registry),
                "👨🏻‍💻 Multi-Feature Orchestrator",
            )
        self.assertEqual(
            derive_root_task_title([coordination_only, executable]),
            "👨🏻‍💻 Feature Orchestrator",
        )
        self.assertEqual(
            [
                derive_root_task_title(registry)
                for registry in (
                    [executable],
                    [executable, executable],
                    [executable],
                )
            ],
            [
                "👨🏻‍💻 Feature Orchestrator",
                "👨🏻‍💻 Multi-Feature Orchestrator",
                "👨🏻‍💻 Feature Orchestrator",
            ],
        )
        with self.assertRaises(ValueError):
            derive_root_task_title([coordination_only])

        contract = run_state.split("## Root Title And Portfolio Goal", 1)[1].split(
            "## Review Timing", 1
        )[0]
        compact_contract = " ".join(contract.split())
        for token in (
            "`total_spec_count`",
            "implementation-eligible Feature Spec",
            "coordination-only parent/global",
            "`👨🏻‍💻 Feature Orchestrator`",
            "`👨🏻‍💻 Multi-Feature Orchestrator`",
            "with no counter or suffix",
            "stable for the accepted run",
            "UI evidence",
            "scheduling input",
            "set and observe the calling task title",
            "`root-title-observed`",
            "`get_goal`",
            "`create_goal`",
            "`portfolio-goal-activated`",
        ):
            self.assertIn(token, compact_contract)

        self.assertIn("`portfolio-goal-completed`", self.read("references/packets-closeout.md"))

        self.assertLess(
            compact_contract.index("set and observe the calling task title"),
            compact_contract.index("atomic baseline"),
        )

        register = " ".join(self.read("references/root-bootstrap.md").split())
        for token in (
            "exact-byte snapshot",
            "execution-scope fingerprint",
            "validation-plan derivation",
            "Goal state remains internal `pending`",
        ):
            self.assertIn(token, register)

        self.assertIn("stable root title", " ".join(packets.split()))
        self.assertIn("Goal state `pending`", packets)

        compact_recovery = " ".join(recovery.split())
        for token in (
            "complete read-only pass",
            "Record live title drift without repairing it",
            "Call `get_goal` in the root",
            "Only after the full pass succeeds",
            "Repair generated-title drift only",
            "preserve a later explicit user title",
            "Never repair or resume implementation",
            "Do not infer identity from task titles",
        ):
            self.assertIn(token, compact_recovery)
        fingerprint_contract = delivery.split(
            "## Canonical Execution Contract", 1
        )[1].split("## Intake Validation", 1)[0]
        for text in (
            options,
            claim_helper,
            fingerprint_contract,
        ):
            self.assertNotIn("root_task_title", text)
            self.assertNotIn("total_spec_count", text)
        self.assertIn("root_task_title", cache_helper)
        self.assertNotIn("Root Task Display Title", worker)

        terminal_contract = " ".join(self.read("references/worker-closeout.md").split())
        closeout_order = (
            "root-title revalidation",
            "Seal each task",
            "Record its `pull-request-ready` handoff",
            "Independently reverify every task",
            "Complete the sole root Goal",
            "release the claim",
        )
        offsets = [terminal_contract.index(token) for token in closeout_order]
        self.assertEqual(offsets, sorted(offsets))

    def test_root_title_state_transitions_are_crash_safe_and_closeout_gated(
        self,
    ) -> None:
        executable = {"implementation_eligible": True}
        singular = [executable]
        plural = [executable, executable]

        success, transitions = run_root_title_registration_fixture(plural)
        self.assertEqual(
            transitions,
            [
                "claim",
                "cache",
                "run-state-registry",
                "persist-desired-title",
                "set-title",
                "observe-title",
                "persist-title-evidence",
                "portfolio-goal",
                "dispatch",
            ],
        )
        self.assertTrue(success["goal_registered"])
        self.assertTrue(success["dispatched"])

        for stop_after, last_transition in (
            ("before-mutation", "persist-desired-title"),
            ("after-mutation", "set-title"),
            ("observation-failure", "observe-title-failed"),
        ):
            with self.subTest(stop_after=stop_after):
                state, stopped = run_root_title_registration_fixture(
                    plural,
                    stop_after=stop_after,
                )
                self.assertEqual(stopped[-1], last_transition)
                self.assertEqual(
                    state["root_task_title_evidence_ref"],
                    "pending",
                )
                self.assertTrue(state["claim_retained"])
                self.assertFalse(state["goal_registered"])
                self.assertFalse(state["dispatched"])
                self.assertNotIn("portfolio-goal", stopped)
                self.assertNotIn("dispatch", stopped)

        drifted, recovery_transitions = recover_root_title_fixture(
            singular,
            live_title="manually renamed",
            portfolio_goal_state="active",
            recorded_title="👨🏻‍💻 Feature Orchestrator",
            evidence_ref="observed:stale",
        )
        self.assertEqual(
            recovery_transitions,
            [
                "freshness-pass",
                "persist-desired-title",
                "set-title",
                "observe-title",
                "persist-title-evidence",
            ],
        )
        self.assertEqual(drifted["live_title"], "👨🏻‍💻 Feature Orchestrator")

        for goal_state in ("pending", "active", "complete"):
            with self.subTest(goal_state=goal_state):
                backfilled, backfill_transitions = recover_root_title_fixture(
                    singular,
                    live_title="👨🏻‍💻 Feature Orchestrator",
                    portfolio_goal_state=goal_state,
                )
                self.assertEqual(backfill_transitions[0], "freshness-pass")
                self.assertIn("persist-desired-title", backfill_transitions)
                self.assertNotIn("set-title", backfill_transitions)
                self.assertEqual(
                    backfilled["root_task_title_evidence_ref"],
                    "observed:👨🏻‍💻 Feature Orchestrator",
                )
                self.assertEqual(backfilled["portfolio_goal_state"], goal_state)

        takeover, takeover_transitions = recover_root_title_fixture(
            plural,
            live_title="👨🏻‍💻 Feature Orchestrator",
            portfolio_goal_state="pending",
            recorded_title="👨🏻‍💻 Feature Orchestrator",
            evidence_ref="observed:👨🏻‍💻 Feature Orchestrator",
        )
        self.assertEqual(
            takeover["root_task_title"],
            "👨🏻‍💻 Multi-Feature Orchestrator",
        )
        self.assertIn("persist-desired-title", takeover_transitions)
        self.assertIn("set-title", takeover_transitions)

        terminal = dict(success)
        self.assertFalse(
            terminal_release_allowed(
                terminal,
                goals_complete=True,
                gates_complete=True,
            )
        )
        terminal["portfolio_goal_state"] = "complete"
        self.assertTrue(
            terminal_release_allowed(
                terminal,
                goals_complete=True,
                gates_complete=True,
            )
        )
        terminal["live_title"] = "manual drift"
        self.assertFalse(
            terminal_release_allowed(
                terminal,
                goals_complete=True,
                gates_complete=True,
            )
        )
        terminal["live_title"] = terminal["root_task_title"]
        terminal["root_task_title_evidence_ref"] = "pending"
        self.assertFalse(
            terminal_release_allowed(
                terminal,
                goals_complete=True,
                gates_complete=True,
            )
        )

    def test_one_consent_covers_the_complete_fixed_flow(self) -> None:
        skill = " ".join(self.read("SKILL.md").split())
        options = " ".join(
            line.removeprefix("> ")
            for line in self.read("references/options.md").splitlines()
        )
        options = " ".join(options.split())
        for token in (
            "change and validate code",
            "push commits",
            "create or update pull requests",
            "AutoReview sends Git status, staged/unstaged diffs, and every non-ignored untracked file to Codex",
            "no extra authorization",
            "address Codex review",
            "wait for CI",
            "prepare hosted issue closeout",
            "move, commit, and push completed local issue files",
            "prepare merge-ready pull requests",
            "never plans, expands scope, merges, releases, or deploys",
        ):
            self.assertIn(token, options)
        self.assertIn(
            "visible_app_task_permission=granted", skill
        )
        self.assertIn("fixed model, reasoning policy, and execution flow", options)
        self.assertIn(
            "Generic delegation, worker assignment, subagent authority, or "
            "permission to create tasks alone never supplies",
            skill,
        )

    def test_cache_maintenance_is_root_owned_bounded_and_after_claim(self) -> None:
        skill = self.read("SKILL.md")
        lifecycle = self.read("references/cache-lifecycle.md")
        normalized_lifecycle = " ".join(lifecycle.split())
        ledger = self.read("references/run-state.md")
        normalized_ledger = " ".join(ledger.split())
        controller = self.read("references/root-bootstrap.md")

        options = " ".join(
            line.removeprefix("> ")
            for line in self.read("references/options.md").splitlines()
        )
        options = " ".join(options.split())
        self.assertIn(
            "automatically deletes valid run-state archives older than 180 days",
            options,
        )
        self.assertLess(controller.index("acquire the complete portfolio claim"), controller.index("cache doctor"))
        self.assertLess(controller.index("cache doctor"), controller.index("registration packet"))
        self.assertLess(controller.index("registration packet"), controller.index("enter the controller loop"))

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
        self.assertIn("After the terminal projection passes", lifecycle)
        self.assertIn("For an in-flight review wait, retain", normalized_lifecycle)
        self.assertIn("Dependency-only waits also retain", normalized_lifecycle)
        self.assertIn("raw 64-hex", lifecycle)
        self.assertIn("never a `sha256:` value", normalized_lifecycle)
        monitoring = lifecycle.split("For an in-flight review wait", 1)[1].split("After the terminal", 1)[0]
        terminal = lifecycle.split("After the terminal projection passes", 1)[1].split("The release receipt binds", 1)[0]
        self.assertIn("do not release ownership", monitoring)
        self.assertNotIn("claim release", monitoring)
        self.assertIn("do not fabricate", monitoring)
        for token in (
            "--root-id '<root-id>'",
            "--expected-fingerprint '<claim-fingerprint>'",
            "--release-reason terminal",
            "--evidence '<terminal-evidence-ref>'",
            "--root-id '<same-root-id>'",
            "--evidence-ref '<same-terminal-evidence-ref>'",
        ):
            self.assertIn(token, terminal)
        self.assertLess(terminal.index("claim release"), terminal.index("ledger archive"))
        self.assertIn(
            "an archive-ready terminal projection before receipt or claim deletion",
            normalized_lifecycle,
        )
        self.assertIn(
            "Rejection leaves claim and ledger unchanged",
            normalized_lifecycle,
        )
        self.assertIn("bind validated JSON bytes", normalized_lifecycle)
        self.assertIn("ledger's exact terminal evidence", normalized_lifecycle)
        self.assertIn("permits only `terminal` and", lifecycle)
        self.assertIn("`preimplementation-abort`", lifecycle)
        baseline = self.read("references/baseline-validation.md")
        normalized_baseline = " ".join(baseline.split())
        abort = baseline.split("## Preimplementation Stop", 1)[1]
        self.assertLess(abort.index("task-stop evidence"), abort.index("`preimplementation-aborted`"))
        self.assertLess(abort.index("`preimplementation-aborted`"), abort.index("`set_thread_archived`"))
        preimplementation = lifecycle.split("If baseline preparation/acceptance cannot continue", 1)[1]
        self.assertLess(preimplementation.index("`preimplementation-aborted`"), preimplementation.index("`set_thread_archived`"))
        self.assertLess(preimplementation.index("`set_thread_archived`"), preimplementation.index("--release-reason preimplementation-abort"))
        self.assertIn("A fresh start is orchestration, not a ledger state", baseline)
        self.assertIn("automatically selects it without another owner question", normalized_baseline)
        self.assertIn("control-plane-unrecoverable", baseline)
        self.assertIn("not deterministic baseline", normalized_baseline)
        self.assertIn("new claim, ledger, task, and checkout identities", normalized_baseline)
        self.assertIn("new empty transient bootstrap directory", normalized_baseline)
        self.assertIn("discard and regenerate every derived registration", normalized_baseline)
        self.assertIn("never start over again automatically", normalized_baseline.lower())
        self.assertIn("Do not ask for a separate `start over`", skill)
        self.assertIn("A recoverable run still requires an explicit request", skill)
        self.assertIn("one fresh run with new identities", skill)
        self.assertIn("reuses only revalidated immutable source inputs", skill)
        self.assertIn("regenerates every derived packet", skill)
        self.assertIn("Create a new empty transient directory", " ".join(controller.split()))
        self.assertIn(
            "Never copy, reopen, or reuse derived registration JSON",
            " ".join(controller.split()),
        )
        self.assertIn("Do not require or ask for a separate `start over`", options)
        self.assertIn("still-recoverable run", options)
        packets = self.read("references/packets-task.md")
        self.assertIn("`not-bound`, `present-clean`, or `removed`", packets)
        self.assertIn("and `unavailable` for an existing task", packets)
        self.assertIn('"failed", "unavailable"', self.read("scripts/ledger-cache"))
        self.assertIn("Frozen archive-v1 entries remain readable evidence", normalized_ledger)
        self.assertIn("deterministic Markdown audit report is rendered only during archival", normalized_ledger)

    def test_fixed_worker_actions_are_not_an_option(self) -> None:
        worker = self.read("scripts/ledger-cache")
        options = self.read("references/options.md")
        self.assertIn("CONTROLLER_ACTIONS", worker)
        for action in (
            "observe-baseline-tasks",
            "steer-implementation",
            "steer-validation",
            "steer-publication",
            "steer-ready-transition",
            "steer-review-fix",
            "execute-autoreview-phase",
            "execute-gitstack-request",
            "execute-gitstack-wait",
            "execute-gitstack-warning",
            "execute-gitstack-reply",
            "execute-gitstack-resolve",
            "steer-ci",
            "steer-tracker-closeout",
            "steer-mergeability",
            "apply-current-gate-evidence",
            "record-terminal-handoff",
        ):
            self.assertIn(action, worker)
        self.assertNotIn("worker_allowed_actions", worker)
        self.assertNotIn("worker_allowed_actions", options)

    def test_review_fixes_use_target_repo_fixup_policy_without_autosquash(self) -> None:
        worker = " ".join(self.read("references/worker-review-fix.md").split())

        self.assertIn("Use `$gitstack:git-commit`", worker)
        self.assertIn("`commit_kind=regular`", worker)
        self.assertIn("target-repository instructions require one exact targeted fixup", worker)
        self.assertIn("Feedback alone never selects a fixup", worker)
        self.assertIn("`target_commit`", worker)
        self.assertIn("Never autosquash or rewrite a published branch", worker)
        self.assertIn("invalidates current-revision review and CI evidence", worker)

    def test_app_has_one_fixed_successful_conclusion_and_never_merges(self) -> None:
        runtime = self.runtime_text()
        skill = " ".join(self.read("SKILL.md").split())
        fixed = "pull-request-ready-for-merge"
        for relative in (
            "SKILL.md",
            "references/options.md",
            "references/worker-closeout.md",
            "agents/openai.yaml",
        ):
            self.assertIn(fixed, self.read(relative))
        self.assertIn("only successful task result", skill)
        self.assertIn("Never enqueue, merge", skill)
        self.assertIn("A later merge request starts a separate GitHub workflow", skill)
        self.assertNotIn("pull_request_merge_permission", runtime)
        self.assertNotIn("pull_request_merge_confirmation", runtime)

    def test_intake_uses_one_execution_contract_and_root_fingerprints(self) -> None:
        delivery = self.read("references/spec-backed-delivery.md")
        skill = " ".join(self.read("references/root-bootstrap.md").split())
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
        self.assertIn("one exact-byte snapshot", skill)
        self.assertIn("planning-required", skill)
        self.assertIn("unsupported-delivery-target", skill)
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
            self.assertNotRegex(
                runtime,
                rf"(?<![a-z0-9_]){re.escape(field)}(?![a-z0-9_])",
                field,
            )

    def test_scheduling_is_deterministic_path_disjoint_and_merge_gated(self) -> None:
        skill = " ".join(self.read("references/root-bootstrap.md").split())
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        self.assertIn("Sort ready candidates by canonical claim/task source id", skill)
        self.assertIn("`## Feature Dependencies` table", delivery)
        self.assertIn("Greedily select", skill)
        self.assertIn("remaining three-task capacity", skill)
        self.assertIn("pairwise path-disjoint", skill)
        self.assertIn("ancestor/descendant scopes as overlapping", skill)
        self.assertIn(
            "every upstream ref is merged",
            skill,
        )
        self.assertIn("merge-ready-but-unmerged is still a dependency wait", skill)
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
        self.assertIn("immutable assignment fingerprint", normalized)
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
        self.assertIn("reuse the original task", worker)
        self.assertNotIn("resumed or replaced", normalized)
        self.assertNotIn("`replaced`", self.read("references/worker.md"))

    def test_root_only_goal_tools_and_worker_assignment_are_mandatory(self) -> None:
        skill = self.read("SKILL.md")
        worker = self.read("references/worker.md")
        run_state = self.read("references/run-state.md")
        packets = self.read("references/packets-registration.md") + self.read("references/packets-closeout.md")
        recovery = self.read("references/recovery-validation.md")
        normalized_recovery = " ".join(recovery.split())

        for text in (skill, run_state, recovery):
            for tool in ("`create_goal`", "`get_goal`", "`update_goal`"):
                self.assertIn(tool, text)

        for tool in ("`create_goal`", "`get_goal`", "`update_goal`"):
            self.assertNotIn(tool, worker)

        self.assertIn("without", run_state)
        self.assertIn("`token_budget`", run_state)
        self.assertIn("exact authored Feature Spec", worker)
        self.assertIn("repositories and managed checkouts", worker)
        self.assertIn("acceptance criteria", worker)
        self.assertIn("validation", worker)
        self.assertIn("pull-request-ready-for-merge", worker)
        self.assertIn("objective_fingerprint", packets)
        self.assertIn("portfolio-goal-activated", packets)
        self.assertIn("portfolio-goal-completed", packets)
        self.assertNotIn("portfolio-goal-paused", packets)
        self.assertNotIn("review-monitoring-scheduled", packets)
        self.assertNotIn("task-monitoring-paused", packets)
        self.assertIn("goal_evidence_ref", packets)
        self.assertIn("Before any mutation, read each exact recorded task", normalized_recovery)
        self.assertIn("portfolio_goal_state=pending", recovery)
        self.assertIn("portfolio_goal_state=complete", recovery)
        self.assertIn("submits one atomic event batch", run_state)
        self.assertIn("do not adopt or create it during this pass", normalized_recovery)
        self.assertIn("Only after the full pass succeeds", normalized_recovery)
        self.assertIn("Never repair or resume implementation", normalized_recovery)
        self.assertIn("complete terminal release/archive sequence", normalized_recovery)
        self.assertIn("finish the same archive operation idempotently", normalized_recovery)
        self.assertIn("These are closeout transitions, not implementation resume", normalized_recovery)
        normalized_run_state = " ".join(run_state.split())
        self.assertIn("A different unfinished Goal is `needs-owner`", normalized_run_state)
        self.assertIn(
            "missing active Goal is never recreated during recovery",
            normalized_run_state,
        )
        normalized_worker = " ".join(worker.split())
        self.assertIn("fixed successful outcome", normalized_worker)
        self.assertIn("never wait for later evidence", normalized_worker)
        for text in (normalized_run_state, normalized_worker):
            self.assertIn("CI when configured", text)
            self.assertIn("never reuse", text.lower())
        self.assertIn("rejects unconditional-CI registration and active state", normalized_run_state)
        self.assertIn(
            'PORTFOLIO_OBJECTIVE_CI_CLAUSE = "CI when configured"',
            self.read("scripts/ledger-cache"),
        )
        self.assertIn(
            "Fresh portfolio Goal text containing exact `CI when configured`",
            packets,
        )

        surface = " ".join(skill.split("## Immutable Safety Contract", 1)[0].split())
        self.assertIn("sole lifecycle Goal", skill)
        self.assertIn("external root Goal", run_state)
        self.assertIn("Goal pause/resume and App heartbeat automation are outside", surface)
        self.assertIn("Do not create a task to inspect capabilities", surface)
        dispatch = " ".join((
            worker + self.read("references/baseline-validation.md")
        ).split())
        self.assertIn("title, assignment, and complete checkout map", dispatch)
        self.assertIn("may not edit source", dispatch)

        register = " ".join(self.read("references/root-bootstrap.md").split())
        self.assertIn("Goal state remains internal `pending`", register)
        self.assertIn("do not call `create_goal` yet", register)

        delivery = " ".join(self.read("references/worker-closeout.md").split())
        closeout_order = (
            "Seal each task",
            "Record its `pull-request-ready` handoff",
            "Independently reverify every task",
            "Complete the sole root Goal",
            "release the claim",
        )
        offsets = [delivery.index(token) for token in closeout_order]
        self.assertEqual(offsets, sorted(offsets))

        runtime = self.runtime_text()
        for retired in (
            "create the portfolio Goal or exact fallback",
            "Record an exact objective fallback only if",
            "or recorded unavailable fallback",
        ):
            self.assertNotIn(retired, runtime)

    def test_review_is_mandatory_with_one_fixed_45_minute_deadline(self) -> None:
        closeout = self.read("references/codex-review-closeout.md")
        normalized_closeout = " ".join(closeout.split())
        gates = self.read("references/gates.md")
        worker = self.read("references/worker.md")
        packets = self.read("references/packets-task.md") + self.read("references/packets-gates.md")
        runtime = self.runtime_text()
        for token in ("head SHA", "base ref", "merge-base SHA"):
            self.assertIn(token, normalized_closeout)
        self.assertIn("entire tuple matches", closeout)
        self.assertIn("immutable exact\n   45-minute deadline", closeout)
        for token in ("`pending-at-deadline`", "`warning-required`", "`warned-timeout`", "zero-timeout"):
            self.assertIn(token, normalized_closeout)
        authority = self.read("references/review-mutation-authority.md")
        self.assertIn("exactly request start plus 45 minutes", authority)
        self.assertIn("no reset", authority.lower())
        self.assertIn("`owned-operation-started`", authority)
        self.assertEqual(
            derive_provider_timeout_seconds(wait_deadline=2_700, wait_invoked_at=120),
            2_580,
        )
        self.assertEqual(
            derive_provider_timeout_seconds(wait_deadline=2_700, wait_invoked_at=2_700),
            0,
        )
        self.assertEqual(
            derive_provider_timeout_seconds(wait_deadline=2_700, wait_invoked_at=2_800),
            0,
        )
        for retired in (
            "review-monitoring-scheduled",
            "task-monitoring-paused",
            "task-monitoring-resumed",
            "portfolio-goal-paused",
            "portfolio-goal-resumed",
            "monitoring_cycle",
            "schedule_fingerprint",
        ):
            self.assertNotIn(retired, runtime)
        self.assertFalse((ROOT / "references/review-monitoring.md").exists())
        self.assertIn("Terminal Handoff Only", closeout)
        self.assertIn("Never repost a request", closeout)
        self.assertIn("Review request has no skip", gates)
        self.assertNotIn("15-minute", closeout)
        self.assertNotIn("--timeout 15m", runtime)

    def test_provider_text_transport_is_file_backed_guarded_and_scope_bounded(self) -> None:
        skill = self.read("SKILL.md")
        worker = self.read("references/worker-publication.md")
        closeout = self.read("references/codex-review-closeout.md")
        recovery = self.read("references/recovery-validation.md")
        authority = self.read("references/review-mutation-authority.md")
        normalized = " ".join((skill + worker + closeout + recovery + authority).split())

        for token in (
            "Provider Text Transport",
            "opaque UTF-8 bytes",
            "absolute regular non-symlink file",
            "`apply_patch`",
            "`--json repo snapshot`",
            "`--expected-worktree-fingerprint <fingerprint>`",
            "provider object id and URL",
            "UTF-8 byte count and SHA-256",
            "unchanged worktree fingerprint",
            "one exact-target read-back",
            "never retried blindly",
            "partial-success evidence",
            "connector response alone is not byte verification",
            "`reviews address` is read-only",
            "`publish open --title-file --body-file`",
            "GitStack has no `publish edit` command",
        ):
            self.assertIn(token, normalized)

        for forbidden_boundary in (
            "argv, an environment variable, a shell command string",
            "logs, dry-run output, or errors",
            "Inline text flags, parser aliases, generic API writes",
        ):
            self.assertIn(forbidden_boundary, normalized)

        self.assertIn("typed GitStack request operation", normalized)
        self.assertIn("does not extend `execution-manifest`", normalized)
        self.assertIn("does not define Codex review-request content", normalized)
        self.assertNotIn("reviews comment --body-file", closeout)
        self.assertIn("GitStack owns", closeout)
        self.assertIn("old snapshots and old temporary files are not recovery authority", normalized)

        unsafe = re.compile(r"--(?:title|body|description|comment)(?:=|\s+)[\"']|\s-[fF]\s+body=")
        for relative in (
            "SKILL.md",
            "references/worker.md",
            "references/codex-review-closeout.md",
            "references/recovery-validation.md",
        ):
            fences = re.findall(
                r"```(?:bash|sh)\n(.*?)```",
                self.read(relative),
                flags=re.DOTALL,
            )
            with self.subTest(relative=relative):
                self.assertFalse(any(unsafe.search(fence) for fence in fences))

    def test_ci_requires_current_head_evidence_only_when_configured(self) -> None:
        skill = " ".join(self.read("references/root-bootstrap.md").split())
        gates = " ".join(self.read("references/gates.md").split())

        self.assertIn("CI classification `configured|not-configured`", skill)
        self.assertIn("`not-configured` is valid", skill)
        self.assertIn("no artifacts", skill)
        self.assertIn("exact head SHA", gates)
        self.assertIn("only when `ci_availability=configured`", gates)
        self.assertIn("at least one applicable run or status context", gates)
        self.assertIn("When `ci_availability=not-configured`", gates)
        self.assertIn("do not emit, wait for, poll, or accept a `ci` gate", gates)
        self.assertNotIn("`ci-unavailable` blocker", gates)

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

    def test_run_state_is_typed_atomic_derived_and_a_hard_cut(self) -> None:
        run_state = self.read("references/run-state.md")
        packets = "\n".join(
            self.read(path)
            for path in (
                "references/packets-registration.md",
                "references/packets-task.md",
                "references/packets-gates.md",
                "references/packets-closeout.md",
            )
        )
        helper = self.read("scripts/ledger-cache")

        for command in ("ledger create", "ledger apply", "ledger read", "ledger archive"):
            self.assertIn(command, run_state)
        for token in (
            "direct-child `.json`",
            "expected_generation",
            "operation_id",
            "idempotent",
            "one atomic event batch",
            "deterministic projections",
            "Hard Cut",
            "no compatibility path or migration for active Markdown",
            "Frozen archive-v1 entries remain readable evidence",
        ):
            self.assertIn(token, run_state)
        self.assertIn("`ledger-cache` owns the generic envelope", packets)
        self.assertIn(
            "phase-specific inputs and evidence",
            " ".join(packets.split()),
        )
        self.assertIn('__version__ = "23.0.0"', helper)
        self.assertIn("unsupported-ledger", helper)
        self.assertNotIn("review-authority", helper)
        for removed in (
            "references/ledger.md",
            "references/ledger-template.md",
            "references/runtime-efficiency.md",
        ):
            self.assertFalse((ROOT / removed).exists())
        for retired_heading in ("## Wave Reports", "## Recovery Packet"):
            self.assertNotIn(retired_heading, run_state)

    def test_event_packet_registry_matches_the_v23_runtime(self) -> None:
        helper = self.read("scripts/ledger-cache")
        packets = "\n".join(
            self.read(path)
            for path in (
                "references/packets-registration.md",
                "references/packets-task.md",
                "references/packets-gates.md",
                "references/packets-closeout.md",
            )
        )
        run_state = " ".join(self.read("references/run-state.md").split())

        for constant in (
            '__version__ = "23.0.0"',
            'LEDGER_SCHEMA_VERSION = "15.0.0"',
            'REGISTRATION_SCHEMA_VERSION = "10.0.0"',
        ):
            self.assertIn(constant, helper)
        self.assertIn("Registration schema is exactly `10.0.0`", packets)
        self.assertIn(
            "claim-identical Git common directories",
            packets,
        )
        self.assertNotIn("run-state-packets.md", packets)
        self.assertIn("Active state accepts only ledger schema `15.0.0`", run_state)
        self.assertIn("no compatibility path or migration", run_state)

        module = ast.parse(helper)
        apply_event = next(
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef) and node.name == "apply_event"
        )
        runtime_fields: dict[str, set[str]] = {}
        for node in ast.walk(apply_event):
            if not isinstance(node, ast.If):
                continue
            test = node.test
            if not (
                isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name)
                and test.left.id == "event_type"
                and len(test.ops) == 1
                and isinstance(test.ops[0], ast.Eq)
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and isinstance(test.comparators[0].value, str)
            ):
                continue
            event_type = test.comparators[0].value
            for call in ast.walk(node):
                if not (
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Name)
                    and call.func.id == "exact_object"
                    and len(call.args) >= 2
                    and isinstance(call.args[1], ast.Set)
                ):
                    continue
                fields = {
                    item.value
                    for item in call.args[1].elts
                    if isinstance(item, ast.Constant) and isinstance(item.value, str)
                }
                if "type" in fields:
                    runtime_fields[event_type] = fields - {"type"}
                    break

        packet_fields: dict[str, set[str]] = {}
        for line in packets.splitlines():
            match = re.fullmatch(r"\| `([^`]+)` \| (.+) \|", line)
            if match:
                event_type = match.group(1)
                if event_type in runtime_fields or event_type == "command-finished":
                    self.assertNotIn(event_type, packet_fields)
                    packet_fields[event_type] = {match.group(2).strip()}
        retired = set(ast.literal_eval(next(
            node.value for node in module.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "RETIRED_MANAGED_EVENT_TYPES" for target in node.targets)
        )))
        event_types = set(ast.literal_eval(next(
            node.value for node in module.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "EVENT_TYPES" for target in node.targets)
        )))
        self.assertEqual(set(packet_fields), event_types - retired)
        self.assertTrue(all(packet_fields.values()))

    def test_behavior_vocabulary_hard_cut_has_no_retired_values(self) -> None:
        replacements = {
            "pull-request-ready-for-merge-but-not-merged": "pull-request-ready-for-merge",
            "codex-review-timeout-accepted": "codex-review-warned-timeout",
            "timeout-accepted": "warned-timeout",
            "pending-warning": "warning-required",
            "review-polling": "review-wait",
            "granted-by-authorized-user": "granted",
            "denied-by-authorized-user": "denied",
            "marking-ready-for-review": "readying-pr",
            "preparing-tracker-closeout": "tracker-closeout",
            "checking-mergeability": "mergeability",
            "task-terminal-sealed": "task-sealed",
            "terminal-sealed": "sealed",
            "unchanged-outside-scope-allowed": "unchanged-outside-scope",
            "managed-checkouts-observed": "checkouts-observed",
            "implementation-baseline-accepted": "baseline-accepted",
            "validation-nonregression-observed": "nonregression-observed",
            "portfolio-preimplementation-aborted": "preimplementation-aborted",
            "delivery-preflight-observed": "preflight-observed",
            "execution-command-reserved": "command-reserved",
            "execution-command-launch-observed": "command-launched",
            "execution-command-cancellation-authorized": "command-cancel-authorized",
            "execution-command-terminal-observed": "command-finished",
            "task-dependency-wait-started": "dependency-wait-started",
            "task-dependency-wait-resolved": "dependency-wait-resolved",
            "autoreview-hosted-finding-obligated": "hosted-finding-obligated",
            "terminal-handoff-recorded": "handoff-recorded",
            "portfolio-terminal-verified": "portfolio-verified",
            "post-terminal-drift-recorded": "terminal-drift-recorded",
            "post-terminal-drift": "terminal-drift",
            "dependency-integration": "dependencies-merged",
            "scope-acceptance": "scope",
            "integration-validation": "integration",
            "unsupported-app-delivery-target": "unsupported-delivery-target",
            "gitstack-installation-mismatch": "gitstack-mismatch",
            "delivery-preflight-failed": "preflight-failed",
            "unsupported-active-ledger": "unsupported-ledger",
            "owner-required": "needs-owner",
            "pull-request-draft": "draft-pr",
            "pull-request-not-ready": "pr-not-ready",
            "missing-pull-request": "missing-pr",
            "missing-current-revision-set": "missing-revision-set",
            "portfolio-goal-ready": "goal-ready",
            "portfolio-verification-ready": "verification-ready",
        }
        runtime_paths = [
            REPO / "AGENTS.md",
            ROOT / "SKILL.md",
            ROOT / "agents/openai.yaml",
            *sorted((ROOT / "references").glob("*.md")),
            *sorted(path for path in (ROOT / "scripts").iterdir() if path.is_file()),
        ]
        runtime = "\n".join(path.read_text() for path in runtime_paths)
        for retired, current in replacements.items():
            self.assertNotIn(retired, runtime, retired)
            self.assertIn(current, runtime, current)

    def test_autoreview_producer_and_ledger_import_one_protocol_file(self) -> None:
        producer = self.read("../autoreview/scripts/autoreview")
        ledger = self.read("scripts/ledger-cache")
        protocol_path = (ROOT.parent / "autoreview/scripts/autoreview_protocol.py").resolve()
        self.assertTrue(protocol_path.is_file())
        self.assertIn('with_name("autoreview_protocol.py")', producer)
        self.assertNotIn('autoreview/scripts/autoreview_protocol.py', ledger)
        self.assertNotIn("AUTOREVIEW_PHASES =", ledger)
        self.assertNotIn("AUTOREVIEW_TERMINAL_STATES =", ledger)
        self.assertNotIn('REVIEW_PHASES = {"full"', producer)
        self.assertEqual(ledger.count("validate_transition("), 0)

    def test_review_reconciliation_is_branch_only_and_has_no_legacy_adoption(self) -> None:
        skill = self.read("SKILL.md")
        worker = self.read("references/worker.md")
        reconciliation = self.read("references/review-reconciliation.md")
        packets = self.read("references/packets-task.md")
        self.assertIn(
            "references/review-reconciliation.md", self.read("scripts/ledger-cache")
        )
        self.assertNotIn("review-reconciliation.md", worker)
        self.assertIn("request-correlation-failure", reconciliation)
        self.assertIn("non-executable", reconciliation)
        self.assertIn("never imported", reconciliation)
        self.assertIn("`review-reconciled`", reconciliation)

    def test_v6_registration_packet_registry_matches_the_runtime(self) -> None:
        helper = self.read("scripts/ledger-cache")
        packets = self.read("references/packets-registration.md")
        module = ast.parse(helper)
        validate_registration = next(
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "validate_registration"
        )
        runtime_sets: dict[str, set[str]] = {}
        for node in ast.walk(validate_registration):
            if not (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id
                in {"required", "source_required", "delivery_required"}
                and isinstance(node.value, ast.Set)
            ):
                continue
            runtime_sets[node.targets[0].id] = {
                item.value
                for item in node.value.elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            }

        top = packets.split("Supply:", 1)[1].split(
            "Each `sources[]` object", 1
        )[0]
        documented_top = set(re.findall(r"^\| `([^`]+)` \|", top, re.MULTILINE))

        def listed_fields(after: str) -> set[str]:
            block = packets.split(after, 1)[1].split("```text", 1)[1].split("```", 1)[0]
            return set(re.findall(r"[a-z][a-z0-9_]*", block))

        self.assertEqual(documented_top, runtime_sets["required"])
        self.assertEqual(
            listed_fields("Each `sources[]` object supplies exactly:"),
            runtime_sets["source_required"],
        )
        self.assertEqual(
            listed_fields("Each nonempty `deliveries[]` object supplies exactly:"),
            runtime_sets["delivery_required"],
        )
        self.assertNotIn("tracker_sources", packets)
        self.assertIn("execution-manifest-installation:v1", packets)
        self.assertIn("rejects a missing, copied, or stale", packets)
        self.assertIn("execution_manifest_installation_evidence", helper)
        self.assertIn("registration execution-manifest evidence is stale", helper)

    def test_gate_scopes_and_handoff_authorities_are_closed(self) -> None:
        helper = self.read("scripts/ledger-cache")
        packets = self.read("references/packets-gates.md")
        run_state = " ".join(self.read("references/run-state.md").split())
        module = ast.parse(helper)
        expected = {
            "TASK_STATIC_GATES": {"dependencies-merged"},
            "TASK_REVISION_SET_GATES": {
                "scope",
                "integration",
                "domain-closeout",
            },
            "DELIVERY_REVISION_GATES": {
                "focused-validation",
                "full-validation",
                "autoreview",
                "publication",
                "codex-review",
                "ci",
                "pr-ready",
                "tracker-closeout",
                "mergeability",
            },
        }
        actual: dict[str, set[str]] = {}
        for node in module.body:
            if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Set):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in expected:
                    actual[target.id] = {
                        item.value
                        for item in node.value.elts
                        if isinstance(item, ast.Constant)
                    }
        self.assertEqual(actual, expected)

        scope_to_constant = {
            "task static": "TASK_STATIC_GATES",
            "task revision set": "TASK_REVISION_SET_GATES",
            "delivery revision": "DELIVERY_REVISION_GATES",
        }
        for scope, constant in scope_to_constant.items():
            row = next(
                line for line in packets.splitlines() if line.startswith(f"| {scope} |")
            )
            gates_column = row.strip("|").split("|")[1]
            documented = set(re.findall(r"`([^`]+)`", gates_column))
            self.assertEqual(documented, expected[constant])

        self.assertIn("task-static", run_state)
        self.assertIn("dependency integration", run_state)
        self.assertIn("delivery evidence key binds its revision key and preflight key", run_state)
        closeout_packets = self.read("references/packets-closeout.md")
        self.assertIn("`external-merge-required`", closeout_packets)
        self.assertIn("Handoff requires the unchanged seal", " ".join(closeout_packets.split()))
        self.assertNotIn("durable-review-monitoring", packets)
        self.assertNotIn("monitoring-handoff-recorded", packets)
        self.assertNotIn("external-handoff-recorded", packets)

    def test_takeover_contract_uses_renamed_permission(self) -> None:
        runtime = self.runtime_text()
        helper = self.read("scripts/active-root-claim")
        combined = runtime + helper
        compact_runtime = " ".join(runtime.split())
        self.assertIn("stale_claim_takeover_permission", runtime)
        self.assertIn("--takeover-permission", helper)
        self.assertIn("granted", helper)
        self.assertIn("--expected-task-termination", helper)
        self.assertIn("--expected-task-adoption", helper)
        self.assertIn("recover-takeover", combined)
        self.assertIn("stale heartbeat alone", runtime.lower())
        self.assertIn("five-minute stale threshold", compact_runtime)
        self.assertIn('SCHEMA_VERSION = "8.0.0"', helper)
        self.assertIn(
            "Do not import, migrate, rename, dual-read, dual-write, retire, or delete",
            compact_runtime,
        )
        self.assertNotIn("claim retire-legacy", combined)
        self.assertNotIn("--takeover-policy", combined)
        self.assertNotIn("takeover-authorized", combined)

    def test_takeover_permission_precedes_task_stop_and_preserves_task_identity(self) -> None:
        options = " ".join(self.read("references/options.md").split())
        run_state = " ".join(self.read("references/run-state.md").split())
        skill = f"{options} {run_state}"
        worker = " ".join(self.read("references/worker.md").split())

        discovery = skill.index("after read-only discovery proves")
        permission = skill.index("`stale_claim_takeover_permission`")
        stop = skill.index("permits the root to stop and verify every task")
        takeover = skill.index("prepared journal")
        self.assertIn("Resolve `stale_claim_takeover_permission` after read-only discovery proves", options)
        self.assertIn("Only a grant permits the root to stop and verify every task", options)
        self.assertLess(stop, takeover)

        self.assertIn("Denial aborts as `needs-owner` before stopping a task", skill)
        self.assertIn("complete repository/source scope", skill)
        self.assertIn("full-scope claim replacement", skill)
        self.assertIn("same-task adoption", skill)
        self.assertIn(
            "do not infer identity or replace a mapped task",
            skill,
        )
        self.assertIn("before stopping a task", options)
        self.assertIn("same-task adoption", options)
        self.assertIn("reuse the original task", worker.lower())
        self.assertIn("missing, shared, symlinked, unmanaged, or non-isolated evidence blocks", worker.lower())

    def test_takeover_is_prepared_recoverable_and_self_contained(self) -> None:
        skill = " ".join(self.read("references/run-state.md").split())
        run_state = " ".join(self.read("references/run-state.md").split())
        recovery = " ".join(
            self.read("references/recovery-validation.md").split()
        )
        worker = " ".join(self.read("references/worker.md").split())
        options = self.read("references/options.md")
        helper = self.read("scripts/active-root-claim")

        self.assertIn("prepared-takeover journal before deleting any prior claim", skill)
        self.assertIn("journal remains an ownership record", skill)
        self.assertIn("full replaced-claim snapshot", skill)
        self.assertIn("validated per-Spec adoption data", skill)
        self.assertIn("claim recover-takeover", skill)
        self.assertIn("prepared journal", run_state)
        self.assertNotIn("claim-rebound", run_state)
        self.assertIn("keeps its exact claim and fingerprint", run_state)
        self.assertIn("Missing state initializes only from the current claim's complete adoption mappings", run_state)
        self.assertIn("initialize only from the current prepared journal", recovery)
        self.assertIn("complete embedded adoption mappings", recovery)
        self.assertIn("no candidate JSON because creation never completed", recovery)
        for field in (
            '"source_spec_ref"',
            '"task_ref"',
            '"task_assignment_fingerprint"',
            '"managed_checkouts"',
            '"task_model"',
            '"target_branch_name"',
            '"baseline_revision"',
        ):
            self.assertIn(field, helper)
        self.assertIn('"ledger_ref"', helper)
        self.assertIn('"no-task"', helper)
        self.assertIn("current claim's complete adoption mappings", run_state)
        self.assertIn("prepared-takeover transaction ids", options)
        self.assertNotIn("expected_task_adoption", options)

    def test_reference_load_predicates_cover_takeover_and_partial_bundles(self) -> None:
        skill = " ".join(self.read("references/root-bootstrap.md").split())
        recovery = " ".join(
            self.read("references/recovery-validation.md").split()
        )
        workspace = " ".join(
            self.read("references/multi-repo-workspace.md").split()
        )

        self.assertIn("prepared takeover", recovery)
        self.assertIn("before a candidate JSON state exists", recovery)
        self.assertIn("partial plus integration", skill)
        self.assertIn("more than one affected repository", skill)
        self.assertIn("partial and integration", workspace)
        self.assertIn("single-repository", workspace)

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
                "denied",
                True,
                "permission-denied",
                ["surface", "snapshot", "delivery-preflight", "intake", "authorization"],
            ),
            (
                True,
                True,
                "granted",
                False,
                "planning-required",
                ["surface", "snapshot", "delivery-preflight", "intake"],
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

        outcome, observed, mutations = run_app_preclaim_fixture(
            surface_available=True,
            goal_surface_available=True,
            root_goal_state="blocked",
            permission="not-requested",
            bundle_ready=True,
        )
        self.assertEqual(outcome, "new-root-required")
        self.assertEqual(observed, ["surface"])
        self.assertEqual(mutations, [])

        outcome, observations, mutations = run_app_preclaim_fixture(
            surface_available=True,
            permission="granted",
            bundle_ready=True,
        )
        self.assertEqual(outcome, "accepted")
        self.assertEqual(
            observations,
            ["surface", "snapshot", "delivery-preflight", "intake", "authorization"],
        )
        self.assertEqual(
            mutations,
            [
                "atomic-claim",
                "cache-retention",
                "run-state-create",
                "root-task-title",
                "portfolio-goal",
            ],
        )

        surface_contract = self.read("SKILL.md").split(
            "## Immutable Safety Contract", 1
        )[0]
        self.assertIn("Goal pause/resume", surface_contract)
        self.assertIn("outside this runtime", " ".join(surface_contract.split()))
        compact_surface = " ".join(surface_contract.split())
        for token in (
            "Call `get_goal` once",
            "blocked root Goal",
            "`new-root-required`",
            "Before reading sources or asking permission",
            "stop before source reads, claim",
            "stop before source reads, claim, artifacts, tasks, or mutation",
        ):
            self.assertIn(token, compact_surface)

        recovery = " ".join(
            self.read("references/recovery-validation.md").split()
        )
        self.assertIn("before authorization/run-state reads", recovery)
        self.assertIn("never adopt/update that Goal", recovery)

    def test_multi_repo_requires_one_task_and_all_managed_checkouts(self) -> None:
        text = " ".join(self.read("references/multi-repo-workspace.md").split())
        self.assertIn("one visible App task per Feature Spec", text)
        self.assertIn("distinct isolated checkout for every required repository", text)
        self.assertIn("one real, non-draft, reviewed PR with CI passed", text)
        self.assertIn("Each task uses its Feature Spec's target branch name", text)
        self.assertIn("exactly one distinct repo-owned integration Feature Spec", text)
        self.assertIn("bounded path change", text)
        self.assertIn("validation-only or no-op", text)
        self.assertIn("feature/<feature_slug>-integration", text)
        self.assertIn("<ordinary_target_branch_name>-integration", text)
        self.assertIn("must equal `<ordinary_target_branch_name>-integration`", text)

    def test_knowledge_payload_exists_only_on_the_final_issue(self) -> None:
        delivery = self.read("references/spec-backed-delivery.md")
        skill = self.read("references/worker-implementation.md")
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
        self.assertIn("`domain_operation=implementation-closeout`", skill)
        self.assertIn("spec-backed-delivery.md", self.read("references/root-bootstrap.md"))

    def test_knowledge_targets_must_fit_final_issue_execution_scope(self) -> None:
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        skill = " ".join(self.read("references/root-bootstrap.md").split())

        for contents in (delivery,):
            self.assertIn("repository", contents)
            self.assertIn("repo-relative path", contents)
            self.assertIn("`affected_repositories`", contents)
            self.assertIn("`allowed_paths`", contents)
            self.assertIn("`planning-required`", contents)
        self.assertIn("every `target_surfaces` entry", delivery)
        self.assertIn("intake must not widen the Execution Contract", delivery)
        self.assertIn("spec-backed-delivery.md", skill)

    def test_knowledge_closeout_owner_is_graph_final_and_self_contained(self) -> None:
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        skill = " ".join(self.read("references/worker-implementation.md").split())

        for contents in (delivery,):
            self.assertIn("remaining", contents)
            self.assertIn("dedicated integration partial", contents)
            self.assertIn("memory_slice=domain-memory", contents)
            self.assertIn("domain_operation=implementation-closeout", contents)
            self.assertIn("after integrated behavior", contents)
            self.assertIn("planning-required", contents)
        self.assertIn("knowledge delta", skill)
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
        worker = " ".join(self.read("references/worker-implementation.md").split())

        self.assertIn("capture_outcome=captured", delivery)
        self.assertIn("every supplied accepted item", gates)
        self.assertIn("named verified destinations", worker)
        self.assertIn("documentation-diff", worker)
        self.assertIn("deferred", worker)
        self.assertIn("no-durable-change", worker)
        self.assertIn("blocks", gates)
        self.assertIn("`deferred`, or `no-durable-change` blocks for owner direction", worker)
        self.assertIn("owner decision", gates)
        self.assertIn("Domain Knowledge Closeout Gate", gates)
        self.assertIn("blocks domain closeout and terminal `merge-ready`", gates)

    def test_domain_closeout_evidence_is_revision_bound_and_recoverable(self) -> None:
        packets = " ".join(self.read("references/packets-gates.md").split())
        gates = " ".join(self.read("references/gates.md").split())
        worker = " ".join(self.read("references/worker-implementation.md").split())
        recovery = " ".join(self.read("references/recovery-validation.md").split())
        review = " ".join(self.read("references/codex-review-closeout.md").split())

        for token in (
            "delta fingerprint",
            "verified named destination",
            "documentation-diff fingerprint",
            "implementation revision tuples",
        ):
            self.assertIn(token, worker)
        self.assertIn("`knowledge_delta`", gates)
        self.assertIn("`domain-closeout`", packets)
        self.assertIn("domain closeout", recovery)
        self.assertIn("invalidates captured domain-closeout evidence", review)
        self.assertIn("persist fresh delta", review)

    def test_intake_rejects_non_forward_generated_dependencies(self) -> None:
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        skill = " ".join(self.read("references/root-bootstrap.md").split())

        self.assertIn("earlier-only dependencies", skill)
        self.assertIn("strictly earlier generated issue", delivery)
        self.assertIn("reject self, same-ID, and later-ID dependencies", delivery)

    def test_github_shorthand_is_normalized_for_claim_and_task_identity(self) -> None:
        skill = " ".join(self.read("references/root-bootstrap.md").split())
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        packets = self.read("references/packets-registration.md")

        for text in (skill, delivery):
            self.assertIn("owner/repository#N", text)
            self.assertIn("https://github.com/owner/repository/issues/N", text)
        self.assertIn("for helper claim/task identity", skill)
        self.assertIn("Preserve the shorthand as the authoritative artifact ref", delivery)
        self.assertIn("source_spec_ref", packets)
        self.assertIn("source_id", packets)
        self.assertIn("never pass it directly to a helper", skill)

    def test_local_move_is_scoped_and_revalidated_at_the_resulting_head(self) -> None:
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        gates = " ".join(self.read("references/gates.md").split())
        recovery = " ".join(
            self.read("references/recovery-validation.md").split()
        )
        packets = " ".join(self.read("references/packets-task.md").split())
        registration_packets = self.read("references/packets-registration.md")
        helper = self.read("scripts/ledger-cache")

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
        self.assertIn("planned_done_ref", registration_packets)
        self.assertIn("`source-moved`", packets)
        self.assertIn('SOURCE_STATES = {"ready-for-agent", "done"}', helper)
        self.assertIn("accept a missing active path only when", recovery)
        self.assertIn("If a local move is fully proven, apply `source-moved`", recovery)
        self.assertIn("Both paths, neither path", recovery)

    def test_revision_and_delivery_observations_are_distinct(self) -> None:
        helper = self.read("scripts/ledger-cache")
        run_state = " ".join(self.read("references/run-state.md").split())
        revision = helper.split('if event_type == "revision-observed":', 1)[1].split(
            'if event_type == "delivery-observed":', 1
        )[0]
        delivery = helper.split('if event_type == "delivery-observed":', 1)[1].split(
            'if event_type == "source-moved":', 1
        )[0]

        for field in (
            '"repository"',
            '"pr_number"',
            '"pr_url"',
            '"head_sha"',
            '"base_ref"',
            '"merge_base_sha"',
        ):
            self.assertIn(field, revision)
        self.assertIn('"revision_key"', delivery)
        self.assertIn('"pr"', delivery)
        self.assertIn('"committed"', delivery)
        self.assertIn('"published"', delivery)
        self.assertNotIn("tracker_dirty_after_revision_key\"] = None", revision)
        self.assertIn("tracker_dirty_after_revision_key\"] = None", delivery)
        self.assertIn("revision[\"revision_key\"] != dirty", delivery)
        self.assertIn("The events are distinct, not aliases", run_state)

    def test_terminal_pr_base_is_derived_default_branch(self) -> None:
        skill = " ".join(self.read("references/worker-publication.md").split())
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        gates = " ".join(self.read("references/gates.md").split())
        closeout = " ".join(
            self.read("references/codex-review-closeout.md").split()
        )

        self.assertIn("Create or update each delivery PR against", skill)
        self.assertIn("discovered default branch", skill)
        self.assertIn("discovered default branch", skill)
        self.assertIn("verified during preflight and current-head review", delivery)
        self.assertIn("base equal to that repository's currently discovered default branch", gates)
        self.assertIn("closing keywords cannot take effect", closeout)

    def test_terminal_pr_requires_current_mergeability_and_repo_rules(self) -> None:
        skill = " ".join(self.read("references/worker-publication.md").split())
        gates = " ".join(self.read("references/gates.md").split())
        worker = " ".join(self.read("references/worker-publication.md").split())
        packets = " ".join(self.read("references/packets-gates.md").split())
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
        self.assertIn("`mergeability`", packets)
        self.assertIn("`isDraft=false`", worker)
        revision_packets = self.read("references/packets-task.md")
        for field in ("pr_number", "pr_url", "head_sha", "base_ref", "merge_base_sha"):
            self.assertIn(field, revision_packets)
        self.assertIn("current branch-rule, approval, base-freshness, conflict, mergeability", skill)

        report = " ".join(self.read("references/worker.md").split())
        for token in (
            "actual `capture_outcome`",
            "delta fingerprint",
            "verified named destination",
            "documentation-diff fingerprint",
            "implementation revision tuples",
        ):
            self.assertIn(token, report)
        self.assertIn("convert a draft through exact PR identity", skill)
        self.assertIn("ready-for-review transition is nonterminal", skill)
        self.assertIn("Do not make draft status a circular prerequisite", gates)
        self.assertIn("ready-for-review with `isDraft=false`", gates)
        self.assertIn("convert a draft through exact PR identity", worker)
        self.assertIn("After that nonterminal transition", worker)
        self.assertLess(
            worker.index("convert a draft through exact PR identity"),
            worker.index("current branch-rule"),
        )
        states = self.read("references/packets-task.md").split("Task states are", 1)[1].split(".\n", 1)[0]
        self.assertLess(
            states.index("`readying-pr`"),
            states.index("`review-wait`"),
        )
        self.assertLess(
            states.index("`tracker-closeout`"),
            states.index("`mergeability`"),
        )
        self.assertNotIn("`marking-ready`", states)
        self.assertIn("domain-closeout", gates)
        self.assertIn("readable lifecycle", self.read("references/root-bootstrap.md"))
        self.assertIn("mergeability/conflicts", self.read("references/root-bootstrap.md"))
        for token in (
            "current PR lifecycle/conflict/mergeability",
            "required base freshness",
            "approval",
            "merge-queue eligibility",
            "observation tuple/time",
        ):
            self.assertIn(token, report)

    def test_ready_transition_resolves_and_reuses_exact_pr_identity(self) -> None:
        worker = " ".join(self.read("references/worker-publication.md").split())
        for token in (
            "Outside the ready mutation's shell chain",
            "exact number and URL",
            "`gh pr ready <number> --repo <owner/repo>`",
            "selectorless or branch inference",
            "re-read the same number and require the unchanged URL and `isDraft=false`",
        ):
            self.assertIn(token, worker)
        self.assertLess(worker.index("exact number and URL"), worker.index("gh pr ready <number>"))
        self.assertLess(worker.index("gh pr ready <number>"), worker.index("re-read the same number"))
        self.assertNotIn("gh pr ready --repo", self.runtime_text())

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
            REPO / "skills/plan-feature/references/complete-bundle-proposal.md"
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
        skill = " ".join(self.read("references/root-bootstrap.md").split())
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        workspace = " ".join(
            self.read("references/multi-repo-workspace.md").split()
        )

        for contents in (delivery, workspace):
            self.assertIn("(repository, target_branch_name)", contents)
            self.assertIn("implementation-eligible", contents)
            self.assertIn("coordination-only parent/global", contents)
            self.assertIn("no task", contents)
            self.assertIn("App-managed worktree", contents)
            self.assertIn("same branch name", contents)
            self.assertIn("different repositories", contents)
            self.assertIn("paths are disjoint", contents)
            self.assertIn("`planning-required` before CLAIM", contents)
        self.assertIn("Never serialize", skill)
        self.assertIn("force-bind", skill)
        self.assertIn("schedule around the collision", workspace)

    def test_local_closeout_uses_one_ready_for_review_sequence(self) -> None:
        gates = " ".join(self.read("references/gates.md").split())
        segment = gates.split("For local Markdown", 1)[1]
        order = (
            "move each issue",
            "tracker delivery dirty",
            "commit and push",
            "`revision-observed`",
            "`delivery-observed`",
            "$autoreview",
            "ready-for-review",
            "current-revision review",
            "CI",
            "terminal merge-ready",
        )
        offsets = [segment.index(token) for token in order]
        self.assertEqual(offsets, sorted(offsets))

        closeout = " ".join(self.read("references/worker-closeout.md").split())
        publication = " ".join(self.read("references/worker-publication.md").split())
        self.assertIn("local tracker sources", closeout)
        self.assertIn("newer revision", closeout)
        self.assertIn("rerun validation", closeout)
        self.assertIn("terminal AutoReview", closeout)
        self.assertIn("convert a draft", publication)
        self.assertIn("current-revision Codex review", publication)

    def test_metadata_is_manual_and_compact(self) -> None:
        skill = self.read("SKILL.md")
        metadata = self.read("agents/openai.yaml")
        self.assertEqual(ROOT.name, "implement-feature")
        self.assertIn("name: implement-feature", skill)
        self.assertIn("explicitly invokes `$implement-feature`", skill)
        self.assertIn("merge-ready-but-unmerged pull requests", skill)
        self.assertIn('display_name: "Implement Feature"', metadata)
        self.assertIn("allow_implicit_invocation: false", metadata)
        skill_bytes = len(skill.encode("utf-8"))
        self.assertLessEqual(skill_bytes, 16_500)
        self.assertLessEqual((skill_bytes + 3) // 4, 4_125)
        successful_path = (
            "SKILL.md",
            "references/options.md",
            "references/task-model-policy.md",
            "references/spec-backed-delivery.md",
            "references/baseline-validation.md",
            "references/run-state.md",
            "references/packets-registration.md",
            "references/packets-task.md",
            "references/packets-gates.md",
            "references/packets-closeout.md",
            "references/cache-lifecycle.md",
            "references/worker.md",
            "references/gates.md",
            "references/codex-review-closeout.md",
        )
        # The root-only qualified diagnostics contract adds one bounded read
        # model while the worker prompt remains at its existing ceiling.
        self.assertLessEqual(
            sum(len(self.read(path).encode("utf-8")) for path in successful_path),
            115_200,
        )
        manifest_path = successful_path + ("references/execution-manifest.md",)
        # Bounded execution stays branch-loaded; normal, manifest, and
        # multi-repository paths retain explicit measured ceilings.
        self.assertLessEqual(
            sum(len(self.read(path).encode("utf-8")) for path in manifest_path),
            126_600,
        )
        multi_repository_path = successful_path + (
            "references/multi-repo-workspace.md",
        )
        self.assertLessEqual(
            sum(
                len(self.read(path).encode("utf-8"))
                for path in multi_repository_path
            ),
            119_500,
        )
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

    def test_execution_manifest_scope_and_worker_prompt_budget_are_bounded(self) -> None:
        skill = self.read("SKILL.md")
        worker = self.read("references/worker.md")
        execution = self.read("references/execution-manifest.md")
        run_state = self.read("references/run-state.md")
        script = self.read("scripts/execution-manifest")
        prompt_match = re.search(r"## Fixed Task Prompt\n\n(.*?)\n## Report", worker, re.DOTALL)
        self.assertIsNotNone(prompt_match)
        assert prompt_match is not None
        prompt = prompt_match.group(1)
        # Bounded attempt and root monitor ownership add 329 characters while
        # provider and helper mechanics remain behind references.
        baseline_characters = 2033
        self.assertLessEqual(len(prompt), baseline_characters)
        self.assertNotIn("scripts/autoreview --", prompt)
        self.assertNotIn("scripts/delivery-preflight", prompt)
        self.assertNotIn("ledger-cache --json", prompt)
        self.assertNotIn("--projection diagnostics", prompt)
        self.assertNotIn("terminal_verification", prompt)
        self.assertIn("canonical source/title", prompt)
        self.assertIn("validation/integration command manifests", prompt)
        self.assertIn("Never create, fork", prompt)
        self.assertIn("another visible App task", prompt)
        self.assertIn("codex_app__create_thread", worker)
        self.assertIn("codex_app__fork_thread", worker)
        self.assertIn("codex_app__send_message_to_thread", worker)
        self.assertIn("scripts/execution-manifest", self.read("references/worker-validation.md"))
        self.assertIn("per 60 seconds", worker)
        self.assertIn("one bounded attempt", prompt)
        self.assertIn("HEARTBEAT_INTERVAL_SECONDS = 60", self.read("scripts/active-root-claim"))
        self.assertIn("MONITOR_DEGRADED_AFTER_SECONDS = 180", self.read("scripts/active-root-claim"))
        for operation in ("delivery-preflight", "validation", "autoreview"):
            self.assertIn(f'"{operation}"', script)
            self.assertIn(operation, execution)
        for deferred in ("Claims", "ledger commands", "GitStack", "CI"):
            self.assertIn(deferred, execution)
        self.assertIn("scripts/ledger-cache --json ledger create", run_state)
        self.assertIn("projection 'status|dispatch|recovery|terminal|diagnostics'", run_state)

    def test_diagnostic_wording_is_qualified_without_renaming_raw_values(self) -> None:
        prose = "\n".join(
            self.read(path)
            for path in (
                "SKILL.md",
                "references/autoreview-fix-loop.md",
                "references/baseline-validation.md",
                "references/codex-review-closeout.md",
                "references/execution-manifest.md",
                "references/gates.md",
                "references/multi-repo-workspace.md",
                "references/review-reconciliation.md",
                "references/run-state.md",
                "references/spec-backed-delivery.md",
            )
        )
        errors = "\n".join(
            (
                self.read("scripts/ledger-cache"),
                self.read("scripts/execution-manifest"),
            )
        )
        for banned in (
            "complete and clean",
            "completed and clean",
            "CI-clean",
            "clean scoped local commit",
            "clean committed revision",
            "Git-visible clean",
        ):
            with self.subTest(banned=banned):
                self.assertNotIn(banned.lower(), prose.lower())
                self.assertNotIn(banned.lower(), errors.lower())
        run_state = self.read("references/run-state.md")
        ledger = self.read("scripts/ledger-cache")
        self.assertIn("Provider `merge_state=clean` renders", run_state)
        self.assertIn('"raw_merge_state": raw_merge_state', ledger)
        self.assertIn('display_result = "conflict-free"', ledger)
        for raw_identifier in (
            "clean-required",
            "clean-exit-v1",
            '"clean": ("accepted"',
            "terminal-clean",
            'pr["merge_state"] != "clean"',
        ):
            self.assertIn(raw_identifier, errors)

    def test_execution_manifest_validation_forbids_shell_transport(self) -> None:
        execution = self.read("references/execution-manifest.md")
        script = self.read("scripts/execution-manifest")
        self.assertIn("literal string array", execution)
        self.assertIn("A string command line is invalid", " ".join(execution.split()))
        self.assertIn("SHELL_WRAPPERS", script)
        self.assertIn("environment assignment", script)
        self.assertNotIn("shlex", script)

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

    def test_phase_scoped_hard_cut_has_one_public_router_and_no_legacy_packet_registry(self) -> None:
        skill = self.read("SKILL.md")
        controller = self.read("references/controller.md")
        runtime = self.runtime_text()

        self.assertFalse((ROOT / "references/run-state-packets.md").exists())
        self.assertNotIn("run-state-packets.md", runtime)
        self.assertNotIn("0. **SURFACE**", skill)
        self.assertNotIn("## Fixed Actions", self.read("references/worker.md"))
        self.assertIn("controller next", skill)
        self.assertIn("Load exactly the returned `required_contracts`", skill)
        self.assertIn("sole action-to-contract mapping", " ".join(skill.split()))
        self.assertNotIn("observe-root-title", controller)
        self.assertNotIn("steer-implementation", controller)
        self.assertIn("exhaustive and final", controller)
        self.assertIn("returned list is exhaustive and final", controller)
        for relative in (
            "references/root-bootstrap.md",
            "references/worker-implementation.md",
            "references/worker-validation.md",
            "references/worker-publication.md",
            "references/worker-review-fix.md",
            "references/worker-closeout.md",
            "references/packets-registration.md",
            "references/packets-task.md",
            "references/packets-gates.md",
            "references/packets-closeout.md",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_controller_registry_is_closed_sufficient_and_reloads_worker_role_after_compaction(self) -> None:
        runtime = self.controller_runtime()
        runtime.validate_controller_registry()
        actions = runtime.CONTROLLER_ACTIONS

        self.assertEqual(len(actions), 31)
        for action, spec in actions.items():
            paths = [path for _contract_id, path in spec["contracts"]]
            self.assertEqual(len(paths), len(set(paths)), action)
            self.assertTrue(all((ROOT / path).exists() for path in paths), action)
            limit = 4 if spec["phase"] == "operation-recovery" else 3
            self.assertLessEqual(len(paths), limit, action)
            packet_paths = [path for path in paths if path.startswith("references/packets-")]
            if spec["events"]:
                self.assertEqual(len(packet_paths), 1, action)
            else:
                self.assertEqual(packet_paths, [], action)
            if spec["executor"] == "visible-task":
                self.assertIn("references/worker.md", paths, action)

        for action in (
            "steer-implementation",
            "steer-validation",
            "steer-publication",
            "steer-ready-transition",
            "steer-review-fix",
            "steer-ci",
            "steer-tracker-closeout",
            "steer-mergeability",
        ):
            paths = [path for _contract_id, path in actions[action]["contracts"]]
            self.assertEqual(len(paths), 3, action)
            self.assertEqual(paths[0], "references/worker.md", action)
            self.assertEqual(paths[-1], "references/packets-task.md", action)

    def test_deterministic_controller_replay_reuses_live_path_sha_without_redundant_loads(self) -> None:
        runtime = self.controller_runtime()
        replay = (
            "steer-implementation",
            "steer-validation",
            "steer-validation",
            "execute-autoreview-phase",
            "steer-review-fix",
            "steer-validation",
            "steer-publication",
            "execute-gitstack-request",
            "execute-gitstack-wait",
            "execute-gitstack-wait",
            "execute-gitstack-reply",
            "execute-gitstack-resolve",
            "apply-current-gate-evidence",
            "seal-task",
            "record-terminal-handoff",
            "verify-portfolio",
            "complete-root-goal",
            "release-and-archive",
        )
        live: set[tuple[str, str]] = set()
        selections = 0
        physical_loads = 0
        repeated_selections = 0
        redundant_physical_loads = 0

        for action in replay:
            for _contract_id, relative in runtime.CONTROLLER_ACTIONS[action]["contracts"]:
                selections += 1
                path = ROOT / relative
                key = (relative, hashlib.sha256(path.read_bytes()).hexdigest())
                if key in live:
                    repeated_selections += 1
                    continue
                live.add(key)
                physical_loads += 1

        self.assertGreater(repeated_selections, 0)
        self.assertEqual(physical_loads, len(live))
        self.assertEqual(redundant_physical_loads, 0)
        self.assertLess(physical_loads, selections)
        self.assertEqual(len(replay), 18)

    def test_phase_scoped_invoked_path_metrics_meet_binding_thresholds(self) -> None:
        runtime = self.controller_runtime()
        skill = ROOT / "SKILL.md"
        controller = ROOT / "references/controller.md"
        skill_text = skill.read_text()

        self.assertLessEqual(len(skill_text.splitlines()), 120)
        self.assertLessEqual(len(skill_text.split()), 900)
        self.assertLessEqual(len(skill.read_bytes()), 7_000)
        self.assertLessEqual(len(skill.read_bytes()) + len(controller.read_bytes()), 13_500)

        counts: list[int] = []
        contract_bytes: list[int] = []
        fresh_normal_bytes: list[int] = []
        for action, spec in runtime.CONTROLLER_ACTIONS.items():
            paths = [ROOT / path for _contract_id, path in spec["contracts"]]
            byte_count = sum(len(path.read_bytes()) for path in paths)
            counts.append(len(paths))
            contract_bytes.append(byte_count)
            if spec["phase"] == "operation-recovery":
                self.assertLess(byte_count, 25_000, action)
                self.assertLessEqual(len(paths), 4, action)
            else:
                self.assertLess(byte_count, 18_000, action)
                self.assertLessEqual(len(paths), 3, action)
                fresh_normal_bytes.append(
                    len(skill.read_bytes()) + len(controller.read_bytes()) + byte_count
                )

        self.assertLess(statistics.median(contract_bytes), 12_000)
        self.assertLess(max(fresh_normal_bytes), 31_500)
        self.assertLessEqual(max(counts), 4)


if __name__ == "__main__":
    unittest.main()
