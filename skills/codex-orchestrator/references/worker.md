# Worker Reference

Use this reference before creating, naming, messaging, steering, or closing
Codex worker threads or subagents.

## Worker Surfaces

Choose and record the worker surface before delegation:

- `codex-app-thread`: a visible Codex App thread created with
  `codex_app.create_thread`. Use this in Codex App only when the owner
  explicitly asks for visible, new, separate, or background worker threads, or
  otherwise explicitly indicates they expect visible, inspectable,
  handoff-ready background work.
- `cli-subagent`: a CLI/subagent worker created with `multi_agent_v1.spawn_agent`
  or the CLI `/agent` equivalent. Use this by default in CLI-oriented runs
  where spawned workers are inspectable through `/agent`.
- `no-delegation`: use the root thread only when delegation is not authorized,
  no inspectable worker surface is available, or the task is too small or
  tightly coupled for a worker.

Do not present hidden subagents as visible App threads. If the chosen surface
will not be visible in the Codex App sidebar, say that in the ledger and final
report.

## When Not To Delegate

Stay in the root orchestrator thread when:

- the task is small enough that orchestration overhead would dominate;
- the work overlaps heavily with root-owned integration or another worker's
  active files;
- no inspectable worker surface is available;
- the owner did not authorize delegation for the requested scope; or
- the remaining work is mostly gate evaluation, ledger updates, closeout, or
  publication decisions.

## Worker Rules

- Create one worker per repository or tightly scoped workstream.
- Give each worker a single clear objective, repository path or URL, branch
  expectations, and exit condition.
- Workers may inspect, implement, test, and report only within their authorized
  mode.
- Workers must not spawn sub-workers, create new Codex threads, manage other
  chats, or delegate their assignment.
- Workers must not edit orchestrator ledgers. They report status back to the
  orchestrator, which updates the ledger.
- Workers must preserve unrelated local changes and stage only authorized
  paths.
- Only the root orchestrator creates, reuses, forks, assigns, renames,
  messages, archives, closes, interrupts, or replaces worker threads.

## Worker Status Vs Root Lifecycle

Workers report execution status. The root orchestrator decides lifecycle:

- Worker status: `done`, `blocked`, `needs-owner`, `ready-for-review`
- Root lifecycle: `integrated`, `retained-for-inspection`, `abandoned`,
  `handoff-pending`

Do not equate a worker saying `done` with the workstream being complete. The
root still needs to inspect the latest state, choose an integration path, rerun
root-owned gates, and record the lifecycle decision in the ledger.

## Visible Thread Naming

For visible Codex App worker threads, set the thread title immediately after
creation and whenever the material assignment changes:

```text
<Project>: <short current task>
```

Examples:

- `livekit-vision: BE preview API`
- `dotagents: GitHub skill audit`
- `mobile: CI rerun fix`

Keep names short and task-specific. Avoid status-only names such as `Worker 1`,
`Active`, or `Needs review`. Record the worker id and title in the ledger.

## Read-Before-Steer

Before sending a new instruction, changing a title, archiving, interrupting,
closing, replacing, or handing off a worker, read its latest state with the
available thread/subagent inspection tool. Base any steering message on the
current worker status, files touched, blockers, validation, risks, and next
checkpoint.

Do not send broad new scope into a worker without recording why the existing
scope changed. If the latest state is unavailable, stop and report the missing
inspection surface instead of guessing.

## Multi-Wave Resync

Before reusing a worker for a second or later wave, or before changing a worker
to overlapping scope, reconcile the worker with root-integrated state:

- read the worker's latest state and identify its current branch, checkout,
  worktree, dirty files, generated ignored artifacts, validation, and remaining
  risks;
- identify root-integrated changes accepted since the worker's assignment,
  especially changes from other workers that touch the same files, contracts,
  fixtures, or docs;
- either hand the worker to a current checkout, send a precise resync brief
  with the accepted root changes, create a fresh worker from the current root,
  or keep the overlapping integration in the root thread;
- do not ask a stale worker to keep editing overlapping files until the resync
  path is explicit in the ledger.

If a worker still has unintegrated output from a previous assignment, integrate
or intentionally abandon that output before adding unrelated new scope. When
preserving previous worker changes is required, state that requirement in the
new prompt and ask the worker to report any overlap or conflict.

Prefer creating a fresh worker when the old one is stale, its checkout drift is
unclear, or the new scope overlaps accepted root changes enough that resync
would be harder to reason about than replacement.

## Worker Output Integration

The root orchestrator owns integration. Choose and record one integration path
per worker output:

- `handoff`: use `codex_app.handoff_thread` or the equivalent inspected worker
  surface when the worker's checkout should become the integration checkout.
