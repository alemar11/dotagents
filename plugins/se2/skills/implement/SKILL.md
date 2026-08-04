---
name: implement
description: "Implement one or more authoritative GitHub Features using one isolated Feature Worker and one pull request per Feature, serial Task-DAG execution, exact-HEAD review, acceptance-criteria evidence, and verified standalone or stacked delivery; use only for explicit implementation or resume requests, and stop with a clear blocker when the Feature specification is incomplete or invalid."
---

# Implement Features

## Input and output invariant

Use this skill only for an explicit request to implement or resume one or more
published SE2 Features from GitHub. Every input Feature must resolve to one
authoritative Feature issue, its complete Task issue set, Task dependencies,
repository identities, stable acceptance-criterion IDs, acceptance coverage,
monotonic Feature and Task acceptance high-water marks, validation policy, and
readiness evidence. The acceptance coverage must come from the authoritative
hosted Feature body, not only a planner report. Do not start from an isolated
Task, local draft, Idea, or unbounded implementation request. A legacy checkbox
or a missing, duplicate, malformed, ambiguous, or high-water-inconsistent
criterion ID makes the bundle non-ready; block with Feature maintenance as the
smallest recovery instead of inventing or normalizing IDs inside Implement.

The expected terminal output is one verified pull-request delivery topology
with exactly one PR output per implementation-eligible selected Feature. Return
a complete mapping from each selected Feature and its complete Task set to its
repository, Feature branch, exact HEAD, PR reference, and standalone or stacked
relationships, acceptance-evidence matrices, exact Task-only
`closing_issue_refs`. `complete` means every Task and Feature criterion is
verified against that Feature's single current candidate HEAD, every
implementation-eligible selected Feature has a verified `standalone-ready` or
`stack-ready` PR output backed by a current
`$g:github-delivery-status` disposition of `ready` or
`ready-with-manual-action`, and each PR's GitHub
closing references equal its fully satisfied Task issue set while excluding
Feature and Idea issues. A selected Feature proven to have no exclusive
implementation delta must instead carry an authoritative Contract Repair
resolution that withdraws or redefines it; never create an empty commit, empty
PR, cosmetic change, or artificial proof. This skill never merges, deploys,
releases, or performs post-merge closure; GitHub closes the linked Tasks when an
eligible PR merges, while the Feature remains open.

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
verification belong to the G-owned workflows. The explicit Implement request
implicitly authorizes the exact in-scope GitHub writes required for its
selected Features; the dependency gate verifies availability and does not
broaden that scope.

Require `$g:github-delivery-status` for exact-HEAD provider readiness. Its
automation observations are facts, not authority: repository auto-merge
capability, an existing PR auto-merge request, or a merge-queue entry never
authorize Implement and are not blockers by themselves. Implement never
merges, bypasses protections, enables or disables auto-merge, or enqueues or
dequeues a PR.

Before the first hosted write, load the shared
[hosted-content-safety.md](../../references/hosted-content-safety.md). Apply its
complete gate immediately before every issue, comment, PR title/body, review
request, or review-text write, including content returned by Feature Workers or
tools.
Implement owns the final portable projection; G owns transport and readback and
must not be asked to invent semantic conversions.

Implement keeps the ownership split explicit: Feature Workers own
implementation semantics, conflict resolution, validation, and candidate
evidence; G-owned
workflows own local Git transport and every hosted GitHub operation. The shared
dependency gate applies before the first hosted read or write, not before local
worktree editing or validation. Read
[review-delivery.md](references/review-delivery.md) for the operation-by-operation
owner and readback matrix.

Local dependency setup is part of implementation when it is required by the
authorized Feature. Feature Workers may install dependencies already declared
by the repository and may add or update application dependencies, the manifest, and
the lockfile when that change is necessary to satisfy the Feature scope. Those
changes remain subject to scoped review and must not include generated
dependency directories such as `node_modules/`. Stop only when the dependency
change materially expands the Feature scope, introduces an unrelated
architectural choice, or requires external credentials or remote state beyond
the declared implementation workflow. This policy does not authorize
installing, replacing, or refreshing SE2/G runtime dependencies implicitly.

