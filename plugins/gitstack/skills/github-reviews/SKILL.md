---
name: github-reviews
description: Use when handling PR review threads.
---

# GitHub Reviews

## Overview

Use this bundled skill when the request is clearly about review comments,
review threads, replies, or submitting a review.

Prefer direct `gh` for simple review submission or top-level PR comments. Use
resolved `ghflow` when the job needs thread selection, reply routing, or shared
higher-level behavior. Keep reactions and mixed-domain GitHub work in the
umbrella `github` skill.

## Direct commands first

- `gh pr comment <n> --repo <owner/repo> --body <text>`
- `gh pr review <n> --repo <owner/repo> --approve`
- `gh pr review <n> --repo <owner/repo> --request-changes --body <text>`

## Use Resolved `ghflow` When

- the task is about review-thread inspection rather than a single top-level
  review submission
- the task needs reply routing to selected comments or thread rows
- the task benefits from shared fallback handling across review comment
  transports

Resolve `ghflow` with `../github/references/core/ghflow-resolution.md` before helper use.

## Fast path

- `<resolved-ghflow> --json reviews address --pr <n> --repo <owner/repo>`
- `gh pr comment <n> --repo <owner/repo> --body <text>`
- `gh pr review <n> --repo <owner/repo> --approve`

## Trigger rules

- Use for review-thread triage, reply drafting, reply posting, and review
  submission.
- Route reactions and non-review PR metadata back to `github`.
- Route CI failures to `github-ci`.

## References navigation

- Start at `references/script-summary.md` for the reviews command map.
- Open `references/workflows.md` for thread-triage, reply, and review-submit
  flows.
