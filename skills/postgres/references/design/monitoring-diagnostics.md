# Monitoring and Diagnostics Best Practices

Use these checks continuously in production, not only during incidents.

## 1) Start with `EXPLAIN (ANALYZE, BUFFERS)`
Use measured execution plans to diagnose slow SQL before changing indexes/config.

```sql
explain (analyze, buffers)
select * from orders where customer_id = 123 and status = 'pending';
```

## 2) Track workload with `pg_stat_statements`
Identify expensive/frequent query fingerprints and prioritize by total impact. The module must be preloaded and query identifiers enabled before `CREATE EXTENSION` is enough.

```sql
-- ensure shared_preload_libraries includes 'pg_stat_statements'
-- and compute_query_id is enabled, then restart if required:
create extension if not exists pg_stat_statements;

select query, calls, mean_exec_time, total_exec_time
from pg_stat_statements
order by total_exec_time desc
limit 20;
```

## 3) Monitor autovacuum/analyze health
Watch stale stats and dead tuples to avoid planner drift and table bloat.

```sql
select relname, n_live_tup, n_dead_tup, last_autovacuum, last_autoanalyze
from pg_stat_user_tables
order by n_dead_tup desc;
```

## 4) Inspect lock and activity views
Find long transactions, blocked sessions, and lock chains early.

```sql
select pid, state, wait_event_type, wait_event, now() - xact_start as xact_age
from pg_stat_activity
where state <> 'idle';
```

## 5) Review index usage and churn periodically
Remove unused indexes and validate index effectiveness over time. Always confirm with workload knowledge before dropping an index; a rarely used index can still protect an important monthly, incident, or constraint path.

```sql
select schemaname, relname as table_name, indexrelname as index_name, idx_scan
from pg_stat_user_indexes
order by idx_scan asc;
```

Check invalid indexes separately; these often come from failed concurrent builds and should be repaired intentionally.

```sql
select
  n.nspname as schema_name,
  c.relname as index_name,
  t.relname as table_name
from pg_index i
join pg_class c on c.oid = i.indexrelid
join pg_class t on t.oid = i.indrelid
join pg_namespace n on n.oid = c.relnamespace
where not i.indisvalid
order by 1, 2;
```

## 6) Run focused smell checks before changing schema
Use small catalog queries to identify likely problems, then inspect the query workload before changing DDL.

Find long transactions:

```sql
select pid, state, now() - xact_start as xact_age, wait_event_type, wait_event
from pg_stat_activity
where xact_start is not null
order by xact_age desc
limit 20;
```

Find tables with dead-tuple pressure:

```sql
select relname, n_live_tup, n_dead_tup, last_autovacuum, last_autoanalyze
from pg_stat_user_tables
where n_dead_tup > 0
order by n_dead_tup desc
limit 20;
```

Find large relations for growth review:

```sql
select
  n.nspname as schema_name,
  c.relname as relation_name,
  pg_size_pretty(pg_total_relation_size(c.oid)) as total_size
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname not in ('pg_catalog', 'information_schema')
  and c.relkind in ('r', 'm', 'p')
order by pg_total_relation_size(c.oid) desc
limit 20;
```

Find foreign keys that may need indexing:

```sql
select c.conrelid::regclass as table_name, c.conname, pg_get_constraintdef(c.oid)
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

## 7) Treat stats resets as operational events
`pg_stat_*` views are cumulative since the last reset. Record the reset time before interpreting low usage counts, and avoid resetting stats during an incident unless everyone depending on those counters agrees.

```sql
select stats_reset
from pg_stat_database
where datname = current_database();
```

## 8) Enable slow-query and lock-wait logging
Capture slow SQL and lock waits in logs so intermittent production issues are diagnosable. `ALTER SYSTEM` is a privileged, cluster-level change, so use it only when you actually manage cluster-wide settings; otherwise apply the equivalent settings through your platform/config-management path.

```sql
alter system set log_min_duration_statement = '250ms';
alter system set log_lock_waits = on;
alter system set deadlock_timeout = '200ms';
select pg_reload_conf();
```

## Verification References
- https://www.postgresql.org/docs/current/using-explain.html
- https://www.postgresql.org/docs/current/pgstatstatements.html
- https://www.postgresql.org/docs/current/routine-vacuuming.html
- https://www.postgresql.org/docs/current/monitoring-stats.html
- https://www.postgresql.org/docs/current/monitoring-locks.html
- https://www.postgresql.org/docs/current/runtime-config-statistics.html
- https://www.postgresql.org/docs/current/runtime-config-logging.html
- https://www.postgresql.org/docs/current/runtime-config-locks.html
- https://www.postgresql.org/docs/current/functions-admin.html#FUNCTIONS-ADMIN-DBSIZE
