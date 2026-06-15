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
