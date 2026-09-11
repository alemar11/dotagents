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

## Codex

For all projects, run:

```sh
codex mcp add discourse -- npx -y @discourse/mcp@latest
```

Check first with `codex mcp get discourse`; leave an existing entry unchanged
unless the user explicitly requests replacement. Authenticate or provide
secrets only through the server's supported environment variables or auth flow.

For one repository, merge this block into `<project>/.codex/config.toml`:

```toml
[mcp_servers.discourse]
command = "npx"
args = ["-y", "@discourse/mcp@latest"]
```

Commit project configuration only when the repository intentionally shares this
tool. Codex project configuration is loaded for trusted projects and is merged
with the user-level configuration.

## Cursor

For all projects, merge this entry into `~/.cursor/mcp.json`:

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

For one repository, merge it into `<project>/.cursor/mcp.json` and commit that
file only when the project should share the server. Cursor merges global and
project files, with the project definition taking priority for the same name.
The Cursor CLI (`agent`) and editor use these same files.

## Use and verification

Verify Codex with `codex mcp list`, or Cursor with `agent mcp list` and
`agent mcp list-tools discourse`. Start a fresh session after changing config.
If startup or authentication fails, report the exact prerequisite or server
error and fix configuration rather than claiming the MCP is ready.
