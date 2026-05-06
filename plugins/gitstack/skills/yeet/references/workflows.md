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
- Resolve the installed `ghflow` artifact first with
  `../../github/references/core/ghflow-resolution.md`; do not assume the bare
  command is on `PATH`.
- Run `<resolved-ghflow> --json publish context` from the target repo
  root before creating branches, commits, or pushes that are intended to end in
  a PR.
- If the user named an explicit PR base, lock it immediately and carry it
  through the rest of the publish flow.
- If the installed artifact path cannot be resolved, stop and treat the
  runtime as a broken GitStack install.
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
- Always pass `--base <locked-base>` when the user request or branch strategy
  established a specific PR base.
- Verify the final PR base before closing the workflow with
  `gh pr view --json baseRefName,url,isDraft` or an equivalent
  current-branch lookup.
- Prefer a PR title that summarizes the full branch-level change.
- Prefer a structured, feature-level PR description with `Feature`, `Impact`,
  `Validation`, and optional `Follow-ups`.
- Use `--body-from-head` only when the latest commit body already follows that
  PR-ready structure; otherwise pass `--body` explicitly.

### Canonical sequence

```bash
git status -sb
resolved_ghflow="$(find "$HOME/.codex/plugins/cache" -path '*/gitstack/*/scripts/ghflow' -type f 2>/dev/null | sort | tail -n 1)"
test -n "$resolved_ghflow" && test -x "$resolved_ghflow"
"$resolved_ghflow" --json publish context
```

Use `"$resolved_ghflow" ...` for later commands shown as
`<resolved-ghflow> ...`.

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
<resolved-ghflow> publish open --draft [--title <text>] [--body-from-head] [--base <branch>]
gh pr view --json baseRefName,url,isDraft
```

### Retry notes

- `gh` install or auth checks fail before mutation: stop, fix the failure, then
  rerun the direct readiness checks from the target repo root.
- Bare `ghflow` is unavailable in the current shell:
  this is expected in embedded-host usage; run the resolved installed artifact
  path instead.
- The installed artifact path cannot be resolved:
  stop and treat the runtime as broken install or plugin exposure drift.
- Repo or remote publishability checks fail before mutation: fix the checkout or
  remote wiring, then rerun `<resolved-ghflow> --json publish context`
  before continuing.
- Current branch has no upstream yet: run
  `git push -u origin "$(git branch --show-current)"`.
- Existing PR already open for this branch: `github` should reuse it instead of
  creating a duplicate.
- Existing PR already open for this branch but targeting the wrong base:
  rerun the open-or-reuse helper with the intended `--base`; if a direct fix is
  needed, use `gh pr edit <n> --base <branch>` or the narrow
  `gh api -X PATCH repos/<owner>/<repo>/pulls/<n> -f base=<branch>`
  instead of silently reusing the wrong target.
- Mixed unrelated worktree changes: stop, narrow scope, and use explicit
  pathspec staging.
