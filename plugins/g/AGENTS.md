# G Plugin Maintenance

`plugins/g/` is the repo-local source package for Git and GitHub provider
primitives plus read-only active-session monitoring. Runtime behavior belongs
in each bundled `SKILL.md` and its references; this file governs the plugin
package and its shared artifact.

## Ownership map

- `.codex-plugin/plugin.json` owns plugin identity, discovery metadata, bundled
  skill exposure, and the plugin version.
- `scripts/g` is the shipped shared artifact. Its maintenance source,
  tests, build, and version-alignment rules live in
  `projects/g/AGENTS.md`.
- `references/options.md` owns shared canonical invocation fields;
  `references/network-execution.md` owns shell network and authentication
  handling.
- `skills/audit/` owns explicit, read-only Codex App monitoring of active tasks
  that use G skills; it does not own Git/GitHub transport.
- `skills/<name>/` owns only its narrow provider-primitive contract and local
  adapters or reference summaries.

## Stacked PR upstream

The stack domain wraps the official [`github/gh-stack`](https://github.com/github/gh-stack)
GitHub CLI extension. The current compatibility reference is upstream `v0.0.9`;
this is a validation baseline, not a runtime pin. The wrapper currently installs
the latest upstream version because its explicit installation path uses
`gh extension install github/gh-stack` without `--pin`.

When the upstream extension changes, revalidate the typed command surface,
non-interactive behavior, JSON output, extension status/version detection, and
the stacked-PR lifecycle workflows before treating the new version as
compatible. The wrapper must fail closed when the extension is missing,
unversioned, or belongs to another repository.

## Maintenance contract

- Keep the manifest, `projects/g/pyproject.toml`, package version,
  rebuilt artifact, and installed/cache verification surfaces aligned after a
  shared runtime change.
- Keep Git/GitHub bundled skills provider-primitive and workflow-agnostic.
  `skills/audit/` is the explicit read-only App-monitoring exception and must
  not add Git/GitHub transport. Caller-owned planning, orchestration, project
  context, queue state, issue-body, and label policy must remain in composing
  skills.
- Do not add a second Git/GitHub transport or move publication policy into the
  shared helper. Preserve explicit authority for every GitHub mutation.
- Treat plugin caches as verification surfaces, never editable sources.

## Validation

- Use the project-scoped guide for tests and artifact rebuilds; do not execute
  maintenance source as the normal runtime.
- For bundled-skill changes, validate the narrow workflow contract and use
  shared artifact checks when the provider transport is affected.
