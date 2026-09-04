# pgmq Runtime Guidance

Use this reference when the task involves database-backed message queues,
visibility timeouts, asynchronous workers, retries, or enqueueing work in the
same transaction as application data.

`pgmq` is an extension, not a core PostgreSQL feature. Upstream currently
lists PostgreSQL 14 through 18 as supported. Verify the installed extension
version, target server major, provider availability, and exact API before
designing around version-sensitive features such as FIFO queues, topic routing,
partitioning, or long polling.

## 1) Use it for database-local asynchronous work

Prefer `pgmq` when producers, queue state, and most durable application state
already live in one PostgreSQL database. It is especially useful when an
application write and its queue message must commit atomically without a
separate transactional-outbox relay.

Prefer an external broker when the queue needs an independent failure domain,
very high fan-out or throughput, cross-database coordination, broker-native
stream replay, or operational isolation from the primary database. Prefer
`pg_cron` for periodic SQL and `pg_durable` for checkpointed multi-step SQL
workflows; neither is a substitute for a work queue with competing consumers.

`pgmq` provides SQL objects and does not run application jobs itself. Consumers
still need an application worker or another execution environment that polls,
processes, and acknowledges messages.

## 2) Verify availability before installation

Inspect both available and installed versions before proposing installation or
version-specific SQL:

```sql
select name, default_version, installed_version
from pg_available_extensions
where name = 'pgmq';

select extversion
from pg_extension
where extname = 'pgmq';
```

After DDL approval, prefer the versioned extension installation supported by
the target operator or managed provider:

```sql
create extension pgmq;
```

Do not assume that a managed PostgreSQL service exposes an extension merely
because upstream supports that server major. Follow the provider's supported
enablement and access model. Upstream also publishes a SQL-only installation
for restricted environments, but an unversioned SQL-only install gives up
PostgreSQL extension version tracking and supported `ALTER EXTENSION` upgrades.
Treat that as a deliberate deployment choice, not an interchangeable fallback.

## 3) Keep queue lifecycle in deployment automation

Create queues with stable lower-kebab or snake-case names accepted by the
installed version, and keep queue creation, grants, and removal in reviewed
deployment automation:

```sql
select pgmq.create('document_jobs');
```

Each queue owns backing tables in the `pgmq` schema. Normal queues use logged
tables and participate in PostgreSQL durability, backup, and replication.
Use unlogged queues only for explicitly disposable work: they are not replicated
to standbys and can be truncated after a crash. Use partitioned queues only
after selecting retention and maintenance rules for the installed version.

Do not read, write, rename, or drop the backing `pgmq.q_*` and `pgmq.a_*`
tables directly. Use the extension API so upgrades and metadata stay coherent.
Dropping a queue or the extension can destroy queued and archived messages, so
resolve the exact target and retention requirement before destructive DDL.

## 4) Use read, process, acknowledge

Producers send JSON messages and may delay their initial visibility:

```sql
select pgmq.send(
  queue_name => 'document_jobs',
  msg        => jsonb_build_object(
    'job_id', 'job-018f',
    'document_id', 42
  )
);
```

Consumers should claim a bounded batch with `pgmq.read()`, commit the short
database transaction, process each message, and delete or archive it only after
successful processing:

```sql
select *
from pgmq.read(
  queue_name => 'document_jobs',
  vt         => 60,
  qty        => 20
);

select pgmq.delete('document_jobs', 123);
-- Or retain completed work for audit or replay:
select pgmq.archive('document_jobs', 123);
```

Choose a visibility timeout longer than normal processing time but short enough
to recover promptly from a dead worker. For work whose duration varies, renew
the timeout with the installed version's `set_vt` API while the worker still
owns the message. Bound batch size, worker concurrency, polling rate, statement
timeouts, and connection-pool use so consumers do not starve the application.

Do not hold a database transaction open while calling slow external services.
Queue functions make queue state transactional, but they cannot make an
external side effect atomic with PostgreSQL.

## 5) Design for redelivery, not exactly-once processing

The extension prevents another consumer from reading a claimed message during
its visibility timeout. If the worker crashes, times out, or loses the result of
an acknowledgement, the message can become visible and run again. Treat normal
`read()` consumption as at-least-once processing across failures.

- Give every logical operation a stable application idempotency key.
- Enforce deduplication with a unique constraint or durable processed marker in
  domain tables, not only an in-memory worker cache.
- Make delete or archive conditional on confirmed processing success.
- Use `read_ct` plus explicit retry policy to identify poison messages; move
  exhausted work to a dedicated dead-letter queue or archive it with enough
  failure context to diagnose and replay safely.
- Reconcile external calls whose outcome is uncertain after a timeout.

Avoid `pgmq.pop()` when work must survive consumer failure. It deletes as it
reads and therefore provides at-most-once delivery if the worker fails before
processing finishes.

## 6) Make ordering and routing requirements explicit

Do not infer strict processing order from message identifiers or ordinary queue
reads. Concurrent consumers, retries, and different job durations can reorder
completion. When ordering is a domain requirement, verify that the installed
version supports FIFO message groups and design the grouping key deliberately.

Likewise, use topic routing only when the installed version supports the exact
binding and wildcard behavior required. For simple competing-consumer work, one
plain queue is easier to operate than a topic topology. For broad event fan-out
or long-lived replayable streams, evaluate a broker designed for those semantics.

## 7) Preserve least privilege

Use separate producer, consumer, and queue-administrator roles when their
responsibilities differ. Application roles normally need only schema usage and
execution rights on the small set of queue functions they call; they should not
own the extension or create and drop queues at runtime.

Revoke broad default access before granting deliberate permissions. Keep the
`pgmq` schema out of an unauthenticated data API unless a provider-supported
wrapper, row-level policy, and tenant authorization model have been reviewed.
Queue payloads are durable database data, so do not place credentials or
unnecessary sensitive content in them.

## 8) Operate queue tables as production data

Monitor queue length, oldest visible message age, enqueue-to-completion latency,
redelivery counts, poison-message count, worker errors, and consumer capacity.
Use the installed version's `pgmq.metrics()` or `pgmq.metrics_all()` functions
where available, and alert on age as well as depth: a small stuck queue can be
more serious than a large healthy one.

Set explicit retention for archived messages and test cleanup under load.
Queue and archive tables need ordinary autovacuum, storage, backup, restore,
replication, and failover planning. Validate that consumers reconnect only to a
writable primary after failover, then reconcile messages whose processing or
acknowledgement was interrupted.

Before an upgrade, read every intermediate extension upgrade note, test with a
copy of representative queue data, pause or drain consumers when required, and
verify the installed version plus a send/read/acknowledge smoke path afterward.

## Official References

- Project, supported majors, and quick start: https://github.com/pgmq/pgmq
- Installation and upgrade tradeoffs: https://github.com/pgmq/pgmq/blob/main/INSTALLATION.md
- Versioned documentation and SQL API: https://pgmq.github.io/pgmq/latest/
- Supabase provider integration: https://supabase.com/docs/guides/queues
