---
name: github-triage
description: Inspect current-repo GitHub issue and PR queues read-only; route mutations to $gitstack:github-issues.
---

# GitHub Triage

## Transport

Prefer the required GitHub connector for supported remote reads and writes. Use
`gh` for connector gaps. An authorized connector write may fall back
automatically only when the operation and repository are identical, `gh`
authentication and access succeed, and the transport switch is reported.


## Role

Triage the current repository's GitHub issues and pull requests with connector
reads and `gh` fallback. Keep reports URL-first, concise, and action-oriented.

Use `$gitstack:github-portfolio-triage` instead when the user gives multiple explicit
repositories. Use `$gitstack:github-stars` for star and list operations. Use
`$gitstack:github-issues` for issue creation, issue type changes, comments, labels,
parent/sub-issue relationships, and closure.

## Workflow

1. Confirm repository context with the connector, or use
   `gh repo view --json nameWithOwner,url` when local context or fallback is needed.
2. Gather open issues and PRs with connector search/list operations, falling
   back to `gh issue list` and `gh pr list` for the identical repository.
3. Inspect only the items needed to answer the user's queue question.
4. Group results by blocker, stale item, ready-for-review, CI/review needed,
   or follow-up owner.
5. Do not edit labels, milestones, assignees, titles, or comments from this
   skill; route authorized GitHub issue lifecycle mutations to
   `$gitstack:github-issues`.
6. Before recommending issue closure or resolution of partial work, read
   `references/issue-workflows.md` and require a linked or proposed follow-up
   for any deferred acceptance criteria.

## References

- `references/workflows.md`: current-repo queue and item workflows.
- `references/issue-workflows.md`: issue closure and follow-up safety rules.
