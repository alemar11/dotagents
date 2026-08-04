# Implement Review And Delivery

This reference owns exact-HEAD Feature Worker-session review, PR publication, provider
review monitoring, and final exact-HEAD evidence.

## Candidate boundary

The Feature Worker operates only in its application-managed worktree. After it
implements every Task in the Feature, validates the complete Feature, and
commits, freeze one candidate with exact repository, base
branch, base SHA, head branch, and full head SHA. The worktree must be clean and
pinned to that candidate before review. Do not create a reviewer task or a
second review worktree.

For a dependency-bearing assignment, also freeze the exact prerequisite HEAD
vector and prove every member is an ancestor of the candidate. The candidate's
integration base and intended PR base must preserve that ancestry; a
prerequisite PR being ready is not sufficient proof.

Freeze one transient delivery record before review. A standalone candidate uses
the verified default branch. A stacked candidate names exactly one immediate
parent assignment and PR, the parent head branch, the exact parent candidate
SHA used as `base_sha`, and its bottom-to-top position. Do not infer a parent
from branch naming, issue order, display metadata, or operational serialization.

## Git and GitHub operation ownership

The Feature Worker owns application semantics: code, tests, conflict
resolution, validation, and the decision that a candidate is ready for review.
It does not select an alternate Git or GitHub transport. Every Git transport
operation is routed through a G-owned workflow, and every hosted GitHub read or
write is routed through the G-owned workflow for that domain. The shared SE2
dependency preflight gates hosted access; local worktree edits and validation
do not require that hosted gate, but they are never a local-only Implement
result. Every run must continue through the authoritative hosted source and
verified PR-delivery path.

Before every hosted write in this reference, load and apply the shared
[hosted-content-safety.md](../../../references/hosted-content-safety.md) to the
exact final title/body, comment, reply, review text, or review request. This
includes Feature Worker- and tool-originated content. A typed review request with only
its required portable marker and full SHA still passes the same final gate.

| Operation | Semantic owner | Required authority and readback |
| --- | --- | --- |
| Worktree inspection, scoped staging, and candidate commit | G-owned local Git workflow; Feature Worker owns the content and validation evidence | Authorized repository and paths; read back branch, clean worktree, full candidate HEAD, and staged scope. |
| Feature-branch creation, checkout, or scoped rebase after parent drift | G-owned branch transport; Feature Worker owns conflict resolution and revalidation | Exact repository, source/base HEAD, target branch, resulting full HEAD, and a fresh validation record. |
| One candidate branch push and draft PR create/update | G-owned single-PR publication workflow | Implicit authority from the explicit Implement request for the exact declared repository and branch and Task-only `closing_issue_refs`; read back repository, base, branch, full PR HEAD, URL, canonical closing lines, `closingIssuesReferences`, and draft state. |
| Link one child PR to one immediate parent PR | G-owned pairwise stack-link workflow | Implicit authority from the explicit Implement request for the one derived parent/current pair; read back both identities, child base, stack order, and link receipt. |
| Ready transition, issue linkage, labels, or type metadata | G-owned hosted publication or issue workflow for the exact operation | Implicit authority from the explicit Implement request for each declared mutation; read back the resulting state and bind it to the current full PR HEAD or issue identity. |
| Provider delivery readiness, CI, mergeability, rulesets, queue, and automation observation | `$g:github-delivery-status` | Require the current full PR HEAD and preserve the typed disposition, attribution, blockers, pending evidence, warnings, automation facts, and completeness. |
| Hosted Codex review and actionable review-thread observation | G-owned review workflow | Reconcile against the current full PR HEAD; pending, stale, ambiguous, or draft-only evidence is non-terminal. |
| Merge, deploy, release, or post-merge closure | No Implement owner; outside this skill | Never perform these operations as part of Implement completion. |

The Feature Worker may decide that evidence is insufficient and return to
implementation, but it may not bypass the owner boundary. A successful
publication and an unverified relation are separate effects and must be
reconciled independently.

## Native review loop

Before review, independently verify Feature Worker/worktree identity, candidate
cleanliness, base and prerequisite ancestry, and exact full SHA. The Feature Worker
runs the available native code-review capability in the same session against
the declared base using its resolved Sol reasoning level. The required outcome
is an independently reported exact-HEAD finding set or clean result; the skill
does not encode an application operation or interface.

Bind every finding and clean result to the exact candidate SHA. The Feature Worker
decides whether a finding is actionable, owns every fix, reruns validation, and
creates a new candidate. Any new HEAD invalidates the previous review evidence;
run a new review cycle in the same Feature Worker session against the new exact SHA.

