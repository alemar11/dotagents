# App Orchestration

This reference owns the root's visible App task and Goal sequence. Workers must
not use any task-management or Goal tool.

## Surface And Project Mapping

Require these current root capabilities before state:

- `codex_app__list_projects` and `codex_app__list_threads`;
- `codex_app__create_thread`, `codex_app__read_thread`,
  `codex_app__wait_threads`, `codex_app__send_message_to_thread`, and
  `codex_app__set_thread_title`, plus `codex_app__set_thread_archived` only for
  verified preimplementation reconciliation;
- `get_goal`, `create_goal`, and `update_goal`.

Call `list_projects` before `create_thread`, as required by the App contract.
Map every repository's resolved absolute path to exactly one project ID. A
thread targets one project and one App-managed worktree; never pretend one
thread can own several repositories.

Do not pass `model` or `thinking` when creating or messaging a task unless the
owner explicitly requested exact values. Otherwise inherit the platform and
thread defaults.

## Root Goal

Read the current Goal before `run start`:

- no unfinished Goal: put the intended exact objective in the start manifest;
  after start, journal `owner=app`, `action=create-goal`, and
  `subject_id=<root_task_id>`, invoke `create_goal`, read back `active`, finish
  the operation with `{status,objective_sha256}`, then call `goal bind` with
  `source=created`;
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
   `list_threads` results until that queued identity resolves to one thread ID;
   only then use `wait_threads`/`read_thread`. Never create a replacement.
   Finish with `{thread_id}`.
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

Use `wait_threads` for bounded multi-task waits and `read_thread` for
authoritative transitions. Persist only material state in `run-state`; task
commentary remains App evidence.

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

Before any task receives implementation authority, a failed baseline or broken
task may finish naturally or be journaled and archived through
`codex_app__set_thread_archived`, then read back as `completed` or `archived`. Record that exact
identity with `task abort`. When every created task is terminal and every other
assignment remains planned, `run finish --outcome preimplementation-aborted`
releases claims. The root Goal stays active and may be adopted by the fresh run.

After implementation authority, use recovery. Do not archive, replace, or
discard the worker as a start-over shortcut.
