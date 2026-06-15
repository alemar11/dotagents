---
name: git-commit
description: Use when committing local changes, preparing commit messages, staging explicit paths, splitting changes into commits, or doing commit-and-push flows that do not open a pull request. Use direct git commands only; route PR publishing to yeet.
---

# Git Commit

## Core Rule

Use direct `git` commands. This skill is scriptless by design.

If the user asks for a PR, draft PR, branch publication, or "publish", use
`yeet` instead. If the user says "commit and push" without PR language, ask
"PR or push-only?" and default to push-only when unclear. When the user
explicitly authorizes direct-to-main issue closure, use issue-closing commit
trailers such as `Closes #123` only after staging the intended paths and
verifying the diff.

## Workflow

1. Inspect the worktree with `git status --short --branch`.
2. Inspect relevant diffs with `git diff` and `git diff --staged`.
3. Stage only intended paths with explicit pathspecs such as
   `git add -- <path>`.
4. Re-check `git diff --staged` before committing.
5. Write a concise imperative subject and a body with summary, rationale, and
   validation.
6. Commit with `git commit -F <message-file>`.
7. Verify with `git status --short --branch` and
   `git log -1 --pretty=fuller`.
8. For push-only requests, use `git push` or `git push -u origin HEAD`.

## References

- `references/workflows.md`: commit, split-commit, and push-only workflows.
