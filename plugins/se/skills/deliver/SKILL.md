---
name: deliver
description: "Orchestrate isolated workers in one repository to deliver specs, issues, or bounded requests through ready PRs."
---

# Deliver

Deliver verified ready PRs for selected scope in one repository. The current task
orchestrates; isolated workers implement, validate and publish. Even one bounded
change uses a worker. Follow shared [execution scope](../../references/execution-scope.md).

The orchestrator is designed for `gpt-6-astra` with caller-configured reasoning.
Honor explicit overrides without changing task settings or replacing the
coordinator. Once scope is known, use `🚚 Deliver · <scope>` when supported;
titles are metadata and never gate execution.

## Select and assign

Accept saved specs, selected issues or bounded requests. Resolve one repository
before dispatch, defaulting to the current repository when it matches. A saved
spec selects its whole scope unless the caller names a subset; read its task
contracts, prerequisites, shared contracts and accepted decisions. Apply shared
[readiness states](../../references/states.md) for eligibility and duplicate pickup.

For requests spanning repositories or requiring external inputs, read
[external prerequisites](references/integration.md#external-prerequisites).
Other repositories remain outside implementation scope. Do not implement
unselected prerequisites. Backlog discovery, monitoring and queue persistence
belong to the caller.

Create bounded assignments around verifiable outcomes, not new tracker issues.
Prefer narrow end-to-end behavior over separate layer assignments when those
layers must work together. Keep coupled work together; each assignment needs an
acceptance boundary, not its own PR.

Default to one active worker implementing and publishing one coherent outcome
on one branch. Add isolated workers when independent assignments can reduce
elapsed time. Keep dependent or overlapping writes serial unless isolation and
required inputs are established. Choose PR topology before dispatch. Read
[integration.md](references/integration.md) for dependencies, stacks, combining
contributions or topology changes. Integration is needed only when separate
branches must combine into one PR; parallelism alone requires neither a stack
nor an extra PR.

Read the [runtime surface](../../references/codex-runtime-surface.md), then
[workers.md](references/workers.md) before creating or assigning workers. Supply
complete assignments through required CI and publication, or validated commits
for an assigned integration worker. The worker contract owns transport, profiles,
checkout verification, writer isolation, reuse and result evidence.

## Authority and execution

Explicit invocation authorizes required worker creation, scoped branches,
implementation, commits, pushes, PR publication/readiness, integration of assigned
commits and CI corrections. Reuse that authority across continuations without
phase-by-phase approval. Ask only for material unresolved scope or authority;
keep independent selected work moving.

User restrictions win. No-push work ends with a local handoff and PR delivery
explicitly incomplete; never ask to override that restriction. Landing PRs,
deployment, releases, production actions, direct issue closure, destructive
recovery and scope expansion remain unauthorized.

Workers compose Implement, then applicable G workflows. Before hosted access or
publication, follow [publication and readiness](references/workers.md#publication-and-readiness),
including dependency preflight and hosted-content safety. Independent review is
not mandatory; user/repository-required reviews apply and optional reviews run
only when requested. For review findings, follow
[requested reviews](references/workers.md#requested-reviews).

## Source references

Supply exact source references and each assignment's contributing outcome.
Saved specs are GitHub issues; local documents may inform bounded requests but
are not tracked specs. Worker assignments never acquire issue identities.

Supply G Send the exact selected issues whose accepted scope the PR fully
completes, using closing references for them. A parent spec qualifies only when
that PR completes its whole scope. Use ordinary links for partial contributions,
prerequisites and context. Verify published references against delivered scope;
a finished assignment alone proves no issue complete. For combined or stacked
work, apply the [integration linkage rules](references/integration.md#source-references-through-integration-and-stacks).

Closing references permit later automatic closure through the PR. Leave issues
open at the ready-PR handoff and never claim closure before it occurs. Source
progress is report-only unless requested, except the readiness handoff below.

## Coordinate and finish

Wait for results, attention requests or meaningful changes without busy-polling
or generic continuation messages. Correct scoped failures while evidence shows
progress; repeated unchanged failures or unresolved authority/decisions yield a
precise blocker. Continue independent work.

Accept [worker results](references/workers.md#assignment-and-result) against current
PR/CI facts and selected outcomes, including assembled behavior where required.
Reuse valid evidence; repeat or broaden checks only for changes, failures or
evidence gaps. Changed scope, base or HEAD invalidates affected evidence.

Delivery completes only when all required PRs are non-draft, required CI passes,
selected outcomes and required reviews are verified, and source links are correct.
Draft, pending, partial and blocked results are incomplete. Ready PRs stay
unmerged. Later merge/deployment conditions are handoff information unless
explicitly required for readiness; neither invent nor weaken acceptance gates.

For fully delivered saved specs, apply and verify the human-ready transition
under [readiness states](../../references/states.md) using G GitHub Issues.
Partial/blocked specs do not transition; metadata failure does not requeue
implementation. Direct requests need no readiness artifact.

Return ready PR links and verified outcomes, then material limitations or resume
inputs. For interruption, uncertainty or partial results, follow
[recovery](references/workers.md#recovery). Preserve worktrees and leave App workers
visible by default. No mandatory retrospective, token accounting, claims,
scheduling graph or ledger.

## Skill Dependencies

Bundled [Implement](../implement/SKILL.md) owns local implementation and validation.
Installed `g@alemar11` owns Git/GitHub publication, CI and optional stacks; load
only needed workflows. The orchestrator owns assignments, integration and acceptance.
