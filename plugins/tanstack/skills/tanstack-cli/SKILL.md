---
name: tanstack-cli
description: Review and use TanStack CLI workflows for scaffolding, add-ons, ecosystem discovery, custom add-on iteration, and machine-readable docs lookup.
---

# TanStack CLI

Use this umbrella skill when a task involves the TanStack CLI broadly, or when the exact CLI workflow is not yet narrowed to scaffolding, existing-app add-ons, ecosystem discovery, custom add-on authoring, or docs queries.

## What to Optimize For

- Correct CLI workflow selection before constructing commands.
- Minimal non-interactive command shapes that preserve intent.
- Discovery from CLI metadata instead of stale assumptions.
- Clear separation between CLI mechanics and framework design guidance.

## Workflow

1. Identify the CLI job first.
   Decide whether the task is about scaffolding, add-ons, ecosystem selection, custom add-on authoring, or machine-readable docs discovery.
2. Use the matching macro guide.
   Consult the appropriate reference doc under `references/` before reaching for a leaf skill or composing commands.
3. Keep scope on the CLI surface.
   If the task turns into framework architecture, hand off to `tanstack-router`, `tanstack-react-start`, `tanstack-query`, or `tanstack-integration`.

## Macro Guides

- `references/scaffolding.md`: `tanstack create` app scaffolding, framework choice, templates, deployments, and add-on-aware bootstrap decisions.
- `references/addons-existing-app.md`: `tanstack add` workflows, add-on ids, dependency chains, and existing-project preconditions.
- `references/ecosystem-integrations.md`: ecosystem metadata queries, integration comparison, and installable option selection.
- `references/custom-addons-dev-watch.md`: custom add-on and template authoring, compile loops, and dev-watch iteration.
- `references/docs-and-library-metadata.md`: `tanstack doc`, `tanstack libraries`, and machine-readable discovery before making tool-sensitive claims.
- `references/README.md`: quick map of which CLI workflow owns which task.

## Focused Skills

- `tanstack-cli-create-app-scaffold`
- `tanstack-cli-add-addons-existing-app`
- `tanstack-cli-choose-ecosystem-integrations`
- `tanstack-cli-maintain-custom-addons-dev-watch`
- `tanstack-cli-query-docs-library-metadata`

## Avoid

- Treating framework design questions as CLI questions.
- Reaching for `tanstack create` when the app already exists and `tanstack add` is the actual job.
- Guessing integration or add-on availability without checking CLI metadata first.
- Mixing custom add-on authoring guidance into ordinary app-consumer workflows.

## Verification

When exact flags, JSON shapes, or CLI capability boundaries matter, verify against the current `@tanstack/cli` docs or installed first-party CLI Intent skills.
