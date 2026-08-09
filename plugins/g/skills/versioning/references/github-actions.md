# GitHub Actions release workflow authoring

Read this reference only when the user asks to create, review, or upgrade the
GitHub Actions release workflow owned by `g:versioning`. The SemVer and tag
rules remain owned by `semver.md`; this file owns the reusable GitHub Actions
topology, the resolver asset lifecycle, and the boundary between universal
behavior and repository policy.

## Outcome and topology

Install three repository-local files:

- `.github/workflows/release-version-dry-run.yml`: manual read-only proposal
  and reusable exact-confirmation resolver;
- `.github/workflows/release-version-apply.yml`: manual mutation workflow for
  candidate or final application;
- `.github/scripts/resolve_release_version.py`: copied from
  `assets/resolve_release_version.py` and invoked only through `python3`.

The dry run calculates one proposal and never creates refs. The apply workflow
accepts the exact proposed tag, re-resolves current state, and proceeds only
when the confirmation still matches. A candidate creates an immutable
`vX.Y.Z-rc.N` tag and its `release/vX.Y.Z` branch. A final creates or verifies
the immutable `vX.Y.Z` tag, then creates or reuses one open pull request to the
current default branch only when the release branch is ahead. It never merges
that pull request.

No environment or manual approval gate is part of this topology. The explicit
tag entered into the apply workflow is the confirmation gate. Repository or
organization policy may add an environment, but that is not part of the
portable template.

## Universal contract

Preserve all of these invariants in every project:

- Discover the current default branch through GitHub; never hardcode `main`.
- Read remote tags and exact branch SHAs from the provider immediately before
  calculation and again before mutation.
- Accept new tags only as exact `vX.Y.Z` or `vX.Y.Z-rc.N`; never normalize a
  rejected confirmation.
- Use the highest stable SemVer tag as the default-branch increment baseline.
  Unrelated active release lines must not change that baseline or globally
  block another line.
- If the exact patch, minor, or major line already has an RC, require the user
  to continue from that line's `release/vX.Y.Z` branch.
- Require an existing stable baseline. Establish the initial version through
  the normal `g:versioning` preview and confirmation flow; the Actions do not
  infer it from source or package metadata.
- Permit a stable final without a prior RC, because prereleases are optional.
- Expose `is_final` as a lowercase boolean workflow output derived from the
  exact resolved canonical tag, so downstream jobs can distinguish a stable
  `vX.Y.Z` from a candidate `vX.Y.Z-rc.N` without reparsing the tag.
- Treat branches and tags as immutable: create missing refs, verify exact SHAs,
  and never move, replace, or delete an existing ref.
- Hash the sorted remote tag-name snapshot and reject stale application state.
- Check out only the resolver from the verified default-branch commit. Never
  check out, inspect, edit, build, test, or commit application code, and never
  read `package.json` or another package manifest.
- Deny token permissions at workflow scope and grant only `contents: read` to
  the resolver, `contents: write` to candidate creation, and both
  `contents: write` and `pull-requests: write` to final application.
- Cancel superseded dry runs. Serialize mutating apply runs without cancelling
  an in-flight mutation, so a new dispatch cannot interrupt a partially
  completed tag/branch/PR transaction.
- Pin external actions to a verified full commit SHA. The template uses
  `actions/checkout` v4 at
  `11d5960a326750d5838078e36cf38b85af677262`.
- Create a final PR only when the release branch is ahead of the default
  branch. Reuse only one exact open same-repository head/base match, reject
  ambiguity, and verify the returned PR fields.
- Make final application recoverable: if the final tag already exists at the
  selected commit, do not recreate it; continue only with PR reconciliation.

## Repository choices, not universal rules

| Surface | Portable default | Repository-owned alternative |
| --- | --- | --- |
| Workflow display names and PR prose | Use the templates below | Wording may change without changing semantic input keys |
| Runner | `ubuntu-latest` | A compatible runner may replace it if it provides Bash, Python 3, `gh`, `jq`, and `sha256sum` |
| Parallel release lines | Allowed when they are different lines | A repository may impose a stricter policy, but do not call it SemVer |
| Manual environment approval | Absent | May be added only when explicitly requested by repository policy |
| Automatic merge | Disabled | A separate, explicitly authorized delivery workflow may own merge policy |
| Initial version | Established before these Actions | Never infer it from application files or package metadata |

