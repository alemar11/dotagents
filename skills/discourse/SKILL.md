---
name: discourse
description: Configure the Discourse MCP server for Codex or Cursor, globally or for one project, and verify its tools and authentication.
---

# Discourse MCP

Use this skill when the user asks to set up, repair, inspect, or use Discourse
through its MCP server. The local server is launched with `npx` and requires a
working Node.js/npm installation. The package may request authentication or
additional configuration when it starts; follow the package's current prompts
and never place tokens in a repository file.

Inspect existing configuration before changing it. Preserve unrelated servers,
environment variables, and credentials. If `npx` is unavailable, report the
Node.js/npm prerequisite and stop.

## MCP configuration

Prefer project scope so the repository declares the tool it needs and teammates
can reproduce the setup. Inspect existing entries first, preserve unrelated
servers and credentials, and replace an existing entry only when the user asks.

### Project scope (recommended)

For Codex, merge this block into `<project>/.codex/config.toml` and commit it
when the project should share the setup:

```toml
[mcp_servers.discourse]
command = "npx"
args = ["-y", "@discourse/mcp@latest"]
```

Codex project configuration is loaded for trusted projects and is merged with
the user-level configuration.

For Cursor, merge this entry into `<project>/.cursor/mcp.json` and commit it only
when the project should share the server:

```json
{
  "mcpServers": {
    "discourse": {
      "command": "npx",
      "args": ["-y", "@discourse/mcp@latest"]
    }
  }
}
```

Cursor merges global and project files, with the project definition taking
priority for the same name. The Cursor CLI (`agent`) and editor use these same
files.

### Global scope (optional)

For Codex, run:

```sh
codex mcp add discourse -- npx -y @discourse/mcp@latest
```

For Cursor, merge the same JSON entry into `~/.cursor/mcp.json` instead of the
project file.

### Verification

Verify Codex with `codex mcp list`, or Cursor with `agent mcp list` and
`agent mcp list-tools discourse`. Start a fresh session after changing config.
If startup or authentication fails, report the exact prerequisite or server
error and fix configuration rather than claiming the MCP is ready.
