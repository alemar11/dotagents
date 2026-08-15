---
name: postgres
description: Connect to Postgres, run SQL/diagnostics, inspect schemas/migrations, and apply version-aware SQL, PostGIS, pgvector, or pg_durable patterns.
---

# Postgres

## Goal

Use this skill to connect to Postgres, run SQL, inspect schemas, review query
performance, design tables and indexes, work with common PostGIS, pgvector, or
pg_durable patterns, select SQL supported by the target PostgreSQL major, and
manage migration release flow through the shipped
`scripts/postgres` launcher in the skill package.

## Runtime surface

- The only supported runtime entrypoint is the shipped `scripts/postgres`
  launcher inside this skill package.
- If your current working directory is the skill root, run it as
  `./scripts/postgres`.
- If you are invoking the skill from another repo, resolve the skill package
  path first and run `<postgres-skill-root>/scripts/postgres`.
- `<postgres-skill-root>/scripts/postgres --version` is the runtime version
  check.
- Runtime model, platform binary, and maintenance implementation details live
  in `references/runtime/usage.md`.
- Load `references/runtime/options.md` before reading or reporting
  behavior-affecting config choices.
- Load `references/states.md` before interpreting migration lifecycle or
  derived command outcomes.
- Canonical persisted config lives at `<project-root>/.skills/postgres/config.toml`.
- Ordinary runtime commands read and normalize config only in memory. Use
  `profile migrate-config`, `profile bootstrap --save`,
  `profile set-ssl-mode`, or the documented
  `DB_AUTO_UPDATE_SSL_MODE=1` opt-in when a config write is intended.
- Profile `access_mode` values `read`, `write`, and `read-write` are local CLI
  safety guards; they do not replace PostgreSQL roles, grants, RLS, or
  server-side read-only settings.
- This runtime skill does not provide dump, restore, export, or schema-diff
  workflows. Keep those operator tasks outside this skill.
- If a target repo has `.skills/postgres/config.toml` or legacy
  `.skills/postgres/postgres.toml`, use the shipped `scripts/postgres`
  launcher for normal app-database work instead of raw `psql`.
- Bare `psql` is allowed only as an explicit exception for container-local
  runbooks such as `docker compose exec pg psql ...`, repo-documented smoke
  checks, unsupported operator workflows outside this skill's runtime surface,
  or emergency fallback when the shipped launcher cannot run.

## Start here (minimal)

Common installed locations for the shipped runtime:

- `~/.agents/skills/postgres/scripts/postgres` (typical when this repo’s `skills/`
  are linked into `~/.agents/skills`)
- `<dotagents>/skills/postgres/scripts/postgres` (when running from this workspace checkout)

Resolve the shipped CLI once and reuse it:

- `POSTGRES_CLI=/path/to/postgres-skill/scripts/postgres`
- `DB_PROJECT_ROOT=/path/to/repo`
- Optional: `DB_PROFILE=local`

Minimal happy path:

- `DB_PROJECT_ROOT="$DB_PROJECT_ROOT" "$POSTGRES_CLI" --json doctor`
- `DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" profile test`
- `DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" query run -c "select now();"`

## Common workflows

Use `references/workflows/common-workflows.md` for copy/paste playbooks:

- enums (find type + values)
- find table/column/function by name
- show table shape + indexes
- confirm which DB you are connected to
- safe “quick lookup” templates

## Version-aware SQL

Before proposing syntax whose availability depends on the PostgreSQL major,
resolve the oldest deployed major and load
`references/sql/postgres-sql-versions.md`. Select the relevant capability route
and load only its linked guide sections. Do not load all per-version guides for
an ordinary SQL task.

Load a complete PostgreSQL 14–19 guide only for an explicit upgrade review,
broad release comparison, or targeted lookup of a feature omitted from the
high-impact router. Never load a guide newer than the target unless the caller
is considering that upgrade.

If the target major is unknown, prefer portable syntax or state the minimum
required major and a fallback. Treat PostgreSQL 19 release status as volatile:
verify the current official documentation and exact target build before using
its syntax or behavior.

## Guardrails (short)

- Before you run any non-trivial query, confirm the target:
  - `DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" --json profile resolve`
  - then run the identity query from
    `references/workflows/common-workflows.md` (“Which DB am I connected to?”).
- If the user says “production”, “prod”, “staging”, or “remote DB”:
  - stop and ask for the exact `DB_PROFILE` / `DB_URL` they intend
  - default to `access_mode=read` and require an explicit confirmation before any write/DDL
- Always ask for approval before DDL changes.
- Before editing or releasing a migration, load
  `references/workflows/migration-guardrails.md`; it owns pending-file
  selection, released-file immutability, release authorization, and
  verification.

## References

- Runtime command surface and JSON mode: `references/runtime/usage.md`
- Runtime option fields and compatibility aliases: `references/runtime/options.md`
- Migration lifecycle and derived outcomes: `references/states.md`
- Runtime environment contract: `references/runtime/environment.md`
- Runtime config schema: `references/runtime/config-schema.md`
- Common inspection workflows: `references/workflows/common-workflows.md`
- Migration guardrails: `references/workflows/migration-guardrails.md`
- Local and Docker recovery: `references/workflows/local-recovery.md`
- Broad design or migration review: load `references/design/README.md` for the
  first-pass checklist and select only the relevant detailed references.
- Schema and storage design: load `references/design/schema-design.md` for
  constraints, keys, data types, partitioning, naming, or storage layout.
- Query and access design: load `references/design/query-performance.md` for
  indexes and measured plans, and `references/design/data-access-patterns.md`
  for batching, upserts, pagination, query shape, or write-heavy workloads.
- Concurrency and connections: load `references/design/concurrency-locking.md`
  for transactions and locks, or `references/design/connection-management.md`
  for pooling, session behavior, memory, and connection timeouts.
- Security and diagnostics: load `references/design/security-rls.md` for roles,
  grants, or RLS, and `references/design/monitoring-diagnostics.md` for workload,
  vacuum, lock, activity, logging, or index diagnostics.
- Advanced built-in features: load `references/design/advanced-features.md`
  for full-text, JSONB, arrays, trigrams, ranges, generated expressions,
  PL/pgSQL, triggers, or extension-management tradeoffs.
- PostGIS guidance: load `references/extensions/postgis.md` only for spatial
  types, SRIDs, spatial predicates, or spatial-index tasks.
- pgvector guidance: load `references/extensions/pgvector.md` only for
  embeddings, vector indexes, similarity search, or retrieval tasks.
- pg_durable guidance: load `references/extensions/pg-durable.md` only for
  asynchronous workflow, retry, schedule, signal, or durable-job tasks.
- SQL capability router and version-selection rules:
  `references/sql/postgres-sql-versions.md`
- Foreign tables and FDW version changes: load
  `references/sql/postgres-fdw-versions.md` only for foreign-table,
  `postgres_fdw`, `file_fdw`, remote-pushdown, or FDW-backed subscription tasks.
- Optional PostgreSQL release catalogs: `references/sql/postgres-sql-14.md`
  through `references/sql/postgres-sql-19.md`; keep all majors in this one
  category.
