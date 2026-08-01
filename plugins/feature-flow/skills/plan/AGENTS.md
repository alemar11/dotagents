# Plan Maintenance

`plugins/feature-flow/skills/plan/` is the single public planning surface for converging a
complete Feature Spec bundle and its implementation issue graph. Runtime
planning behavior stays in `SKILL.md` and phase-owned references.

## Ownership map

- `references/options.md` owns the run-scoped option contract.
- `references/publication.md` owns GitHub publication, stable refs, and
  recoverable publication transactions.
- `references/spec-phase.md`, `issue-phase.md`, and `vertical-slices.md` own
  phase behavior and their templates own rendered artifact shapes.
- GitHub issue transport is delegated to `$gitstack:github-issues`. Project
  Context owns durable context routing and closeout, while Plan owns the
  focused repository research, issue hardening, and artifact merge required
  before an issue is agent-ready.
- `tests/` protects graph compression, scope repair, and validator behavior.

## Maintenance contract

- Preserve the convergent terminal boundary: a successful run has a complete
  implementation-eligible Feature Spec bundle and a nonempty hardened issue
  graph. Do not restore a standalone Spec-only success path.
- Keep the hard-cut Feature Spec vocabulary, canonical `run_mode`, exact
  repository identity propagation, linked multi-repository `feature_id`, and
  lower-kebab feature slugs. Do not add read aliases for retired fields,
  values, paths, or authority names.
- Keep GitHub Issues and pull-request delivery fixed. Do not add provider,
  delivery, repository-topology, or completion-method options to this skill.
- Treat publication facts as transient workflow data owned by the publication
  reference, not as durable Project Context or repository configuration.
- Keep generated issue dependency and relationship data canonical; preserve
  retained issue identities and stop on stale, conflicting, duplicate, or
  extra durable artifacts rather than repairing them heuristically.
- Accepted durable decisions are carried as optional `knowledge_delta` phase
  data. Planning must not write it into a Feature Spec, ordinary issue, or
  domain memory; only the repository-owned final `Domain Knowledge Closeout`
  issue may persist its exact shard for Implement to reconcile through
  `$project-context` after integrated behavior is proven.
- Keep issue hardening as an internal Plan phase. Research only the relevant
  codebase files, contracts, documentation, and tests; preserve caller-owned
  scope and dependencies; and persist only the final stable issue body.

## Validation

- This package has no shipped runtime CLI. Validate reference links, canonical
  vocabulary, and generated-shape invariants statically, then run the focused
  test suite when graph or validator behavior changes.
- Publication changes require proposal/recovery fixture checks; never validate
  by performing a remote mutation without explicit authority.
