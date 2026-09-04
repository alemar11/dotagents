---
name: implement
description: "Implement or resume published SE Features through a small transient workflow graph, visible orchestrator, and reusable workers. Use for lightweight standalone or stacked PR delivery; never merge, deploy, or release without separate authorization."
---

# Implement

## Scope and authority

Use `se:implement` only when the caller explicitly asks to implement or
resume published SE parent Features. The selected set is exactly the supplied
Feature issue references. Read sibling and dependency data for context and
consistency, but never add a sibling merely because it is discoverable.

An explicit invocation authorizes the visible Codex tasks, isolated worktrees,
branches, commits, pushes, and pull requests needed to deliver the selected
Features. It does not authorize merge, deploy, release, issue closure,
destructive recovery, or unrelated cleanup.

The durable outputs are Git branches, commits, pull requests, and provider
state. The small local registry coordinates repository ownership only. The
workflow graph below governs execution, but its current node is reconstructed
from live evidence rather than persisted. The registry must never become the
source of truth for workflow position, Feature, worker, branch, commit,
pull-request, review, or CI state.

## Runtime topology

Create or reuse one visible graph orchestrator for the complete immutable set
of selected repositories. The orchestrator follows this skill's workflow graph
and alone decides concurrency. Load
[orchestration.md](references/orchestration.md) before choosing task placement,
creating or reusing a worker, accepting a worker target, scheduling a Feature,
or deriving branch and pull-request topology. That reference is the canonical
owner of these decisions and every workflow transition condition.
Read [candidate-review.md](references/candidate-review.md) before entering
`review-candidate`; it owns reviewer independence, target identity, profile,
findings, repair convergence, and recovery.
Read [repository-claims.md](references/repository-claims.md) before deciding
whether the invoking visible task itself can be bound as that orchestrator or
a separate orchestrator must be created, and before acquiring, binding,
inspecting, or releasing claims.

## Read routing

Before every handoff to a G-owned workflow, the role making that handoff must
run the shared
[G dependency preflight](../../references/codex-dependency-preflight.md).
Immediately before every hosted write, that role must apply the shared
[hosted-content safety contract](../../references/hosted-content-safety.md).
Project both obligations into every worker handoff that permits G-owned work.

Read the shared [workflow-graph contract](../../references/workflow-graph.md)
before using the graph registry. Read [states.md](references/states.md) before
interpreting workflow nodes or repository claims.

## Workflow graph

The workflow node table in this section is the structural source of truth.
Follow its edges; do not replace it with an improvised numbered procedure.
Mermaid is only its maintained projection. Multiple ready assignments may
occupy `deliver-feature` or `review-candidate` concurrently when `schedule`
chooses fan-out, but every review result re-enters `reconcile` before another
scheduling decision.

| node_id | kind | purpose | entry_conditions | inputs | outputs | transitions | stop_if | side_effects | terminal_states |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| intake | action | Resolve the exact selected Feature set, body-backed dependency graph, repository identities, and intended visible home. | Explicit implementation or resume request with exact parent Feature issue references. | Caller request and published Feature contracts. | Validated selection, dependency graph, immutable repository set, and visible home. | claim-repositories, deferred, blocked | The selection is ambiguous, cyclic, semantically incomplete, or requires a material user choice. | read, transient | none |
| claim-repositories | action | Acquire or reuse the complete repository claim and establish one correlated visible orchestrator. | Intake produced a valid immutable repository set and visible home. | Repository keys, home key, selected Features, and optional existing claim. | Independently bound orchestrator identity and fenced repository ownership. | claim-repositories, reconcile, blocked | Claim ownership, provisional task effects, or orchestrator identity cannot be reconciled safely. | durable | none |
| reconcile | validation | Reconstruct current execution truth and resolve ambiguous effects once from authoritative owners. | A bound orchestrator exists, or a returning worker or material external change requires refresh. | Feature graph, Git/worktrees, pull requests, candidate and hosted review/CI, task history, and ownership claim. | Current delivery evidence, trustworthy worker lanes, and unresolved blockers or choices. | schedule, release-claims, complete, deferred, blocked | An effect remains ambiguous, required evidence is unavailable, or safe continuation needs user authority. | read, transient | none |
| schedule | decision | Compute the ready frontier and choose serial execution or bounded concurrent worker lanes. | Reconciled evidence shows unfinished selected Features. | Feature graph, delivery evidence, repository bases, and trustworthy lanes. | One or more flat Feature assignments, or a reason to reconcile, defer, or stop. | deliver-feature, reconcile, deferred, blocked | No responsible scheduling decision can be made from current evidence. | read, transient | none |
| deliver-feature | action | Verify or resume a repository worker; implement, validate, and locally commit one stable Feature candidate; after a clean candidate review, publish its standalone or stacked pull request and converge exact-HEAD hosted review and CI. | `schedule` selected a dependency-ready Feature and verified whether the lane requires implementation, candidate repair, candidate review preparation, or publication. | Feature contract, worker target, branch/base facts, current candidate-review evidence, allowed mutations, and G handoff obligations. | A locally committed candidate requiring independent review, or exact branch, base, HEAD, pull request, ready transition, validation, candidate review, hosted review, CI, and blocker evidence. | review-candidate, reconcile | The worker cannot establish a stable committed candidate, preserve the reviewed candidate through publication, or return trustworthy partial evidence. | durable, hosted | none |
| review-candidate | validation | Run a fresh independent read-only adversarial review of the complete locally committed Feature delta using the required reviewer profile. | `deliver-feature` produced a stable candidate at an exact local HEAD with required validation passing and no clean candidate review for that contract, base, and HEAD. | Immutable Feature-contract identity, repository instructions, verified base and candidate HEADs, complete delta, validation evidence, and remaining review-cycle budget. | A contract-base-and-HEAD-bound clean, findings, or indeterminate candidate-review result with reviewer-profile and immutable-snapshot evidence. | reconcile | Reviewer independence, isolated read-only execution, immutable target, required profile, trustworthy output, or remaining review-cycle budget cannot be established; return the evidence to `reconcile`. | read, transient | none |
| release-claims | action | Release the exact complete repository claim after an explicitly requested handoff or abandonment. | `reconcile` proved the orchestrator and all workers quiescent and release is authorized. | Bound claim, fencing token, and quiescence evidence. | Verified whole-group release. | complete, blocked | Any actor or ownership fact remains active, uncertain, or mismatched. | durable | none |
| complete | terminal | Return verified selected Feature outcomes, or confirm an explicitly requested ownership handoff or abandonment. | Every selected Feature has a current exact-HEAD pull request that is ready rather than draft, its authoritative Feature contract and current intended base match the immutable contract identity and full base SHA reviewed locally, it has a clean independent candidate review and terminal clean G-normalized hosted Codex review for that same HEAD, and it passes required validation and CI with no unresolved blocker, or is proved already incorporated into its integration base; alternatively, `release-claims` completed. | Final reconciled evidence. | Plain-language delivery or release report. | none | terminal | none | complete |
| deferred | terminal | Return the material user decision required for a contract-preserving continuation. | A semantic choice or missing authority cannot be resolved safely inside Implement. | Reconciled evidence and the smallest concrete question. | Deferred report retaining the bound claim. | none | terminal | none | deferred |
| blocked | terminal | Return the exact capability, identity, evidence, ownership, or reconciliation blocker. | No responsible graph edge remains. | Retained evidence and blocker. | Blocked report retaining the claim unless an authorized release already completed. | none | terminal | none | blocked |

