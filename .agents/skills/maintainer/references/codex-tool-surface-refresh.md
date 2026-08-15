# Codex Tool Surface Refresh

Use this playbook when explicitly asked to check whether Codex changed how
subagents are spawned or Codex App tasks are created and managed. This task
keeps `$se:implement` current.

## Scope

Review only Codex worker and thread orchestration surfaces:

- subagent creation, roles, model inheritance, wait/message/follow-up/
  interruption lifecycle, listing, and UI visibility;
- Codex App project discovery, task creation, project/worktree targets, task
  read/write/wait, title, archive, handoff status, fork, pin, and listing
  behavior;
   - SE Implement task requirements and managed-worktree behavior.

Do not use this task to redesign generic orchestration behavior, add new
workers to a live task, or update unrelated skills.

## Workflow

1. Inspect the currently exposed capability surface before editing:
   - discover internal subagent creation, observation, waiting, messaging,
     follow-up, interruption, and listing capabilities;
   - discover visible Codex App project and task creation, observation,
     waiting, messaging, title, archive, handoff, fork, pin, and listing
     capabilities;
   - record exact live callable names only as time-bound maintenance evidence,
     never as runtime-skill instructions;
   - note whether each capability belongs to internal subagents, visible Codex
     App tasks, or is unavailable in the current runtime.
2. Compare the discovered surface against:
   - `plugins/se/skills/implement/SKILL.md`;
   - `plugins/se/skills/implement/references/orchestration.md`;
   - `plugins/se/skills/implement/references/task-profile.md`;
   - `plugins/se/skills/implement/references/run-state.md`;
   - `plugins/se/skills/implement/references/review-delivery.md` only when tool
     changes affect authorization, proof, or closeout behavior.
3. Check whether current docs still answer these questions precisely:
   - What creates a subagent?
   - What creates a separate visible Codex App thread?
   - Which surfaces are visible to the user, and where?
   - Which lifecycle actions can the root orchestrator perform?
   - What should happen when a logical tool name is unavailable or renamed?
   - Does the skill remain confined to visible App tasks and App-managed
     worktrees?
4. Update the App contract when the live capability surface materially differs
   from the documented semantic contract. Material differences include changed
   lifecycle outcomes, authorization or visibility behavior, missing required
   capabilities, or newly available safer primitives.
5. If no material drift exists, return `result=pass` and
   `change_state=no-change`, and include the discovered
   current callable names in the report.
6. Finish with `release-checklist.md` for touched files.

## Guardrails

- Treat Codex tool availability as runtime-dependent. Do not claim a tool is
  globally unavailable just because it is missing in one thread.
- Describe Codex interactions in runtime skills only through required outcomes,
  topology, authorization, lifecycle, verification, and recovery. Record
  actual callable names only in the maintenance report as live evidence.
- Keep visible Codex App tasks distinct from subagents unless the current
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
- Any runtime-dependent uncertainty that should be rechecked in Codex App

Add these items to the common final report owned by `release-checklist.md`.
