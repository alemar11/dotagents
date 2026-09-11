---
name: hopper
description: Configure Hopper Disassembler's HopperMCPServer for Codex or Cursor, globally or for one project, and verify that the server is available.
---

# Hopper MCP

Use this skill when the user asks to set up, repair, inspect, or use Hopper
Disassembler through its MCP server. The server is local and requires Hopper
Disassembler to be installed on macOS.

Before changing configuration, discover the installed app instead of assuming a
fixed installation directory. For example, search the standard macOS app
locations and derive the executable from the bundle:

```sh
hopper_app="$(mdfind 'kMDItemFSName == "Hopper Disassembler.app"' | head -n 1)"
if [ -z "$hopper_app" ]; then
  hopper_app="$(find /Applications "$HOME/Applications" -maxdepth 1 \
    -type d -name 'Hopper Disassembler.app' -print -quit 2>/dev/null)"
fi
if [ -z "$hopper_app" ]; then
  echo "Hopper Disassembler.app was not found" >&2
  exit 1
fi
hopper_server="$hopper_app/Contents/MacOS/HopperMCPServer"
if [ ! -x "$hopper_server" ]; then
  echo "HopperMCPServer was not found in: $hopper_app" >&2
  exit 1
fi
```

If the search returns no app, explain what is missing and stop. If multiple
copies exist, ask which one to use. Do not invent a download URL or silently
install Hopper. Preserve existing MCP entries and credentials.

## MCP configuration

Prefer project scope so the repository declares the tool it needs and teammates
can reproduce the setup. Inspect existing entries first, preserve unrelated
servers and credentials, and replace an existing entry only when the user asks.

### Project scope (recommended)

For Codex, add this block to `<project>/.codex/config.toml` and commit it when
the project should share the setup:

```toml
[mcp_servers.HopperMCPServer]
command = "<resolved HopperMCPServer path>"
```

Codex loads project configuration only for trusted projects and merges it with
the user configuration.

For Cursor, merge this entry into `<project>/.cursor/mcp.json`, replacing the
command placeholder with the resolved value of `$hopper_server`. Commit the file
when teammates should receive it:

```json
{
  "mcpServers": {
    "HopperMCPServer": {
      "command": "<resolved HopperMCPServer path>"
    }
  }
}
```

Cursor merges global and project files; a project entry with the same name takes
priority.

### Global scope (optional)

For Codex, run this from a shell:

```sh
codex mcp add HopperMCPServer -- "$hopper_server"
```

For Cursor, merge the same JSON entry into `~/.cursor/mcp.json` instead of the
project file.

### Verification

Verify Codex with `codex mcp list`, or Cursor with `agent mcp list` (or the Cursor
MCP settings screen). Start a fresh agent session after changing configuration.

## Use and verification

After setup, ask the agent to inspect an opened Hopper project or to list the
Hopper MCP tools. Confirm the server appears in the client's MCP list and that a
read-only inspection succeeds before attempting edits, patches, or exports.

For a macOS app or Mach-O sample, begin by identifying the artifact and its
security and loading metadata, then use Hopper for static disassembly and
cross-reference analysis:

```sh
file <target>
codesign -dv --verbose=4 <target>
spctl -a -vv <target>
otool -L <target>
```

Record the target path, signature or Hardened Runtime observations, loaded
libraries, and any address- or symbol-level conclusions. For `.app` bundles,
inspect the relevant executable inside the bundle rather than treating the
bundle directory as a Mach-O file.

If the target is an iOS IPA, route the work as mobile analysis: inspect
`Info.plist`, signing, Objective-C metadata, Swift symbols, and Mach-O
dependencies as appropriate, and use Hopper alongside tools such as
`class-dump`, `swift-demangle`, `dsymutil`, `otool`, or `jtool2` when available.
Device, signing, jailbreak, and runtime-instrumentation requirements are
separate from Hopper MCP setup and must be established before dynamic work.

For reverse-engineering work, establish the target and the user's authority
before opening files, attaching to a process, or changing a binary. Start with
the least-invasive Hopper operation that answers the question, record the
input path, relevant tool calls, and resulting addresses or findings, and keep
original samples immutable. Do not fetch or bootstrap an unrelated reverse-
engineering toolchain automatically; ask when a missing dependency changes the
scope. Limit dynamic analysis and network interaction to systems the user owns
or has explicitly authorized.