Before creating, resuming, or monitoring application tasks, load:

- [task-profile.md](references/task-profile.md) for orchestrator and Feature Worker
  profiles;
- [task-preflight.md](../../references/task-preflight.md) for capability,
  destination, identity, authorization, observation, and recovery gates;
- [task-handoff.md](../../references/task-handoff.md) for assignments, title
  metadata, update relay, reconciliation, and terminal reports.

For the orchestrator, every Feature Worker, and every Feature Contract Repair
planner, complete the shared title-reconciliation subprotocol after stable task identity
observation and before normal monitoring or update relay. Preserve valid task
execution on a title warning, report that warning explicitly, and never create
a replacement task or repeat the bounded title adjustment.

The orchestrator owns title-adjustment recovery for every Implement-managed
task. Before an adjustment, reserve the effect in the existing operations
index using the stable task identity alone, retain the exact requested title as
effect evidence, then finish it from the adjustment evidence and authoritative
readback. On resume, reconcile an existing pending or unknown reservation;
never begin a second adjustment.

Load [orchestration.md](references/orchestration.md) when scheduling Feature
Workers, deriving delivery topology, handling Feature Worker dialogue, or
repairing a Feature contract. Load
[review-delivery.md](references/review-delivery.md) when a candidate HEAD is
ready for review or publication. Load [run-state.md](references/run-state.md)
before preparing, resuming, checkpointing, or resetting the ledger.

## Transition-condition ownership

The registry below lists target node IDs only. Each source-node group has one
canonical condition owner:

| Source nodes | Canonical condition owner |
| --- | --- |
| `intake`, `source-preflight`, `runtime-preflight`, `prepare-run` | This skill's input invariant and shared-contract sections. |
| `schedule`, `delivery-gate`, `worker-bootstrap`, `assignment-blocked`, `assignment-deferred`, `release-claims` | [orchestration.md](references/orchestration.md), including control-plane, execution/delivery-topology, and aggregate-completion rules. |
| `implement-validate`, `contract-conflict`, `repair-authority`, `repair-task`, `repair-readback` | [orchestration.md](references/orchestration.md), including assignment-ownership, Contract Repair, and authorization rules. |
| `candidate`, `native-review`, `review-decision`, `publish-pr`, `stack-reconcile`, `ready-monitor`, `final-verify` | [review-delivery.md](references/review-delivery.md). |
| `deferred`, `complete`, `blocked` | This skill's terminal definitions; terminal nodes have no outgoing conditions. |

Each owner must define the conditions for every declared outgoing target from
its assigned source nodes and must not add an edge absent from the registry.
[run-state.md](references/run-state.md) owns persistence and recovery evidence,
not workflow transitions.

## Workflow graph

