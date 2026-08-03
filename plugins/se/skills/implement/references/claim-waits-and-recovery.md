# Implement Claim Waits And Recovery

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

### Parent root creation may already have happened

If the parent session was interrupted after requesting the root but before
receiving a stable task identity, reconcile authoritative App state using any
provisional identity evidence when available. Verify the root's stable identity,
exact local project, execution mode, state, and `gpt-5.6-sol` / medium-reasoning
profile before continuing. A title warning is telemetry;
structural or settings drift stops before any worker or run-state mutation.

If a real root exists, reuse it and continue monitoring; if authoritative
readback proves that no root exists, one bounded creation retry may use the
same parent bootstrap attempt. Timeout, transport error, or contradictory
evidence remains unresolved and forbids a duplicate. The parent must never
search by title alone or create a second root with a new title.

Once the root has started `run-state`, its `root_task_id` is the durable
controller identity. Parent-session interruption does not release claims or
authorize a replacement root; resume is routed to the same visible root.

### The root task was interrupted

An unfinished run keeps its exact `root_task_id` as the sole controller
identity. Resume that same visible root task manually, read `run show`, and
reconcile every pending or unknown task operation against authoritative
Codex task state in the ChatGPT App before scheduling or considering any authorized
replay.
Never create a replacement root, infer completion from task idleness, persist
the objective, or use a heartbeat as lifecycle state.

### Worker creation may already have happened

If root was interrupted after requesting a visible worker but before recording
the result, read the ChatGPT App task list and the candidate Codex task.
Reconcile the exact recorded operation ID and launch count against the live App
state before accepting or replaying the operation. Independently verify the
task's stable ID, selected project, host, environment, checkout directory, Git
common directory, and current state. If the exact worker exists, finish the
already recorded `create-worker` operation and reuse it. First reconcile its
independently observed creation title. If that title is not exact, reconcile
the separately recorded `set-worker-title` fallback: apply the title only for
its authorized launch, observe the exact title, and bootstrap only after that
creation-or-fallback path is attempted. If the exact worker exists but title
initialization did not happen, do not treat the creation prompt or an
incidental title as sufficient evidence; record `title-unverified` or
`title-drift` and bootstrap once the structural worker evidence is verified.
If authoritative evidence proves no task was created, finish that launch as
`failed` with its `readback_ref`; the resulting `replay_authorized=true` permits
`app-operation replay` with the same `operation_id` and incremented
`launch_count`. Ambiguous evidence stays `unknown`, is not replayable for
worker creation, and forbids a duplicate worker.

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
closed. Use `assignment capability-block` only while the ChatGPT App
capability remains unavailable; after authoritative recovery, the same root
uses `assignment resume --observation <absolute-path>`. The strict observation
binds the exact run, assignment, current run revision, blocked reason, matching
recovered state, and authoritative readback ref. Durable-contract recovery
likewise supplies the exact durable-source reread ref. The resume transition
stores that evidence on the retained claim; it must not rely only on controller
judgment. That source correction must have been published by the
`external-planning-owner` defined in `feature-spec-contract.md`; root and worker
must not create or repair the stable planning change they later use for resume.
Resume is valid only when the reread restores the exact stable contract already
accepted by the run. A changed stable contract cannot be rebound onto the
retained assignment or claim and requires a new run after existing-owner
reconciliation.

An assignment in `blocked-scope-repair` does not use `assignment resume`.
Recover the recorded planner-task and scope-revision operations through
`scope-repair-orchestration.md`. Root retains the Feature Spec claim and the
original worker task, and the contract generation changes only after verified
delivery of the exact scope revision.

## Terminal Owner Reconciliation

Before blocking a waiting Spec after recovery, read the exact owner root and
worker from the ChatGPT App and call `claim reconcile` with that exact
owner revision and typed observation.

- Active worker or present checkout: retain the owner and continue the bounded
  wait.
- Archived, completed, or authoritatively missing worker plus released/absent
  checkout and no unresolved recorded changes: mark the owner
  `preimplementation-aborted` if bootstrap never succeeded, otherwise
  `abandoned`, then release that exact claim. Acquire the waiter only when the
  command returns `claim_acquired=true`. When it returns
  `claim_acquired=false` with a new `conflicting_owner`, keep the waiter in
  `waiting-for-spec` and reconcile that newly recorded owner before worker
  creation.
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
