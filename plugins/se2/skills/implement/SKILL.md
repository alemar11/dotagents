---
name: implement
description: "Execute one or more authoritative GitHub SE2 Features through a mandatory GitHub-backed graph-first multi-Feature orchestrator, isolated implementation workers, exact-HEAD review, verified standalone or stacked PR delivery, and Contract Repair; use only for explicit implementation or resume requests."
---

# Implement Graph

## Input and output invariant

Use this skill only for an explicit request to implement or resume one or more
published SE2 Features from GitHub. Every input Feature must resolve to one
authoritative Feature issue, its complete Task issue set, Task dependencies,
repository identities, acceptance criteria, validation policy, and readiness
evidence. Do not start from an isolated Task, local draft, Idea, or unbounded
implementation request.

The expected terminal output is one verified pull-request delivery topology.
Return a complete mapping from each selected Feature and Task set to its
repositories, branches, exact HEADs, PR references, and standalone or stacked
relationships. `complete` means every selected Feature has a verified
`standalone-ready` or `stack-ready` PR output; this skill never merges, deploys,
releases, or performs post-merge closure.

Implement has no local-only or preview execution mode. GitHub interaction is
mandatory: the run reads authoritative Feature and Task contracts, uses hosted
state for readiness and delivery decisions, and completes only with verified
GitHub PR outputs. Local worktrees and local Git transport are execution
surfaces inside that flow, never an alternative terminal result. If the
required hosted dependency or authoritative GitHub state is unavailable, block
the run rather than converting it into a local-only implementation.

## Shared contracts and dependencies

Read the shared [workflow-graph.md](../../references/workflow-graph.md) before
using the registry below. The registry is the structural source of truth;
Mermaid is its maintained projection.

Before the mandatory first GitHub Feature, Task, issue, PR, or review read or
write, load the shared
[codex-dependency-preflight.md](../../references/codex-dependency-preflight.md).
All GitHub transport, mutation safety, publication, and read-after-write
verification belong to the G-owned workflows. A passing dependency gate does
not grant GitHub mutation authority.

Implement keeps the ownership split explicit: workers own implementation
semantics, conflict resolution, validation, and candidate evidence; G-owned
workflows own local Git transport and every hosted GitHub operation. The shared
dependency gate applies before the first hosted read or write, not before local
worktree editing or validation. Read
[review-delivery.md](references/review-delivery.md) for the operation-by-operation
owner and readback matrix.

Before creating, resuming, or monitoring application tasks, load:

- [task-profile.md](references/task-profile.md) for orchestrator and worker
  profiles;
- [task-preflight.md](../../references/task-preflight.md) for capability,
  destination, identity, authorization, observation, and recovery gates;
- [task-handoff.md](../../references/task-handoff.md) for assignments, title
  metadata, update relay, reconciliation, and terminal reports.

For the orchestrator, every worker, and every Feature Contract Repair planner,
complete the shared title-reconciliation subprotocol after stable task identity
observation and before normal monitoring or update relay. Preserve valid task
execution on a title warning, report that warning explicitly, and never create
a replacement task or repeat the bounded title adjustment.

The orchestrator owns title-adjustment recovery for every Implement-managed
task. Before an adjustment, reserve the effect in the existing operations
index using the stable task identity alone, retain the exact requested title as
effect evidence, then finish it from the adjustment evidence and authoritative
readback. On resume, reconcile an existing pending or unknown reservation;
never begin a second adjustment.

Load [orchestration.md](references/orchestration.md) when scheduling workers,
deriving delivery topology, handling worker dialogue, or repairing a Feature
contract. Load
[review-delivery.md](references/review-delivery.md) when a candidate HEAD is
ready for review or publication. Load [run-state.md](references/run-state.md)
before preparing, resuming, checkpointing, or resetting the ledger.

## Workflow graph

