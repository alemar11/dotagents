# Session History

Use this reference only during existing-project bootstrap, when recent Codex
history can help seed project memory for an already-used repository.

## Default window

- Read local Codex sessions under `~/.codex/sessions`.
- Search the last 14 days from the current date.
- Include archived session history only when it is discoverable in that same
  date window.
- Keep at most the 10 most recent matching sessions.

If session history is missing, unreadable, encrypted beyond useful summaries, or
does not contain matching repo evidence, continue with repo-only evidence and
report the limitation.

## Matching sessions to the repo

Resolve the current repository's git root first. A session matches when any of
these point at the same git root or a path under it:

- `session_meta.cwd`
- `turn_context.cwd`
- tool-call arguments such as `workdir` or `cwd`
- absolute paths mentioned under the repo root

Ignore broad parent directories such as `~/Developer` unless the session also
contains a concrete path under the current repo.

## What to extract

Summarize evidence; do not copy raw transcript text into project memory.

Useful signals:

- final assistant summaries that describe work completed or decisions accepted
- user messages that explicitly accept a rule, term, architecture decision, or
  workflow
- command evidence such as tests, builds, migrations, commits, or issue updates
- file paths that show which subsystem the decision applied to

Reject weak signals:

- tentative plans
- rejected options
- brainstorming that did not land
- raw logs or stack traces unless summarized into an accepted rule
- credentials, tokens, customer data, private message content, or other secrets

## Writing from session evidence

Use `$domain-modeling` for the actual `CONTEXT.md` and ADR shape.

- Put stable terminology, boundaries, workflows, rules, and open questions in
  `CONTEXT.md`.
- Create ADRs under `project-memory/adr/` only for load-bearing accepted
  decisions that future agents or maintainers would otherwise reopen.
- Cite evidence briefly with paths, issue numbers, commit hashes, or session
  dates when available.
- If evidence conflicts, do not choose silently. Record the conflict as an open
  question or ask the user.
