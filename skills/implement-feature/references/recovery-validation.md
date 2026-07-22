# Recovery And Feature Spec Waits

## Bounded Feature Spec Wait

`run start` claims each free assignment independently. A conflict leaves only
that assignment in `waiting-for-spec`; it authorizes no worker, worktree,
branch, or provider mutation for the waiting assignment. Other claimed
assignments in the same run continue.

Run `run wait-sweep` for one waiting assignment at bounded controller sweeps.

- If its exact Feature Spec and head branch become free, one transaction
  acquires the claim and returns `may_create_worker=true`.
- If the same owner remains for three unchanged sweeps, record
  `blocked-by-active-spec` and report the owner run, root task, assignment, and
  known worker. Do not ask, wait indefinitely, or create a replacement.
- If owner identity changes, restart only that assignment's sweep count. Worker
  lifecycle changes are reporting updates and do not reset the bound.

Repository identity alone never conflicts. Different Specs with distinct head
branches may run under different roots in the same repository. The default PR
base is not a head branch and does not participate in claim identity.

## Autonomous Owner Reconciliation

Before declaring a Spec blocked after recovery, read the exact owner root and
worker through authoritative App state. Call `claim reconcile` with the waiting
assignment, exact owner revision, and typed readback.

- `active`, or a terminal worker whose checkout remains present: retain the
  owner's claim and continue the bounded wait.
- `archived`, `completed`, or authoritative `not-found`, with no pending or
  unknown App operation and a released or absent checkout: mark the old
  assignment `preimplementation-aborted` when bootstrap never succeeded,
  otherwise `abandoned`; atomically release the old claim and acquire it for
  the waiting assignment.
- Unknown worker or checkout state, contradictory evidence, or any
  pending/unknown owner operation:
  mark the waiter `abandoned-recovery-required`, retain the owner claim, and
  stop declaratively without asking.

Archiving or inactivity of the root alone is never terminal worker proof. Do
not use elapsed time, heartbeat absence, a title, or a stale worker list to
infer abandonment. Recovery preserves branch, worktree, commits, PR, tracker,
and App evidence; the next worker inspects and reuses compatible existing work
instead of blindly replacing it.

`claim abandon` is an explicit administrative override, never a normal
controller action. It is legal only after the waiting assignment reached
`abandoned-recovery-required` and requires exact waiter and owner identities
plus both current revisions. The invocation is the separate abandonment
authority; it atomically marks the old assignment abandoned and transfers only
that Feature Spec claim. There is no TTL, heartbeat lease, implicit takeover,
or repository-wide release.

Claim release is never dependency completion: dependent Specs still wait for
authoritative upstream merge and integration proof.

## App Recovery

Read `run show`, then page `app-operation list` to completion. For every pending
or unknown App operation, use stable thread/Goal identity plus receipt and
readback to determine its effect. Finish the same operation; never relaunch or
replace the worker.

Recover exact bootstrap through App receipt and thread readback, then reread
the current Feature Spec and issues. If exact baseline sections cannot be
recovered, fail closed. No state row, packet, body, result, or message hash may
stand in for readback.

Never archive a worker while bootstrap is pending, unknown, or succeeded.
Before bootstrap, archive is legal only with proof that implementation
authority was never delivered; `assignment abort` then releases only that
assignment's claim.

After recovery the worker performs its normal pre-issue reread and continues
compatible work autonomously. Stable drift becomes declarative
`blocked-durable-contract`; operational drift does not trigger a question.
