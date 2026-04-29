---
name: tanstack-start-server-core
description: Review TanStack Start server runtime behavior, server-only module boundaries, and non-client execution concerns.
---

# TanStack Start Server Core

Use this skill when the task is specifically about the Start server runtime, server-only modules, or behavior that is not safe to frame as isomorphic client code.

## Owns

- Server runtime behavior and server-only boundaries.
- Server-only modules and runtime assumptions.
- Failure paths or constraints unique to the server side of Start.

## Does Not Own

- `createServerFn` API design itself: use `tanstack-start-server-functions`.
- Deployment target packaging decisions: use `tanstack-start-deployments`.
- Query hydration or loader coordination across the stack: use `tanstack-integration`.

## Workflow

1. Separate server-runtime concerns from isomorphic app code.
2. Keep server-only modules explicit and isolated.
3. Check failure paths and runtime assumptions that only apply on the server.

## Verification

Verify against current TanStack Start server-core guidance when exact server-runtime behavior matters.
