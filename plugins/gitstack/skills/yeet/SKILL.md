---
name: yeet
description: Orchestrate the full publish flow from a local checkout by using `git` for branch and push work, bundled `git-commit` for commit discipline, and bundled `github` plus shared `ghflow` publish helpers only where repo-aware PR orchestration is justified.
---

# Yeet

## Overview

Use this skill when the user explicitly wants the full publish flow from a
local checkout: inspect scope, create a branch if needed, stage intentionally,
commit, push, and open or reuse a draft pull request.

Inside `gitstack`, this skill is intentionally composed:

- `git-commit` owns selective staging, commit authoring, and post-commit
  verification.
- `github` owns already-pushed-branch PR lifecycle work.
- `ghflow` is the shared installed helper artifact for publish-context and
  publish-open operations that multiple GitStack skills reuse.

Keep v1 intentionally narrow:

- same-repo publish only
- no fork-head or cross-repo PR semantics
- no organization-level GitHub actions
- no silent staging of unrelated changes

## Trigger rules

- Use when the user says `yeet` or asks to publish the current worktree from a
  local checkout.
- Use when the request is "commit, push, and open a PR", "publish my current
  branch", or "turn these local changes into a draft PR".
- Keep the current branch only when it is already a non-default, non-long-lived
  local branch.
- Create a new short-lived branch when starting from the repository default
  branch, detached `HEAD`, or a long-lived integration branch such as
  `stable`, `release/*`, `develop`, or `main`.
- Route directly to `github` when commit and push are already done, or when
  the request is PR-only lifecycle work.

## Workflow

1. Confirm scope before mutating anything.
   - Start with `git status -sb`.
   - Resolve the current branch, detached-HEAD state, and whether you are still
     on the repository default branch.
   - Resolve the installed `ghflow` artifact first. Prefer bare `ghflow` only
     when `command -v ghflow` succeeds; otherwise resolve the installed
     GitStack artifact path and run that path directly.
   - Run the resolved `ghflow --json publish context` command from the target
     repo root before creating branches, commits, or pushes that are intended
     to end in a PR.
   - If the user already named a PR base such as `stable`, treat that as
     locked publish intent for the rest of the workflow instead of letting a
     later helper choose a different base.
   - If neither bare `ghflow` nor the installed artifact path can be resolved,
     stop and treat the runtime as a broken GitStack install instead of
     continuing with an alternate publish path.
   - If `git` or `gh` readiness is uncertain, confirm it directly with
     `command -v git`, `git --version`, `command -v gh`, `gh --version`, and
     `gh auth status`.
2. Pick branch strategy.
   - If step 1 captured explicit PR base intent from the user, keep that base
     locked even if the helper would otherwise recommend the repository
     default branch.
   - If on the repo default branch or detached `HEAD`, create a new short-lived
     branch before staging and treat the repo default branch as the PR base.
   - If on a long-lived non-default branch, create a new short-lived branch
     from it before staging and remember that original long-lived branch as the
     PR base.
   - If already on a non-default, non-long-lived local branch, keep that branch
     and keep all current changes there.
3. Stage intentionally.
   - Hand off to `git-commit` for selective staging when the worktree is mixed.
   - Use `git add -A` only when the whole worktree is confirmed in scope.
4. Commit with a well-formed message.
   - Hand off to `git-commit` for commit message structure and sequential
     post-commit verification.
5. Push the branch.
   - If there is no upstream, use `git push -u origin <branch>`.
   - Otherwise use `git push origin <branch>`.
6. Open or reuse the draft PR.
   - Hand off to `github` for publish-context inspection plus current-branch PR
     opening or reuse through the resolved `ghflow publish open` artifact.
   - If step 1 or step 2 captured a locked PR base, always pass it with
     `--base <branch>` on create or reuse flows instead of letting the helper
     fall back to the repository default branch.
   - Let `github` reuse an existing open PR for the current branch
     instead of creating a duplicate.
   - If an existing PR for the current branch targets the wrong base, update it
     explicitly instead of silently reusing it with the wrong target.
   - Prefer a PR title that summarizes the full branch-level change, not just
     the latest commit.
   - Prefer a structured, feature-level description with `Feature`, `Impact`,
     `Validation`, and optional `Follow-ups`.
   - Use `--body-from-head` only when the latest commit body already follows
     that PR-ready structure; otherwise pass `--body` explicitly.
   - Before closing the workflow, verify the final PR target with
     `gh pr view --json baseRefName,url,isDraft` or an equivalent
     current-branch lookup.

## Guardrails

- Never stage unrelated user changes silently.
- Never publish directly from a long-lived branch such as `stable` or
  `release/*`; branch off it and keep that branch as the PR base.
- Never let explicit PR-base intent drift after it has been established from
  the user request or branch strategy; treat it as locked through PR
  verification.
- Never push without confirming scope when the worktree is mixed.
- Never start branch, commit, or push mutations for a PR-intended flow until
  the resolved `ghflow --json publish context` command has passed from the
  target repo root.
- Never treat missing bare `ghflow` as a normal publish branch. Resolve the
  installed GitStack artifact path explicitly; if that also fails, stop and
  treat it as broken install or runtime drift.
- Default to a draft PR unless the user explicitly asks for a ready PR.
- Stop if the repo is not connected to an accessible same-repo GitHub remote.
- Do not vendor or duplicate the bundled `git-commit` or `github` helper
  layers here.

## Fast paths

- Use `git-commit` directly when the job is "make a good commit" without the
  surrounding publish flow.
- Use `github` directly when the branch is already pushed and the only
  remaining step is PR opening or reuse.
- Use plain `git` and `gh` directly for one-off branch or PR tasks that do not
  need the full publish orchestration.
- Use `references/workflows.md` for the full local-checkout publish sequence.

## Examples

- "Yeet this worktree."
- "Publish my current branch as a draft PR."
- "I'm on `main`; branch safely, commit this, and open the PR."
- "Commit, push, and open or reuse the PR for these local changes."