| node_id | kind | entry condition | transitions | side effects | terminal state |
| --- | --- | --- | --- | --- | --- |
| intake | action | explicit implementation or resume request with one or more GitHub Feature refs | source-preflight, blocked | none | none |
| source-preflight | validation | complete Feature and Task bundles are readable from the authoritative hosted source | runtime-preflight, blocked | hosted | none |
| runtime-preflight | validation | authoritative bundles and target repositories are known | prepare-run, blocked | read | none |
| prepare-run | action | every required role and destination passed preflight | schedule, blocked | durable | none |
| schedule | decision | run is ready for another wave or aggregate terminal reconciliation | delivery-gate, release-claims, deferred, blocked | none | none |
| delivery-gate | decision | one or more unfinished Feature assignments are candidates for the next wave | worker-bootstrap, schedule, assignment-blocked, blocked | read | none |
| worker-bootstrap | action | one or more Feature assignments are dependency-ready | implement-validate, assignment-blocked, blocked | durable | none |
| implement-validate | action | Feature Worker identity, one Feature worktree, complete Task DAG, and criterion IDs are verified | candidate, contract-conflict, assignment-blocked, blocked | durable, hosted | none |
| contract-conflict | action | Feature Worker reports an evidence-backed stable contract conflict | repair-authority, assignment-blocked, blocked | durable | none |
| repair-authority | decision | conflict and proposed semantic boundary are known | repair-task, assignment-deferred, blocked | none | none |
| repair-task | action | repair is authorized or requires no material contract mutation | repair-readback, assignment-blocked, blocked | durable, hosted | none |
| repair-readback | validation | Feature planner returned a repair result | implement-validate, schedule, assignment-blocked, blocked | hosted, durable | none |
| candidate | validation | Feature Worker reports one committed Feature candidate HEAD with every Task criterion verified by evidence bound to that HEAD | native-review, assignment-blocked, blocked | read, durable | none |
| native-review | action | Feature Worker session is pinned to the committed candidate HEAD | review-decision, assignment-blocked, blocked | read, durable | none |
| review-decision | decision | in-session review result is bound to current candidate HEAD | implement-validate, publish-pr, assignment-blocked, blocked | durable | none |
| publish-pr | action | native review is clean and the declared publication scope is resolved | stack-reconcile, ready-monitor, assignment-blocked, blocked | hosted, durable | none |
| stack-reconcile | validation | a stacked PR was published or its parent, base, link, or exact-HEAD evidence drifted | ready-monitor, implement-validate, assignment-blocked, blocked | read, durable | none |
| ready-monitor | action | PR identity and exact published HEAD are verified; the initial cycle observes the automatic ready-triggered review, while each post-fix HEAD uses one explicit request lineage | implement-validate, stack-reconcile, final-verify, assignment-blocked, blocked | hosted, durable | none |
| final-verify | validation | current PR, topology, CI, review, task, checkout, HEAD, and acceptance evidence are available | schedule, stack-reconcile, assignment-blocked, blocked | read, durable | none |
| assignment-blocked | action | one assignment cannot progress but independent work may remain | schedule | durable | none |
| assignment-deferred | action | one assignment awaits bounded user authorization | schedule | durable | none |
| release-claims | action | every Feature assignment is delivery-ready or authoritatively contract-resolved and no assignment remains active | complete, blocked | durable | none |
| deferred | terminal | a material contract change awaits user authorization | none | none | deferred |
| complete | terminal | every implementation-eligible selected Feature maps to one verified PR-ready output and every absorbed Feature has authoritative Contract Repair readback | none | none | complete |
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
    subgraph worker_subgraph ["Feature Worker lifecycle"]
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
they are not independent runs. `native-review` is a load-bearing Feature Worker
node, not an application task, separate reviewer, or second worktree.

`assignment-blocked` and `assignment-deferred` checkpoint one affected
assignment and return control to `schedule`; they never terminate independent
Features. `schedule` enters terminal `deferred` only when all remaining work is
waiting for user authority, and terminal `blocked` only for an aggregate or
unrecoverable prerequisite that prevents every remaining path.

`delivery-gate` derives one transient delivery mode for each candidate Feature
assignment without changing its internal Task dependency graph.
`stack-reconcile` is an orchestrator validation node, not another application task or implementation
role. It verifies the stacked relationship created by the separate G-owned
stack-link workflow after PR publication and routes stale descendant evidence
back to the owning Feature Worker.

## Orchestrator boundary

The Sol/medium orchestrator is control plane only. It may coordinate multiple
Features in parallel or serial execution waves, create or resume exactly one
Feature Worker task per Feature, monitor bounded progress, and exchange
control-plane messages with them. It must not inspect or edit Feature Worker
code, choose implementation or review fixes, judge findings, rewrite Feature
contracts, or mirror routine Feature Worker dialogue into the ledger. Feature
Workers never create child tasks; the orchestrator remains the only task
creator for implementation and Contract Repair roles.

