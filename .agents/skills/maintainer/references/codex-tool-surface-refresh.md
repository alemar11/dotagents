# Codex Tool Surface Refresh

Use this playbook when explicitly asked to check whether Codex changed how
subagents are spawned, Codex App tasks are created and managed, or Codex CLI
sessions are supervised. This task keeps the App and CLI orchestrator adapters
current without merging their runtime surfaces.

## Scope

Review only Codex worker and thread orchestration surfaces:

- subagent creation, roles, model inheritance, wait/send/resume/close lifecycle,
  and UI visibility;
- Codex App task creation, project/worktree targets, task read/write,
  title, archive, handoff, fork, pin, and listing behavior;
- CLI subagents plus `codex exec` start/resume/structured-output behavior;
- `codex-orchestrator` App task requirements and managed-worktree adapter;
- `codex-cli-orchestrator` tmux/process, session-id, artifact, and manual
  worktree adapter.

Do not use this task to redesign generic orchestration behavior, add new
workers to a live task, or update unrelated skills.

## Workflow

1. Inspect the currently exposed tool surface before editing:
   - search the available tool registry for `spawn_agent`, `wait_agent`,
     `send_input`, `resume_agent`, `close_agent`, `create_thread`,
     `read_thread`, `send_message_to_thread`, `set_thread_title`,
     `set_thread_archived`, `handoff_thread`, `fork_thread`, `list_threads`,
     and `set_thread_pinned`;
   - record the exact callable namespaces and names;
   - note whether each surface is a subagent surface, visible Codex App thread
     surface, CLI-only equivalent, or unavailable in the current runtime.
2. Compare the discovered surface against:
   - `skills/codex-orchestrator/SKILL.md`;
   - `skills/codex-orchestrator/references/worker.md`;
   - `skills/codex-orchestrator/references/ledger.md`;
   - `skills/codex-orchestrator/references/gates.md` only when tool changes
     affect authorization, proof, or closeout behavior.
   - `skills/codex-cli-orchestrator/SKILL.md` and
     `skills/codex-cli-orchestrator/references/runtime.md` for CLI changes.
3. Check whether current docs still answer these questions precisely:
   - What creates a subagent?
   - What creates a separate visible Codex App thread?
   - Which surfaces are visible to the user, and where?
   - Which lifecycle actions can the root orchestrator perform?
   - What should happen when a logical tool name is unavailable or renamed?
   - Does each public skill remain confined to its own runtime adapter?
4. Update only the affected adapter when the live tool surface materially
   differs from the documented contract. Material differences include renamed
   tools, changed arguments, new required lifecycle calls, new visibility
   behavior, removed capabilities, or newly exposed safer primitives.
5. If no material drift exists, return `result=pass` and
   `change_state=no-change`, and include the discovered
   current callable names in the report.
6. Finish with `release-checklist.md` for touched files.

## Guardrails

- Treat Codex tool availability as runtime-dependent. Do not claim a tool is
  globally unavailable just because it is missing in one thread.
- Prefer logical operation names in runtime skills, but record actual callable
  names when they differ.
- Keep visible Codex App tasks distinct from subagents and CLI sessions unless the current
  runtime explicitly exposes the same surface as both.
- Do not create visible Codex App threads merely to inspect the tool schema.
  Use a bounded internal subagent for live validation only when the active
  runtime policy permits it and the validation adds material evidence. Ask
  before delegation only when runtime policy requires it or when creating a
  visible user-owned Codex App thread.
- Keep runtime skills self-contained; do not mention this Maintainer playbook
  from runtime `SKILL.md` files.

## Branch Report Additions

- Current subagent creation and lifecycle surface
- Current Codex App task creation and lifecycle surface
- Current Codex CLI exec/resume and tmux supervision surface
- Any runtime-dependent uncertainty that should be rechecked in Codex App or CLI

Add these items to the common final report owned by `release-checklist.md`.
