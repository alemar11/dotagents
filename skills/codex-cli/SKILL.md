---
name: codex-cli
description: Explicitly launch one isolated Codex CLI task with a complete caller-provided prompt, selectable GPT-5.6 model, and model-compatible reasoning chosen before execution.
---

# Codex CLI

## Scope

Use this skill only when the user explicitly asks to delegate one task to a
separate Codex CLI execution. The skill is a generic launcher: it does not
own review semantics, implementation workflow, Git delivery, or tracker
authority.

The shipped entrypoint is scripts/codex-cli. It starts one ephemeral codex exec
process, passes the complete prompt through unchanged, and returns the
delegated result. The default model is gpt-5.6-sol; the caller may explicitly
select gpt-5.6-terra or gpt-5.6-luna.

This is a Codex-dependent skill. It requires Python 3.10 or newer, a local
Codex CLI, Codex authentication and engine access, and a usable working
directory. The
delegated execution is a separate networked Codex run: read-only is the
default sandbox, not an offline guarantee.

## Prompt and model contract

The prompt is caller-owned and complete. Do not silently prepend a review,
implementation, or generic task template. Put all instructions, repository
context, evidence, expected output, and success criteria in the prompt sent
to scripts/codex-cli through --prompt, --prompt-file, or stdin.

Resolve caller selection authority before classifying the task:

- If neither model nor reasoning is specified, use `sol` with `medium`.
- If only a model is specified, use that model's default reasoning: Sol
  `medium`, Terra `high`, or Luna `max`.
- If only reasoning is specified, keep the default model `sol` and use that
  explicit reasoning value; do not invent a task profile for the direct
  override.
- If both are specified, use the requested pair only when the effort is
  supported by that model.
- If the caller explicitly grants carte blanche (for example, “choose the
  model and reasoning yourself”), choose both from references/model-policy.md
  and report the selected pair. Do not infer carte blanche from omission.

Before launching the CLI:

1. Read references/model-policy.md.
2. Resolve the model and reasoning according to the caller-selection rules
   above. Use model=terra or model=luna only when explicitly selected or when
   the caller grants carte blanche.
3. If the caller explicitly grants carte blanche, classify the task as
   routine, standard, complex, risky, critical, or extreme using the prompt
   and repository evidence. Otherwise preserve the already resolved model and
   reasoning pair; do not use an internal classification to silently promote
   the effort. When an explicit reasoning override has no caller-supplied task
   profile, report `task_profile=null` rather than claiming the model default.
4. Resolve the model-compatible reasoning effort locally, before launching
   Codex. Do not ask the delegated Codex process to choose its own effort.
5. Pass the resolved --model, --task-profile, and, when needed, explicit
   --reasoning-effort to the shipped CLI. The CLI validates the final model
   and effort pairing and reports the effective values.

Use the smallest effort expected to satisfy the task. Use ultra for Sol or
Terra only when the task has extreme uncertainty, broad independent
workstreams, or quality-critical consequences. Luna has no ultra profile; an
extreme task automatically resolves to its highest supported max effort. Do
not select ultra merely because a change is large.

## Safety and execution boundaries

- Default to --sandbox read-only and --ask-for-approval never.
- Select workspace-write only when the user explicitly authorizes the
  delegated task to modify files. Treat danger-full-access as requiring an
  equally explicit authorization and a concrete reason.
- Do not infer Git, merge, push, deployment, tracker, or external-account
  authority from the prompt.
- Do not pass secrets, credentials, cookies, or unrelated private data unless
  the user has explicitly placed them in scope.
- The delegated process does not modify the caller's files unless a
  write-capable sandbox was explicitly selected. The launcher-owned `--output`
  path is a separate explicit result write. The launcher canonicalizes and
  pins the destination directory before launching delegated code, rejects a
  final symlink, checks directory identity before writing, and performs the
  replacement relative to the pinned descriptor. A replaced parent fails
  closed. The write happens only after a successful non-empty result. The
  launcher does not commit, push, merge, publish, or retry a failed task.
- A delegated task is one-shot. Persistent or resumable Codex App tasks are a
  different orchestration surface.

## Review use

This skill can launch a review when the caller provides the complete review
prompt and change bundle. The caller owns the review instructions, target
selection, output schema, finding vocabulary, and fix loop. For a simple
interactive diff review, the native codex review command remains the
specialized path; this skill is useful when a review must use a custom prompt
or be composed inside another workflow.

Example:

    skills/codex-cli/scripts/codex-cli \
      --model terra \
      --task-profile risky \
      --prompt-file /absolute/path/full-review-prompt.md \
      --output-schema /absolute/path/review-schema.json

The prompt file in this example must already contain the entire review
instruction and evidence bundle. The launcher does not add hidden review
instructions.

## Runtime surface

Run the shipped artifact from the skill root:

    scripts/codex-cli --version
    scripts/codex-cli --json doctor
    scripts/codex-cli --model sol --task-profile standard --prompt-file /path/task.md

Useful options:

- --model sol|terra|luna: select the model family; defaults to sol. With no
  reasoning override, model-only selection uses Sol `medium`, Terra `high`, or
  Luna `max`.
- --task-profile routine|standard|complex|risky|critical|extreme: the
  pre-launch task classification used to resolve reasoning. It is an internal
  skill decision; an explicit --reasoning-effort takes precedence. If omitted
  with `--reasoning-effort auto`, defaults are Sol `standard`→`medium`, Terra
  `complex`→`high`, and Luna `critical`→`max`. If an explicit reasoning effort
  is supplied without this option, the result reports no task profile rather
  than pairing the direct override with an unrelated default. For Luna,
  standard through critical stay at max; routine is the automatic scale-back
  profile and must only be chosen when the savings are worth it.
- --reasoning-effort auto|low|medium|high|xhigh|max|ultra: normally leave
  this as auto; the skill resolves it from the task profile. Direct CLI
  overrides are validated against the selected model and remain separate from
  task-profile classification.
- --prompt, --prompt-file, or stdin: supply the complete prompt.
- --cd: select the delegated working directory; it defaults to the current
  directory.
- --sandbox: choose read-only, workspace-write, or danger-full-access; defaults
  to read-only.
- --output-schema: pass a JSON Schema to the Codex CLI for the final answer.
- --output: explicitly write a successful non-empty delegated final answer to
  a caller-selected launcher-owned file; its canonical destination directory
  is pinned before delegated execution, it is independent of the delegated
  sandbox, and it is not written after a failed or empty run.
- --dry-run: resolve the model, reasoning, prompt, and command without
  launching Codex.
- --json: emit one machine-readable launcher result; progress stays on stderr.

--json doctor is launcher-level read-only: it does not intentionally write
configuration or authentication state, but the underlying Codex startup may
perform host-level checks or maintenance attempts. Any version-check stderr is
returned in the doctor result. A successful task reports the selected model
alias and ID, requested and effective reasoning effort, task profile, sandbox,
prompt size, exit status, and final answer. It does not claim that the remote
model is available until the Codex process confirms it.

## CLI Maintenance

- Keep normal runtime execution on scripts/codex-cli.
- Keep the CLI version source of truth in scripts/codex-cli.
- The implementation is standard-library-only Python; do not introduce a
  projects/codex-cli/ tree unless the script grows beyond a small
  dependency-free launcher.
- Re-verify scripts/codex-cli --help, --version, --json doctor, and a safe
  dry-run fixture after runtime changes.
- The CLI follows semver: major for breaking invocation or JSON-contract
  changes, minor for compatible capabilities, and patch for fixes.
