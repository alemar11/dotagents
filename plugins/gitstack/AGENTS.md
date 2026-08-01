# GitStack Plugin Maintenance

`plugins/gitstack/` is the repo-local source package for Git and GitHub
workflows. Bundled skills remain provider primitives and workflow-specific
composition stays in their callers; runtime behavior belongs in each bundled
`SKILL.md` and its references.

## Ownership map

- `.codex-plugin/plugin.json` owns plugin identity, discovery metadata, bundled
  skill exposure, and the plugin version.
- `scripts/gitstack` is the plugin-shared shipped artifact. Its maintenance
  source, tests, build, rebuild, and version-alignment rules are owned by
  `projects/gitstack/AGENTS.md`.
- `references/options.md` owns the shared canonical GitStack invocation fields;
  `references/network-execution.md` owns shell network and authentication
  handling.
- `skills/<name>/` owns only the narrow workflow contract and any skill-local
  adapters or reference summaries.

## Maintenance rules

- Keep the manifest, `projects/gitstack/pyproject.toml`, package version,
  rebuilt `scripts/gitstack`, and installed/cache verification surfaces aligned
  whenever the plugin runtime changes. Follow the repository plugin version
  rule before committing any change under this directory.
- Use the project-scoped maintenance guide for tests and artifact rebuilds; do
  not execute maintenance source as the normal runtime.
- Treat plugin caches as verification surfaces, never editable sources, and
  preserve explicit authority for all GitHub mutations.
