# Postgres common workflows

This reference is a copy/paste playbook for the shipped `scripts/postgres`
launcher. Keep it generic (no repo-specific IDs, schemas, or secrets).

Assume:

- `POSTGRES_CLI=/path/to/postgres-skill/scripts/postgres`
- `DB_PROJECT_ROOT=/path/to/repo`
- `DB_PROFILE=local` (or whatever the repo uses)

## Rule of thumb: CLI subcommands vs raw SQL

- Prefer CLI subcommands when they exist (`query find`, `schema inspect`, `schema list ...`, `activity ...`).
- Prefer raw SQL (`query run`) for:
  - catalog queries or bespoke joins
  - multi-step verification queries after DDL
  - “show me exactly these columns/rows” ad-hoc work
- Prefer `query run` heredocs for multi-statement SQL or anything involving `DO $$`.

## Find enum + values

### 1) Find candidate enum types by name

```bash
DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" query find status --types table,column
```

If you already know the enum type name, skip to SQL below.

### 2) List enum labels (SQL)

```bash
DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" query run <<'SQL'
SELECT
  n.nspname AS schema_name,
  t.typname AS enum_name,
  e.enumsortorder AS sort_order,
  e.enumlabel AS value
FROM pg_type t
JOIN pg_enum e ON e.enumtypid = t.oid
JOIN pg_namespace n ON n.oid = t.typnamespace
WHERE t.typname = 'your_enum_type_name'
ORDER BY e.enumsortorder;
SQL
```

### 3) Find where an enum is used

```bash
DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" query run <<'SQL'
SELECT
  n.nspname AS table_schema,
  c.relname AS table_name,
  a.attname AS column_name
FROM pg_attribute a
JOIN pg_class c ON c.oid = a.attrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_type t ON t.oid = a.atttypid
WHERE a.attnum > 0
  AND NOT a.attisdropped
  AND t.typname = 'your_enum_type_name'
ORDER BY 1,2,3;
SQL
```

## Find table/column/function by name

### Quick fuzzy search (CLI)

```bash
DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" query find users --types table,column,view,function
```

### Catalog search (SQL)

```bash
DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" query run <<'SQL'
SELECT 'table' AS kind, table_schema AS schema, table_name AS name
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
  AND table_name ILIKE '%user%'
UNION ALL
SELECT 'column' AS kind, table_schema AS schema, table_name || '.' || column_name AS name
FROM information_schema.columns
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
  AND (table_name ILIKE '%user%' OR column_name ILIKE '%user%')
ORDER BY 1,2,3;
SQL
```

## Show table definition + indexes

### Columns (SQL)

```bash
DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" query run <<'SQL'
SELECT
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'your_table'
ORDER BY ordinal_position;
SQL
```

### Indexes (SQL)

```bash
DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" query run <<'SQL'
SELECT
  indexname,
  indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'your_table'
ORDER BY indexname;
SQL
```

If you want to stay on the CLI surface, prefer:

```bash
DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" schema inspect
DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" schema list indexes
```

## Which DB am I connected to?

Prefer the JSON contract:

```bash
DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" --json profile resolve
```

Or run a quick identity query:

```bash
DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" query run -c \
  "select current_database() as db, current_user as user, inet_server_addr() as host, inet_server_port() as port;"
```

## Quick lookup query template (safe)

Prefer a heredoc so the SQL is visible and auditable:

```bash
DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" query run <<'SQL'
SELECT id, created_at
FROM public.your_table
WHERE id = 123
LIMIT 50;
SQL
```

If you need to verify something changed after DDL, include the verification
query in the same heredoc (or run it immediately after) so the transcript proves
the result.
