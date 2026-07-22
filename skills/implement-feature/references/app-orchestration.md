# App Orchestration

This reference owns root App task and Goal sequencing; workers never use those
tools.

## Surface And Project Mapping

Require these current root capabilities before state:

- `codex_app__list_projects`, `codex_app__list_threads`,
  `codex_app__create_thread`, `codex_app__read_thread`,
  `codex_app__send_message_to_thread`, and `codex_app__set_thread_title`;
- `codex_app__set_thread_archived` only for verified preimplementation reconciliation;
- `get_goal`, `create_goal`, and `update_goal`.

Call `list_projects` once per fresh intake snapshot and use only that response.
After a real wait, staleness, or drift, replace the whole snapshot; never reuse
an ID from memory, earlier state, or an old manifest. Map each path to one
project ID and one App-managed worktree.

Do not pass `model` or `thinking` unless the owner requested exact values;
otherwise inherit platform and thread defaults.

## Root Goal

Read the current Goal before `run start`:

- no unfinished Goal: put the exact objective in the manifest; after start,
  journal App `create-goal` for `<root_task_id>`, invoke it, read back `active`,
  finish with `{status,objective_sha256}`, then `goal bind source=created`;
- an active Goal whose objective covers exactly this invocation: preserve its
  exact objective in the manifest, re-read it after start, and call `goal bind`
  with `source=adopted`;
- a blocked or unrelated unfinished Goal: stop before state as `needs-owner`.

The Goal describes the implementation outcome. Its existence does not grant a
worker edit authority. Never create a worker Goal and never synthesize a Goal
state without readback.

## Create And Bootstrap One Task

Use the assignment's exact project ID and `environment=worktree`:

1. Journal App `create-task` with the assignment ID as subject. Call
   `create_thread` once. If it returns `clientThreadId`, poll recent
   `list_threads` until that queued identity resolves to one thread ID; only then
   read it. Never create a replacement. Finish with `{thread_id}`.
2. Journal App `set-task-title`, call `set_thread_title`, then read the same
   thread until its exact immutable assignment title is observed. Finish with
   `{thread_id,title}`.
3. Observe the exact App project ID, Git repository claim, Git common directory,
   managed checkout path, Git top-level, checkout branch, and baseline head in
   that thread. Resolve the common directory independently from inside the
   checkout and call `task bind` with the exact schema-1 observation from
   `run-state.md`.
4. Journal App `send-worker-bootstrap`, send the baseline-only prompt from
   `worker.md`, and finish with `{thread_id}`.
5. Wait for the worker's baseline report. Read the thread and checkout; after
   accepting the exact baseline call `task baseline`.

Task identity is the thread ID, not its title. Delayed creation, title, or
checkout evidence remains the same pending operation and task. Never replace
it because a timeout elapsed.

## Explicit Implementation GO

Accept the complete baseline set for the current dispatch wave before any task
in that wave edits. For each accepted task:

1. journal App `authorize-implementation` for its assignment;
2. send an explicit message stating `implementation_authority=granted`, the
   accepted baseline head, immutable scope fingerprint, and first prose phase;
3. finish the operation with `{thread_id}`;
4. call `task authorize`.

Without all four steps the worker remains baseline-only. This message, not Goal
activation, is the edit boundary. `operation begin` fails closed while any
dispatched task is still `baseline-pending`, before a GO message can be sent.

## Monitor And Refill

One monitoring sweep reads every live task once in canonical order. After three
unchanged sweeps in one controller turn, emit one liveness line and continue on
the next Goal turn. `read_thread` is authoritative; persist only material state.

## Root Goal Blockers

Keep recoverable blockers in the active run. At the platform blocked threshold,
an unrelated pending or unknown operation must not prevent the Goal transition:

1. journal App `block-goal` for the root task;
2. call `update_goal(status=blocked)` and read back the exact objective and
   `blocked` state;
3. finish the operation with `{status:"blocked",objective_sha256}`;
4. re-read `run show` and require `goal.status=blocked`.

Keep that run and its claims active; preimplementation abort needs explicit
abandonment. Only in an explicit owner turn, journal protected
`owner/resume-goal` and use the exact correlation ref
`owner:resume-goal:<run_id>:<operation_key>` in request and result. Finish with
`{status:"granted",authorization_ref}`. Require `run show` to report
`blocked_resume_authorized=true` before worker or provider mutations. The Goal
stays blocked and may later complete directly; never invent `active`.

Before GO, the owner may abandon a permanently blocked run: reconcile tasks and
operations, then in that explicit owner turn journal protected `owner/abandon-run`
with `owner:abandon-run:<run_id>:<operation_key>`, finish with
`{status:"granted",authorization_ref}`, then abort. After GO, abandonment and
claim release are forbidden; after abandonment, work cannot resume.

Keep at most three tasks in `baseline-pending`, `baseline-passed`, or
`implementation-authorized`. When a task becomes `ready-for-merge`, call
`task ready`; that task no longer occupies a live slot. Re-read `run show`, sort
planned assignments by `assignment_id`, and dispatch the first assignments that
do not overlap live allowed paths until three slots are full or no compatible
assignment remains.

Two path sets overlap when either contains a wildcard or one normalized path is
equal to, an ancestor of, or a descendant of the other. Missing path evidence
conflicts. This scheduling decision stays in prose; `run-state` only enforces
the three-task ceiling and exposes planned/live assignments.

## Completion

After `gates.md` independently verifies every assignment:

1. journal App `complete-goal` for the root task;
2. call `update_goal(status=complete)`;
3. call `get_goal` and require the exact objective and `complete` state;
4. finish the operation with `{status:"complete",objective_sha256}`;
5. call `goal complete`, then immediately `run finish --outcome completed`.

Do not complete the Goal merely because tasks stopped. If App truth changes
between Goal readback and run finish, stop for the owner; a completed Goal is
never reopened or falsified.

## Preimplementation Start Over

Before GO, a failed baseline task may finish naturally or be journaled and
archived, then read back as `completed|archived` and recorded with `task abort`.
When every created task is terminal and others remain planned,
`run finish --outcome preimplementation-aborted` releases claims for an active
Goal; start the fresh run in the same controller flow so it can adopt that Goal.
A blocked Goal preserves the run and claims unless explicit preimplementation
`owner/abandon-run` authorizes release.

After implementation authority, use recovery. Do not archive, replace, or
discard the worker as a start-over shortcut.
