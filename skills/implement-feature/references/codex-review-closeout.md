# Mandatory Codex Review And Closeout

## Ownership

The visible Feature Spec task owns review request, polling, feedback fixes, CI,
tracker-closeout preparation, ready-for-review transition, and terminal
merge-ready proof. The root monitors and
reconciles; it never takes this work back as a fallback.

## Current-Revision Review

Request exactly one Codex review for the current revision tuple: PR, head SHA,
base ref, and merge-base SHA. Record the tuple, request evidence, provider
state, findings, disposition, and completion time. Reuse a result only when the
entire tuple matches and every finding is dispositioned. Review is mandatory
and has no skip value.

Actionable findings return to fix, focused validation, `$autoreview`, push, and
a new current-revision review. Head, base-ref, merge-base, or material diff
changes invalidate earlier review and CI evidence. Resolve a review thread only
after its fix and proof exist.

Head, base, merge-base, or repository-rule changes also invalidate mergeability
evidence. Recheck the exact tuple and require lifecycle `OPEN`, conflict-free
GitHub mergeability, required base freshness, approvals, and merge-queue
eligibility before terminal `merge-ready`; unknown or pending state blocks.
Never enqueue or merge.

When a final issue carries a nonempty accepted knowledge delta, a later review
fix or other material code, evidence, target, or documentation change also
invalidates captured domain-closeout evidence whenever it can affect delta
support or its destinations. Rerun the exact Project Memory closeout and persist
fresh delta, destination, docs-diff, and implementation-revision evidence before
terminal `merge-ready`.

## Request Registry And Idempotency

The ledger's Codex Review Wait Registry is the sole request and timing owner.
Keep exactly one row keyed by
`<owner>/<repo>#<number>@<head-sha>@<base-ref>@<merge-base-sha>`. Store request
evidence, provider state, observation fingerprint, result and disposition,
`wait_started_at`, `wait_deadline`, `due_at`, and poll owner.

Before review request, resume, or terminal merge-ready acceptance, recompute the
full revision tuple
and run the canonical GitStack review check. Reuse a current clean/findings
result; wait on a current acknowledged request; create a request only for a
proven not-requested or stale tuple. Persist the row before polling so recovery
cannot duplicate the mutation. API, authentication, or configuration
uncertainty never authorizes another request.

At the GitStack boundary, translate the fixed assignment internally: pass the
exact PR and canonical `review_operation`; add GitStack-owned
`mutation_mode=apply` only for an authorized request, comment, reply, or
resolution. Do not pass App permission, Feature Spec, phase, or fixed-action
fields to GitStack, and never expose the translation as a user option.

## Fixed Wait Deadline

Use one 30-minute total active-wait deadline per exact revision tuple. The first
waiter atomically records `wait_started_at` and `wait_deadline`; every concurrent
or resumed consumer reuses that row and waits only for the remaining time. Use
one bounded GitStack waiter with 10-second initial polling and a 30-second
maximum interval. Never wrap it in another polling loop.

At the deadline, recompute the tuple and check once. Record a terminal result if
available. If the same request remains pollable and pending, persist one
`monitoring-required` handoff with a single `due_at`, stop active polling, and
release the claim only after that durable handoff is recorded. Do not extend the
deadline, create another wait tier, submit another request, or rewrite unchanged
timestamps. A later explicit resume reacquires ownership, revalidates the tuple,
and checks the same registry row before any mutation.

An unpollable provider or access failure is a blocker, not a review skip.

## Tracker Closeout

Put every generated implementation issue's closing keyword in its owning
repository PR and record it as `armed`. When an issue is hosted in another
repository, use the fully qualified `owner/repository#number` form. After one
implementation-eligible Feature Spec's whole-Spec gates pass, put that Spec's
closing keyword in its designated default-branch closeout PR and record it as
`armed`. In multi-repository work, the final integration partial's
default-branch PR additionally arms any accepted hosted parent/global Feature
Spec with a fully qualified ref only after every partial gate passes.
Non-default-base PRs link to the appropriate closeout vehicle and must not close
a Spec prematurely. Every terminal App PR must already target its repository's
discovered default branch; verify that base during preflight and again for the
current revision. A different base blocks terminal closeout because its closing
keywords cannot take effect.

For a local Markdown source, first finish substantive acceptance, integration
proof, and any knowledge closeout. Then move completed issues from their exact
scoped active paths to their exact scoped `done/` destinations on the delivery
branch, commit and push those moves, rerun final validation and `$autoreview`,
convert draft PRs to ready-for-review, then obtain current-revision review and
CI at the resulting head before terminal merge-ready state.
Report local closeout as prepared because the completion paths reach the default
branch only after the later merge. The orchestrator reports the external merge
handoff and stops. A separate GitHub workflow owns merge and verifies hosted or
local tracker closure.
