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

Write the annotated-tag message to an absolute UTF-8 file without shell
interpolation, then use Git's file-backed message input:

```bash
git tag -a <tag> -F <absolute-release-title-file>
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

For hand-written release names or notes, use the structured GitHub connector.
An existing genuinely file-backed `gh --notes-file` operation is allowed only
when no other free-form field is placed in argv. If the required field has no
safe connector or file-backed surface, fail closed; do not add a release
mutation command to G in this refinement.

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
