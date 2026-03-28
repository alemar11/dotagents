# Postgres Skill Environment Variables

Prefer the `DB_*` variables below when invoking this skill directly. The runtime
also accepts common compatibility inputs for connection setup so it can work
cleanly in existing Postgres-oriented environments.

## Preferred runtime variables
- `DB_URL`
- `DB_PROFILE`
- `DB_PROJECT_ROOT`
- `DB_PYTHON_BIN`
- `DB_APPLICATION_NAME`
- `DB_STATEMENT_TIMEOUT_MS`
- `DB_LOCK_TIMEOUT_MS`
- `DB_AUTO_UPDATE_SSLMODE`
- `DB_RESOLVE_CACHE`
- `DB_RESOLVE_CACHE_MAX_ENTRIES`
- `DB_GITIGNORE_CHECK`
- `DB_SSL_RETRY`
- `DB_QUERY_TEXT_MAX_CHARS`
- `DB_TABLE_SIZES_SCHEMA`
- `DB_TABLE_SIZES_MIN_BYTES`
- `DB_FIND_OBJECT_TYPES`
- `DB_PROFILE_SCAN_MODE`
- `DB_CONFIRM`
- `DB_VIEW_DEF_TRUNC`
- `DB_FUNC_DEF_TRUNC`
- `DB_PROFILE_A`
- `DB_PROFILE_B`
- `DB_URL_A`
- `DB_URL_B`
- `DB_DOCS_SEARCH_URL`
- `DB_DOCS_SEARCH_MAX_TIME`

## Compatibility connection inputs
These are accepted as compatibility inputs when `DB_URL` is not set:
- URL aliases: `DATABASE_URL`, `POSTGRES_URL`, `POSTGRESQL_URL`
- libpq env vars: `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGSSLMODE`
- split DB fields: `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

## Project metadata keys
These are not runtime environment variables:
- `DB_MIGRATIONS_PATH` is resolved from project `AGENTS.md` guidance, not from the shell environment.

## Internal bridge variables
The skill may set PostgreSQL-native variables internally when invoking Postgres tools:
- `PGAPPNAME` (from `DB_APPLICATION_NAME`)
- `PGOPTIONS` (from timeout settings)

Do not set these as part of the public skill configuration contract unless you
are intentionally bypassing the skill.

## Still unsupported aliases
- `PROJECT_ROOT` -> `DB_PROJECT_ROOT`
- `PG_DOCS_SEARCH_URL` -> `DB_DOCS_SEARCH_URL`
- `PG_DOCS_SEARCH_MAX_TIME` -> `DB_DOCS_SEARCH_MAX_TIME`
