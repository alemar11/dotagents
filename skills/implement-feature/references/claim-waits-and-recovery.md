# Claim Waits And Recovery

## Bounded Feature Spec Wait

`run start` claims each free assignment independently. A conflict leaves only
that assignment in `waiting-for-spec` and authorizes no task, worktree, branch,
or provider change for it. Other claimed assignments continue.

Run `run wait-sweep` for one waiting assignment at bounded controller sweeps.

- When its exact Feature Spec and head branch become free, one transaction
  acquires the claim and returns `may_create_worker=true`.
- After three unchanged sweeps with the same owner, record
  `blocked-by-active-spec` and report the owner run, root task, assignment, and
  known worker. Do not ask, wait indefinitely, or create a replacement.
- If owner identity changes, restart only that assignment's sweep count.

Repository identity alone never conflicts. Distinct Specs with distinct head
branches may run under different roots in the same repository.

## Concrete Interruption Scenarios

### The root task was interrupted

An unfinished run keeps its exact `root_task_id` as the sole controller
identity. Resume that same visible root task manually, read `run show`, and
reconcile every pending or unknown task operation against authoritative
ChatGPT desktop task state before scheduling or considering any authorized
replay.
Never create a replacement root, infer completion from task idleness, persist
the objective, or use a heartbeat as lifecycle state.

### Worker creation may already have happened

If root was interrupted after requesting a visible worker but before recording
the result, read the ChatGPT desktop task list and the candidate task. Verify
its stable task ID, selected project, checkout directory, Git common directory,
and current state. If the exact worker exists, finish the already recorded
operation and reuse it. If authoritative evidence proves no task was created,
finish that launch as `failed` with its `readback_ref`; the resulting
`replay_authorized=true` permits `app-operation replay` with the same
`operation_id` and incremented `launch_count`. Ambiguous evidence stays
`unknown`, is not replayable for worker creation, and forbids a duplicate
worker.

### A message may already have been sent

Read the exact worker conversation and the immediate tool result associated
with the recorded `send-bootstrap` or `send-worker-message`. When the message
is present in the correct task, finish the existing operation and do not
resend. When bootstrap delivery is absent or indeterminate, finish that same
operation as `failed` or `unknown` with the authoritative `readback_ref`; only
then may `app-operation replay` relaunch it with its original `operation_id`
and `bootstrap_id` and the newly returned `launch_count`. A follow-up message
has no replay path; never infer delivery from a stored body or hash and never
create a replacement identifier.

### Worker is terminal but its checkout still exists

Read both the visible task state and checkout binding. A completed, archived,
or missing task whose checkout remains present retains the owner's claim. The
waiting assignment continues its bounded wait; checkout presence means another
controller may not take over that worktree.

### Evidence is insufficient or contradictory

If task state or checkout state is unknown, observations disagree, or any
recorded change is still pending/unknown, mark the waiter
`abandoned-recovery-required`, retain the owner claim, and stop declaratively
without asking. Never use elapsed time, titles, heartbeat absence, or a stale
task list as proof of abandonment.

When the original root has no waiter, reconcile every recorded task operation
and use `assignment recover` with exact owner revision, worker, checkout, claim,
and readback evidence. Active worker or present checkout retains ownership.
Terminal/missing worker plus released/absent checkout marks the assignment
`abandoned` and releases only its claim; after every sibling is terminal, the
same root may use `run finish --outcome abandoned`. Unknown evidence fails
closed. Use `assignment capability-block` only while the ChatGPT desktop app
capability remains unavailable; after authoritative recovery, the same root
uses `assignment resume --observation <absolute-path>`. The strict observation
binds the exact run, assignment, current run revision, blocked reason, matching
recovered state, and authoritative readback ref. Durable-contract recovery
likewise supplies the exact durable-source reread ref. The resume transition
stores that evidence on the retained claim; it must not rely only on controller
judgment.

## Terminal Owner Reconciliation

Before blocking a waiting Spec after recovery, read the exact owner root and
worker from the ChatGPT desktop app and call `claim reconcile` with that exact
owner revision and typed observation.

- Active worker or present checkout: retain the owner and continue the bounded
  wait.
- Archived, completed, or authoritatively missing worker plus released/absent
  checkout and no unresolved recorded changes: mark the owner
  `preimplementation-aborted` if bootstrap never succeeded, otherwise
  `abandoned`; release that exact claim and acquire it for the waiter.
- Unknown or contradictory evidence: record
  `abandoned-recovery-required`, retain the claim, and stop.

Recovery preserves branch, worktree, commits, PR, tracker, and task evidence.
The next worker inspects and reuses compatible work instead of replacing it.
`claim abandon` remains a separate explicit administrative override requiring
exact waiter/owner identities and revisions after
`abandoned-recovery-required`. There is no TTL, lease, heartbeat takeover, or
repository-wide release.

Claim release never completes a dependency. Dependent Specs still wait for the
exact stable upstream delivery and integration proof required by their contract;
merge is required only when that contract says so.

Before bootstrap, archive is legal only after authoritative task inspection
proves implementation authority was never delivered. After bootstrap, the
worker rereads its sources and continues compatible work; stable drift records
`blocked-durable-contract` without a user question.
