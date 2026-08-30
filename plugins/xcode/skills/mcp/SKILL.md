---
name: mcp
description: Launch and diagnose Apple's native headless Xcode MCP server on attended Macs, unattended hosts, or explicitly isolated CI machines.
---

# Xcode MCP

## Goal

Safely prepare, start, and verify the headless MCP server shipped with Xcode.
This skill operates Apple's `xcrun mcp-server`; it does not install or
substitute XcodeBuildMCP, configure an MCP client, or perform general Apple
platform development work.

## State model

Before interpreting status or choosing a launch branch, read
[references/states.md](references/states.md). Keep the selected Xcode, external
permission state, server process state, agent authorization, and launch outcome
distinct.

When setup provenance or command safety is disputed, read
[references/sources.md](references/sources.md). It records Apple's primary
documentation and the complete X follow-up that corrected the initial unsafe
recommendation. The selected Xcode's live help remains execution authority.

## Preflight

1. Confirm the host is macOS and resolve the active Xcode with
   `xcodebuild -version` and `xcode-select -p`.
2. Check that the selected Xcode provides the launcher with
   `xcrun --find mcp-server`. If it does not, report the exact selected Xcode
   and stop. Do not silently substitute another MCP implementation.
3. Inspect `xcrun mcp-server --help` and confirm that the selected Xcode
   supports every command or flag required by the chosen branch. Treat the
   command blocks below as the expected contract, not as a substitute for the
   selected installation's live help.
4. When the user identifies a different installed Xcode, scope `DEVELOPER_DIR`
   to every command. Pass the same value explicitly inside elevated commands;
   do not assume `sudo` preserves it. Do not change the global `xcode-select`
   value unless the user explicitly requests that separate system mutation.
5. Run `xcrun mcp-server status` before changing anything. If the server is
   already running, return `already-running` after reporting the observed
   state.
6. Classify the requested environment as `attended-local`, `unattended-host`,
   or `isolated-ci`. Default to `attended-local` when the user has not requested
   unattended operation. Never infer `isolated-ci`.

## Attended local Mac

If permission is already enabled and the server is stopped, run:

```sh
xcrun mcp-server start
xcrun mcp-server status
```

If permission is disabled, explain that enablement is persistent and requires
administrator privileges. Obtain explicit approval before running:

```sh
sudo xcrun mcp-server enable
xcrun mcp-server start
xcrun mcp-server status
```

On the first agent connection, keep the authorization choice with the user.
For repeated desktop use, recommend persistent approval only for the verified
signed agent; for one-off work, recommend temporary approval. Never add the
unsafe global flag to this branch.

## Unattended host

An unattended host is not automatically isolated. Use normal enablement,
start the server, initiate the intended agent connection, and inspect status
for pending requests:

```sh
sudo xcrun mcp-server enable
xcrun mcp-server start
xcrun mcp-server status
```

Persistent agent or folder approval is a separate mutation. Require the exact
verified request identity or project root and explicit approval before using:

```sh
sudo xcrun mcp-server approve <request-id> --always
sudo xcrun mcp-server allow-folder <project-root> --always
```

Read status again and verify that the intended agent and folder—not a broader
identity or path—received access. Do not use the unsafe global flag merely
because no person is present at the console.

## Isolated CI

Use this branch only when the user explicitly identifies a disposable,
isolated CI environment and explicitly authorizes global agent access. Then
run:

```sh
sudo xcrun mcp-server enable --unsafe-always-allow-all-agents
xcrun mcp-server start
xcrun mcp-server status
```

If isolation or authorization is uncertain, stop before enablement and return
`approval-required`. Report that unsafe permission persists outside the server
process until it is revoked or headless mode is disabled; do not imply that
stopping the process revokes it.

## Verification and recovery

- Treat the final status readback as launch evidence; an accepted command is
  not proof that the server is running.
- If start fails, inspect current status and use `xcrun mcp-server show-logs`
  when the selected Xcode supports it. Do not retry enablement or persistent
  approval speculatively.
- Do not stop or disable a successfully launched server unless the user asks.
- Report the selected Xcode version and developer directory, environment,
  permission state, server state, agent authorization, exact commands run, and
  canonical `launch_outcome`.
