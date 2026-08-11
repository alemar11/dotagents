---
name: versioning
description: Apply the shared SemVer tag and release-line convention, calculate context-aware suggestions, plan safe legacy-tag migrations, and author stable-only GitHub Actions with explicit downstream dispatch recovery.
---

# Versioning

Use this skill when a project needs a release version, a Git tag, a release
branch, the next candidate suggestions for a release workflow, or the guarded
GitHub Actions that implement this convention without touching application
code.

This skill owns the convention, read-only calculation, and explicit migration
of stable legacy tags. It never moves or deletes a tag. The helper only creates
previews; applying any tag is a mutation and always requires a separate,
explicit confirmation after the exact proposal has been shown. Creating a new
canonical alias is a remote mutation and requires the same confirmation; the
skill must verify the source and target commits before and after the create
operation.

## Canonical convention

Use SemVer 2.0.0 as the version model and `v` as the mandatory G prefix on
new Git tags:

```text
vX.Y.Z
vX.Y.Z-rc.N
```

The semantic version itself is `X.Y.Z` or `X.Y.Z-rc.N`; `v` belongs to the
Git tag name and does not participate in SemVer precedence.

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

A release candidate is optional in SemVer. The stable `vX.Y.Z` may be
proposed and published without any prior `vX.Y.Z-rc.N`, subject to the normal
preview and confirmation gates. For the same `X.Y.Z` core, every release
candidate has lower precedence than the stable version:

```text
v2.4.0-rc.1 < v2.4.0-rc.2 < v2.4.0
```

SemVer defines version meaning and precedence; it does not define Git tag
prefixes, branch names, the number of active release lines, pull requests,
approvals, or automation. The `v` prefix, the restricted `rc.N` spelling, the
hard application gate, and `release/vX.Y.Z` are G workflow conventions rather
than universal SemVer requirements.

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

## Noncanonical application gate

Before any tag can enter the confirmation or mutation path, validate the exact
requested tag with `scripts/version-suggestions --mode validate
--application-tag <tag> --json`. Only an exact `vX.Y.Z` or `vX.Y.Z-rc.N`
result with status `canonical-format` may proceed.

Treat every other spelling as `blocked-noncanonical`, including:

- `1.0.0` without the required `v` prefix;
- `v1.0.0-beta`, `v1.0.0-alpha.1`, or any prerelease other than `rc.N`;
- `v1.0.0-rc01`, `v1.0.0-rc.01`, or `v1.0.0-RC.1`;
- tags with build metadata or any additional suffix.

Explain the mismatch and the two accepted formats. A canonical replacement may
be offered as a new proposal, but never silently normalize the rejected input
or treat authority for the rejected tag as confirmation of the replacement.
The user must select the canonical tag and pass the normal preview and explicit
confirmation gate again.

This gate is not overridable. Never create, annotate, push, or delegate a
noncanonical tag to `$g:github-releases`, even when the user insists, confirms
the exact noncanonical spelling, or asks to preserve an existing project
convention. Legacy tags without `v` remain read-only calculation or migration
sources; they are never valid targets for a new tag application.

## Suggestion behavior

The bundled `scripts/version-suggestions` helper reads local Git tags by
default and emits either human-readable suggestions or stable JSON.

For `main`, it resolves the highest stable SemVer tag as the increment baseline
and proposes the next release lines:

- `patch`: `vX.Y.(Z+1)-rc.1`;
- `minor`: `vX.(Y+1).0-rc.1`;
- `major`: `v(X+1).0.0-rc.1`.

Unrelated RC lines do not change the stable baseline or block other lines. If a
proposed line already has RC tags, the helper reports the next candidate number
and marks only that line `release-in-progress`; the main flow must use its
release branch rather than creating another tag for the same line from `main`.
If no stable baseline exists but RC tags do, the helper reports those lines as
`release-in-progress` and does not derive patch, minor, or major lines from an
unstable version. If the proposed line is already final, it is marked
`finalized` and is not available for a new RC.

For `release/vX.Y.Z`, it proposes:

- `candidate`: the next unused `vX.Y.Z-rc.N`;
- `final`: `vX.Y.Z`.

The final proposal does not require an existing candidate tag. Do not impose a
candidate-first rule unless an explicit repository policy requires one; that
policy is outside SemVer itself.

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
2. Validate the exact requested application tag. If it is
   `blocked-noncanonical`, explain the failure and stop before confirmation or
   mutation; user confirmation cannot override this result.
3. Select only the proposals relevant to that context: `main` gets patch,
   minor, and major; `release/vX.Y.Z` gets the next candidate and final; a
   legacy migration gets only missing canonical aliases.
