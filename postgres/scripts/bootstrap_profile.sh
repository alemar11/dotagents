#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
  cat <<'EOF'
Usage: bootstrap_profile.sh [--help]

Interactive Postgres profile bootstrap.

- Run from the target project root, or set DB_PROJECT_ROOT explicitly.
- Writes/updates .skills/postgres/postgres.toml only if you choose to save.
- Scans project files for likely DB configs; it does not read environment variables.

Optional environment:
- DB_PROJECT_ROOT=/path/to/project
- DB_PROFILE_SCAN_MODE=fast|full
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ $# -gt 0 ]]; then
  echo "Unknown argument: $1" >&2
  usage >&2
  exit 2
fi

source "$SCRIPT_DIR/runtime_env.sh"
if [[ -n "${PROJECT_ROOT+x}" ]]; then
  echo "Unsupported environment variable 'PROJECT_ROOT'. Use 'DB_PROJECT_ROOT' instead." >&2
  exit 1
fi

ROOT_OVERRIDE="${DB_PROJECT_ROOT:-}"
PROJECT_ROOT="$ROOT_OVERRIDE"
if [[ -z "$PROJECT_ROOT" && -x "$(command -v git)" ]]; then
  PROJECT_ROOT="$(git -C "$PWD" rev-parse --show-toplevel 2>/dev/null || true)"
fi
if [[ -z "$PROJECT_ROOT" ]]; then
  PROJECT_ROOT="$PWD"
fi
if [[ -z "$ROOT_OVERRIDE" ]]; then
  case "$PROJECT_ROOT" in
    "$SKILL_ROOT"|"$SKILL_ROOT"/*)
      echo "Project root resolved to the postgres skill directory: $SKILL_ROOT" >&2
      echo "Run this from the postgres skill directory with DB_PROJECT_ROOT set (or run from your project root)." >&2
      exit 1
      ;;
  esac
fi

TOML_PATH="$PROJECT_ROOT/.skills/postgres/postgres.toml"
if [[ -x "$SCRIPT_DIR/check_toml_gitignored.sh" ]]; then
  "$SCRIPT_DIR/check_toml_gitignored.sh" "$PROJECT_ROOT" || true
fi

PYTHON_BIN="$(postgres_runtime_resolve_python "$TOML_PATH")" || exit 1

"$PYTHON_BIN" "$SCRIPT_DIR/bootstrap_profile.py" "$TOML_PATH" "$PROJECT_ROOT"
