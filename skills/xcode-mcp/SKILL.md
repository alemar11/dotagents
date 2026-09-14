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
4. For launch or permission changes, read
   [launch workflows](references/launch-workflows.md) and use only the selected
   branch. Obtain explicit approval immediately before administrator
   enablement, persistent agent or folder approval, or unsafe global
   authorization unless that exact action is already authorized in this session.
   Never use unsafe global authorization outside an explicitly
   identified disposable, isolated CI machine.

## Client setup and connection

For requested client configuration, connection verification, or project access,
read [configuration](references/configuration.md). Status-only inspection stays
read-only and ends with the observed state. Do not launch a client, open a
workspace, or change configuration solely to answer a status question.

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
  `launch_outcome` when a launch or connection was attempted. Distinguish
  configuration, tool discovery, project access, and verification with the UI
  closed; report untested parts relevant to the request.
