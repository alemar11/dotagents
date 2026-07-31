---
name: pi-delegate
description: Delegate and monitor bounded research, investigation, analysis, review, or implementation tasks in Pi with the fixed GLM-5.2 model while Codex remains the controller. Use only when the user explicitly invokes $pi-delegate.
---

# Pi Delegate

## Goal

Give Codex a low-ceremony way to offload one bounded task to Pi with
`zai-coding-cn/glm-5.2`, watch its progress, and independently verify the
result.

Pi is the worker. Codex remains responsible for scope, permissions, review,
validation, and closeout. Pi's response is worker evidence, not proof that the
task is complete.

## Trigger

- Use only when the user explicitly invokes `$pi-delegate`.
- Do not ask for choices already covered by defaults.
- Accept bounded research, investigation, analysis, review, implementation, and
  mixed tasks. Whether Codex could do the work directly is not a reason to
  refuse an explicit delegation.

## Default Contract

- Shipped command: `scripts/pi-delegate`
- Runtime: `python3` plus the local `pi` executable
- Model: always `zai-coding-cn/glm-5.2`; never fall back
- Thinking level: `medium` unless the user explicitly selects another canonical
  Pi level
- Working directory: the caller's current project or worktree
- Permissions: never broader than the user's request
- Project trust: `--approve`, so project Pi resources and skills may load
- Monitoring: sanitized progress plus 30-second heartbeats on stderr
- Timeout: 30 minutes
- Final output: one controller-owned result on stdout

The launcher performs its readiness checks automatically. Do not run a separate
doctor step or ask the user about thinking level, timeout, or session selection
on the normal path.

When a run returns `doctor.checks[].code=state_access_denied`, treat it as a
host permission blocker, not as a missing model or a task failure. Request
narrow, host-approved elevated access for Pi's local state directory and retry
the exact same launcher invocation, task file, session selection, model, and
thinking level after approval. Do not use `sudo`, change directory permissions,
redirect Pi state to an arbitrary temporary directory, or fall back to another
model. If the host cannot provide an approval path or denies it, stop with the
sanitized blocker and remediation; do not create a replacement session.

Read [references/cli-contract.md](references/cli-contract.md) only when changing
defaults, resuming a worker, running concurrent delegations, or diagnosing a
launcher failure.

## Workflow

### 1. Build the worker brief

Use the current task context to write one self-contained brief with:

- the concrete goal and intended scope,
- relevant repository constraints,
- the granted authority: keep research, investigation, analysis, and review
  read-only unless the user also requested changes; allow the read-only local
  commands and public-source access needed for evidence gathering, and permit
  edits or mutating local commands only for implementation work within scope,
- the sources, evidence, or validation the worker must return,
- no commits, pushes, pull requests, deployments, or unrelated changes,
- a final report covering sources and findings, or files changed and commands
  run, plus results, uncertainty, and risks.

Include relevant context, but do not forward unrelated conversation history,
credentials, or secrets. Do not stop to ask about details already clear from
the repository or user request.

Use a UTF-8 task file for multiline, quoted, skill-invoking, or shell-sensitive
briefs. The launcher reads it and sends the brief to Pi over stdin, so task
text does not enter Pi's process arguments. This is an internal transport
detail, not a user-facing ceremony.

### 2. Launch and monitor

Run from the current project or worktree:

```bash
<skill-root>/scripts/pi-delegate --json run \
  --progress \
  --name "<short task name>" \
  --task-file <absolute-task-file>
```

Keep the process handle and read the sanitized stderr stream until
`process_finished`. Give the user concise updates for material phase, tool,
retry, heartbeat, timeout, abort, failure, and completion transitions; do not
paste raw progress records.

The launcher suppresses raw Pi events, model text, tool arguments, tool
results, and stderr contents. Only safe metadata and the count of suppressed
diagnostic lines are exposed.

### 3. Continue only when useful

For a bounded correction, continue the returned session with `--session-id`.
If the exact ID is unavailable and the latest Pi session in this project is the
intended worker, use `--resume-last`. Do not ask the user to choose between
these when the correct continuation is evident.

Override `--timeout` or `--thinking-level` only when the user requests it or the
task clearly cannot use the default. Concurrent read-only runs may overlap;
concurrent runs with write authority require non-conflicting writable scopes.
Distinguish them by stable `run_id`, name, project root, and resolved session
ID.

### 4. Verify independently

After every Pi process exits:

1. Confirm a terminal result: `completed`, `failed`, `timeout`, or `aborted`.
2. Inspect repository status and the complete diff, including after read-only
   tasks, to detect unintended mutations.
3. For research, investigation, analysis, or review, verify material claims
   against the cited primary evidence and confirm that the requested mutation
   boundary was preserved.
4. For implementation, attribute changes to the delegated scope, resolve
   overlap, and re-run validation proportionate to the change.
5. Fix issues directly or continue the same Pi session with a narrow follow-up.
6. Report what Pi found or changed, what Codex verified, and any remaining
   uncertainty.

Never claim success from Pi's final response alone. A timeout or cancellation
terminates Pi's complete process tree; inspect partial working-tree changes
before retrying.

## Safety

- Use only in a trusted project. `--approve` may load and execute project-local
  Pi settings, packages, prompts, skills, and extensions.
- Pi has no built-in sandbox and runs with the process's filesystem and command
  permissions. A read-only worker brief is an instruction boundary, not a
  filesystem sandbox, so Codex must check for unintended mutations.
- Commit, push, pull-request, deployment, publication, and other external
  mutations still require separate user authorization.
- The launcher never installs Pi, stores credentials, changes Pi configuration,
  constructs a shell command, or archives raw Pi events.
- Stop on a missing executable, unavailable fixed model, invalid session,
  protocol failure, timeout, abort, host kill, or nonzero Pi exit.

## CLI Maintenance

Normal runtime execution uses `scripts/pi-delegate`, a direct standard-library
Python artifact. Its `--version` output is the single CLI version source of
truth.

Shipped behavior follows semantic versioning: major for breaking command or
JSON contracts, minor for backward-compatible capabilities, and patch for
backward-compatible fixes. Re-run `--help`, `--version`, `--json doctor`, and
the tests under `tests/` after every CLI change.
