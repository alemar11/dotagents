---
name: implement-feature
description: Implement dependency-ready durable Feature Specs in visible ChatGPT desktop app tasks and deliver reviewed, merge-ready pull requests. Use only when explicitly invoked.
---

# Implement Feature

## Contract

Use this skill only after the owner explicitly invokes `$implement-feature` in
the ChatGPT desktop app. Consume durable execution-ready Feature Specs; never
plan, repair, rewrite, or publish planning artifacts.

One run owns the dependency-ready frontier selected from the requested bundle.
Every executable Feature Spec in that frontier must name exactly one affected
Git repository and becomes one visible App task in that repository's App-managed
worktree. Cross-Spec dependencies must already be merged and integration-proven;
leave blocked Specs for a later invocation. Never merge on their behalf.

The root owns one lifecycle Goal, the task queue, durable state, provider
operations, reconciliation, and final verification. Workers implement and
report only. Neither root nor workers create raw Git worktrees, implement in the
root checkout, use background execution, merge, enqueue, deploy, release, or
perform post-merge closure.

## Fast Start

Load `references/root-bootstrap.md`. Before persistent state, validate the
source and ready frontier, map each repository through the App project list,
perform only the repository/branch/collision reads needed to start, disclose
the exact scope, and resolve authorization. Defer CI, review access, branch
rules, approvals, mergeability, and merge-queue reads to publication or
closeout, where they must be fresh.

Start fresh schema-1 state with `scripts/run-state`, then create or adopt the
root Goal before creating workers. The state database is durable user state at
`$XDG_STATE_HOME/dotagents/skills/implement-feature/run-state-v1.sqlite3` or
`~/.local/state/dotagents/skills/implement-feature/run-state-v1.sqlite3`. It is
not a cache. This hard cut has no migration, legacy reader, archive format, or
compatibility aliases.

## App Orchestration

Load `references/app-orchestration.md` before creating the Goal or a task. Use
the current App task and Goal tools exactly as routed there. Inherit the App's
model and thinking defaults unless the owner explicitly requested particular
values.

Keep at most three live worker tasks. Fill slots in canonical assignment order,
skipping work whose paths overlap a live task. For each task:

1. Journal creation, create the worktree task, resolve its exact identity, set
   and read back its title, then bind the task and checkout in `run-state`.
2. Send the baseline-only bootstrap prompt, run the accepted baseline, and
   record `task baseline`.
3. Journal and send the explicit implementation-authorized message, then
   record `task authorize`. No edit may precede this step.
4. Monitor with bounded waits and authoritative task reads. Load only the
   current phase reference: `worker-implementation.md`,
   `worker-validation.md`, `worker-publication.md`, the review references, or
   `worker-closeout.md`.
5. Record `task ready` only after the exact-head, reviewed, CI-classified,
   merge-ready PR handoff is independently reproducible. A ready task frees one
   slot; immediately dispatch the next non-conflicting planned assignment.

The successful result is `pull-request-ready-for-merge` for every assignment
in this run. Complete and read back the root Goal only after all assignments
are independently verified, then finish state and release claims. See
`references/gates.md`.

## Operations And Recovery

Before any irreversible App, GitStack, AutoReview, or provider mutation, call
`run-state operation begin`. Launch only when it returns
`launch_authorized=true`, then call `operation finish`. Never replace or
relaunch an `unknown` operation; reconcile the same identity. Read the complete
paginated journal during recovery.

Load `references/recovery-validation.md` after compaction, an active claim, a
missing task, or state trouble. Old-version and missing preimplementation state
normally start over after authoritative App/project/Goal readback proves that
no worker can still mutate. Once any task received implementation authority,
preserve its work and recover or stop for the owner; never discard it as a
version repair.

Return concise state-derived source, assignment, Goal, task/worktree, changed
path, validation, commit, PR/head, review, CI, tracker/domain-closeout,
mergeability, warning, blocker, and next-action evidence.

## Reference Routing

- Intake and authorization: `references/spec-backed-delivery.md`,
  `references/options.md`, and `references/multi-repo-workspace.md` only when
  the connected bundle spans repositories.
- App and task state: `references/app-orchestration.md`,
  `references/worker.md`, and `references/baseline-validation.md`. Load
  `references/run-state.md` only for CLI errors, recovery, exact command-shape
  lookup outside the normal path, or maintenance.
- Implementation: `references/worker-implementation.md` and
  `references/worker-validation.md`.
- Publication: `references/worker-publication.md` and
  `references/review-mutation-authority.md`.
- Review: `references/autoreview-fix-loop.md`,
  `references/codex-review-closeout.md`,
  `references/review-reconciliation.md`,
  `references/review-thread-resolution.md`, and
  `references/worker-review-fix.md`.
- Closeout or recovery: `references/worker-closeout.md`,
  `references/gates.md`, and `references/recovery-validation.md`.
