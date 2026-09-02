# GitHub Repository Triage Workflows

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

## Multiple Repository Scan

Use the `<skill-root>` resolved by the active G entrypoint; it may be an
installed or linked package outside the current checkout.

```bash
<skill-root>/scripts/g portfolio scan --repo <owner/repo> --repo <owner/repo>
<skill-root>/scripts/g portfolio scan --repo-file <repos.txt>
<skill-root>/scripts/g --json portfolio scan --repo <owner/repo>
```

Repo files contain one `owner/repo` per line. Ignore blank lines and `#`
comments. For each repository, report its URL, open issue and pull request
counts, recent CI state, latest release state, top queue signals, and
recommended next action. Preserve per-repository failures and keep the entire
scan read-only.

## Focused Follow-Up Routing

Never mutate as a side effect of a read-only triage request. Route GitHub issue
creation, type changes, comments, labels, parent/sub-issue relationships, and
closure to the `github-issues` workflow with `mutation_mode=apply`, the exact
repository and issue target, and one matching `issue_operation` only after the
user authorizes that write. Use `mutation_mode=dry-run` only when the user asks
to preview a specific write-shaped operation. Pure queue reads omit
`mutation_mode` and an operation field.

Route evidence-backed issue disposition, acceptance, or closure judgment to
the `github-investigation` workflow. Route PR review-thread replies to
the `github-review-threads` workflow with the exact repository and PR,
`review_operation=reply`, and `mutation_mode=apply`. For read-only inspection,
use `review_operation=inspect` and omit mutation authority.
