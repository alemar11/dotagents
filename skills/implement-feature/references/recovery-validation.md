# Recovery And Start Over

Use this reference after compaction, an active claim, a missing worker, an
unknown operation, or state/runtime trouble.

## Reconstruct Current Truth

1. Run `scripts/run-state --json doctor`.
2. When the database is initialized and supported, resolve known source or
   repository ownership with `claim find`, read the complete run projection
   with `run show`, and page `operation list` from sequence zero until
   `has_more=false`; use `operation show` for exact result history.
3. When `doctor=uninitialized`, skip state reads and reconstruct identity only
   from App project, task, Goal, source, Git, and provider evidence.
4. Call `list_projects`, then read or wait on every stored or externally
   discovered thread ID. Verify
   title, project, managed checkout, Git top-level, branch, and current head.
5. Read the root Goal and require its exact objective and supported state.
6. Re-read accepted source fingerprints and current Git/provider artifacts.

The stored manifest is the canonical assignment packet. App, Git, and provider
readback is authoritative current truth. Never infer a live task or Goal from a
title, an old message, or state alone.

## Resume

Resume the original thread when its identity and checkout remain provable.
Reconcile `unknown` operations through owner/provider readback and finish the
same key; never launch a replacement operation. `run show` exposes planned
assignments and live-slot count so root can continue deterministic refill.

A disappeared or replaced worker after implementation authority is
`needs-owner`. Preserve its managed checkout and Git work. Do not release its
claims, create a second task, or silently reconstruct implementation elsewhere.

## Start Over

This version has no migration, compatibility, takeover, or `retired` lifecycle.
Use start over for preimplementation state only:

- retired cache layouts and other versioned database filenames are ignored;
- `doctor=uninitialized` starts a new schema-1 database only after App project,
  task, Goal, source, Git, and provider reads prove no matching worker can still
  mutate;
- an active schema-1 run with no authorized task may end its exact created tasks,
  record each `task abort`, and call
  `run finish --outcome preimplementation-aborted` before a fresh run;
- an incompatible database at the current schema-1 path is never read or
  rewritten. Preserve it and require owner direction before moving it aside;
  after the same no-live-work proof, start with a clean schema-1 path.

The fresh run uses new run, task, and operation identities, revalidates current
source and projects, and imports nothing. It may adopt the same still-active
root Goal when that objective remains exact.

Once any task received `implementation_authority=granted`, an old/missing state
error is not a start-over excuse. Recover from the original App task and Git
work or stop for the owner. If the exact schema-1 database is missing, the CLI
cannot adopt that existing task: preserve the checkout and report
`needs-owner` unless the exact database can be restored.

## Preimplementation Abort

End and read back each created baseline-only task as `completed` or `archived`,
then call `task abort` with that exact thread and observation ref. Reconcile all
pending/unknown operations. Planned assignments require no fake task. Only then
may `run finish --outcome preimplementation-aborted` release claims.

Do not complete the root Goal for an aborted attempt. A fresh run may continue
the same objective.
