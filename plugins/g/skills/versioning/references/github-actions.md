# GitHub Actions release workflow authoring

Read this reference only when the user asks to create, review, or upgrade the
GitHub Actions release workflow owned by `g:versioning`. The SemVer and tag
rules remain owned by `semver.md`; this file owns the portable release
controller, the resolver asset lifecycle, and the interface with a
repository-specific publisher.

## Outcome and topology

Install or upgrade these repository-local files:

- `.github/workflows/release-version.yml`: the single normal operator entry
  point for proposing and applying a candidate or final tag;
- `.github/scripts/resolve_release_version.py`: copied byte-for-byte from
  `assets/resolve_release_version.py` and invoked only through `python3`;
- one repository-owned publisher workflow when the project publishes builds,
  packages, releases, or deployments after a final tag.

The release controller has one manual operation-choice UI and four phases:

1. `plan` calculates one exact proposal without creating refs;
2. `approval` displays that proposal and enters the protected
   `release-approval` environment;
3. `resolve` refreshes tags and branch SHAs, then revalidates the exact approved
   proposal;
4. `candidate` or `final` performs the immutable ref and PR mutations.

The approval environment is part of the portable topology. Configure required
reviewers for `release-approval` in repository or organization settings. Use
`deployment: false` so the gate does not create a deployment record. The
workflow file can name the environment, but it cannot configure its reviewers
or wait timer. Report that remote configuration separately from local YAML
readiness.

A candidate creates `release/vX.Y.Z` at the approved default-branch SHA and
creates `vX.Y.Z-rc.N` at that same SHA. A final creates or verifies the
immutable `vX.Y.Z` tag, then creates or reuses one open pull request from the
release branch to the current default branch only when the release branch is
ahead. It never moves refs or merges that pull request.

When stable publication is required, `release-version.yml` calls the
repository publisher as a reusable workflow after final-tag readback. A tag
created with `GITHUB_TOKEN` does not trigger a second workflow, so the portable
contract does not depend on `on.push.tags`. The publisher may also expose
`workflow_dispatch` for manual recovery, but that path accepts only an already
existing canonical final tag.

## Universal controller contract

Preserve all of these invariants in every project:

- Discover the current default branch through GitHub; never hardcode `main`.
- Read remote tags and exact branch SHAs immediately before calculation and
  again after approval, before mutation.
- Accept new tags only as exact `vX.Y.Z` or `vX.Y.Z-rc.N`; never normalize a
  rejected value.
- Use the highest stable SemVer tag as the default-branch increment baseline.
  Unrelated active release lines must not change that baseline or globally
  block another line.
- If a selected patch, minor, or major line already has an RC, require the
  user to continue from that line's `release/vX.Y.Z` branch.
- Require an existing stable baseline. Establish the initial version through
  the normal `g:versioning` preview and confirmation flow; do not infer it from
  application files or package metadata.
- Permit a stable final without a prior RC, because prereleases are optional.
- Expose `application_ready`, `tag`, `release_branch`, `tag_state`, and
  lowercase boolean `is_final` outputs from the exact resolved proposal. The
  final mutation job separately exposes the tag's verified `source_sha`.
- Treat branches and tags as immutable: create missing refs, verify exact SHAs,
  and never move, replace, or delete an existing ref.
- Hash the sorted remote tag-name snapshot and reject stale application state.
- Keep `plan` read-only, pass its exact tag and selected ref SHA through the
  approval job, and re-resolve them against fresh provider state before
  mutation.
- Check out only the resolver from the verified default-branch commit. The
  controller must not inspect, edit, build, test, or commit application code.
- Deny token permissions at workflow scope and grant only `contents: read` to
  resolution and approval, `contents: write` to candidate creation, and both
  `contents: write` and `pull-requests: write` to final application.
- Serialize mutating runs without cancelling an in-flight mutation.
- Pin external actions to a verified full commit SHA. The reference checkout
  pin is `actions/checkout@11d5960a326750d5838078e36cf38b85af677262`.
- Create a final PR only when the release branch is ahead of the default
  branch. Reuse only one exact open same-repository head/base match, reject
  ambiguity, and verify returned PR fields.
- Make final application recoverable: when the final tag already exists at
  the selected commit, do not recreate it; continue with PR reconciliation and
  stable publication as idempotent operations.

## Controller interface

Keep one `workflow_dispatch` interface. Preserve the semantic operation
prefixes because the resolver consumes them:

