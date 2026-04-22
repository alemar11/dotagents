---
name: github-ci
description: Handle focused GitHub CI work inside `gitstack`. Use plain `gh` for PR checks, Actions run inspection, and logs; this skill is guidance-first and does not rely on a dedicated `ghflow` CI surface.
---

# GitHub CI

## Overview

Use this bundled skill when the request is about failing checks, GitHub Actions
runs, or log-oriented CI triage.

Use plain `gh` commands for check reads, run inspection, and logs. This skill
now exists as routing and workflow guidance rather than a separate `ghflow`
command surface. Keep review-thread work in `github-reviews` and publish
lifecycle work in the umbrella `github`.

## Direct commands first

- `gh pr checks <n> --repo <owner/repo>`
- `gh run list --repo <owner/repo>`
- `gh run view <run-id> --repo <owner/repo>`

## Fast path

- `gh pr checks <n> --repo <owner/repo>`
- `gh run list --repo <owner/repo>`
- `gh run view <run-id> --repo <owner/repo>`
- `gh run view <run-id> --repo <owner/repo> --log-failed`

## Trigger rules

- Use for PR checks and generic Actions investigation.
- Distinguish PR-associated failures from generic branch, SHA, workflow, or
  explicit run-id investigations.
- Route release publication back to `github-releases`.

## References navigation

- Start at `references/script-summary.md` for the CI command map.
- Open `references/workflows.md` for PR-check triage and generic Actions flows.
