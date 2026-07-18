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
and provider/result/disposition evidence, observation fingerprint,
`wait_started_at`, `wait_deadline`, `wait_invoked_at`, `provider_timeout`,
`due_at`, and poll owner.

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

The registry owns one 30-minute total active-wait deadline per tuple. The worker
reports tuple/request evidence; the root atomically records
`wait_started_at`/`wait_deadline` and returns `revision_key`/timestamps.
At launch, the worker sets `wait_invoked_at=now`, computes
`provider_timeout=floor(wait_deadline-now)`, and starts GitStack in the same
local step with no root round-trip. If nonpositive, check once. Report actual
invocation/timeout afterward for root persistence.

Use one GitStack waiter for it:
`--timeout <provider_timeout>s --interval 10s --max-interval 30s`. Never use a
provider default/example, hardcode `15m`, segment, or wrap it. Interrupted
recovery recomputes from the unchanged deadline; it never reuses a timeout.

At deadline, check the tuple once. If pending, persist one `monitoring-required`
handoff and `due_at`, stop, then release. Do not extend, re-request, or rewrite
timestamps. Resume checks the row before mutation. Unpollable access blocks; it
is not a review skip.

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
