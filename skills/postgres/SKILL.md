---
name: postgres
description: Connect to Postgres databases, run SQL and diagnostics, inspect schemas and migrations, review query performance, and use common PostGIS or pgvector patterns.
---

# Postgres

## Goal

Use this skill to connect to Postgres, run SQL, inspect schemas, review query
performance, design tables and indexes, work with common PostGIS or pgvector
patterns, and manage migration release flow through the shipped
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
- `scripts/postgres` dispatches to platform-specific Rust binaries under
  `scripts/bin/`, currently named `postgres-<os>-<arch>`.
- Supported shipped binary names are `postgres-darwin-arm64`,
  `postgres-darwin-x86_64`, `postgres-linux-arm64`, and
  `postgres-linux-x86_64`; a platform is usable only when its executable is
  present.
- The implementation lives in `projects/postgres/` and is maintenance-only.
  Normal usage stays on the `scripts/postgres` surface.
- Canonical persisted config lives at `<project-root>/.skills/postgres/config.toml`.
- Profile `access` modes are local CLI safety guards with values `read`,
  `write`, and `read_write`; they do not replace PostgreSQL roles, grants, RLS,
  or server-side read-only settings.
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

Use `references/common-workflows.md` for copy/paste playbooks:

- enums (find type + values)
- find table/column/function by name
- show table shape + indexes
- confirm which DB you are connected to
- safe “quick lookup” templates

## Guardrails (short)

- Before you run any non-trivial query, confirm the target:
  - `DB_PROJECT_ROOT="$DB_PROJECT_ROOT" DB_PROFILE=local "$POSTGRES_CLI" --json profile resolve`
  - then run the identity query from `references/common-workflows.md` (“Which DB am I connected to?”).
- If the user says “production”, “prod”, “staging”, or “remote DB”:
  - stop and ask for the exact `DB_PROFILE` / `DB_URL` they intend
  - default to `access=read` and require an explicit confirmation before any write/DDL
- Always ask for approval before DDL changes.
- Keep schema changes in a pending migration file; do not edit released files.
- Before editing migrations, resolve the repo's exact `migrations_path` and
  pending migration filename by inspecting `.skills/postgres/config.toml` and
  the existing migration directory.
- If a `prerelease*.sql` file exists, use it for pending work instead of
  creating a timestamped migration file.
- Use `references/postgres_guardrails.md` as the canonical migration workflow.

## References

- Usage + command surface + JSON mode: `references/postgres_usage.md`
- Common workflows playbook: `references/common-workflows.md`
- Env var contract: `references/postgres_env.md`
- Config schema: `references/postgres_skill_schema.md`
- Migration guardrails: `references/postgres_guardrails.md`
- Local/Docker recovery: `references/postgres_local_recovery.md`
- Design guidance: `references/postgres_best_practices/README.md`
