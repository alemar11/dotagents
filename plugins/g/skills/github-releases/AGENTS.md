# GitHub Releases Maintenance

This bundled skill owns release, tag, note, asset, and package lifecycle
workflow. Runtime rules remain in `SKILL.md`, `references/workflows.md`, and
`references/package-checks.md`.

## Maintenance boundaries

- Keep release operations provider-primitive and use the shared G
  transport; do not move release policy or repository-specific versioning into
  the plugin helper.
- Preserve the inspect-versus-write boundary for tags, releases, assets, and
  package publication. Registry availability checks remain read-only.
- Validate changes with package-check fixtures and the shared CLI tests and
  shipped-artifact smoke checks. Any plugin runtime change also follows the
  plugin manifest/version rule.
