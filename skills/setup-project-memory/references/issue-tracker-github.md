# Issue Tracker: GitHub

PRDs and implementation issues for this repo live as GitHub issues. Use the
`gh` CLI for all operations.

Tracker mode: `github`
GitHub repo: infer from `git remote -v` unless this file records a specific
`<owner>/<repo>`.

## Non-Mutating Runs

If this setup is being used for a temp exercise, validation pass, rehearsal,
dry run, or any workflow where external GitHub mutation is not authorized, do
not run `gh issue create`, `gh issue edit`, `gh issue comment`, or label
mutation commands. Use local markdown for that run, or return draft issue
bodies and exact `gh` commands without executing them. Record the non-mutating
choice in `project-memory/agents/issue-tracker.md`.

## Conventions

- Create an issue: `gh issue create --title "..." --body "..."`
- Create an issue with a GitHub Issue Type:
  `gh issue create --type "<type>" --title "..." --body "..."`
- Create an implementation issue under a PRD issue:
  `gh issue create --parent <prd-number> --title "..." --body-file <file>`
- Attach existing implementation issues to a PRD issue:
  `gh issue edit <prd-number> --add-sub-issue <issue-number>[,<issue-number>]`
- Read an issue: `gh issue view <number> --comments`
- List issues:
  `gh issue list --state open --json number,title,body,labels,type,comments`
- Set or change issue type: `gh issue edit <number> --type "<type>"`
- Comment on an issue: `gh issue comment <number> --body "..."`
- Apply or remove labels: `gh issue edit <number> --add-label "..."` or
  `gh issue edit <number> --remove-label "..."`
- Close an issue: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v`; `gh` usually does this automatically when
run inside a clone.

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

Create a GitHub issue.

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

Run `gh issue view <number> --comments`.
