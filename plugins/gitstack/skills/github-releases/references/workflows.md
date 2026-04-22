# GitHub release workflows

Use this reference for release-backed tag and release publication flows.

## Inspect release base

- Default branch:
  `gh repo view --repo <owner/repo> --json defaultBranchRef`
- Last published release:
  `gh release list --repo <owner/repo> --exclude-drafts --exclude-pre-releases --limit 1`

## Generate notes

```bash
gh api repos/<owner>/<repo>/releases/generate-notes -X POST -f tag_name=<tag> -f target_commitish=<branch-or-sha> [-f previous_tag_name=<tag>]
```

## Publish release-backed tag

```bash
gh release create <tag> --repo <owner/repo> --target <branch-or-sha> --generate-notes
```
