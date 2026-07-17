# App Orchestrator Authorization Contract

## Syntax And Hard Cut

Behavior fields use snake_case and enum values use lower-kebab. Resolve prose
directly to canonical values and persist only those values. Reject aliases,
retired fields, unknown structured inputs, and merge authorization fields.

This file owns every user-controlled App orchestration field.

## Registry

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `visible_app_task_permission` | `not-requested`, `granted-by-authorized-user`, `denied-by-authorized-user` | `not-requested` | Run-scoped consent to create one visible App task per executable Feature Spec with the disclosed fixed model and adaptive thinking policy, then perform the complete fixed flow. |
| `stale_claim_takeover_permission` | `not-requested`, `granted-by-authorized-user`, `denied-by-authorized-user` | `not-requested` | Exceptional run-scoped consent to stop the disclosed conflicting tasks, replace their complete verified-stale root scopes, and adopt the same task refs. |

Resolve `visible_app_task_permission` only after the mandatory runtime surface
gate proves visible Codex App task creation and App-managed worktree binding.
When missing, ask once. Denial, no answer, or inability to ask aborts without
runtime artifacts.

The visible-task grant authorizes only the disclosed fixed execution flow:
inspect, edit, validate, commit, push, publish or update pull requests, request
and poll current-revision Codex review, fix actionable findings, wait for CI,
prepare tracker closeout, move completed local Markdown issue files to the
configured done folder on the delivery branch after substantive proof, commit
and push the moves, rerun final current-head gates, convert draft pull requests
to ready-for-review, and report. It never
authorizes scope expansion, merge, release, deployment, or target-repository
instruction changes.

Visible-task model and thinking behavior is fixed policy owned only by
`task-model-policy.md`. It is disclosed by the authorization question but is not
another user-controlled field, Feature Spec field, or project configuration
value.

Resolve `stale_claim_takeover_permission` after read-only discovery proves an
atomic claim conflict, stale-heartbeat evidence, every replaced root's complete
repository/source scope, and every recorded task's identity and resumability.
The separate question names those roots, scopes, and tasks and discloses the
exact interruption or termination, full-scope claim replacement, and same-task
adoption. Denial aborts as `needs-owner` before stopping a task. Only a grant
permits the root to stop and verify every task; stale heartbeat alone is
insufficient.

## Fixed Policy And Bundle Data

The successful outcome is always
`pull-request-ready-for-merge-but-not-merged`; current-revision Codex review is
always required; execution always uses one visible task per Feature Spec,
App-managed worktrees, and at most three nonterminal tasks. These are invariants,
not options.

Source refs, feature slugs, repositories, allowed paths, target branch names,
intra-Spec dependency ids, parent Feature Spec dependency rows, acceptance
criteria, validation commands, and an optional final-issue knowledge closeout
are bundle data. A Feature Spec body never carries the knowledge payload. Task
ids, managed checkouts, canonical claim/task source ids, source fingerprints,
discovered default PR bases, PR count, scheduling, tracker closeout, Goal
evidence, review/CI state, prepared-takeover transaction ids, prior-claim
snapshots, and per-Spec task-adoption mappings are derived runtime evidence.
They are never additional user-controlled fields.

For a local Markdown issue, the tracker-owning repository plus its exact active
and derived `done/` paths are required execution-bundle scope. Both paths must
resolve inside an affected Git repository and its App-managed checkout; this is
not another user-controlled field.

Delivery permissions, review requirements or skips, worker action lists,
parallelization, checkout strategies, repository-layout copies, PR-count
strategies, completion methods, closeout enums, lifecycle owners, adapter
fields, and root fallbacks are retired and invalid as structured inputs.
