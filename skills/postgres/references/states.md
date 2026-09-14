# Postgres State Contract

This reference owns the derived config-migration result emitted by the Postgres
skill. Selectable `ssl_mode` and `access_mode` values remain canonically owned
by [runtime/options.md](runtime/options.md); they are configuration, not
execution facts. SQL-file and changelog state is project-owned and is not
tracked here.

## Config migration outcome

`profile migrate-config` emits this transient result. Backup paths and schema
versions remain separate output data.

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `migration_outcome` | `migrated`, `no-change` | Derived | `migrated` means the explicit command persisted a normalized config update; `no-change` means no persistent config edit was needed. |

Database application state is external PostgreSQL state. Verify it with the
least expensive authoritative query required by
[workflows/schema-change-guardrails.md](workflows/schema-change-guardrails.md);
do not infer it from a project migration receipt or file transition.
