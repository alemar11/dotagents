# Ghostty configuration and keybindings

Ghostty configuration uses `key = value` entries. Every configuration key can
also be supplied as a command-line option when launching Ghostty. Inspect the
installed version's defaults before changing a binding, and preserve unrelated
configuration.

## Layout actions

The relevant actions include `new_window`, `new_tab`, `new_split:right` (or
`left`, `down`, `up`), `goto_split`, `next_tab`, `previous_tab`,
`toggle_split_zoom`, `equalize_splits`, `set_tab_title`, and `close_surface`.
Use `keybind = clear` only when the user explicitly wants to replace all
defaults. Trigger sequences such as `ctrl+a>n=new_tab` are useful for a
user-chosen leader key; quote command-line bindings because `>` is shell syntax.

Prefer durable keybindings for repeated manual operations. Prefer AppleScript
for inspecting state, constructing multi-surface layouts, assigning working
directories or commands, and verifying the result. A keybinding alone is not
evidence that a requested layout was created.

On macOS, Ghostty's AppleScript support can be disabled with
`macos-applescript = false`; check this before diagnosing a scripting failure.
Use Ghostty's own action names and platform-specific defaults rather than
assuming macOS shortcuts apply on Linux.
