# Project-local Hopper MCP Configuration

Configure Hopper Disassembler's bundled MCP server only when requested.
Inspection is read-only; setup or repair authorizes the relevant repository
configuration changes. Ordinary disassembly uses the connected tools and does
not require this setup workflow.

## Prerequisites and existing configuration

The server requires Hopper Disassembler on macOS. Locate the requested or
configured app, then check standard macOS app locations if needed. Derive
`hopper_server` as `<app>/Contents/MacOS/HopperMCPServer` and verify that it is
executable. Do not guess an installation path. Ask about multiple copies only
when the request and existing configuration do not identify the intended one.
Report a missing app or bundled server without installing a replacement.

Inspect existing entries and resolve the target file and parent directories
before writing. Reject project config links that escape the repository.
Preserve unrelated servers, credentials, and global configuration. Use `hopper`
for a new registration; reconcile an existing registration for the same server
under its current name, including the historical `HopperMCPServer` name, rather
than creating a duplicate. If a global registration already supplies the server,
report it and use the same name for an explicitly requested project override.
Do not remove or rewrite the global entry.

## Repository configuration

Replace the command placeholder with the verified absolute executable path.
For Codex, merge this block into `<project>/.codex/config.toml`:

```toml
[mcp_servers.hopper]
command = "<resolved HopperMCPServer path>"
```

For Cursor, merge this entry into `<project>/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "hopper": {
      "command": "<resolved HopperMCPServer path>"
    }
  }
}
```

Codex loads project configuration for trusted projects. Cursor merges project
and global MCP files, with the project entry taking priority for the same name.
Keep a discovered installation path local unless sharing that machine-specific
path is intended. Commit only when requested.

### Claude Code

Merge the same JSON entry into `<project>/.mcp.json`. Alternatively, inspect
`claude mcp add --help` and, from the repository root with `hopper_server` set to
the verified path, use:

```sh
claude mcp add --scope project --transport stdio hopper -- "$hopper_server"
```

Use the reconciled registration name when it differs. Always specify
`--scope project`: Claude Code's default `local` scope stores configuration
under the user's home directory rather than in the project file.

### Pi

Check `pi --version` and `pi mcp --help` for native MCP support. Merge the same
JSON entry into `<project>/.pi/mcp.json`, or use the supported command from the
repository root with `hopper_server` set to the verified path:

```sh
pi mcp add hopper --local -- "$hopper_server"
```

Use the reconciled registration name when it differs. Inspect existing entries
first because `add` can replace them. Without `--local`, Pi writes user-level
configuration. Project loading requires trust; `/reload` picks up external
configuration changes in a running session. If native MCP support is unavailable,
report the version and limitation rather than installing an extension.

## Verification

Parse the resulting TOML or JSON and inspect the scoped diff. Report the target
configuration path and resolved server executable. Valid configuration does
not prove a connection or access to an open Hopper document.

When connection verification is requested and host prerequisites permit it,
inspect only the intended client's Hopper registration and discovered tools:
live MCP discovery in Codex, MCP settings in Cursor, or `/mcp` in Claude Code
and Pi. A configured client may spawn its stdio server on demand; do not add a
separate launch or lifecycle workflow. Avoid broad checks that connect to all
configured servers.

If the user supplied an open Hopper document for verification, perform a
relevant read-only inspection. Do not open binaries, start analysis, install
analysis tools, change host permissions, or require a sample merely to verify
configuration. Report configuration, tool discovery, and untested document
access separately; missing host enablement remains a reported prerequisite.

## Sources

- [Hopper Disassembler and its integrated MCP server](https://www.hopperapp.com/)
- [Codex MCP configuration](https://developers.openai.com/codex/mcp)
- [Cursor MCP configuration](https://cursor.com/docs/mcp)
- [Claude Code MCP configuration](https://code.claude.com/docs/en/mcp)
- [Pi MCP configuration](https://pi.dev/docs/latest/mcp)
