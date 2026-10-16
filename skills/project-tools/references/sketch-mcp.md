# Project-local Sketch MCP

Configure Sketch's built-in streamable HTTP server only when MCP setup is
requested. Use this reference alongside the [GitHub skill procedure](github-skills.md)
when both MCP and skills are requested; either operation can finish independently.

## Prerequisites and endpoint

Sketch MCP requires the macOS app from sketch.com, version 2025.2.4 or later;
the Mac App Store version does not include it. The user must already have
started the server in Sketch through the Command Bar's Start MCP Server or
Settings > General > MCP Server, with Local Network access allowed if macOS
requires it. Report missing host prerequisites without installing Sketch,
starting the server, granting permissions, or changing its port.

Use `http://localhost:31126/mcp` by default. Preserve an explicitly selected or
verified custom local endpoint; do not reset it to the default. The client
must run on the same Mac as Sketch. A remote client cannot reach this server
through its own localhost; report that limitation rather than adding a tunnel
or substituting a hosted service.

Inspect existing registrations before writing. Reuse the entry for the same
Sketch endpoint, using `sketch` for a new entry; resolve a conflicting name or
endpoint before replacing it. Preserve unrelated entries and global config.
Resolve the destination and its parents inside the repository, rejecting links
that escape it.

## Repository configuration

Merge only the requested clients' entries into their project files:

| Client | Repository file |
| --- | --- |
| Codex | `.codex/config.toml` |
| Cursor | `.cursor/mcp.json` |
| Pi | `.pi/mcp.json` |
| Claude Code | `.mcp.json` |

For Codex:

```toml
[mcp_servers.sketch]
url = "http://localhost:31126/mcp"
```

For Cursor, Pi, or Claude Code:

```json
{
  "mcpServers": {
    "sketch": {
      "type": "http",
      "url": "http://localhost:31126/mcp"
    }
  }
}
```

Substitute the reconciled entry name and endpoint when different. Use direct
HTTP configuration, not an npm server, stdio proxy, or marketplace plugin.
Do not copy the upstream Codex home-directory example or use client commands
that default to user scope. Existing project trust is a prerequisite; for Pi,
require native MCP support rather than installing an extension.

## Verify

Parse the changed TOML/JSON and inspect the scoped diff. Report each file,
registration, and endpoint separately from connection status. An unavailable
server does not prevent writing the requested repository configuration or
installing the skills; mark the connection unverified or blocked.

When live discovery is available, inspect only the requested client's Sketch
registration and tools. Report any needed client reload or host enablement
without performing host repair. A connection does not prove access to the
intended open document. Do not modify documents, export assets, or run a design
workflow as a setup test.

## Sources

- [Official Sketch agent bundle](https://github.com/sketch-hq/agents)
- [Sketch MCP server and client setup](https://www.sketch.com/docs/mcp-server/)
- [Codex project MCP configuration](https://developers.openai.com/codex/mcp)
- [Cursor MCP configuration](https://cursor.com/docs/mcp)
- [Claude Code MCP configuration](https://code.claude.com/docs/en/mcp)
- [Pi MCP configuration](https://pi.dev/docs/latest/mcp)
