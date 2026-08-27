# Implement Orchestration

This reference owns Feature Plan Set scheduling, textual-plan interpretation,
application-task control, user plan questions, actionable-frontier selection,
and delivery-topology routing. Worker implementation belongs to
[worker-execution.md](worker-execution.md); publication and monitoring are
routed to their phase owners below.
Use [states.md](states.md) for the canonical meaning of workflow nodes,
persisted status/checkpoint pairs, runtime-only modes, and terminal invocation
outcomes.

Before any hosted publication or user-facing hosted relay, apply the shared
[hosted-content-safety.md](../../../references/hosted-content-safety.md)
contract to the exact final content. G owns transport and readback.

## Control plane

The orchestrator coordinates the exact caller-selected Features. Each retains
its Feature and repository identity, Macro projection state, one assignment,
one Feature Worker, and one PR output. The orchestrator derives execution units
and T-AC criteria before scheduling, owns all ledger and aggregate state, and is
the sole monitor after publication.

Run independent Features concurrently only when repository, path envelope,
implementation prerequisites, Feature dependency context, and observed capacity
are safe. A same-repository child may start from its verified
`candidate-published` parent HEAD when no applicable current-head CI check is
confirmed failing. Pending CI is allowed; bypass a confirmed failure only after
G-owned diagnosis proves it exclusively infrastructure or flaky and unrelated
to candidate correctness. Serialize unsafe overlap and cross-repository outcome
dependencies. Never invent dependencies, impose a fixed Worker cap, or stop
independent work because another assignment is blocked, deferred, or
delivery-pending.

Before any Worker starts, claim the complete sorted Feature set atomically. A
conflicting active claim blocks startup without partial claims or a competing
orchestrator. Release the complete claim set only after terminal
reconciliation.

## Actionable frontier and handoff discipline

At every scheduling point, derive the set of effects that are currently
dependency-ready, capacity-safe, authorized, and unambiguous. When exactly one
effect is eligible, perform it directly and reconcile its immediate result
before emitting another scheduling report. When several effects are eligible,
retain normal dependency, safety, capacity, and fairness arbitration. When no
effect is eligible, preserve the current observation lineages and wait for a
material change or close with the applicable terminal outcome.

Direct execution never crosses a pending Worker or provider effect, a required
operation reservation or readback, ambiguous identity or authority, a user
decision, multiple eligible effects, or an exact-HEAD or recovery
reconciliation boundary. The actionable frontier is derived transient control
logic, not a field, status, checkpoint, runtime mode, or ledger value.

Before creating or resuming a Feature Worker, freeze one complete but compact
handoff. It contains or canonically references the run and Feature identities,
repository/project destination, exact base and intended branch ownership,
`feature_plan_set_id` and revision, current `runtime_contract_version`,
publication stop boundary, requested Worker profile and bootstrap-result
contract, phase references, and the result expected at an existing workflow
node. The Plan Set revision and runtime contract version are the stable source
and runtime contract generation; do not invent another field. Project source
contracts and shared doctrine by reference; never paste this skill, a parent
prompt, prior bootstrap result, or transcript into the Worker prompt.

The shared [task handoff](../../../references/task-handoff.md) owns
change-driven observation and relay. For control-plane reconciliation between
assigned tasks, a material delta is a new workflow node or persisted pair,
candidate/provider HEAD or evidence fingerprint, claim/reservation/authority
decision, review finding or disposition, blocker or user decision,
execution-target change, or terminal result. Relay only the new facts and the
identifiers needed to bind them to the existing assignment.

A control-plane delta is not automatically a user-facing update. The outer
controller coalesces internal node, checkpoint, and milestone changes and
reports them only when they introduce or resolve a blocker, require a user
decision, materially change mutation authority or delivery evidence, or reach a
terminal result. It does not mirror every orchestrator transition or unchanged
observation. The orchestrator likewise does not send a generic `continue`
message while [worker execution](worker-execution.md) still owns an eligible
local action.

## Application-task control hierarchy

Apply the shared [task handoff](../../../references/task-handoff.md) to both
required controller edges. The invoking controller creates or resumes the one
orchestrator in the invoking application project, independently observes its
stable identity, project visibility, state, and title, and binds the
orchestrator's assigned-task bootstrap before normal relay. The orchestrator's
first turn performs that authoritative self-check before ledger, repository,
Worker, or hosted effects.

