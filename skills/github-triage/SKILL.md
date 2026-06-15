---
name: github-triage
description: Use when triaging issues, pull requests, labels, milestones, or queue health in the current GitHub repository. Prefer direct gh commands and stay read-only unless the user explicitly asks for a mutation.
---

# GitHub Triage

## Role

Triage the current repository's GitHub issues and pull requests with direct
`gh` commands. Keep reports URL-first, concise, and action-oriented.

Use `github-portfolio-triage` instead when the user gives multiple explicit
repositories. Use `github-stars` for star and list operations.

## Workflow

1. Confirm repository context with `gh repo view --json nameWithOwner,url`.
2. Gather open issues and PRs with `gh issue list` and `gh pr list`.
3. Inspect only the items needed to answer the user's queue question.
4. Group results by blocker, stale item, ready-for-review, CI/review needed,
   or follow-up owner.
5. Do not edit labels, milestones, assignees, titles, or comments unless the
   user asked for that specific change.
6. Before closing issues or resolving partial work, read
   `references/issue-workflows.md` and require a linked or proposed follow-up
   for any deferred acceptance criteria.

## References

- `references/workflows.md`: current-repo queue and item workflows.
- `references/issue-workflows.md`: issue mutation and comment safety rules.
