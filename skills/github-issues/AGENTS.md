# GitHub Issues Maintenance

This skill owns issue lifecycle, metadata classification, and read-only taxonomy
proposals. Keep exact operation mechanics in `references/lifecycle.md` and
`references/workflows.md`, classification in
`references/metadata-classification.md`, and result registries in
`references/states.md`. Invocation fields live in `SKILL.md`.

GitHub CLI owns attachment uploads through native `--attach`; do not add an
upload helper or reproduce GitHub's HTTP transport. Preserve classification's
additive metadata scope and taxonomy's no-write boundary.

Validate attachment guidance against the installed command's help and current
GitHub documentation. Check reference paths and metadata without live uploads
unless a publication target and files are explicitly authorized.
