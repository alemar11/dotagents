# Postgres Option Contract

Load this reference before reading, writing, or reporting Postgres skill config.
It is the canonical registry for behavior-affecting option fields.

## Registry

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `ssl_mode` | `disable`, `require` | `disable` | Local runtime TLS choice. It does not model PostgreSQL `verify-ca` or `verify-full` semantics. |
| `access_mode` | `read`, `write`, `read-write` | `read-write` | Local CLI safety guard; server roles and grants remain authoritative. |
| `migration_outcome` | `migrated`, `no-change` | Derived | Emitted by `profile migrate-config`; backup paths and schema versions remain separate data. |

## Compatibility Boundary

- Config schema v3 emits only `ssl_mode` and `access_mode`.
- Read legacy config keys `sslmode` and `access` as aliases. Read boolean SSL
  values and `read_write` as legacy values. Normalize them only in memory for
  ordinary runtime commands and persist them only during an explicit config
  write.
- The hidden `profile migrate-toml` and `profile set-ssl` commands remain input
  aliases for compatibility. Current help, docs, JSON, and config output use
  `migrate-config`, `set-ssl-mode`, `ssl_mode`, and `access_mode`.
- PostgreSQL-owned syntax remains unchanged: accept `PGSSLMODE` and URL query
  parameters named `sslmode` at the external boundary.
