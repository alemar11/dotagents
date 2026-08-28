# pg_cron Runtime Guidance

Use this reference when the task involves periodic SQL, database maintenance,
retention, rollups, or other schedules that should run inside PostgreSQL.

`pg_cron` is an extension, not a core PostgreSQL feature. Verify the installed
extension version, target provider support, and access to server configuration
before designing around it. Managed services may expose `pg_cron` while
retaining control of its preload and cluster settings.

## 1) Use it for small database-local schedules

Prefer `pg_cron` for bounded SQL statements or stored procedures whose work and
observability belong in PostgreSQL. Prefer an application scheduler or job
queue when work depends mainly on application code, external services,
elastic workers, rich retry policies, or deployment coordination. Prefer
`pg_durable` when a database-centered workflow needs durable multi-step
checkpoints, signals, or replay-aware retries rather than a recurring trigger.

## 2) Verify the cluster setup before scheduling

The extension uses a background worker loaded through
`shared_preload_libraries`, which normally requires an operator-controlled
restart. It can be installed in only one database per cluster; use
`cron.schedule_in_database()` for jobs targeting other databases. It does not
launch jobs while the server is in hot standby and starts automatically after
promotion.

Inspect availability and configuration before proposing installation or jobs:

```sql
select name, default_version, installed_version
from pg_available_extensions
where name = 'pg_cron';

select name, setting, context
from pg_settings
where name like 'cron.%'
   or name = 'shared_preload_libraries'
order by name;
```

After DDL approval, install it through reviewed deployment automation in the
database configured by `cron.database_name`:

```sql
create extension pg_cron;

grant usage on schema cron to maintenance_scheduler;

select extversion
from pg_extension
where extname = 'pg_cron';
```

Do not guess a self-hosted installation procedure for a managed service. Use
the provider's supported extension and configuration flow.

## 3) Make schedule ownership explicit

Use a stable job name, an explicit schedule, and a small stored procedure or
static parameter-free command. Confirm `cron.timezone`; do not infer it from an
application or session timezone.

```sql
select cron.schedule(
  'prune-rendered-page-cache',
  '15 * * * *',
  $$call prune_rendered_page_cache(1000)$$
);
```

Use `cron.schedule_in_database()` when the job targets a database other than
the metadata database. Manage changes with `cron.alter_job()` and removal with
`cron.unschedule()` instead of editing `cron.job` directly. In repeatable
migrations, inspect the stable job name before scheduling so a retry does not
create a duplicate job.

## 4) Preserve least privilege and connection safety

Jobs execute with the permissions of the user that scheduled them. Grant
`USAGE` on the `cron` schema only to roles that should schedule work, then rely
on ordinary table, function, database, and RLS privileges for the job body.
Do not schedule as a superuser merely to bypass missing grants, and do not put
secrets in stored command text. Ordinary roles can see and modify only their
own jobs through the extension's row-level policy, so keep scheduler-role
ownership stable and deliberate.

By default, `pg_cron` opens local libpq connections, so its job roles need a
valid local authentication path. Background-worker execution is an alternative
when the deployment supports `cron.use_background_workers`; its concurrency is
bounded by `max_worker_processes`. Diagnose connection failures through the
configured authentication mode rather than weakening host authentication
globally.

## 5) Design for overlap, failure, and bounded work

`pg_cron` runs at most one instance of a specific job at a time. If the next
run becomes due while the current run is active, it is queued and begins after
the current run finishes. Different jobs can still overlap, even when they
touch the same data.

- Keep each job transactional, idempotent, and safe to run after partial
  external progress.
- Bound batches and execution time so a slow run does not create an unbounded
  queue of later runs.
- Use a database invariant or advisory lock when different job names must share
  one singleton critical section.
- Treat the next scheduled run as recurrence, not as an automatic retry policy.
  Put deliberate retry state in the job procedure, or use a durable workflow or
  application queue when retry timing and exhaustion are business behavior.
- Do not claim exactly-once side effects; reconcile any external action whose
  outcome can become uncertain.

## 6) Monitor runs and retain history deliberately

Inspect configured jobs in `cron.job` and recent executions in
`cron.job_run_details` when `cron.log_run` is enabled:

```sql
select jobid, jobname, schedule, database, username, active
from cron.job
order by jobid;

select jobid, status, return_message, start_time, end_time
from cron.job_run_details
order by start_time desc
limit 100;
```

Alert on failed runs, jobs that have not succeeded within their expected
window, and growing execution duration. Run history is not cleaned
automatically, so apply a reviewed retention policy or disable run logging only
when another observability path replaces it. After failover, verify that jobs
resumed on the promoted primary and reconcile any interrupted run.

## Official References

- Project and operational guidance: https://github.com/citusdata/pg_cron
- PostgreSQL background workers: https://www.postgresql.org/docs/current/bgworker.html
- PostgreSQL client authentication: https://www.postgresql.org/docs/current/client-authentication.html