That controller-to-orchestrator bootstrap is the invocation envelope outside
the Implement node registry. The verified orchestrator enters the graph at
`intake`. A `source-preflight` failure creates no Feature Worker, ledger,
worktree, branch, publication, or other downstream effect; retain only the
orchestrator bootstrap and authoritative source-read evidence needed to report
the failure.

A fresh run creates new required roles; a validated resume reuses only the exact
retained project-visible identities. Create a missing role only after
authoritative evidence proves no prior creation effect was applied. Missing or
unverifiable retained identity is `unsupported-runtime`, never authority for a
replacement.

After bootstrap, the orchestrator becomes controller for every Feature Worker.
It freezes the assignment-specific request, creates or resumes the Worker in
the target repository's application project, independently observes the stable
identity and project visibility, and binds the Worker's authoritative bootstrap
and actual Git target before accepting role work. The Worker performs this
self-check before content writes, never creates another Feature Worker, and may
have a profile intentionally different from the orchestrator.

Both edges are required project-visible application tasks; subordinate
delegation cannot satisfy either. Optional support may start only below a
verified Worker. Preserve the same task after `unsupported-runtime`,
`effective-profile-mismatch`, `task-identity-mismatch`, or
`execution-target-mismatch` and follow the shared reconciliation path. These
checks add no ledger state.

## Starting-branch selection and freshness

Treat `starting_branch` as caller-owned input scoped to one repository.
Require repository-qualified overrides for multi-repository runs and use the
authoritative provider default only where no override exists. Reject a missing,
ambiguous, inaccessible, or wrong-repository selection without fallback.

Before each standalone or stack-root bootstrap wave, use G-owned branch
transport to refresh the selected upstream and read its full remote tip SHA.
Do not rely on a fetch receipt, stale tracking ref, current checkout, or branch
name alone. Any local update used for bootstrap must be fast-forward-only and
preserve unrelated or dirty checkout state; otherwise use an isolated ref or
block.

Freeze that tip as the wave's `base_branch` and `base_sha`. Reread it before
each worktree creation. If it changes, stop unstarted bootstraps, refresh, and
recompute that remainder so one wave never mixes base SHAs. Verify every new
worktree starts at the frozen SHA; attached or detached HEAD is valid. Project
metadata is not Git evidence.

After task identity, profile, and initial target match, the Worker establishes
its deterministic `head_branch` from the unchanged base through G-owned branch
transport and reads back branch and HEAD before content writes. Only then record
`active @ worker-bootstrap`. On recovery, the recorded head branch is required.

A stacked child instead starts at its verified immediate parent's
`candidate-published` branch and exact candidate SHA, then creates its own
head branch. The repository selection still governs the stack root and landing
branch.

## Macro plan interpretation and execution units

Resolve only the caller-supplied parent issues. Verify their Plan Set identity,
revision, sibling membership, Feature contract, F-AC set, high-water evidence,
and Feature-level `blocked_by`; siblings never expand the selection. Classify
local Macro projections as `complete`, `partial`, or `absent`, use verified
children as context, and quarantine invalid projections. Continue when the
parent contract remains sufficient, and never create or repair a hosted Task.

`source-preflight` blocks the invocation when a selected parent contract or the
identity and direction of its semantic dependency relation is unreadable or
ambiguous. An edge to an unselected Feature does not expand the selection:
observe only the upstream identity and fulfillment evidence needed to interpret
the selected contract. Missing or negative fulfillment evidence is then an
assignment-local dependency condition under `delivery-gate` or `plan-question`,
so independent selected Features continue; it is not a whole-run source failure
when the relation itself is authoritative.

GitHub labels and native Issue Types are outside this workflow. Native
`blockedBy` and `blocking` are diagnostic only and never create, remove,
repair, or gate a semantic edge. Same-repository Feature edges create stack
intent; cross-repository edges create scheduling order; Macro edges remain
same-parent planning context. None automatically becomes a technical
execution-unit edge.

