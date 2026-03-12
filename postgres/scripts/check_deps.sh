#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/runtime_env.sh"

required=(psql pg_dump pg_restore)
optional=(diff)

missing=()

echo "Required:"
for cmd in "${required[@]}"; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "  ok   $cmd"
  else
    echo "  missing $cmd"
    missing+=("$cmd")
  fi
done

toml_path="$(postgres_runtime_resolve_toml_path "$(postgres_runtime_resolve_project_root)")"
if python_bin="$(postgres_runtime_resolve_python "$toml_path" 2>/dev/null)"; then
  python_version="$("$python_bin" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null || true)"
  echo "  ok   python (${python_bin}${python_version:+, ${python_version}})"
else
  echo "  missing python>=3.11 (tomllib for postgres.toml profiles)"
  missing+=("python>=3.11")
fi

echo ""
echo "Optional:"
for cmd in "${optional[@]}"; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "  ok   $cmd"
  else
    echo "  missing $cmd"
  fi
done

if (( ${#missing[@]} == 0 )); then
  exit 0
fi

echo ""
echo "Install hints:"
case "$(uname -s 2>/dev/null || echo unknown)" in
  Darwin)
    echo "  macOS: brew install postgresql"
    ;;
  Linux)
    echo "  Ubuntu/Debian: sudo apt install -y postgresql-client"
    echo "  Fedora: sudo dnf install -y postgresql"
    ;;
  MINGW*|MSYS*|CYGWIN*)
    echo "  Windows: winget install PostgreSQL.PostgreSQL"
    echo "  Windows (diff): install Git or diffutils for diff.exe"
    ;;
  *)
    echo "  Install PostgreSQL client tools for psql/pg_dump/pg_restore."
    ;;
esac

exit 1
