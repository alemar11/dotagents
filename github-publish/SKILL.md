---
name: github-publish
description: Open pull requests and manage PR lifecycle state through repo-owned `gh` helpers without staging, committing, branching, or pushing.
---

# GitHub Publish

## Overview

Use this skill when the job is to open a pull request or mutate PR lifecycle
state on GitHub. It owns current-branch PR opening, explicit PR creation, and
PR lifecycle changes such as draft, ready, merge, close, reopen, and checkout.

This skill is intentionally narrower than a full publish pipeline. Commit
authoring, branch creation, staging, and pushing stay with `git-commit`.

## Trigger rules

- Use when the user wants to open a PR from the current pushed branch, create
  a PR from explicit head/base refs, mark a PR draft/ready, merge, close,
  reopen, or check out a PR locally.
- Prefer `scripts/prs_open_current_branch.sh` when the request is about the
  already-pushed current branch.
- Use `scripts/prs_create.sh` when the user provides explicit PR parameters.
- Keep PR metadata edits such as title/body/base/labels/reviewers in umbrella
  `github`.

## Workflow

1. Resolve repository and, when relevant, PR scope first.
2. Use `scripts/prs_open_current_branch.sh` when the request is "open a PR
   from this pushed branch."
3. Use `scripts/prs_create.sh` when the user already knows `head` and `base`.
4. Use the PR lifecycle helpers for draft, ready, merge, close, reopen, or
   checkout flows.
5. Restate the exact repo, PR, branch, and side effects before mutation.
6. For `scripts/prs_checkout.sh`, call out explicitly that the local checkout
   will change.

## Guardrails

- Do not absorb staging, commit authoring, branch creation, or push
  orchestration.
- Stop when the current branch has no upstream or does not track a same-name
  remote branch for the current-branch helper.
- Keep review-thread work, CI debugging, release/tag work, issues, and
  reactions out of this skill.
- Keep cross-repo current-branch PR opening unsupported unless the general
  explicit `scripts/prs_create.sh` path is used.

## Fast paths

- Use `scripts/prs_open_current_branch.sh` for already-pushed current-branch
  PR opening.
- Use `scripts/prs_create.sh` for explicit PR creation.
- Use `scripts/prs_ready.sh`, `scripts/prs_draft.sh`, `scripts/prs_merge.sh`,
  `scripts/prs_close.sh`, and `scripts/prs_reopen.sh` for PR lifecycle
  mutations.

## Reference map

- `references/script-summary.md`: publish-owned helper catalog and flags.
- `references/workflows.md`: current-branch PR opening, PR lifecycle, and retry
  guidance.

## Examples

- "Open a draft PR from my current pushed branch."
- "Create a PR from branch feature/x into main."
- "Mark PR 482 ready for review."
- "Merge PR 482 with squash and delete the branch."
