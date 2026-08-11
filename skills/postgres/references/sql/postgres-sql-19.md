# PostgreSQL 19 SQL Additions — Preview

> **Volatile development snapshot:** This guide was verified against
> **PostgreSQL 19 Beta 2 on 2026-08-11**. Recheck the current release stage,
> syntax, and behavior against the exact target build; do not use this guide
> alone to approve a production migration.

Use the [official PostgreSQL 19 documentation](https://www.postgresql.org/docs/19/)
and [Beta 2 announcement](https://www.postgresql.org/about/news/postgresql-19-beta-2-released-3350/)
as the current source of truth.

## Contents

- [SQL/PGQ property graphs (preview)](#sqlpgq-property-graphs-preview)
- [`ON CONFLICT DO SELECT` with `RETURNING` (preview)](#on-conflict-do-select-with-returning-preview)
- [`FOR PORTION OF` temporal DML (preview)](#for-portion-of-temporal-dml-preview)
- [`GROUP BY ALL` (preview)](#group-by-all-preview)
- [Window `IGNORE NULLS` (preview)](#window-ignore-nulls-preview)
- [`COPY` JSON and field-level error handling (preview)](#copy-json-and-field-level-error-handling-preview)
- [Core `REPACK` (preview)](#core-repack-preview)
- [Merge and split partitions (preview)](#merge-and-split-partitions-preview)
- [`WAIT FOR LSN` (preview)](#wait-for-lsn-preview)
- [`EXPLAIN (ANALYZE, IO)` (preview)](#explain-analyze-io-preview)
- [Publication sequences and exclusions (preview)](#publication-sequences-and-exclusions-preview)
- [Global-object DDL reconstruction (preview)](#global-object-ddl-reconstruction-preview)
- [Online data checksums (preview)](#online-data-checksums-preview)
- [AIO workers and parallel autovacuum (preview)](#aio-workers-and-parallel-autovacuum-preview)
- [New operational statistics views (preview)](#new-operational-statistics-views-preview)
- [Unsigned `oid8` values (preview)](#unsigned-oid8-values-preview)
- [Changed JIT, lock, and TOAST defaults (preview)](#changed-jit-lock-and-toast-defaults-preview)
- [Foreign-data changes](postgres-fdw-versions.md#postgresql-19-preview)

## SQL/PGQ property graphs (preview)

**Use when:** the data remains relational but fixed graph-pattern matching is a
clearer read model than a chain of joins or a recursive CTE.

```sql
create property graph social_graph
  vertex tables (
    people key (id)
      label person properties (id, display_name as name, active)
  )
  edge tables (
    friendships key (id)
      source key (from_id) references people (id)
      destination key (to_id) references people (id)
      label follows properties (created_at)
  );

select *
from graph_table (
  social_graph
  match (src is person)
        -[rel is follows]->
        (dst is person where dst.active = true)
  columns (
    src.id as source_id,
    dst.id as destination_id,
    rel.created_at as followed_at
  )
);
```

`CREATE PROPERTY GRAPH` records a logical graph over tables, views, or foreign
tables; it does not copy or materialize the data. Vertices and edges are rows,
labels define element kinds, and properties expose typed expressions.
`GRAPH_TABLE` returns a normal relational result that can be joined and filtered.

This is SQL/PGQ, not Cypher. Mutations still target the base relations. The
caller needs privileges on both the graph and its base relations, and labels
with the same name must expose compatible property names and types. Use only
the pattern forms documented for the exact PostgreSQL 19 build.

**Fallback through 18:** use ordinary joins for fixed hops and recursive CTEs
for variable-depth traversal, carrying visited paths when cycle prevention is
required.

[Official property-graph DDL](https://www.postgresql.org/docs/19/sql-create-property-graph.html)
and [graph-query syntax](https://www.postgresql.org/docs/19/queries-graph.html)

## `ON CONFLICT DO SELECT` with `RETURNING` (preview)

**Use when:** implementing atomic get-or-create without performing a dummy
update on the conflicting row.

```sql
insert into users (email, display_name)
values ($1, $2)
on conflict (email) do select for key share
returning user_id, email, display_name;
```

The statement returns either the inserted row or the existing conflicting row.
`DO SELECT` requires both an explicit conflict target and `RETURNING`; its
optional locking clause is `FOR UPDATE`, `FOR NO KEY UPDATE`, `FOR SHARE`, or
`FOR KEY SHARE`. A `WHERE` condition can suppress returned rows after conflict
detection.

Only non-deferrable unique constraints and unique indexes can arbitrate this
path; exclusion constraints are unsupported. Account for `SELECT` privilege,
and additional update privilege when a row-locking form is used.

**Fallback through 18:** use `INSERT ... ON CONFLICT DO NOTHING RETURNING`, then
`SELECT` the existing row and retry if a concurrent uncommitted insert made the
same-statement snapshot return no row. Do not use a no-op `DO UPDATE` merely to
obtain `RETURNING` unless update triggers, row locks, and tuple churn are truly
acceptable.

[Official `INSERT` documentation](https://www.postgresql.org/docs/19/sql-insert.html)

## `FOR PORTION OF` temporal DML (preview)

**Use when:** updating or deleting only part of a range or multirange that
represents application time.

```sql
begin;

select 1
from product_prices
where product_id = $1
  and valid_at && daterange($2::date, $3::date, '[)')
for update;

update product_prices
  for portion of valid_at from $2::date to $3::date
  set amount = $4
  where product_id = $1;

commit;
```

PostgreSQL shrinks affected rows to the targeted period and inserts up to two
temporal-leftover rows to preserve history outside it. `DELETE` has analogous
syntax. Leftovers fire `INSERT` triggers, while `RETURNING` reports changed
rows but not the inserted leftovers.

At `READ COMMITTED`, precede each temporal update/delete with a matching
`SELECT ... FOR UPDATE`, including the period overlap, or concurrent changes can
be missed. Higher isolation has different retry behavior. Bounds must be
constant for the statement; column references are not allowed.

**Fallback through 18:** lock the matching rows, split ranges explicitly, and
insert/update/delete every segment in one transaction with exclusion and
temporal-key constraints rechecked.

[Official temporal-DML guide](https://www.postgresql.org/docs/19/dml-application-time-update-delete.html)

## `GROUP BY ALL` (preview)

**Use when:** every non-aggregate, non-window output expression should define
the grouping key.

```sql
select
  tenant_id,
  status,
  date_trunc('month', created_at) as month,
  count(*) as order_count
from orders
group by all;
```

`GROUP BY ALL` is derived from the select list. Adding or changing an output
expression can therefore change cardinality and report semantics. Prefer
explicit grouping expressions in long-lived interfaces where that coupling is
undesirable.

**Fallback through 18:** list each grouping expression explicitly or group by
the corresponding select-list ordinals when their maintenance tradeoff is
acceptable.

[Official `SELECT` documentation](https://www.postgresql.org/docs/19/sql-select.html)

## Window `IGNORE NULLS` (preview)

**Use when:** carrying the latest observed value forward or looking past gaps in
an ordered partition.

```sql
select
  device_id,
  measured_at,
  last_value(reading) ignore nulls over (
    partition by device_id
    order by measured_at
    rows between unbounded preceding and current row
  ) as latest_reading
from measurements;
```

`IGNORE NULLS` is available for `lag`, `lead`, `first_value`, `last_value`, and
`nth_value`; the default remains `RESPECT NULLS`. Frame semantics still apply.
In particular, spell the frame explicitly for `last_value` and `nth_value`.

**Fallback through 18:** use a lateral lookup for the nearest non-null row, a
filtered intermediate relation, or a purpose-built aggregate after checking
its ordering and frame semantics.

[Official window-function documentation](https://www.postgresql.org/docs/19/functions-window.html)

## `COPY` JSON and field-level error handling (preview)

**Use when:** streaming query rows as newline-delimited JSON or a single JSON
array, or retaining an input row while nulling only a field that fails type
conversion.

```sql
copy (
  select order_id, status, total
  from orders
) to stdout with (format json, force_array);

copy imported_orders (external_id, ordered_at, total)
from stdin
with (format csv, on_error set_null, log_verbosity verbose);
```

`FORMAT JSON` is output-only. Without `FORCE_ARRAY`, each output row is one JSON
object; with it, the stream is wrapped as one array. SQL `NULL` and a JSON
literal `null` are indistinguishable in JSON output.

`ON_ERROR set_null` applies only to text/CSV input-conversion failures. It does
not bypass `NOT NULL`, `CHECK`, foreign-key, trigger, or other integrity errors,
and `REJECT_LIMIT` remains specific to `ON_ERROR ignore`.

**Fallback through 18:** generate JSON with `row_to_json()` or `jsonb_build_*`
and load questionable fields into text staging columns before typed conversion.

[Official `COPY` documentation](https://www.postgresql.org/docs/19/sql-copy.html)

## Core `REPACK` (preview)

**Use when:** reclaiming table and index space through a core rewrite, optionally
while keeping a supported table available to other transactions.

```sql
repack (concurrently, analyze) orders;
```

Plain `REPACK` takes an `ACCESS EXCLUSIVE` lock. Concurrent mode requires a
primary key or index-based replica identity and is unavailable for unlogged,
partitioned, system, or TOAST tables and inside a transaction block. It is not
MVCC-safe. Budget at least table-plus-index temporary space, potentially more
when sorting, and monitor `pg_stat_progress_repack`.

**Fallback through 18:** use `VACUUM FULL`, `CLUSTER`, or a separately vetted
repacking extension according to lock, ordering, and availability needs.

[Official `REPACK` documentation](https://www.postgresql.org/docs/19/sql-repack.html)

## Merge and split partitions (preview)

**Use when:** changing partition granularity while asking PostgreSQL to create
the replacement partitions and move rows.

```sql
alter table sales
  merge partitions (sales_2026_q1, sales_2026_q2)
  into sales_2026_h1;

alter table sales
  split partition sales_2026_h2 into (
    partition sales_2026_q3
      for values from ('2026-07-01') to ('2026-10-01'),
    partition sales_2026_q4
      for values from ('2026-10-01') to ('2027-01-01')
  );
```

Both operations move data and can run for a long time. Split acquires
`ACCESS EXCLUSIVE` on the parent and source partition, does not support hash
partitioning, and only splits a simple non-partitioned child. Review copied and
dropped dependent objects, ACLs, bounds, space, and lock duration beforehand.

**Fallback through 18:** create replacement partitions, route or copy rows,
validate bounds and constraints, then attach/detach them in a controlled
migration.

[Official `ALTER TABLE` documentation](https://www.postgresql.org/docs/19/sql-altertable.html)

## `WAIT FOR LSN` (preview)

**Use when:** a read routed to an asynchronous replica must wait for a write's
WAL position to be replayed.

```sql
wait for lsn '0/306EE20'
with (mode 'standby_replay', timeout '500ms', no_throw);
```

The command returns a status such as `success` or `timeout` with `NO_THROW`.
It must be top-level, cannot hold an active snapshot, and is incompatible with
transactions above `READ COMMITTED`. Numeric LSN comparison does not identify
the WAL timeline, so promotion and cascading-replica designs need explicit
failover handling. Recovery conflicts can interrupt the wait.

**Fallback through 18:** poll `pg_last_wal_replay_lsn()` with a deadline, retry
policy, timeline/failover handling, and a route-to-primary fallback.

[Official `WAIT FOR` documentation](https://www.postgresql.org/docs/19/sql-wait-for.html)

## `EXPLAIN (ANALYZE, IO)` (preview)

**Use when:** examining prefetch depth, request counts and sizes, waits, and I/O
concurrency for scan nodes that expose those details.

```sql
explain (analyze, io, buffers)
select *
from large_events
where tenant_id = 42;
```

`IO` requires `ANALYZE`, so the statement executes. It complements rather than
replaces `BUFFERS`, timing settings, `pg_stat_io`, and operating-system
telemetry. Not every plan node reports every I/O field.

**Fallback through 18:** combine `EXPLAIN (ANALYZE, BUFFERS)`, `pg_stat_io`,
and external storage telemetry.

[Official `EXPLAIN` documentation](https://www.postgresql.org/docs/19/sql-explain.html)

## Publication sequences and exclusions (preview)

**Use when:** logical replication should include persistent sequences and all
tables except an explicit denylist.

```sql
create publication application_publication
for all sequences,
    all tables except (table audit_log, scratch_data);
```

`ALL SEQUENCES` includes current and future persistent sequences; temporary and
unlogged sequences are excluded. `EXCEPT` follows table object identity across
rename or schema moves. A table included by another subscribed publication is
still included overall. Creating the publication defines selection only; it
does not start replication.

**Fallback through 18:** list tables explicitly and synchronize sequence state
through a separately owned deployment or failover procedure.

[Official `CREATE PUBLICATION` documentation](https://www.postgresql.org/docs/19/sql-createpublication.html)

## Global-object DDL reconstruction (preview)

**Use when:** auditing or scripting reconstructed DDL for roles, databases, and
tablespaces.

```sql
select * from pg_get_role_ddl('application_user'::regrole);
select * from pg_get_database_ddl(current_database()::regdatabase);
```

The functions return one reconstructed statement per row; they do not preserve
the original command text. `pg_get_role_ddl()` never includes passwords. Treat
the result as reviewed migration input, not as an automatically complete backup
or a reason to export secrets through another path.

**Fallback through 18:** query the catalogs and generate narrowly scoped DDL,
or use established dump tooling with explicit secret-handling rules.

[Official system-information documentation](https://www.postgresql.org/docs/19/functions-info.html)

## Online data checksums (preview)

**Use when:** an existing cluster must enable or disable page checksums without
an offline `pg_checksums` maintenance window.

```sql
select pg_enable_data_checksums();
```

Online enablement rewrites cluster pages through a background worker, emits
WAL, consumes I/O, waits on old transactions and temporary tables, and does not
resume automatically after interruption. Monitor the cluster-wide checksum
state and replication lag; throttle and schedule it like a major maintenance
operation. Disabling checksums removes protection and requires an explicit risk
decision.

[Official PostgreSQL 19 checksum documentation](https://www.postgresql.org/docs/19/checksums.html)

## AIO workers and parallel autovacuum (preview)

**Use when:** PG18-style asynchronous I/O needs dynamically managed workers or
large relations benefit from parallel autovacuum processing.

The `worker` I/O method adds `io_min_workers`, `io_max_workers`, idle timeout,
and launch interval controls. Autovacuum adds cluster and per-table parallel
worker limits, while scoring weights influence which table is processed next.
Treat both as resource schedulers: cap CPU and I/O concurrency, observe queue
age and replica impact, and tune from production-like measurements.

[Official PostgreSQL 19 release notes](https://www.postgresql.org/docs/19/release-19.html)

## New operational statistics views (preview)

**Use when:** diagnosing lock pressure, recovery state, or why autovacuum chose
a table.

```sql
select * from pg_stat_lock;
select * from pg_stat_recovery;
select * from pg_stat_autovacuum_scores;
```

These are aggregate or current-state diagnostics, not immutable audit logs.
Capture samples with timestamps when trend or incident reconstruction matters,
and check view privileges before embedding them in application diagnostics.

[Official PostgreSQL 19 monitoring statistics](https://www.postgresql.org/docs/19/monitoring-stats.html)

## Unsigned `oid8` values (preview)

**Use when:** PostgreSQL-owned identifiers or interoperability data genuinely
need the full unsigned 64-bit range.

`oid8` is not a reason to replace ordinary application `bigint` keys. Confirm
driver encoding, casts, comparison behavior, and downstream type support before
exposing it through an API. `regdatabase` provides name-to-`oid8` casts for
database identifiers.

**Fallback through 18:** use `numeric(20, 0)` with explicit range checks when
the unsigned range is required, or retain `bigint` for signed application IDs.

[Official PostgreSQL 19 data types](https://www.postgresql.org/docs/19/datatype.html)

## Changed JIT, lock, and TOAST defaults (preview)

**Use when:** comparing performance or memory behavior across an upgrade.

PG19 disables JIT by default, changes the default TOAST compression from
`pglz` to `lz4`, and raises `max_locks_per_transaction` from 64 to 128 while
changing lock allocation sizing. Existing TOAST values are not rewritten merely
because the default changed. Explicitly benchmark analytical workloads before
re-enabling JIT and size shared memory from the new lock semantics rather than
copying the old numeric setting.

[Official PostgreSQL 19 migration notes](https://www.postgresql.org/docs/19/release-19.html)
