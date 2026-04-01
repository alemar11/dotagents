#!/usr/bin/env bash

if [[ -z "${PGAPPNAME:-}" ]]; then
  export PGAPPNAME="${DB_APPLICATION_NAME:-codex-postgres-skill}"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/runtime_env.sh"

if ! postgres_runtime_require_env_unset "PROJECT_ROOT" "DB_PROJECT_ROOT"; then
  return 1 2>/dev/null || exit 1
fi

pg_env_add_path() {
  local dir="$1"
  if [[ -n "$dir" && -d "$dir" ]]; then
    case ":$PATH:" in
      *":$dir:"*) ;;
      *) export PATH="$dir:$PATH" ;;
    esac
  fi
}

pg_env_normalize_bin_dir() {
  local path="$1"
  if [[ -z "$path" ]]; then
    return 0
  fi
  local trimmed="${path%/}"
  if [[ -f "$trimmed" || "${trimmed##*/}" == "psql" ]]; then
    dirname "$trimmed"
  else
    echo "$trimmed"
  fi
}

pg_env_resolve_project_root() {
  postgres_runtime_resolve_project_root
}

pg_env_read_pg_bin_dir() {
  local toml_path="$1"
  local value=""
  value="$(postgres_runtime_read_configuration_value "$toml_path" "pg_bin_dir")"
  if [[ -n "$value" ]]; then
    printf '%s' "$value"
    return 0
  fi
  postgres_runtime_read_configuration_value "$toml_path" "pg_bin_path"
}

pg_env_preferred_pg_bin_key() {
  local toml_path="$1"
  local schema_version=""

  schema_version="$(postgres_runtime_schema_version "$toml_path")"
  case "$schema_version" in
    1.1.0)
      echo "pg_bin_dir"
      return 0
      ;;
  esac

  if [[ -n "$(postgres_runtime_read_configuration_value "$toml_path" "pg_bin_dir")" ]]; then
    echo "pg_bin_dir"
    return 0
  fi

  echo "pg_bin_path"
}

pg_env_write_config_string_key() {
  local toml_path="$1"
  local key="$2"
  local new_value="$3"
  local remove_key="${4:-}"
  local escaped_value=""
  if [[ -z "$toml_path" || -z "$key" || ! -f "$toml_path" ]]; then
    return 1
  fi
  escaped_value="${new_value//\\/\\\\}"
  escaped_value="${escaped_value//\"/\\\"}"
  local tmp_file
  tmp_file="$(mktemp)" || return 1
  if awk -v key="$key" -v remove_key="$remove_key" -v new="$escaped_value" '
    BEGIN { in_config=0; found=0; seen_config=0 }
    /^[[:space:]]*\[configuration\][[:space:]]*$/ {
      seen_config=1
      in_config=1
      print
      next
    }
    /^[[:space:]]*\[[^]]+\][[:space:]]*$/ {
      if (in_config && !found) {
        print key " = \"" new "\""
        print ""
        found=1
      }
      in_config=0
      print
      next
    }
    {
      if (in_config && remove_key != "" && $0 ~ "^[[:space:]]*" remove_key "[[:space:]]*=") {
        next
      }
      if (in_config && $0 ~ "^[[:space:]]*" key "[[:space:]]*=") {
        print key " = \"" new "\""
        found=1
        next
      }
      print
    }
    END {
      if (in_config && !found) {
        print key " = \"" new "\""
        found=1
      }
      if (!seen_config) {
        exit 3
      }
    }
  ' "$toml_path" > "$tmp_file"; then
    mv "$tmp_file" "$toml_path"
    return 0
  fi

  status=$?
  rm -f "$tmp_file"
  [[ $status -eq 3 ]] || return 1
  echo "postgres.toml is missing [configuration]. Run ./scripts/migrate_toml_schema.sh before persisting ${key}." >&2
  return 1
}

pg_env_write_pg_bin_dir() {
  local toml_path="$1"
  local new_dir="$2"
  local key=""
  local remove_key=""

  if [[ -z "$toml_path" || -z "$new_dir" || ! -f "$toml_path" ]]; then
    return 1
  fi

  key="$(pg_env_preferred_pg_bin_key "$toml_path")"
  if [[ "$key" == "pg_bin_dir" ]]; then
    remove_key="pg_bin_path"
  fi

  if pg_env_write_config_string_key "$toml_path" "$key" "$new_dir" "$remove_key"; then
    echo "Updated postgres.toml: [configuration] ${key} = \"$new_dir\"" >&2
    return 0
  fi
  return 1
}

