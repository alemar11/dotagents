# Implement Orchestration

This reference owns multi-Plan scheduling, textual-plan interpretation,
Feature Worker dialogue, user plan questions, and delivery-topology routing.

Before any hosted publication or user-facing hosted relay, apply the shared
[hosted-content-safety.md](../../../references/hosted-content-safety.md)
contract to the exact final content. G owns transport and readback.

## Control plane

The orchestrator coordinates one run containing one or more authoritative
GitHub Feature Plans. Each plan member retains its repository binding, one
Feature assignment, one Feature Worker, and one PR output. The orchestrator
derives execution units from the plan before scheduling; the Feature Plan
does not contain the runtime execution graph.

Provider delivery readiness is observed through
$g:github-delivery-status against the current exact PR HEAD; the orchestrator
does not reinterpret raw provider states.

Run independent plan members concurrently when their repositories, derived
path envelopes, real cross-member code dependencies, and observed runtime
capacity are safe. Serialize real dependencies and unsafe overlap. Do not
create synthetic dependencies, impose a fixed worker cap, or stop independent
plan members because one assignment is blocked or deferred.

Before any Feature Worker starts, claim the complete sorted plan-member set in
one ledger transaction. A conflicting active claim blocks startup without
partial claims or a competing orchestrator. Release all claims atomically
after terminal reconciliation.

## Plan interpretation and execution units

The orchestrator reads the authoritative Feature Plan and derives a transient
execution unit set. Each unit must have:

- one observable technical outcome;
- repository and path scope;
- implementation and validation intent;
- Feature-criterion mapping;
- real implementation prerequisites;
- evidence needed from the Feature Worker.

Use the smallest useful vertical units. Keep implementation and validation
layers together when they serve one outcome. Do not split a unit merely by
database, API, UI, test, documentation, or tracker layer unless that layer is
independently valuable.

Dependency edges mean real implementation prerequisites. Path overlap,
capacity, and preferred order are separate scheduling facts. Cross-repository
prerequisites remain plan-member context and never become a shared execution
edge.

The orchestrator owns this translation and may ask the Feature Worker to
refine technical units during implementation. It must not rewrite or publish
the Feature Plan.

## User plan questions

When a Feature Worker finds a product-level contradiction, missing outcome,
ownership conflict, or material acceptance gap, create one plan-question
record for the affected assignment. Present the bounded decision to the user
with its evidence and impact. Keep the assignment deferred while independent
plan members continue.

Do not create a separate Feature planner task automatically. If the user's
answer requires changing the published Feature Plan, report an explicit
se2:feature maintenance request as the recovery action and preserve the
worker's useful implementation evidence where safe. Technical implementation
ambiguity remains inside Implement and never becomes a Feature question.

## Execution and delivery topology

For every plan member, bootstrap exactly one Feature Worker. The worker
executes its derived units in deterministic prerequisite order inside one
isolated worktree. Parallelism is only between plan members whose paths,
repositories, dependencies, and live capacity are safe.

Derive standalone or stacked delivery separately from execution order:

- standalone: no concrete same-repository parent branch is required;
- stacked: one same-repository immediate parent is the intended integration
  base and its exact verified branch and HEAD are available.

Serialization caused only by path overlap, capacity, or preferred order
remains standalone. A fan-in requires one Feature Worker-owned integration
candidate containing every prerequisite HEAD or an authoritative merged base.

Before bootstrapping a stacked child, reread the parent PR, branch, full HEAD,
review, delivery disposition, and stack capability. A stale or ambiguous
parent keeps only that child out of the runnable wave. Never silently degrade
to standalone.

If a parent changes after a child starts, invalidate the descendant's
integration, review, CI, and readiness evidence. Return the parent to its
worker, then rebase and revalidate descendants bottom to top. The
orchestrator coordinates this sequence but never edits or rebases worker code.

## Feature Worker dialogue

The orchestrator may exchange only bounded control-plane messages:

- verified bootstrap and plan revision;
- execution-unit or coarse milestone request;
- evidence-only mismatch or reconciliation request;
- plan-question decision request;
- terminal-state request.

It must not prescribe code, files, commands, tests, review fixes, or design.
The Feature Worker owns implementation semantics, conflict resolution,
validation, candidate evidence, exact-HEAD review, and fixes.

The orchestrator is the only task creator for implementation. A Feature
Worker never creates another worker or planner task.

## Ledger boundary

The orchestrator alone reads and writes the SQLite WAL ledger. Feature Workers
return bounded evidence through the task handoff and never access ledger state.
Store only durable claims, assignment identity, checkpoints, exact candidate
heads, user-authority waits, and idempotent side-effect reservations. Do not
store plans, prompts, messages, execution-unit bodies, findings, or routine
worker state.

On resume, reread the authoritative plan, repository/project destination,
current base and full HEAD, worker identity, and hosted delivery state before
another side effect. Ledger text never proves external state.
