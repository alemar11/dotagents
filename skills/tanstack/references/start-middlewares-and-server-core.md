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
1. Choose request middleware for SSR, HTTP routes, and server functions; choose
   function middleware for server-function input validation or client hooks.
   Request middleware cannot depend on function middleware.
2. Keep auth or header shaping ownership out of scattered components.
3. Preserve server-function same-origin protection when customizing startup.
   Current docs require explicitly installing `createCsrfMiddleware()` when
   defining `src/start.ts`; verify support and defaults in the installed version.
   Check proxy/public-origin behavior rather than disabling origin checks.

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

Sources: [Middleware](https://tanstack.com/start/latest/docs/framework/react/guide/middleware) and [server-function origin protection](https://tanstack.com/start/latest/docs/framework/react/guide/server-functions).
