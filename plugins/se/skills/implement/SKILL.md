---
name: implement
description: "Implement or resume only the published Features named by caller-supplied GitHub issue references, from refreshed selected base branches. A fresh run creates one new observable user-owned ChatGPT application task for the orchestrator and one per-Feature Worker; a validated resume reuses only the exact bound tasks. Deliver each Feature through one resumable worker and pull request, centrally monitor exact-head delivery, and leave merge and post-merge closure to the user."
---

# Implement Feature Plan Sets

## Scope and result

Use this skill only for an explicit request to implement or resume one or more
published SE parent Features identified by caller-supplied GitHub issue
references. The selected set is exactly those parent issues. Never discover or
add Features from a Plan Set ID, sibling registry, title, search, label, native
Issue Type, or dependency edge. An unqualified issue number is valid only when
one target repository is unambiguous.

Each selected parent issue must resolve to one complete authoritative sibling
registry and the exact supplied parent reference. Require
`feature_plan_set_id`, revision, stable `feature_id`, repository identity and
complete hosted readback; observable outcome, scope, non-goals, landing state,
ownership boundary, and delivery reason; stable F-AC-NN criteria and monotonic
high-water evidence; resolved material questions, explicit assumptions, risks,
and validation intent; Feature-level `blocked_by`, set-membership and dependency
readback; a complete textual handoff ready for technical interpretation; and
publication readiness. Sibling entries are consistency and dependency evidence
only.

Classify the optional local Macro Task registry and hosted child projections as
`complete`, `partial`, or `absent`. Use every verified unambiguous child as
planning context and closure intent. Quarantine missing, extra, duplicate,
cross-set, cross-parent, cyclic, or mismatched projections and continue when the
parent Feature contract is still sufficient. Never invent, repair, or publish a
Task projection during Implement.

The caller may select one optional `starting_branch` per repository. Require
repository-qualified overrides for a multi-repository run; otherwise use that
repository's authoritative provider default. Reject a supplied branch that is
missing, ambiguous, inaccessible, or belongs to another repository. Refresh
and freeze the exact selected upstream tip before root Worker bootstrap; never
silently substitute the current checkout or another branch.

Feature-level `blocked_by` is semantic authority and may cross repositories.
Every same-repository edge is mandatory stack intent; every cross-repository
edge is scheduling-only. Native GitHub dependency relations are diagnostic and
never add, remove, repair, or gate an edge. Macro dependencies remain
same-parent planning context and never define a Worker or PR boundary.

During Prepare Run, derive transient technical execution units, safe path
envelopes, real implementation prerequisites, and stable assignment-scoped
`T-AC-NN` criteria. Every T-AC specializes one or more current F-AC criteria
without replacing, weakening, or reinterpreting them, and both evidence sets
bind to the current exact HEAD. Resolve ordinary technical ambiguity inside
Implement. Enter `plan-question` only when no semantic-preserving
implementation exists because criteria or outcome conflict, scope must change,
Feature dependencies are contradictory or cyclic, or an unselected or
unfulfilled Feature blocks the selection.

The result is exactly one verified PR output per implementation-eligible
Feature, standalone or stacked as derived above. Its source-derived closing set
contains only that parent Feature and every verified existing associated local
Macro Task. A Feature with no exclusive implementation delta receives no empty
commit, cosmetic change, artificial proof, or empty PR; report the product
question and stop that assignment.

GitHub is mandatory end to end. Implement never merges, deploys, releases,
changes provider policy, performs post-merge closure, or substitutes a local
result. Complete requires one current exact-HEAD PR topology with complete
F-AC/T-AC validation, hosted review, CI, body/closure-intent, base, and stack
readback for every eligible Feature.

## Non-negotiable runtime invariants

A fresh run creates one observable user-owned application task for the
orchestrator and exactly one observable user-owned Feature Worker task for each
selected Feature. A validated resume reuses only the exact retained identities.
Subordinate delegation and optional support never replace either required role,
and an unavailable or unverifiable required task fails closed without a
replacement. Application routing and saved-project metadata never establish or
invalidate either role.

Before any task effect, load [task-profile.md](references/task-profile.md), the
shared [task preflight](../../references/task-preflight.md), and the shared
[task handoff](../../references/task-handoff.md). Actively request each
role's complete model and reasoning profile, bind its authoritative assigned
task bootstrap and Git execution target to the independently observed stable
task identity, and reconcile its deterministic title once. The explicit
Implement invocation authorizes only this required hierarchy and its declared
delivery effects.

The orchestrator alone owns the SQLite ledger, Feature claims, path-claim
coordination, side-effect reservations, delivery monitoring, and aggregate
completion. A Worker owns one Feature's implementation, validation, candidate
and repair semantics; it never accesses the ledger or polls its inactive PR.

Before first publication, complete validation and native review bind to the
same exact candidate HEAD in the same Worker. Any pre-publication HEAD change
invalidates both and repeats that gate. Exact first-PR publication readback
permanently transfers review authority to the hosted lineage; later repairs,
rebases, or parent drift update the same PR and never restart native review.
Complete validation and clean hosted review must converge on the same final
exact HEAD.

