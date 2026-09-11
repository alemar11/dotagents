# GitHub Stacked PR Maintenance

This skill owns stack-level routing and operational guidance for the wrapper
around `github/gh-stack`. Keep single-PR publication policy in Yeet and the
typed command contract with `scripts/stack`.

## Ownership boundaries

- Keep stack lifecycle procedures in `SKILL.md` and `references/workflows.md`.
- `references/states.md` owns `ensure` extension-status meanings
  (`ready`, `missing`, `gh-missing`, `conflict`, `unverified`).
- Do not reimplement extension behavior in the skill or route ordinary single-
  PR publication through `stack submit`.
- Preserve explicit authorization for installation, push, submit, sync, rebase,
  merge, and remote unstack.
- Treat the official extension and `scripts/stack` as verification surfaces; do
  not edit installed skill caches as source.

## Validation

- Validate frontmatter and metadata with the skill creator validator.
- Scan routing and command examples for stale `submit` ownership or direct
  `gh stack` invocation outside `scripts/stack`.
- Run `git diff --check` for document-only changes.

## Executable maintenance

- `scripts/stack` is the shipped runnable artifact (`ensure`, upstream verbs,
  `raw`, `doctor`).
- `scripts/stack_lib/` holds the implementation and local helpers (not the
  shared provider protocol).
- Naming: `stack_lib` uses underscores as the Python import-syntax
  compatibility exception; the public skill (`github-stacked-pr`) and command
  (`stack`) stay lower-kebab.
- Validate with `python3 -m unittest discover -s skills/github-stacked-pr/tests -v`
  and `scripts/stack --help|--version|--json doctor` plus `--json ensure`.
