---
name: tanstack-router-code-splitting
description: Review TanStack Router lazy route files, route-level code splitting, and route config placement.
---

# TanStack Router Code Splitting

Use this skill when the task is specifically about lazy route files, code-splitting boundaries, or where route config should live.

## Owns

- Lazy route files and split boundaries.
- Keeping heavy UI separate from core route config.
- Route-level code-splitting tradeoffs.

## Does Not Own

- General route tree design: use `tanstack-router-core`.
- Build plugin wiring: use `tanstack-router-plugin`.
- SSR tradeoffs: use `tanstack-router-ssr`.

## Workflow

1. Decide what route config must stay eager.
2. Move heavy route UI to lazy boundaries where it improves startup or bundle shape.
3. Avoid scattering critical route identity across lazy files.

## Verification

Verify against current Router lazy-route guidance when exact conventions matter.
