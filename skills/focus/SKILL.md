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
5. Resolve the new task's destination semantically:
   - For repository-backed work, call `list_projects`, match the current
     workspace root and host to exactly one saved project, and require the new
     task to use that project directly without creating a worktree.
   - For work with no repository context, require a standalone task outside a
     saved project only when the live creation tool supports that outcome.
   - If repository-backed work has no unique saved-project match, stop and
     report the mismatch. Do not substitute another destination.
6. Before any task mutation, inspect the live declarations for `list_projects`,
   `create_thread`, and the `read_thread` or `list_threads` operation that will
   verify the created task's identity, project, host, environment, and state.
   Inspect `set_thread_title` when available so it can be used once as a title
   fallback. The model calls these live tools directly and passes only fields
   exposed by their current declarations; this skill does not reproduce their
   signatures or target schema. Stop before creation only when a structural
   operation or required outcome is unavailable or unverifiable, and report
   `unsupported-runtime`.
7. Call `create_thread` directly once with the compact handoff. Let the user's
   configured model and reasoning defaults apply. Pass the chosen title in the
   creation call only when the inspected declaration supports it; otherwise
   continue to the verified fallback below when available. Treat the immediate
   response only as a receipt, never as visible-title or structural proof. A
   client-side setup identifier is not a real task ID and must not be used with
   task-ID operations.
8. When creation returns a real `threadId`, independently read or list the
   created task and verify its identity, exact project and host, direct local
   environment, and operational state. Compare the observed title separately.
   If it is missing or different and the live declaration exposes
   `set_thread_title`, call that tool directly at most once, then read or list
   the task again. If the setter or title readback is unavailable, retain the
   structurally verified task and record `title-unverified`. Never rename the
   calling task and never retry a title mutation.
9. A rejection, timeout, transport error, client-side setup identifier, or
   uncertain response requires bounded reconciliation through the live App
   read/list surface before any retry. Reuse the exact task if it exists; retry
   creation only after authoritative evidence proves that no task was created.
   If reconciliation remains uncertain, report the partial result and do not
   create a replacement. Treat an unavailable or missing title as
   `title-unverified` and a different or normalized title as `title-drift`.
   Preserve the real task and return the warning, observed title, and App's
   native created-task link or card. Require an exact title only when the user
   explicitly requested one; otherwise title warnings must not block completion.

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
- If structural creation or independent identity verification fails, report
  the partial result accurately and do not claim the task is ready. Title
  initialization and title readback are best-effort metadata: retain the
  warning in the result without blocking the structurally verified task.
