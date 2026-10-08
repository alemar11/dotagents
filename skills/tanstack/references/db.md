# TanStack DB

Use this reference when a task involves TanStack DB, collections, live queries, normalized client data, sync-backed data loading, optimistic mutations, or integrating TanStack DB with TanStack Query.

TanStack DB is currently a beta-area product. Verify exact adapter APIs and collection option names against current docs and installed package versions.

## What to Optimize For

- Collections that model stable entity boundaries.
- Live queries that derive UI data without duplicating backend endpoints.
- Optimistic mutations with explicit transaction and rollback behavior.
- Clear sync ownership between REST, Electric, TrailBase, RxDB, PowerSync,
  IndexedDB, local storage, or local-only data sources.
- Predictable interoperability with TanStack Query where Query is still the fetch/cache layer.

## Workflow

1. Identify the source of truth.
   Decide which collection owns each entity and which backend or sync adapter populates it.
2. Define collection shape and keys.
   Keep IDs, schemas, and mutation handlers explicit before wiring UI queries.
3. Use live queries for derived reads.
   Prefer query-driven UI reads over endpoint-shaped local filtering when DB is the selected model.
4. Make optimistic writes auditable.
   Confirm what mutates immediately, what syncs remotely, and how errors revert or reconcile.
5. Check integration boundaries.
   If TanStack Query is involved, keep Query collection behavior and invalidation rules aligned.

## Client Scope, Persistence, and Offline Work

- Current docs use stable `collectionOptions(...)` descriptors materialized
  through `DbClient`; React uses `DbProvider` and `useDbClient`. Verify installed
  support before migrating older `createCollection(...)` code.
- For SSR, use a separate client per request and hydrate the browser client
  before consumers read collections. Share descriptors, not server collection state.
- Choose eager, on-demand, or progressive sync deliberately; on-demand Query
  collections need backend parameter mapping for the requested subset.
- SQLite row persistence and an offline transaction outbox are separate
  capabilities. Restored rows do not prove server freshness or authorization;
  offline replay needs server idempotency and explicit settlement handling.

## Review Checklist

- Are collections normalized around durable entity IDs?
- Do live queries read from collections rather than duplicating component-local derived state?
- Are optimistic actions transactional and error-aware?
- Is the chosen adapter appropriate for the app's sync and offline requirements?
- Are schema and mutation responsibilities clear enough to test?

## Avoid

- Using TanStack DB as a generic replacement for all local UI state.
- Loading large unbounded collections without a sync/query strategy.
- Mixing direct server writes and collection mutations without reconciliation.
- Treating optimistic success as guaranteed remote persistence.

## Verification

Use the official [overview](https://tanstack.com/db/latest/docs/overview) for
collection adapters and sync modes. Read [SSR](https://tanstack.com/db/latest/docs/guides/ssr),
[SQLite persistence](https://tanstack.com/db/latest/docs/guides/sqlite-persistence),
or [offline transactions](https://tanstack.com/db/latest/docs/guides/offline-transactions)
when that boundary is involved. Match beta APIs to installed versions, including
the Query adapter and its Query dependency.
