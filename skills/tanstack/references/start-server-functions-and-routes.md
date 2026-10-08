# Server Functions And Routes

Use this guide when the issue is about explicit server entrypoints rather than general framework shape.

Owns:
- `createServerFn`, validation, and server-only helper placement
- distinguishing server functions from server routes
- raw HTTP route handling when endpoints live alongside app routes

## Server Functions

Use this section when the task is specifically about `createServerFn`, validator
usage, or server-only helpers invoked through Start.

Workflow:
1. Move server-only work behind `createServerFn` or clearly server-only helpers.
2. Validate inputs and authorize access at the server boundary. A TypeScript
   annotation or identity validator alone does not validate runtime input.
   Check the installed validator API against matching package docs.
3. Keep handler logic clean and avoid leaking secrets into shared modules.

Do not use this section for middleware-wide auth shaping, experimental server
components, or cross-stack Query prefetch and hydration decisions.

## Server Routes

Use this section when the task is specifically about Start server routes, raw
request handling, or API-style endpoints defined in route files.

Workflow:
1. Use server routes for external or intentionally cross-origin HTTP APIs;
   server functions are same-origin RPC for the Start application.
2. Align route file structure with raw HTTP ownership.
3. Keep API-style endpoint handling separate from component-driven data loading.

Do not use this section for general middleware shaping, Router-owned data
fetching, or server-only runtime deployment constraints.

Verification: verify against current TanStack Start server-function or
server-route guidance when exact helper APIs, validator shapes, or route file
behavior matter.

Sources: [Server functions](https://tanstack.com/start/latest/docs/framework/react/guide/server-functions) and [server routes](https://tanstack.com/start/latest/docs/framework/react/guide/server-routes).
