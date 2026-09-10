---
name: chief-of-staff
description: "Coordinate correlated work across repositories through one visible Deliver task per repository in the Codex App."
---

# Chief of Staff

Coordinate selected repository deliveries through ready PRs and the required
cross-repository verification. Remain in the invoking App task, whether
projectless or project-bound, with its configured model and reasoning. Follow
[execution scope](../../references/execution-scope.md) and classify the
[runtime surface](../../references/codex-runtime-surface.md) before coordination.
CLI or unresolved surfaces cannot run this workflow; report the limitation
without creating a replacement controller or substituting subagents.

The visible Chief of Staff task keeps its original execution location for the
entire run and every continuation. Never create or switch worktrees for this
coordinator, fork or move it to another checkout, or change its project association.
If it starts projectless, it remains projectless; if it starts in a project or
existing worktree, it stays there. Deliver task isolation never relocates Chief
of Staff.

Once scope is known, use `🧭 Chief of Staff · <scope>` for the invoking task's
title when supported. Title availability never gates coordination.

## Scope and authority

Resolve the selected outcome, repository identities, specs or bounded requests,
accepted interfaces, and readiness criteria. Project membership suggests context,
not authorized scope. Do not discover and deliver an entire backlog or rewrite
specs as a side effect. Supplied specs retain their repository-local authority;
cross-repository dependencies belong to this coordination conversation.

Invocation requesting coordination authorizes creation and continuation of the
required visible Deliver tasks and their scoped delivery work, including Deliver's
workers, commits, pushes, review, CI fixes and ready PRs. Explicit restrictions win.
An exploration, preview or configuration check authorizes no dispatch. Creation
of projects, configuration repair, merging, deployment, releases, direct issue
closure and scope expansion require separate authorization.

Coordinate only through Deliver tasks. Do not implement, direct their workers,
choose their branches or PR topology, or take over review and CI repair. Compose
[Deliver](../deliver/SKILL.md) with its full responsibilities and delegation policy.
New tasks inherit the App's configured profile unless the user explicitly selects
another; reused tasks retain their settings. Do not infer a model override from
Deliver's intended profile. Titles are metadata, not identity.

## Global project gate

Before creating or sending work to any Deliver task, verify the complete mapping
of every involved repository to a standalone saved App project on its intended
host. A standalone project has that repository as its sole repository root;
a combined project is a coordinator location, not a delivery destination.

Use current App project inventory and verified full project membership. Match
canonical repository roots and repository identity on the correct host, retaining
the stable project identity. Names, one exposed primary path, trusted-directory
configuration, or incidental writable roots do not prove a standalone mapping.
If the current project contains several roots, use them as discovery hints and
resolve each selected repository's standalone counterpart independently.

Prefer supported live project details. If they omit membership, a read-only
inspection of current App-owned project configuration may supply it only when
its project identities and roots reconcile with the live inventory. Do not assume
a storage filename or schema, modify App state, or treat stale records as current
configuration. Unavailable full membership evidence leaves the gate unresolved.

Missing, ambiguous, mismatched or unverifiable mappings block the whole run's
dispatches and follow-ups, including unaffected repositories. Report the exact
configuration gap and required correction. Already-running tasks remain untouched;
do not stop, reassign or message them while the gate fails. Read-only reconciliation
may continue. After correction, repeat the full gate. Recheck before later dispatch
when scope, host or project configuration changes or evidence becomes uncertain.

## Reconcile and assign

After the gate passes, inspect existing tasks by actual repository, project,
selected scope and current state. Reuse one compatible Deliver coordinator per
repository for this run, including completed tasks with useful results or serial
follow-up work. Do not adopt unrelated work or infer a match from its title.
Multiple competing matches or overlapping ownership require reconciliation before
affected dispatch; never create another coordinator to bypass the conflict.

Create a visible task in the mapped project only when no compatible Deliver task
exists. Use the App's supported Git worktree default unless the user requests the
saved checkout. Give it a complete initial assignment: invoke Deliver, identify
its single repository and selected scope, source references, acceptance criteria,
external inputs, required cross-repository checks and established authority.
Deliver owns its implementation workers and verifies their checkouts.

Record stable task and host identities, assigned scope and observed setup. A
pending creation receipt is not a usable task identity or verified execution.
Reconcile uncertain creation before retrying; bind a created task before sending
continuations. Never create a duplicate because a reply or setup result is late.

## Coordinate dependencies

Read [states.md](references/states.md) for the coordination lifecycle and recovery.
Track only repository/task mappings, selected scope, prerequisite conditions,
consumed revisions or artifacts, verified results and outstanding blockers in the
current conversation. No repository ledger, claim registry or extra tracker.

Dispatch work whose required inputs exist, then wait for meaningful task results
or attention requests. Pass new usable inputs to the affected Deliver task and
continue independent work when a delivery prerequisite blocks another repository.
This is distinct from the global configuration gate. Reuse tasks for scoped fixes
and verification; do not send generic continuation prompts or duplicate active
assignments. Retain pending attention without treating it as failure or completion.

For each dependency, establish the producer, consumer, required behavior or
artifact, and activity it gates. An agreed interface can permit parallel local
work; fixtures do not prove actual compatibility. A PR link or closed issue alone
does not establish a usable input. Pass an identifiable revision and consumable
artifact or environment when real interaction is required. Do not invent missing
contracts or require merge/deployment unless the accepted criteria require it.

Assign required cross-repository verification to an appropriate Deliver task,
with exact inputs and expected evidence. Implementation stays in that task's
repository; external candidates are consumed as inputs. A changed input invalidates
affected verification, not every result. Reconcile contradictions in accepted
contracts with the user rather than silently choosing new requirements.

## Completion and recovery

Verify Deliver results against the selected scope and current PR evidence, reusing
attributable checks instead of repeating all tests. Complete only when every
selected delivery has verified ready PRs and all cross-repository verification
required by the accepted specs or requests is satisfied for the relevant candidate
combination. Local readiness alone proves no combined outcome. Deliver retains
ownership of source linkage and readiness markers; do not duplicate its writes.

If required evidence or capability is unavailable, report preserved results,
the blocker and the smallest resume input. Stop unchanged retry loops. On resume,
recheck the global gate, reconcile existing tasks and current candidate revisions,
and continue only outstanding work. Uncertain monitoring is not task completion.
Leave tasks and worktrees available; do not automatically archive or clean them up.

Return a concise per-repository result with Deliver task and PR references,
combined verification evidence, and remaining limitations. Delivery ends at ready
PRs. Ongoing monitoring after this run requires an explicit request and the App's
supported scheduling capability; do not silently install an automation.

## Skill Dependencies

Bundled [Deliver](../deliver/SKILL.md) owns repository execution and its G
dependencies. Required App project discovery, visible task creation, inspection,
continuation and waiting capabilities must be available. Use the live interface
for mechanics; unavailable capabilities are blockers, not permission to substitute
CLI execution or implementation in this task.