Do not bake project language, build commands, package managers, deployment
targets, changelog generation, issue policy, reviewers, labels, or branch
protection assumptions into these workflows.

## Downstream stable-only work

Use `is_final == 'true'` together with `application_ready == 'true'` to gate a
build, publish, or deployment job in the same workflow or in a reusable
workflow caller. The output is a decision fact; it does not trigger another
workflow by itself.

A tag created with the repository `GITHUB_TOKEN` does not cause a separate
tag-`push` workflow run. If a project later needs an independent build
workflow, add an explicitly authorized `workflow_dispatch` or
`repository_dispatch` after the final tag readback, or use a separately
approved GitHub App or personal access token. Keep that project-specific build
and credential policy outside the portable release-version templates.

## Permissions preflight

Before writing or upgrading the workflows, run the read-only preflight from
`../github-actions/references/configuration.md`. The repository must allow
GitHub Actions to create pull requests, and the YAML must still declare the
job-level permissions above. A blocked or unavailable preflight is advisory:
write the explicitly requested files, report the missing setting, and do not
claim that PR creation is functional.

## Resolver asset and version lifecycle

The bundled source is `assets/resolve_release_version.py`. Its current
independent resolver version is `0.2.0`; it is not the G plugin version and not
a project release version. `RESOLVER_VERSION` is the single source of truth
and `python3 <path> --version` must print only that SemVer value.

Inspect both versions before copying:

```bash
python3 assets/resolve_release_version.py --version
python3 .github/scripts/resolve_release_version.py --version
```

Derive exactly one resolver state:

| State | Meaning | Required action |
| --- | --- | --- |
| `resolver-absent` | No project resolver exists | Copy the bundled asset and install both workflow templates |
| `resolver-current` | Versions and bytes match | Leave the resolver unchanged; review the workflows for the same contract |
| `resolver-upgrade-available` | The project version is lower | Review the behavior delta, then update resolver, tests, and both workflows together |
| `resolver-project-newer` | The project version is higher | Never downgrade; inspect compatibility and report that the bundled template is older |
| `resolver-unversioned` | `--version` is absent or cannot produce SemVer | Treat it as a local legacy implementation; review it and never overwrite silently |
| `resolver-version-conflict` | Versions match but bytes differ | Treat it as a local fork; review the diff and require an explicit resolution |

Compare versions numerically as SemVer, not lexically. A resolver behavior
change requires its own version bump: major for incompatible CLI/output or
workflow-contract changes, minor for backward-compatible capabilities, and
patch for backward-compatible fixes. Documentation-only changes do not bump
the resolver.

The project copy should remain byte-identical to the bundled asset. Project
policy belongs in the workflow YAML or project context, not in a fork of the
resolver. If a real project needs different resolver behavior, record that
divergence explicitly instead of masking it behind the same version.

## Authoring workflow

1. Read the repository context and inspect existing workflows, resolver, tags,
   default branch, and working-tree changes. Preserve unrelated changes.
2. Run the permissions preflight and report its exact status.
3. Verify that a stable SemVer baseline exists. If not, stop Action execution
   and route initial tagging through the normal confirmation-gated versioning
   flow.
4. Resolve the asset/project resolver state above. Do not downgrade or silently
   replace an unversioned or same-version divergent script.
5. Copy the asset to `.github/scripts/resolve_release_version.py` when the
   resolved state authorizes installation or upgrade.
6. Write the complete templates below. Preserve their semantic input keys,
   outputs, permission scopes, concurrency split, ref checks, and mutation
   boundaries.
7. Add or update focused resolver tests in `.github/scripts/`. At minimum test
   `--version`, stable-baseline increments, same-line continuation, unrelated
   parallel lines, direct final, legacy read-only input, exact confirmation,
   noncanonical rejection, existing-final reconciliation, and output fields.
8. Validate Python tests, `--help`, `--version`, YAML parsing, every Bash
   `run` block with ShellCheck, and `git diff --check`. Run application tests
   only when repository instructions require them; the workflows themselves
   must not invoke them.
9. Report local implementation separately from remote readiness. Commit, push,
   workflow dispatch, tags, branches, and PRs remain separate mutations.

