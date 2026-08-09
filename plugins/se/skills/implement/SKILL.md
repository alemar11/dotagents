---
name: implement
description: "Implement or resume only the published Features named by caller-supplied GitHub issue references, from refreshed selected base branches. Deliver each Feature through one resumable worker and pull request, centrally monitor exact-head delivery, and leave merge and post-merge closure to the user."
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
Issue Type.

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
cross repositories. Implement projects every same-repository edge as mandatory
stack intent and every cross-repository edge as scheduling-only.
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

The expected terminal output is one verified pull-request delivery topology
with exactly one PR output per implementation-eligible selected Feature.
Return a complete mapping from each Feature ID, its available local Macro Task
projections, and its derived execution units to its repository, Feature branch,
exact HEAD, PR reference, and standalone or stacked relationship. Bind every
Feature acceptance criterion and derived T-AC to evidence on the same final
candidate HEAD. Map available Macro Task outcomes as planning context, but do
not make missing projections an acceptance gate. T-AC identities are
Implement-owned evidence and never rewrite the hosted Plan Set or Macro Task
registries.

Complete means every implementation-eligible Feature has a verified
standalone-ready or stack-ready PR output on its current exact HEAD, all
required Feature criteria and derived T-AC coverage are verified against that
HEAD, the PR/base/stack topology is read back, and current CI and hosted
review evidence contain no unresolved actionable feedback. Branch protection,
rulesets, mergeability policy, merge queues, and auto-merge are outside the
Implement completion contract and may only be reported as optional provider
diagnostics. The Feature's source-derived closing set is still read back as
PR-body publication intent; GitHub's `closingIssuesReferences` field is an
optional provider diagnostic and never a completion gate. A Feature with no exclusive
implementation delta must not receive an empty commit, empty PR, cosmetic
change, or artificial proof; report the zero-delta product question to the
user and stop that assignment.

Keep SE-authored PR bodies reviewer-facing and durable: a short outcome
summary, compact names of validation commands or check categories, only
material operational notes, and the G-rendered closing lines. Do not publish
routine test counts, pass totals, raw output, internal execution evidence, or
other mutable delivery diagnostics in the PR body. The exact contract lives in
[review-delivery.md](references/review-delivery.md).

This skill never merges, deploys, releases, or performs post-merge closure.
GitHub interaction is mandatory end to end. Local worktrees and local Git
transport are execution surfaces inside the implementation flow, never an
alternative terminal result.

The delivery lifecycle ends at a published PR verified on its exact HEAD.
The PR may remain open; merge, effective Feature/Macro Task closure, and all
post-merge activity remain outside the workflow. The canonical lifecycle and
the registry-derived closure intent are defined in
[review-delivery.md](references/review-delivery.md).

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
observations, preserve them as optional diagnostics and never block completion
on their availability or disposition. Automation observations never authorize
Implement to merge or change hosted policy.
Implement never merges, bypasses protections, enables or disables auto-merge, or
enqueues or dequeues a PR.

Before every hosted write, load the shared
[hosted-content-safety.md](../../references/hosted-content-safety.md) contract.
Implement owns the final portable projection; G owns transport and readback.

Before creating, resuming, or monitoring application tasks, load the
Implement task profile, shared task preflight, and shared task handoff. The
orchestrator and every Feature Worker are required roles. Stable task-identity
observation, authoritative assigned-task profile bootstrap, Git
execution-target verification, and title reconciliation are required before
normal monitoring or update relay. Saved-project identity and project-root
metadata remain optional diagnostics.
Actively request each role's complete resolved model and reasoning profile;
never omit either value or rely on ambient inheritance. Project every
orchestrator, Feature Worker, and optional support prompt through the shared
flat prompt projection; never forward a raw parent prompt or transport envelope.

