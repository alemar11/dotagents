#!/usr/bin/env bash

set -euo pipefail

force=false
dry_run=false

usage() {
  cat <<'EOF'
Install global Codex MCP server entries that are not bundled with Codex itself.

Usage:
  mcps/install-global-mcps.sh [options]

Options:
  --force                 Replace existing MCP entries with the repo defaults.
  --dry-run               Print the commands that would run.
  -h, --help              Show this help.

Default MCPs:
  XcodeBuildMCP    npx -y xcodebuildmcp@latest mcp
  discourse        npx -y @discourse/mcp@latest
  HopperMCPServer  /Applications/Hopper Disassembler.app/Contents/MacOS/HopperMCPServer

Codex-bundled MCPs such as node_repl are intentionally not installed here.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --force)
      force=true
      ;;
    --dry-run)
      dry_run=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

run() {
  if [ "$dry_run" = true ]; then
    printf '+'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

require_command() {
  command_name="$1"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    exit 1
  fi
}

mcp_exists() {
  codex mcp get "$1" >/dev/null 2>&1
}

codex_config_file() {
  if [ -n "${CODEX_CONFIG_FILE:-}" ]; then
    printf '%s\n' "$CODEX_CONFIG_FILE"
  else
    printf '%s\n' "${CODEX_HOME:-$HOME/.codex}/config.toml"
  fi
}

set_mcp_disabled() {
  name="$1"
  config_file="$(codex_config_file)"

  if [ "$dry_run" = true ]; then
    printf '+ set %q enabled=false in %q\n' "$name" "$config_file"
    return 0
  fi

  if [ ! -f "$config_file" ]; then
    echo "Codex config file not found: $config_file" >&2
    exit 1
  fi

  temp_file="$(mktemp "$config_file.XXXXXX")"
  awk -v name="$name" '
    BEGIN {
      target = "[mcp_servers." name "]"
      in_target = 0
      saw_enabled = 0
    }
    function flush_enabled() {
      if (in_target && !saw_enabled) {
        print "enabled = false"
      }
    }
    /^\[mcp_servers\.[^]]+\]$/ {
      flush_enabled()
      in_target = ($0 == target)
      saw_enabled = 0
      print
      next
    }
    /^\[/ {
      flush_enabled()
      in_target = 0
      saw_enabled = 0
      print
      next
    }
    in_target && /^enabled[[:space:]]*=/ {
      print "enabled = false"
      saw_enabled = 1
      next
    }
    { print }
    END {
      flush_enabled()
    }
  ' "$config_file" > "$temp_file"
  mv "$temp_file" "$config_file"
}

install_stdio_mcp() {
  name="$1"
  shift

  if mcp_exists "$name"; then
    if [ "$force" = true ]; then
      echo "Replacing MCP: $name"
      run codex mcp remove "$name"
    else
      echo "$name already exists. Leaving current settings unchanged. Use --force to replace it."
      return 0
    fi
  else
    echo "Installing MCP: $name"
  fi

  run codex mcp add "$name" -- "$@"
}

install_disabled_stdio_mcp() {
  name="$1"
  shift

  if mcp_exists "$name"; then
    if [ "$force" = true ]; then
      echo "Replacing MCP as disabled: $name"
      run codex mcp remove "$name"
      run codex mcp add "$name" -- "$@"
    else
      echo "$name already exists. Leaving current settings unchanged. Use --force to replace it."
      return 0
    fi
  else
    echo "Installing MCP as disabled: $name"
    run codex mcp add "$name" -- "$@"
  fi

  set_mcp_disabled "$name"
}

require_command codex

if ! command -v npx >/dev/null 2>&1; then
  echo "Missing required command: npx" >&2
  echo "Install Node.js/npm first, then rerun this installer." >&2
  exit 1
fi

install_stdio_mcp XcodeBuildMCP npx -y xcodebuildmcp@latest mcp
install_stdio_mcp discourse npx -y @discourse/mcp@latest

hopper_app="/Applications/Hopper Disassembler.app"
hopper_server="/Applications/Hopper Disassembler.app/Contents/MacOS/HopperMCPServer"
if [ ! -d "$hopper_app" ]; then
  echo "HopperMCPServer app not found: $hopper_app"
elif [ -x "$hopper_server" ]; then
  install_stdio_mcp HopperMCPServer "$hopper_server"
else
  echo "HopperMCPServer executable not found: $hopper_server"
fi

echo
echo "Installed external MCP entries:"
run codex mcp list
