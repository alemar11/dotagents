---
name: ghostty
description: "Use when explicitly asked to inspect or arrange Ghostty windows, tabs, split panes, terminal commands, titles, configuration, or keybindings."
---

# Ghostty

Control Ghostty as a terminal workspace on macOS and explain or update its
configuration and keybindings when requested. Prefer Ghostty's native
AppleScript interface for live layout work; use configuration and keybindings
for durable behavior. On systems without the macOS scripting interface, use
the available Ghostty keybindings or report the limitation rather than
pretending to have inspected the live layout.

Read [AppleScript operations](references/applescript.md) before inspecting or
changing live windows, tabs, or splits. Read [configuration and keybindings](references/configuration.md)
when the request concerns `config`, shortcuts, or persistent defaults.

## Layout workflow

For a requested layout, first inspect the current Ghostty windows, tabs, and
terminals when the runtime supports it. Treat the current layout as user-owned:
preserve unrelated windows and tabs, and identify an existing target by stable
properties such as window, tab, title, or working directory before acting.

Translate the request into a small declarative plan: windows, tab titles,
split directions, working directories, commands, and the final focused
terminal. Create only missing surfaces, keep a map of returned window/tab/
terminal objects, and use that map for subsequent splits and commands. Do not
rebuild an existing layout merely to make it look canonical.

After creation or modification, inspect the resulting hierarchy and verify the
expected counts, titles, working directories, commands, and focus. Report any
surface that could not be verified. Never close or replace existing surfaces
unless the user explicitly requests cleanup and the exact targets are clear.

Sending a command to a terminal is an external effect. Do it only when the
request includes that command, and preserve quoting and newlines exactly. Ask
before destructive commands, closing surfaces, or broad layout replacement.
