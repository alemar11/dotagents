# Git Commit Workflows

## Preferred Entry Signals

Treat these user phrasings as direct entry points into this workflow:

- `commit`
- `commit this`
- `commit and push`
- `push-only`
- `stage only these files and commit`
- `fixup <commit>`
- `fixup and push <commit>`
- `amend fixup <commit>`

Normalize them once using the shared registry: commit phrases select
`commit_operation=commit-only`, `commit and push` selects
`commit_operation=commit-and-push`, and `push-only` selects
`commit_operation=push-only`.

For a commit-producing operation, default to `commit_kind=regular`. Select
`commit_kind=fixup|amend-fixup` only from an explicit user request or a
target-repository instruction. A review finding alone is not a selection
signal. Both targeted kinds require exact `target_commit` data.

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

## Targeted Fixup And Amend-Fixup

Use this path only after the normal index and diff guards. Resolve
`<skill-root>` from the active G entrypoint, then validate the target
before staging:

```bash
validator=<skill-root>/scripts/validate-fixup-target
target_sha=$("$validator" "$target_commit")
git show --stat --oneline --decorate --no-renames "$target_sha"
```

Stop if the reference does not resolve to exactly one commit, is not an
ancestor of `HEAD`, has a subject shared by another commit reachable from
`HEAD`, or the refinement does not map cleanly to that commit. The complete
reachable-history check is intentionally conservative because this workflow
does not own or know the base of a future autosquash. If independent changes
belong to different targets, split them by target. If the mapping remains
ambiguous, ask the user instead of guessing.

For `commit_kind=fixup`, stage and review the intended paths, then run:

```bash
git commit --fixup="$target_sha"
```

When the explicitly authorized path-limited workflow must preserve unrelated
staged entries, require the complete intended files to be staged with no
remaining unstaged hunks. Immediately before committing, run:

```bash
git diff --quiet -- <explicit-paths>
git diff --staged -- <explicit-paths>
git commit --only --fixup="$target_sha" -- <explicit-paths>
```

`git diff --quiet` must exit zero. Otherwise stop: `git commit --only` reads the
named paths from the working tree and would include unstaged changes. Partial
staging within an intended file is unsupported on this isolation path.

For `commit_kind=amend-fixup`, first re-read the target's complete message. Use
it only when the refinement makes that message inaccurate. Run:

```bash
git commit --fixup="amend:$target_sha"
```

The same path-limited isolation requires the identical quiet and staged-diff
guards immediately before
`git commit --only --fixup="amend:$target_sha" -- <explicit-paths>`.

In the editor, keep the generated `amend! <original subject>` matcher as the
first line and replace the following subject and body with the complete message
the target should have after a future autosquash.

For noninteractive execution, write a UTF-8 replacement-message file outside
the repository containing only the complete replacement subject and body:

```text
<replacement subject>

<replacement body>
```

Use `<skill-root>` from the active G entrypoint, then use the
bundled target-aware editor adapter while retaining Git's exact-target command:

```bash
helper=<skill-root>/scripts/replace-amend-fixup-message
G_AMEND_MESSAGE_FILE="$replacement_message_file" \
  GIT_EDITOR="$helper" \
  git commit --fixup="amend:$target_sha"
```

The adapter preserves the `amend!` matcher generated from `target_sha` and
replaces only the following subject and body. It rejects a missing matcher, an
empty replacement subject, or a replacement file that supplies its own
`amend!` line. Never replace this command with a plain `git commit -F`.

Verify the new commit message and target relationship with
`git log -1 --pretty=fuller`. The target commit remains unchanged and the new
fixup becomes `HEAD`. Push only for `commit_operation=commit-and-push`.

Never use `git commit --amend`, `git rebase --autosquash`, an interactive
rebase, or a force push as part of this workflow. The user or a separately
authorized repository workflow owns any later history rewrite. Because a
fixup creates a new head SHA, callers that require current-head CI or review
must rerun those gates after pushing it.

## Issue-Closing Commit And Push

Use for `commit_operation=commit-and-push` when the owner explicitly authorizes
committing directly to the current branch, pushing, and closing GitHub issues
through commit trailers instead of a PR. This is a
`commit_kind=regular` workflow, never a fixup or `push-only` path.

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
the `github-issues` workflow before committing or closing.
