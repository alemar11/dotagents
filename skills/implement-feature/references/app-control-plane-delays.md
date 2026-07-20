# App Control-Plane Delay Recovery

Load only after App task identity, title, or root Goal evidence is delayed or
ambiguous, or a generated title overwrites the persisted title. This edge case
was observed in two monitored runs; the normal path adds nothing.

## Fixed Budgets And Notice

Measure deadlines with a monotonic clock from the first operation attempt.
Responses, overwrites, resumes, reads, and retries never reset it. Clip waits
to the remaining budget; no wait slice exceeds 30 seconds.

| operation | absolute elapsed-time budget |
| --- | ---: |
| title or Goal stabilization | 60 seconds |
| queued creation identity resolution | 120 seconds |

At 10 seconds, emit at most one concise notice that the App control plane is
delayed and worker activity may be unknown; emit no unchanged-progress chatter.
`control-plane-delayed` is transient root/user-facing wording only, never a
ledger field, event, option, lifecycle state, packet, helper, or automation.

Resume only when the original first-attempt/deadline and notice evidence remain
available from the same live controller or exact durable App/tool history. If
the deadline origin is unavailable, treat the budget as exhausted. If notice
history is unavailable, suppress another notice. Never grant a fresh window.

These bounds do not change the 60-second claim heartbeat, 180-second
monitor-degraded rule, five-minute closeout rule, review deadline, freshness
monitoring, or unchanged-progress policy.

## Identity And Read Authority

A queued `clientThreadId` stays bound to its App-managed creation until that
exact creation exposes `(hostId, threadId)`. Correlate only with returned
creation evidence. Titles, timestamps, guessed mappings, and nearby tasks are
never identity. Never create a replacement.

Compact `wait_threads` snapshots/cursors are transient hints. Only a direct
full `read_thread` page chain with existing EOF or unbroken-anchor proof may
create durable observation or authorize transition. Wait and read pagination
cursors are opaque, distinct, and never compared. A pre-identity timeout is
control-plane latency, not worker inactivity.

## Retry And Readback Policy

Safe retries are limited to reads and the exact same
`(hostId, threadId, persisted_title)` title write within the original 60-second
budget. Never retry `create_thread`, steering or message calls, `create_goal`,
or `update_goal` after ambiguous transport.

Authoritative readback may prove an ambiguous mutation applied. Matching task
identity, Goal objective/state, or title permits the existing transition;
conflicting or unknown readback stops fail-closed. Latency is
`unsupported-runtime` only when the existing test proves support missing, and
is never implementation failure.

## Ordering And Title Stabilization

Preserve order: SURFACE/root `get_goal`, authorization/CLAIM, REGISTER root-title
readback, then worker identity/title before assignment, checkout, and baseline
acceptance. After atomic acceptance, call `create_goal` exactly once and use
`get_goal`; reconcile terminal `update_goal` the same way, never blindly retry.

The title quiet window exists only immediately after creation or activation and
inside the same 60-second budget. Require two consecutive matching title
observations at least five seconds apart. A mismatch resets only the consecutive
match count, never the deadline. When title-source evidence exists, precedence
is explicit user title, persisted parent title, then generated title. Without
source metadata, stop automatic correction when the quiet window ends so later
user renames are preserved.

## Exhaustion

An unresolved pre-CLAIM SURFACE or `get_goal` delay exits with zero workflow
mutations. After CLAIM, preserve the exact claim, task, creation, and Goal
identities and use existing `needs-owner` handling without another permission
or authorization prompt. Do not replace an identity, manufacture readback,
reset a deadline, or classify the implementation as failed.
