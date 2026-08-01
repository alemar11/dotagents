# Maintainer Package

This project-local skill is the maintenance control plane for this repository's
existing skills and plugins. Keep user-facing invocation and runtime contracts
in `SKILL.md` and the routed references; this file records only repository
ownership and maintenance boundaries.

## Ownership

- `SKILL.md` owns request routing and the manual-only boundary.
- `references/` owns maintenance playbooks, validation lanes, metadata checks,
  lifecycle rules, and refresh runbooks.
- `scripts/` contains maintenance-only refresh and inspection helpers. They are
  not reusable runtime artifacts and must not be added to the install lists.

## Maintenance rules

- Use `skill-audit` read-only when a health, prompt-quality, overlap, or usage
  claim needs portfolio or session evidence; apply approved fixes only in the
  owning package.
- Keep metadata-only work on the metadata playbook and preserve the canonical
  `SKILL.md` frontmatter as the source of truth.
- Route substantial new-skill or public package reshapes through the creator
  skill before returning here for repository integration and validation.
- Select validation from `references/validation-matrix.md`; do not treat a
  diagnostic portfolio signal as a failed package by itself.
