---
name: tanstack-start-execution-model
description: Review TanStack Start isomorphic execution boundaries, module placement, and server versus client responsibilities.
---

# TanStack Start Execution Model

Use this skill when the task is specifically about where code runs, which modules are safe to share, or how Start's isomorphic execution model affects design.

## Owns

- Server versus client responsibility boundaries.
- Shared-module safety and module placement.
- Start's isomorphic execution model.

## Does Not Own

- Server function APIs themselves: use `tanstack-start-server-functions`.
- Middleware pipeline design: use `tanstack-start-middlewares`.
- Query hydration boundaries across the full stack: use `tanstack-integration`.

## Workflow

1. Identify where the code actually executes.
2. Move server-only behavior behind explicit server boundaries.
3. Keep shared modules safe for both environments.

## Verification

Verify against current TanStack Start execution-model guidance when exact boundary rules matter.
