# Maintainer Package

`.agents/skills/maintainer/` is the repository's maintenance control plane for
existing skills and plugins. User-facing invocation and runtime contracts stay
in `SKILL.md` and routed references; this file governs package maintenance.

## Owned surfaces

- `SKILL.md` owns request routing and the manual-only boundary.
- `references/` owns maintenance playbooks, validation matrices, metadata
  checks, lifecycle rules, and refresh runbooks.
- `scripts/` contains maintenance-only inspection and refresh helpers. They are
  not reusable runtime artifacts and must not be added to install lists.

## Maintenance contract

- Use `skill-audit` read-only when health, prompt-quality, overlap, or usage
  claims require portfolio or session evidence; apply approved fixes only in
  the owning package.
- Keep metadata-only changes on the metadata playbook and preserve
  `SKILL.md` frontmatter as the source of truth.
- Route substantial new-skill or public package reshapes through the creator
  skill before repository integration.
- Keep runtime skills independent from this package. Only repository-level
  guidance may route explicit maintenance work here.
- Keep instruction-density reviews proposal-first and wait for approval before
  compaction refactors.

## Validation

- Select validation from `references/validation-matrix.md`.
- Plugin and CLI maintenance must verify shipped artifacts and installed/cache
  state where applicable; composed workflows require focused contract tests and
  bounded scenario proof when risk justifies it.
- A portfolio diagnostic is evidence for investigation, not by itself a
  package failure or deletion authorization.
