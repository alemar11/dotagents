# GitHub CI Workflows

For release workflows that create pull requests, branches, or tags, run the
configuration preflight in
[`configuration.md`](configuration.md) before editing workflow files. Detailed
workflow-authoring instructions are not currently present. A blocked or
unavailable preflight is an advisory warning: when the user requested the
workflow, write it with the required `permissions` block and report that its PR
operation will remain non-functional until the repository setting is enabled.

```bash
<plugin-root>/scripts/g --json ci permissions --repo <owner/repo> --allow-non-project
```

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
<plugin-root>/scripts/g ci inspect --repo <owner/repo> --pr <number>
<plugin-root>/scripts/g --json ci inspect --repo <owner/repo> --pr <number>
```

Use this when direct logs are too large and the task is to find the actionable
failure lines.
