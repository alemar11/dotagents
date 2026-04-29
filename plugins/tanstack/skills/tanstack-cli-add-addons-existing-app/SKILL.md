---
name: tanstack-cli-add-addons-existing-app
description: Use the TanStack CLI to apply add-ons to existing apps, including add-on resolution and project metadata preconditions.
---

# TanStack CLI Add Addons Existing App

Use this skill when the task is specifically about `tanstack add` for an existing project.

## Owns

- `tanstack add` workflows.
- Add-on id resolution and dependency-chain awareness.
- Existing-project metadata preconditions.

## Does Not Own

- New app scaffolding: use `tanstack-cli-create-app-scaffold`.
- Ecosystem option discovery before a choice is made: use `tanstack-cli-choose-ecosystem-integrations`.
- App architecture after install: use the relevant framework skill.

## Workflow

1. Confirm the project already exists and is a valid CLI target.
2. Resolve the desired add-on ids and dependency implications.
3. Keep the guidance scoped to add-on application, not framework redesign.

## Verification

Verify against current `@tanstack/cli` add-on guidance when exact commands or metadata constraints matter.
