---
name: yeet
description: Orchestrate the full publish flow from a local checkout by choosing branch strategy, using `git-commit` for intentional commits, pushing, and handing off to `github-publish` for draft PR opening or reuse.
---

# Yeet

## Overview

Use this skill when the user explicitly wants the full publish flow from a
local checkout: inspect scope, create a branch if needed, stage intentionally,
commit, push, and open or reuse a draft pull request.

This skill is intentionally composed. It requires the `git-commit` and
`github-publish` companion skills at runtime:

- `git-commit` owns selective staging, commit authoring, and post-commit
  verification.
- `github-publish` owns current-branch publish context inspection plus PR
  opening or reuse after the branch is ready or pushed.

Keep v1 intentionally narrow:

- same-repo publish only
- no fork-head or cross-repo PR semantics
- no organization-level GitHub actions
- no silent staging of unrelated changes

## Trigger rules

- Use when the user says `yeet` or asks to publish the current worktree from a
  local checkout.
- Use when the request is "commit, push, and open a PR", "publish my current
  branch", or "turn these local changes into a draft PR".
- Keep the current branch when it is already a non-default local branch.
- Create a new `topic/<slug>` branch only when starting from the repository
  default branch or detached `HEAD`.
- Route directly to `github-publish` when commit and push are already done, or
  when the request is PR-only lifecycle work.
- If `git-commit` or `github-publish` is unavailable, name the missing
  companion skill and stop instead of re-expanding `yeet` into a standalone
  helper surface.

## Workflow

1. Confirm scope before mutating anything.
   - Start with `git status -sb`.
   - Resolve the current branch, detached-HEAD state, and whether you are still
     on the repository default branch.
2. Pick branch strategy.
   - If on the repo default branch or detached `HEAD`, create `topic/<slug>`
     before staging.
   - If already on a non-default local branch, keep that branch and keep all
     current changes there.
3. Stage intentionally.
   - Hand off to `git-commit` for selective staging when the worktree is mixed.
   - Use `git add -A` only when the whole worktree is confirmed in scope.
4. Commit with a well-formed message.
   - Hand off to `git-commit` for commit message structure and sequential
     post-commit verification.
5. Push the branch.
   - If there is no upstream, use `git push -u origin <branch>`.
   - Otherwise use `git push origin <branch>`.
6. Open or reuse the draft PR.
   - Hand off to `github-publish` for its `publish_context.sh` and
     `prs_open_current_branch.sh --draft` helpers.
   - Let `github-publish` reuse an existing open PR for the current branch
     instead of creating a duplicate.

## Guardrails

- Never stage unrelated user changes silently.
- Never switch a non-default feature branch to a different local branch by
  default.
- Never push without confirming scope when the worktree is mixed.
- Default to a draft PR unless the user explicitly asks for a ready PR.
- Stop if the repo is not connected to an accessible same-repo GitHub remote.
- Do not vendor or duplicate the `git-commit` or `github-publish` helper
  layers here.

## Fast paths

- Use `git-commit` directly when the job is "make a good commit" without the
  surrounding publish flow.
- Use `github-publish` directly when the branch is already pushed and the only
  remaining step is PR opening or reuse.
- Use `references/workflows.md` for the full local-checkout publish sequence.

## Reference map

- `references/workflows.md`: composed full publish-from-worktree runbook and
  operator guardrails.

## Examples

- "Yeet this worktree."
- "Publish my current branch as a draft PR."
- "I'm on `main`; branch safely, commit this, and open the PR."
- "Commit, push, and open or reuse the PR for these local changes."
