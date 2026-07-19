from __future__ import annotations

import ast
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
    root_goal_state: str | None = None,
) -> tuple[str, list[str], list[str]]:
    observations = ["surface"]
    mutations: list[str] = []
    if not surface_available or not goal_surface_available:
        return "unsupported-runtime", observations, mutations
    if root_goal_state == "blocked":
        return "new-root-required", observations, mutations
    observations.append("authorization")
    if permission != "granted-by-authorized-user":
        return "permission-denied", observations, mutations
    observations.extend(["snapshot", "delivery-preflight", "intake"])
    if not bundle_ready:
        return "planning-required", observations, mutations
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
            "references/run-state-packets.md",
            "references/worker.md",
            "references/gates.md",
            "references/spec-backed-delivery.md",
            "references/codex-review-closeout.md",
            "references/recovery-validation.md",
            "references/multi-repo-workspace.md",
        }
        self.assertTrue(all((ROOT / path).is_file() for path in required))
        self.assertFalse((ROOT / "references/stacked-feature-specs.md").exists())
        for removed in (
            "references/ledger.md",
            "references/ledger-template.md",
            "references/runtime-efficiency.md",
        ):
            self.assertFalse((ROOT / removed).exists(), removed)

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
                "granted-by-authorized-user",
                "denied-by-authorized-user",
            ):
                self.assertIn(value, row)
        self.assertIn("This file owns every user-controlled App orchestration field", options)

    def test_standard_authorization_prompt_is_exact_and_user_friendly(self) -> None:
        skill = self.read("SKILL.md")
        options = self.read("references/options.md")
        disclosure = (
            "Each executable Feature Spec is one feature; one plan may create "
            "multiple visible tasks. This run may change and validate code, push "
            "commits, create or update pull requests, address "
            "Codex review, wait for CI when a repository has CI configured, "
            "prepare hosted issue closeout, and move, "
            "commit, and push completed local issue files when used. AutoReview "
            "sends Git status, staged/unstaged diffs, and every non-ignored "
            "untracked file to Codex; no extra authorization. Tasks use "
            "`gpt-5.6-sol`: `medium` only for routine localized work, `xhigh` for "
            "risky or cross-system work, and `high` otherwise. Codex waits up to "
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
        self.assertIn("standard disclosure, exact question", normalized_skill)
        self.assertIn("do not improvise them", normalized_skill)
        self.assertIn(disclosure, normalized_options)
        self.assertIn("| Header | `Start work?` |", options)
        self.assertIn(
            "| Question id | `visible_app_task_permission` |", options
        )
        self.assertIn(f"| Question | {prompt} |", options)
        self.assertIn(
            "| 1 | `Start implementation (Recommended)` | Use this workflow "
            "for the ready specs found in this run. | "
            "`granted-by-authorized-user` |",
            options,
        )
        self.assertIn(
            "| 2 | `Cancel` | Stop here without starting implementation or "
            "changing anything. | "
            "`denied-by-authorized-user` |",
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
        skill = self.read("SKILL.md")
        policy = self.read("references/task-model-policy.md")
        options = self.read("references/options.md")
        worker = self.read("references/worker.md")
        packets = self.read("references/run-state-packets.md")
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
            .split("## Fixed Contract", 1)[0]
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
        worker = self.read("references/worker.md")
        run_state = self.read("references/run-state.md")
        packets = self.read("references/run-state-packets.md")
        recovery = self.read("references/recovery-validation.md")
        options = self.read("references/options.md")
        claim_helper = self.read("scripts/active-root-claim")
        compact_run_state = " ".join(run_state.split())

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

        self.assertIn("task_title", packets)
        self.assertIn(
            "bound identities are immutable",
            " ".join(packets.split()),
        )
        self.assertIn("never display titles", compact_run_state)
        normalized_recovery = " ".join(recovery.split())
        self.assertIn("Record live title drift without repairing it", normalized_recovery)
        self.assertIn("Only after the full pass succeeds", normalized_recovery)
        self.assertIn("derived display title", normalized_recovery)
        self.assertIn("that same task", normalized_recovery)
        self.assertNotIn("task_title", options)
        self.assertNotIn('"task_title"', claim_helper)

    def test_root_task_title_is_stable_adaptive_and_recoverable(self) -> None:
        skill = self.read("SKILL.md")
        run_state = self.read("references/run-state.md")
        packets = self.read("references/run-state-packets.md")
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
            "## Sources, Tasks, And Scheduling", 1
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
            "`portfolio-goal-completed`",
        ):
            self.assertIn(token, compact_contract)

        self.assertLess(
            compact_contract.index("set and observe the calling task title"),
            compact_contract.index("Goal registration or dispatch"),
        )
        self.assertLess(
            compact_contract.index("`get_goal`"),
            compact_contract.index("`create_goal`"),
        )

        register = " ".join(
            skill.split("7. **REGISTER**", 1)[1]
            .split("8. **DISPATCH**", 1)[0]
            .split()
        )
        for token in (
            "complete Spec registry",
            "root_task_title",
            "set and observe the calling task title",
            "portfolio_goal_state=pending",
        ):
            self.assertIn(token, register)
        self.assertLess(
            register.index("root_task_title"),
            register.index("get_goal"),
        )
        self.assertLess(register.index("get_goal"), register.index("create_goal"))

        self.assertIn("root_task_title", packets)
        self.assertIn("portfolio_goal_state=pending", packets)

        compact_recovery = " ".join(recovery.split())
        for token in (
            "complete read-only pass",
            "Record live title drift without repairing it",
            "Call `get_goal` in the root and every recorded task",
            "Only after the full pass succeeds",
            "Repair title drift on that same task",
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

        terminal_contract = " ".join(
            skill[skill.index("After root-title revalidation") :].split()
        )
        closeout_order = (
            "root-title revalidation",
            "`task-terminal-sealed`",
            "`task-goal-completed`",
            "`terminal-handoff-recorded`",
            "`portfolio-terminal-verified`",
            "`portfolio-goal-completed`",
            "release and archive",
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
            "visible_app_task_permission=granted-by-authorized-user", skill
        )
        self.assertIn("fixed model, reasoning policy, and execution flow", options)
        self.assertIn("Generic delegation or subagent authority never supplies this grant", skill)

    def test_cache_maintenance_is_root_owned_bounded_and_after_claim(self) -> None:
        skill = self.read("SKILL.md")
        lifecycle = self.read("references/cache-lifecycle.md")
        normalized_lifecycle = " ".join(lifecycle.split())
        ledger = self.read("references/run-state.md")
        normalized_ledger = " ".join(ledger.split())
        controller = skill.split("## Controller Loop", 1)[1]

        options = " ".join(
            line.removeprefix("> ")
            for line in self.read("references/options.md").splitlines()
        )
        options = " ".join(options.split())
        self.assertIn(
            "automatically deletes valid run-state archives older than 180 days",
            options,
        )
        self.assertLess(controller.index("5. **CLAIM**"), controller.index("6. **CACHE-MAINTENANCE**"))
        self.assertLess(controller.index("6. **CACHE-MAINTENANCE**"), controller.index("7. **REGISTER**"))
        self.assertLess(controller.index("7. **REGISTER**"), controller.index("8. **DISPATCH**"))

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
        self.assertIn("`terminal` is the only active release reason", lifecycle)
        self.assertIn("Frozen archive-v1 entries remain readable evidence", normalized_ledger)
        self.assertIn("deterministic Markdown audit report is rendered only during archival", normalized_ledger)

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
        self.assertIn("one read-only snapshot", skill)
        self.assertIn("planning-required", skill)
        self.assertIn("unsupported-app-delivery-target", skill)
        self.assertIn("no claim, run state, Goal, task, tracker write, or source mutation", skill)
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
        skill = " ".join(self.read("SKILL.md").split())
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        self.assertIn("Sort ready candidates by canonical claim/task source id ascending", skill)
        self.assertIn("`## Feature Dependencies` table", delivery)
        self.assertIn("Greedily select", skill)
        self.assertIn("remaining three-task capacity", skill)
        self.assertIn("pairwise disjoint", skill)
        self.assertIn("ancestor/descendant path scopes as overlapping", skill)
        self.assertIn(
            "every upstream ref is merged",
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
        self.assertIn("assignment-scoped objective", normalized)
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
        run_state = self.read("references/run-state.md")
        packets = self.read("references/run-state-packets.md")
        recovery = self.read("references/recovery-validation.md")
        normalized_recovery = " ".join(recovery.split())

        for text in (skill, worker, run_state, recovery):
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
        self.assertIn("interrupted completion transition", normalized_recovery)
        self.assertIn("These are closeout transitions, not implementation resume", normalized_recovery)
        normalized_run_state = " ".join(run_state.split())
        self.assertIn("A different unfinished Goal is `needs-owner`", normalized_run_state)
        self.assertIn(
            "missing active Goal is never recreated during recovery",
            normalized_run_state,
        )
        normalized_worker = " ".join(worker.split())
        self.assertIn("already recorded at the fixed terminal result", normalized_worker)
        self.assertIn("must not resume implementation", normalized_worker)
        self.assertIn("finish that transition only", normalized_worker)
        for text in (normalized_run_state, normalized_worker):
            self.assertIn("CI when configured", text)
            self.assertIn("never reuse", text.lower())
        self.assertIn("rejects unconditional-CI registration and active state", normalized_run_state)
        self.assertIn(
            'PORTFOLIO_OBJECTIVE_CI_CLAUSE = "CI when configured"',
            self.read("scripts/ledger-cache"),
        )
        self.assertIn(
            "freshly derived portfolio Goal text containing exact `CI when configured`",
            packets,
        )

        surface = " ".join(
            skill.split("## Mandatory Runtime Surface Gate", 1)[1]
            .split("## Mandatory Run Authorization", 1)[0]
            .split()
        )
        self.assertIn("general visible-task Goal-tool support", surface)
        self.assertIn("`pending` to `active` to `complete`", surface)
        self.assertIn("Goal pause/resume and App heartbeat automation are not part", surface)
        self.assertIn("does not create a task to inspect task-local tools", surface)
        dispatch = " ".join(
            skill.split("8. **DISPATCH**", 1)[1].split("9. **MONITOR**", 1)[0].split()
        )
        self.assertIn("observe title, Goal tools/objective", dispatch)
        self.assertIn("before advancing beyond `created`", dispatch)

        register = " ".join(
            skill.split("7. **REGISTER**", 1)[1].split("8. **DISPATCH**", 1)[0].split()
        )
        self.assertLess(
            register.index("portfolio_goal_state=pending"),
            register.index("otherwise call `create_goal`"),
        )

        delivery = " ".join(skill.split("## Delivery And Final Report", 1)[1].split())
        closeout_order = (
            "`task-terminal-sealed`",
            "`task-goal-completed`",
            "`terminal-handoff-recorded`",
            "`portfolio-terminal-verified`",
            "`portfolio-goal-completed`",
            "release and archive",
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
        packets = self.read("references/run-state-packets.md")
        runtime = self.runtime_text()
        for token in ("head SHA", "base ref", "merge-base SHA"):
            self.assertIn(token, normalized_closeout)
        self.assertIn("entire tuple matches", closeout)
        self.assertIn("one 45-minute total active-wait deadline", closeout)
        for token in (
            "`revision_key`",
            "`wait_started_at`",
            "`wait_deadline`",
            "`wait_invoked_at`",
            "`provider_timeout=max(0,floor(wait_deadline-wait_invoked_at))`",
            "`--timeout <provider_timeout>s --interval 10s --max-interval 30s`",
            "unchanged deadline",
            "`timeout-accepted`",
            "`warning_ref`",
            "persistent PR warning",
            "later merge workflow must re-check",
        ):
            self.assertIn(token, normalized_closeout)
        self.assertLess(
            normalized_closeout.index("worker reports"),
            normalized_closeout.index("root atomically records"),
        )
        self.assertLess(
            normalized_closeout.index("root atomically records"),
            normalized_closeout.index("Before launch"),
        )
        self.assertLess(
            normalized_closeout.index("root must persist"),
            normalized_closeout.index("worker calls GitStack"),
        )
        self.assertIn("Before `poll-review`", worker)
        self.assertIn("require root-issued", worker)
        self.assertIn("Before launch set", worker)
        self.assertIn("single-launch authority", worker)
        self.assertIn("Start GitStack only after the root persists", worker)
        self.assertIn("provider_timeout", packets)
        self.assertIn("wait_invoked_at", packets)
        self.assertIn("warning_ref", packets)
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
        self.assertIn("Never schedule another check", closeout)
        self.assertIn("`review_operation`", closeout)
        self.assertIn("`mutation_mode=apply`", closeout)
        self.assertIn("never expose the translation as a user option", closeout)
        self.assertIn("Review request has no skip", gates)
        self.assertNotIn("15-minute", closeout)
        self.assertNotIn("--timeout 15m", runtime)

    def test_ci_requires_current_head_evidence_only_when_configured(self) -> None:
        skill = " ".join(self.read("SKILL.md").split())
        gates = " ".join(self.read("references/gates.md").split())

        self.assertIn("classify CI as `configured` or `not-configured`", skill)
        self.assertIn("`not-configured` is valid", skill)
        self.assertIn("zero artifacts", skill)
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
        packets = self.read("references/run-state-packets.md")
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
        self.assertIn("Use exactly these top-level fields", packets)
        self.assertIn(
            "Every event uses exactly the fields below",
            " ".join(packets.split()),
        )
        self.assertIn('__version__ = "7.0.0"', helper)
        self.assertIn("unsupported-active-ledger", helper)
        for removed in (
            "references/ledger.md",
            "references/ledger-template.md",
            "references/runtime-efficiency.md",
        ):
            self.assertFalse((ROOT / removed).exists())
        for retired_heading in ("## Wave Reports", "## Recovery Packet"):
            self.assertNotIn(retired_heading, run_state)

    def test_v4_event_packet_registry_matches_the_v7_runtime(self) -> None:
        helper = self.read("scripts/ledger-cache")
        packets = self.read("references/run-state-packets.md")
        run_state = " ".join(self.read("references/run-state.md").split())

        for constant in (
            '__version__ = "7.0.0"',
            'LEDGER_SCHEMA_VERSION = "4.0.0"',
            'REGISTRATION_SCHEMA_VERSION = "4.0.0"',
        ):
            self.assertIn(constant, helper)
        self.assertIn("| `schema_version` | `4.0.0` |", packets)
        self.assertIn(
            "exact `{git_common_dir, checkout}` claim map",
            packets,
        )
        self.assertNotIn("exact `{repository, checkout}` claim map", packets)
        self.assertIn("Active state accepts only ledger schema `4.0.0`", run_state)
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
            if match and match.group(1) in runtime_fields:
                packet_fields[match.group(1)] = set(
                    re.findall(r"`([^`]+)`", match.group(2))
                )
        self.assertEqual(packet_fields, runtime_fields)

    def test_v4_registration_packet_registry_matches_the_runtime(self) -> None:
        helper = self.read("scripts/ledger-cache")
        packets = self.read("references/run-state-packets.md")
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

        top = packets.split("Use exactly these top-level fields:", 1)[1].split(
            "Each `sources[]` object", 1
        )[0]
        documented_top = set(re.findall(r"^\| `([^`]+)` \|", top, re.MULTILINE))

        def listed_fields(after: str) -> set[str]:
            block = packets.split(after, 1)[1].split("```text", 1)[1].split("```", 1)[0]
            return set(re.findall(r"[a-z][a-z0-9_]*", block))

        self.assertEqual(documented_top, runtime_sets["required"])
        self.assertEqual(
            listed_fields("Each `sources[]` object has exactly:"),
            runtime_sets["source_required"],
        )
        self.assertEqual(
            listed_fields("Each nonempty `deliveries[]` object has exactly:"),
            runtime_sets["delivery_required"],
        )
        self.assertNotIn("tracker_sources", packets)

    def test_gate_scopes_and_handoff_authorities_are_closed(self) -> None:
        helper = self.read("scripts/ledger-cache")
        packets = self.read("references/run-state-packets.md")
        run_state = " ".join(self.read("references/run-state.md").split())
        module = ast.parse(helper)
        expected = {
            "TASK_STATIC_GATES": {"dependency-integration"},
            "TASK_REVISION_SET_GATES": {
                "scope-acceptance",
                "integration-validation",
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
            "task-static": "TASK_STATIC_GATES",
            "task-revision-set": "TASK_REVISION_SET_GATES",
            "delivery-revision": "DELIVERY_REVISION_GATES",
        }
        for scope, constant in scope_to_constant.items():
            row = next(
                line for line in packets.splitlines() if line.startswith(f"| `{scope}` |")
            )
            gates_column = row.strip("|").split("|")[1]
            documented = set(re.findall(r"`([^`]+)`", gates_column))
            self.assertEqual(documented, expected[constant])

        self.assertIn("task-static", run_state)
        self.assertIn("dependency integration", run_state)
        self.assertIn("delivery evidence key binds its revision key and preflight key", run_state)
        self.assertIn("`authority=external-merge-required`", packets)
        self.assertIn("A review wait never creates a handoff", packets)
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
        self.assertIn("granted-by-authorized-user", helper)
        self.assertIn("--expected-task-termination", helper)
        self.assertIn("--expected-task-adoption", helper)
        self.assertIn("recover-takeover", combined)
        self.assertIn("stale heartbeat alone", runtime.lower())
        self.assertIn("fixed five-minute stale threshold", compact_runtime)
        self.assertIn("current schema-5 claims", compact_runtime)
        self.assertIn(
            "Do not import, migrate, rename, dual-read, dual-write, retire, or delete",
            compact_runtime,
        )
        self.assertNotIn("claim retire-legacy", combined)
        self.assertNotIn("--takeover-policy", combined)
        self.assertNotIn("takeover-authorized", combined)

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
        self.assertIn("adopt each original task", worker.lower())
        self.assertIn("inability to adopt or resume it is a blocker", worker)

    def test_takeover_is_prepared_recoverable_and_self_contained(self) -> None:
        skill = " ".join(self.read("SKILL.md").split())
        run_state = " ".join(self.read("references/run-state.md").split())
        recovery = " ".join(
            self.read("references/recovery-validation.md").split()
        )
        worker = " ".join(self.read("references/worker.md").split())
        options = self.read("references/options.md")
        helper = self.read("scripts/active-root-claim")

        self.assertIn("prepared-takeover journal before it deletes any prior claim", skill)
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
            '"goal_evidence_ref"',
            '"managed_checkouts"',
            '"task_model"',
            '"target_branch_name"',
            '"baseline_revision"',
        ):
            self.assertIn(field, helper)
        self.assertIn('"ledger_ref"', helper)
        self.assertIn('"no-task"', helper)
        self.assertIn("candidate claim's validated embedded adoption mapping", worker)
        self.assertIn("prepared-takeover transaction ids", options)
        self.assertNotIn("expected_task_adoption", options)

    def test_reference_load_predicates_cover_takeover_and_partial_bundles(self) -> None:
        skill = " ".join(self.read("SKILL.md").split())
        recovery = " ".join(
            self.read("references/recovery-validation.md").split()
        )
        workspace = " ".join(
            self.read("references/multi-repo-workspace.md").split()
        )

        self.assertIn("prepared takeover", recovery)
        self.assertIn("before a candidate JSON state exists", recovery)
        for text in (skill, workspace):
            self.assertIn("partial and integration", text)
            self.assertIn("single-repository", text)

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
                ["surface", "authorization", "snapshot", "delivery-preflight", "intake"],
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
            permission="granted-by-authorized-user",
            bundle_ready=True,
        )
        self.assertEqual(outcome, "accepted")
        self.assertEqual(
            observations,
            ["surface", "authorization", "snapshot", "delivery-preflight", "intake"],
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
            "## Mandatory Runtime Surface Gate", 1
        )[1].split("## Mandatory Run Authorization", 1)[0]
        self.assertIn("Goal pause/resume", surface_contract)
        self.assertIn("not part of this runtime contract", " ".join(surface_contract.split()))
        compact_surface = " ".join(surface_contract.split())
        for token in (
            "Call `get_goal` once in the root",
            "`blocked` Goal",
            "`new-root-required`",
            "before authorization",
            "do not read sources, preflight, claim",
            "Prior artifacts stay untouched",
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
        self.assertIn("domain-knowledge closeout", skill)
        self.assertIn("references/spec-backed-delivery.md", skill)

    def test_knowledge_targets_must_fit_final_issue_execution_scope(self) -> None:
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        skill = " ".join(self.read("SKILL.md").split())

        for contents in (delivery,):
            self.assertIn("repository", contents)
            self.assertIn("repo-relative path", contents)
            self.assertIn("`affected_repositories`", contents)
            self.assertIn("`allowed_paths`", contents)
            self.assertIn("`planning-required`", contents)
        self.assertIn("every `target_surfaces` entry", delivery)
        self.assertIn("intake must not widen the Execution Contract", delivery)
        self.assertIn("references/spec-backed-delivery.md", skill)

    def test_knowledge_closeout_owner_is_graph_final_and_self_contained(self) -> None:
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        skill = " ".join(self.read("SKILL.md").split())

        for contents in (delivery,):
            self.assertIn("remaining", contents)
            self.assertIn("dedicated integration partial", contents)
            self.assertIn("memory_slice=domain-memory", contents)
            self.assertIn("domain_operation=implementation-closeout", contents)
            self.assertIn("after integrated behavior", contents)
            self.assertIn("planning-required", contents)
        self.assertIn("domain-knowledge closeout", skill)
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

        for contents in (delivery, gates, worker):
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
        packets = " ".join(self.read("references/run-state-packets.md").split())
        gates = " ".join(self.read("references/gates.md").split())
        worker = " ".join(self.read("references/worker.md").split())
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
        skill = " ".join(self.read("SKILL.md").split())

        self.assertIn("earlier-only dependencies", skill)
        self.assertIn("strictly earlier generated issue", delivery)
        self.assertIn("reject self, same-ID, and later-ID dependencies", delivery)

    def test_github_shorthand_is_normalized_for_claim_and_task_identity(self) -> None:
        skill = " ".join(self.read("SKILL.md").split())
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        packets = self.read("references/run-state-packets.md")

        for text in (skill, delivery):
            self.assertIn("owner/repository#N", text)
            self.assertIn("https://github.com/owner/repository/issues/N", text)
        self.assertIn("use the URL as the claim/task source id", skill)
        self.assertIn("Preserve the shorthand as the authoritative artifact ref", delivery)
        self.assertIn("source_spec_ref", packets)
        self.assertIn("source_id", packets)
        self.assertIn("Never pass GitHub shorthand directly to the helper", skill)

    def test_local_move_is_scoped_and_revalidated_at_the_resulting_head(self) -> None:
        delivery = " ".join(
            self.read("references/spec-backed-delivery.md").split()
        )
        gates = " ".join(self.read("references/gates.md").split())
        recovery = " ".join(
            self.read("references/recovery-validation.md").split()
        )
        packets = " ".join(self.read("references/run-state-packets.md").split())
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
        self.assertIn("planned_done_ref", packets)
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
        packets = " ".join(self.read("references/run-state-packets.md").split())
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
        self.assertIn('"is_draft": false', packets)
        for field in ("pr_number", "pr_url", "head_sha", "base_ref", "merge_base_sha"):
            self.assertIn(field, packets)
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

    def test_ready_transition_resolves_and_reuses_exact_pr_identity(self) -> None:
        worker = " ".join(self.read("references/worker.md").split())
        for token in (
            "Outside the ready mutation's shell chain",
            "exact number and URL",
            "`gh pr ready <number> --repo <owner/repo>`",
            "Selectorless or branch inference is forbidden",
            "Re-read the same number; require unchanged URL and `isDraft=false`",
        ):
            self.assertIn(token, worker)
        self.assertLess(worker.index("exact number and URL"), worker.index("gh pr ready <number>"))
        self.assertLess(worker.index("gh pr ready <number>"), worker.index("Re-read the same number"))
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
        skill = " ".join(self.read("SKILL.md").split())
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
        self.assertIn("never serialize around the collision", skill)
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

        for path in (
            "SKILL.md",
            "references/codex-review-closeout.md",
            "references/spec-backed-delivery.md",
            "references/worker.md",
        ):
            contents = " ".join(self.read(path).split())
            self.assertIn("local", contents.lower(), path)
            self.assertIn("delivery", contents, path)
            self.assertIn("invalidat", contents, path)
            self.assertIn("$autoreview", contents, path)
            self.assertIn("ready-for-review", contents, path)
            self.assertIn("current-revision review", contents, path)

    def test_metadata_is_manual_and_compact(self) -> None:
        skill = self.read("SKILL.md")
        metadata = self.read("agents/openai.yaml")
        self.assertEqual(ROOT.name, "implement-feature")
        self.assertIn("name: implement-feature", skill)
        self.assertIn("explicitly invokes $implement-feature", skill)
        self.assertIn("merge-ready-but-unmerged pull requests", skill)
        self.assertIn('display_name: "Implement Feature"', metadata)
        self.assertIn("allow_implicit_invocation: false", metadata)
        skill_bytes = len(skill.encode("utf-8"))
        self.assertLessEqual(skill_bytes, 16_000)
        self.assertLessEqual((skill_bytes + 3) // 4, 4_000)
        successful_path = (
            "SKILL.md",
            "references/options.md",
            "references/task-model-policy.md",
            "references/spec-backed-delivery.md",
            "references/run-state.md",
            "references/run-state-packets.md",
            "references/cache-lifecycle.md",
            "references/worker.md",
            "references/gates.md",
            "references/codex-review-closeout.md",
        )
        self.assertLessEqual(
            sum(len(self.read(path).encode("utf-8")) for path in successful_path),
            92_500,
        )
        multi_repository_path = successful_path + (
            "references/multi-repo-workspace.md",
        )
        self.assertLessEqual(
            sum(
                len(self.read(path).encode("utf-8"))
                for path in multi_repository_path
            ),
            96_500,
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
