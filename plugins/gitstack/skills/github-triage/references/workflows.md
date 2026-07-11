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

## Follow-Up Mutations

Never mutate as a side effect of a read-only triage request. Route GitHub issue
creation, type changes, comments, labels, parent/sub-issue relationships, and
closure to `$gitstack:github-issues`. Route PR review-thread replies to
`$gitstack:github-review-threads`.
