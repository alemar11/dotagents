# Plugin And Splitting

Use this guide when the issue is about build-time Router tooling or route-splitting structure.

Owns:
- router plugin wiring and generated-route assumptions
- lazy route files and code-splitting boundaries
- keeping build-time concerns separate from route semantics

## Router Plugin

Use this section when the task is specifically about the TanStack Router plugin
layer, generated route artifacts, or bundler wiring.

Workflow:
1. Identify the build tool and current Router plugin setup.
2. Check that generated routes and route registration assumptions line up.
3. Keep plugin advice scoped to Router build wiring only.

Do not use this section for route tree design, lazy route strategy, or Start
framework plugin concerns.

## Code Splitting

Use this section when the task is specifically about lazy route files,
code-splitting boundaries, or where route config should live.

Workflow:
1. Check whether file-based routes already use automatic code splitting
   through Start or the supported Router bundler plugin.
2. Prefer `autoCodeSplitting` when supported. The standalone
   `@tanstack/router-cli` generator cannot provide this bundler transform.
3. Use `.lazy.tsx` / `createLazyFileRoute` for manual component boundaries when
   automatic splitting is unavailable. Keep route matching, validation, guards,
   and other critical config eager; the root route cannot be split this way.

Do not use this section for general route tree design, build plugin wiring, or
SSR tradeoffs.

Verification: verify against current TanStack Router plugin and lazy-route docs
when exact setup or generated-file behavior matters.

Source: [Router code splitting](https://tanstack.com/router/latest/docs/guide/code-splitting).
