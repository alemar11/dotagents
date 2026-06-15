---
name: github-portfolio-triage
description: Use when scanning multiple explicit GitHub repositories for read-only queue, PR, issue, CI, release, blocker, and next-action summaries.
---

# GitHub Portfolio Triage

## Role

Scan multiple explicit repositories without mutating them. Use
`scripts/portfolio-scan` for a URL-first queue summary across issues, PRs,
recent CI, latest release state, and next actions.

Use `github-triage` instead for a single current repository.

## Public Script

```bash
skills/github-portfolio-triage/scripts/portfolio-scan --help
skills/github-portfolio-triage/scripts/portfolio-scan --version
skills/github-portfolio-triage/scripts/portfolio-scan --json doctor
```

The script emits stable JSON success/error envelopes for JSON mode and writes
no implicit config.

## Workflow

1. Require explicit `owner/repo` inputs or a repo-file supplied by the user.
2. Run a read-only scan.
3. Summarize queue size, blocking CI, release gaps, and next actions per repo.
4. Do not edit labels, issues, PRs, releases, or workflows.

## References

- `references/workflows.md`: portfolio scan and report workflow.
- `references/script-summary.md`: `portfolio-scan` command contract.
