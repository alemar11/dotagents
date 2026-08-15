---
name: implement
description: "Implement or resume only the published Features named by caller-supplied GitHub issue references, from refreshed selected base branches. A fresh run creates one new project-visible ChatGPT application task for the orchestrator and one per-Feature Worker; a validated resume reuses only the exact bound tasks. Deliver each Feature through one resumable worker and pull request, centrally monitor exact-head delivery, and leave merge and post-merge closure to the user."
---

# Implement Feature Plan Sets

## Input and output invariant

Use this skill only for an explicit request to implement or resume one or more
published SE Features identified by caller-supplied GitHub parent issue
references. The caller must provide one or more exact issue URLs or
repository-qualified issue IDs; an unqualified numeric issue ID is valid only
when one target repository is already unambiguous. The selected implementation
set is exactly those parent issues. Never discover or auto-add a Feature from a
Plan Set ID, sibling registry, title, search result, GitHub label, or native
Issue Type, and never enlarge the selected implementation set.

Each supplied parent issue must resolve to one complete, authoritative sibling
Feature registry. The selected parent Feature issue is the required semantic
contract, and every selected Feature member must have:

- `feature_plan_set_id`, revision, stable `feature_id`, repository identity,
  and complete hosted readback;
- the exact authoritative parent issue reference supplied by the caller;
- an observable outcome, scope, and non-goals;
- a usable landing state, ownership boundary, and delivery reason;
- stable Feature acceptance criteria using F-AC-NN identities;
- monotonic Feature acceptance high-water evidence;
- resolved material questions, explicit assumptions, risks, and validation
  intent;
- Feature-level `blocked_by` readback to Feature IDs in the same set;
- authoritative set-membership and Feature dependency readback;
- available native GitHub dependency attempt/readback evidence as diagnostic
  provider projection only;
- a complete textual handoff that is ready for technical interpretation;
- publication and readiness evidence.

The local Macro Task registry and hosted child Task issues are optional
planning projections for Implement. Classify their observed availability as
`complete`, `partial`, or `absent`. Validate and use every unambiguous local
projection that exists, but a missing registry entry, missing child issue, or
unreadable child projection does not block implementation when the parent
Feature semantic contract is sufficient. Quarantine an extra, duplicate,
cross-set, cross-parent, cyclic, or mismatched Task projection from execution
and closure intent, record the exact degradation, and continue from the parent
Feature contract unless that defect also makes Feature outcome, scope, F-AC,
or Feature-level dependencies ambiguous. Never invent, repair, or publish a
Task issue automatically.

The caller may provide one optional `starting_branch` selection per target
repository. This is a selectable invocation input, not Feature Plan content or
durable configuration. An unqualified value is valid only when every selected
Feature targets one repository; a multi-repository run requires each override
to be repository-qualified. When an override is omitted, resolve that
repository's authoritative provider default branch. A supplied branch must
exist in the declared target repository; never silently substitute the default
branch, another local branch, or the current checkout.

The hosted Feature Plan Set and selected parent Feature semantic contract are
required input. Local Macro Task projections are useful planning context, not
an implementation gate or a technical execution graph. Read sibling registry
entries only to validate set consistency and dependency context; do not expand
the implementation selection beyond the caller-supplied parent issue refs.
Feature-level `blocked_by` relations express hard outcome dependencies and may
cross repositories. Every same-repository edge is mandatory stack intent;
Implement projects every cross-repository edge as scheduling-only. Macro Task
dependencies are same-parent-only.
Read native `blockedBy`/`blocking` relations when available and compare them to
the body-backed graph, but never use them as semantic authority or a gate. A
missing, failed, unavailable, unknown, extra, or stale native projection is
reported as provider drift and does not erase, add, or alter a Plan Set edge.
Implement never repairs native issue dependencies automatically.
Macro `blocked_by` relations are local to one `parent_feature_id` and remain
eligible for technical internalization when their projections are available.
An authoritative technical Task dependency graph, published T-AC identifiers,
or automatic plan-repair result is not required input.
Implement derives internal execution units, implementation dependencies, safe
path envelopes, and runtime waves from the set and each Feature registry
during Prepare Run. Those units belong to the Implement control plane and are
not silently sent back to Feature for ordinary technical clarification.

Implement also derives deterministic `T-AC-NN` technical criteria for the
assignment. Each T-AC maps to one or more current F-AC identities and may only
specialize how those Feature criteria are demonstrated. A T-AC must never
replace, weaken, delete, or reinterpret an F-AC, or change the Feature outcome,
scope, non-goals, or dependency topology. Preserve T-AC identities across
candidate revisions in the assignment and bind their evidence to the current
exact HEAD. Every F-AC must have direct exact-HEAD evidence or coverage through
one or more mapped T-AC criteria.

Do not start from an isolated Macro Task, an isolated technical Task, local
draft, Idea, unbounded request, or preview-only plan. Implement resolves
ordinary technical ambiguity, missing execution decomposition, and acceptance
specificity autonomously. Pause the affected assignment at `plan-question` and
report the exact conflict only when no semantic-preserving implementation is
possible: F-AC contradict each other or the outcome, satisfying them requires
changing outcome or scope, Feature dependencies are contradictory or cyclic,
or a selected Feature is blocked by an unselected or unfulfilled Feature. Keep
independent Features moving. Do not create a hidden planner task or
automatically invoke se:feature.

