# Issue Tracker: GitHub

PRDs and implementation issues for this repo live as GitHub issues. Use the
`gh` CLI for all operations.

## Conventions

- Create an issue: `gh issue create --title "..." --body "..."`
- Create an implementation issue under a PRD issue:
  `gh issue create --parent <prd-number> --title "..." --body-file <file>`
- Attach existing implementation issues to a PRD issue:
  `gh issue edit <prd-number> --add-sub-issue <issue-number>[,<issue-number>]`
- Read an issue: `gh issue view <number> --comments`
- List issues: `gh issue list --state open --json number,title,body,labels,comments`
- Comment on an issue: `gh issue comment <number> --body "..."`
- Apply or remove labels: `gh issue edit <number> --add-label "..."` or
  `gh issue edit <number> --remove-label "..."`
- Close an issue: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v`; `gh` usually does this automatically when
run inside a clone.

## Title Format

- PRD issue: `PRD: <Feature Name>`
- Implementation issue: `<feature-slug>: <NN> <vertical outcome>`

Use a lowercase kebab-case `<feature-slug>` derived from the PRD title. Use
two-digit ordering (`01`, `02`, `03`) for implementation issues so the global
issue list remains scannable even outside the PRD sub-issue view.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

For feature planning:

- The PRD is a GitHub issue titled `PRD: <Feature Name>`.
- Implementation issues are GitHub sub-issues of the PRD issue.
- Implementation issue titles use
  `<feature-slug>: <NN> <vertical outcome>`.
- Each implementation issue body must also include `Source PRD: #<number>` for
  searchability and backlinks.

## When a skill says "fetch the relevant issue"

Run `gh issue view <number> --comments`.
