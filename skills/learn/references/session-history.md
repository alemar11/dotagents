<!-- Learn-owned durable repository-context reference. -->

# Session History

Use this reference only during existing-project bootstrap, when recent local
agent session history can help seed project context for an already-used
repository.

## Sources and scope

Read the session specified by the user, or the current conversation when none
is named. This may include searching local session logs available in the
current environment; do not assume a particular agent, storage path, or format.

When broader history is needed to seed existing-project context, limit the
default search to the last 14 days and at most the 10 most recent matching
sessions, including discoverable archives. An explicit session selection
overrides that default window.

If session history is missing, unreadable, encrypted beyond useful summaries, or
does not contain matching repo evidence, continue with repo-only evidence and
report the limitation.

Use only read-only history surfaces available in the current runtime. Do not
require a bundled resolver or treat inability to inspect local session files as
a bootstrap blocker.

## Matching sessions to the repo

Resolve the current repository's git root first. Match sessions using available
evidence of their working directory, repository identity, or concrete file
paths under that root. Use the source's actual format rather than requiring
particular metadata fields.

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
