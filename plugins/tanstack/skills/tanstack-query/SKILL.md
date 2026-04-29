---
name: tanstack-query
description: Review, design, and refactor TanStack Query usage with emphasis on query keys, queryOptions, cache policy, invalidation, optimistic updates, and SSR-safe data flows.
---

# TanStack Query

Use this skill when a task involves `@tanstack/react-query`, `QueryClient`, `useQuery`, `useSuspenseQuery`, `useMutation`, `queryOptions`, cache invalidation, optimistic updates, or persistence.

This plugin currently owns TanStack Query guidance as a local gap-filler. As of the current observed TanStack Intent registry state, TanStack does not publish a first-party Query Intent package.

## What to Optimize For

- Stable, predictable query keys.
- Reusable `queryOptions(...)` factories instead of inline duplication.
- Explicit `staleTime`, `gcTime`, retry, and suspense choices.
- Targeted invalidation instead of blanket cache resets.
- Clear separation between server state and local UI state.

## Workflow

1. Identify the cache shape first.
   Define the canonical key hierarchy before touching hooks or invalidation.
2. Centralize query definitions.
   Prefer query key factories and `queryOptions(...)` helpers for anything reused across components, loaders, or prefetch paths.
3. Check invalidation and mutation coupling.
   Each mutation should either update cache directly or invalidate the exact affected scope.
4. Review fetch behavior.
   Ensure query functions are abort-aware when practical and do not hide dependencies outside the key.
5. Verify SSR and router integration.
   If Router or Start is involved, prefer loader prefetch with `ensureQueryData(...)` and component reads with `useSuspenseQuery(...)`.

## Default Rules

- Always use array query keys.
- For non-trivial apps, organize keys through factories instead of ad hoc literals.
- Prefer `queryOptions(...)` when the same query is used in multiple places.
- Include every cache-relevant input in the query key.
- Use `placeholderData` and `initialData` deliberately; they solve different problems.
- Keep optimistic updates reversible and scoped.
- Make mutation side effects explicit: update cache, invalidate cache, or both.
- Disable or tune retries for operations where repeated failure is expensive or noisy.

## Review Checklist

- Are the query keys stable, serializable, and complete?
- Is `queryOptions(...)` used where reuse or type inference matters?
- Do mutations invalidate too much, too little, or the wrong branch?
- Are `staleTime` and `gcTime` chosen intentionally rather than left implicit everywhere?
- Is server data being copied into local component state without a clear reason?

## Routing

- Keep this skill as the broad entrypoint for Query work.
- If the task is really about Router or Start boundaries, hand off to `tanstack-router`, `tanstack-start`, or `tanstack-integration`.
- If the task is about Query plus Router loader prefetch or Start SSR hydration, prefer `tanstack-integration`.

## Avoid

- String query keys.
- Inline keys repeated across many files.
- Blanket `invalidateQueries()` without a scoped key.
- Treating TanStack Query as a generic client-state store.
- Copying stale community examples when the installed package or official docs say otherwise.

## Verification

When exact current API names matter, verify against the current TanStack Query docs before claiming a pattern is authoritative. Do not imply there is a first-party TanStack Query Intent package unless one is actually present in the installed project or current upstream registry.