## Complete dry-run workflow template

The YAML comments and display text may remain in the copied workflow. The
semantic input prefixes (`[patch]`, `[minor]`, `[major]`, `[candidate]`, and
`[final]`) are machine-facing and must not change without a resolver version
change.

```yaml
# g:versioning release workflow template; resolver API 0.2.0
name: Release version (dry run)

run-name: Dry run · ${{ github.ref_name }}

on:
  workflow_dispatch:
    inputs:
      operation:
        description: Select the operation that matches the branch chosen above
        required: true
        type: choice
        options:
          - "[patch] Default branch → vX.Y.(Z+1)-rc.1"
          - "[minor] Default branch → vX.(Y+1).0-rc.1"
          - "[major] Default branch → v(X+1).0.0-rc.1"
          - "[candidate] release/vX.Y.Z → vX.Y.Z-rc.N"
          - "[final] release/vX.Y.Z → vX.Y.Z"
  workflow_call:
    inputs:
      application_mode:
        description: Require an exact confirmation and expose mutation-ready outputs
        required: false
        default: false
        type: boolean
      operation:
        description: Internal semantic operation or automatic inference
        required: true
        type: string
      confirmed_tag:
        description: Exact canonical tag to confirm; empty means planning only
        required: false
        default: ""
        type: string
      ref_name:
        description: Selected branch name
        required: true
        type: string
      target_sha:
        description: Selected branch SHA at dispatch time
        required: true
        type: string
    outputs:
      application_ready:
        description: Whether the exact current proposal was confirmed
        value: ${{ jobs.resolve.outputs.application_ready }}
      context:
        description: Default-branch or release-branch context
        value: ${{ jobs.resolve.outputs.context }}
      default_branch:
        description: Current repository default branch
        value: ${{ jobs.resolve.outputs.default_branch }}
      is_final:
        description: Whether the exact resolved tag is a stable final tag
        value: ${{ jobs.resolve.outputs.is_final }}
      kind:
        description: Candidate or final operation kind
        value: ${{ jobs.resolve.outputs.kind }}
      release_branch:
        description: Exact release branch
        value: ${{ jobs.resolve.outputs.release_branch }}
      resolver_version:
        description: Version of the trusted release resolver
        value: ${{ jobs.resolve.outputs.resolver_version }}
      status:
        description: Resolver status
        value: ${{ jobs.resolve.outputs.status }}
      tag:
        description: Exact canonical tag
        value: ${{ jobs.resolve.outputs.tag }}
      tag_snapshot:
        description: SHA-256 of the sorted remote tag-name set
        value: ${{ jobs.resolve.outputs.tag_snapshot }}
      tag_state:
        description: Whether the resolved tag is absent or an existing final
        value: ${{ jobs.resolve.outputs.tag_state }}

permissions: {}

concurrency:
  group: release-version-resolver-${{ github.repository }}-${{ inputs.application_mode && github.run_id || 'dry-run' }}
  cancel-in-progress: ${{ !inputs.application_mode }}

jobs:
  resolve:
    name: Resolve exact tag
    runs-on: ubuntu-latest
    permissions:
      contents: read
    outputs:
      application_ready: ${{ steps.resolve.outputs.application_ready }}
      context: ${{ steps.resolve.outputs.context }}
      default_branch: ${{ steps.resolve.outputs.default_branch }}
      is_final: ${{ steps.resolve.outputs.is_final }}
      kind: ${{ steps.resolve.outputs.kind }}
      release_branch: ${{ steps.resolve.outputs.release_branch }}
      resolver_version: ${{ steps.resolve.outputs.resolver_version }}
      status: ${{ steps.resolve.outputs.status }}
      tag: ${{ steps.resolve.outputs.tag }}
      tag_snapshot: ${{ steps.resolve.outputs.tag_snapshot }}
      tag_state: ${{ steps.resolve.outputs.tag_state }}
    steps:
      - name: Capture repository version state
        id: snapshot
        env:
          GH_TOKEN: ${{ github.token }}
        shell: bash
        run: |
          set -euo pipefail

          tags_file="$RUNNER_TEMP/release-tags.txt"
          gh api --paginate \
            -H "Accept: application/vnd.github+json" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "repos/${GITHUB_REPOSITORY}/git/matching-refs/tags/" \
            --jq '.[].ref | sub("^refs/tags/"; "")' \
            | LC_ALL=C sort -u > "$tags_file"

          default_branch="$(
            gh api \
              -H "Accept: application/vnd.github+json" \
              -H "X-GitHub-Api-Version: 2022-11-28" \
              "repos/${GITHUB_REPOSITORY}" \
              --jq .default_branch
          )"
          default_ref="refs/heads/${default_branch}"
          default_sha="$(
            gh api \
              -H "Accept: application/vnd.github+json" \
              -H "X-GitHub-Api-Version: 2022-11-28" \
              "repos/${GITHUB_REPOSITORY}/git/matching-refs/heads/${default_branch}" \
              | jq -r --arg default_ref "$default_ref" \
                '[.[] | select(.ref == $default_ref) | .object.sha][0] // empty'
          )"
          if [[ -z "$default_sha" ]]; then
            echo "Could not resolve the current default-branch commit." >&2
            exit 1
          fi

          tag_snapshot="$(sha256sum "$tags_file" | cut -d ' ' -f 1)"
          {
            echo "default_branch=$default_branch"
            echo "default_sha=$default_sha"
            echo "tag_snapshot=$tag_snapshot"
          } >> "$GITHUB_OUTPUT"

      - name: Check out only the trusted version resolver
        uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4
        with:
          ref: ${{ steps.snapshot.outputs.default_sha }}
          sparse-checkout: .github/scripts/resolve_release_version.py
          sparse-checkout-cone-mode: false
          persist-credentials: false
          fetch-depth: 1

      - name: Verify release resolver API version
        env:
          EXPECTED_RESOLVER_VERSION: "0.2.0"
        shell: bash
        run: |
          set -euo pipefail

          actual_version="$(python3 .github/scripts/resolve_release_version.py --version)"
          if [[ "$actual_version" != "$EXPECTED_RESOLVER_VERSION" ]]; then
            echo "Resolver version $actual_version does not match workflow API $EXPECTED_RESOLVER_VERSION." >&2
            exit 1
          fi

      - name: Resolve without reading application code
        id: resolve
        env:
          APPLICATION_MODE: ${{ inputs.application_mode || false }}
          CONFIRMED_TAG: ${{ inputs.confirmed_tag }}
          DEFAULT_BRANCH: ${{ steps.snapshot.outputs.default_branch }}
          OPERATION: ${{ inputs.operation }}
          REF_NAME: ${{ inputs.ref_name || github.ref_name }}
          TAG_SNAPSHOT: ${{ steps.snapshot.outputs.tag_snapshot }}
          TARGET_SHA: ${{ inputs.target_sha || github.sha }}
        shell: bash
        run: |
          set -euo pipefail

          args=(
            --default-branch "$DEFAULT_BRANCH"
            --github-output "$GITHUB_OUTPUT"
            --github-step-summary "$GITHUB_STEP_SUMMARY"
            --operation "$OPERATION"
            --ref-name "$REF_NAME"
            --tag-snapshot "$TAG_SNAPSHOT"
            --tags-file "$RUNNER_TEMP/release-tags.txt"
            --target-sha "$TARGET_SHA"
          )
          if [[ "$APPLICATION_MODE" == "true" ]]; then
            args+=(--application-mode --confirmed-tag "$CONFIRMED_TAG")
          fi

          python3 .github/scripts/resolve_release_version.py "${args[@]}"
```

