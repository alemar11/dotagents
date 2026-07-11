# GitHub CI Workflows

## PR Checks

```bash
gh pr checks <number> --repo <owner/repo>
gh pr checks <number> --repo <owner/repo> --json name,state,conclusion,detailsUrl,startedAt,completedAt
```

Use this first when the user only needs check status.

## Runs And Logs

```bash
gh run list --repo <owner/repo> --branch <branch> --limit 10
gh run view <run-id> --repo <owner/repo> --log
```

Prefer run URLs and job names in summaries. Quote only short log snippets.

## Focused Failure Extraction

Resolve `<plugin-root>` as two directories above the directory containing the owning
`SKILL.md`; this may be an installed or linked package outside the current
checkout.

```bash
<plugin-root>/scripts/gitstack ci inspect --repo <owner/repo> --pr <number>
<plugin-root>/scripts/gitstack --json ci inspect --repo <owner/repo> --pr <number>
```

Use this when direct logs are too large and the task is to find the actionable
failure lines.