The invoking task controller creates or resumes the orchestrator,
independently observes its stable task identity, and binds the orchestrator's
structured bootstrap result to that identity. An orchestrator already started
from that handoff reads its own authoritative task-scoped execution context and
performs the shared assigned-task bootstrap self-check before ledger,
repository, Worker, or hosted effects. It does not create another
orchestrator. After bootstrap, the orchestrator is the task controller for
Feature Workers: it creates or resumes each Worker, independently observes the
stable Worker identity, and binds that Worker's authoritative bootstrap result
before accepting implementation. Never compare the invoking controller's
profile with the orchestrator, or the orchestrator's profile with a Worker;
compare only each exact assigned task's self-observed values with its own
resolved request.

The orchestrator is the sole delivery monitor and aggregate lifecycle owner.
After a PR reaches `candidate-published`, its Feature Worker becomes inactive
but resumable while the assignment remains `delivery-pending`. The
orchestrator observes exact-head hosted review, CI, and stack drift through
G-owned workflows; it contacts the same Worker only for an actionable fix,
evidence repair, or rebase.

The Feature Worker may use the task profile's optional delegated support role
for bounded code analysis, execution-unit assistance, validation, or critique.
Before the first optional support effect, inspect delegation once and record
delegation as available, unavailable, or unknown separately from observed
worker capacity. Delegation is not a required topology gate: when it is
unavailable, unknown, or has no usable capacity, the Feature Worker performs
the same work serially and the run continues.

Load orchestration when interpreting plans, deriving execution units,
scheduling workers, resolving plan questions, or calculating delivery
topology. Load review-delivery at candidate review and publication. Load
run-state before preparing, resuming, checkpointing, or resetting the ledger.
Use [states.md](references/states.md) as the canonical human-readable meaning
of every state namespace and persisted pair.

## Transition-condition ownership

| Source nodes | Canonical condition owner |
| --- | --- |
| intake, source-preflight, runtime-preflight, prepare-run | This skill's input invariant and shared contracts |
| schedule, delivery-gate, worker-bootstrap, plan-question, assignment-blocked, assignment-deferred, release-claims | orchestration.md |
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
| implement-validate | action | Feature Worker identity, worktree, sibling context, Macro projection state, derived execution units, and F-AC/T-AC criteria are verified | candidate, plan-question, assignment-blocked, blocked | durable, hosted | none |
| plan-question | decision | a semantic conflict requires user authority because no contract-preserving implementation exists | schedule, assignment-deferred, blocked | none | none |
| candidate | validation | Feature Worker reports a committed candidate HEAD with plan criteria evidence | native-review, assignment-blocked, blocked | read, durable | none |
| native-review | action | Feature Worker session is pinned to the committed candidate HEAD | review-decision, assignment-blocked, blocked | read, durable | none |
| review-decision | decision | in-session review result is bound to the current candidate HEAD | implement-validate, publish-pr, assignment-blocked, blocked | durable | none |
| publish-pr | action | review is clean and publication scope is resolved | stack-reconcile, candidate-published, assignment-blocked, blocked | hosted, durable | none |
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
    implement-validate --> plan-question
    implement-validate --> assignment-blocked
    implement-validate --> blocked
    plan-question --> schedule
    plan-question --> assignment-deferred
    plan-question --> blocked
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
    publish-pr -->|standalone| candidate-published
    publish-pr -->|stacked| stack-reconcile
    publish-pr --> assignment-blocked
    publish-pr --> blocked
    stack-reconcile --> candidate-published
    stack-reconcile --> implement-validate
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

The orchestrator control plane and Feature Worker lifecycle are one
hierarchical graph. They are not independent runs. A Feature Worker is an
application task plus its isolated worktree lifecycle; native-review is a
phase inside that lifecycle, not a second worker. Optional support
assignments are subordinate execution envelopes, not Feature Workers, graph
nodes, Feature members, or ledger assignments.

## Plan interpretation and orchestration

