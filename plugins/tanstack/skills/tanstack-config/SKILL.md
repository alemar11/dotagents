---
name: tanstack-config
description: Review and implement TanStack Config usage for JavaScript and TypeScript package build, lint, versioning, publishing, and shared configuration workflows.
---

# TanStack Config

Use this skill when a task involves TanStack Config, package build tooling, lint or formatting configuration, release or publishing setup, shared TypeScript package configuration, or repository package-quality workflows.

TanStack Config is a package/tooling surface. Verify exact commands and config file names against the installed package and current docs before changing a repository's release pipeline.

## What to Optimize For

- A small, predictable package configuration surface.
- Build, lint, typecheck, and publish commands that work in CI and locally.
- Clear ownership between shared config and package-specific overrides.
- Release behavior that is explicit about versioning, generated artifacts, and registry targets.

## Workflow

1. Identify the package boundary.
   Check whether the repo is a single package, workspace, library package, or app package.
2. Inspect existing scripts and config.
   Prefer existing package-manager conventions and CI commands before introducing new config.
3. Add shared config only where it removes real duplication.
   Keep package-specific exceptions local and documented by command names, not long prose.
4. Validate generated outputs.
   Confirm build outputs, type declarations, lint behavior, and publish metadata match the package contract.
5. Recheck CI and release assumptions.
   Ensure the configured commands are non-interactive and safe for automation.

## Review Checklist

- Do package scripts match the selected package manager and workspace layout?
- Are build outputs, type declarations, and package exports aligned?
- Are lint/format/typecheck commands deterministic in CI?
- Is publish configuration explicit about access, registry, and generated files?
- Are package-specific overrides minimal and justified?

## Avoid

- Replacing a working repo-specific release flow just to standardize naming.
- Adding shared config that obscures package-specific build requirements.
- Assuming package exports, declaration generation, or publish access without checking `package.json`.
- Running formatter or release commands that rewrite files before the requested implementation step.

## Verification

Verify exact TanStack Config APIs, command names, and supported package-manager behavior against current TanStack Config docs and the target repo's installed package versions.
