---
name: hopper
description: Set up, repair, or verify Hopper Disassembler's MCP server for Codex or Cursor.
---

# Hopper MCP

Use this skill for MCP setup, repair, or connection inspection. Ordinary
disassembly work uses the connected Hopper tools and does not require setup.
Keep inspection read-only; a setup or repair request authorizes relevant
configuration changes. The server requires Hopper Disassembler on macOS.

Before changing configuration, locate the requested or configured Hopper app,
then check standard macOS app locations if needed. Derive `hopper_server` as
`<app>/Contents/MacOS/HopperMCPServer` and verify it is executable. Do not guess
an installation path. Ask about multiple copies only when the request and
existing configuration do not identify the intended one. A missing app is a
prerequisite to report, not authority to install it.

## MCP configuration

Prefer project scope so the repository declares the tool it needs and teammates
can reproduce the setup. Inspect existing entries first, preserve unrelated
servers and credentials. Reuse the requested scope or existing configuration;
project scope is the default only for new setup without an established scope.

### Project scope (recommended)

For Codex, add this block to `<project>/.codex/config.toml`. Commit only when
requested:

```toml
[mcp_servers.HopperMCPServer]
command = "<resolved HopperMCPServer path>"
```

Codex loads project configuration only for trusted projects and merges it with
the user configuration.

For Cursor, merge this entry into `<project>/.cursor/mcp.json`, replacing the
command placeholder with the resolved value of `$hopper_server`:

```json
{
  "mcpServers": {
    "HopperMCPServer": {
      "command": "<resolved HopperMCPServer path>"
    }
  }
}
```

Cursor merges global and project files; a project entry with the same name takes
priority.

### Global scope (optional)

For Codex, run this from a shell:

```sh
codex mcp add HopperMCPServer -- "$hopper_server"
```

For Cursor, merge the same JSON entry into `~/.cursor/mcp.json` instead of the
project file.

### Verification

Verify Codex with `codex mcp list`, or Cursor with `agent mcp list` (or the Cursor
MCP settings screen). Start a fresh agent session after changing configuration.

Confirm the intended client can enumerate Hopper tools. If the user supplied
an open project for verification, perform a relevant read-only inspection and
report its result. Do not require a sample, install analysis tools, or begin
binary analysis merely to prove server configuration. Report configuration,
tool discovery, and any untested connection or project access separately.
