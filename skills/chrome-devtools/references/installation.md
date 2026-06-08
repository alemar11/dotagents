# Installation

Use Homebrew as the default local install path.

```sh
brew install chrome-devtools-mcp
chrome-devtools-mcp --version
chrome-devtools --version
```

The Homebrew formula installs both:

- `chrome-devtools-mcp`: MCP server for agent integrations.
- `chrome-devtools`: shell CLI for direct browser commands.

If the binaries are not found after installation, verify Homebrew's bin
directory is on `PATH`:

```sh
brew --prefix
ls -l "$(brew --prefix)/bin/chrome-devtools-mcp" "$(brew --prefix)/bin/chrome-devtools"
```

## Codex MCP configuration

Prefer the resolved Homebrew binary path instead of `npx` for this skill's local
setup:

```sh
command -v chrome-devtools-mcp
codex mcp add chrome-devtools -- "$(command -v chrome-devtools-mcp)" --no-usage-statistics
```

Headless isolated mode is appropriate for most local app checks:

```sh
codex mcp add chrome-devtools -- "$(command -v chrome-devtools-mcp)" --headless --isolated --no-usage-statistics
```

On macOS or Linux systems where Homebrew is supported, ask the user whether they
want to install with `brew install chrome-devtools-mcp` before suggesting any
non-Homebrew path. Treat `npx chrome-devtools-mcp@latest` as a last-resort
fallback for unsupported environments, unavailable Homebrew, or an explicit user
request for the upstream npm install path.

## Existing Chrome sessions

Use `--autoConnect` only when the user needs an already-running, authenticated
Chrome session:

1. Open Chrome.
2. Visit `chrome://inspect/#remote-debugging`.
3. Enable remote debugging.
4. Configure MCP with `--autoConnect` or run the skill runner with
   `--current-chrome`.
5. Accept Chrome's remote debugging permission prompt.

Auto-connect exposes the user's active browser state, including signed-in pages
and cookies, to the agent. Prefer a new isolated page for public browsing.

## Browser URL fallback

If `--autoConnect` fails because the client is sandboxed or cannot discover the
running browser, start Chrome manually with a debugging port and a dedicated user
data directory:

```sh
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-devtools-profile
```

Then point MCP at that browser:

```sh
chrome-devtools-mcp --browser-url=http://127.0.0.1:9222 --no-usage-statistics
```