## PR publication

Publish only after native review is clean and the exact publication scope is
resolved from the explicit Implement request.

Before constructing the PR body, derive one exact `closing_issue_refs` set from
the authoritative assignment and current candidate evidence:

- include every Task issue in this Feature; each Task's complete accepted scope
  and current `T-AC-NN` set must be satisfied by the same candidate;
- exclude every Feature and Idea issue even when all of its Tasks are complete;
  Implement delivery intentionally leaves the owning Feature open;
- reject a missing, extra, duplicate, partially satisfied, or repository-
  ambiguous Task ref instead of silently publishing without closure linkage;
- never treat a narrative `Task #N`, `Feature #N`, `Related to`, or
  `## References` entry as a substitute for a closing keyword.

Pass the verified nonempty set unchanged to the G-owned single-PR publication
workflow. G renders one canonical `Closes` line per Task under `## Issues` and
requires a default-branch PR for effective GitHub auto-closure. A stacked child
whose current base is not the default branch must retain its exact pending Task
closure set and stop on the G issue-linkage gate; never drop the refs merely to
publish or claim `stack-ready`.

Apply the shared hosted-content safety gate to the exact final PR title and body
immediately before publication. Use the G-owned single-PR publication workflow
to push the committed candidate and create or reuse a draft PR. Independently
read back repository, base, branch, full PR HEAD, URL, body, draft state, and
GitHub `closingIssuesReferences`. Require the read-back closing issue set to
equal `closing_issue_refs` exactly and require every canonical Task `Closes`
line exactly once. The PR HEAD must equal the reviewed candidate HEAD.

For a stacked candidate, supply the verified parent head branch as the explicit
PR base. Require the G-owned workflow to identify exactly one open parent PR in
the same repository, publish only the current Feature Worker branch, and use the
G-owned pairwise stack-link workflow after the child PR is read back. Preserve
the returned parent identity and `stack_link_receipt`. Do not use a stack-wide
publication, push, sync, rebase, or merge operation from normal publication,
and never install a missing stack dependency implicitly.

When validation, body, and required CI are stable, mark the PR ready through
the G-owned workflow and independently observe the transition. A draft review
is consultative and never satisfies the ready cycle.

## Stack reconciliation

After a stacked publication, the orchestrator independently verifies the exact
repository, parent and child PR identities, unchanged draft states, child base,
both full heads, immediate parent relationship, stack order, and link receipt.
The child base must equal the parent head branch, the live parent head must equal
the frozen `base_sha`, and the child head must equal the reviewed candidate.

Treat a confirmed child PR and an unverified stack link as separate effects.
Preserve successful publication evidence, record an ambiguous link as unknown,
and reconcile authoritative provider state before any repair. Never recreate or
repush the child merely because stack readback failed. A proven stale base or
parent HEAD returns the same child Feature Worker to implementation; an unreconciled
link blocks only that assignment while independent work continues.

## Hosted review monitoring

The first hosted Codex review and every later re-review have different trigger
lineages. Keep them separate:

1. After the G-owned draft-to-ready transition, persist its exact typed ready
   receipt and invoke the G-owned `ready-wait` operation for the published full
   PR HEAD. This observes the automatic review configured for a PR opened for
   review and never posts `@codex review`. Do not invoke `reviews request` for
   this initial cycle.
2. Accept only G-normalized current-head terminal evidence. A clean formal
   review, authenticated terminal comment, or clean provider reaction may be a
   clean outcome; actionable inline or terminal findings return the assignment
   to the same Feature Worker. Absence of comments, zero unresolved
   threads, zero CI checks, or a generic `not-requested` observation is not a
   clean result.
3. After findings, the Feature Worker fixes and validates, creates a new candidate,
   repeats native review, and publishes the new exact HEAD to the existing PR.
   Only then invoke the G-owned `request` operation with a new request key,
   persist its exact request receipt, and invoke `wait` against that same full
   SHA. Repeat this fix, publish, explicit-request, and wait cycle until the
   current full PR HEAD has a clean terminal result.

Monitor `$g:github-delivery-status` and actionable review threads alongside
that provider-review cycle. Bind every delivery-status observation to the exact
published full HEAD. Pending, timed-out, stale, ambiguous, draft-only,
missing-ready-receipt, request-correlation, or incomplete provider evidence is
not terminal. One bounded wait may return a pending state at its caller-owned
deadline; when continued monitoring remains authorized, the orchestrator
resumes through later bounded waits without posting a duplicate request or
resetting the existing lineage.

