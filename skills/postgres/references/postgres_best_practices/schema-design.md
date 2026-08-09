# Schema Design Best Practices

These rules prioritize correctness first, then predictable performance.

## 1) Normalize first, denormalize from evidence
Start with normalized tables that preserve one fact in one place and enforce relationships declaratively. Denormalize only after measured query evidence shows the read path needs it, and keep constraints or refresh logic that protect the duplicated data from drift.

## 2) Encode business invariants in constraints
Use `NOT NULL`, `CHECK`, `UNIQUE`, foreign keys, and exclusion constraints where applicable. Remember that `CHECK` evaluates to true for `NULL`, so pair it with `NOT NULL` when the value must be present.

```sql
create table products (
  id bigint generated always as identity primary key,
  sku text not null unique,
  price numeric(10,2) not null check (price >= 0)
);
```

On PostgreSQL 15+, if a nullable column still needs true uniqueness, use
`NULLS NOT DISTINCT`. For older targets, use the fallback in
[`postgres-sql-15.md`](../postgres-sql-15.md#unique-null-values-with-nulls-not-distinct).

```sql
create table external_accounts (
  id bigint generated always as identity primary key,
  external_ref text unique nulls not distinct
);
```

## 3) Choose primary keys deliberately
- Use identity keys for simple single-cluster write paths.
- Prefer identity columns over `serial`.
- Use UUIDs when externally visible/global uniqueness is required.
- Treat gaps in identity sequences as normal; never encode business meaning in sequence continuity.

```sql
create table users (
  id bigint generated always as identity primary key
);
```

## 4) Use semantically correct data types
- `timestamptz` for real-world timestamps; avoid `timestamp without time zone` unless the value is intentionally timezone-free.
- `numeric` for exact currency/financial math.
- `text` by default for strings; add an explicit length check when the limit is part of the domain.
- `citext` (when the extension is available) or a unique expression index on `lower(value)` for case-insensitive identity fields.
- `jsonb` for semi-structured payloads you query, with `CHECK` constraints when specific keys or value types are required.
- Enums for stable, small value sets; lookup tables when values need metadata, localization, soft deletes, or runtime changes; checks for simple per-column predicates.
- Domains for reusable scalar constraints that should be consistent across tables.
- Arrays for small bounded attributes queried as a unit; use a junction table when elements need their own attributes, constraints, or relationships.

```sql
create table customer_profiles (
  id bigint generated always as identity primary key,
  display_name text not null check (length(display_name) <= 120),
  created_at timestamptz not null default now(),
  settings jsonb not null default '{}'
);
```

## 5) Index foreign key columns explicitly
PostgreSQL enforces the FK but does not auto-create the referencing index.

```sql
create table orders (
  id bigint generated always as identity primary key,
  customer_id bigint not null references customers(id)
);

create index orders_customer_id_idx on orders (customer_id);
```

To find referencing foreign-key columns that are not covered by a simple index, start with a catalog check and review each candidate manually before adding indexes:

```sql
select
  c.conrelid::regclass as table_name,
  c.conname as constraint_name,
  pg_get_constraintdef(c.oid) as constraint_definition
from pg_constraint c
where c.contype = 'f'
  and not exists (
    select 1
    from pg_index i
    where i.indrelid = c.conrelid
      and i.indisvalid
      and i.indpred is null
      and (
        select bool_and(i.indkey[ord - 1] = c.conkey[ord])
        from generate_subscripts(c.conkey, 1) as ord
      )
  )
order by 1, 2;
```

## 6) Use generated columns or expression indexes for repeated computed predicates
Persist or index deterministic computed values that appear frequently in filters or joins.

```sql
alter table users
add column email_domain text
generated always as (split_part(lower(email), '@', 2)) stored;

create index users_email_domain_idx on users (email_domain);
```

## 7) Use partitioning only when justified
Partition for large tables with clear partition-key filters and lifecycle operations (retention, archival, fast drops).

```sql
create table events (
  id bigint generated always as identity,
  created_at timestamptz not null,
  payload jsonb not null
) partition by range (created_at);
```

Confirm destructive partition actions before running them. Detaching or dropping a partition is operationally useful for retention, but it can remove large slices of data quickly.

## 8) Keep naming conventions stable
Unquoted lowercase identifiers avoid case-sensitivity surprises across tools and SQL clients.

## 9) Account for PostgreSQL storage behavior
- A primary key does not cluster heap storage by default; use indexes and query plans rather than assuming physical row order.
- Updates and deletes leave dead tuples until vacuum can reclaim them; update-heavy tables need monitoring, short transactions, and enough autovacuum headroom.
- Updating indexed columns can prevent HOT updates and increase index churn; separate frequently updated columns from wide or heavily indexed data when that shape is stable.

## Verification References
- https://www.postgresql.org/docs/current/ddl-constraints.html
- https://www.postgresql.org/docs/current/sql-createtable.html
- https://www.postgresql.org/docs/current/datatype.html
- https://www.postgresql.org/docs/current/citext.html
- https://www.postgresql.org/docs/current/extend-type-system.html
- https://www.postgresql.org/docs/current/ddl-generated-columns.html
- https://www.postgresql.org/docs/current/indexes-expressional.html
- https://www.postgresql.org/docs/current/ddl-partitioning.html
- https://www.postgresql.org/docs/current/storage.html
- https://www.postgresql.org/docs/current/routine-vacuuming.html
