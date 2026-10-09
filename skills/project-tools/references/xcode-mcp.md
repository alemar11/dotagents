# Project-local Xcode MCP Configuration

Configure Apple's native `xcrun mcpbridge` in the requested client's repository
configuration. This workflow writes client configuration; it does not enable
headless mode, approve agents or folders, or start, stop, or reset the service.

## Prerequisites

Confirm macOS and the selected Xcode with `xcodebuild -version` and
`xcode-select -p`. If another Xcode was requested, scope `DEVELOPER_DIR` to the
inspection commands without changing global selection. Check
`xcrun --find mcpbridge` and its live help. If the bridge is unavailable, report
the selected Xcode and the missing prerequisite; do not substitute a different
MCP implementation or install Xcode.

Inspect the target configuration and preserve unrelated entries. Resolve the
file and parent directory paths before writing; do not follow a project config
link into a global file. Reconcile an existing `xcode` entry rather than adding
a duplicate. Leave global MCP configuration unchanged.

## Repository configuration

For Codex, merge this block into `<project>/.codex/config.toml`:

```toml
[mcp_servers.xcode]
command = "xcrun"
args = ["mcpbridge"]
```

For Cursor, merge this entry into `<project>/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "xcode": {
      "command": "xcrun",
      "args": ["mcpbridge"]
    }
  }
}
```

Codex project configuration is loaded for trusted projects. Cursor merges
project and global MCP files, with the project entry taking priority for the
same name.

### Claude Code

From the repository root, inspect `claude mcp add --help`, then configure a
project-scoped stdio server:

```sh
claude mcp add --scope project --transport stdio xcode -- xcrun mcpbridge
```

Alternatively, merge the JSON entry shown above into `<project>/.mcp.json`.
Preserve unrelated entries and reconcile an existing `xcode` entry before
replacing it. Claude Code's default MCP scope is `local`, which stores data
under the user's home directory; it is not the project file. Always pass
`--scope project`. If client approval or Xcode access is pending, report it as
a prerequisite; do not change trust settings or access grants.

### Pi

Check `pi --version` and `pi mcp --help` for native MCP support. From the
repository root, merge the same JSON entry into `<project>/.pi/mcp.json`, or
use the supported project-scoped command:

```sh
pi mcp add xcode --local -- xcrun mcpbridge
```

Inspect an existing entry first: `add` can replace it. Without `--local`, Pi
writes user-level configuration. Pi loads the project file after project trust
is granted. For requested discovery verification in a running session,
`/reload` picks up external configuration changes. If the installed Pi lacks
native MCP support, report the version and limitation; do not install an
unrelated extension or invent a config schema.

### Selected Xcode

When a particular Xcode installation is requested, persist its absolute
`DEVELOPER_DIR` in the bridge entry's `env` map as well as scoping setup
commands. Otherwise the later bridge process can select a different Xcode.
For Codex use `[mcp_servers.xcode.env]`; for Cursor, Claude Code, and Pi use
`env` inside the `xcode` JSON entry. Do not copy a machine-specific path into
shared configuration without checking that sharing it is intended. Commit only
when requested.

Use the external client selected by the user. Do not launch another client or
change the host environment to make this repository configuration work.

## Verification

Parse the resulting JSON or TOML, inspect the scoped repository diff, and
confirm that only the requested project entries changed. Report the absolute
configuration path and selected Xcode. A valid configuration file does not
prove a live connection or workspace access.

When connection verification is requested, inspect the intended client's live
Xcode entry and discovered tools, provided the existing host setup permits it:

| Client | Connection inspection |
| --- | --- |
| Codex | Live MCP registration and tool discovery |
| Cursor | MCP settings and live tool discovery |
| Claude Code | `/mcp` in the active session |
| Pi | `/mcp` in the active session |

Connecting the configured client may start its stdio bridge on demand; do not
add separate server-launch or lifecycle commands. Avoid broad checks such as
`pi mcp list`, which connects to every enabled server, when inspecting only
Xcode. If client trust, Xcode permissions, or host enablement are missing, report
configuration as written and connection as unverified or blocked. Do not
approve access, open workspaces, quit Xcode, enable headless mode, or run builds
and simulators to complete this configuration task.

## Sources

- [Apple's native Xcode bridge](https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode)
- [Codex project MCP configuration](https://developers.openai.com/codex/mcp)
- [Cursor MCP configuration](https://cursor.com/docs/mcp)
- [Claude Code MCP configuration](https://code.claude.com/docs/en/mcp)
- [Pi MCP configuration](https://pi.dev/docs/latest/mcp)
