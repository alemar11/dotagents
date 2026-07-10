# Codex Tool Surface Refresh

Use this playbook when explicitly asked to check whether Codex changed how
subagents are spawned, subagents are inspected or closed, or Codex App worker
threads are created and managed. This task exists primarily to keep
`skills/codex-orchestrator/` current.

## Scope

Review only Codex worker and thread orchestration surfaces:

- subagent creation, roles, model inheritance, wait/send/resume/close lifecycle,
  and UI visibility;
- Codex App thread creation, project/worktree targets, thread read/write,
  title, archive, handoff, fork, pin, and listing behavior;
- CLI `/agent` equivalents when available;
- `codex-orchestrator` runtime requirements, worker-surface selection,
  worker prompt templates, and ledger fields that depend on those surfaces.

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
3. Check whether current docs still answer these questions precisely:
   - What creates a subagent?
   - What creates a separate visible Codex App thread?
   - Which surfaces are visible to the user, and where?
   - Which lifecycle actions can the root orchestrator perform?
   - What should happen when a logical tool name is unavailable or renamed?
   - Which worker type should be selected by default under current owner intent?
4. Update `codex-orchestrator` only when the live tool surface materially
   differs from the documented contract. Material differences include renamed
   tools, changed arguments, new required lifecycle calls, new visibility
   behavior, removed capabilities, or newly exposed safer primitives.
5. If no material drift exists, return `PASS (NOOP)` and include the discovered
   current callable names in the report.
6. Finish with `release-checklist.md` for touched files.

## Guardrails

- Treat Codex tool availability as runtime-dependent. Do not claim a tool is
  globally unavailable just because it is missing in one thread.
- Prefer logical operation names in runtime skills, but record actual callable
  names when they differ.
- Keep visible Codex App threads distinct from subagents unless the current
  runtime explicitly exposes the same surface as both.
- Do not create visible Codex App threads merely to inspect the tool schema.
  Use a bounded internal subagent for live validation only when the active
  runtime policy permits it and the validation adds material evidence. Ask
  before delegation only when runtime policy requires it or when creating a
  visible user-owned Codex App thread.
- Keep runtime skills self-contained; do not mention this Maintainer playbook
  from runtime `SKILL.md` files.

## Reporting

Report:

- Scope checked
- Tool registry queries or commands used
- Current subagent creation and lifecycle surface
- Current Codex App thread creation and lifecycle surface
- `codex-orchestrator` files changed, or `PASS (NOOP)`
- Any runtime-dependent uncertainty that should be rechecked in Codex App or CLI
