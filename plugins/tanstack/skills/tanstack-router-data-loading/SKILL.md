---
name: tanstack-router-data-loading
description: Review TanStack Router loaders, loaderDeps, preload behavior, and route-owned data loading boundaries.
---

# TanStack Router Data Loading

Use this skill when the task is specifically about route loaders, `loaderDeps`, preload freshness, or route-owned data loading.

## Owns

- Loader design and route-owned fetch boundaries.
- `loaderDeps` and refetch triggers.
- Preload behavior and route-level data freshness.

## Does Not Own

- QueryClient ownership across Router and Query: use `tanstack-integration`.
- Search params: use `tanstack-router-search-params`.
- SSR hydration decisions spanning Start: use `tanstack-integration`.

## Workflow

1. Identify what the route should own directly.
2. Check loader dependencies and invalidation triggers.
3. Align preload behavior with the actual cache owner.

## Verification

When Query integration or Start SSR is involved, hand off to `tanstack-integration`; otherwise verify against current Router loader docs.
