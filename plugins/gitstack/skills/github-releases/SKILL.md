---
name: github-releases
description: Handle focused GitHub release work inside `gitstack`. Use plain `git` and `gh` for release-backed tags, notes, and publication; this skill is guidance-first and does not rely on a dedicated `ghflow` release surface.
---

# GitHub Releases

## Overview

Use this bundled skill when the request is about release-backed tags, notes
generation, release planning, or release publication.

Use plain `git` and `gh` for tag-only and release-backed flows. This skill now
acts as routing and workflow guidance rather than a separate `ghflow` command
surface. Keep tag-only or local publish orchestration decisions aligned with
the umbrella `github` skill and `yeet`.

## Direct commands first

- `git tag <tag> <sha>`
- `gh release view <tag> --repo <owner/repo>`
- `gh release create <tag> --repo <owner/repo> ...`
- `gh release create <tag> --repo <owner/repo> --generate-notes`

## Fast path

- `gh repo view --repo <owner/repo> --json defaultBranchRef`
- `gh release list --repo <owner/repo> --exclude-drafts --exclude-pre-releases --limit 1`
- `gh api repos/<owner>/<repo>/releases/generate-notes -X POST -f tag_name=<tag> -f target_commitish=<branch-or-sha>`
- `gh release create <tag> --repo <owner/repo> --target <branch-or-sha> --generate-notes`

## Trigger rules

- Use for release planning, notes generation, and release publication.
- Resolve target refs explicitly; do not guess `main`.
- Keep generic GitHub routing in the umbrella `github`.

## References navigation

- Start at `references/script-summary.md` for the releases command map.
- Open `references/workflows.md` for release-backed tag and notes flows.
