---
name: tanstack
description: Review or build TanStack apps across Query, Router, Start, Form, Table, Charts, Virtual, Store, DB, AI, CLI, and integrations.
---

# TanStack

## Goal

Use this skill to make TanStack decisions from the app's actual installed packages and current official TanStack guidance, while keeping product-specific detail in focused reference files.

## Quick Workflow

1. Identify the TanStack product or cross-stack boundary in the user request.
2. Inspect the target repo before recommending a pattern:
   - package manager and installed `@tanstack/*` packages
   - framework boundaries such as Router, Start, Query, or Vite setup
   - local route, cache, form, table, state, or CLI conventions
3. Read [references/README.md](references/README.md) to pick the smallest useful reference.
4. Open only the product reference needed for the task, then open a focused Router, Start, or CLI reference only when the issue has narrowed to that subdomain.
5. Verify exact APIs against installed package versions or current TanStack-owned docs before making version-sensitive claims.
6. Prefer existing app conventions and TanStack ecosystem primitives over hand-rolled alternatives when they fit the problem.

## Product Routing

- Query cache keys, `queryOptions`, invalidation, mutations, SSR data: [references/query.md](references/query.md)
- Router route trees, search params, loaders, auth guards, navigation: [references/router.md](references/router.md)
- Start server functions, middleware, SSR, env boundaries, deployment: [references/start.md](references/start.md)
- Query + Router + Start ownership, loader prefetch, hydration: [references/integration.md](references/integration.md)
- CLI scaffolding, add-ons, docs lookup, ecosystem metadata: [references/cli.md](references/cli.md)
- Forms, typed fields, arrays, validation, React Hook Form migration: [references/form.md](references/form.md)
- Tables, columns, row models, sorting, filtering, pagination: [references/table.md](references/table.md)
- Charts, typed marks and channels, D3 scales, SVG or Canvas rendering, accessibility: [references/charts.md](references/charts.md)
- Virtual lists, grids, dynamic measurement, overscan: [references/virtual.md](references/virtual.md)
- Store, DB, AI, Config, Devtools, Pacer, Ranger: use the matching product reference from [references/README.md](references/README.md).

## Default Rules

- Treat TanStack Query as server-state ownership, not generic client state.
- For Query + Router, share query factories across loaders, prefetch paths, and component reads.
- For Start, check server/client execution boundaries before moving code, imports, or environment access.
- For Router, prefer typed route APIs, validated search params, and route-owned loaders over ad hoc URL parsing.
- For Form, preserve behavior during migrations before polishing API shape.
- For CLI workflows, discover capabilities from the installed CLI or machine-readable docs before guessing add-ons or flags.

## References

- Start with [references/README.md](references/README.md) for the full product and focused-reference map.
- Read product references such as [references/query.md](references/query.md), [references/router.md](references/router.md), or [references/start.md](references/start.md) only when that product is relevant.
- Read focused Router, Start, or CLI references only after the task has narrowed to that concern.
