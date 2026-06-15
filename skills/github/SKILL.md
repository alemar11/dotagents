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

## Prerequisites

Check host readiness before writes:

```bash
command -v git && git --version
command -v gh && gh --version
gh auth status
```

## Direct Commands First

Use `gh repo view`, `gh issue ...`, `gh pr ...`, `gh run ...`, and
`gh release ...` directly for simple reads and mutations. Use `--json` whenever
parsing or relaying structured output.

## References

- `references/installation.md`: cross-platform `git` and `gh` setup checks.
- `references/routing.md`: skill routing and direct command map.
- `references/failure-retries.md`: common failure recovery.