| node_id | kind | entry condition | transitions | side effects | terminal state |
| --- | --- | --- | --- | --- | --- |
| intake | action | explicit implementation or resume request with one or more GitHub Feature refs | source-preflight, blocked | none | none |
| source-preflight | validation | complete Feature and Task bundles are readable from the authoritative hosted source | runtime-preflight, blocked | hosted | none |
| runtime-preflight | validation | authoritative bundles and target repositories are known | prepare-run, blocked | read | none |
| prepare-run | action | every required role and destination passed preflight | schedule, blocked | durable | none |
| schedule | decision | run is ready for another wave or aggregate terminal reconciliation | delivery-gate, release-claims, deferred, blocked | none | none |
| delivery-gate | decision | one or more unfinished assignments are candidates for the next wave | worker-bootstrap, schedule, assignment-blocked, blocked | read | none |
| worker-bootstrap | action | one or more assignments are dependency-ready | implement-validate, assignment-blocked, blocked | durable | none |
| implement-validate | action | worker identity and implementation worktree are verified | candidate, contract-conflict, assignment-blocked, blocked | durable, hosted | none |
| contract-conflict | action | worker reports an evidence-backed stable contract conflict | repair-authority, assignment-blocked, blocked | durable | none |
| repair-authority | decision | conflict and proposed semantic boundary are known | repair-task, assignment-deferred, blocked | none | none |
| repair-task | action | repair is authorized or requires no material contract mutation | repair-readback, assignment-blocked, blocked | durable, hosted | none |
| repair-readback | validation | Feature planner returned a repair result | implement-validate, schedule, assignment-blocked, blocked | hosted, durable | none |
| candidate | validation | worker reports committed, validated candidate HEAD | native-review, assignment-blocked, blocked | read, durable | none |
| native-review | action | worker session is pinned to the committed candidate HEAD | review-decision, assignment-blocked, blocked | read, durable | none |
| review-decision | decision | in-session review result is bound to current candidate HEAD | implement-validate, publish-pr, assignment-blocked, blocked | durable | none |
| publish-pr | action | native review is clean and GitHub mutation is authorized | stack-reconcile, ready-monitor, assignment-blocked, blocked | hosted, durable | none |
| stack-reconcile | validation | a stacked PR was published or its parent, base, link, or exact-HEAD evidence drifted | ready-monitor, implement-validate, assignment-blocked, blocked | read, durable | none |
| ready-monitor | action | PR identity and exact published HEAD are verified | implement-validate, stack-reconcile, final-verify, assignment-blocked, blocked | hosted, durable | none |
| final-verify | validation | current PR, topology, CI, review, task, checkout, and HEAD evidence are available | schedule, stack-reconcile, assignment-blocked, blocked | read, durable | none |
| assignment-blocked | action | one assignment cannot progress but independent work may remain | schedule | durable | none |
| assignment-deferred | action | one assignment awaits bounded user authorization | schedule | durable | none |
| release-claims | action | every selected Feature is delivery-ready and no assignment remains active | complete, blocked | durable | none |
| deferred | terminal | a material contract change awaits user authorization | none | none | deferred |
| complete | terminal | every selected Feature maps to verified PR-ready output | none | none | complete |
| blocked | terminal | required evidence, capability, identity, authority, or reconciliation is unavailable | none | none | blocked |

