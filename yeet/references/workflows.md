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
- If the worktree contains unrelated changes, do not default to `git add -A`.
- If on the default branch or detached `HEAD`, create `topic/<slug>` before
  staging.
- If already on a non-default local branch, keep that branch and keep all
  current changes there.
- Use `git-commit` for selective staging, commit creation, and sequential
  verification.
- Push with `git push -u origin <branch>` when no upstream exists, otherwise
  `git push origin <branch>`.
- Finish by handing off to `github` for publish-context inspection and
  current-branch PR opening or reuse.

### Companion skills

- `git-commit`: stage intentionally, create the commit, and verify it.
- `github`: inspect post-push publish context and open or reuse the PR through
  its `publish` domain.

### Canonical sequence

```bash
git status -sb
```

If on the default branch or detached `HEAD`, create a topic branch first:

```bash
git switch -c topic/<slug>
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
# 2. scripts/publish/prs_open_current_branch.sh --draft --body-from-head
```

### Retry notes

- Current branch has no upstream yet: run `git push -u origin "$(git branch --show-current)"`.
- Existing PR already open for this branch: `github` should reuse it instead
  of creating a duplicate.
- Mixed unrelated worktree changes: stop, narrow scope, and use explicit pathspec staging.
