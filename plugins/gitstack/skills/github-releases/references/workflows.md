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

## Verification

After publishing, verify both GitHub and any requested package channel:

```bash
gh release view <tag> --json tagName,name,isDraft,isPrerelease,assets,publishedAt,url
git ls-remote --tags origin <tag>
```
