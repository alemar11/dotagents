# Visible Codex App Feature Spec Task

## Task Fields

Record Feature Spec ref/title, visible task id/title, managed workspace root,
repository checkout map, allowed actions and paths, Goal objective and status,
capability snapshot, internal subagents, lifecycle state, changed files,
validation, PR/review/CI evidence, blockers, and next action.

The task id, managed checkout, and Goal are derived runtime evidence. They are
not human-selectable options.

## Session Option Resolution

Worker authorization is resolved per workstream and session by the root. The
root resolves `worker_allowed_actions` per workstream and records them in the
assignment; source artifacts never grant worker actions by implication.

```text
feature_spec_task_assignment: <canonical Feature Spec ref>
worker_allowed_actions: <exact comma-separated actions>
root_implementation_fallback: forbidden
```

## Worker evidence

Record the task id, managed checkout, Goal evidence, allowed actions,
capability snapshot, internal subagent topology, state transitions, validation,
delivery artifacts, blockers, and any fallback reason. Root-owned or simulated
execution may appear only as imported historical evidence; this App adapter
cannot select either as an implementation location.

## Authorization

Task creation requires `visible_app_task_permission=granted-by-authorized-user`.
That grant selects mandatory one-task-per-Feature-Spec execution. The task
inherits only root-resolved actions and delivery permissions. It cannot expand
scope or authority. Create exactly one visible task per Feature Spec.

Every task receives the fixed terminal target
`pull-request-ready-for-merge-but-not-merged`. It must implement, validate,
commit, publish or update a draft PR, complete current-revision review and CI,
resolve actionable feedback, and mark the PR ready. It may report only
`merge-ready`, `blocked`, or `needs-owner` as its terminal lifecycle state.

Allowed actions are independent: inspect, edit, validate, commit, push,
publish-pull-request, mutate-named-issue, request-review, poll-review, fix-review,
mark-ready, and report. Allowed paths narrow an action and never grant another.

## Managed Checkout

Create the task through the App's managed worktree target before implementation.
Record every repository path, branch, Git top-level, and isolation proof. For a
multi-repository Spec, the managed task workspace must expose all child
checkouts. If any required checkout is missing or not isolated, stop and
report the App run as blocked.

The App adapter never creates, removes, or repairs raw Git worktrees and never
rotates the caller checkout.

## Goal Contract

The initial prompt contains the exact assignment and fixed PR-ready target
and requires the task to create or resume that Goal before work. The root reads
the task and verifies reported Goal evidence before advancing beyond `created`.
Record a fallback objective only when the task reports that its runtime has no
Goal tool.

## Lifecycle

Canonical states are `created`, `implementing`, `validating`, `draft-pr`,
`review-polling`, `fixing-review`, `ci`, `awaiting-upstream-merge`, `resyncing`,
`marking-ready`, `merge-ready`, `blocked`, `needs-owner`, and
`replaced`.

The root reads before steering. A correction names current drift, expected next
state, and preserved authority. A failed or stale task is resumed or replaced
after evidence is recorded; no root/background implementation fallback exists.

## Internal Subagents

The task decides whether bounded internal background subagents materially help.
They inherit the task scope and authority, stay inside the Feature Spec slot,
and report through the task. The task reports ids, scopes, outcomes, and serial
or parallel topology.

## Prompt

```text
You own one visible Codex App Feature Spec task through the fixed terminal
target `pull-request-ready-for-merge-but-not-merged`.

Feature Spec: <ref and exact title>
Managed repositories: <repo id, checkout, branch>
Scope and acceptance: <exact items>
Allowed actions and paths: <canonical list>
GitHub PR and publication permissions: <resolved values>
Validation and gates: <exact commands and proof>

Create or resume the assignment Goal before implementation. Work only in the
managed checkouts. Use bounded internal subagents when useful and report their
topology. Do not edit the orchestration ledger, manage sibling/root tasks,
change authority or delivery strategy, merge, release, deploy, or close the
source. Continue until every affected repository PR is ready to merge or report
a concrete blocker.
```

## Execution Report

Report task/Goal evidence, current state, repositories, changes, generated
artifacts, validation, commits and PRs, current reviewed SHA, review/CI status,
internal subagents, blockers, drift, and next action. The root verifies current
evidence before accepting any lifecycle transition.
