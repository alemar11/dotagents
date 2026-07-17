# Visible Codex App Feature Spec Task

## Assignment

Create exactly one visible App task per implementation-eligible Feature Spec.
Record its Spec ref and title, task id and title, managed repository checkout
map, allowed paths, Goal evidence, lifecycle state, changed files, validation,
commits, PRs, current-revision review, CI, tracker-closeout preparation,
blockers, and next action.

Task ids, managed checkouts, Goals, PR count, and internal subagent topology are
derived runtime evidence. They are not user options.

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

Provider skills receive only provider-owned primitives. For GitStack review
operations, derive the exact PR and `review_operation` from the current fixed
phase and pass `mutation_mode=apply` only for an authorized mutation. These are
internal call arguments, not Feature Spec fields, worker action lists, or user
options.

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

The initial prompt requires the task to create or resume an
assignment-scoped Goal before work. The Goal contains the exact Feature Spec,
repositories and paths, acceptance criteria, validation, and fixed terminal
result `pull-request-ready-for-merge-but-not-merged`. The root verifies Goal
evidence before advancing beyond `created`. Record an exact objective fallback
only when the task runtime reports no Goal tool.

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
body during the move. Commit and push the complete change set, publish or update
every repository PR against its discovered default branch, then rerun final
validation and non-trivial `$autoreview` at the resulting head, then convert any
draft to ready-for-review (`isDraft=false`).
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
is resumed in the same visible task only after evidence is recorded. If it
cannot be resumed, stop as blocked; never create a replacement task for that
Spec.

After an authorized stale-root takeover, use the candidate claim's validated
embedded adoption mapping and cross-check any available prior ledger. Adopt the
exact original task ref for every previously dispatched Spec and resume it after
verifying its Goal and managed checkouts. Across the adopted set, no task ref or
managed `(repository, checkout)` pair may belong to two Specs. An explicit
embedded no-task entry is required before first creation. Do not create a task
when embedded, prior-ledger, or live App evidence records one for the Spec;
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

Create or resume the assignment Goal before implementation. Work only in the
managed checkouts. Use the fixed action set and report any internal subagents.
Do not edit the ledger, manage sibling tasks, widen scope, change delivery
strategy, merge, release, deploy, or perform post-merge closure. Continue until
every affected PR is ready to merge or report a concrete blocker.
```

## Report

Report task and Goal evidence, state, managed checkouts, changed files,
validation, commits, PR URLs, full current revision tuples, review disposition,
CI, current PR lifecycle/conflict/mergeability state, required base-freshness,
approval state, merge-queue eligibility, and the observation tuple/time (or
exact blocker), prepared tracker closeout, internal subagents, blockers, drift,
and next action. When a knowledge delta exists,
report its actual `capture_outcome`, delta fingerprint, every verified named
destination, documentation-diff fingerprint, and relevant implementation
revision tuples, or the exact closeout blocker. Only the root accepts lifecycle
transitions.