- `worker-commit`: accept a worker-prepared commit or branch only when the
  authorization mode permits commit or publication and the root has reviewed
  the diff.
- `patch-apply`: apply a worker diff or patch in the root checkout, then inspect
  conflicts and rerun root gates.
- `manual-root`: reimplement or copy the relevant change in the root checkout
  when the worker output is partial, stale, conflicting, or easier to reproduce
  safely than to apply directly.

For every path, inspect the tracked diff, preserve unrelated local changes,
exclude generated ignored artifacts, rerun the required root gates, and record
the integration method and proof in the ledger. Do not commit, push, merge,
close, release, or mutate external services unless the current authorization
mode and gate state permit it.

## Generated Artifacts

Workers may create local ignored artifacts while validating work, such as
dependency directories, build outputs, caches, virtual environments, screenshots,
or coverage files. The worker final report must list those artifacts separately
from tracked source changes.

Generated ignored artifacts are not automatically a failure, but they are part
of closeout. The root orchestrator decides whether they are removed, retained
for inspection, or left inside a disposable worker worktree. Never treat ignored
artifacts as proof that tracked changes are clean; inspect tracked status and
diffs explicitly.

## Worker Closeout

After a worker reports `done`, `ready-for-review`, `blocked`, or `needs-owner`,
the root orchestrator decides the worker lifecycle state before final owner
status:

- `integrated`: output was accepted into the root checkout, root gates passed,
  and the worker can be archived or its helper worktree removed.
- `retained-for-inspection`: output or artifacts are intentionally kept for
  owner/root review; record what remains and why.
- `abandoned`: output was not used; record the reason and confirm there is no
  required follow-up hidden only in the worker thread.
- `handoff-pending`: the worker's checkout or thread is the intended next
  integration surface; record the pending action and owner decision needed.

Do not remove or archive a worker before reading its latest state. Do not remove
a helper worktree that contains unreviewed tracked work, unreported artifacts,
or the only copy of evidence needed for a gate. Once all useful output is
integrated or intentionally abandoned, remove or archive helper surfaces when
that cleanup is safe and available, or record why they remain.

## Authorization Modes

- `inspect`: read-only investigation, triage, diagnosis, or plan.
- `implement`: local code/docs changes plus focused validation, but no push,
  PR, merge, release, or external mutation.
- `push-pr`: commit, push, or draft PR creation when the user explicitly
  authorized publication.
- `ci-rerun-fix`: rerun checks or push targeted fixes for a known PR or branch
  when the user authorized CI follow-up.
- `merge-close`: merge, close, label, comment, or otherwise mutate GitHub state
  only with explicit owner approval.
- `release`: tag, release, publish, or package promotion only with explicit
  owner approval and the release gate satisfied.

## Prompt Template

```text
You are a Codex worker for the <portfolio> portfolio.

Scope:
- Repository: <repo path or owner/repo>
- Workstream: <short name>
- Objective: <one concrete outcome>
- Authorization mode: <inspect|implement|push-pr|ci-rerun-fix|merge-close|release>
- Allowed paths or surfaces: <paths, branches, PRs, issues, or commands>
- Forbidden actions: no subdelegation, no ledger edits, no unrelated cleanup,
  no worker/thread/chat management, no publish/merge/release unless this mode
  explicitly permits it.

Context:
- Owner request: <summary>
- Current ledger status: <summary>
- Known blockers or assumptions: <bullets>
- Required gates: <gate names from references/gates.md>
- Required proof: <tests, live proof, CI, autoreview, docs, screenshots>
- Known root-integrated changes since assignment: <bullets or none>

Execution:
1. Inspect the current state before editing.
2. Preserve unrelated worktree changes.
3. If editing, run focused validation.
4. Run or request autoreview when required by the gate.
5. Stop and report if blocked by access, ambiguous owner intent, unsafe state,
   missing dependency, worker-reported risk, or a gate that cannot be
   satisfied.

Final report:
- Status: done|blocked|needs-owner|ready-for-review
- Changes: files or external objects touched
- Validation: commands run and outcomes
- Gate status: pass/fail/not-applicable with evidence
- Generated artifacts: ignored local files or directories created, or none
- Risks: residual risks, dependency audit warnings, security findings,
  untested adapters, setup gaps, or test gaps
- Next: exact owner or orchestrator action
```

## Heartbeat Checks

When heartbeat monitoring is requested, poll workers at the requested interval
or a conservative default such as five minutes. Read the worker state first
when the worker surface supports it, then ask for status, blocker, validation,
risks, and expected next checkpoint only if the latest state is stale or
insufficient. Do not interrupt a worker with new scope unless the user changed
priority, a contract mismatch was discovered, or a gate failed.
