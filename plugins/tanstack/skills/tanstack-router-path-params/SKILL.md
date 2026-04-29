---
name: tanstack-router-path-params
description: Review and implement TanStack Router path params, route path structure, and file-route alignment.
---

# TanStack Router Path Params

Use this skill when the task is about route params, route path segments, or how file routes map to typed params.

## Owns

- Path param naming and typing.
- Route path structure and param placement.
- File-route alignment for paramized routes.

## Does Not Own

- Search params: use `tanstack-router-search-params`.
- Navigation APIs: use `tanstack-router-navigation`.
- Route-level auth: use `tanstack-router-auth-and-guards`.

## Workflow

1. Check the URL structure and param semantics.
2. Align route files or definitions with the intended param model.
3. Keep param typing inferred instead of manually duplicated.

## Verification

Verify against current TanStack Router param conventions when exact filenames or route helpers matter.
