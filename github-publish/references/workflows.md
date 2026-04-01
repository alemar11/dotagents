# GitHub publish workflows

Use this reference for current-branch publish context inspection, current-branch
PR opening or reuse, and PR lifecycle mutations.

## publish-context

Purpose: inspect whether the current branch is ready for PR opening and whether
an open PR already exists.

### Preconditions

- `gh` installed and authenticated.
- You are inside a local git checkout of the target repository.

### Operator policy

- Use this helper before mutation when the branch, upstream, or open-PR state
  is not already known.
- Prefer it as the post-push handoff point from `yeet`.

### Preferred helper

```bash
scripts/publish_context.sh [--repo <owner/repo>] [--json]
```

## pr-open-current-branch

Purpose: open or reuse a PR from the already-pushed current branch without
staging, committing, or pushing.

### Preconditions

- `gh` installed and authenticated.
- Run `scripts/preflight_gh.sh --expect-repo <owner/repo>` from the target repo
  root before mutation.
- The current branch is pushed to a same-name remote branch.

### Operator policy

- Prefer `scripts/publish_context.sh` first when the branch, upstream, or
  open-PR state is not already obvious.
- Prefer `scripts/prs_open_current_branch.sh` when the request is about the
  current pushed branch.
- Stop when the branch has no upstream or the upstream branch name differs from
  the local branch name.
- Reuse an existing open PR for the current branch instead of creating a
  duplicate.
- Do not stretch this flow into staging, commit creation, branch creation, or
  pushing.
- If the user wants the full local-checkout publish flow, route to `yeet`
  instead of composing it from this skill.

### Preferred helper

```bash
scripts/prs_open_current_branch.sh [--title <text>] [--body <text>] [--body-from-head] [--base <branch>] [--draft] [--repo <owner/repo>] [--dry-run]
```

## pr-lifecycle

Purpose: create a PR from explicit refs or mutate existing PR lifecycle state.

### Operator policy

- Use `scripts/prs_create.sh` when `head` and `base` are explicit.
- Use `scripts/prs_draft.sh`, `scripts/prs_ready.sh`, `scripts/prs_merge.sh`,
  `scripts/prs_close.sh`, and `scripts/prs_reopen.sh` for remote lifecycle
  mutations.
- Use `scripts/prs_checkout.sh` only when the local checkout side effect is
  acceptable and has been restated to the user.
- Keep PR metadata edits in umbrella `github`.

### Preferred helpers

```bash
scripts/prs_create.sh --title <text> [--body <text>] [--base <branch>] [--head <branch>] [--draft] [--labels <label1,label2>] [--repo <owner/repo>]
scripts/prs_ready.sh --pr <number> [--repo <owner/repo>]
scripts/prs_draft.sh --pr <number> [--repo <owner/repo>]
scripts/prs_merge.sh --pr <number> [--merge|--squash|--rebase] [--delete-branch] [--admin] [--auto] [--repo <owner/repo>]
scripts/prs_close.sh --pr <number> [--repo <owner/repo>]
scripts/prs_reopen.sh --pr <number> [--repo <owner/repo>]
scripts/prs_checkout.sh --pr <number> [--branch <name>] [--detach] [--force] [--recurse-submodules] [--repo <owner/repo>]
```

## Retry notes

- Auth/session errors: `gh auth login && scripts/preflight_gh.sh --host github.com`
- Repository mismatch errors: rerun
  `scripts/preflight_gh.sh --host github.com --expect-repo owner/repo` from
  the target repo root.
- Current branch has no upstream or same-name remote branch: run
  `git push -u origin $(git branch --show-current)` from the target repo root,
  then rerun `scripts/publish_context.sh` or `scripts/prs_open_current_branch.sh`.
- Detached HEAD during current-branch PR opening: switch back to a branch
  first, then rerun the helper.
