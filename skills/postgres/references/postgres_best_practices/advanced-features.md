# Advanced Features Best Practices

These features are high leverage when used with the right workload shape.

## 1) Use native full-text search for linguistic queries
For document search, prefer `tsvector` + GIN over wildcard `LIKE` scans.

```sql
alter table articles
add column search_vector tsvector
generated always as (
  to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
) stored;

create index articles_search_idx on articles using gin (search_vector);
```

## 2) Use JSONB with the right index strategy
Use GIN for containment/existence, and expression indexes for scalar path filters. Avoid `jsonb_column::text LIKE ...` for structured searches; it bypasses JSON semantics and usually prevents useful index use.

```sql
create index products_attrs_gin_idx on products using gin (attributes);
create index products_brand_expr_idx on products ((attributes ->> 'brand'));

select id
from products
where attributes @> '{"color": "red"}';
```

When a JSONB document needs required keys or value types, add a `CHECK` constraint instead of relying only on application validation.

```sql
alter table products
add constraint products_attrs_shape_check
check (
  jsonb_typeof(attributes) = 'object'
  and attributes ? 'brand'
);
```

## 3) Use arrays for bounded attributes, not relationships
Arrays work well for small bounded lists that are queried as a unit. Use operators such as `@>` for containment and `&&` for overlap, and pair frequent containment/overlap predicates with a GIN index. Use a junction table when array elements need their own metadata or constraints.

```sql
create index posts_tags_gin_idx on posts using gin (tags);

select id
from posts
where tags @> array['postgres'];
```

## 4) Use trigram indexes for fuzzy/wildcard text search
`pg_trgm` can accelerate `ILIKE '%term%'` and similarity search.

```sql
create extension if not exists pg_trgm;
create index users_email_trgm_idx on users using gin (email gin_trgm_ops);
```

## 5) Use range types + exclusion constraints for overlap rules
For scheduling and booking, enforce non-overlap at the database level. When a GiST exclusion constraint mixes range operators with scalar equality (for example `room_id with =`), install `btree_gist` so the scalar column has a compatible operator class.

```sql
create extension if not exists btree_gist;

create table room_bookings (
  room_id bigint not null,
  during tstzrange not null,
  exclude using gist (room_id with =, during with &&)
);
```

## 6) Use generated columns or expression indexes for computed predicates
Persist or index deterministic expressions used often in filters.

```sql
create index users_lower_email_idx on users (lower(email));
```

## 7) Review PL/pgSQL functions and triggers for hidden work
Database functions and triggers can centralize invariants, but they can also hide row-by-row work. Keep trigger predicates narrow with `WHEN`, avoid unnecessary per-row queries, handle exceptions deliberately, and measure function-heavy paths with normal query diagnostics.

```sql
create trigger orders_touch_updated_at
before update on orders
for each row
when (old.* is distinct from new.*)
execute function set_updated_at();
```

## 8) Manage extensions deliberately
Install extensions in migrations, verify they are available in the target environment, and document why each extension is needed. Prefer built-in capabilities when they satisfy the requirement, and avoid adding extensions only for one-off convenience.

## Verification References
- https://www.postgresql.org/docs/current/textsearch-intro.html
- https://www.postgresql.org/docs/current/datatype-json.html#JSON-INDEXING
- https://www.postgresql.org/docs/current/functions-json.html
- https://www.postgresql.org/docs/current/arrays.html
- https://www.postgresql.org/docs/current/functions-array.html
- https://www.postgresql.org/docs/current/pgtrgm.html
- https://www.postgresql.org/docs/current/rangetypes.html
- https://www.postgresql.org/docs/current/btree-gist.html
- https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-EXCLUSION
- https://www.postgresql.org/docs/current/ddl-generated-columns.html
- https://www.postgresql.org/docs/current/indexes-expressional.html
- https://www.postgresql.org/docs/current/plpgsql-trigger.html
- https://www.postgresql.org/docs/current/sql-createextension.html
