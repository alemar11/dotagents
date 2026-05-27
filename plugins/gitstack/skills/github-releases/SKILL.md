---
name: github-releases
description: Use when checking GitHub or package releases.
---

# GitHub Releases

## Overview

Use this bundled skill when the request is about release-backed tags, notes
generation, release planning, or release publication.

Use plain `git` and `gh` for tag-only and GitHub Release flows. GitHub
Releases are not the same as package-registry availability; when users ask
whether a release exists on PyPI, npm, Homebrew, or another distributor, verify
that registry separately.

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
- Use for package-release verification when the user asks whether a release is
  available from a package registry or Homebrew tap.
- Resolve target refs explicitly; do not guess `main`.
- Keep generic GitHub routing in the umbrella `github`.

## References navigation

- Start at `references/script-summary.md` for the releases command map.
- Open `references/workflows.md` for release-backed tag and notes flows.
