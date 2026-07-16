---
name: github-triage
description: Inspect current-repo GitHub issue and PR queues read-only; route mutations to $gitstack:github-issues.
---

# GitHub Triage

## Transport

Prefer the required GitHub connector for supported remote reads. Use `gh` only
for read gaps after authentication and access verification, and report that
fallback. This skill never performs GitHub writes or automatically falls back
between write transports; route every write-shaped request to its owning skill.


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
   `$gitstack:github-issues` only after normalizing the handoff to
   `mutation_mode=apply`, the exact repository and issue target, and one
   canonical `issue_operation`. Route an explicit mutation preview with
   `mutation_mode=dry-run` and the same exact target and operation. Pure queue
   reads omit both fields.
6. Route evidence-backed issue disposition questions, including whether an
   issue should close or partial work satisfies its acceptance criteria, to
   `$gitstack:github-deep-review`. Route any authorized resulting lifecycle
   mutation to `$gitstack:github-issues`.

## References

- `references/workflows.md`: current-repo queue and item workflows.
- `../../references/options.md`: canonical GitStack invocation fields for routed handoffs.
