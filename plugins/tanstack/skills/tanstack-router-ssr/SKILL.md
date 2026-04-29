---
name: tanstack-router-ssr
description: Review TanStack Router SSR patterns, hydration boundaries, and when Router SSR should defer to TanStack Start.
---

# TanStack Router SSR

Use this skill when the task is specifically about TanStack Router SSR behavior, hydration boundaries, or manual SSR wiring.

## Owns

- Router-specific SSR patterns.
- Hydration boundaries at the Router layer.
- Knowing when Router SSR should defer to Start-based SSR.

## Does Not Own

- Full Start SSR and server runtime concerns: use `tanstack-start-server-core` or `tanstack-start`.
- Query cache dehydration across Router and Start: use `tanstack-integration`.
- Route-level code splitting unrelated to SSR: use `tanstack-router-code-splitting`.

## Workflow

1. Confirm whether the app is using Router SSR directly or via Start.
2. Keep hydration boundaries consistent with the actual runtime model.
3. Avoid mixing Start-first SSR assumptions into plain Router SSR without evidence.

## Verification

When Start is the actual SSR surface, route to the focused Start skill or `tanstack-integration`; otherwise verify against current Router SSR docs.
