#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_main_help() {
  cat <<'EOF'
Usage:
  postgres.sh help [group]
  postgres.sh <group> <command> [args...]

Thin dispatcher over the postgres skill scripts.
It improves discoverability and forwards all remaining arguments to the
existing script for the selected command.

Groups:
  profile    bootstrap, test, info, version, resolve, migrate-toml,
             set-ssl, check-psql, check-deps
  query      run, psql, explain, find, docs
  activity   overview, locks, slow, long-running, cancel, terminate,
             cancel-pid, terminate-pid, pg-stat-top
  schema     inspect, diff, dump, table-sizes, index-health,
             missing-fk-indexes, vacuum-status, roles
  dump       schema, data, restore
  migration  release

Examples:
  ./scripts/postgres.sh help
  DB_PROFILE=local ./scripts/postgres.sh query run -c "select now();"
  DB_PROFILE=local ./scripts/postgres.sh activity cancel --pid 12345
  DB_PROJECT_ROOT=/path/to/project ./scripts/postgres.sh profile bootstrap

Notes:
  - Underlying scripts remain the stable primitives.
  - Power users can keep calling ./scripts/<name>.sh directly.
EOF
}

show_group_help() {
  case "${1:-}" in
    profile)
      cat <<'EOF'
Profile commands:
  bootstrap      -> bootstrap_profile.sh
  test           -> test_connection.sh
  info           -> connection_info.sh
  version        -> pg_version.sh
  resolve        -> resolve_db_url.sh
  migrate-toml   -> migrate_toml_schema.sh
  set-ssl        -> update_sslmode.sh
  check-psql     -> check_psql.sh
  check-deps     -> check_deps.sh

Examples:
  ./scripts/postgres.sh profile test
  eval "$(./scripts/postgres.sh profile resolve)"
  ./scripts/postgres.sh profile set-ssl local true
EOF
      ;;
    query)
      cat <<'EOF'
Query commands:
  run       -> run_sql.sh
  psql      -> psql_with_ssl_fallback.sh
  explain   -> explain_analyze.sh
  find      -> find_objects.sh
  docs      -> search_postgres_docs.sh

Examples:
  ./scripts/postgres.sh query run -c "select now();"
  ./scripts/postgres.sh query psql -c "select current_database();"
  ./scripts/postgres.sh query explain --no-analyze "select * from users"
  ./scripts/postgres.sh query find auth --types table,column
EOF
      ;;
    activity)
      cat <<'EOF'
Activity commands:
  overview        -> activity_overview.sh
  locks           -> locks_overview.sh
  slow            -> slow_queries.sh
  long-running    -> long_running_queries.sh
  cancel          -> query_action.sh cancel
  terminate       -> query_action.sh terminate
  cancel-pid      -> cancel_backend.sh
  terminate-pid   -> terminate_backend.sh
  pg-stat-top     -> pg_stat_statements_top.sh

Examples:
  ./scripts/postgres.sh activity slow 20
  ./scripts/postgres.sh activity cancel --query "select * from events"
  DB_CONFIRM=YES ./scripts/postgres.sh activity terminate --pid 12345
EOF
      ;;
    schema)
      cat <<'EOF'
Schema commands:
  inspect             -> schema_introspect.sh
  diff                -> schema_diff.sh
  dump                -> schema_dump.sh
  table-sizes         -> table_sizes.sh
  index-health        -> index_health.sh
  missing-fk-indexes  -> missing_fk_indexes.sh
  vacuum-status       -> vacuum_analyze_status.sh
  roles               -> roles_overview.sh

Examples:
  ./scripts/postgres.sh schema inspect
  ./scripts/postgres.sh schema diff local staging
  ./scripts/postgres.sh schema table-sizes 20
EOF
      ;;
    dump)
      cat <<'EOF'
Dump commands:
  schema   -> schema_dump.sh
  data     -> data_dump.sh
  restore  -> restore_dump.sh

Examples:
  ./scripts/postgres.sh dump schema
  ./scripts/postgres.sh dump data data_local.dump
  ./scripts/postgres.sh dump restore ./backup.dump
EOF
      ;;
    migration)
      cat <<'EOF'
Migration commands:
  release  -> release_migration.sh

Examples:
  ./scripts/postgres.sh migration release --summary "Ship migration"
