---
name: tanstack
description: Build, debug, review, or migrate TanStack integrations and package APIs.
---

# TanStack

Ground recommendations in the app's installed `@tanstack/*` versions and local
framework conventions. Verify version-sensitive APIs against installed code or
current TanStack-owned documentation.

Use product-reference workflows as decision guides for the affected concern.
A small fix needs only relevant steps and checks; do not redesign surrounding
state, routing, or configuration merely to follow the whole reference.

Read the product reference for the affected boundary:

- Cache, queries, mutations: [Query](references/query.md).
- Routes, search parameters, loaders: [Router](references/router.md).
- Server functions, middleware, SSR: [Start](references/start.md).
- Shared loading, prefetch, hydration: [integration](references/integration.md).
- Forms and validation: [Form](references/form.md).
- Columns and row models: [Table](references/table.md).
- Virtual lists or grids: [Virtual](references/virtual.md).
- Scaffolding and add-ons: [CLI](references/cli.md).
- Other products or narrower concerns: [reference map](references/README.md).

Load focused subreferences only for the relevant concern. Preserve application
behavior during migrations and check server/client ownership before moving
imports, code, or environment access.
