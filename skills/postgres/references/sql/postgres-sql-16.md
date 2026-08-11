# PostgreSQL 16 SQL Additions

Use these patterns only when the oldest target is PostgreSQL 16 or newer.

## Contents

- [SQL/JSON constructors and validation](#sqljson-constructors-and-validation)
- [Representative values with `ANY_VALUE`](#representative-values-with-any_value)
- [Array sampling and shuffling](#array-sampling-and-shuffling)
- [Time-zone-aware date arithmetic](#time-zone-aware-date-arithmetic)
- [`COPY FROM` default-value sentinels](#copy-from-default-value-sentinels)
- [Generic prepared-statement plans](#generic-prepared-statement-plans)
- [Cluster I/O diagnostics](#cluster-io-diagnostics)
- [Independent role-membership options](#independent-role-membership-options)
- [Custom ICU collation rules](#custom-icu-collation-rules)
- [Standby logical decoding and parallel apply](#standby-logical-decoding-and-parallel-apply)
- [Regex and included authentication rules](#regex-and-included-authentication-rules)
- [Readable numeric literals](#readable-numeric-literals)
- [COPY throughput changes](#copy-throughput-changes)
- [Foreign-data changes](postgres-fdw-versions.md#postgresql-16)

## SQL/JSON constructors and validation

**Use when:** constructing JSON with SQL-standard null/uniqueness behavior or
validating text before conversion.

```sql
select json_object(
  'id' value id,
  'email' value email
  absent on null
  returning jsonb
)
from users;

select payload is json object with unique keys
from inbound_messages;
```

`JSON_ARRAY`, `JSON_ARRAYAGG`, `JSON_OBJECT`, and `JSON_OBJECTAGG` expose
standard clauses such as `ABSENT ON NULL`, `WITH UNIQUE KEYS`, and `RETURNING`.
`IS JSON` can test values, scalars, arrays, objects, and key uniqueness without
raising a parse error for invalid text.

**Fallback below 16:** use `json[b]_build_object()`, `json[b]_agg()`, explicit
null filtering, and guarded casts or `jsonb_typeof()`.

[Official JSON documentation](https://www.postgresql.org/docs/16/functions-json.html)

## Representative values with `ANY_VALUE`

**Use when:** any non-null member of a group is semantically interchangeable and
choosing the minimum or maximum would falsely imply ordering.

```sql
select
  customer_id,
  any_value(customer_display_name) as customer_display_name,
  sum(total) as lifetime_value
from orders
group by customer_id;
```

The chosen value is deliberately unspecified. Do not use `ANY_VALUE()` to hide
inconsistent group data when the selected value affects correctness.

**Fallback below 16:** use `min()` or `max()` only when that deterministic choice
is semantically acceptable, or repair the functional dependency in the schema.

[Official aggregate documentation](https://www.postgresql.org/docs/16/functions-aggregate.html)

## Array sampling and shuffling

**Use when:** a small, bounded array already belongs in one row and needs a
random subset or ordering.

```sql
select
  array_sample(tags, least(3, cardinality(tags))) as sampled_tags,
  array_shuffle(candidate_ids) as randomized_candidates
from recommendations;
```

`array_sample()` cannot request more items than the first dimension contains.
For multidimensional arrays, both functions operate on first-dimension slices.
Do not move a large relational sampling problem into an array just to use these
functions.

**Fallback below 16:** `unnest()` the array, order by `random()`, limit, and
aggregate again when needed.

[Official array documentation](https://www.postgresql.org/docs/16/functions-array.html)

## Time-zone-aware date arithmetic

**Use when:** adding or subtracting calendar intervals must follow the rules of
an explicitly named time zone, including daylight-saving transitions.

```sql
select date_add(
  timestamptz '2026-03-28 12:00:00+01',
  interval '1 day',
  'Europe/Rome'
);
```

`date_add()` and `date_subtract()` take an optional zone. PostgreSQL 16 also
adds a time-zone argument to the `timestamptz` form of `generate_series()`, which
is useful for calendar schedules across offset changes.

**Fallback below 16:** set a controlled session `TimeZone` for the transaction,
or convert explicitly with `AT TIME ZONE` and test daylight-saving boundaries.

[Official date/time documentation](https://www.postgresql.org/docs/16/functions-datetime.html)

## `COPY FROM` default-value sentinels

**Use when:** an input field must request the destination column's default rather
than supply a literal value or SQL null.

```sql
copy imported_users (user_id, created_at, status)
from stdin
with (format csv, default '\D');
```

Each unambiguous input field equal to the configured sentinel uses that column's
default. The option is for `COPY FROM` text/CSV input, not binary input. Choose a
sentinel that cannot collide with real data.

**Fallback below 16:** preprocess the file, omit defaulted columns in separate
loads, or load into text staging columns and transform with `INSERT`.

[Official `COPY` documentation](https://www.postgresql.org/docs/16/sql-copy.html)

## Generic prepared-statement plans

**Use when:** diagnosing the parameter-independent plan a prepared query may use,
without selecting arbitrary parameter values.

```sql
explain (generic_plan)
select *
from orders
where tenant_id = $1 and status = $2;
```

`GENERIC_PLAN` permits parameter placeholders but cannot be combined with
`ANALYZE`, because there are no concrete values to execute.

**Fallback below 16:** `PREPARE` the statement and compare `EXPLAIN EXECUTE`
across representative values, while accounting for custom-versus-generic plan
selection.

[Official `EXPLAIN` documentation](https://www.postgresql.org/docs/16/sql-explain.html)

## Cluster I/O diagnostics

**Use when:** distinguishing relation, temporary, WAL, and other I/O by backend
type and operation context.

```sql
select
  backend_type,
  object,
  context,
  reads,
  read_time,
  writes,
  write_time,
  fsyncs,
  fsync_time
from pg_stat_io
order by backend_type, object, context;
```

Counters are cumulative and need rates or before/after deltas for workload
analysis. Timing columns depend on the relevant tracking settings, and a zero
counter is not automatically proof of an I/O problem or absence.

**Fallback below 16:** combine `pg_stat_database`, `pg_stat_bgwriter`, relation
statistics, `EXPLAIN (ANALYZE, BUFFERS)`, and operating-system telemetry.

[Official monitoring documentation](https://www.postgresql.org/docs/16/monitoring-stats.html#MONITORING-PG-STAT-IO-VIEW)

## Independent role-membership options

**Use when:** privilege inheritance, `SET ROLE`, and membership administration
must be granted independently.

```sql
grant reporting to app_user
with inherit true, set false, admin false;
```

`INHERIT` controls immediate use of the granted role's ordinary privileges,
`SET` controls whether the member can become that role, and `ADMIN` controls
whether it can manage memberships. Model object ownership carefully: inherited
privileges without `SET` do not make unsafe ownership arrangements harmless.

**Fallback below 16:** separate login, group, and owner roles more strictly and
use the older aggregate membership semantics.

[Official role-membership documentation](https://www.postgresql.org/docs/16/role-membership.html)

## Custom ICU collation rules

**Use when:** an ICU-backed collation needs application-specific tailoring that
cannot be expressed by a locale tag alone.

```sql
create collation custom_sort (
  provider = icu,
  locale = 'und',
  rules = '&V << w <<< W'
);
```

This requires an ICU-enabled server. Collation rules and ICU versions can affect
indexes and ordering across upgrades, so record the intended behavior and test
version drift before rebuilding or migrating.

**Fallback below 16:** use an existing ICU locale/collation or store an explicit
normalized sort key maintained by the application.

[Official `CREATE COLLATION` documentation](https://www.postgresql.org/docs/16/sql-createcollation.html)

## Standby logical decoding and parallel apply

**Use when:** decoding should move to a standby or a subscriber must apply a
large streamed transaction with parallel workers.

PG16 permits logical decoding on standbys; `pg_log_standby_snapshot()` can
write the snapshot WAL record needed before slot creation. Subscriptions can
request parallel application with `STREAMING = parallel`, bounded by
`max_parallel_apply_workers_per_subscription`.

Standby slots still depend on physical WAL retention and invalidation rules.
Parallel apply changes concurrency and resource use, not commit ordering or the
need for replica identity and conflict handling.

[Official PostgreSQL 16 logical replication notes](https://www.postgresql.org/docs/16/release-16.html)

## Regex and included authentication rules

**Use when:** large `pg_hba.conf` or `pg_ident.conf` policies need named file
fragments or pattern-based database and role matching.

PG16 adds leading-slash regular expressions and `include`,
`include_if_exists`, and `include_dir`. Quote literal names that begin with a
slash. Validate parsed rules through `pg_hba_file_rules` and
`pg_ident_file_mappings` before reloading, and preserve first-match ordering
across included files.

**Fallback below 16:** enumerate explicit names and generate one reviewed,
deterministically ordered configuration file.

[Official client-authentication documentation](https://www.postgresql.org/docs/16/client-authentication.html)

## Readable numeric literals

**Use when:** bit masks, protocol constants, or large numeric constants are
clearer in non-decimal notation or with separators.

```sql
select 0x2a, 0o52, 0b101010, 1_000_000;
```

Hexadecimal, octal, and binary integer literals and underscores between digits
arrive in PG16. Keep migration generators and SQL parsers version-aware; these
forms are less portable than plain decimal literals.

**Fallback below 16:** use ordinary decimal constants or an explicit cast from
a validated string.

[Official PostgreSQL 16 lexical syntax](https://www.postgresql.org/docs/16/sql-syntax-lexical.html)

## COPY throughput changes

**Use when:** reassessing ingestion sizing after a PG16 upgrade.

PG16 reduces several `COPY FROM` CPU and allocation costs, while foreign-table
inserts can batch rows through a wrapper-specific `batch_size`. The core speedup
does not change durability, trigger, constraint, WAL, or error semantics.
Benchmark the actual format, row width, indexes, and storage path before
changing batch or concurrency limits.

[Official PostgreSQL 16 release notes](https://www.postgresql.org/docs/16/release-16.html)