For a stacked child, also monitor the immediate parent PR and base relationship.
Any parent HEAD or readiness change invalidates the child's ancestry, review,
CI, and readiness evidence even when the child head itself did not move. Wait
for the parent to pass final verification, then require the child Feature Worker to
rebase onto the new parent HEAD and repeat its complete candidate cycle.

If hosted review produces an actionable finding, preserve its exact provider,
PR, head, artifact, and observation fingerprint when returning it to the same
Feature Worker. Never force-push, merge, enqueue, deploy, release, or
perform post-merge closure.

## Provider delivery status

After publication and again during final verification, invoke
`$g:github-delivery-status` with the exact repository, PR, and full candidate
HEAD. Accept only these current-head dispositions:

- `ready`: GitHub reports the PR technically mergeable with observed required
  provider gates satisfied; record `merge_boundary=none`;
- `ready-with-manual-action`: the same evidence is satisfied and G attributes
  the remaining provider boundary to a restricted manual branch update; record
  `merge_boundary=manual`.

Treat `pending`, `blocked`, `conflicting`, and `unknown`, a head mismatch, or
incomplete evidence as non-ready. Return repairable current-HEAD mismatches to
the same Feature Worker only when implementation evidence must change; otherwise keep
the orchestrator in bounded provider monitoring or report the provider blocker.
Do not reinterpret raw GitHub `mergeStateStatus` values inside Implement.

Repository auto-merge capability, an existing PR auto-merge request, and a
merge-queue entry remain reported automation facts. They neither block
delivery readiness nor grant authority. Implement must not enable, disable,
enqueue, dequeue, bypass, or merge, even when the current actor has permission.
If another actor merges or closes the PR during the run, observe the changed
lifecycle, stop normal delivery reconciliation, and report the external event
without post-merge work.

## Final verification

The orchestrator performs read-only final verification. Require:

- exact Feature and Task refs and current accepted contract generation;
- exact current `F-AC-NN` and `T-AC-NN` sets with no missing, duplicate,
  malformed, or ambiguous IDs;
- authoritative hosted Feature coverage and monotonic Feature/Task acceptance
  high-water marks consistent with every current criterion ID;
- Feature Worker task/project/worktree identity;
- clean implementation worktree and exact current HEAD;
- a complete acceptance matrix for every Task in the Feature whose every
  `T-AC-NN` is `verified` by evidence bound to the same exact current candidate
  HEAD;
- current-head validation and native review evidence;
- PR publication readback and exact PR HEAD equality;
- exact Task-only `closing_issue_refs`, one canonical `Closes` line per Task,
  and an equal GitHub `closingIssuesReferences` set, with no Feature or Idea
  issue present;
- `standalone` default-base evidence, or stacked parent identity, unchanged
  parent HEAD, exact child base, stack order, and verified link receipt;
- ready-transition receipt plus a clean current-head automatic-review
  certificate for an unchanged initial HEAD, or the latest explicit-request
  receipt plus its clean current-head review result after one or more fix
  pushes;
- a complete current-head `$g:github-delivery-status` certificate whose
  disposition is `ready` or `ready-with-manual-action`, plus zero unresolved
  actionable review threads.

After every required Task passes these checks, aggregate each `F-AC-NN`
through the authoritative Feature-to-Task-and-Task-criterion coverage map.
Require every owning `T-AC-NN` row to remain verified at the Feature candidate
SHA and retain that exact SHA. Any uncovered, unverified,
blocked, stale, or ambiguous criterion prevents delivery readiness. This
acceptance verification is evidence-only and never edits the Feature or Task
issue body.

On recovery, use the assignment's stored `worker_task_id` and `candidate_sha`
to reread the Feature Worker's final acceptance matrix. Accept it only when its
Feature ref, complete Task-ref set, contract generation, and candidate SHA
exactly match current authoritative state; task invisibility or drift
invalidates the matrix.

Return repairable evidence mismatches to the Feature Worker without diagnosis. The
Feature Worker owns repair and replacement evidence. Final verification never edits
code, reruns review, mutates issues, or merges.

Report a standalone PR as `standalone-ready` with its exact GitHub delivery
disposition and `merge_boundary`. Report a child as `stack-ready`
only when every lower parent in the selected chain is current and
delivery-ready, while recognizing that the child is not independently
mergeable ahead of those parents.
