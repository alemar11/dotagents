# Implement Delivery Monitoring

This reference owns orchestrator-only monitoring after the verified
`candidate-published` handoff: ready transition, hosted review and re-review,
current-head CI, provider diagnostics, repair resumption, stack drift, and final
exact-HEAD verification. Publication and stack-link readback remain in
[review-delivery.md](review-delivery.md); Worker-owned repair and validation
remain in [worker-execution.md](worker-execution.md). Use
[states.md](states.md) for every workflow and persisted-state meaning.

Before every ready transition, review request, comment, reply, or other hosted
write, load and apply the shared
[hosted-content-safety.md](../../../references/hosted-content-safety.md)
contract to the exact final content. G owns transport and readback.

## Monitoring operation ownership

| Operation | Semantic owner | Required authority and readback |
| --- | --- | --- |
| Ready transition or issue linkage | G-owned hosted publication or issue workflow for the exact operation | Implicit authority from the explicit Implement request for each declared mutation; read back the resulting state and bind it to the current full PR HEAD or issue identity. |
| Branch protection, rulesets, mergeability policy, merge queue, and auto-merge | Outside Implement completion | Do not invoke or require these policy surfaces; any supplied observation is diagnostic only and cannot block completion. |
| Hosted Codex review and actionable review-thread observation | G-owned review workflow, centrally coordinated by the Implement orchestrator | Reconcile against the current full PR HEAD; pending, stale, ambiguous, or draft-only evidence is non-terminal. Feature Workers do not poll while inactive. |

## Hosted review monitoring

The orchestrator owns the monitoring loop for every delivery-pending PR. It
uses bounded G-owned observations and never asks an inactive Feature Worker to
poll provider state. A pending observation returns to scheduling so newly
unblocked Feature Workers and other PR observations can progress.

Retain one delivery lineage per PR, exact HEAD, and hosted-review request.
Monitoring is change-driven: a timeout, silence, or observation with the same
provider identity, state, and evidence fingerprint remains pending and does
not cause a duplicate request, status message, Worker resumption, overlapping
observation, or immediate no-work scheduling cycle. Prefer event-driven
observation; when only repeated observation is supported, lengthen its interval
after unchanged results, reset after material change, and fairly interleave
independent PR lineages. Coalesce facts observed together for the same PR and
HEAD.

After `candidate-published`, when local validation and the published body are
stable, mark the PR ready through the G-owned workflow and independently
observe the transition. Hosted CI and provider review may remain pending and
are reconciled by this monitoring loop.

The first hosted Codex review and every later re-review have different trigger
lineages. Keep them separate:

1. After the G-owned draft-to-ready transition, persist its exact typed ready
   receipt and invoke the G-owned ready-wait operation for the published full
   PR HEAD. This observes the automatic review configured for a PR opened for
   review and never posts an explicit review request for this initial cycle.
2. Accept only G-normalized current-head terminal evidence. A clean formal
   review, authenticated terminal comment, or clean provider reaction may be a
   clean outcome; actionable inline or terminal findings return the assignment
   to the same Feature Worker. Absence of comments, zero unresolved threads,
   zero CI checks, or a generic not-requested observation is not a clean result.
3. After findings, the same Worker applies the repair contract in
   [worker-execution.md](worker-execution.md) and returns a focused-validated
   candidate. The orchestrator reserves and authorizes the exact PR update; the
   Worker publishes that SHA under [review-delivery.md](review-delivery.md)
   without native review and returns typed receipt/readback. Only after
   reconciliation invoke the G-owned request operation with a new request key,
   retain its exact receipt, and wait against that same full SHA. Repeat this
   repair, publish, explicit-request, and wait sequence until the current full
   PR HEAD has a clean terminal result.

For each later PR update, freeze an identity-bound effect reservation from the
assignment, verified PR identity, prior published HEAD, and new candidate SHA.
For ready transitions and re-review requests, freeze the analogous PR/HEAD and
request lineage. These are deterministic delivery-lineage records, not new
ledger fields, operation enums, workflow states, or modes. On interruption,
reconstruct the expected effect from the retained assignment/PR/HEAD evidence
and reconcile authoritative provider state before any retry; an ambiguous or
already-applied effect never produces a duplicate update or request. Retain
receipts and readback in the orchestrator's delivery evidence, while only the
orchestrator performs any existing ledger mutation.

