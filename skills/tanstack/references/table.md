# TanStack Table

Use this reference when a task involves `@tanstack/react-table`, headless table state, column definitions, row models, sorting, filtering, pagination, row selection, grouping, expansion, pinning, column visibility, or integrating tables with TanStack Virtual.

The current official `latest` docs target TanStack Table v9. Inspect the
installed major before using examples: v9 registers only the features and row
models a table needs, while v8 applications should keep their existing API
shape unless the task explicitly includes migration.

## What to Optimize For

- Stable column definitions, accessors, and row IDs.
- Explicit client-side vs server-side ownership for sorting, filtering, pagination, and grouping.
- Controlled table state where the app needs URL, persistence, or server synchronization.
- Accessible table markup and predictable keyboard/focus behavior where the app renders the UI.
- Virtualization that preserves row identity and measurement correctness.

## Workflow

1. Identify the data ownership model.
   Decide which features are client-side row models and which are server-driven.
2. Define columns carefully.
   Use stable accessors, IDs, headers, cells, and metadata; avoid recreating column definitions unnecessarily.
3. Configure features and row models deliberately.
   In v9, register only the feature plugins and row-model factories the table
   uses. In v8, preserve the installed API rather than translating examples
   mechanically from v9.
4. Control state where needed.
   Sync table state to URL, server params, or app state only when product behavior requires it.
5. Verify rendering and accessibility.
   Ensure headers, cells, loading/empty states, selection controls, and virtualized rows remain coherent.

## Review Checklist

- Are column IDs stable, especially for computed or display columns?
- Is row identity stable through sorting, filtering, pagination, and virtualization?
- Are server-side features marked and wired consistently?
- Are expensive row models avoided when data is already server-shaped?
- Does table state sync avoid loops between URL, server params, and local controls?

## Avoid

- Treating TanStack Table as a styled component library.
- Mixing client-side and server-side sorting/filtering without clear ownership.
- Recreating data or columns every render in ways that reset table state.
- Using array indexes as durable row IDs for mutable data.
- Adding virtualization before verifying table feature state and row identity.

## Verification

Use current TanStack Table docs and, when available for the installed package,
its first-party Intent skills for feature registration, column definitions,
row models, feature state, controlled state, migration, and framework adapter
APIs. For large tables, also verify TanStack Virtual integration guidance.
