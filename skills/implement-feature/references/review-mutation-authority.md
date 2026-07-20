# Review Mutation Authority

This authority is unavailable while any task has
`implementation_baseline=pending`. Do not prepare or persist a reservation,
start a provider call, or invoke GitStack until the atomic baseline is accepted
and the root Goal is active.

Load this reference before any review provider mutation or its recovery. It is
the Implement Feature boundary for GitStack's shared pure protocol; it does not
duplicate GitStack receipts or AutoReview's attempt protocol.

## Immutable packet and CAS

GitStack owns the one physical
`plugins/gitstack/projects/gitstack/src/gitstack/review_mutation.py` module.
Implement Feature imports that exact file for field and identity validation.
The typed `reviews prepare`/`reviews validate` surface creates or checks one
immutable packet containing the exact repository, PR, full head, request key
and fingerprint, thread/finding identity, body or reply-receipt fingerprint,
operation id, task/delivery identity, expected ledger generation, expected
state/claim fingerprints, expected task state, recovery policy, and transport.
The packet has no `attempt_state`.

GitStack 5.0.0 intentionally makes the four provider mutation commands
managed-only: standalone callers may use typed `reviews prepare` and
`reviews validate` to create and inspect the same packet, but cannot POST or
resolve a provider artifact from a packet alone. Each mutation also receives
`--ledger-file`; GitStack invokes the read-only
`ledger review-authority` bridge, which validates the active root claim and
proves that this exact packet is the single journal entry in
`mutation-started`. This is the breaking authority boundary, not an
Implement Feature schema shortcut or a second lifecycle protocol: a
self-consistent packet alone is not authority.
The read-only verifier command is:
`scripts/ledger-cache --json ledger review-authority --ledger <absolute-ledger>
--reservation-file <absolute-packet>`.
Independent installs place the verifier under an installation-owned standard
skill root. Arbitrary environment overrides are not accepted: GitStack never
trusts a caller-selected executable and never searches the target checkout.

The root applies `review-provider-mutation-reserved` and then
`review-provider-mutation-started` in CAS before dispatch. The ledger journal
alone advances `prepared` → `mutation-started` → `completed` or
`failed-or-ambiguous`; result and resolution are one CAS batch when possible,
and preserve the exact dependency-wait `resume_state` when separated.
During a wait, a packet binds the current generation/state and effective
`resume_state`; exact delayed replays are no-ops, while new stale authority is
rejected.

| worker action | durable guard and receipt |
| --- | --- |
| request POST | mutation-started (`review-request`), consumed marker, exact GitStack request receipt |
| provider wait launch | `review-wait-invoked`, immutable request receipt/revision, one invocation |
| observation/finding handling | `review-observed`/`review-thread-resolved`, exact observation/reply/resolution receipts |
| AutoReview fix verification | existing `autoreview-action-reserved`/`autoreview-attempt-observed` protocol |
| terminal closeout | existing `task-terminal-sealed`/`terminal-handoff-recorded` CAS sequence |

Mutation kinds are `review-request`, `review-warning`, `review-reply`, and
`review-resolution`.

Warning comments, replies, and requests carry the stable non-semantic operation
marker. Reconciliation matches it plus exact repository/PR/head/request,
thread/finding, body, and actor. Thread resolution has no synthetic marker;
its proof is exact thread identity and `isResolved=true`. `@codex review` must
remain followed by the exact full SHA.

## Crash, replay, and recovery

GitStack atomically writes and fsyncs a one-use consumed marker before POST or
GraphQL dispatch. A crash before transport therefore forbids retry. After
consumption, recovery performs at most one read-only exact-artifact lookup. A
unique marker-plus-target artifact completes the journal; missing, conflicting,
or ambiguous evidence records `failed-or-ambiguous`/`needs-owner`. Never delete
a marker, recreate a packet, retry/relaunch, reset a deadline, or use a creation
window as the sole identity proof. Resolution reads the exact thread rather
than inventing a comment.

The root may precompute packet fields, but `wait_invoked_at` must be reported
from the actual worker launch: it determines the immutable
`provider_timeout=max(0,floor(wait_deadline-wait_invoked_at))`. Persist
`review-wait-invoked` before launch; one zero-timeout check is still one launch.
The 45-minute exact-revision deadline is never extended or recomputed.

Dependency wait is only root bookkeeping. A fresh active-root liveness proof
makes the interval expected and it never counts toward blocked-audit turns.
Worker Goals do not exist. Host rediscovery reuses stable task/review identity,
does not persist `host_id`, replace a task, reset a deadline, or create another
request/attempt. A stale or blocked UI projection cannot be repaired with stale
evidence; recovery requires a supported root state transition and remains
fail-closed otherwise.

The contract suite must load this same module by resolved path, reject duplicate
field/transition tables, and cover valid/missing/stale/conflicting packets,
CAS replay and delayed messages, request/reply POST ambiguity, crash-before-
POST, warning/reply markers, resolution readback, zero-timeout launch,
simulated root latency, prompt ceilings, host rediscovery, and no retry after
consumption.
