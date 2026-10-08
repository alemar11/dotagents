# Scaffolding

Use this guide when the task is about `tanstack create` or selecting the initial shape of a new TanStack app.

Owns:
- choosing framework, template, deployment, toolchain, and bootstrap add-ons
- constructing non-interactive `tanstack create` commands
- distinguishing scaffold-time options from post-scaffold framework work

Workflow:
1. Confirm framework and app mode. Current CLI supports React and Solid and
   creates a Start app by default. `--router-only` selects a Router app and
   excludes add-ons, deployment adapters, and templates.
2. Discover compatible flags from the installed CLI. `--blank` selects a minimal
   Start scaffold; `-y` accepts defaults and does not imply a minimal scaffold.
   Use `--no-git` and `--no-install` when those side effects are outside scope.
   Do not force an overwrite of an existing directory merely to make it run.
3. Keep CLI guidance scoped to scaffolding rather than app design.

Do not use this guide for post-scaffold app architecture review, existing-app
add-ons, or ecosystem add-on discovery before choices are fixed.

Escalate to:
- `start.md` for React Start framework design after the app exists
- `router.md` for Router architecture after bootstrap

Verification: verify against current `@tanstack/cli` docs when exact flags or
compatibility constraints matter.

Use the current `@tanstack/cli create` entrypoint when replacing legacy
`create-tsrouter-app` or `create-tanstack-app` instructions. Preserve the
existing project when the task is migration rather than new scaffolding.

Source: [CLI scaffold options](https://tanstack.com/cli/latest/docs/cli-reference).
