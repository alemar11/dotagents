# Session History

Use this reference only during existing-project bootstrap, when recent local
agent session history can help seed project context for an already-used
repository.

## Default window

- When reading Codex history, use local sessions under `~/.codex/sessions`.
- Search the last 14 days from the current date.
- Include archived session history only when it is discoverable in that same
  date window.
- Keep at most the 10 most recent matching sessions.

If session history is missing, unreadable, encrypted beyond useful summaries, or
does not contain matching repo evidence, continue with repo-only evidence and
report the limitation.

Use only read-only history surfaces available in the current runtime. Do not
require a bundled resolver or treat inability to inspect local session files as
a bootstrap blocker.

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

Summarize evidence; do not copy raw transcript text into project context.

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

Use `references/domain-modeling.md` for the actual `CONTEXT.md`, domain-doc,
and ADR content.

- Put shared stable terminology, boundaries, workflows, rules, and open
  questions in root `CONTEXT.md`; put only a selected scope's delta in its
  scoped `CONTEXT.md` after following root routing.
- Create ADRs under `project-context/adr/` only for load-bearing accepted
  decisions that future agents or maintainers would otherwise reopen.
- Cite evidence briefly with paths, issue numbers, commit hashes, or session
  dates when available.
- If evidence conflicts, do not choose silently. Record the conflict as an open
  question or ask the user.
