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

## Focused Follow-Up Routing

Never mutate as a side effect of a read-only triage request. Route GitHub issue
creation, type changes, comments, labels, parent/sub-issue relationships, and
closure to `$gitstack:github-issues` with `mutation_mode=apply`, the exact
repository and issue target, and one matching `issue_operation` only after the
user authorizes that write. Use `mutation_mode=dry-run` only when the user asks
to preview a specific write-shaped operation. Pure queue reads omit
`mutation_mode` and an operation field.

Route evidence-backed issue disposition, acceptance, or closure judgment to
`$gitstack:github-deep-review`. Route PR review-thread replies to
`$gitstack:github-review-threads` with the exact repository and PR,
`review_operation=reply`, and `mutation_mode=apply`. For read-only inspection,
use `review_operation=inspect` and omit mutation authority.
