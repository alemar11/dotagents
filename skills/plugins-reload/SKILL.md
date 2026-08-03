---
name: plugins-reload
description: Refresh this project's repo-local G, SE, and SE2 plugins in the Codex cache. Use after changing any plugin or when a new Codex task must load the current plugin files.
---

# Plugins Reload

Run these commands from the repository root:

```sh
codex plugin add "g@alemar11" --json
codex plugin add "se@alemar11" --json
codex plugin add "se2@alemar11" --json
```

For G maintenance, prefer the repository's Bash helper. It runs the
focused tests, rebuilds the artifact, removes the old installation, and then
executes the G `codex plugin add` command:

```sh
plugins/g/projects/g/scripts/reinstall-local
```

Keep the plugin manifest version updated when plugin source changes. Never edit
copies under `~/.codex/plugins/cache/`; the repository plugin directories are
the source of truth. Open a fresh task after reinstallation so updated bundled
skills are discovered.
