# Postgres Skill Config Schema

Config file:

```text
<project-root>/.skills/postgres/config.toml
```

Current schema version: `3.0.0`

## Shape

```toml
schema_version = "3.0.0"

[defaults]
profile = "local"

[tools.postgres]
ssl_mode = "disable"
migrations_path = "db/migrations"

[tools.postgres.profiles.local]
description = "Local development DB"
access_mode = "read-write"
host = "127.0.0.1"
port = 5432
database = "app"
user = "postgres"
password = "postgres"
ssl_mode = "disable"
migrations_path = "db/migrations"
```

## Notes

- `schema_version` is required and normalizes to `3.0.0`.
- Canonical `config.toml` is local persisted operator config; consuming repos
  should gitignore `.skills/postgres/config.toml`.
- `[defaults].profile` stores the preferred saved profile when multiple
  profiles exist.
- `[tools.postgres]` stores shared Postgres defaults. `access_mode` is allowed
  here only as an inheritance/default source.
- `[tools.postgres.profiles.<name>]` stores per-profile overrides.
- `[tools.postgres.profiles.<name>].access_mode` is `read`, `write`, or
  `read-write`.
- Missing `access_mode` values resolve to `read-write` for compatibility and
  normalize in memory for ordinary runtime commands. They are written
  explicitly only by an authorized config write such as
  `profile migrate-config`.
- `access_mode` is a local CLI safety guard. PostgreSQL roles, grants, RLS, and
  server-side read-only settings remain authoritative.
- `ssl_mode` is `disable` or `require`. The skill intentionally does not claim
  `verify-ca` or `verify-full` semantics; legacy values in that family
  normalize to `require` because the runtime only distinguishes TLS on/off.
- `url` may be used in a profile when the user wants to persist a full
  connection string instead of discrete fields.
- `[meta]` is intentionally absent from this skill.
- `pg_bin_dir`, `pg_bin_path`, and `python_bin` are not part of the canonical
  persisted schema.

## Migration Rules

- If canonical `config.toml` exists, it is always the source of truth.
- A legacy v1 table layout found at canonical `config.toml` is still legacy
  persisted encoding: ordinary reads normalize it in memory, while
  `profile migrate-config` backs it up and rewrites the v3 layout.
- Existing `2.0.0` and `2.1.0` canonical configs normalize in memory to
  `3.0.0` for ordinary runtime commands and migrate in place only when the
  operator runs `profile migrate-config` or another explicit config-writing
  command.
- During v3 migration, every profile missing `access_mode` gets an explicit
  value using this precedence: profile `access_mode` or legacy `access`, then
  `[tools.postgres].access_mode` or legacy `access`, then `read-write`.
- Legacy `sslmode` becomes `ssl_mode`; booleans map to `disable` or `require`.
- Legacy `access` becomes `access_mode`; `read_write` becomes `read-write`.
- If canonical `config.toml` is absent and legacy `postgres.toml` exists,
  ordinary runtime commands read and normalize it without writing. Running
  `profile migrate-config` performs the one-way persistence into canonical
  `config.toml`.
- When a consuming repo previously ignored legacy `postgres.toml`, update its
  ignore rules to cover canonical `config.toml` in the same rollout; do not
  leave the migrated canonical file unignored.
- Missing legacy `schema_version`, `1`, `1.0.0`, and `1.1.0` all migrate to
  canonical `3.0.0`.
- Before any migration write, copy the source config to the next available
  `.bak` path under the owner-scoped cache at
  `$XDG_CACHE_HOME/dotagents/skills/postgres/config-backups/<source-key>/` or
  `~/.cache/dotagents/skills/postgres/config-backups/<source-key>/`. Backup
  directories use `0700` and backup files are allocated collision-free with
  descriptor-relative, no-follow operations and `0600` before the already-read
  source bytes are written and synced on Unix.
  Empty, relative, parent-traversing, project-local, or symlink-resolved
  project-local cache roots are rejected in favor of a safe absolute fallback;
  migration stops if no external cache root is available.
  Write canonical `config.toml` only after that proof, through a temporary file
  and atomic rename. A no-change rerun creates no backup and performs no write.
- Ordinary config loads normalize only in memory and never create a backup or
  write a file.
- Unsupported future schema versions are a hard stop with no backup or write.
