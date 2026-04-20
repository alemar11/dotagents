---
name: tanstack-router
description: Review, design, and refactor TanStack Router usage with emphasis on type registration, loaders, search params, navigation, route organization, and code splitting.
---

# TanStack Router

Use this skill when a task involves `@tanstack/react-router`, route trees, `createFileRoute`, `createRouter`, `beforeLoad`, `loader`, `loaderDeps`, `validateSearch`, `Link`, `useNavigate`, or lazy route files.

## What to Optimize For

- End-to-end type safety with minimal manual annotation.
- Predictable route organization and file conventions.
- Validated search params as application state.
- Loader behavior that composes cleanly with TanStack Query.
- Explicit navigation and code-splitting choices.

## Workflow

1. Check router registration first.
   Ensure the app registers the router type once so hooks and `Link` stay fully typed.
2. Validate route boundaries.
   Confirm path params, search params, layouts, and pathless groups match the actual file structure.
3. Review loaders and dependencies.
   Each loader should have a clear cache strategy, and `loaderDeps` should reflect the inputs that really trigger refetch.
4. Tighten search params.
   Prefer `validateSearch` and typed updates over ad hoc string parsing.
5. Recheck navigation ergonomics.
   Use `from` to narrow hook types when a component is route-specific, and use lazy route files when splitting is intended.

## Default Rules

- Register the router type once and let inference flow through the app.
- Prefer validated search params over raw `URLSearchParams` style handling.
- Use `beforeLoad` for auth gates and route-level preconditions.
- Keep critical route config in the main route file and move heavy components to lazy files when appropriate.
- Prefer route loaders for route-owned fetching, especially when paired with TanStack Query preloading.
- Use `from` on hooks and links when narrowing improves precision and TypeScript performance.

## Review Checklist

- Is the router registered correctly for global type inference?
- Are search params validated and updated through typed APIs?
- Do loaders use `loaderDeps` or equivalent cache boundaries where needed?
- Are auth redirects and route guards implemented in `beforeLoad` instead of leaking into components?
- Are route files organized in a way that matches URL structure and layout ownership?

## Avoid

- Mixing React Router or Next.js assumptions into TanStack Router code.
- Manually annotating values that Router already infers.
- Leaving search params unvalidated.
- Putting server-only logic directly in client-first loaders.
- Treating lazy route files as a dumping ground for core route configuration.

## Verification

When the task depends on exact current Router APIs or filenames, compare against the installed `@tanstack/intent` Router skills if available, otherwise verify with the current TanStack Router docs.
