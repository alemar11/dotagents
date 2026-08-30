# TanStack Hotkeys

Use this reference when a task involves `@tanstack/hotkeys`, a framework
adapter such as `@tanstack/react-hotkeys`, keyboard shortcuts, scoped hotkeys,
multi-key sequences, shortcut recording, held-key state, platform-aware
display, or Hotkeys devtools.

TanStack Hotkeys is currently alpha and its API may change. Inspect the
installed adapter and core versions, then verify exact APIs against the
matching official docs before implementation.

## Ownership Boundaries

- Hotkeys owns shortcut parsing, platform normalization, registration,
  conflict detection, target scoping, sequences, recording, and key state.
- The application owns command authorization, durable shortcut preferences,
  command execution, discoverability, and product-specific conflict policy.
- Use the framework adapter for application UI. Install the core package
  directly only for framework-free usage; adapters re-export the core surface.

## Workflow

1. Inventory the command and its scope.
   Decide whether the shortcut is global, focused-container, modal, or
   route-specific, and identify browser or operating-system conflicts.
2. Use portable shortcut notation.
   Prefer `Mod` for Command on macOS and Control on Windows or Linux when the
   product intends the same semantic shortcut across platforms.
3. Register through the installed adapter.
   Keep handlers stable, use explicit targets and enabled state, and choose a
   sequence API only when a single chord cannot express the interaction.
4. Preserve user input and accessibility.
   Verify behavior in text fields, editable content, dialogs, and assistive
   technology; expose commands through visible UI in addition to shortcuts.
5. Test conflicts and cleanup.
   Cover repeated keys, focus changes, route or component unmount, disabled
   state, user-customized bindings, and platform-specific display.

## Default Rules

- Treat shortcut strings as interaction contracts, not arbitrary event checks.
- Keep privileged or destructive actions behind the same confirmation and
  authorization path used by visible controls.
- Store user-configured bindings in application state; use recording only as
  the input mechanism.
- Format shortcuts for the active platform instead of hard-coding glyphs.
- Add devtools only when their debugging value justifies the extra package.

## Avoid

- Global listeners that bypass Hotkeys scoping and cleanup.
- Capturing browser, operating-system, or assistive-technology shortcuts
  without a deliberate product decision.
- Making a keyboard-only command undiscoverable from the visible interface.
- Assuming alpha APIs or package names are stable across versions.

## Verification

Use current TanStack Hotkeys overview, installation, framework quick-start,
scoping, sequence, recording, formatting, and devtools docs. Verify pointer,
keyboard, focus, editable-field, and cross-platform behavior in the target UI.
