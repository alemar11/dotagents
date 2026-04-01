#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
PROJECT_ROOT="$(postgres_runtime_resolve_project_root_or_die)" || exit 1

TOML_PATH="$PROJECT_ROOT/.skills/postgres/postgres.toml"
if [[ -x "$SCRIPT_DIR/check_toml_gitignored.sh" ]]; then
  "$SCRIPT_DIR/check_toml_gitignored.sh" "$PROJECT_ROOT" || true
fi

PYTHON_BIN="$(postgres_runtime_resolve_python "$TOML_PATH")" || exit 1

"$PYTHON_BIN" "$SCRIPT_DIR/bootstrap_profile.py" "$TOML_PATH" "$PROJECT_ROOT"
