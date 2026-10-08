# TanStack Workflow

Use this reference for durable TypeScript workflows, replay, approvals, signals,
timers, scheduled runs, execution stores, and deployment adapters.

Workflow is an early Alpha project with public source documentation, currently
hidden from the public TanStack library catalog. Verify installed package
exports and published versions before using APIs described on `main`.

## Ownership Boundaries

- `@tanstack/workflow-core` owns workflow definitions, middleware, replay,
  durable primitives, and the low-level `RunStore`.
- `@tanstack/workflow-runtime` adds registrations, execution leases, schedules,
  timers, signal delivery, and bounded sweeps through `WorkflowExecutionStore`.
- Store adapters own persistence and schema migrations; host adapters connect
  provider entrypoints to runtime sweeps. The application owns ingress
  authorization, credentials, cron cadence, retention, and external effects.
- Framework hooks and devtools are planned; do not infer shipped `useWorkflow`
  bindings from framework template directories or marketing descriptions.

## Workflow

1. Choose core-only embedding or the runtime based on execution ownership.
   Use `RunStore` with `runWorkflow`; use `WorkflowExecutionStore` with
   `defineWorkflowRuntime`. In-memory stores are for tests and local demos.
2. Put external effects and nondeterministic reads inside `ctx.step` with stable
   IDs. Use recorded `ctx.now()` and `ctx.uuid()` values when replay must preserve
   time or identity. Replay must reach durable primitives in the same order.
3. Treat fresh effects as at-least-once. Use `stepCtx.id` for provider idempotency
   where supported, stable `runId` for starts, and stable signal/approval IDs
   for retryable deliveries. Leases do not guarantee exactly-once side effects.
4. Keep earlier workflow versions loadable for paused runs. Persisted workflow
   identifiers and version routing must still select compatible code after a
   deployment; the store does not serialize function closures.
5. Select a documented persistence adapter, such as Drizzle/Postgres or
   Cloudflare D1, and apply its package-owned migrations during setup/deploy.
   Do not assume a host sweep creates the database schema.
6. Wire the selected host adapter and bound sweep counts and duration to the
   host's execution budget. Current source includes Cloudflare, Railway,
   Netlify, and Vercel adapters; verify availability in the installed release.
   Sweeps wake due timers and schedules and recover expired execution leases.
7. Validate replay after a process exit, duplicate event delivery, pending
   approvals, timer wake-ups, and old-version resumption. Best-effort live event
   publishing is separate from the durable event log.

## Verification

Use the official source [installation guide](https://github.com/TanStack/workflow/blob/main/docs/installation.md),
[runtime model](https://github.com/TanStack/workflow/blob/main/docs/guide/runtime-model.md),
[persistence guide](https://github.com/TanStack/workflow/blob/main/docs/guide/persistence.md),
and [replay contract](https://github.com/TanStack/workflow/blob/main/docs/concepts/replay-and-resume.md).
Match these to the installed release before adding packages or changing an
existing persistence or deployment contract.
