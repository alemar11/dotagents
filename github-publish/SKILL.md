---
name: github-publish
description: Open pull requests and manage PR lifecycle state through repo-owned `gh` helpers without staging, committing, branching, or pushing.
---

# GitHub Publish

## Overview

Use this skill when the job is to open a pull request or mutate PR lifecycle
state on GitHub. It owns current-branch publish context inspection, current-branch
PR opening or reuse, explicit PR creation, and PR lifecycle changes such as
draft, ready, merge, close, reopen, and checkout.

This skill is intentionally narrower than a full publish pipeline. When the
user wants branch creation, staging, commit authoring, push, and PR opening as
one flow, route to `yeet` instead. `github-publish` starts after the branch is
already ready or pushed and is the post-push companion that `yeet` hands off
to.

## Trigger rules

- Use when the user wants to open a PR from the current pushed branch, create
  a PR from explicit head/base refs, mark a PR draft/ready, merge, close,
  reopen, or check out a PR locally.
- Use `scripts/publish_context.sh` when the user needs to know whether the
  current branch is pushed, tracks a same-name remote branch, or already has an
  open PR.
- Route full publish-from-worktree requests to `yeet`.
- Prefer `scripts/prs_open_current_branch.sh` when the request is about the
  already-pushed current branch and should open or reuse the PR.
- Use `scripts/prs_create.sh` when the user provides explicit PR parameters.
- Keep PR metadata edits such as title/body/base/labels/reviewers in umbrella
  `github`.

## Workflow

1. Resolve repository and, when relevant, PR scope first.
2. Use `scripts/publish_context.sh` when branch/upstream/open-PR state needs to
   be confirmed before mutation.
3. Use `scripts/prs_open_current_branch.sh` when the request is "open or reuse
   the PR from this pushed branch."
4. Use `scripts/prs_create.sh` when the user already knows `head` and `base`.
5. Use the PR lifecycle helpers for draft, ready, merge, close, reopen, or
   checkout flows.
6. Restate the exact repo, PR, branch, and side effects before mutation.
7. For `scripts/prs_checkout.sh`, call out explicitly that the local checkout
   will change.

## Guardrails

- Do not absorb staging, commit authoring, branch creation, or push
  orchestration.
- When the user wants the full local-checkout publish flow, stop and route to
  `yeet` instead of composing it here.
- Stop when the current branch has no upstream or does not track a same-name
  remote branch for the current-branch helper.
- Reuse an existing open PR for the current branch instead of creating a
  duplicate.
- Keep review-thread work, CI debugging, release/tag work, issues, and
  reactions out of this skill.
- Keep cross-repo current-branch PR opening unsupported unless the general
  explicit `scripts/prs_create.sh` path is used.

## Fast paths

- Use `scripts/publish_context.sh` for already-pushed current-branch context.
- Use `scripts/prs_open_current_branch.sh` for already-pushed current-branch
  PR opening or reuse.
- Use `scripts/prs_create.sh` for explicit PR creation.
- Use `scripts/prs_ready.sh`, `scripts/prs_draft.sh`, `scripts/prs_merge.sh`,
  `scripts/prs_close.sh`, and `scripts/prs_reopen.sh` for PR lifecycle
  mutations.

## Reference map

- `references/script-summary.md`: publish-owned helper catalog and flags.
- `references/workflows.md`: publish-context inspection, current-branch PR
  opening or reuse, PR lifecycle, and retry guidance.

## Examples

- "Show me whether this branch already has a PR."
- "Open or reuse the draft PR from my current pushed branch."
- "Create a PR from branch feature/x into main."
- "Mark PR 482 ready for review."
- "Merge PR 482 with squash and delete the branch."
