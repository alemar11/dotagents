# Postgres Skill Config Schema

Config file:

```text
<project-root>/.skills/postgres/config.toml
```

Current schema version: `2.1.0`

## Shape

```toml
schema_version = "2.1.0"

[defaults]
profile = "local"

[tools.postgres]
sslmode = false
migrations_path = "db/migrations"

[tools.postgres.profiles.local]
description = "Local development DB"
access = "read_write"
host = "127.0.0.1"
port = 5432
database = "app"
user = "postgres"
password = "postgres"
sslmode = false
migrations_path = "db/migrations"
```

## Notes

- `schema_version` is required and normalizes to `2.1.0`.
- Canonical `config.toml` is local persisted operator config; consuming repos
  should gitignore `.skills/postgres/config.toml`.
- `[defaults].profile` stores the preferred saved profile when multiple profiles
  exist.
- `[tools.postgres]` stores shared Postgres defaults. `access` is allowed here
  only as an inheritance/default source.
- `[tools.postgres.profiles.<name>]` stores per-profile overrides.
- `[tools.postgres.profiles.<name>].access` stores the profile access mode:
  `read`, `write`, or `read_write`.
- Missing `access` values are treated as `read_write` for compatibility and are
  normalized in memory for ordinary runtime commands. They are written
  explicitly only by an authorized config write such as `profile migrate-toml`.
- `access` is a local CLI safety guard. PostgreSQL roles, grants, RLS, and
  server-side read-only settings remain authoritative.
- `sslmode` must be boolean in TOML (`true` / `false`), not a string.
- `url` may be used in a profile when the user wants to persist a full
  connection string instead of discrete fields.
- `[meta]` is intentionally absent from this skill.
- `pg_bin_dir`, `pg_bin_path`, and `python_bin` are not part of the canonical
  persisted schema.

## Migration rules

- If canonical `config.toml` exists, it is always the source of truth.
- Existing `2.0.0` canonical configs normalize in memory to `2.1.0` for
  ordinary runtime commands and migrate in place only when the operator runs
  `profile migrate-toml` or another explicit config-writing command.
- During `2.1.0` migration, every profile missing `access` gets an explicit
  value using this precedence: profile `access`, then `[tools.postgres].access`,
  then `read_write`.
- If canonical `config.toml` is absent and legacy `postgres.toml` exists,
  ordinary runtime commands read and normalize it without writing. Running
  `profile migrate-toml` performs the one-way persistence into canonical
  `config.toml`.
- When a consuming repo previously ignored legacy `postgres.toml`, update its
  ignore rules to cover canonical `config.toml` in the same rollout; do not
  leave the migrated canonical file unignored.
- Missing legacy `schema_version`, `1`, `1.0.0`, and `1.1.0` all migrate to
  canonical `2.1.0`.
- String `sslmode` values such as `require` / `disable` are normalized to
  boolean form during migration.
- Unsupported future schema versions are a hard stop.
