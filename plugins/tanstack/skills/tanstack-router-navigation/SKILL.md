---
name: tanstack-router-navigation
description: Review and implement TanStack Router navigation patterns, typed links, and route-aware hook usage.
---

# TanStack Router Navigation

Use this skill when the task is specifically about `Link`, `navigate`, `useNavigate`, or route-aware hook narrowing.

## Owns

- `Link` and imperative navigation usage.
- `from` narrowing for route-aware hooks and links.
- Safe typed navigation patterns.

## Does Not Own

- Search state design: use `tanstack-router-search-params`.
- Loader strategy: use `tanstack-router-data-loading`.
- Auth redirects implemented in route guards: use `tanstack-router-auth-and-guards`.

## Workflow

1. Check whether navigation is declarative or imperative for the use case.
2. Tighten type precision with route-aware narrowing where appropriate.
3. Avoid stringly-typed URL construction when Router APIs can express the same intent.

## Verification

Verify against current TanStack Router navigation APIs when exact call shapes matter.
