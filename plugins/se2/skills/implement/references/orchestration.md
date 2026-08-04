# Implement Orchestration

This reference owns multi-Feature scheduling, worker dialogue, Contract Repair,
and authorization routing for `se2:implement`.

## Control plane

The orchestrator coordinates one run containing one or more authoritative
GitHub Features. Each Feature retains its own Task DAG, repository bindings,
assignment states, and PR outputs. Derive runnable waves from Task dependencies,
path overlap, repository isolation, and observed runtime capacity.

Implement is one hierarchical graph with an orchestrator control-plane
subgraph and one worker-lifecycle traversal per assignment. GitHub interaction
is mandatory for every run: source Features and Tasks, readiness, PR delivery,
and hosted review evidence remain authoritative. Cross-subgraph
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

## Feature Bundle handoff and path ownership

The Feature Bundle Report is planning evidence, not an execution authorization.
It may contain each Feature or Task's `allowed_paths`, theoretical execution
waves, observed path overlap, and a `scope-overlap-gate` explaining why shared
scope is not a logical dependency or a GitStack parent. Implement must
independently read back the current repository identity, checkout, branch,
base, and full HEAD before scheduling; stale or incomplete Feature planning
evidence is not a substitute for current repository state.

Implement owns the operational decision for every runnable wave. Before a
worker is bootstrapped, the orchestrator must establish an atomic path claim
for the assignment's normalized `allowed_paths` envelope. A conflicting claim
serializes only the overlapping assignments and never creates a synthetic Task
dependency or PR stack. Disjoint claims may proceed concurrently when their
contracts and current base/HEAD evidence are valid.

For a worker that will touch a shared path, claim readback and the current
base/full-HEAD readback are required immediately before execution. If the
base or HEAD has drifted, invalidate the affected scheduling and candidate
evidence; the owning worker must rebase its own branch through the G-owned
transport, read back the resulting full HEAD, and revalidate before executing
or reviewing. The orchestrator coordinates and records this boundary but does
not edit, rebase, or resolve worker code.

## Execution and delivery topology

Keep scheduling and PR delivery as separate projections of the authoritative
Task DAG. For every assignment considered by `delivery-gate`, derive exactly one
transient mode:

- `standalone`: no concrete same-repository parent branch is required; publish
  against the verified repository default branch;
- `stacked`: exactly one same-repository prerequisite is the intended immediate
  parent, and the child will use that parent's verified branch and exact HEAD as
  its integration base.

Serial execution caused only by path overlap, capacity, or a preferred working
order remains standalone. Parallel assignments and cross-repository
prerequisites never form one stack. A fan-in cannot be represented as multiple
stack parents: require one worker-owned integration candidate containing the
complete prerequisite HEAD vector, or wait for an authoritative merged base.

A stacked child is dependency-ready only after the immediate parent assignment
is `delivery-ready` at `final-verify`, the live parent PR is open and ready, its
current exact-head `$g:github-delivery-status` disposition is `ready` or
`ready-with-manual-action`, its hosted review is clean, and its full head still
equals the reviewed candidate SHA. Verify the G-owned single-PR publication workflow and official
stack capability before creating the child worker. Missing, failing, stale, or
ambiguous evidence keeps only that child out of the runnable wave; continue
independent assignments and never degrade to a standalone PR.

Returning from `delivery-gate` to `schedule` yields control until fresh parent
or capacity evidence exists; it is not a polling loop and does not create an
application task for a waiting child.

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

For a stacked assignment, also pass the exact parent assignment, PR, branch,
candidate SHA, and verified stack order. The worker creates its isolated
worktree from that SHA and publishes against the parent branch through the
G-owned single-PR workflow. That workflow may create the child PR and link the
verified parent/current pair; neither the worker nor orchestrator uses
stack-wide submit as a shortcut.

## Parent drift and descendant recovery

Re-read every parent PR immediately before child bootstrap, publication, stack
reconciliation, and final verification. If a parent branch, full HEAD,
readiness, or stack relationship changes after a child starts, invalidate every
affected descendant's integration-base, review, CI, and delivery-ready
evidence. Do not treat a green child check against the old base as current.

First return the changed parent to its owning worker and require it to pass
`final-verify` at the new exact HEAD. Then resume descendant workers in
bottom-to-top order. Each worker rebases and validates only its own branch,
runs a new exact-HEAD review, republishes through G, and returns fresh link and
hosted-review evidence. The orchestrator coordinates this sequence and records
reconciliation but never runs a stack-wide rebase, edits code, or resolves
conflicts. An ambiguous link result preserves the confirmed PR publication,
records the link effect as unknown, and blocks blind retry.

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

After producing a validated candidate, the worker uses the G-owned local Git
workflow to create the candidate commit, then runs the runtime's native
code-review capability in its own session and worktree. Review does not create
another task, worktree, or ownership identity.

## Contract Repair

A worker may request Contract Repair with one internal repair record
identifying:

- the exact Feature and Task refs;
- the stable field that is incomplete, contradictory, or wrong;
- the conflicting source and implementation evidence;
- the current worker and task identity, `project_root`, worktree, repository,
  branch, and full HEAD;
- the safe boundary where implementation stopped.

Record one active repair ID and incrementing `contract_generation` per
assignment. Preserve the worker and its useful changes while repair is active.
The internal record may retain local control-plane paths and identities. Before
creating the planner handoff or any hosted Feature/Task/changelog content, load
the shared
[hosted-content-safety.md](../../../references/hosted-content-safety.md) and
derive separate portable publication evidence. Convert repository-contained
paths to repo-relative form and represent external `project_root` or worktree
context only by repository identity, branch, and full SHA. Exclude worker/task,
host, prompt, and irrelevant transcript identity. Fail closed when that
projection cannot be established.

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
output passes final verification and every `F-AC-NN` criterion is verified from
the coverage map and current Task acceptance matrices. Aggregate one Feature
acceptance row with the criterion ID and current text, owning Task and
`T-AC-NN` IDs, `verified`, `unverified`, or `blocked` status, evidence
references, and candidate-SHA vector. The orchestrator aggregates worker-owned
proof but does not replace or reinterpret it. The run is complete only when
every selected Feature is delivery-ready and terminal reconciliation has
released every claim owned by the run. Preserve claims for resumable blocked or
deferred runs and preserve one aggregate vector:

`feature_ref, task_refs, repository_identity, delivery_mode, parent_pr,
base_branch, base_sha, head_branch, head_sha, pr_url, stack_order,
stack_link_status, github_delivery_disposition, merge_boundary,
github_delivery_evidence_ref, task_acceptance_evidence_refs,
feature_acceptance_evidence_ref, readiness_state`.
