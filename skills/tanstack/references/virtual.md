# TanStack Virtual

Use this reference when a task involves TanStack Virtual, `useVirtualizer`, large list or grid rendering, virtualized tables, dynamic row measurement, custom scroll containers, overscan tuning, or scroll performance.

## What to Optimize For

- Correct scroll container ownership.
- Stable item counts, keys, and estimates.
- Smooth rendering with measured dynamic sizes where needed.
- Overscan tuned to interaction needs instead of arbitrary large values.
- Integration with Table or custom layouts without breaking row identity.

## Workflow

1. Identify the virtualized axis and container.
   Confirm window vs element scrolling, vertical vs horizontal, list vs grid, and nested scroll behavior.
2. Define stable count, key, and estimate behavior.
   Use stable item keys and realistic `estimateSize` values before optimizing.
3. Choose measurement strategy.
   Use static estimates for fixed items and dynamic measurement only when item sizes vary materially.
4. Wire layout from virtual items.
   Keep total size, transforms, padding, and absolute positioning aligned with the selected pattern.
5. Tune and test.
   Check fast scroll, resize, data changes, prepend/append behavior, and accessibility of rendered content.

## Review Checklist

- Is `getScrollElement` correct and stable?
- Are item keys durable across sorting, filtering, and data refreshes?
- Does `estimateSize` match real content closely enough?
- Is dynamic measurement guarded for browser quirks and layout shifts?
- Does overscan balance smoothness with render cost?
- Are table integrations preserving row identity from TanStack Table?

## Avoid

- Virtualizing small lists where normal rendering is simpler and fast enough.
- Measuring every item when fixed or bounded estimates are sufficient.
- Using array indexes as durable keys for mutable or server-updated data.
- Nesting virtualizers without a clear scroll ownership model.
- Breaking semantic table/list markup without replacing accessibility behavior.

## Verification

Use current TanStack Virtual docs for React adapter APIs, scroll containers, dynamic measurement, lanes/grids, window virtualization, and integration patterns with TanStack Table.
