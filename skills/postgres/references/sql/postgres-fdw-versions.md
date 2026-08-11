# PostgreSQL 14–19 Foreign-Data Capability Guide

Use this reference when a task involves foreign tables, `postgres_fdw`,
`file_fdw`, remote pushdown, foreign-server connections, or subscriptions that
reuse foreign-server connection data. These capabilities mix core SQL with
bundled extensions, so verify both the server major and installed extension.

## Contents

- [PostgreSQL 14](#postgresql-14)
- [PostgreSQL 15](#postgresql-15)
- [PostgreSQL 16](#postgresql-16)
- [PostgreSQL 17](#postgresql-17)
- [PostgreSQL 18](#postgresql-18)
- [PostgreSQL 19 preview](#postgresql-19-preview)
- [Review checklist](#review-checklist)

## PostgreSQL 14

**Use when:** federated scans or writes need better concurrency, throughput, or
connection control.

- Foreign scans under an append can run concurrently when the wrapper supports
  asynchronous execution; `postgres_fdw` opts in with `async_capable`.
- `postgres_fdw` can batch inserts.
- `IMPORT FOREIGN SCHEMA ... LIMIT TO` can import named partitions rather than
  only the partitioned root.
- `postgres_fdw_get_connections()`, `keep_connections`, reconnect handling,
  and cache-discard functions expose and control pooled remote connections.

Async scans change remote load and completion order, while batching changes the
failure unit. Set timeouts on both sides and reconcile partial remote effects.

[Official PostgreSQL 14 release notes](https://www.postgresql.org/docs/14/release-14.html)

## PostgreSQL 15

**Use when:** remote expressions or distributed transaction completion should
move less work through the local server.

- `postgres_fdw` can push down `CASE` expressions.
- `postgres_fdw.application_name` labels remote sessions consistently.
- The `parallel_commit` server option allows commits on multiple foreign
  servers to proceed in parallel.
- Parallel foreign scans are available in more plans.

Pushdown is a planner decision, not a guarantee. Verify with `EXPLAIN (VERBOSE)`
and keep remote collations, functions, and transaction semantics compatible.

[Official PostgreSQL 15 release notes](https://www.postgresql.org/docs/15/release-15.html)

## PostgreSQL 16

**Use when:** bulk ingestion, remote analysis, or multi-server abort latency is
material.

- `COPY` into a foreign table can use the `postgres_fdw` `batch_size` option.
- `parallel_abort` allows remote transaction aborts to run concurrently.
- `analyze_sampling` selects a more efficient foreign-table sampling method.
- Foreign tables can own truncate triggers.
- Shipping of `reg*` constants is restricted to built-in or explicitly
  shippable extension objects.

Batch size trades round trips for larger failure and memory units. Remote
statistics can still drift; compare local estimates with remote reality.

[Official PostgreSQL 16 release notes](https://www.postgresql.org/docs/16/release-16.html)

## PostgreSQL 17

**Use when:** correlated filters and joins should execute remotely or an
upgrade changes foreign-plan selection.

- `postgres_fdw` can push down `EXISTS` and `IN` subqueries.
- Joins with non-join qualifications can be pushed to capable foreign wrappers
  and custom scans.
- The default foreign tuple cost increased, which can change local-versus-
  remote planner choices after upgrade.
- Extensions can expose custom wait events; `postgres_fdw` uses them.

Re-baseline representative plans after upgrade. A semantically valid pushdown
can still be slower when the remote side lacks indexes or has stale statistics.

[Official PostgreSQL 17 release notes](https://www.postgresql.org/docs/17/release-17.html)

## PostgreSQL 18

**Use when:** foreign-table definitions, authentication, ingestion tolerance,
or connection diagnostics need stronger core support.

- `CREATE FOREIGN TABLE (... LIKE source ...)` can copy a local relation shape.
- `postgres_fdw` supports SCRAM credential pass-through with
  `use_scram_passthrough`, avoiding stored remote passwords.
- `postgres_fdw_get_connections()` reports transaction use, closure, remote
  user, and remote backend PID.
- `file_fdw` adds `on_error`, `log_verbosity`, and `reject_limit` for bounded
  invalid-row handling.

Copied constraints are declarations that PostgreSQL generally assumes true;
ensure the remote source really satisfies them. SCRAM pass-through requires
compatible client, local server, and remote server configuration.

[Official PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html)

## PostgreSQL 19 preview

**Use when:** evaluating PostgreSQL 19 federated planning or subscription
connection reuse. Recheck every item against the exact beta or release build.

- Local `READ ONLY` and `DEFERRABLE` transaction state propagates to
  `postgres_fdw` sessions.
- `CREATE FOREIGN DATA WRAPPER ... CONNECTION` can provide subscription
  connection parameters, and `CREATE SUBSCRIPTION ... SERVER` can reference a
  foreign server.
- Prepared-statement array comparisons can be pushed to `postgres_fdw`.
- Foreign wrappers can retrieve remote statistics; `postgres_fdw` enables this
  with `restore_stats`.
- `file_fdw` can process multi-line headers.

The transaction-state change is a compatibility boundary: a read-only local
transaction can no longer mutate a remote table through `postgres_fdw`.
Treat subscription connection indirection as secret-bearing configuration and
review ownership and user mappings before adoption.

[Official PostgreSQL 19 release notes](https://www.postgresql.org/docs/19/release-19.html)

## Review checklist

- Confirm core major, wrapper extension version, and remote server version.
- Inspect user mappings without exposing credentials.
- Use `EXPLAIN (VERBOSE)` to confirm actual pushdown.
- Bound connect, statement, and transaction timeouts locally and remotely.
- Re-test plans after upgrades or statistics changes.
- Account for remote transaction, batching, retry, and partial-failure units.
- Verify collation, type, function, and constraint semantics on both sides.
