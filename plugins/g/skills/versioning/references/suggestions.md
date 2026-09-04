# Suggestion workflow

Read this reference when calculating the next patch, minor, major, candidate,
or final tag. The helper is read-only and reads local Git tags by default; it
does not fetch or mutate provider state. Refresh the tag view before using it
when remote state may be newer.

## Default-branch proposals

In `main` mode, the helper resolves the highest stable SemVer tag as the
increment baseline and proposes:

- `patch`: `vX.Y.(Z+1)-rc.1`;
- `minor`: `vX.(Y+1).0-rc.1`;
- `major`: `v(X+1).0.0-rc.1`.

Unrelated RC lines do not change the stable baseline or block other lines. If
a proposed line already has RC tags, the helper calculates its next candidate
and marks only that line `release-in-progress`; continue that line from its
`release/vX.Y.Z` branch instead of creating another tag from the default
branch. If RC tags exist without a stable baseline, report those active lines
without deriving patch, minor, or major proposals from an unstable version.

If no SemVer tags exist, do not infer a historical version. The default branch
gets the bootstrap proposal `v0.1.0-rc.1`. When the user supplies an initial
version, pass it as `--initial-version X.Y.Z` and show its corresponding
candidate instead.

## Release-branch proposals

For `release/vX.Y.Z`, propose:

- `candidate`: the next unused `vX.Y.Z-rc.N`;
- `final`: `vX.Y.Z`.

A final does not require a prior candidate unless an explicit repository
policy says otherwise. If the stable tag already exists, both operations are
blocked; never remove it to restart the candidate sequence. The release branch
itself supplies enough version context when no other tags exist.

Interpret `available`, `bootstrap-required`, `release-in-progress`,
`finalized`, and every blocking result through [the state registry](states.md)
rather than creating another status vocabulary.

## Helper usage

```bash
scripts/version-suggestions --mode main --json
scripts/version-suggestions --mode main --initial-version 2.3.0 --json
scripts/version-suggestions --mode release --line release/v2.4.0 --json
scripts/version-suggestions --mode main --tag v2.3.1-rc.2
scripts/version-suggestions --mode validate --application-tag v2.4.0-rc.1 --json
```

For deterministic automation or tests, pass one or more `--tag` values or a
`--tags-file` instead of reading the current repository. A finalized line may
exit successfully with no suggestions; its JSON state explains the result.
Validate mode exits nonzero for `blocked-noncanonical`.
