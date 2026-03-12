# Postgres Skill TOML Schema

This document describes all known `postgres.toml` schema versions for the postgres skill.

## Schema versioning rules
- `schema_version` is required in all new TOMLs.
- New TOMLs use semver strings such as `"1.1.0"`.
- Legacy integer `1` is treated as schema `1.0.0`.
- Missing `schema_version` is treated as pre-`1.0.0` and must be migrated.
- Any schema change must:
  - Bump `schema_version` in `assets/postgres.toml.example`.
  - Add a migration step for every prior supported version in `scripts/migrate_toml_schema.sh`.
  - Update this document with the new version details.

## Version `1.1.0` (current)
**Status:** current.

### Required
```toml
[configuration]
schema_version = "1.1.0"
pg_bin_dir = "/path/to/postgres/bin"
python_bin = "/path/to/python3.14"
```

### Defaults / base tables
```toml
[database]
sslmode = false
```

### Profiles
Profiles live under `[database.<profile>]`.

Required fields:
- `host`
- `port`
- `database`
- `user`
- `password`

Optional fields:
- `project`
- `description`
- `migrations_path`
- `sslmode` (boolean override; defaults to `[database].sslmode`)
- `url` (full connection URL; if set, it overrides host/port/user/password/database)

### Optional global section
```toml
[migrations]
path = "db/migrations"
```

### Behavior
- `sslmode = false` maps to `sslmode=disable` in connection URLs.
- `sslmode = true` maps to `sslmode=require` in connection URLs.
- `pg_bin_dir` must point to a directory containing a `psql` binary.
- `python_bin` must point to a Python 3.11+ executable with `tomllib`.
- `project` (per-profile) is used for auto-selecting a profile when `DB_PROFILE` is unset; profiles without `project` are treated as shared/global.
- One-off `DB_URL` usage does not require `postgres.toml` and bypasses TOML schema checks.

## Version `1.0.0` (legacy current before semver)
**Status:** legacy; still readable, migration recommended.

### Required
```toml
[configuration]
schema_version = 1
pg_bin_path = "/path/to/postgres/bin"
```

`schema_version = "1.0.0"` is treated the same as `schema_version = 1`.

### Behavior
- `pg_bin_path` points to the directory containing `psql`.
- Runtime still accepts `1.0.0` for compatibility, but `./scripts/migrate_toml_schema.sh` upgrades it to `1.1.0`.

### Migration to `1.1.0`
- Rename `[configuration].pg_bin_path` to `pg_bin_dir`.
- Add `[configuration].python_bin` using the resolved Python interpreter running the migration.
- Rewrite `schema_version` to `"1.1.0"`.

## Version `0.0.0` (legacy, pre-`schema_version`)
**Status:** legacy; must be migrated.

### Notes
- No `[configuration]` table.
- `sslmode` values may appear as strings (for example `"disable"`, `"require"`, `"verify-full"`) or booleans depending on historical usage.

### Migration to `1.0.0`
- Add `[configuration].schema_version = "1.0.0"`.
- Normalize `sslmode` to boolean:
  - `"disable"` → `false`
  - `"require"`, `"verify-ca"`, `"verify-full"`, `"true"`, `"enable"` → `true`
- If `sslmode` is unrecognized (for example `prefer`, `allow`), migration fails and requires a manual fix.
- Add `[configuration].pg_bin_path` (detected from `psql` or set explicitly).

### Migration to `1.1.0`
- `0.0.0 -> 1.0.0 -> 1.1.0` is automatic through `./scripts/migrate_toml_schema.sh`.
