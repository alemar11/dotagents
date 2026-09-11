# Xcode MCP Sources

Use these sources to verify provenance or investigate command drift. Always
confirm the selected installation's live `mcp-server` help before execution.

## Apple documentation

- [Giving external agents access to Xcode](https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode)
  documents Apple's native bridge registration. Its UI-open instructions
  describe UI-bound access; do not impose them on Xcode 27 headless mode.
- [Xcode 27 release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes)
  introduced the headless `mcp-server` preview and states that unsafe global
  agent approval is not recommended for at-desk use.

## Client configuration

- [Codex MCP configuration](https://developers.openai.com/codex/mcp)
  documents project configuration and per-server environment variables.

## Headless workflow context

- [Headless Xcode: From Prompt to Simulator with MCP](https://artemnovichkov.com/blog/headless-xcode-from-prompt-to-simulator-with-mcp)
  describes on-demand service startup, workspace-triggered approvals, and
  verification with the UI closed. Its app-building walkthrough is outside
  this setup skill's scope. Treat it as practitioner evidence and cross-check
  commands with the selected installation.

## Local command validation

Checked on 2026-09-11 against Xcode 27.0, build 27A266a:

- `mcp-server --help` exposes `open`, not `start`; `open` launches if needed.
- `status --help` supports `--format json` for process and permission readback.
- `enable --help` exposes the unsafe global-agent flag.
- `approve --help` and `allow-folder --help` support `--always` and
  `--for-24-hours`; durable agent trust requires a signed agent.
- `deny --help` identifies targeted revocation; top-level help distinguishes
  `clear-permissions`, `reset-all`, and `show-logs`.
- `mcpbridge --help` describes stdio transport and optional `MCP_XCODE_PID`
  process pinning.

These are command-contract checks, not proof of a successful client connection
or approved project access. Recheck live help on other Xcode builds.
