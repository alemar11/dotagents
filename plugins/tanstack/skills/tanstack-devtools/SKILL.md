---
name: tanstack-devtools
description: Review and implement TanStack Devtools usage for centralized devtools panels, library plugins, framework integration, and production-safe diagnostics.
---

# TanStack Devtools

Use this skill when a task involves TanStack Devtools, devtools panels, library-specific devtools plugins, local debugging UI, or diagnostics for TanStack Query, Router, Form, DB, or related packages.

## What to Optimize For

- Devtools that are easy to enable locally and safe to exclude or gate in production.
- Plugin setup that matches the TanStack libraries actually installed in the app.
- Diagnostics that help inspect state without changing runtime behavior.
- Framework integration that does not break SSR, hydration, or bundle boundaries.

## Workflow

1. Identify the framework and installed TanStack libraries.
   Match devtools plugins to actual package usage.
2. Decide the exposure model.
   Gate devtools by environment, debug flag, or local-only entrypoint as appropriate.
3. Wire devtools near the owning providers.
   Place Query, Router, Form, DB, or shared devtools components where they can read the correct context.
4. Check SSR and production builds.
   Avoid browser-only devtools code in server-only modules or production-critical bundles.
5. Verify diagnostics manually.
   Confirm panels show the expected state for the target library.

## Review Checklist

- Are devtools imported from current package names?
- Is production exposure intentionally gated?
- Are providers and devtools mounted in the same app/router/query context?
- Does setup avoid SSR or hydration errors?
- Are debug-only dependencies kept out of critical runtime paths where possible?

## Avoid

- Enabling devtools globally in production by accident.
- Installing devtools plugins for libraries the app does not use.
- Mounting devtools outside the provider context they need to inspect.
- Treating devtools as a substitute for tests or runtime error handling.

## Verification

Verify exact package names, plugin APIs, and framework setup against current TanStack Devtools docs and the target app's installed TanStack packages.
