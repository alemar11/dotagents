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
1. Decide what route config must stay eager.
2. Move heavy route UI to lazy boundaries where it improves startup or bundle
   shape.
3. Avoid scattering critical route identity across lazy files.

Do not use this section for general route tree design, build plugin wiring, or
SSR tradeoffs.

Verification: verify against current TanStack Router plugin and lazy-route docs
when exact setup or generated-file behavior matters.
