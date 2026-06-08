# Troubleshooting

Start with the smallest diagnostic that proves which layer is failing.

## Installation and versions

```sh
command -v chrome-devtools-mcp
command -v chrome-devtools
chrome-devtools-mcp --version
chrome-devtools --version
```

If Homebrew binaries are missing:

```sh
brew install chrome-devtools-mcp
brew info chrome-devtools-mcp
```

## Daemon startup failures

Start the CLI daemon with logging:

```sh
DEBUG=* chrome-devtools start --logFile /tmp/chrome-devtools-mcp.log --usageStatistics=false
```

If you are debugging Codex MCP configuration rather than the CLI, run the MCP
server directly:

```sh
DEBUG=* chrome-devtools-mcp --logFile /tmp/chrome-devtools-mcp.log --no-usage-statistics
```

Inspect the error text and the log file. Common causes:

- Unsupported or mismatched Node/npm environment.
- Chrome is missing, old, or cannot launch.
- A sandboxed MCP client prevents Chrome from starting.
- A stale or incompatible Chrome profile is being reused.

For sandboxed clients, start Chrome outside the client and connect with
`--browser-url=http://127.0.0.1:9222`.

## Missing tools

If only a tiny tool set is available, check these causes:

- The MCP server was started with `--slim`.
- The client is in a read-only/safe mode that hides mutating tools.
- Category tools need explicit flags, such as `--categoryExtensions=true`,
  `--experimentalMemory=true`, or `--experimentalScreencast=true`.

Use the skill runner to list the installed CLI command surface:

```sh
<chrome-devtools-skill-root>/scripts/chrome-devtools-session --list-tools
```

## Auto-connect failures

For `chrome-devtools start --autoConnect`, MCP `--autoConnect`, or runner
`--current-chrome`, verify:

1. Chrome is already running.
2. Chrome supports the auto-connect flow.
3. Remote debugging is enabled at `chrome://inspect/#remote-debugging`.
4. The browser permission prompt was accepted.
5. Another tool is not competing for the same browser/debugging connection.

The runner uses the MCP stdio path for `--current-chrome` specifically so Chrome
can surface the existing-window permission flow. If it lists only `about:blank`
instead of the user's existing tabs, stop the session and fix the attach path
before continuing.

If this still fails, use a manual debugging port:

```sh
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-devtools-profile

chrome-devtools start --browserUrl=http://127.0.0.1:9222 --usageStatistics=false
chrome-devtools-mcp --browser-url=http://127.0.0.1:9222 --no-usage-statistics
```

## Runner session cleanup

The bundled runner reports the CLI daemon status, calls `chrome-devtools stop`
for `--close-all-sessions`, and can still close matching runner/server PIDs:

```sh
<chrome-devtools-skill-root>/scripts/chrome-devtools-session --list-running-sessions
<chrome-devtools-skill-root>/scripts/chrome-devtools-session --close-session <PID>
<chrome-devtools-skill-root>/scripts/chrome-devtools-session --close-all-sessions
```

Prefer `--close-session <PID>` when account-bearing Chrome sessions may be open.
