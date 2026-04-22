# Yeet workflows

Use this reference for the composed full local-checkout publish flow inside the
`gitstack` plugin.

## full-publish

Purpose: turn a local worktree into a pushed branch plus a draft PR without
silently broadening scope.

### Preconditions

- You are inside a local git checkout of the target repository.
- `git-commit` and `github` are bundled alongside this skill.
- The target is the same repository as the current checkout.

### Operator policy

- Start with `git status -sb`.
- Run `ghflow --json publish context` from the target repo
  root before creating branches, commits, or pushes that are intended to end in
  a PR.
- If `git` or `gh` readiness is uncertain, confirm it directly with
  `command -v git`, `git --version`, `command -v gh`, `gh --version`, and
  `gh auth status`.
- If the worktree contains unrelated changes, do not default to `git add -A`.
- If on the default branch or detached `HEAD`, create a new short-lived branch
  before staging and keep the default branch as the PR base.
- If on a long-lived integration branch such as `stable`, `release/*`,
  `develop`, or `main`, create a new short-lived branch from it before staging
  and keep that long-lived branch as the PR base.
- If already on a non-default, non-long-lived local branch, keep that branch
  and keep all current changes there.
- Use `git-commit` for selective staging, commit creation, and sequential
  verification.
- Push with `git push -u origin <branch>` when no upstream exists, otherwise
  `git push origin <branch>`.
- Finish by handing off to `github` for publish-context inspection and
  current-branch PR opening or reuse through the shared `ghflow` runtime.
- Prefer a PR title that summarizes the full branch-level change.
- Prefer a structured, feature-level PR description with `Feature`, `Impact`,
  `Validation`, and optional `Follow-ups`.
- Use `--body-from-head` only when the latest commit body already follows that
  PR-ready structure; otherwise pass `--body` explicitly.

### Canonical sequence

```bash
git status -sb
ghflow --json publish context
```

Use direct readiness checks only when the runtime itself is suspect:

```bash
command -v git && git --version
command -v gh && gh --version
gh auth status
```

If on the default branch, detached `HEAD`, or a long-lived integration branch,
create a new short-lived branch first:

```bash
git switch -c <branch-prefix>/<slug>
```

Stage and commit through the bundled `git-commit` workflow, then push and open
or reuse the draft PR:

```bash
git push -u origin "$(git branch --show-current)"
ghflow publish open --draft [--title <text>] [--body-from-head] [--base <branch>]
```

### Retry notes

- `gh` install or auth checks fail before mutation: stop, fix the failure, then
  rerun the direct readiness checks from the target repo root.
- Repo or remote publishability checks fail before mutation: fix the checkout or
  remote wiring, then rerun `ghflow --json publish context`
  before continuing.
- Current branch has no upstream yet: run
  `git push -u origin "$(git branch --show-current)"`.
- Existing PR already open for this branch: `github` should reuse it instead of
  creating a duplicate.
- Existing PR already open for this branch but targeting the wrong base:
  rerun the open-or-reuse helper with the intended `--base` and update the PR
  base instead of silently reusing the wrong target.
- Mixed unrelated worktree changes: stop, narrow scope, and use explicit
  pathspec staging.
