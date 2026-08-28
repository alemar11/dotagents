# Data Access Pattern Best Practices

These patterns improve throughput and reduce avoidable database work.

## 1) Batch writes instead of row-at-a-time loops
Use multi-row `INSERT` or `COPY` for bulk ingestion.

```sql
insert into events (user_id, action)
values (1, 'click'), (1, 'view'), (2, 'click');
```

## 2) Use `ON CONFLICT` for atomic upserts
Replace check-then-insert/update races with a single SQL statement.

```sql
insert into settings (user_id, key, value)
values (123, 'theme', 'dark')
on conflict (user_id, key)
do update set value = excluded.value;
```

## 3) Prefer keyset pagination for deep paging
`OFFSET` cost grows with page depth; keyset/cursor pagination remains stable. Order by a stable unique key (or compound key with a unique tiebreaker) and build the index in the same column order.

```sql
select * from products
where (created_at, id) > ($1, $2)
order by created_at, id
limit 50;
```

## 4) Avoid N+1 query patterns
Join or batch related lookups rather than issuing one query per row at the application layer.

```sql
select u.id, u.name, o.total
from users u
left join orders o on o.user_id = u.id
where u.active = true;
```

## 5) Use parameterized queries/prepared statements
Parameterized SQL improves safety and can reduce parse/plan overhead for repeated query shapes.

## 6) Use `RETURNING` to avoid extra round trips
When a write needs to return generated IDs or updated values, use `RETURNING` in the same statement.

```sql
insert into orders (customer_id, total)
values ($1, $2)
returning id, created_at;
```

## 7) Keep exploratory reads bounded
Avoid unbounded `SELECT *` in application paths and ad-hoc inspection. Project only the columns needed and use a deterministic `ORDER BY` with a practical `LIMIT`.

```sql
select id, created_at, status
from orders
where created_at >= now() - interval '7 days'
order by created_at desc, id desc
limit 100;
```

## 8) Keep predicates index-friendly
Prefer predicates that let the planner use indexes directly. Avoid wrapping indexed columns in functions unless the same expression is indexed.

```sql
-- Better than date(created_at) = current_date for a plain created_at index:
select id
from events
where created_at >= current_date
  and created_at < current_date + interval '1 day';
```

## 9) Prefer `UNION ALL` and `EXISTS` when semantics allow
Use `UNION ALL` when duplicate removal is not required, and use `EXISTS` for existence checks that do not need row materialization.

```sql
select id from invoices where status = 'open'
union all
select id from invoices where status = 'overdue';

select 1
from orders o
where exists (
  select 1
  from order_items i
  where i.order_id = o.id
);
```

## 10) Shape tables for write-heavy workloads
For high-ingest tables, keep secondary indexes minimal, batch writes, and use `COPY` when loading large files.

For update-heavy tables, avoid repeatedly updating indexed columns, keep transactions short, and consider table-specific `fillfactor` only after measuring page churn and HOT update behavior.

## 11) Use `UNLOGGED` only for disposable caches and staging data
An `UNLOGGED` table skips write-ahead logging for its data and indexes, which
can reduce write cost for a write-heavy cache. The tradeoff is a hard
durability boundary: PostgreSQL truncates it after a crash or unclean shutdown,
and its contents are not replicated to standby servers. Treat it as empty after
crash recovery or standby promotion even if clean restarts usually preserve its
contents.

Use `UNLOGGED` only when all of these are true:

- a durable source of truth exists outside the table
- a cache miss can rebuild the value without changing business semantics
- startup and failover remain correct while the cache is empty or warming
- expiry or cleanup bounds table and index growth
- monitoring distinguishes expected cache loss from a failed rebuild

Do not use it for sessions, authentication state, security rate limits,
idempotency keys, locks, queues, or the only copy of business data. Prefer a
regular table when cache contents must survive failover, and a temporary table
when the data is private to one session.

```sql
create unlogged table rendered_page_cache (
  cache_key text primary key,
  payload jsonb not null,
  source_version text not null,
  expires_at timestamptz not null
);

create index rendered_page_cache_expires_at_idx
on rendered_page_cache (expires_at);
```

Make the read path treat a missing or expired row as a normal cache miss. Keep
the rebuild idempotent, upsert by the stable cache key, and run bounded expiry
deletes. Do not route standby reads to this cache because standby contents are
not maintained.

## Verification References
- https://www.postgresql.org/docs/current/sql-copy.html
- https://www.postgresql.org/docs/current/sql-insert.html
- https://www.postgresql.org/docs/current/queries-limit.html
- https://www.postgresql.org/docs/current/indexes-multicolumn.html
- https://www.postgresql.org/docs/current/sql-prepare.html
- https://www.postgresql.org/docs/current/dml-returning.html
- https://www.postgresql.org/docs/current/indexes-expressional.html
- https://www.postgresql.org/docs/current/queries-union.html
- https://www.postgresql.org/docs/current/sql-createtable.html#SQL-CREATETABLE-UNLOGGED
- https://www.postgresql.org/docs/current/storage-hot.html
