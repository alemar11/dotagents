# GitStack Plugin Maintenance

`plugins/gitstack/` is the repo-local source package for Git and GitHub
provider primitives. Runtime behavior belongs in each bundled `SKILL.md` and
its references; this file governs the plugin package and its shared artifact.

## Ownership map

- `.codex-plugin/plugin.json` owns plugin identity, discovery metadata, bundled
  skill exposure, and the plugin version.
- `scripts/gitstack` is the shipped shared artifact. Its maintenance source,
  tests, build, and version-alignment rules live in
  `projects/gitstack/AGENTS.md`.
- `references/options.md` owns shared canonical invocation fields;
  `references/network-execution.md` owns shell network and authentication
  handling.
- `skills/<name>/` owns only its narrow provider-primitive contract and local
  adapters or reference summaries.

## Maintenance contract

- Keep the manifest, `projects/gitstack/pyproject.toml`, package version,
  rebuilt artifact, and installed/cache verification surfaces aligned after a
  shared runtime change.
- Keep bundled skills provider-primitive and workflow-agnostic. Caller-owned
  planning, orchestration, project context, queue state, issue-body, and label
  policy must remain in composing skills.
- Do not add a second Git/GitHub transport or move publication policy into the
  shared helper. Preserve explicit authority for every GitHub mutation.
- Treat plugin caches as verification surfaces, never editable sources.

## Validation

- Use the project-scoped guide for tests and artifact rebuilds; do not execute
  maintenance source as the normal runtime.
- For bundled-skill changes, validate the narrow workflow contract and use
  shared artifact checks when the provider transport is affected.
