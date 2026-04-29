---
name: tanstack-router-not-found-and-errors
description: Review TanStack Router not-found handling, route error boundaries, and failure-path ownership.
---

# TanStack Router Not Found And Errors

Use this skill when the task is specifically about not-found routes, route error boundaries, or failure-path behavior.

## Owns

- Not-found route behavior.
- Route-level error boundaries and failure ownership.
- Distinguishing user navigation misses from loader or render failures.

## Does Not Own

- General route tree design: use `tanstack-router-core`.
- Start server error boundaries outside Router concerns: use `tanstack-start-server-core`.
- Query mutation error policy: use `tanstack-query`.

## Workflow

1. Separate not-found handling from other error modes.
2. Place error ownership at the right route boundary.
3. Ensure failure paths do not leak unrelated framework assumptions.

## Verification

Verify against current Router error and not-found guidance when exact APIs or file conventions matter.
