# Visible ChatGPT Desktop App Feature Spec Task

## Assignment

Create exactly one visible App task per implementation-eligible Feature Spec.
Record its Spec ref and title, task id and title, managed repository checkout
map, resolved task model and thinking, profile decision reason, allowed paths,
Goal evidence, lifecycle state, changed files, validation, commits, PRs,
current-revision review, CI, tracker-closeout preparation, blockers, and next
action.

Task ids, managed checkouts, Goals, PR count, and internal subagent topology are
derived runtime evidence. They are not user options.

## Task Model Profile

Use the exact per-Spec profile resolved under `task-model-policy.md`. Pass its
model and thinking value to `codex_app__create_thread` when creating the visible
task and to every `codex_app__send_message_to_thread` call used to steer or
resume it. Never omit, substitute, or recompute either value after task
creation. Recovery and takeover preserve the recorded profile on the original
task; they never create a replacement to change it.

This profile governs the root-owned visible task. It does not create a separate
model-selection contract for the task's bounded internal subagents.

## Task Display Title

Give every created task exactly one root-owned display-title prefix. Resolve one
semantically relevant emoji from the validated Feature Spec title and its
dominant user-facing goal, use `🛠️` when no clearer choice exists, then
format `task_title` as `<emoji> <exact authored Feature Spec title>`. The prefix
is one emoji grapheme followed by one space; preserve the authored title
unchanged even when it already contains emoji. This is fixed derived UI
evidence, not a user option, Feature Spec field, source fingerprint, claim key,
scheduling key, branch component, or recovery identity.

Resolve and persist `task_title` once after the Spec enters the selected
DISPATCH set and before calling `codex_app__create_thread`. Reuse that exact
value for the task's lifetime; never recompute it during monitoring, steering,
recovery, or takeover. Apply the title through the root-owned App surface, not
through the worker prompt:

1. Create the managed visible task with `codex_app__create_thread` and its exact
   task profile.
2. If worktree setup returns only `clientThreadId`, record that creation evidence
   and wait for the existing managed-creation flow to expose the concrete
   `threadId`; never create another task.
3. Record the concrete task ref, call `codex_app__set_thread_title` with the
   persisted `task_title`, and observe the exact live title.
4. Advance beyond `created` only after both the title and assignment Goal are
   verified.

If creation fails before a task exists, retain the resolved title for the same
dispatch retry. If title mutation or observation fails after creation, record
the task ref, desired title, and blocker; resume and repair that same task
instead of creating a replacement. The worker must never rename its own task.

## Fixed Actions

Every task receives the same action set:

```text
inspect, edit, validate, complete-domain-closeout, move-local-issues-to-done,
commit, push, publish-or-update-pull-request, run-autoreview,
mark-ready-for-review, request-review, poll-review, fix-review, run-ci,
prepare-tracker-closeout, check-mergeability, report
```

Allowed paths narrow edit scope; they do not alter this action set or grant
scope expansion. The run authorization disclosed and covers these actions for
the accepted bundle. The task may not edit the orchestration ledger, manage
sibling or root tasks, change branch or PR strategy, merge, release, deploy,
perform post-merge closure, or change target-repository instructions.

For a local Markdown issue, the move action is legal only when its tracker-owning
repository and exact active plus derived `done/` paths are already present in
the Execution Contract and exposed by the App-managed checkout.

Give GitStack only exact PR, `review_operation`, and `mutation_mode=apply` for an
authorized mutation. Before `poll-review`, report tuple/request evidence and
require root-issued `revision_key`, `wait_started_at`, and `wait_deadline`.
At launch set `wait_invoked_at=now`, compute
`provider_timeout=floor(wait_deadline-now)`, and start GitStack with 10s/30s
bounds in one local step with no root round-trip. If nonpositive, check once.
Report invocation/timeout afterward; never reuse, default, or segment it.

For local commit actions, use `$gitstack:git-commit` and keep
`commit_kind=regular` unless target-repository instructions require a targeted
fixup. Review or `$autoreview` feedback alone never selects a fixup. A required
`commit_kind=fixup|amend-fixup` must name one exact `target_commit`; ambiguous or
cross-commit corrections stop for owner direction. Never autosquash or rewrite
the published branch. Any resulting head change invalidates current-revision
review and CI evidence and repeats the fixed final gates.

## Managed Checkout

Create the task through the App-managed worktree target before implementation.
Record each repository id, checkout path, target branch, Git top-level, baseline
revision, and isolation proof. A multi-repository Spec stays one task and its
managed workspace must expose every required child checkout.

If any checkout is missing or not isolated, stop as blocked. Never create,
remove, or repair raw Git worktrees, rotate the caller checkout, or fall back to
root or background implementation.

## Goal Contract

The initial prompt requires a newly created task to call `create_goal` before
work. Its assignment-scoped objective contains the exact Feature Spec,
repositories and allowed paths, acceptance criteria, validation, and fixed
terminal result `pull-request-ready-for-merge-but-not-merged`. Do not pass
`token_budget`.

On recovery, call `get_goal`. A nonterminal task requires an active objective
and fingerprint matching the recorded Goal evidence before implementation
resumes. A task already recorded at the fixed terminal result requires matching
completed Goal evidence and must not resume implementation. Never call
`create_goal` for either recovery path. The root verifies that evidence and the
exact live task title before advancing beyond `created` or resuming a
nonterminal task. If any required Goal tool is unexpectedly absent after task
creation, report an
`unsupported-runtime` blocker on that same task. Never record an objective
fallback or create a replacement task.

