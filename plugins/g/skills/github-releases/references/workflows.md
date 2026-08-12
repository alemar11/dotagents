# GitHub Release Workflows

## Readiness

```bash
git status --short --branch
git fetch --tags
git tag --list --sort=-version:refname | head -20
gh release list --limit 100 --json tagName,isLatest,isDraft,isPrerelease,publishedAt
gh release view <tag> --json tagName,name,body,isDraft,isImmutable,isPrerelease,publishedAt,url
```

Do not publish from a dirty or ambiguous checkout unless the user explicitly
confirms the release source.

## Target And Range

Require one exact existing tag before release creation. When `$g:versioning`
delegates the operation, preserve its verified tag and notes-start tag. Do not
replace them with a timestamp-derived tag, the current branch, or a locally
stale ref.

For an explicitly selected older tag, verify the remote ref and ensure the new
release will not become the repository's latest release. For an RC tag, create
a prerelease. If the tag already has a GitHub Release, do not attempt another
create operation; inspect or update that release instead.

Release creation never implies tag creation. If the requested tag is absent,
stop and obtain separate authority for `release_operation=create-tag` before
resuming release creation.

## Notes Planning

Generated release notes are a factual starting point, not an importance model.
Use the verified comparison start supplied by `$g:versioning`, or an explicit
existing start tag selected by the user. Preserve GitHub's contributor and full
changelog information. When the repository has `.github/release.yml`, honor its
label categories and exclusions.

Curate generated or repository-owned evidence into this shape, omitting empty
sections rather than inventing content:

```markdown
## Highlights

- The most important user-visible or compatibility changes.

## Breaking changes

- Required migration or compatibility impact.

## Features

- New user-visible capabilities.

## Fixes

- Important corrected behavior.

## Contributors

GitHub-generated contributor information.

**Full Changelog**: GitHub-generated comparison link.
```

Treat a change as a highlight only when supported by release documentation,
pull-request labels such as `highlight` or `breaking-change`, or clear
user-visible impact in the reviewed change. Do not infer importance from a
commit subject alone. Read maintained changelog content when applicable, but
do not make the application-code-blind versioning controller inspect project
files.

## Create A Tag

Use `release_operation=create-tag` only with explicit mutation authority:

Write the annotated-tag message to an absolute UTF-8 file without shell
interpolation, then use Git's file-backed message input:

```bash
git tag -a <tag> -F <absolute-release-title-file>
git push origin <tag>
git ls-remote --tags origin <tag>
```

## Default Draft

A plain request to create a release does not authorize immediate publication.
Generate and show the exact tag, title, comparison range, prerelease/latest
state, and Markdown body. After approval, create a draft with
`release_operation=draft`, then read it back. Draft creation is a remote
mutation and is never part of the preview.

Use generated notes when the project does not maintain hand-written release
notes:

```bash
gh release create <tag> --draft --generate-notes --verify-tag
```

For hand-written release names or notes, use the structured GitHub connector.
An existing genuinely file-backed `gh --notes-file` operation is allowed only
when no other free-form field is placed in argv. If the required field has no
safe connector or file-backed surface, fail closed; do not add a release
mutation command to G in this refinement.

## Direct Create And Publish

An explicit request to `create and publish` one release authorizes
`release_operation=publish` with `mutation_mode=apply`. Resolve and curate the
notes internally, then create the published release directly. Do not show a
notes preview, create a draft, or ask for another publication confirmation.

This shortcut does not relax any target checks. Require the exact existing tag,
verify the notes range, reject duplicate releases, preserve prerelease state,
and perform provider readback. It never authorizes creation of a missing tag.
For an explicitly selected historical stable tag, force the result not to be
latest. Prefer the structured GitHub connector for curated title and body
fields; use `gh release create --generate-notes --verify-tag` only when the
provider-generated title and body are accepted without free-form refinement.

Publishing an existing draft is also `release_operation=publish` and requires
explicit authority:

```bash
gh release edit <tag> --draft=false
```

## Improve Existing Notes

Use `release_operation=update-notes` for an existing release description:

1. Read the exact release identity, title, body, draft/prerelease/latest state,
   tag, and assets.
2. Prepare a complete replacement body and show the exact replacement or diff.
3. Ask for approval of that exact text update.
4. Update only the authorized title or notes. Preserve tag, target, draft,
   prerelease, latest, discussion, and asset state unless separately requested.
5. Read the release back and require the returned title and body to match.

Use the structured GitHub connector when available. A genuinely file-backed
CLI update is an allowed fallback when the body is the only free-form field:

```bash
gh release edit <tag> --notes-file <absolute-release-notes-file>
```

Published immutable releases may still accept title and notes changes, but do
not treat that as authority to mutate their protected tag or assets.

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

After creating, publishing, or updating notes, verify both GitHub and any
requested package channel:

```bash
gh release list --limit 100 --json tagName,isLatest,isDraft,isPrerelease,publishedAt
gh release view <tag> --json tagName,name,body,isDraft,isImmutable,isPrerelease,assets,publishedAt,url
git ls-remote --tags origin <tag>
```