Derive stable assignment-scoped `T-AC-NN` criteria and map each to current
F-AC identities without changing outcome, scope, non-goals, or dependency
topology. Every F-AC needs direct exact-HEAD evidence or mapped T-AC coverage,
and every T-AC needs exact-HEAD evidence. Preserve their identities across
candidate revisions.

An upstream Feature outside the selected and fulfilled scope blocks or defers
its dependent assignment. A same-repository dependent becomes runnable only
from a verified `candidate-published` ancestor vector satisfying the current
CI rule; a cross-repository dependent remains ordered and standalone.

Each derived unit records one observable technical outcome, repository/path
scope, implementation and validation intent, F-AC/T-AC mapping, real
prerequisites, and expected Worker evidence. Use small technical vertical
units. Path overlap, capacity, preferred order, and delivery topology remain
separate scheduling facts rather than invented prerequisites. The Worker may
refine technical units and T-AC details while preserving the Feature contract;
Implement never rewrites the Plan Set or Macro registry.

## User plan questions

Resolve ordinary decomposition, implementation, and acceptance detail inside
Implement. Enter `plan-question` only when no contract-preserving result is
possible because criteria conflict with each other or the outcome, scope must
change, dependencies are contradictory or cyclic, or an unselected or
unfulfilled Feature blocks the assignment. Persist `deferred @ plan-question`
without storing the question body, and keep independent Features moving.

Do not create a planner task. If the answer requires a published Plan Set
change, report the required se:feature maintenance and preserve safe Worker
evidence.

## Execution and delivery topology

Bootstrap exactly one Feature Worker per selected Feature. It executes derived
units in prerequisite order inside one isolated worktree, commits coherent
units of work, and may use bounded optional support only under
[worker-execution.md](worker-execution.md).

Delivery topology is independent of execution order. A Feature is standalone
when it has no same-repository Feature parent; otherwise it is stacked on one
verified immediate parent branch and exact `candidate-published` HEAD.
Serialization caused by overlap, capacity, or preference stays standalone. For
fan-in, select one immediate parent only when its candidate contains every
required prerequisite HEAD; otherwise require Plan Set reconciliation.

Before stacked-child bootstrap, reread parent PR, branch, full HEAD,
publication checkpoint, stack capability, and applicable current-head CI.
Stale or ambiguous evidence blocks only that child and never degrades it to
standalone. Parent HEAD drift returns affected descendants to their same
Workers for bottom-to-top rebase, validation, publication, and hosted review;
native review does not restart after verified first publication.

## Worker execution routing

The Feature Worker owns implementation, optional support, pre-candidate
convergence, complete candidate-bound validation, hosted-finding repair, and
valid existing-node exits under
[worker-execution.md](worker-execution.md). The orchestrator supplies the
verified handoff, accepts only those bounded outcomes, and never prescribes
code, files, commands, tests, review fixes, or design.

## Publication and monitoring handoff

Publication, stack reconciliation, and the verified `candidate-published`
boundary belong to [review-delivery.md](review-delivery.md). Hosted review, CI,
provider observation, repair resumption, and final verification belong to
[delivery-monitoring.md](delivery-monitoring.md).

After a verified publication handoff, return to `schedule`. An unchanged
pending observation adds no eligible effect to the actionable frontier. New
actionable evidence resumes the same Feature Worker only after its path
envelope is reacquired, and the resumption contains only the new evidence plus
the identifiers needed to bind it to the retained assignment. Independent
runnable assignments and delivery lineages continue fairly.

## Ledger boundary

The orchestrator alone reads and writes the SQLite WAL ledger. Feature Workers
return bounded evidence through the task handoff and never access ledger state.
Store only durable claims, assignment identity, checkpoints, exact candidate
heads, user-authority waits, and idempotent side-effect reservations. Do not
store plans, prompts, messages, execution-unit bodies, findings, or routine
worker state.

`delivery-pending @ candidate-published` is one coarse status/checkpoint pair,
not two sequential states or a second delivery engine. The ledger never proves
that a Worker is inactive, that a PR remains current, or that a path envelope
is free; recover each fact from the application, repository, provider, and
transient control plane.

On resume, reread the authoritative plan, repository execution target, current
base and full HEAD, worker identity, and hosted delivery state before another
side effect. Ledger text never proves external state.
