---
name: tanstack-start-server-routes
description: Review TanStack Start server routes, raw HTTP handling, and file-route alignment for API-style endpoints.
---

# TanStack Start Server Routes

Use this skill when the task is specifically about Start server routes, raw request handling, or API-style endpoints defined in route files.

## Owns

- Server route file placement and shape.
- Raw HTTP request and response handling.
- Distinguishing server routes from server functions.

## Does Not Own

- General middleware shaping: use `tanstack-start-middlewares`.
- Route loaders and Router-owned data fetching: use `tanstack-router-data-loading`.
- Server-only runtime deployment constraints: use `tanstack-start-server-core`.

## Workflow

1. Confirm the endpoint really belongs in a server route rather than a server function.
2. Align route file structure with raw HTTP ownership.
3. Keep API-style endpoint handling separate from component-driven data loading.

## Verification

Verify against current TanStack Start server-route guidance when exact route file or HTTP utility behavior matters.
