# GitHub release command summary

Use this as the authoritative releases-domain command map referenced by the
bundled `github-releases` skill.

## Direct `git` and `gh` commands

- `gh repo view --repo <owner/repo> --json defaultBranchRef`
- `gh release list --repo <owner/repo> --exclude-drafts --exclude-pre-releases --limit 1`
- `gh api repos/<owner>/<repo>/releases/generate-notes -X POST -f tag_name=<tag> -f target_commitish=<branch-or-sha>`
- `gh release create <tag> --repo <owner/repo> --target <branch-or-sha> --generate-notes`
