# PostgreSQL 18 SQL Additions

Use these patterns only when the oldest target is PostgreSQL 18 or newer.

## Contents

- [Explicit `OLD` and `NEW` in DML `RETURNING`](#explicit-old-and-new-in-dml-returning)
- [Virtual generated columns](#virtual-generated-columns)
- [Temporal keys and foreign keys](#temporal-keys-and-foreign-keys)
- [Documentary `NOT ENFORCED` constraints](#documentary-not-enforced-constraints)
- [Core UUIDv7 generation](#core-uuidv7-generation)
- [Bounded bad-row tolerance in `COPY`](#bounded-bad-row-tolerance-in-copy)
- [Named and cataloged `NOT NULL` constraints](#named-and-cataloged-not-null-constraints)
- [Logical replication of stored generated columns](#logical-replication-of-stored-generated-columns)
- [B-tree skip-scan diagnostics](#b-tree-skip-scan-diagnostics)
- [`CREATE FOREIGN TABLE LIKE`](#create-foreign-table-like)
- [Asynchronous I/O](#asynchronous-io)
- [`pg_upgrade` statistics retention](#pg_upgrade-statistics-retention)
- [OAuth authentication](#oauth-authentication)
- [Unicode case folding](#unicode-case-folding)
- [Richer default `EXPLAIN ANALYZE`](#richer-default-explain-analyze)
- [Foreign-data changes](postgres-fdw-versions.md#postgresql-18)

## Explicit `OLD` and `NEW` in DML `RETURNING`

**Use when:** an application or audit pipeline needs pre-change and post-change
values from the same atomic statement.

```sql
update inventory
set quantity = quantity - $2
where sku = $1
returning with (old as before, new as after)
  before.quantity as old_quantity,
  after.quantity as new_quantity;
```

`OLD` and `NEW` work with `INSERT`, `UPDATE`, `DELETE`, and `MERGE`. For a plain
`INSERT`, old values are normally `NULL`; for a plain `DELETE`, new values are
normally `NULL`. Returned values include changes made by row triggers.

**Fallback below 18:** use a data-modifying CTE where its semantics are enough,
a trigger-based audit table, or a prior locked read in the same transaction.
Do not assume a separate unlocked `SELECT` observes the same row version.

[Official `RETURNING` documentation](https://www.postgresql.org/docs/18/dml-returning.html)

## Virtual generated columns

**Use when:** a deterministic value should be computed on read without occupying
per-row storage.

```sql
create table order_lines (
  quantity integer not null,
  unit_price numeric(12, 2) not null,
  line_total numeric(14, 2)
    generated always as (quantity * unit_price) virtual
);
```

Virtual is the PostgreSQL 18 default when neither `VIRTUAL` nor `STORED` is
written; prefer spelling the kind explicitly in portable migrations. A virtual
column cannot use a user-defined type, function, operator, or cast, even
indirectly. Generated expressions remain immutable, row-local, and unable to
reference another generated column.

**Fallback below 18:** use a view or expression index for read-time derivation,
or declare a stored generated column and accept write-time computation and
storage.

[Official generated-column documentation](https://www.postgresql.org/docs/18/ddl-generated-columns.html)

## Temporal keys and foreign keys

**Use when:** validity periods must not overlap per entity and a referencing
period must be fully covered by referenced periods.

```sql
-- bigint equality in the GiST-backed temporal key requires btree_gist.
create extension if not exists btree_gist;

create table product_prices (
  product_id bigint not null,
  valid_at daterange not null,
  amount numeric(12, 2) not null,
  primary key (product_id, valid_at without overlaps)
);

create table price_assignments (
  product_id bigint not null,
  covered_at daterange not null,
  foreign key (product_id, period covered_at)
    references product_prices (product_id, period valid_at)
);
```

`WITHOUT OVERLAPS` must be the final column of a `PRIMARY KEY` or `UNIQUE`
constraint and must be a range or multirange; empty values are rejected. A
`PERIOD` foreign key checks complete temporal coverage, which can come from
multiple referenced rows. Approve and install `btree_gist` explicitly when the
non-period key types need its GiST operator classes.

**Fallback below 18:** use an exclusion constraint for non-overlap and custom
transactional checks or triggers for temporal referential coverage. Analyze
race behavior carefully; a check trigger without suitable locking is unsafe.

[Official `CREATE TABLE` documentation](https://www.postgresql.org/docs/18/sql-createtable.html)

## Documentary `NOT ENFORCED` constraints

**Use when:** a `CHECK` or foreign-key relationship is guaranteed elsewhere and
must be represented as database metadata without runtime validation.

```sql
create table imported_events (
  event_id bigint primary key,
  source_id bigint,
  payload jsonb,
  constraint imported_events_payload_object
    check (payload is json object) not enforced
);
```

`NOT ENFORCED` means PostgreSQL does not protect the invariant. It is not a
deferred, unvalidated, or eventually checked constraint. The optimizer may
still use the declaration where doing so does not affect result correctness.
Use it only when ownership of the real integrity guarantee is explicit.

**Fallback below 18:** document the invariant with comments or schema tooling,
or use an enforced constraint after validating and repairing the data.

[Official `CREATE TABLE` documentation](https://www.postgresql.org/docs/18/sql-createtable.html)

## Core UUIDv7 generation

**Use when:** globally unique identifiers should have time-ordered UUIDv7
layout without relying on an extension.

```sql
create table events (
  event_id uuid primary key default uuidv7(),
  occurred_at timestamptz not null default clock_timestamp()
);
```

UUIDv7 improves temporal locality compared with random UUIDv4, but its embedded
timestamp is not an authoritative event time and does not replace an ordinary
timestamp column. `uuid_extract_timestamp()` supports UUIDv1 and UUIDv7 in
PostgreSQL 18.

**Fallback below 18:** use UUIDv4, identity keys, or a separately approved UUIDv7
implementation, and keep the migration's generator ownership explicit.

[Official UUID documentation](https://www.postgresql.org/docs/18/functions-uuid.html)

## Bounded bad-row tolerance in `COPY`

**Use when:** a best-effort staging load must abort after a finite number of
input-conversion failures.

```sql
copy imported_orders (external_id, ordered_at, total)
from stdin
with (
  format csv,
  on_error ignore,
  reject_limit 100,
  log_verbosity default
);
```

`REJECT_LIMIT` requires `ON_ERROR ignore`, is a positive `bigint`, and counts
input-conversion errors. Without it, ignore mode can skip an unlimited number
of bad rows. `LOG_VERBOSITY silent` is also new, but use it only when skipped
row counts are captured through another observable channel.

**Fallback below 18:** enforce the threshold in the import client, or convert
from a text staging table and abort based on an explicit rejected-row query.

[Official `COPY` documentation](https://www.postgresql.org/docs/18/sql-copy.html)

## Named and cataloged `NOT NULL` constraints

**Use when:** stable constraint names are needed for migrations, diagnostics,
or schema introspection.

```sql
create table users (
  user_id bigint primary key,
  email text constraint users_email_not_null not null
);

select conname, conkey
from pg_constraint
where conrelid = 'users'::regclass
  and contype = 'n';
```

PostgreSQL 18 stores not-null constraints in `pg_constraint`, with
`contype = 'n'`, instead of treating them only as a column attribute.
Constraint names are not globally unique, so pair them with relation/schema
identity.

**Fallback below 18:** inspect `pg_attribute.attnotnull`; do not expect a named
not-null object in `pg_constraint`.

[Official `pg_constraint` documentation](https://www.postgresql.org/docs/18/catalog-pg-constraint.html)

## Logical replication of stored generated columns

**Use when:** subscribers or output plugins need the computed value of a stored
generated column from the publisher.

```sql
create publication order_publication
for table order_lines
with (publish_generated_columns = stored);
```

A publication column list can nominate stored generated columns instead. A
column list takes precedence over the publication parameter. The subscriber
column receiving a published generated value must be a regular column;
publishing into another generated column is unsupported. Initial synchronization
to subscribers older than PostgreSQL 18 does not copy these columns.

**Fallback below 18:** recompute on the subscriber, replicate a regular column,
or have the output consumer derive the value.

[Official generated-column replication documentation](https://www.postgresql.org/docs/18/logical-replication-gencols.html)

## B-tree skip-scan diagnostics

**Use when:** a multicolumn B-tree has a low-cardinality leading column and a
query constrains a later column strongly enough for repeated index searches to
beat a full scan.

```sql
create index orders_status_customer_idx on orders (status, customer_id);

explain (analyze, buffers)
select order_id
from orders
where customer_id = 42;
```

Skip scan is a planner optimization, not new query syntax. In PostgreSQL 18,
`EXPLAIN` can report `Index Searches`, making repeated probes visible. Verify
the chosen plan with representative statistics and workload; do not remove a
purpose-built index merely because skip scan can sometimes use another one.

**Fallback below 18:** create an index whose leading columns match the query or
accept the planner's alternative plan after measurement.

[Official `EXPLAIN` guidance](https://www.postgresql.org/docs/18/using-explain.html)

## `CREATE FOREIGN TABLE LIKE`

**Use when:** a foreign table should start from an existing relation's column
layout rather than duplicate it manually.

```sql
create foreign table analytics_orders (
  like orders including defaults including generated
)
server analytics_server
options (schema_name 'public', table_name 'orders');
```

The copied definition is decoupled from its source after creation. Options and
enforcement still depend on the foreign-data wrapper and remote system. Core
PostgreSQL generally assumes foreign-table constraints are true rather than
enforcing them, so do not copy constraints that the remote data can violate.

**Fallback below 18:** generate and review an explicit foreign-table column
list or import the remote schema through the foreign-data wrapper.

[Official `CREATE FOREIGN TABLE` documentation](https://www.postgresql.org/docs/18/sql-createforeigntable.html)

## Asynchronous I/O

**Use when:** sequential scans, bitmap heap scans, VACUUM, or other read-heavy
operations should queue multiple reads instead of waiting on each one.

PG18 introduces the AIO subsystem controlled by `io_method` and related
concurrency limits. Inspect active handles through `pg_aios` and compare
`pg_stat_io`, latency, queue depth, and CPU before and after changing the
method. Availability and best settings depend on the operating system and
PostgreSQL build.

**Fallback below 18:** tune existing prefetch and concurrency settings and rely
on OS caching without expecting equivalent queue visibility.

[Official PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html)

## `pg_upgrade` statistics retention

**Use when:** reducing the post-upgrade period of poor plans caused by missing
optimizer statistics.

PG18 can preserve per-relation and per-column statistics during `pg_upgrade`.
Extended statistics are not preserved. Keep post-upgrade `ANALYZE` validation,
inspect stale or missing statistics, and use `--no-statistics` when the old
statistics are not trustworthy for the new environment.

Statistics retention shortens recovery of planner quality; it does not prove
plans remain optimal after data, collation, extension, or server changes.

[Official PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html)

## OAuth authentication

**Use when:** clients should authenticate with externally issued OAuth tokens
and the server can load a trusted validator implementation.

PG18 adds the `oauth` HBA method, libpq OAuth parameters, and
`oauth_validator_libraries`. The server must be built with the required curl
support. Validate issuer, audience, token lifetime, role mapping, TLS trust, and
fail-closed behavior; do not treat token validation as authorization inside the
database.

**Fallback below 18:** terminate OAuth at a trusted proxy that establishes a
separately authenticated PostgreSQL connection, or use an existing supported
database authentication method.

[Official PostgreSQL 18 OAuth documentation](https://www.postgresql.org/docs/18/auth-oauth.html)

## Unicode case folding

**Use when:** caseless matching must handle Unicode equivalences that simple
`lower()` cannot represent.

```sql
select casefold('Straße') = casefold('STRASSE');
```

Case folding can change string length and depends on encoding/collation
behavior. Store the original value, define uniqueness semantics explicitly,
and verify whether an expression index or maintained normalized key matches the
application's locale and upgrade requirements.

**Fallback below 18:** use a reviewed normalization strategy, `citext`, or a
`lower()` expression index only when its weaker semantics are acceptable.

[Official PostgreSQL 18 string functions](https://www.postgresql.org/docs/18/functions-string.html)

## Richer default `EXPLAIN ANALYZE`

**Use when:** comparing execution plans with less diagnostic boilerplate.

PG18 automatically includes buffer statistics in `EXPLAIN ANALYZE`, reports
index lookup counts, and uses fractional row counts where useful. Existing
parsers and snapshots may change even when the query plan does not, so update
tooling before upgrade and compare semantic fields rather than raw text.

[Official PostgreSQL 18 `EXPLAIN` documentation](https://www.postgresql.org/docs/18/sql-explain.html)
