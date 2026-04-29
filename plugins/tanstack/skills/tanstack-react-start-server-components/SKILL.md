---
name: tanstack-react-start-server-components
description: Review experimental TanStack React Start server component setup, composition rules, and caching caveats.
---

# TanStack React Start Server Components

Use this skill when the task is specifically about TanStack Start server components, their setup, or their experimental constraints.

## Owns

- Server component setup and feature gating.
- Composition rules and slot limitations.
- Caching caveats and current experimental boundaries.

## Does Not Own

- General server functions: use `tanstack-start-server-functions`.
- Whole-app framework setup unrelated to server components: use `tanstack-react-start`.
- Broad Query hydration design: use `tanstack-integration`.

## Workflow

1. Confirm that the app is intentionally using the server component feature set.
2. Check setup, rendering boundaries, and client/server composition rules.
3. Keep recommendations conservative because the feature is experimental.

## Verification

Verify against current TanStack React Start server component docs before treating any pattern as stable.
