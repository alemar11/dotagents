# Server Components And Migrations

Use this guide when the task is specifically about experimental server components or moving from Next.js assumptions into Start.

Owns:
- Start server component setup and caveats
- Next.js App Router migration sequencing
- avoiding leaked `use server`, `use client`, or server-component mental models

## Server Components

Use this section when the task is specifically about TanStack Start server
components, their setup, or their experimental constraints.

Workflow:
1. Confirm that the app is intentionally using the server component feature set.
2. Check setup, rendering boundaries, and client/server composition rules.
3. Keep recommendations conservative because the feature is experimental.

Do not use this section for general server functions, whole-app framework setup
unrelated to server components, or broad Query hydration design.

## Migrate From Next.js

Use this section when the task is specifically about moving from Next.js App
Router conventions to TanStack Start.

Workflow:
1. Identify which Next.js assumptions are still present.
2. Map routes, server actions, middleware, and config to Start equivalents.
3. Prioritize the execution-model shift before code cleanup.

Do not use this section for general Start framework design without migration
context, detailed server function implementation after the migration boundary is
clear, or Query integration redesign after migration.

Verification: verify against current TanStack Start server-component or
migration guidance before treating any pattern as stable.
