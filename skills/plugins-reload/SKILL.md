---
name: plugins-reload
description: Refresh this project's repo-local GitStack and Software Project plugins in the Codex cache. Use after changing either plugin or when a new Codex task must load the current plugin files.
---

# Plugins Reload

Run these commands from the repository root:

```sh
codex plugin add "gitstack@alemar11" --json
codex plugin add "software-project@alemar11" --json
```

For GitStack maintenance, prefer the repository's Bash helper. It runs the
focused tests, rebuilds the artifact, removes the old installation, and then
executes the GitStack `codex plugin add` command:

```sh
plugins/gitstack/projects/gitstack/scripts/reinstall-local
```

Keep the plugin manifest version updated when plugin source changes. Never edit
copies under `~/.codex/plugins/cache/`; the repository plugin directories are
the source of truth. Open a fresh task after reinstallation so updated bundled
skills are discovered.
