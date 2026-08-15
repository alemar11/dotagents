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
- The shared artifact's `attachment upload` command owns the plugin's single
  binary transport to GitHub's user-attachment upload host. The
  `github-issues` skill owns authorization, Markdown placement, publication,
  and readback policy around that primitive.
- `references/options.md` owns shared canonical invocation fields;
  `references/network-execution.md` owns shell network and authentication
  handling.
- `skills/audit/` owns explicit, read-only Codex App monitoring of active tasks
  that use G skills; it does not own Git/GitHub transport.
- Each skill that defines workflow or result states owns one
  `references/states.md`; procedure and schema references route to that file
  instead of defining a second semantic registry.
- `skills/github-tagger/` owns evidence-backed selection from current
  repository-owned labels and enabled native issue types, plus explicitly
  requested read-only proposals for missing labels and organization issue
  types. It delegates exact issue mutations to `skills/github-issues/` and
  never mutates taxonomy from proposal mode.
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
  skills or provider-owned metadata. GitHub Tagger may interpret the current
  provider-owned taxonomy or propose a minimal evidence-backed extension when
  explicitly requested, but proposal mode must remain read-only.
- Keep native issue dependencies in `github-issues` as exact provider-identity
  operations. One operation owns one directed blocked-issue/blocker edge,
  supports cross-repository blockers by URL, and verifies both `blockedBy` and
  reciprocal `blocking` readback. Composing planners own why the edge exists.
- Do not duplicate the attachment upload transport in a skill or add another
  Git/GitHub transport. Do not move issue or pull-request publication policy
  into the shared helper. Preserve explicit authority for every GitHub
  mutation.
- Treat plugin caches as verification surfaces, never editable sources.

## Validation

- Use the project-scoped guide for tests and artifact rebuilds; do not execute
  maintenance source as the normal runtime.
- For bundled-skill changes, validate the narrow workflow contract and use
  shared artifact checks when the provider transport is affected.
- For GitHub Tagger changes, validate the explicit mode boundary, canonical
  states, minimal-proposal rules, repository-versus-organization scope, and the
  prohibition on taxonomy writes from proposal mode.
