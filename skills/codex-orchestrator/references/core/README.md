# Shared Orchestration Core

This directory is the cross-adapter entrypoint. `options.md` owns shared
non-merge authority values. `merge-authorization.md` owns the separately loaded
post-conclusion merge contract. The following neutral contracts remain one
directory above and are linked from both public skills:

- `ledger.md` and `ledger-template.md`;
- `spec-backed-delivery.md` for the execution-ready bundle and
  `stacked-feature-specs.md` for explicit stack edges;
- `gates.md` and `codex-review-closeout.md`;
- `runtime-efficiency.md`.

The CLI skill must not load the App `SKILL.md`, `worker.md`,
`multi-repo-workspace.md`, or App `options.md`. The App skill loads shared core
plus those App adapter files.

Both adapters execute the sibling `../../scripts/orchestrator-claim` artifact
for atomic active-root ownership. That shared runtime primitive does not invoke
either public orchestrator entrypoint.
