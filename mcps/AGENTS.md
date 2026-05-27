# MCP Installer Guidelines

## Purpose
This folder owns small scripts for recreating global Codex MCP server entries on
new machines.

`install-global-mcps.sh` should install MCP servers that the user wants available
globally through `~/.codex/config.toml`, but that are not bundled with Codex
itself.

## Scope
- Include external MCP servers that can be installed or registered repeatably on
  another machine.
- Exclude Codex-bundled MCP servers such as `node_repl`; those are installed and
  managed by Codex.app.
- Prefer `codex mcp add`, `codex mcp remove`, and `codex mcp list` over direct
  edits to `~/.codex/config.toml`. Direct config edits are allowed only for
  state that the Codex CLI cannot currently persist, such as setting an
  installed MCP entry to `enabled = false`.
- Keep the script idempotent: leave existing entries, including their current
  `enabled` state, unchanged by default. Replace entries only when the user
  passes `--force`.
- Install `chrome-devtools` as disabled only when the entry is missing or when
  `--force` is used. Do not change the enabled state of an existing entry during
  a normal install.

## Maintenance
- When adding an MCP, document its exact `codex mcp add` command in
  `README.md` and add a matching installer branch in `install-global-mcps.sh`.
- If an MCP requires a host application, check for the app bundle first and then
  the specific executable path, and report clearly when either is missing.
- If an MCP requires `npx` or another package manager, verify that dependency
  before installation and fail with an actionable message.
- Keep command names stable unless the Codex MCP entry itself is intentionally
  renamed.
- Do not write secrets, tokens, or machine-local credentials into this folder.
  Use Codex MCP auth flows or environment-variable references instead.
- Validate changes with:

```sh
bash -n mcps/install-global-mcps.sh
shellcheck mcps/install-global-mcps.sh
./mcps/install-global-mcps.sh --dry-run
git diff --check -- mcps README.md AGENTS.md
```
