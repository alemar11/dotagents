# Middlewares And Server Core

Use this guide when the concern is request-wide behavior or server-runtime boundaries.

Owns:
- middleware ordering, auth, cookies, headers, and shared request shaping
- server-runtime-only assumptions and failure boundaries
- separating middleware concerns from route-local guards or component logic

## Middlewares

Use this section when the task is specifically about Start middleware, reusable
request shaping, or cross-cutting concerns like auth and headers.

Workflow:
1. Move shared request logic into middleware when it truly applies broadly.
2. Keep auth or header shaping ownership out of scattered components.
3. Separate middleware concerns from route-local guards when both exist.

Do not use this section for Router-only guards, server function implementation
details, or end-to-end session coordination across layers.

## Server Core

Use this section when the task is specifically about the Start server runtime,
server-only modules, or behavior that is not safe to frame as isomorphic client
code.

Workflow:
1. Separate server-runtime concerns from isomorphic app code.
2. Keep server-only modules explicit and isolated.
3. Check failure paths and runtime assumptions that only apply on the server.

Do not use this section for `createServerFn` API design, deployment target
packaging decisions, or Query hydration/loader coordination across the stack.

Verification: verify against current TanStack Start middleware and server-core
guidance when exact APIs or ordering behavior matter.
