# pg_durable Runtime Guidance

Use this reference when the task involves durable SQL workflows, asynchronous
database jobs, retries, schedules, signals, or multi-step data pipelines that
should resume after a PostgreSQL restart.

`pg_durable` is a Microsoft-maintained PostgreSQL extension, not a core
PostgreSQL feature. It is currently in preview. Published packages target
PostgreSQL 17 and 18 as of 2026-08-11; verify the current extension release,
supported server majors, and provider availability before designing around it.

## 1) Use it for database-centered orchestration

Prefer `pg_durable` when most workflow steps read or write PostgreSQL and need
checkpointed retries, schedules, parallel branches, or external signals.
Keep a normal transaction or single SQL statement when the work is short and
atomic. Prefer a general-purpose orchestrator when most steps live in other
systems or need arbitrary application code.

## 2) Verify installation and runtime prerequisites

The extension requires a compatible build, a background worker loaded through
`shared_preload_libraries`, a configured worker database, and an administrator
who can install and grant it. Do not assume managed PostgreSQL providers expose
it merely because they support ordinary extensions.

Inspect the installed version before emitting version-sensitive DSL:

```sql
select extversion
from pg_extension
where extname = 'pg_durable';
```

Installation is an operator-owned change:

```sql
create extension pg_durable;
select df.grant_usage('app_role');
```

Keep both statements in reviewed deployment automation. Re-run the extension's
grant helper after upgrades when the release adds functions.

## 3) Treat `df.start()` as asynchronous submission

`df.start()` persists a workflow and returns an instance identifier; it does
not wait for completion.

```sql
select df.start(
  'select id from pending_documents limit 100' |=> 'batch'
  ~> 'update documents
       set queued_at = clock_timestamp()
       where id in (select id from $batch.*)',
  'queue-documents'
);
```

Persist or return the instance identifier when the caller needs later
correlation. Use the installed version's status, result, and instance-inspection
functions to observe completion before validating side effects.

## 4) Compose the smallest explicit workflow graph

Use the DSL operators only when their topology is intentional:

- `~>` sequences steps.
- `&` runs branches in parallel and waits for all of them.
- `|` races branches and keeps the first completion.
- `|=>` binds a result for a later `$name` reference.
- `?>` and `!>` branch conditionally.
- `@>` repeats a graph durably.

Prefer named built-ins such as `df.join()`, `df.if()`, or `df.loop()` when they
make a complex graph easier to review. Keep embedded SQL parameterized or built
from trusted static text; the DSL does not make string concatenation safe.

## 5) Design every step for replay

Workflow steps execute in separate sessions and transactions with durable
checkpoints between them. A failed in-progress step can run again, so a single
transaction does not span the whole graph.

- Make database writes idempotent with keys, unique constraints, upserts, or
  explicit processed markers.
- Give external API calls stable idempotency keys.
- Do not assume session-local state, temporary tables, advisory locks, or
  transaction settings survive into the next step.
- Record enough domain state to reconcile an uncertain external outcome.

Durable execution prevents completed checkpoints from being repeated; it does
not make non-idempotent side effects exactly once.

## 6) Preserve caller identity and least privilege

The runtime captures the submitting identity and executes SQL under that
identity, while its background worker needs elevated internal privileges to
coordinate users. Grant usage only to application roles that should be able to
submit workflows, and keep RLS and ordinary object grants authoritative.

Do not enable superuser-submitted workflows for convenience in a multi-tenant
or partially trusted deployment. Review HTTP egress allowlists and treat data
returned by workflow inspection views as tenant-scoped operational data.

## 7) Operate workflows as durable application state

Include the extension schemas and workflow state in backup, restore, HA, and
upgrade planning. Drain or cancel active instances before an extension upgrade
when the installed release does not guarantee state portability. After a
failover, verify that the worker resumed and reconcile workflows whose current
step had an external side effect.

Monitor backlog, age, retries, failed work, worker health, and result-retention
growth. Use schedules and signals for durable waits rather than holding a
database connection or transaction open.

## Official References

- Project and version support: https://github.com/microsoft/pg_durable
- Project documentation: https://microsoft.github.io/pg_durable/
- Azure HorizonDB durable functions: https://learn.microsoft.com/en-us/azure/horizondb/development/durable-functions