~~~mermaid
flowchart TD
    subgraph orchestrator_subgraph ["Orchestrator control plane"]
        intake
        source-preflight
        runtime-preflight
        prepare-run
        schedule
        delivery-gate
        worker-bootstrap
        contract-conflict
        repair-authority
        repair-task
        repair-readback
        stack-reconcile
        final-verify
        assignment-blocked
        assignment-deferred
        release-claims
        deferred
        complete
        blocked
    end
    subgraph worker_subgraph ["Worker lifecycle"]
        implement-validate
        candidate
        native-review
        review-decision
        publish-pr
        ready-monitor
    end
    intake --> source-preflight
    intake --> blocked
    source-preflight --> runtime-preflight
    source-preflight --> blocked
    runtime-preflight --> prepare-run
    runtime-preflight --> blocked
    prepare-run --> schedule
    prepare-run --> blocked
    schedule --> delivery-gate
    schedule --> release-claims
    schedule --> deferred
    schedule --> blocked
    delivery-gate --> worker-bootstrap
    delivery-gate --> schedule
    delivery-gate --> assignment-blocked
    delivery-gate --> blocked
    worker-bootstrap --> implement-validate
    worker-bootstrap --> assignment-blocked
    worker-bootstrap --> blocked
    implement-validate --> candidate
    implement-validate --> contract-conflict
    implement-validate --> assignment-blocked
    implement-validate --> blocked
    contract-conflict --> repair-authority
    contract-conflict --> assignment-blocked
    contract-conflict --> blocked
    repair-authority --> repair-task
    repair-authority --> assignment-deferred
    repair-authority --> blocked
    repair-task --> repair-readback
    repair-task --> assignment-blocked
    repair-task --> blocked
    repair-readback --> implement-validate
    repair-readback --> schedule
    repair-readback --> assignment-blocked
    repair-readback --> blocked
    candidate --> native-review
    candidate --> assignment-blocked
    candidate --> blocked
    native-review --> review-decision
    native-review --> assignment-blocked
    native-review --> blocked
    review-decision --> implement-validate
    review-decision --> publish-pr
    review-decision --> assignment-blocked
    review-decision --> blocked
    publish-pr -->|standalone| ready-monitor
    publish-pr -->|stacked| stack-reconcile
    publish-pr --> assignment-blocked
    publish-pr --> blocked
    stack-reconcile --> ready-monitor
    stack-reconcile --> implement-validate
    stack-reconcile --> assignment-blocked
    stack-reconcile --> blocked
    ready-monitor --> implement-validate
    ready-monitor --> stack-reconcile
    ready-monitor --> final-verify
    ready-monitor --> assignment-blocked
    ready-monitor --> blocked
    final-verify --> schedule
    final-verify --> stack-reconcile
    final-verify --> assignment-blocked
    final-verify --> blocked
    assignment-blocked --> schedule
    assignment-deferred --> schedule
    release-claims --> complete
    release-claims --> blocked
~~~

This is one hierarchical workflow graph. The two subgraphs have separate role
rules and communicate only through the registered cross-subgraph transitions;
they are not independent runs. `native-review` is a load-bearing worker node,
not an application task, separate reviewer, or second worktree.

`assignment-blocked` and `assignment-deferred` checkpoint one affected
assignment and return control to `schedule`; they never terminate independent
Features. `schedule` enters terminal `deferred` only when all remaining work is
waiting for user authority, and terminal `blocked` only for an aggregate or
unrecoverable prerequisite that prevents every remaining path.

`delivery-gate` derives one transient delivery mode for each candidate
assignment without changing its Task dependency graph. `stack-reconcile` is an
orchestrator validation node, not another application task or implementation
role. It verifies the stacked relationship created by the G-owned publication
workflow and routes stale descendant evidence back to the owning worker.

## Orchestrator boundary

The Sol/medium orchestrator is control plane only. It may coordinate multiple
Features and Task assignments in parallel or serial execution waves, create or
resume the required worker tasks, monitor bounded progress, and exchange
control-plane messages with them. It must not inspect or edit worker
code, choose implementation or review fixes, judge findings, rewrite Feature
contracts, or mirror routine worker dialogue into the ledger.

Derive execution waves from each Feature Task DAG, repository and path overlap,
and verified runtime capacity. Derive delivery topology separately. Operational
serialization, path overlap, and runtime capacity never create a PR stack. A
single same-repository prerequisite may produce a stacked child only when the
parent assignment passed `final-verify`, its current PR HEAD equals its reviewed
candidate, and the child will use that exact branch and HEAD as its integration
base. Parallel, unrelated, and cross-repository assignments remain standalone.
Do not add a numeric worker cap or invent cross-Feature dependencies. A blocked
or deferred assignment does not stop independent Features; shared prerequisites
remain binding.

Before bootstrapping a stacked child, verify the parent is still
`delivery-ready`, its required CI and reviews remain clean, its exact HEAD is
unchanged, and the required G publication and official stack capability are
available. A pending, failing, stale, or ambiguous parent keeps the child out of
the runnable wave. Never install a missing stack dependency or silently publish
the child as standalone.

