# Review Thread Resolution

GitStack 6.0.0 owns reply and resolution request/result schemas, body and thread
identity, provider transport, receipts, and reconciliation. Implement Feature
selects the closed owner operation and supplies immutable authority only.

Every reply or resolve transport requires a fresh generic
`owned-operation-started` receipt immediately before the physical mutation.
A second start fails; after consumption, use GitStack `reconcile-mutation`
readback and never post or resolve again. `operation record-result` calls
GitStack's request-correlated validator and persists the opaque result plus
normalized state. A different result for the same start fails closed.

Resolve only the exact accepted finding thread after current committed repair
evidence. Summary-only findings have no synthetic thread. Resolution never
grants merge, enqueue, deploy, Goal, task, or worktree authority.
