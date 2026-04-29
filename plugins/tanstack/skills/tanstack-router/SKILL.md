---
name: tanstack-router
description: Review, design, and refactor TanStack Router usage with emphasis on type registration, loaders, search params, navigation, route organization, and code splitting.
---

# TanStack Router

Use this skill when a task involves `@tanstack/react-router`, route trees, `createFileRoute`, `createRouter`, `beforeLoad`, `loader`, `loaderDeps`, `validateSearch`, `Link`, `useNavigate`, or lazy route files.

Use this umbrella skill when the Router scope is broad, mixed, or still unclear. When the task collapses to one Router concern, route to the matching focused bundled skill instead of keeping the whole problem here.

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

## Macro Guides

- `references/routing-structure.md`: route tree shape, route ownership, path params, and type registration.
- `references/navigation-and-search.md`: validated search params, URL state, `Link`, and navigation ergonomics.
- `references/data-loading-and-ssr.md`: loaders, `loaderDeps`, preload behavior, cache boundaries, and Router-layer SSR.
- `references/auth-and-failures.md`: `beforeLoad`, redirects, not-found paths, and route error ownership.
- `references/plugin-and-splitting.md`: router plugin wiring, generated routes, and lazy-route code splitting.
- `references/README.md`: quick map from Router problem shape to the right macro guide or focused skill.

## Default Rules

- Register the router type once and let inference flow through the app.
- Prefer validated search params over raw `URLSearchParams` style handling.
- Use `beforeLoad` for auth gates and route-level preconditions.
- Keep critical route config in the main route file and move heavy components to lazy files when appropriate.
- Prefer route loaders for route-owned fetching, especially when paired with TanStack Query preloading.
- Use `from` on hooks and links when narrowing improves precision and TypeScript performance.

## Focused Skills

- `tanstack-router-core`: overall Router mental model and route tree shape.
- `tanstack-router-search-params`: validated search params and typed updates.
- `tanstack-router-path-params`: route params, path structure, and file-route alignment.
- `tanstack-router-navigation`: `Link`, `navigate`, and route-aware hook narrowing.
- `tanstack-router-data-loading`: loaders, `loaderDeps`, preload behavior, and cache boundaries.
- `tanstack-router-auth-and-guards`: `beforeLoad`, redirects, and auth preconditions.
- `tanstack-router-code-splitting`: lazy route files and route-owned code splitting.
- `tanstack-router-not-found-and-errors`: not-found routing and route error handling.
- `tanstack-router-type-safety`: registration, inference, and unnecessary annotations.
- `tanstack-router-ssr`: Router SSR patterns and Start handoff boundaries.
- `tanstack-router-plugin`: Vite or bundler plugin setup for generated routes and build wiring.

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
