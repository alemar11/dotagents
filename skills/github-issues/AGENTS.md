# GitHub Issues Maintenance

This skill owns issue lifecycle, metadata classification, and read-only taxonomy
proposals. Keep exact operation mechanics in `references/lifecycle.md` and
`references/workflows.md`, classification in
`references/metadata-classification.md`, and result registries in
`references/states.md`. Invocation fields live in `SKILL.md`.

Use `<skill-root>/scripts/attachment-upload` for binary uploads; do not create a
second issue transport. Preserve classification's additive metadata scope and
taxonomy's no-write boundary.

## Executable maintenance

- `scripts/attachment-upload` is the shipped runnable artifact. Flags are
  accepted directly (`--repo`, `--file`, ...); there is no `upload` subcommand.
- `scripts/attachment_lib/` holds the implementation and local helpers.
- Naming: `attachment_lib` uses underscores as the Python import-syntax
  compatibility exception; the public skill (`github-issues`) and command
  (`attachment-upload`) stay lower-kebab.
- Validate with `python3 -m unittest discover -s skills/github-issues/tests -v`
  and `scripts/attachment-upload --help|--version|--json doctor`.
