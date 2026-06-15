# Framework And Execution

Use this guide when the problem is about how Start works as a framework, or where code should execute.

Owns:
- framework-level Start setup and high-level structure
- isomorphic execution boundaries and shared-module safety
- deciding whether a concern belongs in Start at all versus plain Router

## React Start Framework

Use this section when the task is broadly about `@tanstack/react-start` as a
React framework and is not yet narrowed to server functions, middleware, or
deployment.

Workflow:
1. Confirm the task is really about React Start as the framework surface.
2. Place the concern into the right Start subdomain before making code-level
   recommendations.
3. Keep React-specific Start advice separate from lower-level core runtime
   concerns.

## Start Core

Use this section when the task is about the Start core runtime model and does
not fit a narrower React-specific or server-only subdomain.

Workflow:
1. Confirm the task is about Start core behavior rather than one narrow feature.
2. Keep advice centered on runtime model and framework invariants.
3. Move to a narrower section once the problem becomes specific.

## Execution Model

Use this section when the task is specifically about where code runs, which
modules are safe to share, or how Start's isomorphic execution model affects
design.

Workflow:
1. Identify where the code actually executes.
2. Move server-only behavior behind explicit server boundaries.
3. Keep shared modules safe for both environments.

Verification: verify against current TanStack React Start, Start core, or
execution-model guidance when exact APIs or runtime boundaries matter.
