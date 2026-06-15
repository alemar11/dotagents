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

```bash
skills/github-ci/scripts/ci-inspect --repo <owner/repo> --pr <number>
skills/github-ci/scripts/ci-inspect --json --repo <owner/repo> --pr <number>
```

Use this when direct logs are too large and the task is to find the actionable
failure lines.