### Dry-run annotations

| YAML surface | Why it is portable |
| --- | --- |
| `workflow_dispatch.inputs.operation` | One manual menu covers default-branch increments and release-branch candidate/final operations |
| `workflow_call` and outputs | The apply workflow reuses the exact same resolver; `is_final` gives downstream jobs a parser-free stable/candidate gate |
| top-level `permissions: {}` | Denies implicit write scope before job-level least privilege |
| `concurrency` | Superseded planning runs are disposable; application-mode calls get an isolated key because the caller owns mutation serialization |
| `Capture repository version state` | Reads only provider-owned refs and current default-branch identity |
| pinned sparse `actions/checkout` | Loads only the trusted resolver from the verified default branch and avoids application code |
| resolver API version check | Fails clearly when workflow and copied resolver were not upgraded together |
| resolver environment and arguments | Passes explicit facts; it does not infer from package files or mutable workspace state |

## Complete apply workflow template

```yaml
# g:versioning release workflow template; resolver API 0.2.0
name: Release version (apply)

run-name: Apply · ${{ inputs.confirmed_tag }} · ${{ github.ref_name }}

on:
  workflow_dispatch:
    inputs:
      confirmed_tag:
        description: Exact canonical tag shown by Release version (dry run)
        required: true
        type: string

permissions: {}

concurrency:
  group: release-version-apply-${{ github.repository }}
  cancel-in-progress: false

jobs:
  resolve:
    name: Revalidate exact confirmation
    uses: ./.github/workflows/release-version-dry-run.yml
    with:
      application_mode: true
      operation: auto
      confirmed_tag: ${{ inputs.confirmed_tag }}
      ref_name: ${{ github.ref_name }}
      target_sha: ${{ github.sha }}
    permissions:
      contents: read

  candidate:
    name: Create candidate tag and release branch
    if: >-
      needs.resolve.outputs.application_ready == 'true' &&
      needs.resolve.outputs.is_final == 'false' &&
      needs.resolve.outputs.kind == 'candidate'
    needs: resolve
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Revalidate and create immutable candidate refs
        env:
          CONTEXT: ${{ needs.resolve.outputs.context }}
          DEFAULT_BRANCH: ${{ needs.resolve.outputs.default_branch }}
          EXPECTED_TAG_SNAPSHOT: ${{ needs.resolve.outputs.tag_snapshot }}
          GH_TOKEN: ${{ github.token }}
          RELEASE_BRANCH: ${{ needs.resolve.outputs.release_branch }}
          TAG: ${{ needs.resolve.outputs.tag }}
        shell: bash
        run: |
          set -euo pipefail

          tags_file="$RUNNER_TEMP/release-tags.txt"
          gh api --paginate \
            -H "Accept: application/vnd.github+json" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "repos/${GITHUB_REPOSITORY}/git/matching-refs/tags/" \
            --jq '.[].ref | sub("^refs/tags/"; "")' \
            | LC_ALL=C sort -u > "$tags_file"
          current_tag_snapshot="$(sha256sum "$tags_file" | cut -d ' ' -f 1)"
          if [[ "$current_tag_snapshot" != "$EXPECTED_TAG_SNAPSHOT" ]]; then
            echo "The tag set changed after resolution; run the dry run and Release version (apply) again." >&2
            exit 1
          fi

          canonical_tag_pattern='^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-rc\.[1-9][0-9]*)?$'
          release_branch_pattern='^release/v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
          if [[ ! "$TAG" =~ $canonical_tag_pattern ]]; then
            echo "Refusing a noncanonical tag; expected vX.Y.Z or vX.Y.Z-rc.N." >&2
            exit 1
          fi
          if [[ ! "$RELEASE_BRANCH" =~ $release_branch_pattern ]]; then
            echo "Refusing a noncanonical release branch." >&2
            exit 1
          fi

          current_default_branch="$(gh api "repos/${GITHUB_REPOSITORY}" --jq .default_branch)"
          if [[ "$current_default_branch" != "$DEFAULT_BRANCH" ]]; then
            echo "The default branch changed after resolution; run the dry run and Release version (apply) again." >&2
            exit 1
          fi

          ref_sha() {
            local namespace="$1"
            local name="$2"
            local exact_ref="refs/${namespace}/${name}"
            gh api "repos/${GITHUB_REPOSITORY}/git/matching-refs/${namespace}/${name}" \
              | jq -r --arg exact_ref "$exact_ref" \
                '[.[] | select(.ref == $exact_ref) | .object.sha][0] // empty'
          }

          selected_sha="$(ref_sha heads "$GITHUB_REF_NAME")"
          if [[ "$selected_sha" != "$GITHUB_SHA" ]]; then
            echo "The selected branch changed after dispatch; refusing a stale SHA." >&2
            exit 1
          fi

          target_sha="$GITHUB_SHA"
          branch_ref="refs/heads/${RELEASE_BRANCH}"
          branch_sha="$(ref_sha heads "$RELEASE_BRANCH")"
          if [[ "$CONTEXT" == "default" ]]; then
            if [[ -z "$branch_sha" ]]; then
              gh api --method POST "repos/${GITHUB_REPOSITORY}/git/refs" \
                --raw-field ref="$branch_ref" \
                --raw-field sha="$target_sha" >/dev/null
            elif [[ "$branch_sha" != "$target_sha" ]]; then
              echo "$RELEASE_BRANCH exists at a different SHA; refusing to move it." >&2
              exit 1
            fi
          elif [[ "$CONTEXT" != "release" || "$RELEASE_BRANCH" != "$GITHUB_REF_NAME" ]]; then
            echo "The resolved context no longer matches the selected branch." >&2
            exit 1
          fi

          branch_sha="$(ref_sha heads "$RELEASE_BRANCH")"
          if [[ "$branch_sha" != "$target_sha" ]]; then
            echo "$RELEASE_BRANCH was not verified at the selected SHA." >&2
            exit 1
          fi

          if [[ -n "$(ref_sha tags "$TAG")" ]]; then
            echo "$TAG already exists; refusing to recreate or move it." >&2
            exit 1
          fi

          tag_object_sha="$(
            gh api --method POST "repos/${GITHUB_REPOSITORY}/git/tags" \
              --raw-field tag="$TAG" \
              --raw-field message="Create immutable release candidate $TAG" \
              --raw-field object="$target_sha" \
              --raw-field type=commit \
              --jq .sha
          )"
          gh api --method POST "repos/${GITHUB_REPOSITORY}/git/refs" \
            --raw-field ref="refs/tags/${TAG}" \
            --raw-field sha="$tag_object_sha" >/dev/null

          read -r tag_type tag_sha < <(
            gh api "repos/${GITHUB_REPOSITORY}/git/ref/tags/${TAG}" \
              --jq '[.object.type, .object.sha] | @tsv'
          )
          if [[ "$tag_type" != "tag" ]]; then
            echo "Expected an annotated tag object for $TAG." >&2
            exit 1
          fi
          resolved_sha="$(gh api "repos/${GITHUB_REPOSITORY}/git/tags/${tag_sha}" --jq .object.sha)"
          if [[ "$resolved_sha" != "$target_sha" ]]; then
            echo "$TAG does not resolve to the selected SHA." >&2
            exit 1
          fi

          {
            echo "## Candidate refs created"
            echo
            echo "- Tag: \`$TAG\`"
            echo "- Release branch: \`$RELEASE_BRANCH\`"
            echo "- Commit: \`$target_sha\`"
            echo
            echo "No application source or package metadata was read, edited, or committed."
          } >> "$GITHUB_STEP_SUMMARY"

  final:
    name: Create final tag and reconcile release PR
    if: >-
      needs.resolve.outputs.application_ready == 'true' &&
      needs.resolve.outputs.is_final == 'true' &&
      needs.resolve.outputs.kind == 'final'
    needs: resolve
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - name: Revalidate and create immutable final tag
        env:
          DEFAULT_BRANCH: ${{ needs.resolve.outputs.default_branch }}
          EXPECTED_TAG_SNAPSHOT: ${{ needs.resolve.outputs.tag_snapshot }}
          GH_TOKEN: ${{ github.token }}
          RELEASE_BRANCH: ${{ needs.resolve.outputs.release_branch }}
          TAG: ${{ needs.resolve.outputs.tag }}
          TAG_STATE: ${{ needs.resolve.outputs.tag_state }}
        shell: bash
        run: |
          set -euo pipefail

          tags_file="$RUNNER_TEMP/release-tags.txt"
          gh api --paginate \
            -H "Accept: application/vnd.github+json" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "repos/${GITHUB_REPOSITORY}/git/matching-refs/tags/" \
            --jq '.[].ref | sub("^refs/tags/"; "")' \
            | LC_ALL=C sort -u > "$tags_file"
          current_tag_snapshot="$(sha256sum "$tags_file" | cut -d ' ' -f 1)"
          if [[ "$current_tag_snapshot" != "$EXPECTED_TAG_SNAPSHOT" ]]; then
            echo "The tag set changed after resolution; run the dry run and Release version (apply) again." >&2
            exit 1
          fi

          canonical_tag_pattern='^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-rc\.[1-9][0-9]*)?$'
          release_branch_pattern='^release/v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
          if [[ ! "$TAG" =~ $canonical_tag_pattern ]]; then
            echo "Refusing a noncanonical tag; expected vX.Y.Z or vX.Y.Z-rc.N." >&2
            exit 1
          fi
          if [[ ! "$RELEASE_BRANCH" =~ $release_branch_pattern ]]; then
            echo "Refusing a noncanonical release branch." >&2
            exit 1
          fi
          if [[ "$TAG_STATE" != "absent" && "$TAG_STATE" != "existing-final" ]]; then
            echo "Unexpected tag state; refusing final release mutation." >&2
            exit 1
          fi

          current_default_branch="$(gh api "repos/${GITHUB_REPOSITORY}" --jq .default_branch)"
          if [[ "$current_default_branch" != "$DEFAULT_BRANCH" ]]; then
            echo "The default branch changed after resolution; run the dry run and Release version (apply) again." >&2
            exit 1
          fi

          ref_sha() {
            local namespace="$1"
            local name="$2"
            local exact_ref="refs/${namespace}/${name}"
            gh api "repos/${GITHUB_REPOSITORY}/git/matching-refs/${namespace}/${name}" \
              | jq -r --arg exact_ref "$exact_ref" \
                '[.[] | select(.ref == $exact_ref) | .object.sha][0] // empty'
          }

          selected_sha="$(ref_sha heads "$GITHUB_REF_NAME")"
          if [[
            "$RELEASE_BRANCH" != "$GITHUB_REF_NAME" ||
            "$selected_sha" != "$GITHUB_SHA"
          ]]; then
            echo "The selected release branch changed after dispatch; refusing a stale SHA." >&2
            exit 1
          fi

          target_sha="$GITHUB_SHA"
          existing_tag_sha="$(ref_sha tags "$TAG")"
          if [[ "$TAG_STATE" == "absent" ]]; then
            if [[ -n "$existing_tag_sha" ]]; then
              echo "$TAG appeared after validation; refusing to recreate or move it." >&2
              exit 1
            fi
            tag_object_sha="$(
              gh api --method POST "repos/${GITHUB_REPOSITORY}/git/tags" \
                --raw-field tag="$TAG" \
                --raw-field message="Create immutable final release $TAG" \
                --raw-field object="$target_sha" \
                --raw-field type=commit \
                --jq .sha
            )"
            gh api --method POST "repos/${GITHUB_REPOSITORY}/git/refs" \
              --raw-field ref="refs/tags/${TAG}" \
              --raw-field sha="$tag_object_sha" >/dev/null
          elif [[ -z "$existing_tag_sha" ]]; then
            echo "The existing final tag disappeared; refusing to recreate it." >&2
            exit 1
          fi

          read -r object_type object_sha < <(
            gh api "repos/${GITHUB_REPOSITORY}/git/ref/tags/${TAG}" \
              --jq '[.object.type, .object.sha] | @tsv'
          )
          for _ in 1 2 3 4 5; do
            if [[ "$object_type" == "commit" ]]; then
              break
            fi
            if [[ "$object_type" != "tag" ]]; then
              echo "Unsupported tag target type: $object_type" >&2
              exit 1
            fi
            read -r object_type object_sha < <(
              gh api "repos/${GITHUB_REPOSITORY}/git/tags/${object_sha}" \
                --jq '[.object.type, .object.sha] | @tsv'
            )
          done
          if [[ "$object_type" != "commit" || "$object_sha" != "$target_sha" ]]; then
            echo "$TAG does not resolve to the selected SHA; refusing to move it." >&2
            exit 1
          fi

      - name: Create a PR to the default branch only when differences exist
        env:
          DEFAULT_BRANCH: ${{ needs.resolve.outputs.default_branch }}
          GH_TOKEN: ${{ github.token }}
          RELEASE_BRANCH: ${{ needs.resolve.outputs.release_branch }}
          TAG: ${{ needs.resolve.outputs.tag }}
        shell: bash
        run: |
          set -euo pipefail

          ahead_by="$(
            gh api "repos/${GITHUB_REPOSITORY}/compare/${DEFAULT_BRANCH}...${RELEASE_BRANCH}" \
              --jq .ahead_by
          )"
          if [[ "$ahead_by" == "0" ]]; then
            {
              echo "## Final release completed"
              echo
              echo "- Tag: \`$TAG\`"
              echo "- Commit: \`$GITHUB_SHA\`"
              echo "- Pull request: not created because \`$RELEASE_BRANCH\` has no changes for \`$DEFAULT_BRANCH\`"
            } >> "$GITHUB_STEP_SUMMARY"
            exit 0
          fi

          owner="${GITHUB_REPOSITORY%%/*}"
          open_prs="$(
            gh api --method GET "repos/${GITHUB_REPOSITORY}/pulls" \
              -f state=open \
              -f base="$DEFAULT_BRANCH" \
              -f head="${owner}:${RELEASE_BRANCH}"
          )"
          pr_count="$(jq length <<< "$open_prs")"
          if (( pr_count > 1 )); then
            echo "Multiple matching open pull requests exist; refusing an ambiguous update." >&2
            exit 1
          fi

          if (( pr_count == 1 )); then
            pr_payload="$(jq '.[0]' <<< "$open_prs")"
            pr_status="reused"
          else
            pr_payload="$(
              gh api --method POST "repos/${GITHUB_REPOSITORY}/pulls" \
                --raw-field title="Release $TAG" \
                --raw-field head="$RELEASE_BRANCH" \
                --raw-field base="$DEFAULT_BRANCH" \
                --raw-field body="Synchronize $RELEASE_BRANCH into $DEFAULT_BRANCH after immutable final tag $TAG. This workflow never merges the pull request automatically."
            )"
            pr_status="created"
          fi

          read -r pr_url pr_state pr_base pr_head pr_repo < <(
            jq -r '[.html_url, .state, .base.ref, .head.ref, .head.repo.full_name] | @tsv' \
              <<< "$pr_payload"
          )
          if [[
            "$pr_state" != "open" ||
            "$pr_base" != "$DEFAULT_BRANCH" ||
            "$pr_head" != "$RELEASE_BRANCH" ||
            "$pr_repo" != "$GITHUB_REPOSITORY"
          ]]; then
            echo "The pull request readback does not match the exact release branch and default branch." >&2
            exit 1
          fi

          {
            echo "## Final release completed"
            echo
            echo "- Tag: \`$TAG\`"
            echo "- Commit: \`$GITHUB_SHA\`"
            echo "- Pull request: $pr_status — $pr_url"
            echo "- Automatic merge: disabled by workflow design"
            echo
            echo "No application source or package metadata was read, edited, or committed."
          } >> "$GITHUB_STEP_SUMMARY"
```

