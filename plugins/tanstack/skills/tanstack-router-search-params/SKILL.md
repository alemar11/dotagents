---
name: tanstack-router-search-params
description: Review and implement validated TanStack Router search params, typed updates, and URL state boundaries.
---

# TanStack Router Search Params

Use this skill when the task is specifically about `validateSearch`, typed search state, or synchronizing URL query state with the app.

## Owns

- `validateSearch` design.
- Typed search param reads and updates.
- Search param defaults and URL-state boundaries.

## Does Not Own

- Path params: use `tanstack-router-path-params`.
- Route tree design: use `tanstack-router-core`.
- Query cache coordination across loaders and components: use `tanstack-integration`.

## Workflow

1. Identify which state belongs in search params.
2. Validate and type the search shape centrally.
3. Ensure updates use Router APIs instead of ad hoc string building.

## Verification

Verify against current TanStack Router search-param guidance when exact API behavior matters.
