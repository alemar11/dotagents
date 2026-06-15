# TanStack CLI

Use this umbrella reference when a task involves the TanStack CLI broadly, or when the exact CLI workflow is not yet narrowed to scaffolding, existing-app add-ons, ecosystem discovery, custom add-on authoring, or docs queries.

## Which TanStack Reference Should I Use?

Use this quick map when you know the intent but not the reference file:

- **CLI scaffolding / templates / deployments** → `cli-scaffolding.md`
- **Add-ons to an existing app** → `cli-addons-existing-app.md`
- **Compare integrations / pick options** → `cli-ecosystem-integrations.md`
- **Author a custom add-on / dev-watch loop** → `cli-custom-addons-dev-watch.md`
- **Ask “what does the CLI support?” / machine-readable docs** → `cli-docs-and-library-metadata.md`
- **Framework architecture (not CLI)** → `router.md`, `start.md`, `query.md`, `integration.md`

## What to Optimize For

- Correct CLI workflow selection before constructing commands.
- Minimal non-interactive command shapes that preserve intent.
- Discovery from CLI metadata instead of stale assumptions.
- Clear separation between CLI mechanics and framework design guidance.

## Workflow

1. Identify the CLI job first.
   Decide whether the task is about scaffolding, add-ons, ecosystem selection, custom add-on authoring, or machine-readable docs discovery.
2. Use the matching macro guide.
   Consult the appropriate reference doc under `references/` before composing commands.
3. Keep scope on the CLI surface.
   If the task turns into framework architecture, hand off to `router.md`, `start.md`, `query.md`, or `integration.md`.

## Macro Guides

- `cli-scaffolding.md`: `tanstack create` app scaffolding, framework choice, templates, deployments, and add-on-aware bootstrap decisions.
- `cli-addons-existing-app.md`: `tanstack add` workflows, add-on ids, dependency chains, and existing-project preconditions.
- `cli-ecosystem-integrations.md`: ecosystem metadata queries, integration comparison, and installable option selection.
- `cli-custom-addons-dev-watch.md`: custom add-on and template authoring, compile loops, and dev-watch iteration.
- `cli-docs-and-library-metadata.md`: `tanstack doc`, `tanstack libraries`, and machine-readable discovery before making tool-sensitive claims.
- `README.md`: quick map of which CLI workflow owns which task.

## Focused References

- `cli-scaffolding.md`
- `cli-addons-existing-app.md`
- `cli-ecosystem-integrations.md`
- `cli-custom-addons-dev-watch.md`
- `cli-docs-and-library-metadata.md`

## Avoid

- Treating framework design questions as CLI questions.
- Reaching for `tanstack create` when the app already exists and `tanstack add` is the actual job.
- Guessing integration or add-on availability without checking CLI metadata first.
- Mixing custom add-on authoring guidance into ordinary app-consumer workflows.

## Verification

When exact flags, JSON shapes, or CLI capability boundaries matter, verify against the current `@tanstack/cli` docs or installed first-party CLI Intent skills.
