---
name: tanstack-router-auth-and-guards
description: Review TanStack Router auth gates, beforeLoad checks, redirects, and route-level preconditions.
---

# TanStack Router Auth And Guards

Use this skill when the task is specifically about `beforeLoad`, auth redirects, or route-level access checks.

## Owns

- `beforeLoad` auth and guard logic.
- Route-level redirects and access preconditions.
- Separating guard logic from component rendering.

## Does Not Own

- Middleware-wide Start auth concerns: use `tanstack-start-middlewares`.
- Navigation ergonomics unrelated to guards: use `tanstack-router-navigation`.
- Cross-stack session coordination: use `tanstack-integration`.

## Workflow

1. Place route preconditions in guards, not scattered components.
2. Make redirect behavior explicit and testable.
3. Keep auth ownership clear between Router guards and Start middleware.

## Verification

If the task blends Router guards with Start middleware, prefer `tanstack-integration` or the focused Start middleware skill as appropriate.