Call `update_goal` with `status=complete` only after the fixed terminal result
is proven. Temporary blockers and resumable handoffs leave nonterminal task
Goals active; already-terminal task Goals remain complete. If recovery finds
the terminal proof recorded while this Goal is still active, revalidate that
proof, call `update_goal` with `status=complete`, persist the evidence, and
report without resuming implementation. If the Goal already completed but its
evidence write was interrupted, verify and persist that result without calling
`update_goal` again.

## Execution

Implement only the accepted bundle and prove substantive acceptance and
integration. For a nonempty final-issue `knowledge_delta`, complete the exact
Project Memory implementation-closeout after integration and require
`capture_outcome=captured`, every supplied accepted item and required named
target reconciled, named verified destinations, and complete documentation-diff
verification. `deferred`, `no-durable-change`, or a rejected or contradicted
accepted item blocks the task pending an owner decision or separately authorized
planning/implementation correction. For local tracker
artifacts, move each issue to its scoped `done/` path on the delivery branch.
Report the exact tracked rename so the root can atomically advance the issue
source snapshot from its active ref to the predeclared done ref; do not edit the
body during the move. Commit/push and publish/update each PR against the
discovered default branch. Outside the ready mutation's shell chain, record its
exact number and URL. Rerun validation and `$autoreview`, then convert any draft
to ready-for-review only by exact identity; a `gh` fallback is
`gh pr ready <number> --repo <owner/repo>`. Selectorless or branch inference is
forbidden. Re-read the same number; require unchanged URL and `isDraft=false`.
After that nonterminal transition, request mandatory current-revision review
through Codex, fix actionable findings, pass CI, prepare derived tracker
closeout, and check current GitHub mergeability. Declare terminal merge-ready
only while each PR lifecycle is `OPEN`, mergeability is conflict-free, and every
required base update, approval, and merge-queue eligibility condition passes.
Unknown or pending mergeability blocks; never enqueue or merge. Any later head
or base change repeats the invalidated final gates.
Follow the generated issues' dependency order inside the task; do not create a
task per issue.

Canonical states are `created`, `implementing`, `validating`, `draft-pr`,
`marking-ready-for-review`, `review-polling`, `fixing-review`, `ci`,
`preparing-tracker-closeout`, `checking-mergeability`, `merge-ready`, `blocked`,
and `needs-owner`.

The root reads current task evidence before steering. A correction names the
observed drift, expected next state, and preserved scope. A stale or failed task
is resumed in the same visible task only after evidence is recorded. Restore
the recorded `task_title` on that same task when its live title drifts. If it
cannot be resumed, stop as blocked; never create a replacement task for that
Spec.

After an authorized stale-root takeover, use the candidate claim's validated
embedded adoption mapping and cross-check any available prior ledger. Adopt the
exact original task ref for every previously dispatched Spec and resume it after
verifying its Goal and managed checkouts. Across the adopted set, no task ref or
managed `(repository, checkout)` pair may belong to two Specs. An explicit
embedded no-task entry with the exact pre-CLAIM profile is required before first
creation, and that first creation must use the embedded profile without
reclassification. Do not create a task when embedded, prior-ledger, or live App
evidence records one for the Spec;
inability to adopt or resume it is a blocker.

## Internal Subagents

The task may use bounded internal subagents when useful. They inherit its paths
and fixed flow, remain inside the same Feature Spec slot, and report through the
visible task. They never receive separate portfolio or tracker authority.

## Prompt

```text
Own this Feature Spec through pull-request-ready-for-merge-but-not-merged.

Canonical task source id: <canonical claim/task source id>
Authoritative Feature Spec: <authored source_spec_ref and title>
Feature slug: <feature_slug>
Managed repositories: <repository, checkout, target branch, baseline>
Allowed paths: <repository-qualified paths>
Scope and acceptance: <exact requirements and acceptance refs>
Dependencies: <verified merged cross-Spec dependencies>
Validation and integration gates: <commands and proof>
Knowledge closeout: <exact final-issue delta or none>

If this is a new task, call `create_goal` with the exact assignment objective
before implementation and omit `token_budget`. If this is a resumed task, call
`get_goal` and verify the active objective before continuing nonterminal work.
If this task is already terminal, verify its completed Goal and report without
resuming implementation; if its recorded terminal proof precedes an unfinished
Goal completion transition, finish that transition only. Work only in the
managed checkouts. Use fixed actions and the root-issued review deadline; report its
arguments and any internal subagents.
Do not edit the ledger, manage sibling tasks, widen scope, change delivery
strategy, merge, release, deploy, or perform post-merge closure. Continue until
every affected PR is ready to merge or report a concrete blocker. Call
`update_goal` with `status=complete` only after the terminal result is proven.
```

## Report

Report task and Goal evidence, state, managed checkouts, changed files,
the exact task display title and observation evidence, task model, thinking
value, and profile decision reason, validation, commits, PR URLs, full current
revision tuples, review disposition and wait assignment/invocation, CI, current PR
lifecycle/conflict/mergeability state, required base-freshness, approval state,
merge-queue eligibility, and the observation tuple/time (or exact blocker),
prepared tracker closeout, internal subagents, blockers, drift, and next action.
When a knowledge delta exists,
report its actual `capture_outcome`, delta fingerprint, every verified named
destination, documentation-diff fingerprint, and relevant implementation
revision tuples, or the exact closeout blocker. Only the root accepts lifecycle
transitions.
