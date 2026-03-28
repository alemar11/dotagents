#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/pg_env.sh"
eval "$("$SCRIPT_DIR/resolve_db_url.sh")"

input="${1:-}"
if [[ -z "$input" ]]; then
  echo "Usage: restore_dump.sh <dump_file>" >&2
  exit 1
fi
if [[ ! -f "$input" ]]; then
  echo "File not found: $input" >&2
  exit 1
fi

run_restore() {
  local url="$1"
  if [[ "$input" == *.sql ]]; then
    psql "$url" -v ON_ERROR_STOP=1 -f "$input"
  else
    pg_restore --no-owner --no-acl --dbname "$url" "$input"
  fi
}

should_retry_with_ssl() {
  local err_file="$1"
  [[ -s "$err_file" ]] || return 1
  grep -Eiq \
    'SSL off|requires SSL|requires encryption|server requires|sslmode|TLS|certificate|no pg_hba\.conf entry.*SSL off' \
    "$err_file"
}

run_restore_with_stderr_capture() {
  local url="$1"
  local err_file="$2"
  set +e
  run_restore "$url" 2>"$err_file"
  local cmd_status=$?
  set -e
  if [[ -s "$err_file" ]]; then
    cat "$err_file" >&2
  fi
  return $cmd_status
}

first_err_file="$(mktemp)"
retry_err_file=""
trap 'rm -f "$first_err_file" "$retry_err_file"' EXIT

set +e
run_restore_with_stderr_capture "$DB_URL" "$first_err_file"
status=$?
set -e

if [[ $status -ne 0 && "$DB_SSLMODE" == "disable" ]] && should_retry_with_ssl "$first_err_file"; then
  retry_url="$(postgres_runtime_connection_set_sslmode "$DB_URL" "require")"
  echo "Retrying restore with sslmode=require for profile '${DB_PROFILE:-local}'..." >&2
  retry_err_file="$(mktemp)"
  set +e
  run_restore_with_stderr_capture "$retry_url" "$retry_err_file"
  retry_status=$?
  set -e

  if [[ $retry_status -eq 0 && "$DB_URL_SOURCE" == "toml" ]]; then
    if [[ "${DB_AUTO_UPDATE_SSLMODE:-}" == "1" ]]; then
      "$SCRIPT_DIR/update_sslmode.sh" "$DB_PROFILE" "true" || true
      echo "Updated postgres.toml: [database.$DB_PROFILE] sslmode = true" >&2
    else
      echo "sslmode=require succeeded. To persist for profile '$DB_PROFILE', run:" >&2
      echo "  $SCRIPT_DIR/update_sslmode.sh \"$DB_PROFILE\" true" >&2
      echo "(Set DB_AUTO_UPDATE_SSLMODE=1 to auto-update.)" >&2
    fi
  fi

  status=$retry_status
fi

if [[ $status -ne 0 ]]; then
  exit $status
fi

echo "Restore complete."
