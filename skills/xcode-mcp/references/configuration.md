# Client Configuration and Connection

Read for requested client setup, connection verification, or workspace access.
Status-only inspection does not need this reference.

Honor requested or existing configuration scope. For a new setup, prefer project
scope so the repository declares its Xcode tooling. Configuration scope does not
restrict Xcode's permissions; verify the intended agent and folder grants
separately. Inspect existing entries and preserve unrelated servers.

Headless mode does not require the Xcode UI or an already-open project. With
headless access enabled, connect through `xcrun mcpbridge`; the service launches
on demand. To preload an existing workspace, use `xcrun mcp-server open` with
its absolute path. Do not prescribe `mcp-server start` when live help lacks it.
The UI's External Agent Access setting distinguishes Always, While Xcode is
Open, and Never; UI-bound access is not proof of headless readiness.

### Project scope (recommended)

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

When a particular Xcode installation is requested, persist its absolute
`DEVELOPER_DIR` in the bridge entry's `env` map as well as scoping setup
commands. Otherwise the later bridge process can select a different Xcode.
For Codex use `[mcp_servers.xcode.env]`; for Cursor use `env` inside the
`xcode` entry. Do not copy a machine-specific path into shared configuration
without checking that sharing it is intended. Commit only when requested.

Inspect any inherited `MCP_XCODE_PID`: it pins the bridge to an Xcode process.
For requested headless operation, remove an unintended pin from the scoped
launch environment rather than requiring the UI to remain open. Launching an
agent through Xcode may select Xcode's bundled agent and configuration; use
the user's chosen external client for its normal settings and identity.

### Global scope (optional)

For Codex, run:

```sh
codex mcp add xcode -- xcrun mcpbridge
```

For Cursor, merge the same JSON entry into `~/.cursor/mcp.json` instead of the
project file.

### Verification

Verify Codex with `codex mcp list`, or Cursor with `agent mcp list` (or the
Cursor MCP settings screen). Registration is not connection evidence: confirm
that the intended client can enumerate Xcode tools. For project access, use
the live interface to open the requested workspace; opening or creating a
project can trigger agent and folder approval before other operations work.
Do not create a project merely to test setup. For an empty repository, report
tool discovery separately from untested project access.

If headless operation is requested, observe that the Xcode UI is closed during
verification. Do not quit the user's running Xcode without authorization;
report that headless operation remains unverified if it stays open.

Exporting Apple's development skills is a separate explicit `xcode-skills`
task. This setup skill does not install them or perform builds, previews, or
simulator workflows as incidental verification.
