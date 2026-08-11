# PostgreSQL 15 SQL Additions

Use these patterns only when the oldest target is PostgreSQL 15 or newer. In
particular, do not give PostgreSQL 15 `MERGE` capabilities that arrived in 17.

## Contents

- [Batch synchronization with `MERGE`](#batch-synchronization-with-merge)
- [Unique null values with `NULLS NOT DISTINCT`](#unique-null-values-with-nulls-not-distinct)
- [Filtered logical publications](#filtered-logical-publications)
- [Security-invoker views](#security-invoker-views)
- [SQL-standard regular-expression functions](#sql-standard-regular-expression-functions)
- [Validated CSV headers](#validated-csv-headers)
- [Column-specific foreign-key delete actions](#column-specific-foreign-key-delete-actions)
- [Negative and oversized numeric scales](#negative-and-oversized-numeric-scales)
- [Changing a table access method](#changing-a-table-access-method)
- [Secure defaults for the `public` schema](#secure-defaults-for-the-public-schema)
- [Structured JSON server logs](#structured-json-server-logs)
- [WAL and base-backup compression](#wal-and-base-backup-compression)
- [Foreign-data changes](postgres-fdw-versions.md#postgresql-15)

## Batch synchronization with `MERGE`

**Use when:** a source relation drives multiple actions against a target table
in one statement.

```sql
merge into inventory as target
using incoming_inventory as source
on target.sku = source.sku
when matched and source.quantity = 0 then
  delete
when matched then
  update set quantity = source.quantity,
             updated_at = clock_timestamp()
when not matched then
  insert (sku, quantity)
  values (source.sku, source.quantity);
```

PostgreSQL 15 `MERGE` does **not** support `RETURNING`, `merge_action()`,
`WHEN NOT MATCHED BY SOURCE`, or modification of an updatable view. Those are
PostgreSQL 17 additions. Ensure the source cannot produce more than one
candidate modification for the same target row.

**Fallback below 15:** use separate DML statements in a transaction, or
`INSERT ... ON CONFLICT` when the only choices are insert and update.

[Official `MERGE` documentation](https://www.postgresql.org/docs/15/sql-merge.html)

## Unique null values with `NULLS NOT DISTINCT`

**Use when:** `NULL` represents one logical value and at most one row may carry
it for a unique key.

```sql
create table external_accounts (
  id bigint generated always as identity primary key,
  external_ref text unique nulls not distinct
);
```

This changes only the constraint's null comparison; it does not make the column
`NOT NULL`.

**Fallback below 15:** for a single nullable column, combine one unique index
for non-null values with one constant-expression index that permits at most one
null row:

```sql
create unique index external_accounts_ref_uq
  on external_accounts (external_ref)
  where external_ref is not null;

create unique index external_accounts_one_null_uq
  on external_accounts ((true))
  where external_ref is null;
```

Avoid a `coalesce()` sentinel unless the domain has a separately enforced value
that can never collide with real data.

[Official unique-constraint documentation](https://www.postgresql.org/docs/15/ddl-constraints.html#DDL-CONSTRAINTS-UNIQUE-CONSTRAINTS)

## Filtered logical publications

**Use when:** subscribers need only selected rows and columns.

```sql
create publication tenant_42_accounts
for table accounts (tenant_id, account_id, email)
where (tenant_id = 42);
```

For publications that include updates or deletes, every column used by the row
filter and every required identity column must satisfy the replica-identity
rules. Initial synchronization and partition behavior also need explicit review.

**Fallback below 15:** publish the full table and filter in a controlled
downstream pipeline, or redesign the replicated table boundary.

[Official `CREATE PUBLICATION` documentation](https://www.postgresql.org/docs/15/sql-createpublication.html)

## Security-invoker views

**Use when:** a view should apply the caller's privileges and row-level security
policies to underlying relations.

```sql
create view visible_orders
with (security_invoker = true)
as
select id, tenant_id, total, created_at
from orders;
```

The caller needs privileges on both the view and its underlying relations. This
is not equivalent to a `SECURITY DEFINER` function; functions invoked by the view
retain their own security behavior.

**Fallback below 15:** expose the base relation directly with RLS, or design a
small, audited security-invoker function/API boundary.

[Official `CREATE VIEW` documentation](https://www.postgresql.org/docs/15/sql-createview.html)

## SQL-standard regular-expression functions

**Use when:** standard-style regexp counting, matching, positioning, or
sub-string extraction makes intent clearer.

```sql
select
  regexp_count('item-12 item-345', '[0-9]+') as number_count,
  regexp_substr('item-12 item-345', '[0-9]+', 1, 2) as second_number,
  regexp_like('ABC-123', '^[A-Z]+-[0-9]+$') as valid_code;
```

Check flags and occurrence semantics when porting from another database; regexp
dialects are similar, not universally identical.

**Fallback below 15:** use PostgreSQL POSIX operators (`~`, `~*`) and functions
such as `regexp_match()` / `regexp_matches()`.

[Official pattern-matching documentation](https://www.postgresql.org/docs/15/functions-matching.html)

## Validated CSV headers

**Use when:** a `COPY FROM` CSV load must reject a header with the wrong column
names or order.

```sql
copy staging_accounts (account_id, email)
from stdin
with (format csv, header match);
```

`HEADER MATCH` validates the names and order but not the semantic quality of the
following rows.

**Fallback below 15:** parse and validate the first line in the client or ingest
pipeline before starting `COPY`.

[Official `COPY` documentation](https://www.postgresql.org/docs/15/sql-copy.html)

## Column-specific foreign-key delete actions

**Use when:** a composite foreign key includes context that must be preserved
while only the optional relationship column becomes null.

```sql
create table posts (
  tenant_id bigint not null,
  post_id bigint not null,
  author_id bigint,
  primary key (tenant_id, post_id),
  foreign key (tenant_id, author_id)
    references users (tenant_id, user_id)
    on delete set null (author_id)
);
```

Without the column list, both referencing columns would be set to null. Column
lists are available for `ON DELETE SET NULL` and `SET DEFAULT`, not the analogous
`ON UPDATE` actions.

**Fallback below 15:** use a trigger with tests for concurrency, cascading, and
restore behavior, or model the optional relationship separately.

[Official foreign-key documentation](https://www.postgresql.org/docs/15/ddl-constraints.html#DDL-CONSTRAINTS-FK)

## Negative and oversized numeric scales

**Use when:** the type itself should round to powers of ten, or represent only a
small fractional range.

```sql
create table forecasts (
  rounded_revenue numeric(6, -3),
  tiny_ratio numeric(3, 5)
);
```

`numeric(6, -3)` rounds to the nearest thousand. A scale greater than precision
accepts only fractional values in the documented range. These forms are less
portable than conventional non-negative scales.

**Fallback below 15:** enforce rounding through explicit expressions, generated
columns, or domain checks.

[Official numeric-type documentation](https://www.postgresql.org/docs/15/datatype-numeric.html)

## Changing a table access method

**Use when:** migrating an existing table to another installed table access
method.

```sql
alter table events set access method heap;
```

The operation rewrites the table and can be expensive. Confirm extension
availability, locking, disk headroom, replication impact, and rollback before
using a non-default access method.

**Fallback below 15:** create a replacement table with the desired access method,
copy and validate data, then perform a controlled cutover.

[Official `ALTER TABLE` documentation](https://www.postgresql.org/docs/15/sql-altertable.html)

## Secure defaults for the `public` schema

**Use when:** creating new PG15 clusters or databases, or auditing an upgrade
for safe object-creation privileges.

New databases revoke `CREATE` on schema `public` from `PUBLIC` and make the
database-local `pg_database_owner` role its owner. Upgrades and restored dumps
preserve existing ownership and grants, so do not infer the new posture from
the server major alone.

```sql
select nspowner::regrole, nspacl
from pg_namespace
where nspname = 'public';
```

Review application migrations before revoking legacy access; explicitly grant
creation only to intended owner or migration roles.

[Official PostgreSQL 15 release notes](https://www.postgresql.org/docs/15/release-15.html)

## Structured JSON server logs

**Use when:** log collectors should ingest stable structured fields instead of
parsing `stderr` or CSV text.

Set `log_destination = 'jsonlog'` together with a compatible logging collector
and rotation policy. Treat field names and multiline messages as structured
records, preserve server timestamps and session identifiers, and test the
ingestion pipeline before replacing an existing destination.

**Fallback below 15:** use `csvlog` or a consistently configured text prefix
and parse it at the collector boundary.

[Official PostgreSQL 15 logging documentation](https://www.postgresql.org/docs/15/runtime-config-logging.html)

## WAL and base-backup compression

**Use when:** WAL or base-backup bandwidth and storage are material and CPU
headroom is available.

PG15 allows LZ4 or Zstandard for full-page WAL compression through
`wal_compression`. `pg_basebackup` can compress on the server with gzip, LZ4,
or Zstandard and supports richer client/server compression placement.
Benchmark write latency, recovery time, CPU cost, and tool build support before
changing production defaults.

**Fallback below 15:** use the compression methods supported by the exact
server/client pair or compress only after producing and verifying the backup.

[Official PostgreSQL 15 release notes](https://www.postgresql.org/docs/15/release-15.html)
