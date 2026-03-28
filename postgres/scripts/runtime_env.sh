#!/usr/bin/env bash

if [[ -n "${POSTGRES_RUNTIME_ENV_LOADED:-}" ]]; then
  return 0 2>/dev/null || exit 0
fi
POSTGRES_RUNTIME_ENV_LOADED=1

POSTGRES_RUNTIME_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POSTGRES_RUNTIME_SKILL_ROOT="$(cd "$POSTGRES_RUNTIME_SCRIPT_DIR/.." && pwd)"
POSTGRES_RUNTIME_LATEST_SCHEMA="1.1.0"

postgres_runtime_trim() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

postgres_runtime_decode_toml_value() {
  local raw
  raw="$(postgres_runtime_trim "$1")"
  if [[ -z "$raw" ]]; then
    return 0
  fi

  if [[ "$raw" == \"*\" ]]; then
    raw="${raw#\"}"
    raw="${raw%\"}"
    raw="${raw//\\\\/__POSTGRES_BS__}"
    raw="${raw//\\\"/\"}"
    raw="${raw//__POSTGRES_BS__/\\}"
    printf '%s' "$raw"
    return 0
  fi

  raw="${raw%%#*}"
  printf '%s' "$(postgres_runtime_trim "$raw")"
}

postgres_runtime_read_configuration_value() {
  local toml_path="$1"
  local key="$2"
  local raw=""

  if [[ -z "$toml_path" || ! -f "$toml_path" ]]; then
    return 0
  fi

  raw="$(
    awk -v target="$key" '
      BEGIN { in_config=0 }
      /^[[:space:]]*\[configuration\][[:space:]]*$/ {
        in_config=1
        next
      }
      /^[[:space:]]*\[[^]]+\][[:space:]]*$/ {
        in_config=0
      }
      in_config && $0 ~ "^[[:space:]]*" target "[[:space:]]*=" {
        line=$0
        sub(/^[[:space:]]*[^=]+=[[:space:]]*/, "", line)
        print line
        exit
      }
    ' "$toml_path"
  )"

  postgres_runtime_decode_toml_value "$raw"
}

postgres_runtime_resolve_project_root() {
  local root_override="${DB_PROJECT_ROOT:-}"
  local root="$root_override"

  if [[ -z "$root" && -x "$(command -v git)" ]]; then
    root="$(git -C "$PWD" rev-parse --show-toplevel 2>/dev/null || true)"
  fi
  if [[ -z "$root" ]]; then
    root="$PWD"
  fi
  if [[ -z "$root_override" ]]; then
    case "$root" in
      "$POSTGRES_RUNTIME_SKILL_ROOT"|"$POSTGRES_RUNTIME_SKILL_ROOT"/*)
        root=""
        ;;
    esac
  fi

  printf '%s' "$root"
}

postgres_runtime_resolve_toml_path() {
  local project_root="$1"
  if [[ -z "$project_root" ]]; then
    project_root="$(postgres_runtime_resolve_project_root)"
  fi
  if [[ -z "$project_root" ]]; then
    return 0
  fi
  printf '%s/.skills/postgres/postgres.toml' "$project_root"
}

postgres_runtime_schema_version() {
  local toml_path="$1"
  postgres_runtime_read_configuration_value "$toml_path" "schema_version"
}

postgres_runtime_normalize_bin_dir() {
  local path="$1"
  local trimmed="${1%/}"
  if [[ -z "$path" ]]; then
    return 0
  fi
  if [[ -f "$trimmed" || "$trimmed" == *.exe || "${trimmed##*/}" == "psql" ]]; then
    dirname "$trimmed"
  else
    printf '%s' "$trimmed"
  fi
}

postgres_runtime_normalize_sslmode() {
  local raw="${1:-}"
  local lowered=""
  if [[ -z "$raw" ]]; then
    return 0
  fi
  lowered="$(printf '%s' "$raw" | tr '[:upper:]' '[:lower:]')"
  case "$lowered" in
    true|t|1|yes|y|on|enable|enabled|require|required|verify-ca|verify-full)
      echo "require"
      ;;
    false|f|0|no|n|off|disable|disabled)
      echo "disable"
      ;;
    *)
      echo "$raw"
      ;;
  esac
}

postgres_runtime_connection_sslmode() {
  local conn="$1"
  local query raw

  if [[ -z "$conn" ]]; then
    return 0
  fi

  if [[ "$conn" == *"://"* ]]; then
    query="${conn#*\?}"
    raw=""
    if [[ "$query" != "$conn" ]]; then
      query="${query%%#*}"
      local pair
      IFS='&' read -r -a pairs <<< "$query"
      for pair in "${pairs[@]}"; do
        case "$pair" in
          sslmode=*)
            raw="${pair#sslmode=}"
            break
            ;;
        esac
      done
    fi
    postgres_runtime_normalize_sslmode "$raw"
    return 0
  fi

  postgres_runtime_python_exec "" - "$conn" <<'PY'
