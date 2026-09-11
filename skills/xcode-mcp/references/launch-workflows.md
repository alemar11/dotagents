# Xcode MCP Launch Workflows

Use only the branch selected during preflight. Treat these commands as the
expected contract and confirm them against the selected Xcode's live help.

Preserve authorization already supplied for the exact operation. Administrator
execution still requires the host's available privilege mechanism.

## Connection and workspace opening

With headless permission enabled, the configured client's `xcrun mcpbridge`
connection launches the service on demand. Xcode 27 build 27A266a exposes no
`mcp-server start` command. For an existing requested workspace, preload it with:

```sh
xcrun mcp-server open "/absolute/path/to/Project.xcworkspace"
xcrun mcp-server status --format json
```

Use the actual project or workspace path, not a placeholder. Opening a workspace
can require folder approval. For an empty repository, connect the client and
verify tool discovery without inventing a project. A pending project approval
is not a failed server launch.

## Attended local Mac

When permission is enabled, connect the client or open the requested workspace
as above. An already-running service still needs client and access verification.

When permission is disabled, explain that enablement is persistent and
requires administrator privileges. After explicit approval, run:

```sh
sudo xcrun mcp-server enable
xcrun mcp-server status --format json
```

Then connect the client or open the requested workspace. Enablement alone does
not prove that the service is running or that a project is accessible.

Keep the first agent-authorization choice with the user. Recommend persistent
approval only for a verified signed agent used repeatedly, and temporary
approval for one-off work. Never use unsafe global authorization in this
branch.

## Unattended host

An unattended host is not automatically isolated. After explicit approval for
administrator enablement when disabled, use normal enablement:

```sh
sudo xcrun mcp-server enable
```

Connect the intended client or open the requested workspace, then inspect
pending requests with `xcrun mcp-server status --format json`.

Persistent agent or folder approval is a separate mutation. Require the exact
verified request identity or project root and explicit approval before running:

```sh
sudo xcrun mcp-server approve <request-id> --always
sudo xcrun mcp-server allow-folder <project-root> --always
```

Use only the relevant command for each observed request. Live help also offers
`--for-24-hours` for temporary agent or folder access; choose the authorized
duration. Durable agent approval requires a signed agent.

Read status again and verify that access belongs to the intended agent and
folder, not a broader identity or path. Do not use unsafe global authorization
merely because nobody is at the console.

## Isolated CI

Use this branch only when the user explicitly identifies a disposable,
isolated CI environment and authorizes global agent access. After confirming
both conditions and receiving approval for administrator enablement, run:

```sh
sudo xcrun mcp-server enable --unsafe-always-allow-all-agents
```

Connect the client or open the requested workspace, then read structured status.
Unsafe mode bypasses individual agent and folder grants; absent individual
grants are not proof of restricted access.

If isolation or authorization is uncertain, stop before enablement and return
`approval-required`. Report that unsafe permission persists outside the server
process until revoked or headless mode is disabled; stopping the process does
not revoke it.
