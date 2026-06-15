---
name: yeet
description: Use when publishing local work from a checkout to GitHub by confirming scope, composing or reusing a commit, pushing a branch, and opening or updating a draft pull request. This is a scriptless convenience orchestration skill.
---

# Yeet

## Role

Publish local work from a checkout. This skill is scriptless by design and
composes standalone skills conceptually:

- Use `git-commit` for staging and commit authoring.
- Use `github` for GitHub readiness and PR lifecycle commands.
- Use `github-ci` or `github-reviews` only for follow-up CI or review work.

If there is no local work to publish, or the request is only GitHub issue
hygiene such as creating, commenting on, labeling, or closing issues, do not run
the full publish flow. Route that work to `github` or `github-triage`, perform
the authorized GitHub mutation, and state that full `yeet` was not applicable.

## Workflow

1. Inspect branch and worktree state.
2. Confirm the intended scope when the worktree is mixed.
3. Create or reuse a commit through the `git-commit` workflow.
4. Push the branch with direct `git push`.
5. Open or update a draft PR with direct `gh pr create` or `gh pr edit`.
6. Return branch, PR URL, commit hash, and verification performed.

## References

- `references/workflows.md`: publish, existing-PR, and retry workflows.