import shlex
import sys

conn = sys.argv[1]

try:
    tokens = shlex.split(conn)
except ValueError:
    tokens = conn.split()

for token in tokens:
    if "=" not in token:
        continue
    key, value = token.split("=", 1)
    if key == "sslmode":
        print(value.strip())
        break
PY
}

postgres_runtime_connection_set_sslmode() {
  local conn="$1"
  local sslmode="$2"

  postgres_runtime_python_exec "" - "$conn" "$sslmode" <<'PY'
import shlex
import sys
import urllib.parse

conn = sys.argv[1]
sslmode = sys.argv[2]

if "://" in conn:
    parsed = urllib.parse.urlparse(conn)
    if parsed.scheme:
        query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        query["sslmode"] = [sslmode]
        new_query = urllib.parse.urlencode(query, doseq=True)
        print(urllib.parse.urlunparse(parsed._replace(query=new_query)))
        raise SystemExit(0)

try:
    tokens = shlex.split(conn)
except ValueError:
    tokens = conn.split()

params = []
seen = False
for token in tokens:
    if "=" not in token:
        continue
    key, value = token.split("=", 1)
    if key == "sslmode":
        value = sslmode
        seen = True
    params.append((key, value))

if not seen:
    params.append(("sslmode", sslmode))

print(" ".join(f"{key}={shlex.quote(value)}" for key, value in params if value != ""))
PY
}

