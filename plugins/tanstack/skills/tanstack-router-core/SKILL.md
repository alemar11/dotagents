---
name: tanstack-router-core
description: Review or design the overall TanStack Router route tree, route ownership, and core runtime model for React apps.
---

# TanStack Router Core

Use this skill when the task is about the overall TanStack Router model rather than one narrow subdomain such as search params or navigation.

## Owns

- Route tree shape and route ownership.
- Core router setup and mental model.
- Choosing route boundaries, layouts, and pathless group structure.

## Does Not Own

- Search param details: use `tanstack-router-search-params`.
- Navigation ergonomics: use `tanstack-router-navigation`.
- Loader cache behavior: use `tanstack-router-data-loading`.
- Multi-layer Query or Start coordination: use `tanstack-integration`.

## Workflow

1. Confirm the route tree matches URL and layout ownership.
2. Check that router setup supports the desired route model.
3. Keep route responsibilities clear before optimizing sub-features.

## Verification

When exact APIs or file conventions matter, verify against current TanStack Router docs or installed first-party Router Intent skills.
