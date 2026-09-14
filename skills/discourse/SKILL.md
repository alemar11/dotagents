---
name: discourse
description: Set up, repair, or verify Discourse MCP configuration and authentication for Codex or Cursor.
---

# Discourse MCP

Use this skill for MCP setup, repair, or connection inspection. Ordinary
Discourse reads and writes use the connected tools and do not require setup.
Keep inspection read-only; a setup or repair request authorizes relevant
configuration changes. The local server is launched with `npx` and requires a
working Node.js/npm installation. The package may request authentication or
additional configuration when it starts; follow the package's current prompts
and never place tokens in a repository file.

Inspect existing configuration before changing it. Preserve unrelated servers,
environment variables, and credentials. If `npx` is unavailable, report the
Node.js/npm prerequisite and stop.

## MCP configuration

Prefer project scope so the repository declares the tool it needs and teammates
can reproduce the setup. Inspect existing entries first, preserve unrelated
servers and credentials. Reuse the requested scope or existing configuration;
project scope is the default only for new setup without an established scope.

### Project scope (recommended)

For Codex, merge this block into `<project>/.codex/config.toml`. Commit only
when requested:

```toml
[mcp_servers.discourse]
command = "npx"
args = ["-y", "@discourse/mcp@latest"]
```

Codex project configuration is loaded for trusted projects and is merged with
the user-level configuration.

For Cursor, merge this entry into `<project>/.cursor/mcp.json`:

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
