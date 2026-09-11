# GitHub Review Threads Maintenance

This skill owns provider review-thread inspection, request, wait, reply, and
resolution. Keep runtime behavior in `SKILL.md` and `references/workflows.md`.
Callers own implementing code fixes and acceptance.

## Owned surfaces

- `references/script-summary.md` mirrors the typed review commands and JSON
  envelopes exposed by `scripts/reviews`. Update it with any command or schema
  change; do not make it a second source of executable behavior.
- `references/states.md` owns feedback, review, reconciliation, and resolution
  state meanings; schema mirrors must route to it instead of redefining them.

## Maintenance rules

- Preserve exact-head, exact-target, one-use reservation, read-back, and
  no-blind-retry invariants. Never replace typed thread identity with a locally
  assembled GraphQL id or a top-level PR comment.

## Executable maintenance

- `scripts/reviews` is the shipped runnable artifact (existing review verbs plus
  `snapshot`).
- `scripts/reviews_lib/` holds the implementation. Provider-protocol modules are
  synced copies of `projects/github-tools/src/github_provider_protocol/`.
- Naming: `reviews_lib` uses underscores as the Python import-syntax
  compatibility exception; the public skill (`github-review-threads`) and
  command (`reviews`) stay lower-kebab.
- Durable reservation markers and operation journals remain at the historical
  v1 roots `~/.cache/dotagents/plugins/g/review-mutations` and
  `~/.cache/dotagents/plugins/g/review-operations`. These are one-use state and
  journals, not rebuildable cache. Do not move, delete, or auto-migrate records;
  relocating roots without migration risks replay of consumed reservations.
  Keep existing `g-*` schema and transport owner IDs (`owner: "g"`).
- Validate with
  `python3 -m unittest discover -s skills/github-review-threads/tests -v` and
  `scripts/reviews --help|--version|--json doctor`.
