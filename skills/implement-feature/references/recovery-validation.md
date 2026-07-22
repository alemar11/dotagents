# Recovery And Repository Waits

## Bounded Repository Wait

A conflicting `run start` creates only `waiting-for-repository` coordination
state. It acquires no claim and authorizes no Goal, worker, worktree, branch, or
provider mutation. Run `run wait-sweep` at bounded controller sweeps.

- If every requested repository becomes free, one transaction acquires the
  complete set and returns `may_create_goal_or_worker=true`.
- If the same owner set remains for three unchanged sweeps, terminate
  `blocked-by-active-run` and report each owner run, root task, and known worker
  thread. Do not ask, wait indefinitely, or create App objects.
- If owner identity changes, the unchanged-sweep count restarts. Partial claim
  acquisition is never permitted. Worker-list changes are reporting updates,
  not owner changes, and never reset the bound.

A post-bootstrap blocked owner retains every claim. Another root cannot take
over. A verified preimplementation abort may reconcile and archive created
workers, complete and read back an already-created Goal, finish
`preimplementation-aborted`, and release. A whole run releases
normally only after every assignment and the Goal are PR-ready/completed.
Release is not merge proof: dependent Specs still wait for authoritative
upstream merge and integration evidence, while an independent Spec may start.

## App Recovery

Read `run show`, then page `app-operation list` to completion. For every pending
or unknown App operation, use the stable thread/Goal identity plus receipt and
readback to determine its effect. Finish the same operation; never relaunch or
replace the worker.

Recover the exact bootstrap through App receipt and thread readback, then reread
the current Feature Spec and issues. If exact baseline sections cannot be
recovered, fail closed. No state row, packet, body, result, or message hash may
stand in for readback.

Never archive a worker while its bootstrap operation is pending or unknown.
Reconcile delivery first; archive is legal only with proof that bootstrap never
granted implementation authority.

After recovery the worker performs its normal pre-issue reread and continues
compatible work autonomously. Stable drift becomes declarative
`blocked-durable-contract`; operational drift does not trigger a question.
