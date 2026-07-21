# Review Mutation Authority

Load this reference before a GitStack review operation or its recovery.
Authority is unavailable before atomic baseline acceptance and root Goal
activation.

GitStack 6.0.0 owns the closed `request`, `wait`, `warning`, `reply`, `resolve`,
`reconcile-mutation`, and `reconcile-terminal` operation schemas, request
recognition, provider transport, receipts, findings, replies, resolutions, and
readback reconciliation. Implement Feature does not define those fields.

The controller selects an operation and supplies only its immutable authority
binding and typed evidence descriptor. GitStack prepares and validates the
owner request. A prepared request or controller template is not mutation or
wait authority. Immediately before launch, Implement Feature calls its own
`operation start`; that step revalidates exact live controller equality,
claim/CAS, task observation, current revision, and App-managed checkout and
records the `owned-operation-started` receipt described in `controller.md`.
GitStack then independently writes the same deterministic
`gitstack-review-operation-start:v1` receipt to its plugin-owned journal before
provider transport. GitStack never reads this skill's ledger or executes one of
its scripts.

Each started physical mutation or waiter is single-use. Repeating Implement
Feature `operation start` fails with `reconcile-required`; recovery uses
`operation read-start` and the owner reconciliation operation. Repeating a
GitStack execute against its existing start journal also fails closed. GitStack's
consumed marker and both journals bind the same deterministic receipt and exact
request. No caller-selected executable, transport, or installed path is accepted.

## Request and deadline invariants

The canonical request starts with `@codex review <full-40-sha>`, includes the
GitStack machine marker and SHA-256 request key, and is immediately read back.
The receipt binds exact comment id, URL, actor, body fingerprint, request key,
head, provider, repository, and PR. A recognized typed request with no provider
artifact is valid pending; missing acknowledgment is not correlation failure.
Only a proven absent, malformed, mismatched, or ambiguous request artifact is
correlation failure. Legacy/plain requests are rejected and never reposted.

The review deadline is immutable and exactly request start plus 45 minutes.
Launch after expiry performs exactly one zero-timeout check. There is no reset,
extension, repost, retry, or second waiter. `pending-at-deadline` is only
`warning-required`; it cannot pass the gate. The separately started GitStack
warning operation must record the canonical persistent warning for the same
request/revision lineage before normalized state becomes `warned-timeout`.
Provider failure routes to reconciliation or authorized owner attention, never
another waiter.

## Results and reconciliation

`operation record-result` calls GitStack's `validate_result_for_request`, then
stores the complete result as opaque evidence with only normalized orchestration
fields. The same result is idempotent; a different result for the same started
operation is rejected.

A later independently verified exact-head clean or findings artifact may use
`reconcile-terminal` to append a superseding result for the same
repository/PR/head/request/provider lineage. The earlier false stale/unbound
observation remains visible and linked by result fingerprint. Any identity
mismatch rejects supersession. Mutation reconciliation likewise performs
readback only and never posts or resolves again.

Warning, request, reply, and mutation identities retain GitStack's stable
operation marker. Thread resolution is proven by exact thread identity and
`isResolved=true`. No operation grants merge, enqueue, deploy, Goal, task, or
worktree authority.
