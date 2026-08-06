---
name: implement
description: "Implement one or more authoritative GitHub Feature Plans by interpreting their textual outcomes into internal execution units, creating one isolated Feature Worker and one pull request per plan member, and returning verified exact-HEAD delivery; use only for explicit implementation or resume requests."
---

# Implement Feature Plans

## Input and output invariant

Use this skill only for an explicit request to implement or resume one or more
published SE2 Feature Plans from GitHub. Every selected plan must resolve to
one authoritative Feature issue or linked repository-owned Feature Plan
member with:

- repository identity and complete hosted readback;
- an observable outcome, scope, and non-goals;
- stable Feature acceptance criteria using F-AC-NN identities;
- monotonic Feature acceptance high-water evidence;
- resolved material questions, explicit assumptions, risks, and validation
  intent;
- a complete textual handoff that is ready for technical interpretation;
- publication and readiness evidence.

An authoritative hosted Task issue set, Task dependency graph, T-AC identifiers,
or automatic plan-repair result is not required input. Implement derives
internal execution units, implementation dependencies, safe path envelopes,
and runtime waves from the plan during Prepare Run. Those units belong to the
Implement control plane and are not silently sent back to Feature for ordinary
technical clarification.

Do not start from an isolated Task, local draft, Idea, unbounded request, or
preview-only plan. If the plan has a product-level contradiction or an
unresolved material question, pause the affected assignment for one explicit
user decision and report the exact question. Do not create a hidden planner
task or automatically invoke se2:feature.

The expected terminal output is one verified pull-request delivery topology
with exactly one PR output per implementation-eligible selected plan member.
Return a complete mapping from each plan member and its derived execution
units to its repository, Feature branch, exact HEAD, PR reference, and
standalone or stacked relationship. Bind every Feature acceptance criterion
to evidence on the same final candidate HEAD. Any execution-unit acceptance
identities are Implement-owned evidence and never rewrite the hosted plan.

Complete means every implementation-eligible plan member has a verified
standalone-ready or stack-ready PR output backed by a current
$g:github-delivery-status disposition of `ready` or
`ready-with-manual-action`,
all required Feature criteria are verified against that exact HEAD, and every
authorized closing reference is read back. A plan member with no exclusive
implementation delta must not receive an empty commit, empty PR, cosmetic
change, or artificial proof; report the zero-delta product question to the
user and stop that assignment.

This skill never merges, deploys, releases, or performs post-merge closure.
GitHub interaction is mandatory end to end. Local worktrees and local Git
transport are execution surfaces inside the implementation flow, never an
alternative terminal result.

## Shared contracts and dependencies

Read the shared workflow-graph contract before using this registry. The
registry is the structural source of truth and Mermaid is its projection.

Before the mandatory first GitHub Feature Plan, issue, PR, review, label, or
relation read or write, load the shared G dependency preflight. All GitHub
transport, hosted mutation safety, publication, and read-after-write
verification belong to G-owned workflows. The explicit Implement request
implicitly authorizes only the exact selected plan and delivery writes.

Require $g:github-delivery-status for exact-HEAD provider readiness. Provider
automation facts are not blockers by themselves; auto-merge, bypass, and queue
observations never authorize Implement to merge or change hosted policy.
Implement never merges, bypasses protections, enables or disables auto-merge, or
enqueues or dequeues a PR.

Before every hosted write, load the shared
[hosted-content-safety.md](../../references/hosted-content-safety.md) contract.
Implement owns the final portable projection; G owns transport and readback.

Before creating, resuming, or monitoring application tasks, load the
Implement task profile, shared task preflight, and shared task handoff. The
orchestrator and every Feature Worker are required roles. Title
reconciliation is required before normal monitoring or update relay.

Load orchestration when interpreting plans, deriving execution units,
scheduling workers, resolving plan questions, or calculating delivery
topology. Load review-delivery at candidate review and publication. Load
run-state before preparing, resuming, checkpointing, or resetting the ledger.

