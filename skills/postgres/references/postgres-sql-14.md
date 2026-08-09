# PostgreSQL 14 SQL Additions

Use these patterns only when the oldest target is PostgreSQL 14 or newer. This
guide prioritizes additions that materially change generated SQL, schema design,
or diagnostics.

## Contents

- [Recursive CTE search order and cycle detection](#recursive-cte-search-order-and-cycle-detection)
- [`jsonb` subscripting](#jsonb-subscripting)
- [Multirange types](#multirange-types)
- [Arbitrary time buckets with `date_bin`](#arbitrary-time-buckets-with-date_bin)
- [Parsed SQL routine bodies](#parsed-sql-routine-bodies)
- [Procedure output parameters](#procedure-output-parameters)
- [Concurrent partition detach](#concurrent-partition-detach)
- [Extended statistics on expressions](#extended-statistics-on-expressions)
- [Per-column LZ4 TOAST compression](#per-column-lz4-toast-compression)

## Recursive CTE search order and cycle detection

**Use when:** traversing trees or adjacency lists where output order and cycle
handling should be explicit.

```sql
with recursive walk(id, parent_id) as (
  select id, parent_id
  from nodes
  where id = $1

  union all

  select n.id, n.parent_id
  from nodes as n
  join walk as w on n.parent_id = w.id
)
search depth first by id set traversal_order
cycle id set is_cycle using traversal_path
select id, parent_id, traversal_path
from walk
where not is_cycle
order by traversal_order;
```

`SEARCH` computes a sortable breadth- or depth-first key; it does not change the
recursive evaluation order by itself. `CYCLE` tracks visited keys and marks rows
that close a cycle.

**Fallback below 14:** carry a depth column and an array of visited keys in the
recursive term, reject `id = any(path)`, and order the final result explicitly.

[Official recursive CTE documentation](https://www.postgresql.org/docs/14/queries-with.html)

## `jsonb` subscripting

**Use when:** reading or updating known JSON object/array paths with compact
array-style syntax.

```sql
update profiles
set settings['notifications']['email'] = 'true'::jsonb
where id = $1
returning settings;

select *
from profiles
where settings['theme'] = '"dark"'::jsonb;
```

The result and assigned value are `jsonb`, not text. Missing intermediate
objects can be created, but traversal fails if an existing intermediate value is
a scalar. A JSON update still locks and rewrites the containing table row.

**Fallback below 14:** use `->`, `->>`, `#>`, `#>>`, and `jsonb_set()`.

[Official `jsonb` subscripting documentation](https://www.postgresql.org/docs/14/datatype-json.html#JSONB-SUBSCRIPTING)

## Multirange types

**Use when:** one value must represent several normalized, disjoint intervals,
such as availability, reservation gaps, or application-time coverage.

```sql
create table calendars (
  calendar_id bigint generated always as identity primary key,
  blocked datemultirange not null default '{}'::datemultirange
);

select datemultirange(
  daterange(date '2026-01-01', date '2026-01-05', '[)'),
  daterange(date '2026-01-10', date '2026-01-12', '[)')
);
```

Prefer a multirange over an array of ranges when union, intersection,
containment, adjacency, and GiST indexing are part of the domain. Prefer one row
per interval when intervals need independent metadata or ownership.

**Fallback below 14:** normalize intervals into a child table, or use an array
with explicit overlap and normalization logic.

[Official range and multirange documentation](https://www.postgresql.org/docs/14/rangetypes.html)

## Arbitrary time buckets with `date_bin`

**Use when:** grouping timestamps into fixed-width buckets such as 15 minutes,
aligned to an origin that is not a natural `date_trunc()` boundary.

```sql
select
  date_bin(
    interval '15 minutes',
    occurred_at,
    timestamptz '2026-01-01 00:02:30+00'
  ) as bucket,
  count(*)
from events
group by bucket
order by bucket;
```

The stride must be positive and cannot contain months or larger units. Keep the
source and origin timestamp types and time-zone assumptions deliberate.

**Fallback below 14:** use epoch arithmetic for fixed-duration buckets, or
`date_trunc()` when whole supported units are sufficient.

[Official `date_bin()` documentation](https://www.postgresql.org/docs/14/functions-datetime.html#FUNCTIONS-DATETIME-BIN)

## Parsed SQL routine bodies

**Use when:** defining `LANGUAGE SQL` functions whose body should be parsed at
creation time and whose object dependencies should be tracked.

```sql
create function add_tax(amount numeric, rate numeric)
returns numeric
language sql
immutable
returns null on null input
return amount * (1 + rate);
```

The unquoted `RETURN expression` and `BEGIN ATOMIC ... END` forms catch syntax
and name-resolution errors earlier and track dependencies. They cannot cover
every polymorphic or late-bound use case supported by a quoted body.

**Fallback below 14:** use a dollar-quoted SQL body and test dependency changes
explicitly.

[Official `CREATE FUNCTION` documentation](https://www.postgresql.org/docs/14/sql-createfunction.html)

## Procedure output parameters

**Use when:** a procedure invoked with `CALL` should return one result row via
`OUT` parameters after performing procedural work.

```sql
create procedure double_value(in source integer, out result integer)
language plpgsql
as $$
begin
  result := source * 2;
end
$$;

call double_value(21, null);
```

Do not choose a procedure only to mimic a scalar function. Procedures are most
useful when `CALL` semantics or transaction control are required.

**Fallback below 14:** return a scalar, record, or named composite type from a
function.

[Official `CREATE PROCEDURE` documentation](https://www.postgresql.org/docs/14/sql-createprocedure.html)

## Concurrent partition detach

**Use when:** retiring or archiving a partition while reducing the duration of
the strongest lock on the partitioned parent.

```sql
alter table events
detach partition events_2025_12 concurrently;
```

This form cannot run inside a transaction block. If the operation is interrupted
after its first phase, complete it with:

```sql
alter table events
detach partition events_2025_12 finalize;
```

Inspect foreign keys, the default partition, and application routing before the
change. It remains DDL and requires the skill's normal approval and migration
workflow.

**Fallback below 14:** schedule regular `DETACH PARTITION` in a maintenance
window and account for its stronger lock.

[Official `ALTER TABLE` documentation](https://www.postgresql.org/docs/14/sql-altertable.html)

## Extended statistics on expressions

**Use when:** row estimates are poor because filters combine correlated columns
and expressions.

```sql
create statistics users_country_email_stats
on country_code, (lower(email))
from users;

analyze users;
```

Create statistics for observed query predicates, not speculatively. Re-run
`ANALYZE`, compare estimates with `EXPLAIN`, and remove statistics that do not
improve representative plans.

**Fallback below 14:** consider an expression index, a maintained generated
column, or ordinary per-column statistics, then verify the plan.

[Official planner statistics documentation](https://www.postgresql.org/docs/14/planner-stats.html#PLANNER-STATS-EXTENDED)

## Per-column LZ4 TOAST compression

**Use when:** large compressible values benefit from faster compression and the
server build includes LZ4 support.

```sql
alter table documents
alter column body set compression lz4;
```

The setting affects values written after the change; existing values require a
rewrite to change representation. Benchmark with realistic payloads and include
server-build compatibility in deployment checks.

**Fallback below 14 or without LZ4:** use the default `pglz` compression and
address oversized payloads through schema or storage design.

[Official TOAST documentation](https://www.postgresql.org/docs/14/storage-toast.html)