pg_env_confirm_update() {
  local message="$1"
  if [[ -t 0 ]]; then
    local reply
    read -r -p "$message [y/N] " reply
    case "$reply" in
      [yY]|[yY][eE][sS]) return 0 ;;
      *) return 1 ;;
    esac
  fi
  echo "$message (no TTY; skipping update)" >&2
  return 1
}

pg_env_psql_path="$(command -v psql 2>/dev/null || true)"
pg_env_project_root=""
pg_env_toml_path=""
pg_env_config_bin=""

# Fast path: if psql is already available, skip profile/toml parsing overhead.
if [[ -z "$pg_env_psql_path" ]]; then
  pg_env_project_root="$(pg_env_resolve_project_root)"
  if [[ -n "$pg_env_project_root" ]]; then
    pg_env_toml_path="$pg_env_project_root/.skills/postgres/postgres.toml"
  fi

  if [[ -n "$pg_env_toml_path" && -f "$pg_env_toml_path" ]]; then
    pg_env_config_bin="$(pg_env_read_pg_bin_dir "$pg_env_toml_path")"
  fi

  if [[ -n "$pg_env_config_bin" ]]; then
    pg_env_config_bin_dir="$(pg_env_normalize_bin_dir "$pg_env_config_bin")"
    pg_env_add_path "$pg_env_config_bin_dir"
  fi

  if command -v psql >/dev/null 2>&1; then
    pg_env_psql_path="$(command -v psql)"
  fi
fi

if [[ -z "$pg_env_psql_path" ]]; then
  case "$(uname -s 2>/dev/null || echo unknown)" in
    Darwin)
      if command -v brew >/dev/null 2>&1; then
        pg_env_formula="$(brew list --versions 2>/dev/null | awk '/^postgresql(@[0-9]+)? / {print $1}' | sort -V | tail -n 1)"
        if [[ -z "$pg_env_formula" ]]; then
          pg_env_formula="$(brew search postgresql@ 2>/dev/null | awk '/^postgresql@/ {print $1}' | sort -V | tail -n 1)"
          if [[ -z "$pg_env_formula" ]]; then
            pg_env_formula="postgresql"
          fi
        fi
        if [[ -n "$pg_env_formula" ]]; then
          pg_env_prefix="$(brew --prefix "$pg_env_formula" 2>/dev/null || true)"
          if [[ -n "$pg_env_prefix" && -d "$pg_env_prefix/bin" ]]; then
            pg_env_add_path "$pg_env_prefix/bin"
          fi
        fi
      fi
      ;;
    Linux)
      if [[ -d /usr/lib/postgresql ]]; then
        pg_env_candidate="$(ls /usr/lib/postgresql 2>/dev/null | sort -V | tail -n 1)"
        if [[ -n "$pg_env_candidate" && -d "/usr/lib/postgresql/$pg_env_candidate/bin" ]]; then
          pg_env_add_path "/usr/lib/postgresql/$pg_env_candidate/bin"
        fi
      fi
      ;;
    MINGW*|MSYS*|CYGWIN*)
      if [[ -d "/c/Program Files/PostgreSQL" ]]; then
        pg_env_win_version="$(ls "/c/Program Files/PostgreSQL" 2>/dev/null | sort -V | tail -n 1)"
        if [[ -n "$pg_env_win_version" && -d "/c/Program Files/PostgreSQL/$pg_env_win_version/bin" ]]; then
          pg_env_add_path "/c/Program Files/PostgreSQL/$pg_env_win_version/bin"
        fi
      fi
      ;;
  esac
  if command -v psql >/dev/null 2>&1; then
    pg_env_psql_path="$(command -v psql)"
  fi
fi

if [[ -n "$pg_env_psql_path" ]]; then
  pg_env_found_bin="$(dirname "$pg_env_psql_path")"
  # Runtime helpers may discover a usable psql binary for the current process,
  # but persisting pg_bin_dir is reserved for explicit bootstrap/migration flows.
fi

if [[ -n "${DB_STATEMENT_TIMEOUT_MS:-}" || -n "${DB_LOCK_TIMEOUT_MS:-}" ]]; then
  pgopts="${PGOPTIONS:-}"
  if [[ -n "${DB_STATEMENT_TIMEOUT_MS:-}" ]]; then
    pgopts="${pgopts} -c statement_timeout=${DB_STATEMENT_TIMEOUT_MS}"
  fi
  if [[ -n "${DB_LOCK_TIMEOUT_MS:-}" ]]; then
    pgopts="${pgopts} -c lock_timeout=${DB_LOCK_TIMEOUT_MS}"
  fi
  export PGOPTIONS="$pgopts"
fi
