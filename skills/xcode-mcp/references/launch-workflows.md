# Xcode MCP Launch Workflows

Use only the branch selected during preflight. Treat these commands as the
expected contract and confirm them against the selected Xcode's live help.

## Attended local Mac

When permission is enabled and the server is stopped, run:

```sh
xcrun mcp-server start
xcrun mcp-server status
```

When permission is disabled, explain that enablement is persistent and
requires administrator privileges. After explicit approval, run:

```sh
sudo xcrun mcp-server enable
xcrun mcp-server start
xcrun mcp-server status
```

Keep the first agent-authorization choice with the user. Recommend persistent
approval only for a verified signed agent used repeatedly, and temporary
approval for one-off work. Never use unsafe global authorization in this
branch.

## Unattended host

An unattended host is not automatically isolated. After explicit approval for
administrator enablement, use normal enablement, start the server, initiate the
intended connection, and inspect pending requests:

```sh
sudo xcrun mcp-server enable
xcrun mcp-server start
xcrun mcp-server status
```

Persistent agent or folder approval is a separate mutation. Require the exact
verified request identity or project root and explicit approval before running:

```sh
sudo xcrun mcp-server approve <request-id> --always
sudo xcrun mcp-server allow-folder <project-root> --always
```

Read status again and verify that access belongs to the intended agent and
folder, not a broader identity or path. Do not use unsafe global authorization
merely because nobody is at the console.

## Isolated CI

Use this branch only when the user explicitly identifies a disposable,
isolated CI environment and authorizes global agent access. After confirming
both conditions and receiving approval for administrator enablement, run:

```sh
sudo xcrun mcp-server enable --unsafe-always-allow-all-agents
xcrun mcp-server start
xcrun mcp-server status
```

If isolation or authorization is uncertain, stop before enablement and return
`approval-required`. Report that unsafe permission persists outside the server
process until revoked or headless mode is disabled; stopping the process does
not revoke it.
