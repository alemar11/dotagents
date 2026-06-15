# Issue Workflows

## Commenting

Write comments that are specific about observed state, requested action, and
next owner. Prefer `--body-file` for non-trivial comments so the exact text can
be reviewed before posting.

```bash
gh issue comment <number> --body-file <message-file>
```

## Labels And Milestones

Read current labels before adding or removing labels:

```bash
gh issue view <number> --json labels,milestone,assignees
gh issue edit <number> --add-label "<label>"
gh issue edit <number> --remove-label "<label>"
```

If the requested label does not exist, ask before creating new taxonomy.

## Closing Issues

Only close an issue when the user explicitly asks or the repository workflow
clearly requires it after a merged fix. Include the closing rationale in the
comment or close reason.
