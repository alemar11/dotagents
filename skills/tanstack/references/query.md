# TanStack Query

Use this reference when a task involves `@tanstack/react-query`, `QueryClient`, `useQuery`, `useSuspenseQuery`, `useMutation`, `queryOptions`, cache invalidation, optimistic updates, or persistence.

Use this reference for the affected Query behavior. Read Router, Start, or
integration guidance only when that boundary is involved.
React's current docs target v5; match the installed framework adapter and
version before applying examples or migration advice.

## What to Optimize For

- Stable, predictable query keys.
- Reusable `queryOptions(...)` factories instead of inline duplication.
- Explicit `staleTime`, `gcTime`, retry, and suspense choices.
- Targeted invalidation instead of blanket cache resets.
- Clear separation between server state and local UI state.

## Workflow

1. Inspect the affected query keys and their inputs.
   Change the key hierarchy only when the requested behavior requires it.
2. Centralize query definitions.
   Prefer query key factories and `queryOptions(...)` helpers for anything reused across components, loaders, or prefetch paths.
3. Check invalidation and mutation coupling.
   Each mutation should either update cache directly or invalidate the exact affected scope.
4. Review fetch behavior.
   Ensure query functions are abort-aware when practical and do not hide dependencies outside the key.
5. Verify SSR and router integration.
   Share query options between loader prefetch and `useSuspenseQuery(...)`.
   Current Start guidance uses `queryClient.query(...)` with Query 5.102+;
   preserve version-appropriate APIs such as `ensureQueryData(...)` in older
   projects. Read [integration.md](integration.md) for the SSR boundary.

## Default Rules

- Always use array query keys.
- For non-trivial apps, organize keys through factories instead of ad hoc literals.
- Prefer `queryOptions(...)` when the same query is used in multiple places.
- Include every cache-relevant input in the query key.
- Use `placeholderData` and `initialData` deliberately; they solve different problems.
- Distinguish freshness from retention: `staleTime` controls freshness and
  `gcTime` collects inactive queries. `Infinity` still permits invalidation;
  `staleTime: 'static'` blocks invalidation-driven refetches when supported.
- Keep optimistic updates reversible and scoped.
- Make mutation side effects explicit: update cache, invalidate cache, or both.
- Disable or tune retries for operations where repeated failure is expensive or noisy.
- For SSR, create an isolated server `QueryClient` per request and hydrate the
  browser cache; never share user-specific cached data through a server singleton.

## Review Checklist

- Are the query keys stable, serializable, and complete?
- Is `queryOptions(...)` used where reuse or type inference matters?
- Do mutations invalidate too much, too little, or the wrong branch?
- Are `staleTime` and `gcTime` chosen intentionally rather than left implicit everywhere?
- Is server data being copied into local component state without a clear reason?

## Routing

- Keep this reference as the broad entrypoint for Query work.
- If the task is really about Router or Start boundaries, hand off to `router.md`, `start.md`, or `integration.md`.
- If the task is about Query plus Router loader prefetch or Start SSR hydration, prefer `integration.md`.

## Avoid

- String query keys.
- Inline keys repeated across many files.
- Blanket `invalidateQueries()` without a scoped key.
- Treating TanStack Query as a generic client-state store.
- Copying stale community examples when the installed package or official docs say otherwise.

## Verification

Check the official [defaults](https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults),
[query options](https://tanstack.com/query/latest/docs/framework/react/guides/query-options),
and [SSR guide](https://tanstack.com/query/latest/docs/framework/react/guides/ssr)
for the installed adapter. Use first-party Intent skills when discovered in
the installed project or current registry; do not infer coverage from another product.
