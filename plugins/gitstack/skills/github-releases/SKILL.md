---
name: github-releases
description: Check, plan, draft, publish, and validate GitHub releases, tags, release notes, and packages.
---

# GitHub Releases

## Transport

Prefer the required GitHub connector for supported remote reads and writes. Use
`gh` for connector gaps. An authorized connector write may fall back
automatically only when the operation and repository are identical, `gh`
authentication and access succeed, and the transport switch is reported.


## Role

Handle release work with direct `git`, `gh release`, and registry/package
commands. This skill is scriptless by design.

Use this skill for release readiness, tag checks, generated notes, release
asset inspection, draft or published GitHub Releases, and package availability
confirmation.

## Workflow

1. Confirm the repository and default branch.
2. Inspect tags and existing releases before creating anything.
3. Compare the intended version against package manifests or changelog files.
4. Treat release creation, tag creation, asset upload, publishing, and deletion
   as mutations that require explicit user authorization. Without that
   authorization, return the proposed command or draft release notes only.
5. Generate or review notes with `gh release view` and
   `gh release create --generate-notes` only inside the resolved write mode.
6. After publishing, verify GitHub Release state and any package registry
   availability requested by the user.

## References

- `references/workflows.md`: release, tag, notes, and asset workflows.
- `references/package-checks.md`: registry availability checks.
