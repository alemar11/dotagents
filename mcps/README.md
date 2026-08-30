# Codex MCP Installers

This folder contains scripts for installing global Codex MCP server entries that
are not bundled with Codex itself.

Run the default external MCP installer:

```sh
./mcps/install-global-mcps.sh
```

Replace existing entries with the repo defaults:

```sh
./mcps/install-global-mcps.sh --force
```

Preview the commands without changing the Codex config:

```sh
./mcps/install-global-mcps.sh --dry-run
```

The default set installs:

- `XcodeBuildMCP`: `npx -y xcodebuildmcp@latest mcp`
- `discourse`: `npx -y @discourse/mcp@latest`
- `HopperMCPServer`: `/Applications/Hopper Disassembler.app/Contents/MacOS/HopperMCPServer`, after checking that Hopper is installed

Codex-bundled MCPs such as `node_repl` are intentionally excluded.
