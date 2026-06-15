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
2. Validate inputs explicitly at the boundary.
3. Keep handler logic clean and avoid leaking secrets into shared modules.

Do not use this section for middleware-wide auth shaping, experimental server
components, or cross-stack Query prefetch and hydration decisions.

## Server Routes

Use this section when the task is specifically about Start server routes, raw
request handling, or API-style endpoints defined in route files.

Workflow:
1. Confirm the endpoint really belongs in a server route rather than a server
   function.
2. Align route file structure with raw HTTP ownership.
3. Keep API-style endpoint handling separate from component-driven data loading.

Do not use this section for general middleware shaping, Router-owned data
fetching, or server-only runtime deployment constraints.

Verification: verify against current TanStack Start server-function or
server-route guidance when exact helper APIs, validator shapes, or route file
behavior matter.
