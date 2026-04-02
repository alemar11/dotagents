#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for arg in "$@"; do
  case "$arg" in
    -h|--help)
      exec python3 "$SCRIPT_DIR/lists_manage.py" "$@"
      ;;
  esac
done

source "$SCRIPT_DIR/../core/github_lib.sh"
github_preflight_user_scope
exec python3 "$SCRIPT_DIR/lists_manage.py" "$@"