## Transition-condition ownership

| Source nodes | Canonical condition owner |
| --- | --- |
| intake, source-preflight, runtime-preflight, prepare-run | This skill's input invariant and shared contracts |
| schedule, delivery-gate, worker-bootstrap, plan-question, assignment-blocked, assignment-deferred, release-claims | orchestration.md |
| candidate, native-review, review-decision, publish-pr, stack-reconcile, ready-monitor, final-verify | review-delivery.md |
| deferred, complete, blocked | This skill's terminal definitions |

Each owner defines every declared outgoing condition and must not add an
unregistered edge. Run-state owns persistence and recovery evidence, not
workflow transitions.

## Workflow graph

| node_id | kind | entry condition | transitions | side effects | terminal state |
| --- | --- | --- | --- | --- | --- |
| intake | action | explicit implementation or resume request with one or more published Feature Plan refs | source-preflight, blocked | none | none |
| source-preflight | validation | complete Feature Plans are readable from the authoritative hosted source | runtime-preflight, blocked | hosted | none |
| runtime-preflight | validation | plans and target repositories are known | prepare-run, blocked | read | none |
| prepare-run | action | required roles, destinations, and plan interpretation are ready | schedule, blocked | durable | none |
| schedule | decision | run is ready for another plan-member wave or aggregate reconciliation | delivery-gate, release-claims, deferred, blocked | none | none |
| delivery-gate | decision | unfinished plan-member assignments are candidates for the next wave | worker-bootstrap, schedule, assignment-blocked, blocked | read | none |
| worker-bootstrap | action | one or more plan-member assignments are dependency-ready | implement-validate, assignment-blocked, blocked | durable | none |
| implement-validate | action | Feature Worker identity, worktree, derived execution units, and plan criteria are verified | candidate, plan-question, assignment-blocked, blocked | durable, hosted | none |
| plan-question | decision | a product-level plan contradiction or decision is explicit | schedule, assignment-deferred, blocked | none | none |
| candidate | validation | Feature Worker reports a committed candidate HEAD with plan criteria evidence | native-review, assignment-blocked, blocked | read, durable | none |
| native-review | action | Feature Worker session is pinned to the committed candidate HEAD | review-decision, assignment-blocked, blocked | read, durable | none |
| review-decision | decision | in-session review result is bound to the current candidate HEAD | implement-validate, publish-pr, assignment-blocked, blocked | durable | none |
| publish-pr | action | review is clean and publication scope is resolved | stack-reconcile, ready-monitor, assignment-blocked, blocked | hosted, durable | none |
| stack-reconcile | validation | a stacked PR was published or its parent/base/link/exact-HEAD evidence drifted | ready-monitor, implement-validate, assignment-blocked, blocked | read, durable | none |
| ready-monitor | action | PR identity and exact published HEAD are verified | implement-validate, stack-reconcile, final-verify, assignment-blocked, blocked | hosted, durable | none |
| final-verify | validation | current PR, topology, CI, review, checkout, HEAD, and acceptance evidence are available | schedule, stack-reconcile, assignment-blocked, blocked | read | none |
| assignment-blocked | action | one plan-member assignment cannot progress but independent work remains | schedule | durable | none |
| assignment-deferred | action | one plan-member assignment awaits bounded user authority | schedule | durable | none |
| release-claims | action | every assignment is delivery-ready or explicitly resolved and no assignment remains active | complete, blocked | durable | none |
| deferred | terminal | all remaining work awaits user authority | none | none | deferred |
| complete | terminal | every eligible plan member maps to one verified PR-ready output | none | none | complete |
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

The orchestrator control plane and Feature Worker lifecycle are one
hierarchical graph. They are not independent runs. A Feature Worker is an
application task plus its isolated worktree lifecycle; native-review is a
phase inside that lifecycle, not a second worker.

## Plan interpretation and orchestration

