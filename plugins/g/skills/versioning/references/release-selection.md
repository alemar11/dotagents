# GitHub Release tag selection

Read this reference when the requested outcome is a GitHub Release, release
notes, release assets, or a release-description update. This file owns only
existing-tag and comparison-range selection; `$g:github-releases` owns the
release lifecycle and mutations.

Verify provider-owned tags and releases first. A release request never implies
tag creation. If the requested tag is absent, stop and route the new tag
through the versioning preview and exact-tag confirmation gate before returning
to release creation.

When the user omits the tag, select the highest existing canonical stable tag
by SemVer precedence. Do not select by tag timestamp, release date, current
branch, or newest RC. If no canonical stable tag exists, stop rather than
guessing or weakening the canonical gate.

An explicitly selected canonical tag may target an older release. A stable
`vX.Y.Z` selects a normal release; `vX.Y.Z-rc.N` selects a prerelease. An older
stable release must not replace the repository's current latest release.
Legacy or otherwise noncanonical tags remain outside this skill's release
mutation path and may be inspected without treating them as canonical.

For generated notes, select the previous relevant canonical tag as the
comparison start: the previous stable tag for a stable release, or the previous
same-line RC for a prerelease. Verify both refs and the range. If there is no
unambiguous predecessor, report that fact and let the user select an explicit
existing start tag.

After resolving the exact existing tag and comparison range, read and follow
the [$g:github-releases workflow](../../github-releases/references/workflows.md),
which remains the canonical owner of the release lifecycle.
