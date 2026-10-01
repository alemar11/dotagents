# TanStack Charts

Use this reference when a task involves `@tanstack/charts`, a framework adapter
such as `@tanstack/charts/react`, typed chart definitions, marks and channels,
D3 scales or transforms, responsive chart rendering, SVG or Canvas output,
chart interaction, accessibility, SSR, or migration from another chart
library.

TanStack Charts is an Alpha `0.x` product; APIs may break between minor releases.
Inspect the installed version and use its release-source documentation before
relying on version-sensitive APIs. The `latest` docs follow unreleased `main`,
not necessarily the published package.

## Ownership Boundaries

- TanStack Charts owns typed marks and channels, responsive ranges, guide
  layout, scene compilation, rendering, reconciliation, interaction, chart
  lifecycle, and framework adapters.
- The application owns data fetching, cleaning, business aggregation,
  filtering, persistence, and page-level controls.
- Start with exact `@tanstack/charts/scales/linear`, `/band`, `/point`, or
  `/ordinal` entries for common mappings; there is no aggregate `/scales`
  export. Use granular D3 modules for temporal, nonlinear, interpolated, or
  specialized semantics. Charts owns its bundled algorithms; declare a D3
  module and matching TypeScript package only when application source imports it.
- Keep Query, DB, Store, Router, or Start as the owner of application data and
  state. Pass chart-ready data into the chart boundary instead of turning the
  chart runtime into another state layer.

## Workflow

1. Inspect the installed package exports and framework peers.
   Current adapters use subpaths of the same `@tanstack/charts` package, such as
   `/react`, `/vue`, or `/octane`, rather than separate adapter packages.
   Confirm the renderer, framework, SSR boundary, and whether the target behavior
   exists in that published release; React Native support remains experimental.
2. Start from the analytical question and the shape of one observation.
   Choose marks and channels that express the comparison instead of selecting
   a canned chart type first.
3. Define scales and transforms explicitly.
   Keep row-local derivation in accessors, chart-specific transforms beside the
   definition, and reused or expensive transforms in framework memoization or
   the application's data layer.
4. Keep definitions stable.
   Define static charts outside component render. For changing inputs, keep one
   dynamic definition stable and pass the current input rather than rebuilding
   the definition on every render.
5. Choose the rendering surface deliberately.
   Prefer the default accessible SVG path. Use the explicit Canvas entry only
   when its rendering tradeoffs are justified, and verify SSR and hydration
   behavior for the selected adapter.
6. Verify accessibility and interaction.
   Supply a meaningful accessible label, preserve stable datum keys, test
   keyboard focus, and keep selection callbacks connected to application-owned
   actions and state.

## Default Rules

- Preserve source data types and let marks and channels infer datum and value
  types. Fix incorrect row types or accessors instead of casting definitions.
- Declare a scale for each materialized positional dimension. Use a factory
  for domains inferred from marks, a configured instance for fixed domains,
  and `null` only for an unused dimension; responsive pixel ranges stay chart-owned.
- Keep server-safe definitions behind `/universal` or exact capability entries
  when browser-host imports must remain unreachable.
- Use a fixed height or aspect ratio with responsive width unless the product
  layout requires fixed dimensions.
- Treat native tooltips as optional presentation. Keep permissions, business
  actions, and durable selection state outside the chart runtime.
- During migrations, preserve analytical meaning, interaction, accessibility,
  and rendering parity before removing the previous chart implementation.

## Avoid

- Hiding data preparation or business aggregation inside mark callbacks.
- Installing the D3 umbrella package when only granular modules are imported.
- Recreating chart definitions during every framework render.
- Assuming Canvas is the default or that it behaves like server-rendered SVG.
- Copying APIs from unreleased `main` documentation into a project pinned to an
  older published release.
- Treating an Alpha package as production-stable without an explicit risk
  decision and focused validation.

## Verification

Use the official [installation](https://tanstack.com/charts/latest/docs/installation),
[scales](https://tanstack.com/charts/latest/docs/concepts/scales-and-d3), and
[stability](https://tanstack.com/charts/latest/docs/stability) docs to locate the
matching release-source guidance. Verify exact exports, adapter behavior,
accessibility, rendering, and migration contracts against the installed version.