Source-preflight reads the authoritative Feature Plan body and verifies
repository identity, Feature criteria, publication readback, resolved
questions, and plan status. Runtime-preflight independently verifies every
selected repository, project, current checkout, required application roles,
and the G-owned workflows needed for the run.

Prepare Run translates each textual plan into a transient set of
implementation units. An implementation unit has an observable technical
outcome, repository scope, allowed-path proposal, validation intent,
dependencies that are real implementation prerequisites, and evidence linking
it back to one or more Feature criteria. These units are not copied into the
hosted plan by default and are not a reason to rerun Feature.

Schedule independent plan members across safe waves. Within one plan member,
the Feature Worker owns the derived units in deterministic prerequisite order
and never creates child workers. Path overlap, capacity, and preferred order
do not create a PR stack. A stack requires a true same-repository code
dependency and a verified parent exact HEAD.

When implementation reveals a missing product decision, enter plan-question
and present the bounded question to the user. Preserve the worker, worktree,
branch, and useful evidence when safe. If the user explicitly decides that the
published plan must change, stop the affected assignment and report a new
se2:feature request as the recovery action; do not create that planner task
automatically and do not let independent plan members wait.

## Feature Worker and review boundary

Each Feature Worker owns one authoritative plan member, one verified
implementation worktree, one branch, and one eventual PR. It owns technical
design, code, tests, validation, candidate evidence, exact-HEAD native
review, and fixes. It binds every Feature acceptance criterion to evidence on
the same candidate SHA. Internal execution-unit criteria may be used for
worker control, but they are not durable Feature requirements unless the user
explicitly publishes a revised plan.

Any HEAD change invalidates prior acceptance, validation, and review evidence.
The worker repeats the required checks and review at the new exact HEAD. The
orchestrator receives evidence and coordinates delivery; it never edits,
rebases, or judges worker code.

## Delivery topology

Keep implementation waves separate from PR delivery topology. Run independent
plan members concurrently when repositories, paths, dependencies, and live
capacity permit. Serialize real cross-member code dependencies and unsafe
overlap. A stacked child requires one same-repository immediate parent with a
green exact-HEAD candidate, accepted hosted readiness, clean review, and the
verified parent branch and SHA as its integration base. Parallel, unrelated,
cross-repository, and capacity-only ordering remains standalone.

Before bootstrapping a stacked child, reread the parent PR, branch, full HEAD,
review, delivery disposition, and stack capability. Parent drift invalidates
descendant base, review, CI, and readiness evidence. The owning workers
rebase and revalidate their own branches bottom to top; the orchestrator
never performs a stack-wide rebase.

## Ledger boundary

The SQLite WAL ledger remains a minimal checkpoint and recovery index, not a
second workflow engine. It stores exclusive plan-member claims, assignment
identity, durable checkpoints, and idempotent side-effect reservations. It
does not store plans, prompts, messages, worker logs, internal execution-unit
details, findings, or routine technical state.

The orchestrator is the only ledger reader and writer. Feature Workers return
bounded evidence through the task handoff and never access SQLite. On resume,
reread the authoritative plan, current repository/base/HEAD, worker identity,
and hosted delivery state before another side effect.

## Terminal report

Return one aggregate report with:

- every authoritative Feature Plan and repository member;
- every derived execution unit and its Feature-criterion mapping;
- every Feature Worker identity and verified destination;
- execution waves, path-overlap evidence, and deferred or blocked assignments;
- candidate, review, publication, delivery-status, stack, and exact-HEAD
  evidence;
- Feature acceptance evidence bound to each final candidate SHA;
- authorized closing references and their readback;
- aggregate outcome complete, deferred, or blocked.

Never claim completion while an eligible plan member lacks a verified PR,
current exact-HEAD evidence, or verified Feature acceptance coverage.

## Terminal meanings

- complete: every eligible plan member has verified PR delivery and the
  aggregate evidence is reconciled;
- deferred: all remaining work awaits explicit user authority;
- blocked: a required contract, capability, identity, authority, or
  reconciliation result is unavailable.
