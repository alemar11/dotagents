---
name: deliver
description: "Orchestrate isolated workers in one repository to deliver specs, issues, or bounded requests through ready PRs."
---

# Deliver

Deliver verified ready PRs for selected work in one repository. Keep implementation
with isolated workers and finish the source readiness handoff where applicable.

Use the current task as delivery lead and orchestrator, designed for
`gpt-6-astra` with caller-configured reasoning. Honor explicit profile overrides;
do not change task settings or create a replacement coordinator.
Once scope is known, rename that task to `🚚 Deliver · <scope>` when supported.
Reserve 🚚 for the orchestrator; worker titles follow their own contract.
Titles are metadata and never gate execution.
Even a single bounded change uses a worker. Follow shared
[execution scope](../../references/execution-scope.md); this skill's worker
contract is local, not the shared developer role used by Deliver Features.
For saved specs, follow the shared [readiness states](../../references/states.md)
for eligibility, duplicate-pickup reconciliation and the final human handoff.
Deliver selected scope and return its result to the caller. Backlog discovery,
recurring monitoring and queue persistence belong to the caller.

## Select and assign

Each invocation owns exactly one implementation repository. Accept its saved
specs, selected issues or bounded work, and resolve that repository before
assigning workers. Default to the current repository when it matches the request.
For a request spanning repositories, handle the clearly selected local scope and
return the other repository scopes to the caller; if no local target is clear,
resolve that choice before dispatch. Never create another repository's orchestrator
or workers. The caller coordinates separate Deliver runs.