EOF
      ;;
    *)
      echo "Unknown group: ${1:-}" >&2
      return 1
      ;;
  esac
}

is_known_group() {
  case "${1:-}" in
    profile|query|activity|schema|dump|migration) return 0 ;;
    *) return 1 ;;
  esac
}

dispatch_script() {
  local script_name="$1"
  shift
  exec "$SCRIPT_DIR/$script_name" "$@"
}

group="${1:-}"
if [[ -z "$group" || "$group" == "help" || "$group" == "-h" || "$group" == "--help" ]]; then
  if [[ $# -ge 2 ]]; then
    if ! show_group_help "$2"; then
      echo >&2
      show_main_help >&2
      exit 1
    fi
    exit 0
  fi
  show_main_help
  exit 0
fi
shift

if [[ "${1:-}" == "help" || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  if ! show_group_help "$group"; then
    echo >&2
    show_main_help >&2
    exit 1
  fi
  exit 0
fi

command="${1:-}"
if [[ -z "$command" ]]; then
  if ! show_group_help "$group"; then
    echo >&2
    show_main_help >&2
    exit 1
  fi
  exit 0
fi
shift

case "$group:$command" in
  profile:bootstrap) dispatch_script "bootstrap_profile.sh" "$@" ;;
  profile:test) dispatch_script "test_connection.sh" "$@" ;;
  profile:info) dispatch_script "connection_info.sh" "$@" ;;
  profile:version) dispatch_script "pg_version.sh" "$@" ;;
  profile:resolve) dispatch_script "resolve_db_url.sh" "$@" ;;
  profile:migrate-toml) dispatch_script "migrate_toml_schema.sh" "$@" ;;
  profile:set-ssl) dispatch_script "update_sslmode.sh" "$@" ;;
  profile:check-psql) dispatch_script "check_psql.sh" "$@" ;;
  profile:check-deps) dispatch_script "check_deps.sh" "$@" ;;
  query:run) dispatch_script "run_sql.sh" "$@" ;;
  query:psql) dispatch_script "psql_with_ssl_fallback.sh" "$@" ;;
  query:explain) dispatch_script "explain_analyze.sh" "$@" ;;
  query:find) dispatch_script "find_objects.sh" "$@" ;;
  query:docs) dispatch_script "search_postgres_docs.sh" "$@" ;;
  activity:overview) dispatch_script "activity_overview.sh" "$@" ;;
  activity:locks) dispatch_script "locks_overview.sh" "$@" ;;
  activity:slow) dispatch_script "slow_queries.sh" "$@" ;;
  activity:long-running) dispatch_script "long_running_queries.sh" "$@" ;;
  activity:cancel) dispatch_script "query_action.sh" "cancel" "$@" ;;
  activity:terminate) dispatch_script "query_action.sh" "terminate" "$@" ;;
  activity:cancel-pid) dispatch_script "cancel_backend.sh" "$@" ;;
  activity:terminate-pid) dispatch_script "terminate_backend.sh" "$@" ;;
  activity:pg-stat-top) dispatch_script "pg_stat_statements_top.sh" "$@" ;;
  schema:inspect) dispatch_script "schema_introspect.sh" "$@" ;;
  schema:diff) dispatch_script "schema_diff.sh" "$@" ;;
  schema:dump) dispatch_script "schema_dump.sh" "$@" ;;
  schema:table-sizes) dispatch_script "table_sizes.sh" "$@" ;;
  schema:index-health) dispatch_script "index_health.sh" "$@" ;;
  schema:missing-fk-indexes) dispatch_script "missing_fk_indexes.sh" "$@" ;;
  schema:vacuum-status) dispatch_script "vacuum_analyze_status.sh" "$@" ;;
  schema:roles) dispatch_script "roles_overview.sh" "$@" ;;
  dump:schema) dispatch_script "schema_dump.sh" "$@" ;;
  dump:data) dispatch_script "data_dump.sh" "$@" ;;
  dump:restore) dispatch_script "restore_dump.sh" "$@" ;;
  migration:release) dispatch_script "release_migration.sh" "$@" ;;
  *)
    echo "Unknown command: $group $command" >&2
    echo >&2
    if is_known_group "$group"; then
      show_group_help "$group" >&2
      echo >&2
    fi
    show_main_help >&2
    exit 1
    ;;
esac
