# Routing Structure

Use this guide when the core issue is route-tree shape rather than data loading or navigation.

Owns:
- route hierarchy, layout ownership, and pathless groups
- path params and file-route alignment
- router registration and end-to-end type inference setup

## Core Route Model

Use this section when the task is about the overall TanStack Router model rather
than one narrow subdomain such as search params or navigation.

Workflow:
1. Confirm the route tree matches URL and layout ownership.
2. Check that router setup supports the desired route model.
3. Keep route responsibilities clear before optimizing sub-features.

Do not use this section for search param details, navigation ergonomics, loader
cache behavior, or multi-layer Query/Start coordination.

## Path Params

Use this section when the task is about route params, route path segments, or
how file routes map to typed params.

Workflow:
1. Check the URL structure and param semantics.
2. Align route files or definitions with the intended param model.
3. Keep param typing inferred instead of manually duplicated.

Do not use this section for search params, navigation APIs, or route-level auth.

## Type Safety

Use this section when the task is specifically about type registration, Router
inference, or type performance and annotation problems.

Workflow:
1. Confirm the router is registered correctly.
2. Let inference flow before adding annotations.
3. Use narrowing helpers only where they materially improve precision.

Do not use this section for search param semantics, path structure decisions, or
cross-stack Start/Query typing concerns.

Verification: when exact APIs, filenames, or typing behavior matter, verify
against current TanStack Router docs or installed first-party Router Intent
skills.
