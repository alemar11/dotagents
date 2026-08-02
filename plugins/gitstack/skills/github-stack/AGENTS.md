# GitHub Stack Maintenance

This bundled skill owns stack-level routing and operational guidance for the
GitStack wrapper around `github/gh-stack`. Keep single-PR publication policy in
`../send/` and the typed command contract in `../../references/stack-cli.md`.

## Ownership boundaries

- Keep stack lifecycle procedures in `SKILL.md` and `references/workflows.md`.
- Do not reimplement extension behavior in the skill or route ordinary single-
  PR publication through `stack submit`.
- Preserve explicit authorization for installation, push, submit, sync, rebase,
  merge, and remote unstack.
- Treat the official extension and the shipped GitStack artifact as verification
  surfaces; do not edit plugin caches.

## Validation

- Validate frontmatter and metadata with the skill creator validator.
- Scan routing and command examples for stale `submit` ownership or direct
  `gh stack` invocation.
- Run `git diff --check`; no CLI rebuild is required when only skill documents
  and routing metadata change.
