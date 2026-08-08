---
name: versioning
description: Apply the shared SemVer tag and release-line convention, calculate context-aware suggestions, and plan safe legacy-tag migrations.
---

# Versioning

Use this skill when a project needs a release version, a Git tag, a release
branch, or the next candidate suggestions for a release workflow.

This skill owns the convention, read-only calculation, and explicit migration
of stable legacy tags. It never moves or deletes a tag. The helper only creates
previews; applying any tag is a mutation and always requires a separate,
explicit confirmation after the exact proposal has been shown. Creating a new
canonical alias is a remote mutation and requires the same confirmation; the
skill must verify the source and target commits before and after the create
operation.

## Canonical convention

Use SemVer 2.0.0 with a `v` prefix on new Git tags:

```text
vX.Y.Z
vX.Y.Z-rc.N
```

Where:

- `X` is the major version for incompatible changes;
- `Y` is the minor version for backward-compatible features;
- `Z` is the patch version for backward-compatible fixes;
- `rc.N` is a progressive release candidate number starting at `1`.

Examples:

```text
v2.4.0-rc.1
v2.4.0-rc.2
v2.4.0
```

Use `release/vX.Y.Z` for the corresponding stabilization branch. Do not use
`rc01`, `rc.01`, `RC`, or a leading zero in the numeric candidate identifier.
Build numbers belong in CI metadata, the app manifest, and the artifact
manifest; they do not change tag precedence and should not be used as a
replacement for `rc.N`.

Historical tags without `v` may be read as legacy version references but must
not be renamed, moved, deleted, or recreated. A stable legacy tag `X.Y.Z` may
be migrated by adding `vX.Y.Z` at the exact same commit when that canonical tag
does not already exist. The old tag remains untouched. All new release tags
use the canonical form above.

## Suggestion behavior

The bundled `scripts/version-suggestions` helper reads local Git tags by
default and emits either human-readable suggestions or stable JSON.

For `main`, it resolves the highest SemVer tag (stable or RC) and proposes the
next release lines:

- `patch`: `vX.Y.(Z+1)-rc.1`;
- `minor`: `vX.(Y+1).0-rc.1`;
- `major`: `v(X+1).0.0-rc.1`.

If a proposed line already has RC tags, the helper reports the next candidate
number and marks the line `release-in-progress`; the main flow must use that
release branch rather than creating a parallel tag from `main`. If the line is
already final, it is marked `finalized` and is not available for a new RC.

For `release/vX.Y.Z`, it proposes:

- `candidate`: the next unused `vX.Y.Z-rc.N`;
- `final`: `vX.Y.Z`.

If `vX.Y.Z` already exists, both operations are blocked. Never remove the
final tag to restart an RC sequence.

If no SemVer tags exist, do not infer a historical version. On `main`, the
helper returns one bootstrap proposal, `v0.1.0-rc.1`, with status
`bootstrap-required`. If the user supplied an initial version in the context,
pass it as `--initial-version X.Y.Z` and show the corresponding
`vX.Y.Z-rc.1` proposal instead. On a `release/vX.Y.Z` branch, the branch name
is already sufficient context, so the helper can propose `vX.Y.Z-rc.1` and
`vX.Y.Z` even when the repository has no tags. Migration mode returns an empty
`nothing-to-migrate` result when there are no legacy tags.

## Legacy-tag migration

Use `scripts/version-suggestions --mode migration` to produce a read-only
migration plan for stable legacy tags such as `2.3.0`. The plan must include:

- the source tag and canonical target tag;
- the source commit SHA resolved through the commit object, including annotated
  source tags;
- whether the target is absent, already present at the same commit, or a
  conflicting target that must block the operation.

When migration is explicitly authorized, create only the missing `vX.Y.Z` tag
at the resolved source commit. Re-read both refs after creation and require
the source and target to resolve to the same commit. Never delete or move the
legacy tag, and never overwrite an existing canonical tag. A target conflict
is a hard stop. The migration plan is not authorization: after displaying the
source tag, target tag, exact commit, and intended remote operation, ask the
user to confirm that exact tag. Only then use the tag/release workflow to create
and push it.

## Confirmation gate

Every tag application follows this sequence, including when the user has
already asked generally to “release” or “create the tag”:

1. Inspect the current branch, `HEAD`, local/remote tag view, and any explicit
   version or intent in the user's instructions.
2. Select only the proposals relevant to that context: `main` gets patch,
   minor, and major; `release/vX.Y.Z` gets the next candidate and final; a
   legacy migration gets only missing canonical aliases.
3. Display a preview containing the context, exact tag, target commit, branch,
   and whether the operation is candidate, final, or migration.
4. Ask for explicit confirmation of the exact tag and operation. Do not create,
   move, delete, or push a tag before that confirmation.
5. After confirmation, use `$g:github-releases` for the tag/release mutation,
   then verify the resulting ref and commit. A final tag and its release are
   separate operations and each must remain within the user's confirmed scope.

If the current branch is neither `main` nor `release/vX.Y.Z` and the user did
not provide a clear version/intent, do not guess. Show read-only context and
ask which release line or migration the user wants.

## Runtime workflow

1. Refresh or otherwise verify the local tag view when remote state may be
   stale. The helper does not fetch or write remote state implicitly.
2. If the release flow will be implemented in GitHub Actions, run the
   read-only Actions permissions preflight from
   `../github-actions/references/configuration.md` before creating the
   workflow. The workflow-authoring instructions are not currently present. If
   the preflight is blocked, warn that the generated Action will not complete
   its PR operation until the repository setting is enabled; continue writing
   the explicitly requested workflow and keep its status pending configuration.
3. Run the helper in the correct mode and inspect its resolved `latest_tag`,
   `suggestions`, `migrations`, and status values.
4. For migration, re-read the source and target refs immediately before the
   authorized create operation and require the target to be absent.
5. For release publication, re-read the relevant branch and tags immediately
   before the authorized operation.
6. Preserve exact tag and branch SHAs; reject an existing tag or a finalized
   release line.

Examples from the skill directory:

```bash
scripts/version-suggestions --mode main --json
scripts/version-suggestions --mode main --initial-version 2.3.0 --json
scripts/version-suggestions --mode release --line release/v2.4.0 --json
scripts/version-suggestions --mode main --tag v2.3.1-rc.2
scripts/version-suggestions --mode migration --repo /path/to/project --json
```

For deterministic automation or tests, pass one or more `--tag` values or a
`--tags-file` instead of reading the current repository. Migration mode must
read a real repository so it can resolve source commit SHAs.

The command is read-only and exits successfully when a release line is
finalized but has no available suggestions; the JSON status explains why.

## References

- [SemVer and tag format](references/semver.md)
- [Suggestion states](references/states.md)
- [GitHub Actions configuration preflight](../github-actions/references/configuration.md)