~~~mermaid
flowchart TD
    intake --> claim-repositories
    intake --> deferred
    intake --> blocked
    claim-repositories --> claim-repositories
    claim-repositories --> reconcile
    claim-repositories --> blocked
    reconcile --> schedule
    reconcile --> release-claims
    reconcile --> complete
    reconcile --> deferred
    reconcile --> blocked
    schedule --> deliver-feature
    schedule --> reconcile
    schedule --> deferred
    schedule --> blocked
    deliver-feature --> review-candidate
    deliver-feature --> reconcile
    review-candidate --> reconcile
    release-claims --> complete
    release-claims --> blocked
~~~

Do not persist a queue, current node, checkpoint, worker assignment, operation
receipt, or retry record. On resume, enter at `intake`, establish the exact
claim at `claim-repositories`, then derive the current continuation at
`reconcile` from Feature issues, branches and commits, worktrees, pull requests,
and Codex task history. Reconcile an ambiguous task or provider effect once
from authoritative current state before attempting it again.

## Delivery boundaries

Route local Git, publication, hosted pull-request review, CI diagnosis, and
stack operations to their focused G owners. Verify the actual current branch,
base, and exact HEAD before each publication or update. If a parent changes,
rebase or restack its descendants and rerun the validation invalidated by that
change.

Before first publication and after every candidate-changing repair, require a
clean independent candidate review for the complete locally committed delta at
the current immutable Feature-contract identity, full base SHA, and full HEAD.
A clean result authorizes the same worker to continue publication only while
all three identities remain unchanged; findings return that worker to
implementation and validation. Candidate review is local, isolated, read-only,
and transient. It neither replaces nor weakens the hosted review requirement
below.

A fresh pull request created by G Send is an intermediate draft, not completed
delivery. Once its exact HEAD, body, base, and stack topology are stable, make
it ready through the focused G owner, independently read back that it is no
longer draft at the same full HEAD, retain the typed ready-transition evidence,
and use `$g:github-review-threads` to wait for the automatic initial Codex
review. Do not post an explicit review request for that ready-triggered cycle.

Only a terminal clean G-normalized review bound to the current full HEAD can
satisfy hosted review. `not-requested`, absent comments, zero review threads,
draft-only review, pending or timed-out observation, stale evidence, findings,
provider failure, or ambiguous correlation are non-terminal. After findings,
reuse the same trustworthy worker to repair and validate the candidate, locally
commit it, and pass the new full HEAD through `review-candidate -> reconcile`.
Only a clean unchanged result permits publishing it to the existing PR, issuing
one G-owned explicit re-review request, and waiting on its exact receipt.
Reconcile an interrupted transition, request, or wait from authoritative PR and
review evidence before retrying; never toggle ready state or duplicate a review
request to manufacture a fresh lineage.

Keep this lifecycle transient: do not add review fields, checkpoints, or
receipts to the repository-claims registry. If the caller explicitly requires
a PR to remain draft, preserve that constraint and return `deferred` with the
verified draft evidence instead of claiming `complete`. Never weaken required
validation or claim a current result from evidence bound to an older HEAD.

## Result

Report:

- each Feature's repository, branch, pull-request base, exact HEAD,
  pull-request URL, validation, candidate review, hosted review, and CI
  evidence;
- which worker lanes were created or reused;
- whether repository claims were retained or released;
- blockers and the smallest concrete next action.

Do not invent a persisted terminal status. Describe the observed result in
plain language and preserve the orchestrator for a legitimate resume.

## Skill Dependencies

This skill requires the installed `g@alemar11` workflows that own its selected
Git, GitHub, hosted pull-request review, CI, and stacked-pull-request
operations. It never installs, enables, refreshes, or substitutes that
dependency.