Use each Feature Bundle Report only as planning input: it may provide
`allowed_paths`, theoretical execution waves, overlap evidence, and
scope-overlap gates. Independently revalidate the current repository identity,
checkout, branch, base, and full HEAD before scheduling any Feature Worker.
Implement then owns the runnable Feature waves, atomic path claims over each
Feature's complete `allowed_paths` union, and serialization of conflicting
Feature assignments. Derive delivery topology separately. Operational
serialization, path overlap, and runtime capacity never create a PR stack. A
single same-repository prerequisite may produce a stacked child only when the
parent assignment passed `final-verify`, its current PR HEAD equals its reviewed
candidate, and the child will use that exact branch and HEAD as its integration
base. Parallel, unrelated, and cross-repository Feature assignments remain
standalone. Do not add a numeric Feature Worker cap or invent cross-Feature
dependencies. A blocked or deferred assignment does not stop independent
Features; shared prerequisites remain binding.

Before bootstrapping a stacked child, verify the parent is still
`delivery-ready`, its current G delivery disposition is accepted, its required
reviews remain clean, its exact HEAD is
unchanged, and the required G publication and official stack capability are
available. A pending, failing, stale, or ambiguous parent keeps the child out of
the runnable wave. Never install a missing stack dependency or silently publish
the child as standalone.

Before scheduling, atomically claim the complete sorted input Feature set in
the ledger. An active claim held by another run blocks startup for that Feature
set; never create a second orchestrator, split the claim, or steal ownership.
This Feature claim is run ownership only; it does not establish ownership of
any implementation path. Path claims are a separate Implement scheduling
boundary and must be acquired from the normalized assignment `allowed_paths`
before Feature Worker bootstrap.
After every Feature assignment is delivery-ready or authoritatively
contract-resolved, `release-claims` uses current claim revisions to release all
claims before `complete`. Preserve active claims for resumable blocked or
deferred runs. Claim release is one all-or-none
transaction for the complete selected set; an interruption is reconciled before
retry and never justifies a second orchestrator.

## Feature Worker and review boundary

Each Feature Worker owns one complete authoritative Feature in one verified
implementation worktree, branch, and eventual PR. It receives every Task in
that Feature and executes them serially in deterministic Task-DAG order. Tasks
may define semantic prerequisites and acceptance coverage, but they never
create Task workers, Task branches, Task worktrees, or Task PRs. Parallelism is
only between independent Features.

The Feature Worker owns technical design, code, tests, validation,
criterion-level acceptance evidence, candidate evidence, exact-HEAD native
review in the same session, finding decisions, and fixes. For every `T-AC-NN`
in every Task, return one matrix row with criterion ID and text, Task ref,
`verified`, `unverified`, or `blocked` status, evidence reference, and the same
Feature candidate SHA. A candidate may advance only when every required Task
criterion is `verified`. The Feature Worker hands local Git transport and
hosted GitHub transport to their G-owned workflows, then independently checks
the returned evidence. Review runs only after the complete Feature candidate is
committed and the same worktree is clean at its exact HEAD. Any HEAD change
invalidates the prior acceptance and review evidence and requires fresh
criterion verification, validation, and a new in-session review cycle. The
orchestrator receives that evidence but never performs or judges the Feature
Worker's semantic verification or review.

A stacked child Feature Worker starts from the verified parent Feature
candidate SHA in its own isolated worktree. If the parent later changes, the
orchestrator invalidates the descendant base, review, CI, and readiness
evidence. After the parent passes `final-verify` again, each descendant Feature
Worker rebases its own branch in bottom-to-top order, then repeats validation,
review, publication, and hosted monitoring. The orchestrator never edits or
rebases Feature Worker code itself.

## Contract Repair boundary

When a Feature Worker proves that the authoritative Feature or Task issue is
semantically incomplete or contradictory, preserve the Feature Worker, worktree,
branch, HEAD, and useful changes; record the assignment as awaiting Contract
Repair. The orchestrator creates one separate planner task that explicitly uses
`se2:feature` through its maintenance route. That planner is not a
Feature Worker and must not access the implementation worktree.

