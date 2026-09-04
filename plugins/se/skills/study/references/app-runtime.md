# Study App Runtime

Read this reference only when `study_surface=app-task`. It owns App-specific
controller placement, task verification, parent monitoring, visible worker
tasks, and worker archival.

## Saved-project preflight

Resolve the invoking task's exact saved local project and owning host from
authoritative App state before requesting any Study task:

- Match the project by stable identity, exact local path, and host rather than
  by display label alone.
- Require the Study controller and every worker to run directly in that saved
  project on the same host, without an isolated checkout or worktree.
- If the invoking task is not attached to one exact saved local project, or
  the match is missing or ambiguous, stop before creation. Do not guess a
  project, create a projectless task, or switch to the CLI workflow.

## Separate Study controller

Create exactly one visible App task as the Study controller:

- Request `gpt-5.6-sol` with `medium` reasoning explicitly.
- Use the canonical requested title
  `Study: [<run-tag>] <short title>`.
- Place it directly in the resolved project and local environment.
- Supply the complete curated handoff, the fixed `run_tag`, the read-only
  boundary, the recursion prohibition, and the applicable Study protocol.
- Require its first substantive action to compose `$se:grilling` and ask the
  first interview question. Do not insert a setup-only turn before Grilling.

Treat an immediate creation response as a receipt, not proof of final task
state. Bind the controller only to a stable task identity. When the result is
uncertain, perform bounded authoritative reconciliation before any retry;
reuse an observed task and never infer identity from title, prompt preview,
run tag, or timing. A provisional setup identity is not a stable task identity
and never authorizes a duplicate.

After stable identity exists, independently establish the task's project,
host, direct local environment, operational state, and requested profile.
Observed profile drift is `settings-drift`; unavailable independent profile
evidence is `settings-unavailable`. Either fails App controller setup before
worker creation. Preserve a real task on failure and never replace it.

## Title handling

Task titles are visible metadata, never identity:

1. Request the canonical title at creation when supported.
2. Observe the stable task independently.
3. If the title is missing or different, make at most one title-correction
   request when that capability exists, then observe it once more.
4. Record `title-verified`, `title-unverified`, or `title-drift` with the
   evidence source.

A title warning does not block an otherwise verified controller or worker
unless the user explicitly required an exact visible title. Never recreate a
task or perform repeated renames to repair title drift.

## Parent monitoring and Grilling

Keep the invoking parent active after controller creation and monitor the exact
controller through bounded observations. When its Grilling state is
`awaiting-answer`, point the user to the separate visible Study task. Do not
copy the question into the parent or relay interview answers turn by turn.

The controller must remain in Grilling until the handoff is `refined`, the
user stops with `user-stopped`, or the interview is `blocked`. It creates no
workers while awaiting an answer. Relay only meaningful milestones: the first
question is ready, Grilling finished or stopped, scope and worker count were
fixed, a material blocker appeared, the first worker finished, and synthesis
finished.

Do not interpret an idle task as terminal while it is waiting for the user's
next interview answer. The parent returns Study's final Markdown report in the
invoking session only after the separate controller produces a terminal
result.

## Visible App workers

For each positive planned slot, the controller creates one visible worker task
in the same exact saved project, host, and direct local environment:

- Request `gpt-5.6-luna` with `max` reasoning explicitly.
- Use `Worker N: [<run-tag>] <short title>`, where `N` is the reserved slot
  number from 1 through 5.
- Supply the complete bounded assignment and worker protocol from
  [orchestration.md](orchestration.md).
- Verify stable identity and structural placement independently. Compare
  profile evidence when it is exposed, record any observed drift, and record
  unavailable evidence without claiming it was observed.

Use the setup and no-replacement rules in
[states.md](states.md). Do not use CLI subagents or another transport when an
App worker cannot be created or verified.

Monitor each real worker until it is `completed`, `failed`, or explicitly
`abandoned`. Capture its final memo when available; otherwise preserve the
terminal state, reason, error, and last authoritative evidence.

After terminal evidence is captured, request archival for every completed,
failed, or explicitly abandoned worker. Record the request result separately
from any independent archive-state observation. Never treat disappearance
from a recent-task view as archive proof. Keep the Study controller
unarchived as the visible summary task.

App task identity, requested and observed titles, host, project, execution
placement, task telemetry, and archival evidence belong only to the App report
branch.
