---
name: tanstack-cli-choose-ecosystem-integrations
description: Use the TanStack CLI to inspect ecosystem add-ons, integration metadata, and installable option sets before choosing an add-on.
---

# TanStack CLI Choose Ecosystem Integrations

Use this skill when the task is specifically about discovering or comparing ecosystem integrations exposed through the TanStack CLI.

## Owns

- Integration and add-on discovery through CLI metadata.
- Mapping ecosystem options to installable add-on ids.
- Comparing mutually exclusive or constrained add-on choices.

## Does Not Own

- Executing a known add-on install: use `tanstack-cli-add-addons-existing-app`.
- New app scaffolding once choices are already fixed: use `tanstack-cli-create-app-scaffold`.
- Framework-level design questions outside CLI metadata: use the relevant framework skill.

## Workflow

1. Query the available add-on metadata.
2. Compare option constraints before choosing an install path.
3. Keep the recommendation anchored to what the CLI can actually install.

## Verification

Verify against current `@tanstack/cli` ecosystem metadata commands when exact JSON surfaces or compatibility rules matter.
