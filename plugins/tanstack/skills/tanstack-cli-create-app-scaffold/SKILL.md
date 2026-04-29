---
name: tanstack-cli-create-app-scaffold
description: Use the TanStack CLI to scaffold apps with framework, template, deployment, toolchain, and add-on choices.
---

# TanStack CLI Create App Scaffold

Use this skill when the task is specifically about `tanstack create`, non-interactive scaffolding, or choosing initial framework and template flags.

## Owns

- `tanstack create` command construction.
- Framework, template, toolchain, deployment, and add-on flag choices.
- Non-interactive scaffolding decisions.

## Does Not Own

- Post-scaffold app architecture review: use `tanstack-react-start`, `tanstack-router`, or `tanstack-query`.
- Existing-app add-ons: use `tanstack-cli-add-addons-existing-app`.
- Ecosystem add-on discovery: use `tanstack-cli-choose-ecosystem-integrations`.

## Workflow

1. Confirm the desired framework and template.
2. Construct the minimal correct `tanstack create` command.
3. Keep CLI guidance scoped to scaffolding rather than app design.

## Verification

Verify against the current `@tanstack/cli` skill or docs when exact flags or compatibility constraints matter.
