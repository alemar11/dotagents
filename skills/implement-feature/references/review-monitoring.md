# Review Monitoring Lifecycle

Load this reference only when the final check at an initial review deadline is
still pending, or when recovering a recorded review-monitoring schedule.

## Schedule And Quiescence

Record the pending observation before `review-monitoring-scheduled`. The helper
pauses the same worker Goal, moves its task to `review-monitoring`, increments
`monitoring_cycle`, and derives `due_at=observed_at+30m`. The original request,
waiter, `wait_started_at`, `wait_deadline`, `wait_invoked_at`, and
`provider_timeout` never change. Paused tasks remain nonterminal, retain their
scope, and count against the three-task limit.

After every material event, derive whether the portfolio is quiescent. Keep the
root active and retain the claim while any worker is active, a Spec is
dispatch-ready, a review check is due, or controller action remains. Otherwise
create or update one heartbeat targeted to the exact root task for the earliest
future `due_at`. Persist its id, pause and readback the root Goal, apply
`portfolio-goal-paused`, release the claim with `durable-handoff`, and stop.

## Wake And One-Shot Check

On heartbeat or manual wake, resume and readback the root Goal first, reacquire
the claim, apply `claim-rebound`, apply `portfolio-goal-resumed`, and consume or
delete the recorded heartbeat. Resume only due workers through
`review-monitoring-resumed`. Each resumed worker performs exactly one canonical
review check; it never launches a second waiter.

Clean, findings, or failed results complete monitoring. A pending result is
recorded, then the same worker is paused and readback before another
`review-monitoring-scheduled` derives the next check 30 minutes from that
observation. An early manual wake consumes the root heartbeat but does not make
future worker checks due.

## Invalidation And Recovery

Head, base, or merge-base changes require the root and affected worker to be
active before `revision-observed`; consume the old heartbeat and monitoring
schedule before creating any request for the new tuple. Terminal closeout,
takeover, cancellation, and owner intervention likewise delete a stale armed
heartbeat before proceeding.

Crash recovery converges on the committed state:

- a committed heartbeat id is viewed and updated, never duplicated;
- no committed id permits creation of exactly one heartbeat after the schedule
  and Goal state revalidate;
- a heartbeat created before its id was committed is deleted only after proving
  it targets this exact root and schedule;
- a committed root pause without claim release completes that same release;
- a released claim with a waking root reacquires and rebinds before worker
  mutation.

Never use `blocked`, raw app-server RPC, a cron job, or a replacement Goal/task
to imitate pause or wake behavior. If first-class Goal pause/resume or targeted
heartbeat operations are absent, the mandatory surface gate returns
`unsupported-runtime` before authorization.
