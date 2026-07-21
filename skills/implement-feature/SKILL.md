---
name: implement-feature
description: Execute ready Feature Spec bundles in visible ChatGPT desktop app tasks through merge-ready-but-unmerged pull requests. Use only when explicitly invoked.
---

# Implement Feature

## Purpose And Authority

Use this skill only when the owner explicitly invokes `$implement-feature` in
the ChatGPT desktop app. It executes complete durable Feature Spec bundles; it
never plans, repairs, regenerates, or publishes planning artifacts.
It is the single App-only implementation adapter for Feature Specs.

Before reading sources or asking permission, verify visible App task creation,
App-managed worktree binding, task-title mutation and observation, and root
`create_goal`, `get_goal`, and `update_goal`. Call `get_goal` once. Missing
capability returns `unsupported-runtime`; a blocked root Goal returns
`new-root-required`. Both stop before source reads, claim, artifacts, tasks, or
mutation. Goal pause/resume and App heartbeat automation are outside this
runtime. Do not create a task to inspect capabilities.

Immediately after that App surface gate, run the installed GitStack parity gate
in `references/gitstack-installation-parity.md` using the exact bundled-skill
path supplied by the App/system skill catalog. Failure stops before source reads,
permission, claim, artifacts, tasks, Goals, or mutation.

After read-only intake succeeds, use the exact disclosure and fixed answers in
`references/options.md`. Continue only with
`visible_app_task_permission=granted`. The grant binds the
exact bundle, repository, path, validation, tool, and execution-scope
fingerprints. Denial or silence creates nothing. Drift before implementation is
`authorization-stale`; an undeclared path after implementation starts is
`needs-owner`. Never ask again, recapture, or widen scope.
Generic delegation, worker assignment, or subagent authority never supplies
this explicit visible-task grant.

## Immutable Safety Contract

- Root owns the claim, typed state, scheduling, reconciliation, cache work,
  deadlines, final verification, and the sole lifecycle Goal. Workers never
  create, read, update, complete, or block Goals.
- Create exactly one visible App task per implementation-eligible Feature Spec
  and at most three nonterminal Spec tasks. Coordination-only artifacts create
  no task. Identity comes from durable refs and fingerprints, never titles.
- Use only App-managed isolated worktrees. Never create raw Git worktrees,
  rotate the caller checkout, implement in root, or use a background worker.
- Keep the accepted bundle, repositories, target branches, allowed paths,
  validation plan, task assignments, and model profiles immutable.
- Use `scripts/active-root-claim` as the sole ownership authority and
  `scripts/ledger-cache` as the sole active-state writer. Unknown, stale,
  unsupported, incomplete, or ambiguous authority and evidence fail closed.
- Require current-scope validation, terminal `$autoreview`, exact-revision
  Codex review, configured CI or explicit `not-configured`, integration,
  tracker-closeout, branch-rule, approval, mergeability, and merge-queue
  eligibility proof. Pending or unknown evidence blocks except the exact
  warning-backed 45-minute `warned-timeout` review result.
- The only successful task result is
  `pull-request-ready-for-merge`. Never enqueue, merge, deploy,
  release, or perform post-merge closure. A later merge request starts a
  separate GitHub workflow.

## Pre-Registration Bootstrap

After the surface gate, load `references/root-bootstrap.md`. It owns the closed
pre-registration order and selects its complete contract set from the already
observed snapshot. Do not infer another route from this file.

Acquire the claim before durable state. Register the immutable accepted
snapshot, authorization, deliveries, profiles, validation plans, and objective.
Do not call Goal mutation tools until the controller selects Goal activation
after the complete atomic baseline is accepted.

## Post-Registration Controller Loop

After registration, `scripts/ledger-cache --json controller next` is the only
phase router:

1. Run `controller next` against the live claim and ledger.
2. Load exactly the returned `required_contracts`. Reuse a contract only when
   the same installation/worktree path plus content SHA is certainly live in
   context.
3. Perform only the selected action through its typed template and owner.
4. Reconcile or record its result through the typed helper, then repeat.

The registry inside `scripts/ledger-cache` is the sole action-to-contract
mapping. Never add a contract from prose or select a phase manually. Contract
caching is transient prompt behavior, not caller authority or persisted state.
Compaction, uncertain retention, recovery, or changed bytes reloads only the
current action set. A missing, stale, extra, or unreadable contract fails
closed.

## Recovery And Output

Resume or takeover only the original recorded tasks after the controller
selects recovery and its complete contracts. Never infer identity, create a
replacement, import archived state, or migrate an unsupported active schema.

Return state-derived source, task, root Goal, managed-checkout, changed-path,
validation, commit, PR/revision, review, CI, tracker/domain-closeout,
mergeability, warning, blocker, and next-action evidence. Pre-claim exits report
zero mutation. Terminal closeout remains staged and fail closed; changed proof
after sealing blocks archive and never reopens a Goal.
