# Implement Feature Maintenance

`skills/implement-feature/` owns the Codex App orchestration entrypoint for
GitHub Feature Specs. Its runtime contract is intentionally split between
`SKILL.md` and the directly routed references; do not move that contract into
this maintenance pointer.

## Owned runtime surfaces

- `scripts/run-state` is the sole stateful helper. Its CLI version, runtime
  contract, protocol versions, artifact fingerprinting, and database schema are
  separate authorities; the executable and `references/run-state.md` must stay
  aligned.
- `scripts/verify-ready` is a separate read-only terminal verifier and must not
  write run state.
- `tests/test_run_state_github.py` and `tests/test_verify_ready.py` are the
  focused executable regression surfaces. The remaining `references/` files own
  startup, worker, recovery, scope-repair, and closeout details.

## Maintenance rules

- Preserve the one-runtime, no-migration hard cut for the run-state database;
  do not add aliases, compatibility importers, alternate state files, or a
  second orchestrator.
- Keep the Codex-dependent boundary explicit and retain portable fallbacks only
  where the runtime contract already defines them. Do not reintroduce local
  tracker or merge delivery paths.
- Any helper or protocol change requires the focused suites plus the shipped
  command's help/version/doctor or read-only verification checks before it is
  treated as valid.
