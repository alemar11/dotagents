# Xcode

Xcode is a repo-local developer-tools plugin for official Xcode release notes
and Apple's native headless MCP server.

| Skill | Purpose |
| --- | --- |
| `xcode:whats-new` | Resolve release notes for the active, latest, or a requested Xcode version. |
| `xcode:mcp` | Safely launch and verify the Xcode-provided headless MCP server on attended Macs, unattended hosts, or explicitly isolated CI machines. |

The plugin does not bundle an MCP server. The MCP skill operates the launcher
provided by the selected Xcode installation and never substitutes
XcodeBuildMCP.
