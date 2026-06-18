# Issue Tracker: GitHub

PRDs and implementation issues for this repo live as GitHub issues. Use
`$github-issues` for GitHub issue lifecycle operations.

Tracker mode: `github`
GitHub repo: infer from `git remote -v` unless this file records a specific
`<owner>/<repo>`.

## Non-Mutating Runs

If this setup is being used for a temp exercise, validation pass, rehearsal,
dry run, or any workflow where external GitHub mutation is not authorized, do
not mutate GitHub. Use local markdown for that run, or ask `$github-issues` to
return draft issue bodies and exact `gh` commands without executing them.
Record the non-mutating choice in `project-memory/agents/issue-tracker.md`.

## Conventions

Infer the repo from `git remote -v` unless this file records a specific target.
Use `$github-issues` to create, read, edit, comment on, label, type, attach, or
close GitHub issues.

Use `project-memory/agents/triage-labels.md` for type and label mappings. The
default GitHub issue types are:

- `Bug` for `bug`
- `Feature` for `feature`
- `Task` for `task`

If GitHub issue types are disabled or customized for the organization, record
the actual available values or fallback label convention in
`project-memory/agents/triage-labels.md`.

## Title Format

- PRD issue: `PRD: <Feature Name>`
- Implementation issue: `<feature-slug>: <NN> <vertical outcome>`

Use a lowercase kebab-case `<feature-slug>` derived from the PRD title. Use
two-digit ordering (`01`, `02`, `03`) for implementation issues so the global
issue list remains scannable even outside the PRD sub-issue view.

## When a skill says "publish to the issue tracker"

Use `$github-issues` to create a GitHub issue.

For feature planning:

- The PRD is a GitHub issue titled `PRD: <Feature Name>` with type `Feature`
  unless the repo maps `feature` to a different value.
- Implementation issues are GitHub sub-issues of the PRD issue with type
  `Task` unless the repo maps `task` to a different value.
- Implementation issue titles use
  `<feature-slug>: <NN> <vertical outcome>`.
- Each implementation issue body must also include `Source PRD: #<number>` for
  searchability and backlinks.

For triage:

- Existing bug reports should use the mapped `bug` type.
- Existing feature or enhancement requests should use the mapped `feature`
  type.
- Existing maintenance, docs, cleanup, follow-up, or implementation work items
  should use the mapped `task` type.
- Workflow state belongs in the mapped triage labels, not in the GitHub issue
  type.

## Completion

When an implementation issue is fully implemented and validated, close that
implementation issue from the implementation PR body or final commit message
with a GitHub closing keyword such as `Closes #<issue-number>`. The issue
closes when that PR or commit reaches the default branch.

Use closing keywords only for issues actually satisfied by the change. Do not
close the parent PRD issue from a child implementation issue unless the
maintainer explicitly says the whole PRD is complete.

## When a skill says "fetch the relevant issue"

Use `$github-issues` to view the issue and recent comments.