```yaml
name: Create release tag

on:
  workflow_dispatch:
    inputs:
      operation:
        description: Release operation
        required: true
        type: choice
        options:
          - "[patch] Next patch candidate from the default branch"
          - "[minor] Next minor candidate from the default branch"
          - "[major] Next major candidate from the default branch"
          - "[candidate] Next candidate from a release branch"
          - "[final] Final tag from a release branch"

permissions: {}

concurrency:
  group: release-version
  cancel-in-progress: false
```

The resolver API is `0.2.2`. Every controller job that invokes the copied
asset must first require the exact version:

```yaml
env:
  EXPECTED_RESOLVER_VERSION: "0.2.2"

steps:
  - name: Verify resolver API 0.2.2
    shell: bash
    run: |
      actual_version="$(python3 .github/scripts/resolve_release_version.py --version)"
      test "$actual_version" = "$EXPECTED_RESOLVER_VERSION"
```

Pass the complete plan through explicit job outputs. The approval job must not
recalculate or mutate anything:

```yaml
approval:
  name: Approve ${{ needs.plan.outputs.tag }}
  needs: plan
  if: needs.plan.outputs.application_ready == 'true'
  permissions:
    contents: read
  environment:
    name: release-approval
    deployment: false
  runs-on: ubuntu-latest
  steps:
    - name: Record approved proposal
      shell: bash
      run: |
        echo "Approved tag: ${{ needs.plan.outputs.tag }}"
        echo "Approved source: ${{ github.sha }}"
```

`resolve` must depend on `approval`, fetch provider state again, and call the
resolver in application mode with the exact plan outputs. It must reject a
different tag, source SHA, tag snapshot, default branch, or release branch SHA.
Only `candidate` or `final` may depend on the successful revalidation.

## Candidate and final mutations

For a candidate:

- create the missing release branch at the approved source SHA, or require an
  existing release branch to resolve to that exact SHA;
- create the missing RC tag at the same SHA;
- if either ref exists at another SHA, stop without moving it;
- read both refs back from GitHub and require exact equality.

For a final:

- require the selected ref to be the exact `release/vX.Y.Z` branch;
- create `vX.Y.Z` at its approved SHA, or accept only an existing tag at that
  exact SHA;
- read the final tag back before PR reconciliation or publication;
- create no PR when the release branch is not ahead of the default branch;
- otherwise create or reuse exactly one open same-repository release PR and
  never merge it.

The controller is application-code blind. Build commands, package managers,
signing, artifacts, release notes, stores, registries, and deployments belong
in the publisher adapter, not in `release-version.yml`.

## Reusable publisher contract

The normal stable path is a local reusable-workflow call from the final job.
The publisher must accept the exact final tag and its verified source SHA:

```yaml
name: Publish tagged release

on:
  workflow_call:
    inputs:
      tag:
        description: Existing canonical final tag
        required: true
        type: string
      source_sha:
        description: Commit already verified by the release controller
        required: true
        type: string
  workflow_dispatch:
    inputs:
      tag:
        description: Existing canonical final tag to republish
        required: true
        type: string

permissions: {}
```

Call it only after final-tag readback:

```yaml
publish:
  needs: [resolve, final]
  if: >-
    needs.resolve.outputs.application_ready == 'true' &&
    needs.resolve.outputs.is_final == 'true' &&
    needs.final.outputs.source_sha != ''
  uses: ./.github/workflows/release.yml
  with:
    tag: ${{ needs.resolve.outputs.tag }}
    source_sha: ${{ needs.final.outputs.source_sha }}
  secrets: inherit
```

The publisher is deliberately repository-specific and may check out, build,
test, sign, package, or deploy application code. Its portable security and
idempotency boundary is:

- accept only exact canonical stable tags matching `vX.Y.Z`; reject every RC,
  legacy, build-metadata, or additional-suffix spelling;
- resolve the input tag through GitHub and require `refs/tags/<tag>` to exist;
- on `workflow_call`, require the tag commit to equal `inputs.source_sha`;
- on manual recovery, derive `source_sha` from the existing tag because no
  caller-provided SHA is trusted or required;
- classify the resolver result as `existing-final` and require
  `application_ready == 'true'` and `is_final == 'true'`;
- check out `needs.resolve.outputs.tag`, never the manually selected branch,
  event ref, or an unvalidated SHA;
- make release/package/deployment creation idempotent and verify the published
  object after any write;
- grant only the permissions required by that repository's publication steps.

The exact checkout contract is:

```yaml
- uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
  with:
    ref: ${{ needs.resolve.outputs.tag }}
```

