# TanStack Charts

Use this reference when a task involves `@tanstack/charts`, a framework adapter
such as `@tanstack/react-charts`, typed chart definitions, marks and channels,
D3 scales or transforms, responsive chart rendering, SVG or Canvas output,
chart interaction, accessibility, SSR, or migration from another chart
library.

TanStack Charts is a pre-alpha `0.x` product. Inspect the installed package
versions and use the documentation for the published release before relying on
version-sensitive APIs; the repository's `main` documentation may describe
unreleased behavior.

## Ownership Boundaries

- TanStack Charts owns typed marks and channels, responsive ranges, guide
  layout, scene compilation, rendering, reconciliation, interaction, chart
  lifecycle, and framework adapters.
- The application owns data fetching, cleaning, business aggregation,
  filtering, persistence, and page-level controls.
- Use granular D3 modules for scale semantics, domains, binning, stacking,
  grouping, interpolation, and spatial algorithms. Declare every directly
  imported `d3-*` module and matching TypeScript package as an application
  dependency.
- Keep Query, DB, Store, Router, or Start as the owner of application data and
  state. Pass chart-ready data into the chart boundary instead of turning the
  chart runtime into another state layer.

## Workflow

1. Inspect the installed core and framework-adapter versions.
   Confirm the intended renderer, framework, SSR boundary, and whether the
   target behavior exists in that published release.
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
- Keep scale domains and semantics explicit when the visualization depends on
  them; responsive pixel ranges remain chart-owned.
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
- Treating a pre-alpha package as production-stable without an explicit risk
  decision and focused validation.

## Verification

Use the current TanStack Charts overview, framework adapter, scales and D3,
accessibility, rendering, migration, and release-source documentation. Verify
the exact package exports and adapter behavior against the installed version
before finalizing implementation guidance.
