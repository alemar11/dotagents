# TanStack Store

Use this reference when a task involves TanStack Store, framework-agnostic reactive state, immutable store updates, derived state, selectors, subscriptions, or React/Vue/Solid/Angular/Svelte store adapters.

## What to Optimize For

- A small store boundary with explicit ownership.
- Immutable updates that preserve predictable subscriptions.
- Selectors that subscribe only to the state each consumer needs.
- Clear separation between client UI state, server state, and persistent domain data.

## Workflow

1. Confirm Store is the right state owner.
   Use TanStack Query or DB for server/domain data when those are the real owners.
2. Define the state shape.
   Keep state normalized or grouped around real UI/domain boundaries.
3. Write explicit update functions.
   Prefer named actions or local helper functions over scattered anonymous mutations.
4. Use selectors for reads.
   Subscribe components to the smallest stable state slice.
5. Test derived and subscription behavior.
   Verify consumers update when they should and stay quiet when unrelated state changes.

## Review Checklist

- Is Store used for client or reactive app state rather than duplicated server state?
- Are updates immutable and easy to trace?
- Do subscribers use selectors instead of whole-store reads?
- Are derived values computed in one place?
- Does framework adapter usage match the installed package and app framework?

## Avoid

- Using Store as a global dumping ground.
- Copying TanStack Query data into Store without a clear local-state reason.
- Mutating nested state in ways that bypass expected reactivity.
- Building a second event bus on top of store subscriptions.

## Verification

Use current TanStack Store docs for core APIs, derived state, and framework adapters. For server-state or collection-like data, compare against TanStack Query and TanStack DB before choosing Store.
