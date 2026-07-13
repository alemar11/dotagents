---
name: git-commit
description: Commit or commit-and-push local changes with explicit staging and direct git; route PR publishing to $gitstack:yeet.
---

# Git Commit

## Core Rule

Use direct `git` commands. This skill is scriptless by design.

For the common case of a small cohesive change and a user ask like `commit`,
`commit this`, or `commit and push`, normalize the phrase once to
`commit_operation=commit-only|commit-and-push|push-only`, then stay on the
shortest safe path:

1. `git status --short --branch`
2. `git diff --staged --name-status` to identify anything staged before this
   workflow
3. `git diff -- <path>` for the intended files
4. `git add -- <explicit-paths>`
5. `git diff --staged`
6. `git commit -F <message-file>`
7. `git push` only for `commit_operation=commit-and-push`

Escalate to broader diff review or split commits only when the worktree is
mixed, generated files are involved, or the staged scope is still unclear.

If the user asks for a PR, draft PR, branch publication, or "publish", use
`$gitstack:yeet` instead. `commit_operation=push-only` never creates a commit;
`commit_operation=commit-and-push` does both operations. When the user
explicitly authorizes direct-to-main issue closure, use issue-closing commit
trailers such as `Closes #123` only after staging the intended paths and
verifying the diff. Route GitHub issue comments, labels, type changes,
follow-up issue creation, or manual closure to `$gitstack:github-issues`.

## Trigger Cues

Use this skill for short or implicit commit-authoring asks such as:

- `commit`
- `commit this`
- `create a commit`
- `commit and push`
- `push-only`
- `stage only <paths> and commit`

If the request expands into branch publication or PR creation, route to `$gitstack:yeet`
instead of stretching this skill.

## Observable Command Baseline

Prefer the same command spine for most runs so commit work stays easy to audit
from session traces:

```bash
git status --short --branch
git diff --staged --name-status
git diff -- <path>
git add -- <explicit-paths>
git diff --staged
git commit -F <message-file>
git log -1 --pretty=fuller
```

For `commit_operation=commit-and-push`, append:

```bash
git push
```

For `commit_operation=push-only`, do not use the commit-producing baseline.
Inspect the existing commit range without staging or committing:

```bash
git status --short --branch
git diff --staged --name-status
git branch --show-current
git remote get-url origin
git rev-parse --abbrev-ref --symbolic-full-name @{upstream}
```

With a verified upstream, inspect `@{upstream}..HEAD` and run `git push`. When
the branch has no upstream, verify the intended `origin` repository and base,
inspect `<verified-base>..HEAD`, then use `git push -u origin HEAD`. Stop rather
than guessing the base, remote, or target branch.

## Workflow

1. Inspect the worktree with `git status --short --branch`, then inspect and
   record the pre-existing index with `git diff --staged --name-status` before
   running any `git add` command.
2. If unrelated changes are already staged, stop by default without resetting
   or rewriting the user's index. Continue only after the unrelated staged work
   is committed separately, or isolate fully reviewed intended path contents
   with the path-limited workflow in `references/workflows.md` when that scope
   is explicit. Do not use path-limited commit isolation for partial-hunk work.
3. For small cohesive work, inspect only the intended files first. Expand to
   `git diff --stat` or broader review only when the scope is mixed or unclear.
4. Stage only intended paths with explicit pathspecs such as
   `git add -- <path>`.
5. Re-check `git diff --staged` before committing, and compare its path set with
   the recorded pre-existing staged set and the intended commit scope.
6. Write a concise imperative subject and a body with summary, rationale, and
   validation.
7. Commit with `git commit -F <message-file>`.
8. Verify with `git status --short --branch` and
   `git log -1 --pretty=fuller`.
9. For `commit_operation=commit-and-push`, use `git push` or
   `git push -u origin HEAD`; for `push-only`, verify the existing commit range
   and push without staging or committing.

## References

- `references/workflows.md`: commit, split-commit, and push-only workflows.
- `../../references/options.md`: shared canonical GitStack options.
