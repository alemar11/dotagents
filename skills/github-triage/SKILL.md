---
name: github-triage
description: Use for current-repository GitHub issue, pull request, label, milestone, or queue-health triage and URL-first read-only queue summaries. Prefer direct gh read commands; route GitHub issue lifecycle mutations to $github-issues.
---

# GitHub Triage

## Role

Triage the current repository's GitHub issues and pull requests with direct
`gh` read commands. Keep reports URL-first, concise, and action-oriented.

Use `github-portfolio-triage` instead when the user gives multiple explicit
repositories. Use `$github-stars` for star and list operations. Use
`$github-issues` for issue creation, issue type changes, comments, labels,
parent/sub-issue relationships, and closure.

## Workflow

1. Confirm repository context with `gh repo view --json nameWithOwner,url`.
2. Gather open issues and PRs with `gh issue list` and `gh pr list`.
3. Inspect only the items needed to answer the user's queue question.
4. Group results by blocker, stale item, ready-for-review, CI/review needed,
   or follow-up owner.
5. Do not edit labels, milestones, assignees, titles, or comments from this
   skill; route authorized GitHub issue lifecycle mutations to
   `$github-issues`.
6. Before recommending issue closure or resolution of partial work, read
   `references/issue-workflows.md` and require a linked or proposed follow-up
   for any deferred acceptance criteria.

## References

- `references/workflows.md`: current-repo queue and item workflows.
- `references/issue-workflows.md`: issue closure and follow-up safety rules.