### Apply annotations

| YAML surface | Why it is portable |
| --- | --- |
| `confirmed_tag` | Human confirmation is exact data, not a boolean approval |
| apply `concurrency` | Prevents parallel mutations while allowing the current transaction to finish |
| reusable `resolve` job | Recalculates against current tags and selected SHA immediately before writes |
| candidate/final conditions | Require both the semantic operation kind and the resolver-derived `is_final` value before either mutation path runs |
| tag snapshot, regex, default-branch, and selected-SHA checks | Fail closed on stale or noncanonical state |
| annotated tag object plus ref readback | Creates an immutable provider ref and verifies its commit target |
| `final` recovery through `existing-final` | Supports retrying PR reconciliation without moving or recreating the tag |
| compare and exact open-PR query | Avoids empty or duplicate release PRs |
| PR response readback | Verifies open state, exact base/head, and same-repository ownership |
| no merge step | Leaves delivery and branch-protection policy outside version creation |

## Validation and recovery

Use fixture-driven tests for the resolver. Workflow validation must be local
and non-mutating. A successful local validation proves syntax and deterministic
calculation only; it does not prove effective remote token permissions.

Runtime writes are intentionally recoverable:

- a candidate rerun never moves an existing tag or release branch;
- a final rerun accepts an existing canonical final only at the selected commit
  and continues with PR reconciliation;
- a changed tag snapshot, branch SHA, default branch, ambiguous PR set, or
  mismatched readback stops the workflow;
- a PR permission failure leaves the verified final tag intact so the same
  final confirmation can be rerun after repository configuration is fixed.
