# Plan Feature Maintenance

`skills/plan-feature/` is the single public planning surface for converging one
complete Feature Spec bundle and its implementation issue graph. Runtime
planning behavior stays in `SKILL.md` and the phase-owned references.

## Ownership map

- `references/spec-phase.md`, `issue-phase.md`, and `vertical-slices.md` own
  phase behavior; their templates own the rendered artifact shapes.
- `references/options.md` owns the run-scoped option contract. Do not add a
  second provider, delivery, or repository-topology registry here.
- GitHub issue transport is delegated to `$gitstack:github-issues`; Project
  Memory and the clarification skills remain composing dependencies, not
  duplicated planning implementations.
- `tests/` protects graph compression, scope repair, and validator behavior.

## Maintenance rules

- Preserve the convergent Feature Spec vocabulary, repository identity
  propagation, linked multi-repository feature identity, and complete-bundle
  terminal boundary. Do not restore retired names or standalone Spec-only
  success paths.
- This package has no shipped runtime CLI. Validate documentation and reference
  links statically, then run the focused test suite when graph or validator
  behavior changes.
