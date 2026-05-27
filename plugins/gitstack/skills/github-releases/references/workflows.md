# GitHub release workflows

Use this reference for release-backed tag, GitHub Release publication, and
package-distribution verification flows.

## Boundary

GitHub tags and GitHub Releases do not prove package availability. If the user
asks whether a release exists on PyPI, Homebrew, npm, or another distributor,
verify the registry or tap directly after checking GitHub state.

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

## Verify tag-driven package release

Use these checks for repositories where a tag-driven workflow publishes
artifacts and then updates a package index or Homebrew tap:

```bash
gh run list --repo <owner/repo> --workflow Release --limit 5
gh run view <run-id> --repo <owner/repo> --json status,conclusion,jobs,url
git ls-remote --tags origin | rg 'refs/tags/<tag>$'
```

For PyPI:

```bash
python3 -m pip index versions <package> --no-cache-dir | sed -n '1,3p'
```

For Homebrew taps:

```bash
brew info <owner>/tap/<formula>
gh run list --repo <owner>/homebrew-tap --limit 5
```

When validating Python formula resources immediately after publishing to PyPI,
remember that Homebrew may ask pip to ignore files uploaded in the last 24
hours. If dependency pins did not change, updating only the formula URL and
checksum may be enough; let `brew audit`, source install, and `brew test`
decide whether the existing resource blocks are still valid.
