---
name: github-portfolio-triage
description: Scan multiple GitHub repos read-only for queue, PR, issue, CI, release, blocker, and next-action summaries.
---

# GitHub Portfolio Triage

## Role

Scan multiple explicit repositories without mutating them. Use
`<skill-root>/scripts/portfolio-scan` for a URL-first queue summary across
issues, PRs, recent CI, latest release state, and next actions.

Use `github-triage` instead for a single current repository.

## Public Script

Resolve `<skill-root>` as the absolute directory containing this `SKILL.md`,
then invoke the helper from that installed package. Do not assume the current
checkout contains `skills/github-portfolio-triage/`.

```bash
<skill-root>/scripts/portfolio-scan --help
<skill-root>/scripts/portfolio-scan --version
<skill-root>/scripts/portfolio-scan --json doctor
```

The script emits stable JSON success/error envelopes for JSON mode and writes
no implicit config.

## Workflow

1. Require explicit `owner/repo` inputs or a repo-file supplied by the user.
2. Run a read-only scan with `<skill-root>/scripts/portfolio-scan`.
3. Summarize queue size, blocking CI, release gaps, and next actions per repo.
4. Do not edit labels, issues, PRs, releases, or workflows.

## References

- `references/workflows.md`: portfolio scan and report workflow.
- `references/script-summary.md`: `portfolio-scan` command contract.
