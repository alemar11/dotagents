---
name: git-commit
description: Use when committing local changes, preparing commit messages, staging explicit paths, splitting changes into commits, or doing commit-and-push flows that do not open a pull request. Use direct git commands only; route PR publishing to yeet.
---

# Git Commit

## Core Rule

Use direct `git` commands. This skill is scriptless by design.

For the common case of a small cohesive change and a user ask like `commit`,
`commit this`, or `commit and push`, stay on the shortest safe path:

1. `git status --short --branch`
2. `git diff -- <path>` for the intended files
3. `git add -- <explicit-paths>`
4. `git diff --staged`
5. `git commit -F <message-file>`
6. `git push` only if the user asked to push

Escalate to broader diff review or split commits only when the worktree is
mixed, generated files are involved, or the staged scope is still unclear.

If the user asks for a PR, draft PR, branch publication, or "publish", use
`yeet` instead. If the user says "commit and push" without PR language, ask
"PR or push-only?" and default to push-only when unclear. When the user
explicitly authorizes direct-to-main issue closure, use issue-closing commit
trailers such as `Closes #123` only after staging the intended paths and
verifying the diff. Route GitHub issue comments, labels, type changes, follow-up
issue creation, or manual closure to `$github-issues`.

## Trigger Cues

Use this skill for short or implicit commit-authoring asks such as:

- `commit`
- `commit this`
- `create a commit`
- `commit and push`
- `push-only`
- `stage only <paths> and commit`

If the request expands into branch publication or PR creation, route to `yeet`
instead of stretching this skill.

## Observable Command Baseline

Prefer the same command spine for most runs so commit work stays easy to audit
from session traces:

```bash
git status --short --branch
git diff -- <path>
git diff --staged
git add -- <explicit-paths>
git commit -F <message-file>
git log -1 --pretty=fuller
```

For push-only follow-through, append:

```bash
git push
```

## Workflow

1. Inspect the worktree with `git status --short --branch`.
2. For small cohesive work, inspect only the intended files first. Expand to
   `git diff --stat` or broader review only when the scope is mixed or unclear.
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
