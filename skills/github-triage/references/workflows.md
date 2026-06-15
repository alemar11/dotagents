# GitHub Triage Workflows

## Queue Snapshot

```bash
gh repo view --json nameWithOwner,url,defaultBranchRef
gh issue list --state open --limit 50 --json number,title,author,labels,createdAt,updatedAt,url
gh pr list --state open --limit 50 --json number,title,author,isDraft,reviewDecision,mergeStateStatus,statusCheckRollup,createdAt,updatedAt,url
```

Report URLs first, then the reason each item matters. Prefer categories such as
blocked, stale, needs review, needs CI, ready to merge, and needs owner input.

## Item Inspection

```bash
gh issue view <number> --json number,title,body,author,labels,assignees,comments,url
gh pr view <number> --json number,title,body,author,isDraft,reviewDecision,mergeStateStatus,statusCheckRollup,comments,url
```

Inspect only enough detail to make the triage recommendation. Avoid broad
historical reads unless the user asks for a deep queue audit.

## Mutations

Before edits, state the intended mutation and target item. Use direct commands:

```bash
gh issue edit <number> --add-label "<label>"
gh issue comment <number> --body-file <file>
gh pr edit <number> --add-assignee <login>
```

Never mutate as a side effect of a read-only triage request.