Source-preflight resolves only the exact caller-supplied parent issue refs,
then reads each authoritative Feature Plan Set manifest, its hosted sibling
registry, the selected parent Feature semantic contract, and any reachable
local Macro Task children. It verifies set identity/revision, distinct Feature
membership, repository identity, outcome, scope, non-goals, Feature criteria,
Feature-level `blocked_by`, publication readback, resolved questions, and plan
status. Sibling entries are consistency and dependency evidence only; they
never enlarge the selected implementation set. Classify Macro projections as
`complete`, `partial`, or `absent`; validate and use verified local children,
quarantine malformed or foreign projections, and report the degradation
without blocking when the parent semantic contract remains sufficient. A
contradictory or cyclic Feature dependency topology, or an ambiguous parent
semantic contract, blocks before worker creation. GitHub labels and native
Issue Types are never read or evaluated. Native issue dependencies may be read
only as diagnostic projection evidence; mismatch or absence never changes the
body-backed graph and is non-blocking.
Runtime-preflight independently verifies every selected repository, remote,
current checkout or worktree constraint, required application roles, and the
G-owned workflows needed for the run. For each repository, it resolves the
caller-selected `starting_branch` or the authoritative provider default,
verifies its upstream identity, refreshes the branch state used for isolated
worktree creation, and freezes the resulting full tip SHA. Current checkout
state or a previously fetched local ref is never freshness evidence. The
detailed refresh, drift, and worker-bootstrap rules are owned by
[orchestration.md](references/orchestration.md).

Prepare Run uses the Feature semantic contract and every available verified
local Macro Task projection as planning context, then translates each Feature into a
transient set of technical implementation units. A unit has an observable
technical outcome, repository scope, allowed-path proposal, validation
intent, dependencies that are real implementation prerequisites, and evidence
linking it back to one or more Feature criteria and, when applicable, available
local Macro Tasks. Derive stable `T-AC-NN` criteria that specialize the F-AC
evidence expected from those units.
Feature-level `blocked_by` relations do not become technical execution-unit
edges, but repository identity controls their delivery projection. Every
same-repository edge is mandatory stack intent and every cross-repository edge
is scheduling-only. Macro `blocked_by` relations are advisory and
same-parent-only; the orchestrator may combine, reorder, or internalize them
while preserving every available Macro Task outcome and every Feature
criterion. These units
are not copied into the hosted plan by default and are not a reason to rerun
Feature.

Schedule independent Features across safe waves, respecting Feature-level
`blocked_by` context. A same-repository dependent becomes worker-runnable when
one immediate parent has verified `candidate-published` evidence and its exact
branch and full SHA form the child's frozen integration base; parent delivery
readiness is not a development gate. If several same-repository parents exist,
select one immediate parent only when its candidate contains every other
required prerequisite HEAD, otherwise block for explicit plan reconciliation.
Within one Feature, the Feature Worker owns the derived units in deterministic
prerequisite order and does not create child Feature Workers or planner tasks. It may use
bounded support assignments when the optional delegation capability and
usable worker capacity are observed; otherwise it performs the work itself.
Path overlap, capacity, preferred order, and cross-repository dependencies do
not create a PR stack. Same-repository Feature-level `blocked_by` is the only
Plan Set relation that creates mandatory stack intent; Implement still derives
technical execution edges independently and must verify the exact parent
ancestry before child publication.

When implementation reveals a semantic contradiction that cannot be resolved
without changing outcome, scope, F-AC, or Feature dependencies, enter
plan-question and present the bounded conflict to the user. Preserve the
worker, worktree, branch, and useful evidence when safe. Do not escalate
missing Macro decomposition, ordinary technical ambiguity, or the need for
more specific technical acceptance criteria. If the user explicitly decides
that the published semantic contract must change, stop the affected assignment
and report a new se:feature request as the recovery action; do not create that
planner task automatically and do not let independent Features wait.

## Feature Worker and review boundary

