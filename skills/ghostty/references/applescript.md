# Ghostty AppleScript operations

Ghostty on macOS exposes a native AppleScript dictionary for windows, tabs,
terminals, and split panes. Confirm the installed Ghostty version supports
AppleScript, then inspect the dictionary when syntax is uncertain.

## Inspect

Use the application hierarchy `application -> windows -> tabs -> terminals`.
Useful properties include window and tab identifiers, names, indexes,
selection, focused terminal, terminal name, and working directory. Start with
the front window or an explicitly identified window; do not assume window
ordering is stable.

## Create a layout

Build a reusable surface configuration with the requested working directory,
command, initial input, environment, or font size. Create a window or tab,
then split a known terminal in a requested direction (`right`, `left`, `down`,
or `up`). Keep every returned object in memory so later splits target the
intended terminal rather than whichever surface is focused.

The core operations are: create a window, create a tab in a window, split a
terminal, focus a terminal, select a tab, set a tab or surface title, and send
input or a key. Use input only for commands the caller requested; send an
explicit Enter when the command needs to run.

## Verification and recovery

Re-query Ghostty after creation. Verify the expected hierarchy and properties,
and report partial completion when a window, tab, split, title, or command
cannot be observed. Reconcile ambiguous effects before retrying so a lost
response does not create duplicate tabs or panes. Keep cleanup bounded and
never close an ambiguous target.

Ghostty's AppleScript automation is protected by macOS Automation permission.
If permission is denied or unavailable, report that fact and use a documented
keybinding or configuration path only when it can establish the requested
result.