The terminal output is one verified pull-request topology with exactly one PR
output per implementation-eligible selected Feature. Map its branch, exact
HEAD, PR, topology, Macro context, derived units, and F-AC/T-AC evidence as
specified in the terminal report; never rewrite the hosted planning artifacts.

Complete requires current exact-HEAD acceptance, PR/base/stack readback, CI,
and hosted-review evidence for every eligible Feature. Provider policy and
`closingIssuesReferences` remain optional diagnostics; the source-derived
closing intent stays in the PR body. A Feature with no exclusive implementation
delta must not receive an empty commit, empty PR, cosmetic change, or
artificial proof; report the zero-delta product question and stop that
assignment.

Keep SE-authored PR bodies reviewer-facing and durable. Exclude routine counts,
raw output, internal evidence, and mutable diagnostics; use the exact contract
in [review-delivery.md](references/review-delivery.md).

GitHub interaction is mandatory end to end. This skill never merges, deploys,
releases, or performs post-merge closure; local Git is not an alternative
terminal result. The delivery lifecycle ends at a published PR verified on its
exact HEAD. Its merge, effective closure, and later activity remain outside the
workflow; [review-delivery.md](references/review-delivery.md) owns the details.

## Shared contracts and dependencies

Read the shared workflow-graph contract before using this registry. The
registry is the structural source of truth and Mermaid is its projection.
Read the canonical human-readable [state model](references/states.md) before
interpreting a workflow node, persisted status/checkpoint pair, operation
result, provider disposition, runtime-only mode, or output label.

Before the mandatory first GitHub Feature Plan, issue, PR, review, or relation
read or write, load the shared G dependency preflight. All GitHub
transport, hosted mutation safety, publication, and read-after-write
verification belong to G-owned workflows. The explicit Implement request
implicitly authorizes only the exact selected plan and delivery writes.

GitHub labels and native Issue Types are outside the Implement input and state
model. Do not read, search, infer, validate, mutate, or gate on them. Semantic
Feature identity comes only from each caller-supplied parent issue reference
plus its structured body, Plan Set registry, and verified parent/child
relations.

Do not require or invoke $g:github-delivery-status as an Implement completion
gate. Use the focused G-owned PR publication, CI, review, and stack workflows
for the exact-head evidence this skill owns. Branch protection and rulesets
are outside this workflow; if an outer coordinator supplies provider-policy
observations, preserve them as optional provider diagnostics and never block
completion
on their availability or disposition. Automation observations never authorize
Implement to merge or change hosted policy.
Implement never merges, bypasses protections, enables or disables auto-merge, or
enqueues or dequeues a PR.

Before every hosted write, load the shared
[hosted-content-safety.md](../../references/hosted-content-safety.md) contract.
Implement owns the final portable projection; G owns transport and readback.

Before creating, resuming, or monitoring tasks, load the Implement task
profile, shared task preflight, and shared task handoff. An explicit
`se:implement` invocation is the user's request and bounded authority for the
required hierarchy; do not ask for a second task-permission confirmation. For
a fresh run, create exactly one new user-owned orchestrator task in the
invoking ChatGPT application project and one new Feature Worker task per
selected Feature in that Feature's assigned target project. A validated resume
reuses only each exact previously bound project-visible task identity. Create a
not-yet-created role only after authoritative evidence proves no prior creation
effect was applied; a missing or unverifiable retained identity blocks without
a replacement. Independently observe every required task in its project and
bind its authoritative bootstrap before role-owned effects.

The orchestrator and every Feature Worker are required application-task roles.
Subordinate in-task delegation, optional support, or another execution
envelope never satisfies or substitutes for either role. If the live
application cannot create, resume, expose, bootstrap, or monitor this
project-visible hierarchy, stop with `unsupported-runtime` and do not switch
topology. Project association and visibility are required routing evidence;
project metadata inside the task remains diagnostic, while the task's actual
Git target remains authoritative execution evidence.

Actively request each role's complete resolved model and reasoning profile;
never omit either value or rely on ambient inheritance. Project every task
prompt through the shared flat prompt projection; never forward a raw parent
prompt or transport envelope. The orchestrator is the sole delivery monitor
and uses change-driven observation. After its bounded handoff, each Worker
becomes inactive but resumable; contact it only for new actionable evidence.

Load orchestration when interpreting plans, deriving execution units,
scheduling workers, resolving plan questions, converging a first unpublished
candidate, dispatching optional support, or calculating delivery topology.
Load review-delivery at candidate review, publication, or hosted monitoring.
Load run-state before preparing, resuming, checkpointing, or resetting the
ledger.
Use [states.md](references/states.md) as the canonical human-readable meaning
of every state namespace and persisted pair.

## Transition-condition ownership

| Source nodes | Canonical condition owner |
| --- | --- |
| intake, source-preflight, runtime-preflight, prepare-run | This skill's input invariant and shared contracts |
| schedule, delivery-gate, worker-bootstrap, implement-validate, plan-question, assignment-blocked, assignment-deferred, release-claims | orchestration.md |
| candidate, native-review, review-decision, publish-pr, stack-reconcile, candidate-published, delivery-monitor, final-verify | review-delivery.md |
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