Do not add `on.push.tags`. Do not invoke the publisher with `gh workflow run`
or `repository_dispatch`. Do not grant `actions: write` to the controller.
Those paths reintroduce a second event contract and weaken the exact approved
tag/SHA handoff. `workflow_dispatch` on the publisher exists only for an
operator to recover publication of an already existing final tag.

Pushing a tag locally therefore does not publish it through this topology. The
operator must use the approval-gated release controller for the normal path or
manually dispatch the publisher with an existing final tag for recovery.

## Repository choices, not universal rules

| Surface | Portable requirement | Repository-owned choice |
| --- | --- | --- |
| Controller name and input prefixes | Display name `Create release tag`; one approval-gated `release-version.yml`; preserve semantic prefixes | Run-name wording may change |
| Publisher name and filename | Display name `Publish tagged release`; local reusable workflow with `tag` and `source_sha` inputs | Filename and publication implementation |
| Runner | Must provide the commands used by the selected jobs | Hosted or self-hosted runner |
| Parallel release lines | Allowed when lines differ | A stricter repository policy may serialize them |
| Required reviewers | `release-approval` environment is named in YAML | Reviewer list and wait timer are configured remotely |
| Automatic merge | Disabled | A separate explicitly authorized delivery workflow may own merge policy |
| Initial version | Established before these Actions | Never inferred from application files |

## Permissions preflight

Before writing or upgrading the workflows, run the read-only preflight from
`../github-actions/references/configuration.md`. The repository must allow
GitHub Actions to create pull requests, and `release-approval` must exist with
the intended required reviewers. A blocked or unavailable preflight is
advisory: write the explicitly requested files, report the missing remote
configuration, and do not claim the workflow is operationally ready.

Because `deployment: false` is used, the approval environment must rely on
reviewers and wait timers rather than custom deployment protection rules.

## Resolver asset and version lifecycle

The bundled source is `assets/resolve_release_version.py`. Its independent
resolver version is `0.2.2`; it is not the G plugin version or a project
release version. `RESOLVER_VERSION` is the single source of truth and
`python3 <path> --version` must print only that SemVer value.

Inspect both versions before copying:

```bash
python3 assets/resolve_release_version.py --version
python3 .github/scripts/resolve_release_version.py --version
```

Derive exactly one resolver state:

| State | Meaning | Required action |
| --- | --- | --- |
| `resolver-absent` | No project resolver exists | Copy the bundled asset and install the controller |
| `resolver-current` | Versions and bytes match | Leave it unchanged and inspect the workflow contract |
| `resolver-upgrade-available` | The project version is lower | Review the delta, then update resolver, tests, and workflow together |
| `resolver-project-newer` | The project version is higher | Never downgrade; inspect compatibility |
| `resolver-unversioned` | `--version` is absent or invalid | Review it and never overwrite silently |
| `resolver-version-conflict` | Versions match but bytes differ | Treat it as a local fork and require explicit resolution |

Compare versions numerically as SemVer. A resolver behavior change requires
its own version bump: major for incompatible CLI/output or workflow-contract
changes, minor for backward-compatible capabilities, and patch for compatible
fixes. Documentation-only changes do not bump the resolver.

The project copy should remain byte-identical to the bundled asset. Project
policy belongs in workflow YAML or repository context, not in a same-version
fork of the resolver.

## Authoring and validation workflow

1. Inspect existing workflows, resolver, tags, default branch, settings, and
   working-tree changes. Preserve unrelated work.
2. Run the permissions and environment preflight; report exact remote state.
3. Verify that a stable SemVer baseline exists. If not, route initial tagging
   through the normal preview and confirmation flow.
4. Resolve the asset/project resolver state and never downgrade or silently
   replace an unversioned or divergent script.
5. Install the resolver and one approval-gated controller. Integrate a
   repository publisher only when stable publication exists.
6. Preserve operation keys, exact outputs, job dependencies, environment gate,
   permission scopes, concurrency, immutable-ref checks, and publisher inputs.
7. Add focused resolver and workflow-contract tests. Cover `--version`,
   stable-baseline increments, same-line continuation, unrelated lines, direct
   final, exact confirmation, noncanonical rejection, existing-final recovery,
   approval handoff, fresh revalidation, reusable final publication, manual
   existing-tag recovery, RC rejection, absent-tag rejection, SHA mismatch,
   and exact-tag checkout.
8. Validate Python tests, `--help`, `--version`, YAML parsing, every Bash `run`
   block with ShellCheck, and `git diff --check`. Application tests belong to
   the repository publisher, not the universal controller.
9. Report local implementation separately from remote readiness. Commit, push,
   dispatch, tag creation, reviewer configuration, and PRs remain separate
   mutations.
