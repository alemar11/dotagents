---
name: focus
description: Create a focused new Codex task from a compact handoff of the latest substantive discussion.
---

# Focus

## Goal

Make an active discussion easy to resume later without copying the caller's
complete history. Create a new task from a compact handoff, give it a concise
title with one relevant leading emoji, and leave the calling task unchanged.

## Trigger Rules

- Use only when the user explicitly invokes `$focus`.
- Do not trigger for ordinary discussion, summarization, planning, or task
  management requests.
- Invoking `$focus` explicitly authorizes creating one focused new task.
  Do not ask for an additional creation confirmation.

## Workflow

1. Infer the current focus from the conversation already available. Prefer, in
   order:
   - the latest unresolved objective;
   - the latest accepted direction or decision;
   - the immediate next outcome;
   - the current blocker, when resolving it is the active work.
2. Write a title as `<emoji> <specific outcome>`:
   - start with exactly one context-relevant emoji;
   - use 4 to 8 words when practical;
   - describe the outcome rather than the conversation;
   - retain a distinguishing product, component, or constraint when it helps
     the task remain recognizable later;
   - avoid generic wording such as `Work on task`, `Help with code`, or
     `Continue discussion`.
3. Write a compact handoff of at most 200 words containing only applicable
   sections:
   - `Objective`
   - `Accepted decisions`
   - `Constraints`
   - `Current blocker`
   - `Next action`
4. End the handoff prompt with:
   `Do not begin work yet. Acknowledge this focus briefly, then wait for the
   user's follow-up.`
5. Resolve the new task target:
   - For repository-backed work, call `list_projects` and match the current
     workspace root to exactly one saved project. Create the task in that
     project with `environment.type=local` so it retains the intended checkout
     without creating a worktree.
   - For work with no repository context, use a `projectless` target.
   - If repository-backed work has no unique saved-project match, stop and
     report the mismatch. Do not create a projectless substitute.
6. Before any task mutation, inspect the live declarations for `list_projects`,
   `create_thread`, `set_thread_title`, and the `read_thread` or `list_threads`
   operation that will provide title readback. Pass only fields exposed by
   those declarations. If a required operation or argument is unavailable or
   unverifiable, stop before creation and report `unsupported-runtime`.
7. Call `create_thread` with the compact handoff as its prompt. Omit `model` and
   `thinking` so the user's configured defaults apply. When the inspected
   declaration exposes `title`, pass the chosen title in that creation call;
   otherwise omit it and use the verified fallback below. Do not rely on a
   creation response or prompt text as visible-title evidence. If creation
   returns only a client-side identifier, report the setup as pending and do
   not attempt to title the task.
8. When creation returns a real `threadId`, independently read or list the
   created task. If its observed title exactly matches the requested title,
   keep that creation-time result and do not rename the task. If the title is
   missing or different, call `set_thread_title` exactly once with that ID and
   the chosen title, plus only fields exposed by its live declaration, then
   independently read or list the task again. Never rename the calling task.
9. Treat missing final readback as `title-setup-failed` and a different or
   normalized final title as `title-drift`; preserve the created task and
   report the partial result. Declare completion only after the exact title is
   observed, then return the observed title and the App's native created-task
   link or card.

If several topics remain active, choose the most recently discussed unresolved
outcome. Do not copy the full conversation, browse, inspect repository files,
or ask a clarifying question before creation.

## Boundaries

- Creating and titling one focused task are the skill's only mutations.
- Leave the calling task and its title unchanged.
- Do not fork the calling task; a fork carries its completed history instead of
  the compact handoff this skill promises.
- Do not send a second follow-up message to the new task after creation.
- Treat the title as display metadata only. Never use it as task identity,
  durable state, a branch name, or a recovery key.
- If creation, title initialization, or independent title verification fails,
  report the partial result accurately and do not claim the intended final
  state.
