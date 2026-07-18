# Review Monitoring Lifecycle

Load only for a pending initial deadline or typed monitoring schedule.

## Schedule And Quiescence

Persist `review-wait-invoked` before the call; recovery never starts another
waiter. Bind each result to current `monitoring_cycle`. A pending schedule
increments that cycle and derives `due_at=observed_at+30m`; an elapsed due time
remains `checking` for an immediate one-shot.

After every current delivery review is either complete or future-scheduled,
derive the complete schedule fingerprint, pause and read back the worker Goal,
then apply `task-monitoring-paused`. A multi-delivery worker pauses once, not
once per delivery. Paused tasks remain nonterminal and count against the
three-task limit.

After each material event, derive portfolio quiescence. Keep the root active and
retain the claim while any worker is active, a Spec is dispatch-ready, a review
check is due, or controller action remains. Otherwise create or update exactly
one heartbeat targeted to the root task for the earliest future `due_at`.
Persist its id, pause and read back the root Goal, then apply
`portfolio-goal-paused` with that heartbeat/root-pause evidence. Keep the exact
active claim and fingerprint while paused; do not create a handoff or release
ownership.

## Wake And One-Shot Check

On heartbeat or manual wake, first verify the same root still owns the exact
claim/fingerprint. If root is paused, resume/read it and apply
`portfolio-goal-resumed`; otherwise keep it active. Consume any recorded heartbeat. Resume a worker with
`task-monitoring-resumed` and the unchanged schedule fingerprint. `due-review`
activates every due delivery and resumes the Goal only when paused;
`controller-action` permits an early revision, cancellation, or owner
reconciliation without changing review history. Neither launches a waiter.

Clean, findings, or failed results end that monitoring schedule. A pending
result is cycle-bound and rescheduled from its observation. After all current
reviews are again complete or future-scheduled, pause the worker once with the
new complete fingerprint. An early manual wake does not make future checks due.

## Invalidation And Recovery

Before applying a changed delivery revision, resume root if paused, then resume
the worker with `resume_reason=controller-action`, consume any heartbeat, and
apply `revision-observed` followed by current `delivery-observed`. Old revision
schedules remain bounded history and are inert because all due selection uses
only each delivery's current revision. Terminal closeout, cancellation, and
owner intervention also consume a stale armed heartbeat before proceeding.

Crash recovery converges on committed state:

- a committed heartbeat id is viewed and updated, never duplicated;
- no committed id permits exactly one heartbeat after schedule and Goal
  revalidation;
- a heartbeat created before id commit is deleted only after proving it targets
  this exact root and schedule;
- a committed worker pause binds one complete schedule fingerprint;
- a committed root pause retains the same claim; wake verifies it before any
  worker mutation;
- a persisted wait invocation is observed or recovered, never relaunched;
- if an authorized takeover replaced the claim, the old root stops.

Never imitate pause/wake with `blocked`, terminal handoff, raw RPC, cron, or a
replacement Goal/task. Missing Goal pause/resume or targeted heartbeat returns
`unsupported-runtime` before authorization.