Before scheduling, atomically claim the complete sorted input Feature set in
the ledger. An active claim held by another run blocks startup for that Feature
set; never create a second orchestrator, split the claim, or steal ownership.
After every selected Feature is delivery-ready, `release-claims` uses current
claim revisions to release all claims before `complete`. Preserve active claims
for resumable blocked or deferred runs. Claim release is one all-or-none
transaction for the complete selected set; an interruption is reconciled before
retry and never justifies a second orchestrator.

## Worker and review boundary

Each implementation worker owns one eligible Task assignment in its verified
implementation worktree. It owns technical design, code, tests, validation,
candidate evidence, exact-HEAD native review in the same worker session,
finding decisions, and fixes. The worker hands local Git transport and hosted
GitHub transport to their G-owned workflows, then independently checks the
returned evidence. Review runs only after the candidate is committed and the
same worktree is clean at its exact HEAD.
Any HEAD change invalidates the prior review and requires a new in-session
review cycle. The orchestrator receives review evidence but never performs or
judges the review.

A stacked child worker starts from the verified parent candidate SHA in its own
isolated worktree. If the parent later changes, the orchestrator invalidates the
descendant base, review, CI, and readiness evidence. After the parent passes
`final-verify` again, each descendant worker rebases its own branch in
bottom-to-top order, then repeats validation, review, publication, and hosted
monitoring. The orchestrator never edits or rebases worker code itself.

## Contract Repair boundary

When a worker proves that the authoritative Feature or Task issue is
semantically incomplete or contradictory, preserve the worker, worktree,
branch, HEAD, and useful changes; record the assignment as awaiting Contract
Repair. The orchestrator creates one separate planner task that explicitly uses
`se2:feature` through its maintenance route. That planner is not an
implementation worker and must not access the worker worktree.

The orchestrator independently determines whether the proposed repair changes
stable semantics. Outcome, scope, non-goals, requirements, acceptance criteria,
allowed paths, validation policy, dependencies, repository identity, or
readiness changes require user authorization unless the current invocation
already grants that exact contract mutation. Ask only for that material change;
continue independent Features while awaiting the answer.

Resume the same worker only after authoritative complete-bundle readback proves
the repair applied and execution identity remains compatible. Otherwise retain
the old evidence and return the assignment to scheduling for a controlled
replacement. Never infer repair success from the planner report alone.

## Ledger boundary

The SQLite WAL ledger is a durable checkpoint and recovery index, not a second
workflow engine. The graph and orchestrator own live control flow; GitHub, Git,
and the application remain authoritative for external state.

The orchestrator is the ledger's only reader and writer during a run. Workers
never call the ledger or derive decisions from it; they send bounded evidence
to the orchestrator, which records only a verified durable boundary. This
single-writer authority does not replace SQLite transactions or compare-and-swap
guards, which still protect concurrent orchestrators and recovery.

The ledger also owns exclusive active orchestration claims. One authoritative
GitHub Feature may belong to only one active Implement run at a time, while one
run may claim multiple Features atomically.

Write ledger checkpoints only at durable boundaries: run start, assignment and
task binding, bounded title adjustment, candidate HEAD, review cycle, PR
publication, stack-link reconciliation, Contract Repair, and terminal
verification. Do not store prompts, message
bodies, model/reasoning profiles, Feature or Task bodies, findings, validation
logs, or routine worker technical state. A ledger failure blocks only a new
side effect or recovery step that requires durable idempotency; it does not
turn ordinary live dialogue into a database operation.

## Terminal report

Return one aggregate report with:

- every input GitHub Feature and its complete Task set;
- every implementation worker identity and verified destination;
- execution-wave and blocked/deferred evidence;
- Contract Repair generations and authorization outcomes;
- candidate, review, publication, CI, stack, and final exact-HEAD evidence;
- one output row per PR with Feature refs, repository, delivery mode, parent PR
  when present, base, branch, full HEAD, PR URL, stack order and receipt when
  present, and `standalone-ready` or `stack-ready` readiness state;
- aggregate `outcome: complete`, `deferred`, or `blocked`.

Never claim completion while any selected Feature lacks its required verified
PR output.
