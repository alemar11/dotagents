# Postgres Schema Change Guardrails

Use this reference when designing, reviewing, or applying a PostgreSQL schema
change. Repository SQL-file layout, changelog format, migration-runner
selection, and release ordering belong to the consuming project or team. Follow
its documented instructions; if those instructions are absent or ambiguous, ask
instead of inferring conventions such as a prerelease file, `released/`
directory, timestamped filename, or changelog structure.

## Database-focused rules

- Resolve the configured project and profile, and verify database identity,
  before inspecting or changing a consequential target.
- Apply DDL only with authorization for that operation and target database.
  Preparing proposed SQL is separate from applying it.
- Inspect the live schema and relevant dependencies before destructive or
  compatibility-sensitive changes.
- Preserve the consuming project's migration-runner semantics, including
  transaction wrapping, statement splitting, retry behavior, and environment
  ordering.
- After an authorized schema change, run the least expensive authoritative query
  that proves the change landed.

## Schema evolution footguns

- `CREATE INDEX CONCURRENTLY` and `DROP INDEX CONCURRENTLY` cannot run inside a
  transaction block. If a migration runner wraps every statement in one
  transaction, use that project's documented non-transactional path or ask
  before proceeding.
- Adding a column with a volatile default can rewrite or lock more data than
  expected on large tables. Prefer staged changes when the table is large or
  latency-sensitive.
- Changing a function signature can create an overload rather than replacing
  the old function. Drop or replace the intended signature explicitly and
  verify call sites.
- Dropping indexes, constraints, columns, tables, or partitions is destructive.
  Confirm the target object and rollback path before applying the DDL.

## Verification references

- <https://www.postgresql.org/docs/current/sql-createindex.html>
- <https://www.postgresql.org/docs/current/sql-dropindex.html>
- <https://www.postgresql.org/docs/current/ddl-alter.html>
- <https://www.postgresql.org/docs/current/xfunc-overload.html>
