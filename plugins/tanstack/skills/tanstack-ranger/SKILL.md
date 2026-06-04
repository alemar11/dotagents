---
name: tanstack-ranger
description: Review and implement TanStack Ranger usage for headless single-range and multi-range sliders, custom steps, interpolation, drag behavior, and accessible UI wiring.
---

# TanStack Ranger

Use this skill when a task involves TanStack Ranger, headless range sliders, multi-range controls, custom steps, logarithmic or custom interpolation, drag update behavior, or slider accessibility.

TanStack Ranger is a headless utility. It does not own visual styling; the app must provide accessible UI, keyboard behavior, labels, and layout.

## What to Optimize For

- Controlled range state with clear min, max, step, and interpolation behavior.
- Accessible slider semantics and keyboard interactions.
- Stable drag behavior that does not fight app state updates.
- UI styling that reflects thumbs, tracks, selected ranges, and disabled states without hiding state logic.

## Workflow

1. Define the range model.
   Confirm single vs multi-thumb behavior, value type, min/max, step, and constraints between thumbs.
2. Choose interpolation and update timing.
   Use default, custom, or logarithmic interpolation only when product requirements justify it.
3. Wire headless state to UI.
   Keep Ranger-derived props and app event handlers clear at the thumb/track boundary.
4. Add accessibility behavior.
   Ensure labels, keyboard support, focus, ARIA values, and disabled state are correct.
5. Test pointer and keyboard flows.
   Cover drag, click, keyboard increments, constraints, and controlled value updates.

## Review Checklist

- Are min, max, step, and thumb constraints explicit?
- Does multi-range behavior prevent invalid thumb ordering when needed?
- Are pointer and keyboard updates consistent?
- Are ARIA labels and values present for each thumb?
- Does custom interpolation preserve predictable value display and form submission?

## Avoid

- Treating Ranger as a prebuilt visual component.
- Encoding range math separately from Ranger state without a good reason.
- Forgetting keyboard and screen-reader behavior because pointer dragging works.
- Recomputing expensive scale/interpolation data on every render when stable inputs exist.

## Verification

Use current TanStack Ranger docs for React adapter APIs, custom steps, custom styles, logarithmic interpolation, and update-on-drag behavior.