Invalidate evidence selectively during this loop:

- a code HEAD change invalidates prior code-bound acceptance, validation,
  hosted-review, CI, and publication-head evidence, but preserves Feature
  selection, Worker and PR identity, resolved side-effect receipts, and
  unaffected stack identity;
- a PR-body-only update invalidates only body and closure-intent readback;
- a base, parent HEAD, ancestry, or stack-link change invalidates the affected
  integration and descendant evidence, even when a child code HEAD is
  unchanged;
- a disconnected or interrupted hosted monitor preserves the same request and
  review lineage and resumes observation without posting a duplicate request;
- an ambiguous external effect invalidates only that effect until its receipt
  and authoritative readback are reconciled.

Focused validation accelerates intermediate hosted repair candidates; it does
not replace complete candidate validation. Before `final-verify`, require the
Feature Worker to run the complete Feature validation on the exact published
HEAD. If that validation requires a code change, publish the new SHA and return
it to hosted review; a clean hosted result for the older SHA cannot carry
forward.
When complete validation passes without changing the published HEAD,
`implement-validate` may proceed directly to `final-verify`; do not republish,
request another review, or invalidate the clean hosted result for that same SHA.

Monitor current-head CI and actionable review threads alongside that
provider-review cycle. CI is terminal only when every applicable check has
passed, or the repository reports that no checks are configured; pending,
failing, stale, ambiguous, or incomplete CI evidence is not terminal. Bind
review and CI observations to the exact published full HEAD. One bounded wait
may return a pending state at its caller-owned deadline; when continued
monitoring remains authorized, the orchestrator returns to schedule only when
runnable work or materially new evidence exists. Otherwise it retains the
existing lineage and resumes observation later without posting a duplicate
request, resetting the lineage, or producing a status-only control message.

When hosted review and CI are clean but complete current-head validation is
missing or stale, resume the same Feature Worker through `implement-validate`
only for that validation. Reacquire its path envelope even when no write is
expected. An unchanged, fully validated HEAD proceeds directly to
`final-verify`; any resulting code change follows the published-candidate path
and requires hosted re-review.

For a stacked child, also monitor the immediate parent PR and base relationship.
A parent HEAD, base, or link change invalidates the child's ancestry, hosted
review, CI, and readiness evidence even when the child head itself did not move;
return the same child Feature Worker for rebase, focused integration validation,
publication, and hosted re-review without native review. A
parent readiness change without topology or HEAD drift affects bottom-to-top
finalization only and does not invalidate child implementation evidence.

If hosted review produces an actionable finding, preserve its exact provider,
PR, head, artifact, and observation fingerprint. Reacquire the Worker's path
envelope, then return that evidence to the same Feature Worker. Never
force-push, merge, enqueue, deploy, release, or perform post-merge closure.

## Externally supplied diagnostics

Implement never invokes `$g:github-delivery-status`, requests provider-policy
classification, or waits for a branch-protection, ruleset, mergeability-policy,
merge-queue, or auto-merge certificate. If an outer coordinator supplies such
an observation, preserve it as report-only context; it cannot enter a workflow
transition, assignment checkpoint, or completion decision. A missing,
incomplete, negative, or plan-limited policy surface must never block an
otherwise verified PR, CI, review, and stack outcome. Implement must still
never enable, disable, enqueue, dequeue, bypass, or merge anything. If another actor merges
or closes the PR during the run, observe the changed lifecycle, stop normal
delivery reconciliation, and report the external event without post-merge
work.

## Final verification

The orchestrator performs read-only final verification. The following list is
closed: provider readiness, delivery-status output, branch protection,
rulesets, mergeability policy, merge queue, auto-merge, and provider-policy
certificates are not additional requirements and are rejected as
`delivery-ready @ final-verify` evidence. Require:

