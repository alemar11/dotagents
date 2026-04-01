#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF'
Usage:
  query_action.sh <cancel|terminate> --query "<substring>" [--user "<name>"] [--limit N] [--pid PID[,PID...]]
  query_action.sh <cancel|terminate> --user "<name>" [--limit N] [--pid PID[,PID...]]
  query_action.sh <cancel|terminate> --pid PID[,PID...] [--query "<substring>"] [--user "<name>"]

Examples:
  ./scripts/query_action.sh cancel --query "select * from events"
  ./scripts/query_action.sh terminate --user app_user --limit 10
  DB_CONFIRM=YES ./scripts/query_action.sh cancel --pid 12345,12346
EOF
}

missing_option_value() {
  local option="$1"
  echo "Missing value for ${option}." >&2
  usage >&2
  exit 1
}

append_pid_values() {
  local raw="$1"
  local token=""

  raw="${raw//,/ }"
  for token in $raw; do
    if ! [[ "$token" =~ ^[0-9]+$ ]]; then
      echo "Invalid PID: $token" >&2
      exit 1
    fi
    selected_pids+=("$token")
  done
}

action=""
pattern=""
user=""
limit=20
selected_pids=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    cancel|terminate)
      if [[ -n "$action" ]]; then
        echo "Unexpected extra action: $1" >&2
        usage >&2
        exit 1
      fi
      action="$1"
      ;;
    --query)
      if [[ $# -lt 2 || "$2" == --* || "$2" == "-h" ]]; then
        missing_option_value "$1"
      fi
      pattern="$2"
      shift
      ;;
    --user)
      if [[ $# -lt 2 || "$2" == --* || "$2" == "-h" ]]; then
        missing_option_value "$1"
      fi
      user="$2"
      shift
      ;;
    --limit)
      if [[ $# -lt 2 || "$2" == --* || "$2" == "-h" ]]; then
        missing_option_value "$1"
      fi
      limit="$2"
      shift
      ;;
    --pid)
      if [[ $# -lt 2 || "$2" == --* || "$2" == "-h" ]]; then
        missing_option_value "$1"
      fi
      append_pid_values "$2"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift
done

if [[ -z "$action" || ( -z "$pattern" && -z "$user" && ${#selected_pids[@]} -eq 0 ) ]]; then
  usage
  exit 1
fi

if ! [[ "$limit" =~ ^[0-9]+$ ]]; then
  echo "Invalid limit: $limit" >&2
  exit 1
fi

sql_filter="state <> 'idle' and pid <> pg_backend_pid()"
if [[ -n "$pattern" ]]; then
  sql_filter+=" and query ilike '%' || :'pattern' || '%'"
fi
if [[ -n "$user" ]]; then
  sql_filter+=" and usename = :'user'"
fi

rows=""
if [[ -n "$pattern" || -n "$user" ]]; then
  rows="$("$SCRIPT_DIR/psql_with_ssl_fallback.sh" \
    -v ON_ERROR_STOP=1 \
    -v "pattern=${pattern}" \
    -v "user=${user}" \
    -F $'\t' -At \
    -c "
select
  pid,
  usename,
  datname,
  state,
  now() - query_start as query_age,
  left(query, 200) as query
from pg_stat_activity
where ${sql_filter}
order by query_start desc nulls last
limit ${limit};")"
fi

if [[ -n "$pattern" || -n "$user" ]] && [[ -z "$rows" ]]; then
  echo "No matching active queries."
  exit 0
fi

if [[ -n "$rows" ]]; then
  echo "Candidates:"
  printf "%-8s %-16s %-16s %-10s %-12s %s\n" "PID" "USER" "DB" "STATE" "AGE" "QUERY"
  while IFS=$'\t' read -r pid ruser db state age query; do
    printf "%-8s %-16s %-16s %-10s %-12s %s\n" "$pid" "$ruser" "$db" "$state" "$age" "$query"
  done <<<"$rows"
fi

valid_pids=("${selected_pids[@]}")

if [[ ${#valid_pids[@]} -gt 0 && -n "$rows" ]]; then
  for pid in "${valid_pids[@]}"; do
    if ! printf '%s\n' "$rows" | awk -F '\t' -v target="$pid" '$1 == target { found = 1 } END { exit(found ? 0 : 1) }'; then
      echo "PID ${pid} is not present in the current candidate set." >&2
      exit 1
    fi
  done
fi

if [[ ${#valid_pids[@]} -eq 0 ]]; then
  if [[ ! -t 0 ]]; then
    echo "No PIDs provided and stdin is not interactive. Pass --pid to run non-interactively." >&2
    exit 1
  fi

  read -r -p "Enter PID(s) to ${action} (space-separated), or empty to abort: " pids_input || true
  if [[ -z "$pids_input" ]]; then
    echo "Aborted."
    exit 1
  fi

  append_pid_values "$pids_input"
  valid_pids=("${selected_pids[@]}")
fi

confirm="${DB_CONFIRM:-}"
if [[ "$confirm" != "YES" ]]; then
  if [[ -t 0 ]]; then
    read -r -p "Type YES to ${action} PID(s): ${valid_pids[*]}: " confirm
  fi
fi

if [[ "$confirm" != "YES" ]]; then
  echo "Aborted. Set DB_CONFIRM=YES to skip confirmation." >&2
  exit 1
fi

pid_list="$(IFS=,; echo "${valid_pids[*]}")"
if [[ "$action" == "cancel" ]]; then
  "$SCRIPT_DIR/psql_with_ssl_fallback.sh" -v ON_ERROR_STOP=1 -Atc \
    "select pid, pg_cancel_backend(pid) from unnest(array[${pid_list}]) as pid;"
else
  "$SCRIPT_DIR/psql_with_ssl_fallback.sh" -v ON_ERROR_STOP=1 -Atc \
    "select pid, pg_terminate_backend(pid) from unnest(array[${pid_list}]) as pid;"
fi
