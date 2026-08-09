# PostgreSQL 17 SQL Additions

Use these patterns only when the oldest target is PostgreSQL 17 or newer.

## Contents

- [`JSON_TABLE` and SQL/JSON query functions](#json_table-and-sqljson-query-functions)
- [Expanded `MERGE` and action reporting](#expanded-merge-and-action-reporting)
- [Error-tolerant `COPY FROM`](#error-tolerant-copy-from)
- [Changing a generated-column expression](#changing-a-generated-column-expression)
- [`EXPLAIN` planner memory and output serialization](#explain-planner-memory-and-output-serialization)
- [Session-zone conversion with `AT LOCAL`](#session-zone-conversion-with-at-local)
- [UUID metadata extraction](#uuid-metadata-extraction)
- [Bounded random values](#bounded-random-values)

## `JSON_TABLE` and SQL/JSON query functions

**Use when:** projecting nested JSON into typed relational rows or using the
SQL-standard `JSON_EXISTS`, `JSON_QUERY`, and `JSON_VALUE` functions.

```sql
select i.order_id, item.*
from inbound_orders as i,
     json_table(
       i.payload,
       '$.items[*]'
       columns (
         line_no for ordinality,
         sku text path '$.sku',
         quantity integer path '$.quantity' error on error
       )
     ) as item;
```

`JSON_TABLE` is implicitly lateral to the row that supplies its input. Choose
`ON EMPTY` and `ON ERROR` behavior deliberately: their defaults can turn a
missing value or conversion failure into SQL `NULL`. Parsing errors while a
non-`jsonb` context item is converted to `jsonb` are not handled by those
clauses.

**Fallback below 17:** use `jsonb_path_*`, `jsonb_to_recordset()`,
`jsonb_array_elements()` plus a lateral join, or explicit operators and casts.

[Official JSON documentation](https://www.postgresql.org/docs/17/functions-json.html)

## Expanded `MERGE` and action reporting

**Use when:** synchronizing a target against a complete replacement source,
including deleting target rows absent from that source, and reporting each
chosen action.

```sql
merge into inventory as target
using replacement_inventory as source
on source.sku = target.sku
when not matched by target then
  insert (sku, quantity) values (source.sku, source.quantity)
when matched and target.quantity is distinct from source.quantity then
  update set quantity = source.quantity
when not matched by source then
  delete
returning merge_action(), target.*;
```

PostgreSQL 17 adds `WHEN NOT MATCHED BY SOURCE`, `RETURNING`,
`merge_action()`, and support for suitable updatable views. Ensure the source
joins to each target row at most once. Clause order matters, and concurrent
writers still require an isolation and retry policy; `MERGE` is not a drop-in
replacement for the concurrency guarantee of `INSERT ... ON CONFLICT`.

**Fallback on 15–16:** use the smaller `MERGE` feature set and a follow-up query,
or split source-only cleanup into a separate statement. **Fallback below 15:**
use explicit `INSERT`, `UPDATE`, and `DELETE` statements in a transaction.

[Official `MERGE` documentation](https://www.postgresql.org/docs/17/sql-merge.html)

## Error-tolerant `COPY FROM`

**Use when:** a staging load may skip rows whose fields cannot be converted to
the destination data types.

```sql
copy imported_orders (external_id, ordered_at, total)
from stdin
with (
  format csv,
  header match,
  on_error ignore,
  log_verbosity verbose
);
```

`ON_ERROR ignore` applies to text/CSV input-conversion errors. It does not turn
arbitrary constraint, trigger, row-shape, or infrastructure failures into
skipped rows. Prefer a staging table, retain the source file, and reconcile the
reported skipped-row count before promoting data.

**Fallback below 17:** validate in the producer, or load text columns into a
staging table and convert with explicit validation queries.

[Official `COPY` documentation](https://www.postgresql.org/docs/17/sql-copy.html)

## Changing a generated-column expression

**Use when:** the formula of an existing stored generated column must evolve
without dropping and recreating the column definition.

```sql
alter table order_lines
  alter column line_total
  set expression as (quantity * unit_price * (1 - discount_rate));

analyze order_lines;
```

PostgreSQL rewrites existing generated values and removes the column's
statistics. Plan for rewrite time, WAL, locks, replica lag, and the follow-up
`ANALYZE`. PostgreSQL 17 generated columns are stored; virtual generated
columns arrive in PostgreSQL 18.

**Fallback below 17:** add a replacement generated column, backfill dependent
objects, switch consumers, and remove the old column in a staged migration.

[Official `ALTER TABLE` documentation](https://www.postgresql.org/docs/17/sql-altertable.html)

## `EXPLAIN` planner memory and output serialization

**Use when:** separating planner-memory use and result serialization cost from
the execution plan itself.

```sql
explain (analyze, buffers, memory, serialize text)
select payload
from event_log
where tenant_id = 42
order by occurred_at desc
limit 1000;
```

`MEMORY` reports planning-phase memory. `SERIALIZE TEXT` or `BINARY` measures
conversion of result values but not network transmission, and requires
`ANALYZE`. The statement is therefore executed; wrap write statements in a
transaction that is rolled back when diagnostic execution must not persist.

**Fallback below 17:** use ordinary `EXPLAIN (ANALYZE, BUFFERS)` and measure
client-observed result processing separately.

[Official `EXPLAIN` documentation](https://www.postgresql.org/docs/17/sql-explain.html)

## Session-zone conversion with `AT LOCAL`

**Use when:** conversion intentionally follows the session's `TimeZone`.

```sql
begin;

set local timezone = 'Europe/Rome';

select occurred_at at local as local_occurred_at
from events;

commit;
```

`AT LOCAL` is shorthand for `AT TIME ZONE` using the session setting. Keep the
explicit `SET LOCAL` in the same transaction when connection pools or callers
can change session state. Use an explicit named zone instead when the zone is a
business input rather than session policy.

**Fallback below 17:** use `AT TIME ZONE current_setting('TimeZone')` or,
preferably, an explicit zone name.

[Official date/time documentation](https://www.postgresql.org/docs/17/functions-datetime.html)

## UUID metadata extraction

**Use when:** inspecting UUID version metadata or extracting the timestamp from
a version-1 UUID.

```sql
select
  id,
  uuid_extract_version(id) as uuid_version,
  uuid_extract_timestamp(id) as embedded_timestamp
from imported_entities;
```

In PostgreSQL 17, timestamp extraction supports UUIDv1 and returns `NULL` for
other versions. The embedded timestamp depends on the UUID producer and is not
a substitute for an authoritative business timestamp. Core UUIDv7 generation,
and extraction from UUIDv7, arrive in PostgreSQL 18.

**Fallback below 17:** decode only in trusted application code or use a vetted
extension, and keep ordinary timestamp columns for domain events.

[Official UUID documentation](https://www.postgresql.org/docs/17/functions-uuid.html)

## Bounded random values

**Use when:** tests, simulations, or non-security-sensitive sampling need a
value in an inclusive typed range.

```sql
select random(1, 6) as die_roll;
select random(10.00::numeric, 20.00::numeric) as sample_price;
```

The overloads accept `integer`, `bigint`, or `numeric` bounds and include both
endpoints. PostgreSQL's pseudo-random generator is not suitable for secrets,
tokens, or cryptographic keys.

**Fallback below 17:** scale `random()` carefully for the desired range and
type, accounting for inclusive versus exclusive endpoints.

[Official mathematical-function documentation](https://www.postgresql.org/docs/17/functions-math.html)
