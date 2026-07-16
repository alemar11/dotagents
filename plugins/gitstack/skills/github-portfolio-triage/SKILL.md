---
name: github-portfolio-triage
description: Scan multiple GitHub repos read-only for queue, PR, issue, CI, release, blocker, and next-action summaries.
---

# GitHub Portfolio Triage

## Transport

Prefer the required GitHub connector for supported remote reads. Use the
read-only portfolio script or direct `gh` reads only for connector gaps after
authentication and access verification, and report that fallback. This skill
never performs GitHub writes or automatically falls back between write
transports.


## Role

Scan multiple explicit repositories without mutating them. Use
`<plugin-root>/scripts/gitstack portfolio scan` for a URL-first queue summary across
issues, PRs, recent CI, latest release state, and next actions.

Use `$gitstack:github-triage` instead for a single current repository.

## Public Script

Resolve `<plugin-root>` as two directories above the directory containing this `SKILL.md`,
then invoke the helper from the installed plugin root. Do not assume the
current checkout contains the GitStack source tree.

```bash
<plugin-root>/scripts/gitstack portfolio scan --help
<plugin-root>/scripts/gitstack --version
<plugin-root>/scripts/gitstack --json doctor
```

The script emits stable JSON success/error envelopes for JSON mode and writes
no implicit config.

## Workflow

1. Require explicit `owner/repo` inputs or a repo-file supplied by the user.
2. Run a read-only scan with `<plugin-root>/scripts/gitstack portfolio scan`.
3. Summarize queue size, blocking CI, release gaps, and next actions per repo.
4. Do not edit labels, issues, PRs, releases, or workflows.

## References

- `references/workflows.md`: portfolio scan and report workflow.
- `references/script-summary.md`: `gitstack portfolio scan` command contract.
