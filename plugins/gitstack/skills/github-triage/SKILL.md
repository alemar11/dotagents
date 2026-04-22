---
name: github-triage
description: Handle focused GitHub triage inside `gitstack`. Prefer plain `gh` for repository, issue, and PR work, and use shared `ghflow` helpers only for authenticated-user stars and star lists.
---

# GitHub Triage

## Overview

Use this bundled skill when the request is clearly about repo orientation,
issues, PR metadata, authenticated-user stars, or star lists.

Prefer direct `gh` commands for straightforward repo, issue, and PR work.
Use `ghflow` for the parts that are API-heavy, cross-session standardized, or
shared with other bundled skills. Route mixed-domain or publish-lifecycle work
back to the umbrella `github` skill.

## Direct commands first

- `gh repo view --json nameWithOwner,description,defaultBranchRef,url`
- `gh issue view <n> --repo <owner/repo>`
- `gh pr view <n> --repo <owner/repo>`
- `gh issue create --repo <owner/repo> ...`
- `gh issue edit <n> --repo <owner/repo> ...`
- `gh pr edit <n> --repo <owner/repo> ...`

## Use `ghflow` when

- the workflow needs normalized JSON across repos or domains
- the job is about authenticated-user stars or star lists

## Fast path

- `gh repo view --json nameWithOwner,description,defaultBranchRef,url`
- `gh issue view <n> --repo <owner/repo>`
- `gh pr view <n> --repo <owner/repo>`
- `ghflow --json stars list`
- `ghflow --json stars lists list`

## Trigger rules

- Use for repository orientation, issues, PR metadata, stars, and lists.
- Keep review follow-up in `github-reviews`.
- Keep CI and Actions work in `github-ci`.
- Keep release creation and planning in `github-releases`.
- Keep publish lifecycle on already-pushed branches in the umbrella `github`.

## References navigation

- Start at `references/script-summary.md` for the triage command map.
- Open `references/workflows.md` for triage-domain runbooks.
- Open `references/issue-workflows.md` when issue copy, move, or close-with-
  evidence behavior matters and you need the raw `gh` sequence.
- Open `references/github_workflow_behaviors.md` for GitHub-specific behavior
  notes that affect triage results.
