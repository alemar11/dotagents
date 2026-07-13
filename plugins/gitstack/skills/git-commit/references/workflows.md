# Git Commit Workflows

## Preferred Entry Signals

Treat these user phrasings as direct entry points into this workflow:

- `commit`
- `commit this`
- `commit and push`
- `push-only`
- `stage only these files and commit`

Normalize them once using the shared registry: commit phrases select
`commit_operation=commit-only`, `commit and push` selects
`commit_operation=commit-and-push`, and `push-only` selects
`commit_operation=push-only`.

## Fast Path

Use when changes are tiny, cohesive, and low risk:

```bash
git status --short --branch
git diff --staged --name-status
git diff -- <path>
git add -- <path>
git diff --staged --stat
git diff --staged
git commit -F "$message_file"
git status --short --branch
git log -1 --pretty=fuller
```

Keep this command order when practical so session evidence stays easy to
recognize during audits. The first staged-path read must happen before any
`git add`; otherwise pre-existing staged work is indistinguishable from the
newly selected commit scope.

## Safe Path

Use when the worktree is mixed, generated files are present, or validation
matters:

```bash
git status --short --branch
git diff --staged --name-status
git diff --staged --stat
git diff --stat
git diff -- <path>
git add -- <explicit-paths>
git diff --staged --stat
git diff --staged
```

Compare the staged paths recorded before `git add` with the intended paths. Do
not commit if staged files and the commit message describe different work. Do
not run `git reset`, `git restore --staged`, or another index rewrite merely to
clear unrelated staged work; it belongs to the user.

## Pre-existing Staged Work

When the initial `git diff --staged --name-status` is non-empty:

- Continue normally only when every pre-existing staged path is part of the
  explicitly intended commit and its staged content has been reviewed.
- Stop when any pre-existing staged path is unrelated or its ownership is
  unclear. Report the paths and leave the index untouched.
- If the user explicitly wants a commit of complete intended files while
  preserving unrelated staged entries, review the full intended path contents
  against `HEAD`, then isolate with Git's path-limited commit:

```bash
git diff HEAD -- <explicit-paths>
git commit --only -F "$message_file" -- <explicit-paths>
git status --short --branch
git diff --staged --name-status
```

`git commit --only` commits the current complete contents of the named paths
while excluding other staged paths. Do not use it when only selected hunks of
an intended file should be committed; stop and ask the user to finish or
authorize index isolation instead.

For `commit_operation=commit-only`, stop after commit verification. Continue to
push only for `commit_operation=commit-and-push`.

## Split Commits

Default to splitting when changes touch unrelated top-level roots or mix
independent concerns. Stage and verify one commit at a time.

## Issue-Closing Commit And Push

Use for `commit_operation=commit-and-push` when the owner explicitly authorizes
committing directly to the current branch, pushing, and closing GitHub issues
through commit trailers instead of a PR. This is never a `push-only` path.

```bash
git status --short --branch
git diff --staged --name-status
git diff --stat
git diff -- <explicit-paths>
git add -- <explicit-paths>
git diff --staged --stat
git diff --staged
git commit -F "$message_file"
git log -1 --pretty=fuller
git push
gh issue list --state open --limit 50 --json number,title,state,url
```

The commit message should use a concise imperative subject and include trailers
for only the issues actually satisfied by the staged diff:

```text
Implement workflow persistence API

Summary:
- Add persisted workflow storage and FE/AI read endpoints.
- Cover projection and validation behavior with backend tests.

Validation:
- npm test
- npm run build
- npm run lint

Closes #11
```

Do not add `Closes #N` for deferred or partially satisfied work. If the owner
asked to close a partial issue, route issue follow-up handling to
`$gitstack:github-issues` before committing or closing.
