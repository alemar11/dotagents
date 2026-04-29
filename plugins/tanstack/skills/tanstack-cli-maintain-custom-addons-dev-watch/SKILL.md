---
name: tanstack-cli-maintain-custom-addons-dev-watch
description: Use the TanStack CLI to build and iterate custom add-ons or templates with dev-watch workflows.
---

# TanStack CLI Maintain Custom Addons Dev Watch

Use this skill when the task is specifically about authoring or iterating custom TanStack CLI add-ons and templates.

## Owns

- `tanstack add-on init`, compile, and dev-watch workflows.
- Local iteration loops for custom CLI add-ons.
- Watch-path and template-maintenance preconditions.

## Does Not Own

- Installing existing add-ons: use `tanstack-cli-add-addons-existing-app`.
- App scaffolding for end users: use `tanstack-cli-create-app-scaffold`.
- General plugin or skill maintenance in this repo: use the repo maintainer workflow, not this runtime skill.

## Workflow

1. Confirm the task is about custom add-on or template development.
2. Set up the correct init, compile, and watch loop.
3. Keep guidance scoped to CLI authoring mechanics, not framework design.

## Verification

Verify against current `@tanstack/cli` add-on authoring guidance when exact commands or watch-mode constraints matter.
