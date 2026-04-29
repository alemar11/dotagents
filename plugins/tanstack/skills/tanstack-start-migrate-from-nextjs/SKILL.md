---
name: tanstack-start-migrate-from-nextjs
description: Review and plan migrations from Next.js App Router patterns to TanStack Start equivalents.
---

# TanStack Start Migrate From Nextjs

Use this skill when the task is specifically about moving from Next.js App Router conventions to TanStack Start.

## Owns

- Concept mapping from Next.js App Router to Start.
- Migration order and high-risk mental-model shifts.
- Removing stale `use server`, `use client`, or Next-specific assumptions.

## Does Not Own

- General Start framework design without migration context: use `tanstack-react-start`.
- Detailed server function implementation after the migration boundary is clear: use `tanstack-start-server-functions`.
- Query integration redesign after migration: use `tanstack-integration`.

## Workflow

1. Identify which Next.js assumptions are still present.
2. Map routes, server actions, middleware, and config to Start equivalents.
3. Prioritize the execution-model shift before code cleanup.

## Verification

Verify against the current TanStack Start migration guidance when exact migration steps or replacements matter.