- exact caller-supplied parent issue ref, Feature Plan Set ref/revision,
  selected Feature ID, repository, and complete hosted sibling readback;
- exact Feature-level registry/dependency readback plus Macro projection state
  (`complete`, `partial`, or `absent`), every verified existing local child,
  and every quarantined projection defect;
- Feature-level scheduling evidence and the repository-sensitive projection
  that justifies standalone or stacked delivery;
- exact current F-AC-NN set with no missing, duplicate, malformed, or
  ambiguous IDs;
- authoritative hosted plan coverage and monotonic Feature acceptance
  high-water marks consistent with every current criterion ID;
- Feature Worker task/repository/worktree identity;
- clean implementation worktree and exact current HEAD;
- a complete acceptance matrix for every F-AC-NN whose evidence is bound to
  the same exact current candidate HEAD;
- deterministic T-AC-NN criteria, their F-AC mapping, and complete exact-HEAD
  evidence without replacing or weakening any F-AC;
- available Macro Task contextual coverage evidence bound to the same exact
  current candidate HEAD;
- complete current-head validation evidence plus clean current-head hosted
  review evidence; retain native review as the historical first-publication
  gate, not as current-head evidence after a repair push;
- current-head CI evidence showing every applicable check passed or
  authoritatively showing that no checks are configured;
- evidence that final verification started from
  `delivery-pending @ candidate-published`, plus the exact Worker handoff and
  any later resumption lineage;
- PR publication readback and exact PR HEAD equality;
- minimal durable SE-owned PR-body readback with no routine execution counts or
  internal delivery evidence;
- the exact Feature-local source-derived `closing_issue_refs` set containing
  this parent Feature and every verified existing associated local Macro Task, with the same
  closure intent read back from the PR body and no sibling or unrequested
  source closure; GitHub `closingIssuesReferences`, when available, is
  diagnostic only and cannot block final verification;
- standalone selected-base evidence including refreshed branch and exact base
  SHA, or stacked parent identity, unchanged parent HEAD, exact child base,
  stack order, and verified link receipt;
- ready-transition receipt plus a clean current-head automatic-review
  certificate for an unchanged initial HEAD, or the latest explicit-request
  receipt plus its clean current-head review result after one or more fix
  pushes;
- zero unresolved actionable review threads.

When every requirement passes for the same exact HEAD, persist
`delivery-ready @ final-verify`. Until then, preserve
`delivery-pending @ candidate-published` unless a repair, rebase, plan question,
or blocker changes assignment ownership.

Aggregate every current F-AC-NN and derived T-AC-NN through the Feature Worker
evidence map and retain the exact candidate SHA. Every F-AC must have direct
evidence or one or more mapped T-AC criteria, and every T-AC must have
exact-HEAD proof. An uncovered, unverified, stale, or ambiguous criterion
prevents delivery readiness. Map every available local Macro Task outcome as
context, but a `partial` or `absent` projection and a planning-only local Macro
Task status of `blocked` do not block delivery once the final candidate covers
the Feature semantic contract. A Feature-level `blocked_by`
relation controls stack intent or cross-repository scheduling, but it does not
add a sibling to this PR's closing set. This acceptance verification is
evidence-only and never edits the Feature Plan Set or any registry.

On recovery, use the assignment's stored worker_task_id and candidate_sha to
reread the Feature Worker's final acceptance matrix. Accept it only when its
Feature Plan Set ref, Feature ID, observed Macro projection state, complete
F-AC-NN set, T-AC mapping, set/plan revision, and candidate SHA exactly match
current authoritative state. Feature membership or semantic-contract drift,
an unreported Macro projection change, or worker-report invisibility
invalidates the matrix.

Return repairable evidence mismatches to the Feature Worker without diagnosis.
The Feature Worker owns repair and replacement evidence. Final verification
never edits code, reruns review, mutates issues, or merges.

Report a standalone PR as standalone-ready with its exact PR, CI, review, and
stack evidence. Report a child as stack-ready only when every lower parent in
the selected chain is current and the stack topology is verified, while
recognizing that the child is not independently mergeable ahead of those
parents.