4. Display a preview containing the context, exact tag, target commit, branch,
   and whether the operation is candidate, final, or migration.
5. Ask for explicit confirmation of the exact tag and operation. Do not create,
   move, delete, or push a tag before that confirmation.
6. Re-run the exact application-tag validation immediately before delegation.
   If the result is not `canonical-format`, stop without performing a write.
7. After confirmation and successful revalidation, use `$g:github-releases`
   for the tag/release mutation,
   then verify the resulting ref and commit. A final tag and its release are
   separate operations and each must remain within the user's confirmed scope.

The portable GitHub Actions may use the identical operation-choice UI for dry
run and apply. In that mode, apply must first calculate a read-only proposal,
pass the exact generated tag to a second resolver job as an internal
confirmation, and expose the exact tag in the run summary before mutation. Do
not generalize this same-run confirmation to direct tag commands or workflows
that accept an unvalidated operation without the second resolver pass.

If the current branch is neither `main` nor `release/vX.Y.Z` and the user did
not provide a clear version/intent, do not guess. Show read-only context and
ask which release line or migration the user wants.

## Runtime workflow

1. Refresh or otherwise verify the local tag view when remote state may be
   stale. The helper does not fetch or write remote state implicitly.
2. If the release flow will be implemented in GitHub Actions, run the
   read-only Actions permissions preflight from
   `../github-actions/references/configuration.md`, then read
   `references/github-actions.md` before creating or upgrading the workflow.
   That reference owns the complete workflow templates, universal versus
   repository-specific rules, resolver-version comparison, installation,
   validation, and recovery contract. If the preflight is blocked, warn that
   the generated Action will not complete its PR operation until the repository
   setting is enabled; continue writing the explicitly requested workflow and
   keep its status pending configuration.
3. Run the helper in the correct mode and inspect its resolved `latest_tag`,
   `suggestions`, `migrations`, and status values.
4. Validate the exact tag selected for application. A
   `blocked-noncanonical` result is terminal for that request and must never be
   handed to a mutation workflow.
5. For migration, re-read the source and target refs immediately before the
   authorized create operation and require the target to be absent.
6. For release publication, re-read the relevant branch and tags immediately
   before the authorized operation.
7. Preserve exact tag and branch SHAs; reject an existing tag or a finalized
   release line.

## GitHub Actions authoring boundary

When the user asks to create or upgrade the release Actions, install the
portable topology from `references/github-actions.md` and copy
`assets/resolve_release_version.py` to
`.github/scripts/resolve_release_version.py`. The bundled resolver reports its
independent version through `--version`; compare it with any project copy
before writing. Never downgrade a newer project resolver, silently overwrite
an unversioned resolver, or replace same-version divergent bytes.

The Actions may read only provider-owned repository metadata, tags, branches,
commits, and pull requests. They must not read package manifests, inspect or
edit application code, run project build/test commands, create commits, or
merge the final pull request. Preserve the exact canonical tag gate and the
separate dry-run/application confirmation boundary. Preserve the resolver's
`is_final` workflow output so downstream jobs can gate stable-only work without
reparsing the tag. The apply template uses the same operation-choice UI as dry
run and preserves the confirmation boundary through its internal plan-to-
resolve handoff. If publication is owned by a separate workflow, read the
direct-dispatch contract in `references/github-actions.md`: an explicit
`workflow_dispatch` input must be resolved and gated independently of the
workflow's `on.push.tags` filter.

Examples from the skill directory:

```bash
scripts/version-suggestions --mode main --json
scripts/version-suggestions --mode main --initial-version 2.3.0 --json
scripts/version-suggestions --mode release --line release/v2.4.0 --json
scripts/version-suggestions --mode main --tag v2.3.1-rc.2
scripts/version-suggestions --mode migration --repo /path/to/project --json
scripts/version-suggestions --mode validate --application-tag v2.4.0-rc.1 --json
```

For deterministic automation or tests, pass one or more `--tag` values or a
`--tags-file` instead of reading the current repository. Migration mode must
read a real repository so it can resolve source commit SHAs.

The command is read-only and exits successfully when a release line is
finalized but has no available suggestions; the JSON status explains why.
Validate mode exits nonzero with status `blocked-noncanonical` when the exact
application tag violates the canonical format.

## References

- [SemVer and tag format](references/semver.md)
- [Suggestion states](references/states.md)
- [GitHub Actions release workflow authoring](references/github-actions.md)
- [GitHub Actions configuration preflight](../github-actions/references/configuration.md)
