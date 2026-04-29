---
name: tanstack-router-type-safety
description: Review TanStack Router type registration, inference flow, and unnecessary manual annotations.
---

# TanStack Router Type Safety

Use this skill when the task is specifically about type registration, Router inference, or type performance and annotation problems.

## Owns

- Router registration and global inference setup.
- Removing unnecessary manual annotations or casts.
- Keeping route-aware types precise and maintainable.

## Does Not Own

- Search param semantics: use `tanstack-router-search-params`.
- Path structure decisions: use `tanstack-router-path-params`.
- Cross-stack Start or Query typing concerns: use `tanstack-integration`.

## Workflow

1. Confirm the router is registered correctly.
2. Let inference flow before adding annotations.
3. Use narrowing helpers only where they materially improve precision.

## Verification

Verify against current Router typing guidance when exact registration or hook patterns matter.
