# Implement Feature Authorization Contract

## Syntax And Hard Cut

Behavior fields use snake_case and enum values use lower-kebab. Resolve prose
directly to canonical values and persist only those values. Reject aliases,
retired fields, unknown structured inputs, and merge authorization fields.

This file owns every user-controlled App orchestration field.

## Registry

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `visible_app_task_permission` | `not-requested`, `granted-by-authorized-user`, `denied-by-authorized-user` | `not-requested` | Run-scoped consent for one visible task per executable Feature Spec using the fixed model, reasoning policy, and execution flow. |
| `stale_claim_takeover_permission` | `not-requested`, `granted-by-authorized-user`, `denied-by-authorized-user` | `not-requested` | Run-scoped consent to replace complete verified-stale claim scopes and adopt their task refs. |

## Standard Run Authorization

For `visible_app_task_permission=not-requested`, state this exact disclosure:

> Each executable Feature Spec is one feature; one plan may create multiple
> visible tasks. This run may change and validate code, push
> commits, create or update pull requests, address Codex review, wait for CI
> when a repository has CI configured,
> prepare hosted issue closeout, and move, commit, and push completed local issue
> files when used. AutoReview sends Git status, staged/unstaged diffs, and every
> non-ignored untracked file to Codex; no extra authorization. Tasks use
> `gpt-5.6-sol`: `medium` by default, `high` for complex multi-part work, and
> `xhigh` for risky or cross-system work. Codex
> waits up to 45 minutes for each requested review. If a review is still pending
> at that deadline, it records a persistent warning on the pull request, reports
> the warning to you, and continues the remaining gates without treating the
> review as clean. A later merge workflow must check for late findings. After Codex
> reserves the work, it automatically deletes valid run-state archives older
> than 180 days; it never plans, expands scope, merges, releases, or deploys.

Then use one `request_user_input`:

| UI field | Exact value |
| --- | --- |
| Header | `Start work?` |
| Question id | `visible_app_task_permission` |
| Question | Start implementation? Codex will create one visible task per feature and prepare merge-ready pull requests. |

| Order | Label | Description | Canonical value |
| --- | --- | --- | --- |
| 1 | `Start implementation (Recommended)` | Use this workflow for the ready specs found in this run. | `granted-by-authorized-user` |
| 2 | `Cancel` | Stop here without starting implementation or changing anything. | `denied-by-authorized-user` |

Define only these answers. The App owns the free-form response; it is never an
implicit grant. Ask after the runtime surface gate. Denial or no answer aborts
without artifacts. The grant never changes target-repository instructions;
model policy stays fixed by `task-model-policy.md`.

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
always requested, with only an evidenced 45-minute pending timeout eligible for
`timeout-accepted`; execution always uses one visible task per Feature Spec,
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
