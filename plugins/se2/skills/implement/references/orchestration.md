# Implement Orchestration

This reference owns multi-Feature scheduling, worker dialogue, Contract Repair,
and authorization routing for `se2:implement`.

## Control plane

The orchestrator coordinates one run containing one or more authoritative
GitHub Features. Each Feature retains its own Task DAG, repository bindings,
assignment states, and PR outputs. Derive runnable waves from Task dependencies,
path overlap, repository isolation, and observed runtime capacity.

Implement is one hierarchical graph with an orchestrator control-plane
subgraph and one worker-lifecycle traversal per assignment. Cross-subgraph
edges carry verified assignment, conflict, candidate, mismatch, and terminal
evidence. They do not grant either role the other role's authority.

Before any worker starts, claim the complete sorted Feature set in one ledger
transaction. A conflicting active claim proves another orchestrator owns at
least one Feature and blocks startup without leaving partial claims. Do not
create a competing orchestrator or take over an active claim. Release ownership
only after terminal reconciliation for the complete selected set; release every
claim atomically or none. A resumed run reuses its existing idempotent claims.

Run independent assignments concurrently when their contracts and paths are
safe. Serialize real dependencies and unsafe overlap. Do not create synthetic
dependencies, impose a fixed worker cap, or stop independent Features because
one assignment is blocked or deferred.

An assignment-local block or authorization wait returns to scheduling after a
durable checkpoint. Terminal `deferred` applies only when every remaining path
waits for user authority; terminal `blocked` applies only when an aggregate or
unrecoverable prerequisite prevents all remaining work.

For every dependency edge, pass the downstream worker the exact prerequisite
HEAD vector and an independently verified integration base containing every
prerequisite HEAD. A single-parent chain may use the prerequisite branch and
HEAD directly. A fan-in requires a worker-owned integration candidate that
contains all predecessor HEADs. The downstream candidate must prove every
required HEAD is an ancestor before review or publication. PR bases and stacked
relationships must preserve the same ancestry. If no authoritative merged,
stacked, or worker-composed integration base contains the complete vector, the
dependent assignment remains blocked; PR readiness alone is never dependency
completion.

The orchestrator may exchange these messages with workers:

- verified bootstrap and contract revision;
- coarse milestone or terminal-state request;
- evidence-only mismatch or reconciliation request;
- Contract Repair block and resume result.

It must not prescribe implementation, tests, review findings, commands, files,
or fixes. Routine worker collaboration and technical progress remain outside
the ledger.

The orchestrator alone accesses and mutates the ledger. Workers report bounded
evidence through the task dialogue and never read, write, or reconcile SQLite
state themselves.

## Assignment ownership

Create one implementation worker per dependency-ready Task assignment. Preserve
its stable task, project, repository, worktree, branch, and contract-generation
identity until it is complete, formally superseded, or authoritatively
unrecoverable. A worker never creates another worker or planner task.

After producing a committed, validated candidate HEAD, the same worker runs the
runtime's native code-review capability in its own session and worktree. Review
does not create another task, worktree, or ownership identity.

## Contract Repair

A worker may request Contract Repair only with portable evidence identifying:

- the exact Feature and Task refs;
- the stable field that is incomplete, contradictory, or wrong;
- the conflicting source and implementation evidence;
- the current worker, worktree, branch, and full HEAD;
- the safe boundary where implementation stopped.

Record one active repair ID and incrementing `contract_generation` per
assignment. Preserve the worker and its useful changes while repair is active.
Create one separate non-implementation planner task that invokes `se2:feature`
with `entry_route=maintenance` and only the portable evidence. The planner owns
the proposed or published Feature/Task correction; the orchestrator and worker
do not author it.

## Authorization decision

The orchestrator classifies the repair before hosted mutation:

- no material change: typo, formatting, link repair, or clarification that
  leaves every stable semantic field unchanged;
- material change: outcome, non-goals, requirements, scope, acceptance,
  allowed paths, validation, dependencies, repository identity, readiness, or
  another execution obligation changes.

Proceed without another question only when no material change is present or
the current invocation already grants the exact contract mutation. Otherwise
ask the user one bounded authorization question and mark only the affected
Feature assignment deferred. Continue independent Features.

After the planner returns, independently reread the complete authoritative
Feature/Task bundle. `applied` or `no-op` with compatible execution identity may
advance `contract_generation` and resume the same worker. `proposed`,
`deferred`, `blocked`, unverifiable readback, or identity-changing repair does
not resume that worker. A compatible revision is delivered exactly once; an
incompatible assignment returns to scheduling for controlled replacement.

## Aggregate completion

A Feature is delivery-ready only when every required Task assignment and PR
output passes final verification. The run is complete only when every selected
Feature is delivery-ready and terminal reconciliation has released every claim
owned by the run. Preserve claims for resumable blocked or deferred runs and
preserve one aggregate vector:

`feature_ref, task_refs, repository_identity, base_branch, head_branch,
head_sha, pr_url, readiness_state`.