Each Feature Worker owns one authoritative Feature member, its observed Macro
projection state and available local Task context, one verified implementation
worktree, one branch, and one
eventual PR. It owns technical design, code, tests, validation, candidate
evidence, exact-HEAD native review, and fixes. It binds every Feature
acceptance criterion and every derived T-AC to evidence on the same candidate
SHA, and maps available local Macro Task outcomes as contextual coverage. It
never owns a sibling Feature or its Tasks.
Macro Tasks are not worker or PR boundaries. Derived T-AC and execution-unit
criteria are assignment-scoped worker evidence, not durable Feature or Macro
Task requirements, and may only specialize the published F-AC contract.

Any HEAD change invalidates prior acceptance, validation, and review evidence.
The worker repeats the required checks and review at the new exact HEAD. The
orchestrator receives evidence and coordinates delivery; it never edits,
rebases, or judges worker code.

After the orchestrator verifies `delivery-pending @ candidate-published`, the
Worker returns a bounded exact-HEAD handoff and becomes inactive but resumable.
This is not assignment completion: the orchestrator releases the transient
active path claim and monitors the PR centrally. Before returning the Worker
for a finding, evidence mismatch, or parent drift, the orchestrator reacquires
its path envelope and sends only the exact actionable evidence. A Worker never
polls its own PR while inactive.

### Optional Feature Worker support

The Feature Worker remains the sole owner of the Feature member, worktree,
integration branch, candidate commit, acceptance matrix, native review, and
eventual PR. When delegation is available and useful, it may dispatch bounded
support assignments with one of these responsibilities:

- `code-analyst`: read-only repository, impact, and dependency analysis;
- `execution-assistant`: implementation of one explicitly bounded execution
  unit in an exclusive path envelope or isolated helper context;
- `validation-assistant`: focused tests, checks, and validation evidence;
- `critic-reviewer`: independent challenge of design, risks, regressions, and
  current-candidate evidence.

Every support assignment receives the current Feature ID, Plan Set revision,
local Macro Task context, execution-unit scope, path envelope, and validation
intent. It returns bounded
evidence or a scoped change proposal to the Feature Worker. Support
assignments never edit or publish the Feature Plan, never access the SQLite
ledger, never publish or mutate GitHub, never create Feature Workers or
planner tasks, and never become the source of final delivery evidence. The
parent integrates any useful change, reruns the complete validation and review
cycle, and owns the final candidate HEAD.

Never run concurrent writes against overlapping worktree paths. A helper may
edit only an exclusive declared envelope or an isolated helper context, and
the parent must reconcile its result before continuing. A delegated helper is
reported as started only after its task and result have been independently
observed. `delegated-support`, `serial-fallback`, `unavailable`, and `unknown`
are distinct runtime modes; configured delegation or capacity is not proof
that a helper ran.

## Delivery topology

Keep implementation waves separate from PR delivery topology. Run independent
Features concurrently when repositories, paths, dependencies, and live
capacity permit. Every same-repository Feature-level `blocked_by` relation is
mandatory stack intent independently of otherwise serial or parallel
execution. A stacked child requires one immediate parent with verified
`candidate-published` evidence and the parent branch and exact SHA as its
integration base; it does not wait for parent delivery readiness to begin
development. Cross-repository relations, unrelated work, and capacity-only
ordering remain standalone.

Before bootstrapping a stacked child, reread the parent PR, branch, full HEAD,
candidate-published checkpoint, and stack capability. Parent drift invalidates
descendant base, review, CI, and readiness evidence. The owning workers
rebase and revalidate their own branches bottom to top; the orchestrator
never performs a stack-wide rebase.

## Ledger boundary

The SQLite WAL ledger remains a minimal checkpoint and recovery index, not a
second workflow engine. It stores exclusive Feature claims, assignment
identity, durable checkpoints, and idempotent side-effect reservations. It
does not store plans, prompts, messages, worker logs, internal execution-unit
details, findings, or routine technical state.

The orchestrator is the only ledger reader and writer. Feature Workers return
bounded evidence through the task handoff and never access SQLite. On resume,
reread the authoritative plan, current repository/base/HEAD, worker identity,
and hosted delivery state before another side effect.

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
