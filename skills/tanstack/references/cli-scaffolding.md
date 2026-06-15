# Scaffolding

Use this guide when the task is about `tanstack create` or selecting the initial shape of a new TanStack app.

Owns:
- choosing framework, template, deployment, toolchain, and bootstrap add-ons
- constructing non-interactive `tanstack create` commands
- distinguishing scaffold-time options from post-scaffold framework work

Workflow:
1. Confirm the desired framework and template.
2. Construct the minimal correct `tanstack create` command.
3. Keep CLI guidance scoped to scaffolding rather than app design.

Do not use this guide for post-scaffold app architecture review, existing-app
add-ons, or ecosystem add-on discovery before choices are fixed.

Escalate to:
- `start.md` for React Start framework design after the app exists
- `router.md` for Router architecture after bootstrap

Verification: verify against current `@tanstack/cli` docs when exact flags or
compatibility constraints matter.
