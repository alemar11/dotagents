---
name: pi-delegate
description: Delegate coding implementation to Pi with the fixed GLM-5.2 model while Codex remains the controller. Use only when the user explicitly invokes $pi-delegate.
---

# Pi Delegate

## Goal

Offload one bounded coding task to a local Pi session while Codex retains
control of scope, permissions, verification, and closeout.

Pi may edit files and run project commands. Its response is worker evidence,
not proof that the task is complete.

## Trigger Rules

- Use only when the user explicitly invokes `$pi-delegate`.
- Never invoke this skill implicitly for ordinary coding, debugging, review, or
  delegation requests.
- Do not use it for advisory-only work when Codex can answer directly without a
  coding worker.

## Fixed Runtime Contract

- Shipped command: `scripts/pi-delegate`
- Required runtime: `python3` and the `pi` executable
- Provider and model: always `zai-coding-cn/glm-5.2`
- Thinking levels: `off`, `minimal`, `low`, `medium`, `high`, `xhigh`, or
  `max`, selected by the user
- Default thinking level: `medium`
- Working directory: the caller's current project or worktree
- Pi project resources: ignored through `--no-approve`; applicable
  `AGENTS.md` context still loads
- Session behavior: persistent, with an explicit session ID returned by the
  command

Never pass a different provider, model, API key, or Pi configuration directory.

Read [references/cli-contract.md](references/cli-contract.md) before invoking
the launcher or diagnosing a launcher failure. It owns the command inputs, JSON
envelopes, and exit codes.

## Workflow

### 1. Keep the controller in the current project

Resolve the absolute path to this skill's shipped `scripts/pi-delegate`
artifact, but execute it with the current project or worktree as the working
directory. Do not change into the skill directory before launching Pi.

Confirm the user's requested scope and delivery authority. Editing files and
running local project commands are allowed. Commit, push, pull-request,
deployment, publication, and other external mutations remain prohibited unless
the user separately authorizes them.

### 2. Resolve the thinking level

Honor an explicit user selection from `off`, `minimal`, `low`, `medium`,
`high`, `xhigh`, or `max`. Use `medium` when the user does not select a level.
Do not replace the user's choice based on task complexity, and do not ask about
reasoning effort when the default is sufficient.

Record the canonical value as `thinking_level`.

Pi and the fixed model own support and clamping. In Pi 0.82.1,
`zai-coding-cn/glm-5.2` treats `minimal` as unsupported and clamps it to `low`,
maps `low`, `medium`, and `high` to the provider's `high` reasoning effort,
and clamps `xhigh` to `max`. Pass the user's canonical selection unchanged so
future Pi catalogs can honor it without changing this skill.

### 3. Run the non-mutating preflight

Run:

```bash
<skill-root>/scripts/pi-delegate --json doctor
```

The doctor checks `python3`, the `pi` executable, the installed Pi version, and
the exact fixed model without sending a model request.

If Pi is missing, stop and give the installation command returned by the
doctor. Do not install Pi automatically. If the model is unavailable, stop and
ask the user to configure the ZAI Coding Plan China provider; never fall back to
another provider or model.

### 4. Build one bounded worker task

Give Pi a self-contained task containing:

- the concrete implementation goal,
- in-scope files or components,
- relevant repository evidence and constraints,
- permission to edit files and run local commands,
- required validation,
- explicit prohibitions on commits, pushes, pull requests, deployments, and
  unrelated changes,
- a request to report changed files, commands run, results, and remaining
  risks.

Do not forward unrelated conversation history or secrets.

### 5. Launch or continue the Pi session

Start a session:

```bash
<skill-root>/scripts/pi-delegate --json run \
  --name "<short task name>" \
  "<bounded worker task>"
```

Omit `--thinking-level` for the `medium` default. When the user selects a
different level, add `--thinking-level <selected-level>`.

For a long prompt, use `--task-file <path>` or pipe the prompt on stdin instead
of constructing unsafe shell interpolation.

Continue the same worker when a correction or follow-up belongs to the same
task:

```bash
<skill-root>/scripts/pi-delegate --json run \
  --thinking-level <selected-level> \
  --session-id <returned-session-id> \
  "<follow-up task>"
```

Do not launch overlapping write-enabled Pi sessions in the same checkout.

### 6. Verify independently

After Pi exits:

1. Inspect repository status and the complete diff.
2. Check that changes remain inside the delegated scope.
3. Run or re-run validation proportionate to the change.
4. Correct issues directly or continue the same Pi session with a bounded
   follow-up.
5. Report what Pi changed, what Codex independently verified, and any remaining
   uncertainty.

Never claim success from Pi's final response alone.

## Safety

- Pi has no built-in sandbox and runs with the permissions granted to its
  process. Use it only in a trusted project.
- The launcher never uses a shell to construct the Pi command.
- The launcher never installs Pi, stores credentials, or changes Pi
  configuration.
- Do not expose credentials in task text or output.
- Abort on a missing executable, unavailable fixed model, invalid session ID,
  or nonzero Pi exit.

## CLI Maintenance

Normal runtime execution uses `scripts/pi-delegate`. The implementation is the
direct standard-library Python artifact at that path; there is no maintenance
project or generated build output.

`scripts/pi-delegate --version` is the single CLI version source of truth.
Shipped behavior changes follow semantic versioning: major for breaking command
or JSON contracts, minor for backward-compatible capabilities, and patch for
backward-compatible fixes. Re-run `--help`, `--version`, `--json doctor`, and
the tests under `tests/` after every CLI change.
