# Implement Feature Maintenance

`plugins/se/skills/implement/` owns the Codex App orchestration entrypoint for
GitHub Feature Specs. The invoking parent session bootstraps one visible local
root/controller; that root owns the durable run and worker orchestration.
Runtime behavior stays in `SKILL.md` and the directly routed references; this
file records maintenance contracts for the package.

## Owned surfaces

- `scripts/run-state` is the sole stateful helper. Its CLI version, runtime
  contract, named JSON protocols, artifact fingerprint, and database schema
  are separate authorities; the executable and `references/run-state.md`
  must stay aligned.
- `scripts/verify-ready` is a separate read-only terminal verifier and must
  never write run state.
- `tests/test_run_state_github.py` and `tests/test_verify_ready.py` are the
  focused executable regression surfaces. The other references own startup,
  worker, recovery, scope-repair, and closeout details.

## Maintenance contract

- Preserve the one-runtime hard cut for run state: no aliases, compatibility
  importers, alternate state files, migrations, or second orchestrator. Keep
  the database schema version independent from CLI and protocol versions.
- Preserve the Codex App-only, manual invocation boundary and the one-to-one
  local saved Git-project preflight. Do not reintroduce local tracker,
  publication, merge, or delivery paths.
- Preserve the parent-session → root/controller → worker topology: a new
  execution creates exactly one root with explicit `gpt-5.6-sol` /
  `thinking: medium`, the parent relays only coarse milestones and the final
  root report, and resume reuses the recorded root instead of creating a
  replacement. Keep parent relay context transient; `root_task_id` remains the
  durable controller identity.
- Keep GitHub Issues as the source tracker and GitHub PR as the delivery
  boundary. G owns Git/GitHub transport; this package owns orchestration
  and verification, not transport implementation.
- Enforce the plugin `ready-for-agent` gate before run-state preparation,
  claims, workers, or worktrees. Do not apply or repair the label here.
- Keep worker implementation and review evidence worker-owned, root follow-up
  evidence-only, and cross-worktree access forbidden. Do not persist raw
  Feature Spec or issue bodies in run state.
- Treat worker/task identity, exact HEAD evidence, scope revision, and
  recovery observations as typed protocol data. Reject stale generations and
  unknown fields instead of adding compatibility readers.

## Validation

- Run the focused run-state and `verify-ready` suites for helper or protocol
  changes.
- Verify each shipped command's help/version and read-only or doctor checks;
  exercise recovery or scope repair with a bounded fixture when those paths
  change.
