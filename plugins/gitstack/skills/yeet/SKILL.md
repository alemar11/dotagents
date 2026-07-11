---
name: yeet
description: Publish local work to GitHub by committing, pushing, and opening or updating a draft PR.
---

# Yeet

## Role

Publish local work from a checkout. This skill composes bundled GitStack
skills, direct `git`, the shared CLI, and connector-backed PR operations:

- Use `$gitstack:git-commit` for staging and commit authoring.
- Use `<plugin-root>/scripts/gitstack publish preflight` for structured local
  readiness, the connector for supported PR lifecycle operations, and `gh` for
  identical-target fallback.
- Use `$gitstack:github-issues`, `$gitstack:github-triage`, `$gitstack:github-deep-review`, `$gitstack:github-ci`,
  or `$gitstack:github-review-threads` only for focused follow-up GitHub work.

Resolve `<plugin-root>` as two directories above the directory containing this
`SKILL.md`. The CLI cannot invoke connector tools; it uses direct `git` and
authenticated `gh` for its preflight and fallback commands.

If there is no local work to publish, or the request is only GitHub issue
hygiene such as creating, commenting on, labeling, or closing issues, do not run
the full publish flow. Route that work to `$gitstack:github-issues`, perform the
authorized GitHub issue mutation or dry-run draft command,
and state that full `yeet` was not applicable.

Prefer the shortest publish path that matches the state in front of you:

- If a good local commit already exists, reuse it instead of reopening commit
  authoring.
- If the branch already has a PR, update that PR instead of treating the run as
  a fresh publish.
- If there is no publishable local change, stop early and route issue-only
  follow-up to `$gitstack:github-issues`.

## Workflow

1. Run the complete publish preflight before any push: require a named branch,
   reject the repository default branch, verify `gh` authentication, verify the
   `origin` repository and any configured upstream match the current branch,
   and look up an existing open PR for that branch.
2. Inspect worktree state and confirm the intended scope when it is mixed.
3. Reuse the current commit when it already represents the intended scope.
   Otherwise create one through `$gitstack:git-commit` in commit-only mode; Yeet retains
   ownership of push.
4. Rerun the complete publish preflight immediately before pushing. Use a
   normal push to the verified upstream, or `git push -u origin HEAD` only when
   no upstream exists. Never infer permission to force-push.
5. Re-check for an existing PR after push. Open a draft PR only when none
   exists; otherwise update the existing PR. After an ambiguous create failure,
   look up the PR again before retrying so a successful first request cannot
   create a duplicate.
6. Return branch, PR URL, commit hash, and verification performed.

## References

- `references/workflows.md`: publish, existing-PR, and retry workflows.
