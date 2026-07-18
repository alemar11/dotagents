# Recovery Validation

Load this reference on every runtime resume, including prepared takeover and
embedded task-adoption recovery before a candidate JSON state exists.

## Runtime Surface Revalidation

Before reading run state or a recorded task, verify visible ChatGPT desktop app
task creation, App-managed worktree binding, task-title mutation through
`codex_app__set_thread_title`, live task-title observation, and `create_goal`,
`get_goal`, and `update_goal` in the root plus general visible-task Goal-tool
support. Require first-class targeted Goal `active`/`paused` read-write support
and App heartbeat create/view/update/delete plus same-root-task wake support.
Prior evidence, generic subagents, and filesystem access are
insufficient. If a required surface is absent or unverifiable, abort as
`unsupported-runtime` without asking permission or touching runtime artifacts.

Read `ledger-cache ledger read --projection recovery` only after that gate.
Before any mutation, read each exact recorded task and require its runtime to
expose the same Goal tools. A missing task-local tool blocks the existing task;
never create a replacement or objective fallback.

## Freshness Pass

Perform one complete read-only pass:

1. Revalidate run authorization, `task-model-policy.md`, and every recorded
   per-Spec profile, including no-task Specs. Unknown fields, missing evidence,
   unavailable profiles, or silent substitutions block.
2. Recompute every authoritative source and issue fingerprint plus every
   canonical claim/task source id. A verified GitHub shorthand must still map
   to its canonical issue URL. For a local issue, accept a missing active path
   only when its exact predeclared done ref exists in the same managed checkout,
   its body fingerprint is unchanged, and Git proves the planned tracked move.
   Both paths, neither path, another destination, or changed body blocks.
3. Verify repository identity, current HEAD, branch, tracked state, and every
   managed checkout's isolation.
4. Verify that `active-root-claim` still covers the same repositories and
   sources under the recorded acquire-time fingerprint. For
   `takeover-prepared`, require the recorded grant and exact transaction id and
   run only the helper's idempotent `recover-takeover` path. A mismatched
   replaced snapshot blocks.
5. Rebuild the complete implementation-eligible Feature Spec registry. Derive
   exactly `👨🏻‍💻 Feature Orchestrator` for one Spec or
   `👨🏻‍💻 Multi-Feature Orchestrator` for more than one. Require at most one task
   per Spec and three nonterminal tasks portfolio-wide. Record live title drift
   without repairing it during this pass.
6. Call `get_goal` in the root and every recorded task. Pending portfolio Goal
   registration may observe a matching active Goal or no Goal; do not adopt or
   create it during this pass. Active Goals must match their objective,
   fingerprint, and evidence and are never recreated. Paused state is valid only
   for a typed future `review-monitoring` schedule with matching pause evidence.
   Completed state requires
   matching completion evidence. A terminal task with an active matching Goal
   is only an interrupted completion transition; never resume its
   implementation.
7. Recompute exact PR number and URL, head/base/merge-base tuples, review
   request and absolute deadline state, CI, AutoReview, mergeability/rules,
   tracker and domain closeout, merged dependencies, path conflicts, ready
   order, due checks, blockers, and next action. A material revision, evidence,
   target, or documentation change invalidates affected gate evidence.

The recovery projection is derived guidance, not external truth. Any mismatch
requires full source and live-task reconciliation. Do not patch JSON directly,
repair a projection, or manufacture an event from stale prose.

## Resuming Valid State

Only after the full pass succeeds may the root apply material events through
`ledger-cache ledger apply` with the observed generation. If a local move is
fully proven, apply `source-moved`. If revision truth changed, apply
`revision-observed` and let the helper invalidate revision-bound evidence. On a
CAS conflict, discard the batch and rerun the needed freshness checks.

For `portfolio_goal_state=pending`, first repair and observe the exact root title
when needed, then apply `root-title-observed`. Adopt a matching Goal observed
during the pass or, only when none exists, call `create_goal` once without
`token_budget`; apply `portfolio-goal-activated`. A different unfinished Goal is
`needs-owner`.

For a nonterminal task, require the exact Feature Spec assignment, task ref and
derived display title, profile, matching active assignment Goal or the exact
typed paused Goal for a future review check, complete
managed checkout map, and fixed PR-ready flow. Repair title drift on that same
task only after freshness passes, then report it through `task-observed`.
Resume only the original visible task with its recorded profile. Missing or
unrecoverable task or checkout evidence blocks; never allocate a replacement.

## Review-Wait Recovery

Recompute the current revision key before review work. Reuse a clean or
findings result only for the exact unchanged PR/head/base/merge-base tuple with
all findings dispositioned. If a request exists, preserve its original
`wait_started_at` and absolute `wait_deadline`; the worker computes a new
`provider_timeout=floor(wait_deadline-now)` immediately before launching one
GitStack waiter. Never restart, segment, extend, or substitute a provider
default. If time is nonpositive, check once. When still pending, verify the
typed worker pause, schedule, root heartbeat, and root pause evidence. On wake,
resume the root first, reacquire and rebind the claim, consume the heartbeat,
and resume only workers whose `due_at` has arrived for one check. If still
pending, rearm exactly 30 minutes from that observation without another waiter.

An early manual resume consumes the heartbeat but does not make future checks
due. A revision change requires resuming the affected Goal, consuming the old
heartbeat, and recording the new tuple before any new request. Crash recovery
must converge on one schedule and one heartbeat id: create only when no id was
committed, update only the committed id, and delete stale ids after proving the
run-state owner. Never leave two heartbeats for one portfolio.

## Terminal Closeout Recovery

For `portfolio_goal_state=complete`, require every task Goal and fixed terminal
gate complete and independently verify the exact current PR identities and
revision tuples. Never repair or resume implementation. Repair only root-title
evidence when needed. If the claim remains active, run the complete terminal
release/archive sequence in `cache-lifecycle.md`; if already released, finish
the same archive operation idempotently with the same root and evidence.

For interrupted closeout while the portfolio Goal is active, first require
every terminal gate. Complete each terminal task Goal that is still active and
apply its `task-observed` evidence; adopt already-completed matching evidence
without another tool call. Then complete the portfolio Goal, apply
`portfolio-goal-completed`, and continue through checksum-bound release and
archive. These are closeout transitions, not implementation resume.

## Prepared Takeover Without Candidate State

When a recovered takeover claim has no candidate JSON because creation never
completed, initialize only from the current prepared journal's complete
embedded adoption mappings after verifying the claim, source registry, task
Goals, exact profiles, titles, and managed checkouts. Apply `claim-rebound`
after initialization. Do not infer identity from task titles, read a replaced
root's prose, or create a task for a Spec with embedded task evidence.

If candidate JSON already exists, it must validate normally. If an old active
Markdown path or unsupported schema exists, recovery blocks. Do not import,
migrate, rename, dual-read, retire, or delete it. A fresh run is legal only
after the prior owner releases its claim.
