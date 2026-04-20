---
name: tanstack-start
description: Review, design, and refactor TanStack Start apps with emphasis on the execution model, server functions, middleware, environment boundaries, auth, and SSR-safe behavior.
---

# TanStack Start

Use this skill when a task involves `@tanstack/react-start`, `createServerFn`, middleware, server routes, SSR, hydration, environment variables, cookies, or auth flows in a TanStack Start app.

## What to Optimize For

- Correct server/client boundaries.
- Safe handling of secrets and environment variables.
- Current server-function APIs and middleware order.
- SSR and hydration behavior that matches TanStack Start's execution model.
- Clear separation between route code, server-only logic, and shared types.

## Workflow

1. Establish the execution model first.
   TanStack Start is isomorphic by default; check where code actually runs before changing loaders, imports, or env access.
2. Move server-only work to server functions.
   Database access, filesystem access, and secrets should live behind `createServerFn(...)` or other server-only boundaries.
3. Validate inputs at the boundary.
   Prefer the current server-function validation API used by the installed TanStack version.
4. Review middleware and auth flow.
   Keep request shaping, auth checks, and shared server concerns in middleware or server utilities rather than scattered component logic.
5. Recheck SSR and hydration safety.
   Watch for browser-only APIs, module-level env leaks, and server/client mismatch patterns.

## Default Rules

- Treat loaders as isomorphic unless the current framework docs prove otherwise.
- Keep secrets out of shared modules and client bundles.
- Prefer `VITE_` public environment variables for client-visible config in Vite-based Start apps.
- Verify the current server-function validator API for the installed version instead of copying stale examples.
- Keep server-only files and shared files clearly separated.
- Use middleware for reusable request concerns rather than repeating auth and header logic.

## Review Checklist

- Is any server-only work happening directly in loaders or shared modules?
- Are secrets or raw `process.env` values leaking into code that can ship client-side?
- Are server-function inputs validated using the current supported API?
- Does middleware own shared auth, session, or header concerns where appropriate?
- Are SSR and hydration edge cases handled for browser-only code?

## Avoid

- Assuming TanStack Start behaves like Next.js or Remix.
- Using outdated community examples without checking the installed version.
- Using `NEXT_PUBLIC_` naming in a Vite-based Start setup.
- Leaving server-function input validation implicit.
- Hiding server/client boundary problems behind type casts.

## Verification

When exact Start APIs matter, compare against the installed `@tanstack/intent` Start skills if available, otherwise verify with the current TanStack Start docs before finalizing guidance.
