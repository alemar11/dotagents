# Implement Feature Authorization

## Registry

This version accepts one user-controlled field:

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `visible_app_task_permission` | `not-requested`, `granted`, `denied` | `not-requested` | Authority for the disclosed visible tasks and implementation flow. |

Reject aliases, unknown structured fields, compatibility fields, merge
authority, and natural-language values in structured input.

## Resolution

Resolve `visible_app_task_permission=granted` without a redundant question when
the owner explicitly invokes `$implement-feature` and orders implementation of
an identified durable Feature Spec or bundle. Bind the grant after read-only
intake to the exact dependency-ready frontier and scope disclosure.

Inspection, evaluation, planning, conditional intent, or generic permission to
use tasks leaves permission `not-requested`. An explicit stop is `denied`.

## Disclosure

Before `run start`, disclose:

> Each dependency-ready executable Feature Spec creates one visible App task in
> its repository's managed worktree. This run may edit and validate the listed
> paths, commit and push changes, create or update pull requests, run AutoReview
> and current-head Codex review, address findings, wait for configured CI, and
> prepare tracker closeout. Commands use the App's normal sandbox and approval
> surface. Durable orchestration state is stored in the user state directory.
> The run never plans, widens scope, merges, deploys, releases, or performs
> post-merge closure.

Render sorted source refs and fingerprints, repositories and App project IDs,
one Spec/task/title per repository, target branches, allowed paths, validation
commands, Goal objective, blocked next-frontier refs, and expected PR count.

When permission remains `not-requested`, ask one question:

| UI field | Exact value |
| --- | --- |
| Header | `Start work?` |
| Question id | `visible_app_task_permission` |
| Question | Start implementation? Codex will create visible worktree tasks for the ready Feature Specs and prepare merge-ready pull requests. |

Offer `Start implementation (Recommended)` as `granted` and `Cancel` as
`denied`. Denial or silence creates no state, task, new Goal, repository write,
or provider mutation.

Reauthorize only when accepted source, repository, branch, path, validation,
task, Goal, or publication scope changes. Do not ask merely because an
old-version or missing preimplementation run is restarted with the identical
validated scope.

## Fixed Inputs And Results

App-managed worktrees, one root Goal, platform-default task model unless
explicitly requested, at most three live tasks, current-head reviews,
configured CI classification, and no merge are invariants.

Sources, repositories, paths, branches, acceptance criteria, validation,
integration gates, and optional domain closeout are Feature Spec data. App
project IDs, task IDs, worktrees, Git heads, PRs, provider results, and Goal
state are derived observations.
