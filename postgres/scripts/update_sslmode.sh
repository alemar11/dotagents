#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/runtime_env.sh"
PROJECT_ROOT="$(postgres_runtime_resolve_project_root_or_die)" || exit 1

TOML_PATH="$PROJECT_ROOT/.skills/postgres/postgres.toml"

PROFILE="${1:-}"
NEW_SSLMODE="${2:-}"

if [[ -z "$PROFILE" || -z "$NEW_SSLMODE" ]]; then
  echo "Usage: update_sslmode.sh <profile> <true|false>" >&2
  exit 1
fi

normalize_sslmode() {
  local lowered=""
  lowered="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"
  case "$lowered" in
    true|t|1|yes|y|on|enable|enabled|require|required|verify-ca|verify-full)
      echo "true"
      ;;
    false|f|0|no|n|off|disable|disabled)
      echo "false"
      ;;
    *)
      return 1
      ;;
  esac
}

SSL_VALUE="$(normalize_sslmode "$NEW_SSLMODE")" || {
  echo "Invalid sslmode '$NEW_SSLMODE'. Use true/false (or require/disable)." >&2
  exit 1
}

if [[ ! -f "$TOML_PATH" ]]; then
  echo "postgres.toml not found at $TOML_PATH" >&2
  exit 1
fi

if [[ -x "$SCRIPT_DIR/check_toml_gitignored.sh" ]]; then
  "$SCRIPT_DIR/check_toml_gitignored.sh" "$PROJECT_ROOT" || true
fi

tmp_file="$(mktemp)"

awk -v profile="$PROFILE" -v sslmode="$SSL_VALUE" '
  BEGIN { in_profile=0; found=0; updated=0 }
  /^[[:space:]]*\[database\.[a-z0-9_-]+\][[:space:]]*$/ {
    if (in_profile && !updated) {
      print "sslmode = " sslmode
      updated=1
    }
    in_profile=0
    if (match($0, /^[[:space:]]*\[database\.([a-z0-9_-]+)\][[:space:]]*$/, m)) {
      if (m[1] == profile) {
        in_profile=1
        found=1
      }
    }
    print
    next
  }
  {
    if (in_profile && $0 ~ /^[[:space:]]*sslmode[[:space:]]*=/) {
      print "sslmode = " sslmode
      updated=1
      next
    }
    print
  }
  END {
    if (in_profile && !updated) {
      print "sslmode = " sslmode
      updated=1
    }
    if (!found) {
      exit 2
    }
  }
' "$TOML_PATH" > "$tmp_file"

status=$?
if [[ $status -eq 2 ]]; then
  rm -f "$tmp_file"
  echo "Profile '$PROFILE' not found in postgres.toml." >&2
  exit 1
fi

mv "$tmp_file" "$TOML_PATH"