Treat a zero-delta Feature as a contract conflict, not as successful
implementation. If the exact verified base already satisfies every current
`T-AC-NN` and `F-AC-NN` and the Feature has no exclusive observable result,
route it through Contract Repair so Feature maintenance either defines a real
residual outcome or authoritatively withdraws it as absorbed. Never manufacture
a commit, PR, test, or source edit to preserve a planned topology.

The orchestrator independently determines whether the proposed repair changes
stable semantics. Outcome, scope, non-goals, requirements, acceptance criteria,
allowed paths, validation policy, dependencies, repository identity, or
readiness changes require user authorization unless the current invocation
already grants that exact contract mutation. Ask only for that material change;
continue independent Features while awaiting the answer.

Resume the same Feature Worker only after authoritative complete-bundle
readback proves the repair applied and execution identity remains compatible. Otherwise retain
the old evidence and return the assignment to scheduling for a controlled
replacement. Never infer repair success from the planner report alone.

## Ledger boundary

The SQLite WAL ledger is a durable checkpoint and recovery index, not a second
workflow engine. The graph and orchestrator own live control flow; GitHub, Git,
and the application remain authoritative for external state.

The orchestrator is the ledger's only reader and writer during a run. Feature
Workers never call the ledger or derive decisions from it; they send bounded evidence
to the orchestrator, which records only a verified durable boundary. This
single-writer authority does not replace SQLite transactions or compare-and-swap
guards, which still protect concurrent orchestrators and recovery.

The ledger also owns exclusive active orchestration claims. One authoritative
GitHub Feature may belong to only one active Implement run at a time, while one
run may claim multiple Features atomically.

Write ledger checkpoints only at durable boundaries: run start, one Feature
assignment binding, bounded title adjustment, candidate HEAD, review cycle, PR
publication, stack-link reconciliation, Contract Repair, and terminal
verification. Do not store prompts, message
bodies, model/reasoning profiles, Feature or Task bodies, findings, validation
logs, or routine Feature Worker technical state. A ledger failure blocks only a
new side effect or recovery step that requires durable idempotency; it does not
turn ordinary live dialogue into a database operation.

Acceptance matrices remain Feature Worker task evidence, not a new ledger table
or a copy of the Feature/Task bodies. The assignment checkpoint stores the
stable `worker_task_id`, immutable Feature ref, contract generation, and exact
`candidate_sha`. On recovery, reread that Feature Worker task's authoritative
final report and require its complete Task-ref set and acceptance matrix to
match the current authoritative bundle, contract generation, and candidate SHA
before reuse. Missing task visibility or a mismatch blocks reuse.

## Terminal report

Return one aggregate report with:

- every input GitHub Feature and its complete Task set;
- every Feature Worker identity and verified destination;
- execution-wave and blocked/deferred evidence;
- Contract Repair generations and authorization outcomes;
- authoritative absorbed-Feature resolutions with no fabricated delivery row;
- one Task acceptance row per `T-AC-NN` and one aggregated Feature acceptance
  row per `F-AC-NN`, each with status, evidence references, and exact Feature
  candidate SHA;
- candidate, review, publication, G delivery-status, stack, and final exact-HEAD evidence;
- exact Task-only `closing_issue_refs` and verified PR-body/GitHub closing
  references for every delivery;
- exactly one output row per Feature PR with Feature ref, complete Task refs,
  repository, delivery mode, parent PR
  when present, base, branch, full HEAD, PR URL, stack order and receipt when
  present, GitHub delivery disposition, `merge_boundary`, and
  `standalone-ready` or `stack-ready` readiness state;
- aggregate `outcome: complete`, `deferred`, or `blocked`.

Never claim completion while an implementation-eligible Feature has an
unverified required acceptance criterion or lacks its verified PR output, or
while an absorbed Feature lacks authoritative Contract Repair readback.
