# Implement Review And Delivery

This reference owns exact-HEAD worker-session review, PR publication, provider
review monitoring, and final exact-HEAD evidence.

## Candidate boundary

The implementation worker operates only in its application-managed worktree.
After validation and commit, freeze one candidate with exact repository, base
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

The implementation worker owns application semantics: code, tests, conflict
resolution, validation, and the decision that a candidate is ready for review.
It does not select an alternate Git or GitHub transport. Every Git transport
operation is routed through a G-owned workflow, and every hosted GitHub read or
write is routed through the G-owned workflow for that domain. The shared SE2
dependency preflight gates hosted access; local worktree edits and validation
do not require that hosted gate, but they are never a local-only Implement
result. Every run must continue through the authoritative hosted source and
verified PR-delivery path.

| Operation | Semantic owner | Required authority and readback |
| --- | --- | --- |
| Worktree inspection, scoped staging, and candidate commit | G-owned local Git workflow; worker owns the content and validation evidence | Authorized repository and paths; read back branch, clean worktree, full candidate HEAD, and staged scope. |
| Implementation-branch creation, checkout, or scoped rebase after parent drift | G-owned branch transport; worker owns conflict resolution and revalidation | Exact repository, source/base HEAD, target branch, resulting full HEAD, and a fresh validation record. |
| One candidate branch push and draft PR create/update | G-owned single-PR publication workflow | Explicit mutation authority for the exact repository and branch; read back repository, base, branch, full PR HEAD, URL, body, issue linkage, and draft state. |
| Link one child PR to one immediate parent PR | G-owned pairwise stack-link workflow | Explicit stack authority and one parent/current pair; read back both identities, child base, stack order, and link receipt. |
| Ready transition, issue linkage, labels, or type metadata | G-owned hosted publication or issue workflow for the exact operation | Explicit authority per mutation; read back the resulting state and bind it to the current full PR HEAD or issue identity. |
| CI, review, mergeability, and review-thread observation | G-owned hosted read/review workflows | Reconcile against the current full PR HEAD; pending, stale, ambiguous, or draft-only evidence is non-terminal. |
| Merge, deploy, release, or post-merge closure | No Implement owner; outside this skill | Never perform these operations as part of Implement completion. |

The worker may decide that evidence is insufficient and return to
implementation, but it may not bypass the owner boundary. A successful
publication and an unverified relation are separate effects and must be
reconciled independently.

## Native review loop

Before review, independently verify worker/worktree identity, candidate
cleanliness, base and prerequisite ancestry, and exact full SHA. The worker
runs the available native code-review capability in the same session against
the declared base using its resolved Sol reasoning level. The required outcome
is an independently reported exact-HEAD finding set or clean result; the skill
does not encode an application operation or interface.

Bind every finding and clean result to the exact candidate SHA. The worker
decides whether a finding is actionable, owns every fix, reruns validation, and
creates a new candidate. Any new HEAD invalidates the previous review evidence;
run a new review cycle in the same worker session against the new exact SHA.

## PR publication

Publish only after native review is clean and GitHub mutation is explicitly
authorized. Use the G-owned single-PR publication workflow to push the
committed candidate and create or reuse a draft PR. Independently read back
repository, base, branch, full PR HEAD, URL, body, issue linkage, and draft
state. The PR HEAD must equal the reviewed candidate HEAD.

For a stacked candidate, supply the verified parent head branch as the explicit
PR base. Require the G-owned workflow to identify exactly one open parent PR in
the same repository, publish only the current worker branch, and use the
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
parent HEAD returns the same child worker to implementation; an unreconciled
link blocks only that assignment while independent work continues.

## Hosted review monitoring

Monitor the ready-triggered provider review, CI, mergeability, and review
threads for the current full PR HEAD. Pending, timed-out, stale, ambiguous, or
draft-only review evidence is not terminal.

For a stacked child, also monitor the immediate parent PR and base relationship.
Any parent HEAD or readiness change invalidates the child's ancestry, review,
CI, and readiness evidence even when the child head itself did not move. Wait
for the parent to pass final verification, then require the child worker to
rebase onto the new parent HEAD and repeat its complete candidate cycle.

If hosted review produces an actionable finding, return evidence to the same
implementation worker. The worker fixes and validates; the G-owned local Git
workflow creates the new candidate, and the G-owned publication workflow
publishes it. Then repeat native review in the same worker session and request a
new hosted review bound to that exact SHA. Never force-push, merge, enqueue,
deploy, release, or perform post-merge closure.

## Final verification

The orchestrator performs read-only final verification. Require:

- exact Feature and Task refs and current accepted contract generation;
- implementation worker task/project/worktree identity;
- clean implementation worktree and exact current HEAD;
- current-head validation and native review evidence;
- PR publication readback and exact PR HEAD equality;
- `standalone` default-base evidence, or stacked parent identity, unchanged
  parent HEAD, exact child base, stack order, and verified link receipt;
- ready-transition and current-head hosted review evidence;
- required CI, mergeability, and zero unresolved actionable review threads.

Return repairable evidence mismatches to the worker without diagnosis. The
worker owns repair and replacement evidence. Final verification never edits
code, reruns review, mutates issues, or merges.

Report a standalone PR as `standalone-ready`. Report a child as `stack-ready`
only when every lower parent in the selected chain is current and
delivery-ready, while recognizing that the child is not independently
mergeable ahead of those parents.
