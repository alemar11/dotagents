# GitHub Review Threads Maintenance

This bundled skill owns review-thread inspection, selected-fix disposition,
reply, and resolution workflow. Keep runtime behavior in `SKILL.md` and
`references/workflows.md`.

## Owned surfaces

- `references/script-summary.md` mirrors the typed review commands and JSON
  envelopes exposed by the shared `scripts/g` artifact. Update it with
  any shared review command or schema change; do not make it a second source of
  executable behavior.
- `references/states.md` owns feedback, review, reconciliation, and resolution
  state meanings; schema mirrors must route to it instead of redefining them.
- Shared provider journaling, reservation, recovery, and terminal-evidence
  logic belongs to `projects/g/` and its project-scoped maintenance
  guide.

## Maintenance rules

- Preserve exact-head, exact-target, one-use reservation, read-back, and
  no-blind-retry invariants. Never replace typed thread identity with a locally
  assembled GraphQL id or a top-level PR comment.
- Validate review contract changes with the shared G tests and shipped
  artifact smoke checks; use read-only provider evidence for remote behavior.