postgres_runtime_add_python_candidate() {
  local candidate="$1"
  local label="$2"
  local idx

  if [[ -z "$candidate" ]]; then
    return 0
  fi

  for ((idx=0; idx<${#POSTGRES_RUNTIME_PYTHON_CANDIDATES[@]}; idx++)); do
    if [[ "${POSTGRES_RUNTIME_PYTHON_CANDIDATES[$idx]}" == "$candidate" ]]; then
      return 0
    fi
  done

  POSTGRES_RUNTIME_PYTHON_CANDIDATES+=("$candidate")
  POSTGRES_RUNTIME_PYTHON_LABELS+=("$label")
}

postgres_runtime_collect_python_candidates() {
  local toml_path="$1"
  local version
  local candidate
  local config_python=""

  POSTGRES_RUNTIME_PYTHON_CANDIDATES=()
  POSTGRES_RUNTIME_PYTHON_LABELS=()

  if [[ -n "$toml_path" && -f "$toml_path" ]]; then
    config_python="$(postgres_runtime_read_configuration_value "$toml_path" "python_bin")"
    if [[ -n "$config_python" ]]; then
      POSTGRES_RUNTIME_PYTHON_CONFIGURED="$config_python"
    fi
  fi

  postgres_runtime_add_python_candidate "python3" "PATH:python3"
  for version in 15 14 13 12 11; do
    postgres_runtime_add_python_candidate "python3.${version}" "PATH:python3.${version}"
  done

  for candidate in \
    /opt/homebrew/bin/python3 \
    /usr/local/bin/python3
  do
    postgres_runtime_add_python_candidate "$candidate" "common:${candidate}"
  done

  for version in 15 14 13 12 11; do
    postgres_runtime_add_python_candidate "/opt/homebrew/bin/python3.${version}" "common:/opt/homebrew/bin/python3.${version}"
    postgres_runtime_add_python_candidate "/usr/local/bin/python3.${version}" "common:/usr/local/bin/python3.${version}"
    postgres_runtime_add_python_candidate "/opt/homebrew/opt/python@3.${version}/bin/python3.${version}" "brew:/opt/homebrew/opt/python@3.${version}/bin/python3.${version}"
    postgres_runtime_add_python_candidate "/usr/local/opt/python@3.${version}/bin/python3.${version}" "brew:/usr/local/opt/python@3.${version}/bin/python3.${version}"
  done

  if command -v pyenv >/dev/null 2>&1; then
    candidate="$(pyenv which python3 2>/dev/null || true)"
    postgres_runtime_add_python_candidate "$candidate" "pyenv"
  fi

  if command -v asdf >/dev/null 2>&1; then
    candidate="$(asdf which python3 2>/dev/null || true)"
    postgres_runtime_add_python_candidate "$candidate" "asdf"
  fi
}

postgres_runtime_probe_python() {
  local candidate="$1"
  local resolved="$candidate"
  local output

  if [[ -z "$candidate" ]]; then
    return 1
  fi

  if [[ "$candidate" != */* ]]; then
    resolved="$(command -v "$candidate" 2>/dev/null || true)"
  fi
  if [[ -z "$resolved" || ! -x "$resolved" ]]; then
    return 1
  fi

  output="$(
    "$resolved" -c 'import sys, tomllib; print(sys.executable); print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null
  )" || return 1

  POSTGRES_RUNTIME_PROBED_PYTHON="$(printf '%s\n' "$output" | sed -n '1p')"
  POSTGRES_RUNTIME_PROBED_PYTHON_VERSION="$(printf '%s\n' "$output" | sed -n '2p')"
  [[ -n "$POSTGRES_RUNTIME_PROBED_PYTHON" ]]
}

postgres_runtime_resolve_python() {
  local toml_path="$1"
  local idx
  local source_label=""
  local detected=""

  if [[ "${POSTGRES_RUNTIME_PYTHON_CACHE_TOML_PATH:-__unset__}" == "$toml_path" && -n "${POSTGRES_RUNTIME_PYTHON_BIN:-}" ]]; then
    printf '%s' "$POSTGRES_RUNTIME_PYTHON_BIN"
    return 0
  fi

  POSTGRES_RUNTIME_PYTHON_BIN=""
  POSTGRES_RUNTIME_PYTHON_SOURCE=""
  POSTGRES_RUNTIME_PYTHON_VERSION=""
  POSTGRES_RUNTIME_PYTHON_CACHE_TOML_PATH="$toml_path"
  POSTGRES_RUNTIME_PYTHON_CONFIGURED=""

  if [[ -n "${DB_PYTHON_BIN:-}" ]]; then
    if postgres_runtime_probe_python "${DB_PYTHON_BIN}"; then
      POSTGRES_RUNTIME_PYTHON_BIN="$POSTGRES_RUNTIME_PROBED_PYTHON"
      POSTGRES_RUNTIME_PYTHON_SOURCE="env"
      POSTGRES_RUNTIME_PYTHON_VERSION="$POSTGRES_RUNTIME_PROBED_PYTHON_VERSION"
      printf '%s' "$POSTGRES_RUNTIME_PYTHON_BIN"
      return 0
    fi
    echo "DB_PYTHON_BIN must point to a usable Python 3.11+ interpreter with tomllib. Got: ${DB_PYTHON_BIN}" >&2
    return 1
  fi

  postgres_runtime_collect_python_candidates "$toml_path"

  if [[ -n "${POSTGRES_RUNTIME_PYTHON_CONFIGURED:-}" ]]; then
    if postgres_runtime_probe_python "$POSTGRES_RUNTIME_PYTHON_CONFIGURED"; then
      POSTGRES_RUNTIME_PYTHON_BIN="$POSTGRES_RUNTIME_PROBED_PYTHON"
      POSTGRES_RUNTIME_PYTHON_SOURCE="toml"
      POSTGRES_RUNTIME_PYTHON_VERSION="$POSTGRES_RUNTIME_PROBED_PYTHON_VERSION"
      printf '%s' "$POSTGRES_RUNTIME_PYTHON_BIN"
      return 0
    fi
  fi

  for ((idx=0; idx<${#POSTGRES_RUNTIME_PYTHON_CANDIDATES[@]}; idx++)); do
    detected="${POSTGRES_RUNTIME_PYTHON_CANDIDATES[$idx]}"
    source_label="${POSTGRES_RUNTIME_PYTHON_LABELS[$idx]}"
    if postgres_runtime_probe_python "$detected"; then
      POSTGRES_RUNTIME_PYTHON_BIN="$POSTGRES_RUNTIME_PROBED_PYTHON"
      POSTGRES_RUNTIME_PYTHON_SOURCE="$source_label"
      POSTGRES_RUNTIME_PYTHON_VERSION="$POSTGRES_RUNTIME_PROBED_PYTHON_VERSION"
      if [[ -n "${POSTGRES_RUNTIME_PYTHON_CONFIGURED:-}" ]]; then
        echo "Configured python_bin '${POSTGRES_RUNTIME_PYTHON_CONFIGURED}' is not usable. Falling back to '${POSTGRES_RUNTIME_PYTHON_BIN}'." >&2
      fi
      printf '%s' "$POSTGRES_RUNTIME_PYTHON_BIN"
      return 0
    fi
  done

  if [[ -n "${POSTGRES_RUNTIME_PYTHON_CONFIGURED:-}" ]]; then
    echo "Configured python_bin '${POSTGRES_RUNTIME_PYTHON_CONFIGURED}' is not usable." >&2
  fi
  echo "No usable Python 3.11+ interpreter with tomllib was found. Checked DB_PYTHON_BIN, [configuration].python_bin, python3/python3.15..python3.11 on PATH, common Homebrew locations, and pyenv/asdf." >&2
  return 1
}

postgres_runtime_python_exec() {
  local toml_path="$1"
  shift
  local python_bin
  python_bin="$(postgres_runtime_resolve_python "$toml_path")" || return 1
  "$python_bin" "$@"
}
