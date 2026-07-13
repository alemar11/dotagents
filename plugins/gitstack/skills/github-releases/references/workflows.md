# GitHub Release Workflows

## Readiness

```bash
git status --short --branch
git fetch --tags
git tag --list --sort=-version:refname | head -20
gh release list --limit 20
gh release view <tag> --json tagName,name,isDraft,isPrerelease,publishedAt,url
```

Do not publish from a dirty or ambiguous checkout unless the user explicitly
confirms the release source.

## Create A Tag

Use `release_operation=create-tag` only with explicit mutation authority:

```bash
git tag -a <tag> -m "<release title>"
git push origin <tag>
git ls-remote --tags origin <tag>
```

## Draft Or Publish

Use generated notes when the project does not maintain hand-written release
notes:

```bash
gh release create <tag> --draft --generate-notes
gh release edit <tag> --draft=false
```

For asset uploads:

```bash
gh release upload <tag> <asset-path> --clobber
```

This is `release_operation=upload-asset`. Verify the named asset through
`gh release view` after upload.

## Delete A Release

Use `release_operation=delete` only when the user explicitly authorizes the
exact release deletion. Tag deletion is a separate mutation and is not implied.

```bash
gh release delete <tag> --yes
gh release view <tag>
```

The verification command should fail with a not-found result after a successful
deletion; inspect `gh release list` if the result is ambiguous.

## Verification

After publishing, verify both GitHub and any requested package channel:

```bash
gh release view <tag> --json tagName,name,isDraft,isPrerelease,assets,publishedAt,url
git ls-remote --tags origin <tag>
```
