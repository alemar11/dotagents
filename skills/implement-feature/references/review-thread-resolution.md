# Typed Review-Thread Resolution

Load this file only when GitStack returns a nonempty
`review.finding_comment_ids` list or recovery sees a stored thread-resolution
receipt.

## Addressable Findings

Persist `review.findings` as `finding_count` and the exact sorted
`review.finding_comment_ids` list. Their cardinality must match. A terminal
provider-comment `findings` verdict may carry zero for both; it remains
fix-required and needs a fix plus fresh review, but creates no thread gate.
All other review outcomes require zero and an empty list.

V1 handles actionable fixes only. Do not resolve a no-change disposition.

## Reply And Resolve

For every listed id after the fix is pushed:

1. Write the evidence reply through the provider-text contract in `worker.md`.
2. Call typed GitStack `reviews prepare --mutation-kind review-reply` with the
   exact repository, PR, current full head, request/thread/finding identities,
   body file, and root ledger generation/state/claim bindings. Persist the
   reservation and `review-provider-mutation-started` before dispatch.
3. Call GitStack `reviews reply` with the reservation file, active ledger file, exact repository,
   PR, current full head, REST finding id, body file, and fresh worktree
   fingerprint.
4. Persist the complete `gitstack-review-thread-reply:v1` receipt unchanged.
5. Prepare a `review-resolution` reservation from that receipt and the exact
   current thread fingerprint; persist its reservation and started event.
6. Call `reviews resolve` with the active ledger file, same repository, PR and full head, the
   unchanged reply-receipt file, and a fresh worktree fingerprint.
7. Persist both receipts through `review-thread-resolved`, binding the finding
   revision and current resolution revision.

Never assemble a thread id or call raw GraphQL. GitStack discovers all thread
and comment pages, matches the exact finding GraphQL node id, and re-reads the
finding, reply, current head, and thread membership. `already-resolved` is valid
only after the same complete proof and does not identify who resolved it.

If GitStack returns `mutation_may_have_applied=true`, stop as blocked. Do not
retry, undo, or switch transports.

The reply body carries the reservation's stable operation marker. Resolution
has no synthetic comment marker; its one-use proof is the exact thread identity
and `isResolved=true` read-back. A consumed reservation is never retried,
recreated, or released.

## Run-State Rules

The reply receipt must bind repository, PR, finding and reply heads, thread,
finding and reply REST and node ids, author, URLs, timestamps, body fingerprint,
and identity fingerprint. The resolution receipt must bind that exact reply,
head and thread and prove `is_resolved=true`.

Replay of identical receipts is a no-op. A conflicting duplicate, wrong
repository/PR/thread/finding, missing reply, stale resolution revision, malformed
receipt, or ambiguous identity fails closed. Terminal sealing requires exactly
one resolution record for each stored addressable id. Zero-id findings add no
resolution requirement.

On recovery, revalidate stored receipts against their finding and resolution
revisions. Never replace missing or uncertain proof with raw GraphQL.
