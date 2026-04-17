# Yeet workflows

Use this reference for the composed full local-checkout publish flow.

## full-publish

Purpose: turn a local worktree into a pushed branch plus a draft PR without
silently broadening scope.

### Preconditions

- You are inside a local git checkout of the target repository.
- `git-commit` and `github` are installed as companion skills.
- The target is the same repository as the current checkout.

### Operator policy

- Start with `git status -sb`.
- Run `skills/github/scripts/core/preflight_gh.sh` from the target repo root before
  creating branches, commits, or pushes that are intended to end in a PR.
- If the worktree contains unrelated changes, do not default to `git add -A`.
- If on the default branch or detached `HEAD`, create a new short-lived branch
  before staging and keep the default branch as the PR base.
- If on a long-lived integration branch such as `stable`, `release/*`,
  `develop`, or `main`, create a new short-lived branch from it before staging
  and keep that long-lived branch as the PR base.
- If already on a non-default, non-long-lived local branch, keep that branch
  and keep all current changes there.
- Use the active repo or runtime branch-prefix convention for the new branch
  instead of hardcoding `topic/`.
- Use `git-commit` for selective staging, commit creation, and sequential
  verification.
- Push with `git push -u origin <branch>` when no upstream exists, otherwise
  `git push origin <branch>`.
- Finish by handing off to `github` for publish-context inspection and
  current-branch PR opening or reuse from the target repo root.
- Prefer a PR title that summarizes the full branch-level change. If the
  latest commit subject is narrower than the intended PR scope, pass
  `--title <text>` explicitly instead of inheriting it from `HEAD`.
- Prefer a structured, feature-level PR description with `Feature`, `Impact`,
  `Validation`, and optional `Follow-ups`.
- Use `--body-from-head` only when the latest commit body already follows that
  PR-ready structure; otherwise pass `--body` explicitly.

### Companion skills

- `git-commit`: stage intentionally, create the commit, and verify it.
- `github`: inspect post-push publish context and open or reuse the PR through
  its `publish` domain.

### Canonical sequence

```bash
git status -sb
skills/github/scripts/core/preflight_gh.sh
```

Inspect publish context when branch strategy or PR base is not already obvious:

```bash
skills/github/scripts/publish/publish_context.sh --json
```

If on the default branch, detached `HEAD`, or a long-lived integration branch,
create a new short-lived branch first:

```bash
git switch -c <branch-prefix>/<slug>
```

Stage and commit through the `git-commit` workflow:

```bash
# Use `git-commit` here for selective staging, commit authoring, and
# post-commit verification.
```

Push, then open or reuse the draft PR:

```bash
git push -u origin "$(git branch --show-current)"
# Then use `github`:
# 1. scripts/publish/publish_context.sh
# 2. scripts/publish/prs_open_current_branch.sh --draft [--title <text>] --body-from-head [--base <branch>]
```

Suggested PR title shape:

```text
<macro summary of the full branch-level change>
```

Suggested PR body shape when using `--body-from-head` or `--body`:

```text
Feature:
- <macro summary of the feature, fix, or behavior change>

Impact:
- <user-facing effect, API behavior, or operational effect>

Validation:
- <command or "not run (reason)">

Follow-ups:
- <optional rollout note, TODO, or risk>
```

### Retry notes

- `gh` install or auth checks fail before mutation: stop, fix the failure, then
  rerun `skills/github/scripts/core/preflight_gh.sh` from the target repo root before
  continuing.
- Current branch has no upstream yet: run `git push -u origin "$(git branch --show-current)"`.
- Existing PR already open for this branch: `github` should reuse it instead
  of creating a duplicate.
- Existing PR already open for this branch but targeting the wrong base:
  rerun the open-or-reuse helper with the intended `--base` and update the PR
  base instead of silently reusing the wrong target.
- Mixed unrelated worktree changes: stop, narrow scope, and use explicit pathspec staging.
