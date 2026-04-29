---
name: tanstack-start-middlewares
description: Review TanStack Start middleware chains for auth, cookies, headers, and reusable request concerns.
---

# TanStack Start Middlewares

Use this skill when the task is specifically about Start middleware, reusable request shaping, or cross-cutting concerns like auth and headers.

## Owns

- Middleware ordering and composition.
- Auth, cookies, headers, and shared request concerns.
- Middleware ownership versus component or route duplication.

## Does Not Own

- Router-only guards: use `tanstack-router-auth-and-guards`.
- Server function implementation details: use `tanstack-start-server-functions`.
- End-to-end session coordination across layers: use `tanstack-integration`.

## Workflow

1. Move shared request logic into middleware when it truly applies broadly.
2. Keep auth or header shaping ownership out of scattered components.
3. Separate middleware concerns from route-local guards when both exist.

## Verification

Verify against current TanStack Start middleware guidance when exact APIs or ordering behavior matter.
