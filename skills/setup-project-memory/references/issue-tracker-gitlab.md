# Issue Tracker: GitLab

PRDs and implementation issues for this repo live as GitLab issues. Use the
`glab` CLI for all operations.

## Conventions

- Create an issue: `glab issue create --title "..." --description "..."`
- Read an issue: `glab issue view <number> --comments`
- List issues: `glab issue list -F json`
- Comment on an issue: `glab issue note <number> --message "..."`
- Apply or remove labels: `glab issue update <number> --label "..."` or
  `glab issue update <number> --unlabel "..."`
- Close an issue: post any closing note first, then run
  `glab issue close <number>`.

Infer the repo from `git remote -v`; `glab` usually does this automatically
when run inside a clone.

## When a skill says "publish to the issue tracker"

Create a GitLab issue.

## When a skill says "fetch the relevant issue"

Run `glab issue view <number> --comments`.
