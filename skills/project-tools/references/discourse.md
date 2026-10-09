# Project-local Discourse MCP

Configure the official `@discourse/mcp` server only on an explicit user request
for Discourse MCP setup and only for specific, verified sites. A bare invocation,
environment detection, or finding forum links in project documentation does not
authorize this setup. It runs locally over stdio and connects to a Discourse
site's API. This workflow always writes repository configuration.

## Select and verify sites

Require one or more forum URLs from the request or sites already explicitly
selected in the conversation. Resolve an explicitly named forum through the
table below when unambiguous; the table itself never selects sites for the user.
If no sites are specified, ask which forums to
configure before writing entries. Every entry MUST use exactly one
`--site <forum-base-url>`; it fixes the site at startup and hides runtime site
switching.

### Known community destinations

Active official Discourse forums verified on 2026-10-09. Recheck the selected
site's API before writing configuration.

| Ecosystem | Destination / official evidence | Suggested entry |
| --- | --- | --- |
| Swift | [Swift Forums](https://forums.swift.org) — designated the official discussion channel by [Swift.org](https://www.swift.org/community/). | `discourse-swift` |
| LiveKit | [LiveKit Community](https://community.livekit.io) — linked as LiveKit's managed technical forum in its [community documentation](https://docs.livekit.io/intro/community/). | `discourse-livekit` |

Use the actual Discourse base URL, including a deployment subpath if needed,
not a topic URL or an invented `/mcp` endpoint on the forum. Before creating or
changing a site entry, verify the base URL's `about.json` response and confirm
it identifies the intended Discourse instance. Preserve deployment subpaths.
An HTTP success or a reachable login page alone is not sufficient verification.
Use already-authorized access if needed; if verification fails or requires new
authentication, report the reason and leave that site's entry unchanged.
Continue with other requested sites that pass verification.

Create one entry per distinct verified site in each requested client's config.
Normalize equivalent URLs and inspect existing entries by their effective site,
not just their names, so repeated setup reuses the existing entry. Keep distinct
subpath installations distinct; resolve redirects and unexpected destinations
before treating them as the same forum. Use descriptive lower-kebab-case names
such as `discourse-swift`; disambiguate name collisions without overwriting
another site's entry. Do not configure a generic connection without `--site`,
pass several `--site` flags in one entry, or add unrequested forums. An existing
generic entry is not automatically authorization to replace or remove it.

## Configure the requested clients

Check Node.js/npm and `npx`; the current package requires Node.js 24 or newer.
Missing host tools are prerequisites, not installations to perform here.
Inspect existing entries and merge only the selected server without replacing
unrelated configuration. Resolve paths inside the repository.

| Client | Repository file |
| --- | --- |
| Codex | `.codex/config.toml` |
| Cursor | `.cursor/mcp.json` |
| Pi | `.pi/mcp.json` |
| Claude Code | `.mcp.json` |

For Codex, the Swift forum example is:

```toml
[mcp_servers.discourse-swift]
command = "npx"
args = ["-y", "@discourse/mcp@latest", "--site", "https://forums.swift.org"]
```

For Cursor, Pi, or Claude Code, merge the equivalent entry into that client's
file, keeping each file independent:

```json
{
  "mcpServers": {
    "discourse-swift": {
      "command": "npx",
      "args": ["-y", "@discourse/mcp@latest", "--site", "https://forums.swift.org"]
    }
  }
}
```

Substitute the verified entry name and site, repeating the entry for each
distinct requested forum. Preserve an established package
version pin unless an update is requested. Do not use global registration
commands, or infer that a skill-directory symlink also shares MCP configuration.
Existing client/project trust remains a prerequisite; do not grant it here.
For Pi, require native MCP support rather than installing an extension.

## Access and authentication

Public content can be read without authentication when the forum permits it.
The server disables writes by default; ordinary setup keeps that default.
Private content requires access granted by that particular forum. Write tools
require explicit `--allow_writes` opt-in and matching site credentials; enabling
them requires a request for write-capable configuration, not merely MCP setup.
Configuration does not authorize posting, editing, or other forum mutations.

For requested authenticated setup, reuse an existing protected profile through
`--profile /absolute/path/to/profile.json`. The package supports site-specific
admin or user API keys in `auth_pairs`; a profile may contain several sites.
Never embed credentials in committed client config or command arguments.
Check whether the profile enables writes before attaching it to a read-only
setup. Missing credentials or authorization are prerequisites to report; do not
generate keys, start a login, or change forum permissions as incidental setup.

## Verify

Parse the changed JSON/TOML and inspect the scoped diff. Report the repository
paths, each verified site and matching entry, and any skipped sites or
authentication prerequisites. Check that every configured entry has exactly
one `--site` and that equivalent sites have not been duplicated.
If live verification is requested, inspect that client's selected server and
perform a read-only site check when permitted. Verify the returned site identity,
not just the registration's display name. Distinguish written configuration
from a connected server; reload/restart requirements do not justify host repair
or connecting every unrelated MCP server. Do not publish a forum message as a test.

## Sources

- [Official Discourse MCP server and configuration](https://github.com/discourse/discourse-mcp#configuration)
- [Swift Forums](https://forums.swift.org/)
- [LiveKit Community](https://community.livekit.io/)
