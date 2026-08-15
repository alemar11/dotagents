# Postgres State Contract

This reference owns Postgres-skill migration state and derived command
outcomes. Selectable `ssl_mode` and `access_mode` values remain canonically
owned by [runtime/options.md](runtime/options.md); they are configuration, not
execution facts.

## Migration file state

Migration file state is persisted in the repository filesystem.

| Value | Meaning | Allowed transition |
| --- | --- | --- |
| `pending` | The migration remains editable in the repository's resolved pending migration file. | `pending -> released` only through an explicitly authorized release. |
| `released` | The migration is immutable release history under the resolved released directory. | Terminal for that file; create new pending work instead of editing it. |

## Config migration outcome

`profile migrate-config` emits this transient result. Backup paths and schema
versions remain separate output data.

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `migration_outcome` | `migrated`, `no-change` | Derived | `migrated` means the explicit command persisted a normalized config update; `no-change` means no persistent config edit was needed. |

Database application state is external PostgreSQL state. Verify it with the
least expensive authoritative query required by the migration guardrails; do
not infer it from the file transition or command receipt.
