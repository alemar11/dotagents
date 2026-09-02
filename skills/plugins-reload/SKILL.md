---
name: plugins-reload
description: Explicitly refresh this project's repo-local SE and Xcode plugins in the Codex cache. Use only when the user invokes $plugins-reload or directly asks to reload the local plugins after source changes.
---

# Plugins Reload

## Activation and authorization

- Run only after explicit invocation or an equivalent direct reload request.
- That request authorizes replacing the installed local SE and Xcode cache
  entries from this repository's plugin sources. It does not authorize source
  edits, commits, pushes, pull requests, or publication.
- Never edit cache copies. Stop if the repository plugin source or configured
  local marketplace cannot be established.

## Workflow

Run these commands from the repository root:

```sh
codex plugin add "se@alemar11" --json
codex plugin add "xcode@alemar11" --json
```

Keep the plugin manifest version updated when plugin source changes. Never edit
copies under `~/.codex/plugins/cache/`; the repository plugin directories are
the source of truth. Open a fresh task after reinstallation so updated bundled
skills are discovered.
