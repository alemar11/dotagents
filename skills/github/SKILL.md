---
name: github
description: Use for mixed or ambiguous GitHub repository work, GitHub setup and authentication, direct gh command selection, PR lifecycle work after a branch is already pushed, and routing to standalone github-* skills for focused CI, review, release, triage, portfolio, or star workflows.
---

# GitHub

## Role

Use this as the standalone umbrella GitHub skill. Prefer direct `gh` commands
when they express the job clearly, and route focused requests to the smallest
standalone skill:

- `github-triage`: current-repo issue and PR queue triage.
- `github-portfolio-triage`: explicit multi-repo queue scans.
- `github-ci`: GitHub Actions and failing check logs.
- `github-reviews`: review threads and replies.
- `github-releases`: tags, releases, notes, and package availability.
- `github-stars`: authenticated-user stars and star lists.
- `yeet`: full local checkout publish flow.

## Trigger Cues

Use this skill for mixed or ambiguous GitHub asks, especially when the user
does not yet name a narrower GitHub skill:

- `check this repo on GitHub`
- `look at issue 123`
- `inspect PR 45`
- `is gh configured here?`
- `work on the GitHub side`
- `handle the GitHub follow-up`

If the request is clearly about CI, reviews, releases, portfolio triage,
stars, or local publish flow, route to the focused standalone skill instead of
keeping the work here.

## Prerequisites

Check host readiness before writes:

```bash
command -v git && git --version
command -v gh && gh --version
gh auth status
```

## Observable Command Baseline

Prefer a small set of canonical `gh` entry commands so umbrella GitHub work is
easy to recognize in session traces:

```bash
gh auth status
gh repo view --json nameWithOwner,description,defaultBranchRef,url
gh issue list --repo <owner/repo> --state open --limit 50 --json number,title,url
gh pr list --repo <owner/repo> --state open --limit 50 --json number,title,url
```

## Direct Commands First

Use `gh repo view`, `gh issue ...`, `gh pr ...`, `gh run ...`, and
`gh release ...` directly for simple reads and mutations. Use `--json` whenever
parsing or relaying structured output.

## References

- `references/installation.md`: cross-platform `git` and `gh` setup checks.
- `references/routing.md`: skill routing and direct command map.
- `references/failure-retries.md`: common failure recovery.
