---
name: github-triage
description: Use when triaging GitHub repos, issues, PRs, or maintainer queues.
---

# GitHub Triage

## Overview

Use this bundled skill when the request is clearly about repo orientation,
maintainer triage, issues, PR metadata, authenticated-user stars, or star
lists.

Prefer direct `gh` for straightforward repo, issue, and PR work. Use resolved
`ghflow` only for authenticated-user stars and star lists. Route mixed-domain
or publish-lifecycle work back to the umbrella `github` skill.

When the user says `triage` from a GitHub repo, produce a URL-first maintainer
triage report for the current repo's open issues and PRs. This is report-only:
do not implement, merge, close, rerun checks, or comment unless the user
explicitly asks for that follow-up.

## Direct commands first

- `gh repo view --json nameWithOwner,description,defaultBranchRef,url`
- `gh issue list --repo <owner/repo> --state open --limit 50 --json number,title,author,labels,createdAt,updatedAt,url`
- `gh pr list --repo <owner/repo> --state open --limit 50 --json number,title,author,isDraft,reviewDecision,mergeStateStatus,createdAt,updatedAt,url`
- `gh issue view <n> --repo <owner/repo>`
- `gh pr view <n> --repo <owner/repo>`
- `gh issue create --repo <owner/repo> ...`
- `gh issue edit <n> --repo <owner/repo> ...`
- `gh pr edit <n> --repo <owner/repo> ...`

## Use Resolved `ghflow` When

- the job is about authenticated-user stars or star lists

Resolve `ghflow` with `../github/references/core/ghflow-resolution.md` before helper use.

## Fast path

- `gh repo view --json nameWithOwner,description,defaultBranchRef,url`
- `gh issue list --repo <owner/repo> --state open --limit 50 --json number,title,author,labels,createdAt,updatedAt,url`
- `gh pr list --repo <owner/repo> --state open --limit 50 --json number,title,author,isDraft,reviewDecision,mergeStateStatus,createdAt,updatedAt,url`
- `gh issue view <n> --repo <owner/repo>`
- `gh pr view <n> --repo <owner/repo>`
- `<resolved-ghflow> --json stars list`
- `<resolved-ghflow> --json stars lists list`

## Trigger rules

- Use for repository orientation, issues, PR metadata, stars, and lists.
- Use for current-repo maintainer triage when the user asks to `triage`, asks
  what open issues or PRs need attention, or asks for autonomous candidates as
  a report.
- Keep maintainer triage current-repo first. Support explicit `owner/repo`, but
  do not broaden to owner/org-wide queue discovery unless a future workflow
  explicitly adds that behavior.
- Keep review follow-up in `github-reviews`.
- Keep CI and Actions work in `github-ci`.
- Keep release creation and planning in `github-releases`.
- Keep publish lifecycle on already-pushed branches in the umbrella `github`.

## References navigation

- Start at `references/script-summary.md` for the triage command map.
- Open `references/workflows.md` for triage-domain runbooks.
- Open `references/project-triage.md` when the task is maintainer-facing issue
  and PR queue triage for the current repo.
- Open `references/issue-workflows.md` when issue copy, move, or close-with-
  evidence behavior matters and you need the raw `gh` sequence.
- Open `references/github_workflow_behaviors.md` for GitHub-specific behavior
  notes that affect triage results.
