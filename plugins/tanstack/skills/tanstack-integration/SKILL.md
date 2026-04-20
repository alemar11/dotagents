---
name: tanstack-integration
description: Review and design how TanStack Query, Router, and Start work together, especially around QueryClient ownership, loader prefetching, SSR hydration, and cache boundaries.
---

# TanStack Integration

Use this skill when a task spans more than one TanStack layer, especially Query + Router, or Query + Router + Start together.

## What to Optimize For

- One coherent data-loading model across the stack.
- A single source of truth for cache ownership.
- Predictable loader prefetch and component read patterns.
- SSR dehydration and hydration that line up with the same `QueryClient`.
- Minimal duplicated fetching between loaders and components.

## Workflow

1. Identify the cache owner.
   Decide whether TanStack Query is the primary cache and keep Router/Start aligned with that choice.
2. Put `QueryClient` in the right place.
   It should be available to loaders and components through router context and provider wiring.
3. Standardize query definitions.
   Reuse shared `queryOptions(...)` helpers between loaders, prefetch, and component hooks.
4. Align preloading and reads.
   Prefer `ensureQueryData(...)` in loaders and `useSuspenseQuery(...)` or equivalent reads in components.
5. Verify SSR behavior.
   If Start SSR is in play, dehydrate and hydrate the same query cache deliberately.

## Default Rules

- Keep one `QueryClient` per app boundary unless there is a strong reason not to.
- When Router and Query are paired, let Query own freshness and cache semantics.
- Set Router preload freshness deliberately when Query is the real cache owner.
- Avoid fetching the same resource once in a loader and again in a component with a different key or policy.
- Share query factories across loader and component layers.

## Review Checklist

- Is the same `QueryClient` used consistently across Router and component trees?
- Do route loaders preload with the same query factories used by components?
- Is `defaultPreloadStaleTime` or equivalent router preload behavior aligned with Query ownership?
- Is SSR dehydration/hydration wired to the actual `QueryClient` in use?
- Are data dependencies duplicated across loader and component code?

## Avoid

- Parallel cache systems with unclear ownership.
- Loader fetches that bypass Query while components read from Query anyway.
- Repeating query keys or query definitions separately in loader and component files.
- Mixing stale community patterns with current official TanStack guidance.

## Verification

If `@tanstack/intent` is available, compare integration patterns against the installed Router and Start skills before locking in a recommendation. Otherwise verify against current TanStack docs for Query, Router, and Start together.
