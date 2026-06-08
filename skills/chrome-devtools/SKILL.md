---
name: chrome-devtools
description: Debug and automate live Chrome pages with Chrome DevTools MCP, the Homebrew `chrome-devtools` CLI, and the bundled CLI session runner. Use for browser debugging, browser automation, DevTools MCP/CLI setup, page inspection, screenshots, network and console inspection, Lighthouse and performance traces, accessibility checks, LCP/Core Web Vitals work, browser memory debugging, or troubleshooting Chrome DevTools MCP startup and connection failures.
---

# Chrome DevTools

## Goal

Use Chrome DevTools for agents to inspect, debug, test, and automate live browser
pages. Prefer the fastest available runtime surface:

- Direct Chrome DevTools MCP tools when they are already available in the current
  agent session.
- Homebrew `chrome-devtools` for shell-oriented one-off commands.
- This skill's `scripts/chrome-devtools-session` runner when JSON step files,
  interactive batches, guarded current-Chrome attach, or explicit daemon cleanup
  are useful.

## Runtime surfaces

The Homebrew package installs two commands:

- `chrome-devtools-mcp`: the MCP server binary.
- `chrome-devtools`: the CLI that starts and reuses a background server.

The bundled skill runner is the stable embedded artifact:

- From this skill root: `./scripts/chrome-devtools-session`.
- From another repo: `<chrome-devtools-skill-root>/scripts/chrome-devtools-session`.
- Version check: `<chrome-devtools-skill-root>/scripts/chrome-devtools-session --version`.

The runner resolves `chrome-devtools` and `chrome-devtools-mcp` from `PATH`
first, then Homebrew discovery from the paired binary, `HOMEBREW_PREFIX`, and
`brew --prefix`. Normal unauthenticated flows delegate browser actions to the
Homebrew CLI. `--current-chrome` intentionally uses the MCP stdio server with
`--autoConnect` so Chrome can request access to the already-running browser
window on the current OS. Use `--start-arg ...` only for CLI daemon startup and
`--mcp-arg ...` only for the current-Chrome MCP path.

## Installation

If either `chrome-devtools-mcp` or `chrome-devtools` is missing, read
`references/installation.md` and install with Homebrew first:

```sh
brew install chrome-devtools-mcp
chrome-devtools-mcp --version
chrome-devtools --version
```

Use Homebrew paths in Codex MCP configuration when the user wants a persistent
MCP server entry. Use `npx` only as an upstream fallback, not as this skill's
default local setup.

## Safety

Prefer isolated browser sessions for generic browsing, screenshots, local app
testing, and public-page debugging.

Use `--current-chrome` or MCP `--autoConnect` only when the user needs an
already-authenticated Chrome session. In that mode, the agent can read and act
through the user's active browser state. Do not navigate account tabs casually.
When using the runner, `--current-chrome --url` must include one explicit target:
`--new-page`, `--page-id`, or `--use-selected-page`.

## Existing Chrome windows

When the user asks for the current Chrome window already open on this OS, an
existing authenticated tab, or says not to use an isolated browser, start with
the existing-window path:

```sh
<chrome-devtools-skill-root>/scripts/chrome-devtools-session --current-chrome --interactive
```

In interactive mode, send JSON steps such as `{"tool":"list_pages"}` and then
`{"tool":"select_page","arguments":{"pageId":3,"bringToFront":true}}`, replacing
`3` with the page ID for the requested title or URL. Match the requested title
or URL before inspecting or interacting with it. If the session lists only
`about:blank`, or if the target tab is missing or ambiguous, do not continue in
the wrong browser. Ask the user to identify or expose the correct tab/profile,
and use `references/troubleshooting.md#auto-connect-failures` to repair the
attach path.

## Core workflow

For direct MCP tools or the Homebrew CLI:

1. Open or select a page: `new_page`, `navigate_page`, `list_pages`,
   `select_page`.
2. Wait for the expected state with `wait_for` when available, or verify with a
   snapshot/evaluation.
3. Inspect with `take_snapshot` for automation and element `uid`s.
4. Use `click`, `fill`, `press_key`, `evaluate_script`, network, console,
   Lighthouse, or performance tools as the task requires.
5. Save large outputs with file path parameters instead of streaming huge
   screenshots, snapshots, traces, or heap files into context.

For the bundled runner:

```sh
<chrome-devtools-skill-root>/scripts/chrome-devtools-session --list-tools
<chrome-devtools-skill-root>/scripts/chrome-devtools-session --url https://example.com --eval "document.title"
<chrome-devtools-skill-root>/scripts/chrome-devtools-session --steps steps.json
<chrome-devtools-skill-root>/scripts/chrome-devtools-session --current-chrome --interactive
```

Interactive mode accepts one JSON step, a JSON step array, `@steps.json`, or
`exit` per line. In normal mode each step maps to a `chrome-devtools` CLI
command; in `--current-chrome` mode each step maps to an MCP tool. Prefer
`@steps.json` for long batches so the terminal does not depend on a huge single
input line.

Session cleanup:

```sh
<chrome-devtools-skill-root>/scripts/chrome-devtools-session --list-running-sessions
<chrome-devtools-skill-root>/scripts/chrome-devtools-session --close-session <PID>
<chrome-devtools-skill-root>/scripts/chrome-devtools-session --close-all-sessions
```

## Reference routing

- `references/installation.md`: Homebrew install, verification, Codex MCP
  config, `--autoConnect`, and `--browser-url`.
- `references/cli-workflows.md`: command examples for navigation, input,
  emulation, network, console, screenshots, performance, and extensions.
- `references/troubleshooting.md`: startup failures, missing tools, slim mode,
  sandboxing, auto-connect failures, logs, and cleanup.
- `references/a11y-performance-memory.md`: accessibility, Lighthouse, LCP/Core
  Web Vitals, performance traces, and heap snapshot workflows.