Before the first required GitHub read or write, load the shared
[G dependency preflight](../../references/codex-dependency-preflight.md).
Route every Git and GitHub operation through its G-owned workflow and apply the
shared [hosted-content-safety.md](../../references/hosted-content-safety.md)
contract immediately before every hosted write. Branch protection, rulesets,
merge queue, auto-merge, and the general delivery-status workflow are not
completion gates.

The role about to make each G handoff owns that handoff's dependency gate. A
prior pass never substitutes for the next required handoff gate.

## Phase routing

Read the shared [workflow-graph contract](../../references/workflow-graph.md)
before using this registry, and read
[states.md](references/states.md) before interpreting any workflow node,
persisted pair, provider disposition, runtime-only mode, or output label. Load
only the current role and phase owner:

| Role or phase | Canonical reference |
| --- | --- |
| Controller and orchestrator bootstrap, plan interpretation, scheduling, topology, plan questions, and aggregate control | [orchestration.md](references/orchestration.md) |
| Feature Worker implementation, optional support, pre-candidate convergence, complete validation, and phase exits | [worker-execution.md](references/worker-execution.md) |
| Candidate boundary, native review, first publication or PR update, stack reconciliation, and candidate-published handoff | [review-delivery.md](references/review-delivery.md) |
| Ready transition, hosted review and CI, repair monitoring, provider diagnostics, and final verification | [delivery-monitoring.md](references/delivery-monitoring.md) |
| Ledger preparation, checkpointing, reservation, reset, or recovery | [run-state.md](references/run-state.md) |

The orchestrator loads monitoring guidance only after a verified publication
handoff. The Worker loads review-delivery only after candidate-bound validation
reaches `candidate`; it never loads ledger or aggregate-monitoring doctrine.
Project stable source facts and shared contracts by canonical reference rather
than copying them into task prompts.

The shared handoff owns change-driven relay. Implement specializes material
deltas and actionable-frontier scheduling in orchestration, while
worker-execution owns autonomous progress to existing-node phase boundaries.
These refinements add no mode, state, checkpoint, ledger field, or alternate
topology.

## Transition-condition ownership

| Source nodes | Canonical condition owner |
| --- | --- |
| intake, source-preflight, runtime-preflight, prepare-run | This skill's scope, invariants, and shared contracts |
| schedule, delivery-gate, worker-bootstrap, plan-question, assignment-blocked, assignment-deferred, release-claims | orchestration.md |
| implement-validate | worker-execution.md |
| candidate, native-review, review-decision, publish-pr, stack-reconcile, candidate-published | review-delivery.md |
| delivery-monitor, final-verify | delivery-monitoring.md |
| deferred, complete, blocked | This skill's terminal definitions |

Each owner defines every declared outgoing condition and must not add an
unregistered edge. Run-state owns persistence and recovery evidence, not
workflow transitions.

## Workflow graph

| node_id | kind | entry condition | transitions | side effects | terminal state |
| --- | --- | --- | --- | --- | --- |
| intake | action | explicit implementation or resume request with one or more exact parent Feature issue refs | source-preflight, blocked | none | none |
| source-preflight | validation | every supplied parent Feature semantic contract and its dependency context are readable; Macro projection state is classified | runtime-preflight, blocked | hosted | none |
| runtime-preflight | validation | plans, target repositories, and selected or default starting branches are known and refreshable | prepare-run, blocked | read | none |
| prepare-run | action | required roles, destinations, refreshed base snapshots, and plan interpretation are ready | schedule, blocked | durable | none |
| schedule | decision | run is ready for another Feature wave, published-candidate observation, or aggregate reconciliation | delivery-gate, delivery-monitor, release-claims, deferred, blocked | none | none |
| delivery-gate | decision | unfinished Feature assignments are candidates for the next wave | worker-bootstrap, schedule, assignment-blocked, blocked | read | none |
| worker-bootstrap | action | one or more Feature assignments are dependency-ready | implement-validate, assignment-blocked, blocked | durable | none |
| implement-validate | action | Feature Worker identity, worktree, sibling context, Macro projection state, derived execution units, and F-AC/T-AC criteria are verified; implementation and validation converge under Worker ownership | candidate, final-verify, plan-question, assignment-blocked, blocked | durable, hosted | none |
| plan-question | decision | a semantic conflict requires user authority because no contract-preserving implementation exists | schedule, assignment-deferred, blocked | none | none |
| candidate | validation | Feature Worker reports a committed candidate HEAD with the required initial or published-repair evidence | native-review, publish-pr, assignment-blocked, blocked | read, durable | none |
| native-review | action | Feature Worker session is pinned to the committed candidate HEAD | review-decision, assignment-blocked, blocked | read, durable | none |
| review-decision | decision | in-session review result is bound to the current candidate HEAD | implement-validate, publish-pr, assignment-blocked, blocked | durable | none |
| publish-pr | action | pre-publication native review is clean, or a verified existing PR makes hosted review authoritative for this repair candidate | stack-reconcile, candidate-published, assignment-blocked, blocked | hosted, durable | none |
| stack-reconcile | validation | a stacked PR was published or its parent/base/link/exact-HEAD evidence drifted | candidate-published, implement-validate, assignment-blocked, blocked | read, durable | none |
| candidate-published | validation | PR identity, branch, exact candidate HEAD, closing set, and any required stack link are verified | schedule, assignment-blocked, blocked | read, durable | none |
| delivery-monitor | action | one or more published assignments are delivery-pending on a verified exact PR HEAD | schedule, implement-validate, stack-reconcile, final-verify, assignment-blocked, blocked | hosted, durable | none |
| final-verify | validation | current PR, topology, CI, review, checkout, HEAD, and acceptance evidence are available | schedule, stack-reconcile, assignment-blocked, blocked | read | none |
| assignment-blocked | action | one Feature assignment cannot progress but independent work remains | schedule | durable | none |
| assignment-deferred | action | one Feature assignment awaits bounded user authority | schedule | durable | none |
| release-claims | action | every assignment is `delivery-ready @ final-verify` and every operation is resolved | complete, blocked | durable | none |
| deferred | terminal | all remaining work awaits user authority | none | none | deferred |
| complete | terminal | every eligible Feature maps to one verified PR-ready output | none | none | complete |
| blocked | terminal | required evidence, capability, identity, authority, or reconciliation is unavailable | none | none | blocked |

