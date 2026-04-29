---
name: tanstack-router-plugin
description: Review TanStack Router plugin setup for generated routes, build wiring, and router-specific bundler integration.
---

# TanStack Router Plugin

Use this skill when the task is specifically about the TanStack Router plugin layer, generated route artifacts, or bundler wiring.

## Owns

- Router plugin setup and generated route integration.
- Build-time wiring needed for Router-specific tooling.
- Plugin-related route generation assumptions.

## Does Not Own

- Route tree design: use `tanstack-router-core`.
- Lazy route strategy: use `tanstack-router-code-splitting`.
- Start framework plugin concerns: use `tanstack-react-start` or `tanstack-start-core`.

## Workflow

1. Identify the build tool and current Router plugin setup.
2. Check that generated routes and route registration assumptions line up.
3. Keep plugin advice scoped to Router build wiring only.

## Verification

Verify against current first-party TanStack Router plugin guidance when exact setup or generated-file behavior matters.
