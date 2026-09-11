---
name: xcode-mcp
description: "Configure, launch, or diagnose Apple’s native headless Xcode MCP server on macOS."
---

# Xcode MCP

Safely prepare, start, and verify the headless MCP server shipped with Xcode.
This skill operates Apple's `xcrun mcp-server`; it does not install or
substitute XcodeBuildMCP, or perform general Apple platform development work.

## State model

Before interpreting status or choosing a launch branch, read the canonical
[state model](references/states.md). Keep the selected Xcode, permission state,
server state, agent authorization, and launch outcome distinct.

When setup provenance or command safety is disputed, read
[sources](references/sources.md). The selected Xcode's live help remains
execution authority.

## Discovery gate

Confirm the host is macOS and resolve the active Xcode with
`xcodebuild -version` and `xcode-select -p`. When the user identifies another
installed Xcode, scope `DEVELOPER_DIR` to every command and pass it explicitly
inside elevated commands. Do not change global `xcode-select` unless requested.

Run `xcrun --find mcp-server` for that Xcode. On failure, immediately return
`unsupported` with the exact Xcode and developer directory. Stop here: do not
run any other `mcp-server` command or substitute another MCP implementation.

## Supported preflight

Continue only after launcher discovery succeeds.

1. Inspect `xcrun mcp-server --help` and confirm that the selected Xcode
   supports every command or flag required by the chosen branch.
2. Run `xcrun mcp-server status --format json` when supported, otherwise
   plain `status`. Record permissions, process state, agent and folder grants,
   and open workspaces. A running server does not establish that the requested
   client configuration or project access is ready; continue those checks.
3. Classify the environment as `attended-local`, `unattended-host`, or
   `isolated-ci`. Default to `attended-local`; never infer `isolated-ci`.
4. Read [launch workflows](references/launch-workflows.md), then use only the
   selected branch. Obtain explicit approval immediately before administrator
   enablement, persistent agent or folder approval, or unsafe global
   authorization unless that exact action is already authorized in this session.
   Never use unsafe global authorization outside an explicitly
   identified disposable, isolated CI machine.

## MCP configuration

Prefer project scope so the repository declares its Xcode tooling. Configuration
scope does not restrict Xcode's permissions; verify the intended agent and folder
grants separately. Inspect existing entries and preserve unrelated servers.

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

## Verification and recovery

- Treat the final status readback as launch evidence; an accepted command is
  not proof that the server is running.
- If connection or workspace opening fails, inspect current status and use `xcrun mcp-server show-logs`
  when the selected Xcode supports it. Do not retry enablement or persistent
  approval speculatively.
- Do not stop or disable a successfully launched server unless the user asks.
- For requested access revocation, prefer `sudo xcrun mcp-server deny <id>`
  for the exact observed grant. `clear-permissions` removes all grants;
  `reset-all` also kills the service and resets onboarding. Neither is routine
  connection repair. Use public status output rather than editing Xcode's
  internal permission files. Confirm destructive permission changes are in scope.
- Report the selected Xcode version and developer directory, environment,
  permission state, server state, agent authorization, exact commands run, and
  canonical `launch_outcome`. Distinguish configuration, tool discovery,
  project access, and verification with the UI closed; report untested parts.