A saved spec selects the whole spec unless the caller names a subset. Read its
embedded task contracts, prerequisites, shared contracts and accepted decisions.
Linked specs in other repositories are context and external inputs, not selected
implementation. Read [external prerequisites](references/integration.md#external-prerequisites)
when another repository supplies a required interface or implementation. Evaluate
the declared activity and evidence rather than issue closure or merge state.

The orchestrator turns selected implementation scope into bounded worker
assignments. These are not tracker issues or parent/child specs. Use source
section links where useful; do not create issues for worker assignments.
Do not implement unselected prerequisites. Ask only for material unresolved
scope or authority; keep independent selected work moving.

Choose useful repository-bound PR units, not one worker or PR per checklist item.
Default to one active worker. Add isolated workers when independent assignments
can progress concurrently and reduce elapsed time; keep dependent or overlapping
writes serial unless their isolation and required inputs are established. Prefer worker/worktree reuse for compatible serial work
under [workers.md](references/workers.md). Choose PR topology before dispatch;
read [integration.md](references/integration.md) when combining contributions,
handling dependencies, stacks, external inputs or topology changes.
Parallel execution alone does not require a stack or an extra integration PR.
Assign one writer per branch, PR and shared artifact, including
any requested source-progress edits. Worktrees do not isolate ports, databases
or external services; separate those resources or serialize their use.

Read the shared [runtime surface](../../references/codex-runtime-surface.md), then
[workers.md](references/workers.md) before creating, assigning or recovering workers.
Supply a complete assignment through publication and required CI, or through a
validated commit handoff when a designated worker will integrate the contribution.
Ordinary phase transitions need no coordinator approval round trip.

## Authority and worker work

Explicit invocation of this skill requests and authorizes creation of the workers
needed for selected delivery: visible tasks in the selected saved repository project
with isolated worktrees on the App, or native subagents with isolated worktrees
on CLI. Do not ask for separate task-creation confirmation. This authority covers
scoped branches, implementation, commits, pushes, PR creation/readiness and CI
corrections. Reuse established authority across assignments and continuations;
ask only for material unresolved scope or authority. Explicit user restrictions win: no-push
work ends with a local handoff and PR delivery explicitly incomplete. Never ask
to override that restriction. Integrating assigned commits into an owned delivery
branch is authorized under the integration contract. Landing PRs, deployment,
releases, production actions, direct issue closure, destructive recovery and
scope expansion are not authorized.

The worker composes [Implement](../implement/SKILL.md) for local implementation,
self-inspection and relevant validation. Assignments that publish a PR then use
G publication and CI workflows. Implement's responsibility still ends at the committed
local candidate; this delivery assignment authorizes the subsequent G phase.
No independent review is required by this skill. Repository/user-required checks
and reviews still apply; optional reviews run only when explicitly requested.
A separately requested managed review workflow retains its own contract and
budget; ordinary implementation and CI correction use no review-round ledger.

Before hosted access, the actual actor applies [G preflight](../../references/codex-dependency-preflight.md)
for the workflows it needs; immediately before every hosted write it applies
[hosted-content safety](../../references/hosted-content-safety.md). Carry these
routes in worker assignments. Do not install, reload or substitute dependencies.

For publication use G Send; it creates drafts and preserves existing draft state.
Deliver owns the subsequent ready transition: the assigned worker applies G's
[network execution](../../../g/references/network-execution.md) and
[gh preflight](../../../g/references/gh-dependency-preflight.md), marks only its
exact validated PR ready using the supported GitHub CLI operation, then reads
back non-draft state and unchanged full HEAD. This is a distinct authorized
transition, not Send behavior or a request for automated review. Use G GitHub
Actions for current checks and CI fixes. Missing readiness capability blocks
completion; do not report a draft as delivered.

## Source references

The orchestrator supplies each worker the exact source spec or issue references
and explains which implementation outcome its assignment contributes. PRs use
ordinary GitHub references only. Saved specs must be GitHub issues; local
documents may provide context for a direct bounded request but are not tracked
spec artifacts.
Worker assignments never acquire issue identities.

Issue closure is outside Deliver, including automatic closure on merge. Pass no
closing references to G Send and do not add closing keywords. Verify ordinary
source links after publication. Deliver does not plan, assign, or verify later
issue closure. Source progress is report-only unless separately requested,
except the required readiness handoff below.

## Coordinate and finish

Wait for worker results, attention requests or meaningful external changes;
do not busy-poll or send generic continuation messages. Workers correct scoped
failures while evidence shows progress. Repeated unchanged failures, unavailable
authority or unresolved decisions yield a precise blocker, not endless retries.
Continue independent units while another is blocked.

Consume each result under the [worker result contract](references/workers.md#assignment-and-result).
Verify current PR/CI facts and selected outcomes. When contributions need combining,
assign a worker to integrate and validate them under the integration contract;
the orchestrator accepts the assembled outcome. Reuse valid evidence
instead of repeating every worker test. Complete required checks, then broaden
or repeat validation only for new changes, failures, or unresolved evidence gaps.
Changed scope, base or HEAD invalidates
affected evidence. A worker's completed turn alone is not delivery proof.

Finish when every PR required for the selected scope is non-draft, required CI
passes, and selected outcomes and any explicitly required reviews are verified.
Verify each PR references its actual source scope using ordinary links.
If no CI checks are required, establish that from repository policy and current
PR facts. Missing check results alone do not prove that no checks are required.
Already-incorporated work needs current outcome proof, not a duplicate PR.
Draft, pending, partial and blocked results are not successful delivery. Ready
PRs remain unmerged. Later merge/deployment prerequisites are handoff information,
not extra delivery gates, unless the spec explicitly requires that evidence for
PR readiness. Do not invent a universal cross-repository integration requirement
or weaken one required by the selected acceptance criteria.

For each selected spec whose whole outcome meets these criteria, the orchestrator
transitions its authoritative readiness marker to the human-ready state under
[readiness states](../../references/states.md), using G GitHub Issues.
Verify the transition before reporting the source handoff
complete. Leave source issues open for human handling; do not transition partial or
blocked specs or requeue delivered work after a failed metadata update. Direct
requests without a saved spec need no readiness artifact.

Return a concise result led by ready PR links and verified outcomes, followed
only by material limitations or resume inputs. Use the worker result contract
for the evidence needed to substantiate that result;
combine contributions without claiming unselected outcomes. On interruption or
partial results include a resume handoff under the worker recovery rules.
Preserve worktrees and leave App workers visible by default.
No mandatory retrospective, token accounting, claims, lock replacement, scheduling
graph or durable ledger. Separate runs have no automatic ownership exclusion;
known competing work must still be reconciled before a conflicting write.

## Skill Dependencies

Bundled [Implement](../implement/SKILL.md) owns local work with optional UI design help, without
publication. Installed `g@alemar11` owns Git/GitHub publication, required CI and
optional stacks; load only the workflows needed for the selected operation.
The orchestrator owns assignments, integration and acceptance.
