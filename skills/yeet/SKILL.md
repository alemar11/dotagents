---
name: yeet
description: Publish local work to GitHub by committing, pushing, and opening or updating a draft PR.
---

# Yeet

## Role

Publish local work from a checkout. This skill is scriptless by design and
composes standalone skills conceptually:

- Use `$git-commit` for staging and commit authoring.
- Use direct `gh` for GitHub readiness and PR lifecycle commands.
- Use `$github-issues`, `$github-triage`, `$github-deep-review`, `$github-ci`,
  or `$github-review-threads` only for focused follow-up GitHub work.

If there is no local work to publish, or the request is only GitHub issue
hygiene such as creating, commenting on, labeling, or closing issues, do not run
the full publish flow. Route that work to `$github-issues`, perform the
authorized GitHub issue mutation or dry-run draft command,
and state that full `yeet` was not applicable.

Prefer the shortest publish path that matches the state in front of you:

- If a good local commit already exists, reuse it instead of reopening commit
  authoring.
- If the branch already has a PR, update that PR instead of treating the run as
  a fresh publish.
- If there is no publishable local change, stop early and route issue-only
  follow-up to `$github-issues`.

## Workflow

1. Inspect branch and worktree state.
2. Confirm the intended scope when the worktree is mixed.
3. Reuse the current commit when it already represents the intended scope.
   Otherwise create one through the `git-commit` workflow.
4. Push the branch with direct `git push`.
5. Open a draft PR with `gh pr create`, or update the existing PR with
   `gh pr edit` when one is already attached to the branch.
6. Return branch, PR URL, commit hash, and verification performed.

## References

- `references/workflows.md`: publish, existing-PR, and retry workflows.
