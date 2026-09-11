---
name: github-releases
description: "Inspect, draft, publish, or update GitHub Releases, notes, assets, and package availability."
---

# GitHub Releases

Before remote `git`, `gh`, or registry commands, use the runtime's narrowest
network-enabled context for that command family. Keep local-only git sandboxed.
Verify `gh` is runnable (`command -v gh`, `gh --version`) and authentication
with:

```sh
gh auth status --active --hostname github.com --json hosts \
  --jq '.hosts["github.com"] | map(select(.active == true) | {state, scopes})'
```

Require exactly one active account with `state=success`. Treat
restricted-environment network failures as inconclusive. Do not install or
refresh `gh` without explicit authorization. Network permission is not
mutation authority.

## Transport

Use authenticated `gh` for every GitHub provider read and write. Use file-backed
`gh api --input` requests whenever a mutation includes a curated title, body,
or other free-form provider text. This skill is scriptless by design.

## Role

Handle release work with direct `git`, `gh release`, and registry/package
commands. Use this skill for release readiness, tag checks, generated or curated
notes, release-description improvements, release asset inspection, draft or
published GitHub Releases, and package availability confirmation.

## Invocation fields

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `release_operation` | `inspect`, `create-tag`, `draft`, `publish`, `update-notes`, `upload-asset`, `delete` | `inspect` | Requested tag or GitHub Release lifecycle operation. `publish` also covers an explicitly requested direct create-and-publish operation. |
| `mutation_mode` | `apply`, `dry-run` | `dry-run` | For write-shaped operations, whether to execute or preview. Omit for pure reads. |

| Input evidence | Canonical invocation |
| --- | --- |
| `create a release` or `create a draft release` without direct publication language | `release_operation=draft`, `mutation_mode=apply` |
| `create and publish the release` for one resolvable existing tag | `release_operation=publish`, `mutation_mode=apply`; skip notes preview and draft stage |
| `improve the release description` | `release_operation=update-notes`, `mutation_mode=apply` |
| `dry run`, `preview only`, `local only`, or `do not mutate` | `mutation_mode=dry-run` |

## Workflow

1. Confirm the repository and default branch.
2. Inspect tags and existing releases before creating anything.
3. Accept an exact tag from the caller. When `$versioning` selected it, retain
   that skill's verified target and comparison range; do not recalculate its
   SemVer policy inside this provider-primitive skill.
4. Compare the intended version against package manifests or changelog files
   only when that repository maintains them and the operation is not the
   application-code-blind versioning controller.
5. Treat release creation, tag creation, description updates, asset upload,
   publishing, and deletion as mutations that require explicit user
   authorization. For a requested write without that authorization, resolve
   `mutation_mode=dry-run` and return the proposed command or draft release
   notes only.
6. Resolve the requested action to one `release_operation`. Omit
   `mutation_mode` for `inspect`; for a write-shaped operation, resolve
   `mutation_mode=apply|dry-run` before using `gh release create
   --generate-notes` or another mutating command.
7. Apply these creation defaults:
   - `create a release` prepares the exact notes and creates a draft with
     `release_operation=draft`; ask only when a material choice is unresolved;
   - an explicit `create and publish` request resolves directly to
     `release_operation=publish` and `mutation_mode=apply`; it skips the notes
     preview and draft stage without skipping readiness or verification;
   - a preview-only request creates no draft; draft creation is a mutation.
8. For `release_operation=update-notes`, inspect the existing title and body,
   prepare the exact replacement or diff, honor authorization for the
   requested update, change only those text fields, and verify exact readback.
   Direct create-and-publish authority does not carry over to a later notes
   update.
9. After a mutation, verify the resulting tag, GitHub Release, notes, asset
   state, and any package registry availability requested by the user.

## References

- `references/workflows.md`: release, tag, notes, and asset workflows.
- `references/states.md`: release lifecycle and transient planning states.
- `references/package-checks.md`: registry availability checks.
