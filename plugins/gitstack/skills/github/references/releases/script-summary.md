# GitHub release command summary

Use this as the authoritative releases-domain command map referenced by the
bundled `github` skill.

## Direct `git` and `gh` commands

- `gh repo view --repo <owner/repo> --json defaultBranchRef`
- `gh release list --repo <owner/repo> --exclude-drafts --exclude-pre-releases --limit 1`
- `gh api repos/<owner>/<repo>/releases/generate-notes -X POST -f tag_name=<tag> -f target_commitish=<branch-or-sha>`
- `gh release create <tag> --repo <owner/repo> --target <branch-or-sha> --generate-notes`

## Package availability checks

- `gh run list --repo <owner/repo> --workflow Release --limit 5`
- `python3 -m pip index versions <package> --no-cache-dir`
- `brew info <owner>/tap/<formula>`
- `gh run list --repo <owner>/homebrew-tap --limit 5`
