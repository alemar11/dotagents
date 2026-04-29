---
name: tanstack-start-server-functions
description: Review TanStack Start createServerFn usage, validation, server-only helpers, and request or response utilities.
---

# TanStack Start Server Functions

Use this skill when the task is specifically about `createServerFn`, validator usage, or server-only helpers invoked through Start.

## Owns

- `createServerFn` design and handler boundaries.
- Input validation at the server-function boundary.
- Server-only helper placement and request or response utilities.

## Does Not Own

- Middleware-wide auth shaping: use `tanstack-start-middlewares`.
- Experimental server components: use `tanstack-react-start-server-components`.
- Cross-stack Query prefetch and hydration decisions: use `tanstack-integration`.

## Workflow

1. Move server-only work behind `createServerFn` or clearly server-only helpers.
2. Validate inputs explicitly at the boundary.
3. Keep handler logic clean and avoid leaking secrets into shared modules.

## Verification

Verify against current TanStack Start server-function guidance when exact helper APIs or validator shapes matter.