~~~mermaid
flowchart TD
    intake --> source-preflight
    intake --> blocked
    source-preflight --> runtime-preflight
    source-preflight --> blocked
    runtime-preflight --> prepare-run
    runtime-preflight --> blocked
    prepare-run --> schedule
    prepare-run --> blocked
    schedule --> delivery-gate
    schedule --> delivery-monitor
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
    implement-validate -->|published HEAD unchanged after complete validation| final-verify
    implement-validate --> plan-question
    implement-validate --> assignment-blocked
    implement-validate --> blocked
    plan-question --> schedule
    plan-question --> assignment-deferred
    plan-question --> blocked
    candidate -->|first publication| native-review
    candidate -->|published repair| publish-pr
    candidate --> assignment-blocked
    candidate --> blocked
    native-review --> review-decision
    native-review --> assignment-blocked
    native-review --> blocked
    review-decision --> implement-validate
    review-decision --> publish-pr
    review-decision --> assignment-blocked
    review-decision --> blocked
    publish-pr -->|standalone| candidate-published
    publish-pr -->|stacked| stack-reconcile
    publish-pr --> assignment-blocked
    publish-pr --> blocked
    stack-reconcile --> candidate-published
    stack-reconcile -->|published drift| implement-validate
    stack-reconcile --> assignment-blocked
    stack-reconcile --> blocked
    candidate-published --> schedule
    candidate-published --> assignment-blocked
    candidate-published --> blocked
    delivery-monitor --> schedule
    delivery-monitor --> implement-validate
    delivery-monitor --> stack-reconcile
    delivery-monitor --> final-verify
    delivery-monitor --> assignment-blocked
    delivery-monitor --> blocked
    final-verify --> schedule
    final-verify --> stack-reconcile
    final-verify --> assignment-blocked
    final-verify --> blocked
    assignment-blocked --> schedule
    assignment-deferred --> schedule
    release-claims --> complete
    release-claims --> blocked
~~~

## Terminal report

Return one aggregate report with:

- every caller-supplied parent issue ref and its authoritative Feature Plan Set
  and Feature/repository member;
- the Macro projection state (`complete`, `partial`, or `absent`), every
  verified local parent/child Task identity, and every quarantined defect;
- every Feature-level dependency and its scheduling/technical interpretation;
- every observed native dependency result or drift warning, explicitly marked
  non-authoritative and non-blocking;
- every derived execution unit and its F-AC/T-AC mapping plus any available
  Macro context;
- every T-AC and its mapping to final Feature evidence;
- every Feature Worker identity and verified destination;
- every repository's requested or default starting branch, refreshed full base
  SHA, and the worktree-bootstrap readback bound to that SHA;
- execution waves, path-overlap evidence, and deferred or blocked assignments;
- candidate, `delivery-pending @ candidate-published`, Worker resumption,
  review, publication, CI, stack, and exact-HEAD evidence;
- Feature acceptance evidence bound to each final candidate SHA;
- one source-derived `closing_issue_refs` set per Feature containing only that
  parent Feature and every verified existing associated local Macro Task, plus exact PR-body
  closure-intent readback; any GitHub `closingIssuesReferences` observation is
  optional diagnostic evidence and never a gate;
- aggregate outcome complete, deferred, or blocked.

Never claim completion while an eligible Feature lacks a verified PR,
current exact-HEAD evidence, or verified F-AC and derived T-AC coverage. A
reported `partial` or `absent` Macro projection is not by itself incomplete.

## Terminal meanings

- complete: every eligible Feature has verified PR delivery and the
  aggregate evidence is reconciled;
- deferred: all remaining work awaits explicit user authority;
- blocked: a required contract, capability, identity, authority, or
  reconciliation result is unavailable.
