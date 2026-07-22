---
name: implement-feature
description: Implement dependency-ready durable Feature Specs in visible ChatGPT desktop app tasks and deliver reviewed, merge-ready pull requests. Use only when explicitly invoked.
---

# Implement Feature

## Fixed Contract

Use this skill only after explicit `$implement-feature` invocation in the
ChatGPT desktop app. Consume complete execution-ready Feature Specs and their
issues unchanged. Never plan, repair planning artifacts, implement in root,
create raw worktrees, merge, enqueue, deploy, release, or perform post-merge
closure.

The root coordinates; each visible App worker executes one Feature Spec end to
end in its App-managed worktree. A worker that remains within the durable
contract and continues producing coherent progress and evidence must not be
micromanaged. Root owns scheduling, one lifecycle Goal, canonical Feature Spec
claims, typed App-operation reconciliation, coarse status, and read-only final
verification. The worker owns issue order, design, implementation and rewrites,
repairs, tests, validation, publication, reviews and fixes, tracker proof, and
its final PR-ready evidence.

Ask exactly once at startup for `visible_app_task_permission` as defined in
`references/options.md`. That grant covers the selected workers, App-managed
worktrees, normal command approvals, validation, publication, review fixes,
tracker updates, and recovery. Never ask another authority, recovery,
validation, blocker, or continuation question during the run.

## Controller Flow

1. Load `references/spec-backed-delivery.md` and
   `references/root-bootstrap.md`. Validate current durable sources,
   dependencies, repository identities, allowed paths, acceptance, validation,
   and delivery type before state.
2. Start `scripts/run-state`. It uses one per-user schema-1 SQLite DB at
   `~/.cache/dotagents/skills/implement-feature/run-state.sqlite3`. SQLite
   transactions and the fixed busy timeout are the only writer lock.
3. Atomically claim each free `(repository_identity, source_spec_ref)` pair.
   Different Specs and head branches may run under different roots in the same
   repository. Keep a conflicting assignment in its bounded Spec wait without
   blocking claims already acquired by sibling assignments.
4. When at least one assignment owns its claim, create and read back the one
   root Goal. Schedule up to three path-disjoint Feature Specs; serialize
   overlap and dependency order inside this root. Never create a worker for an
   assignment whose Spec or head branch claim is waiting.
5. For each worker, follow `references/app-orchestration.md` and send the full
   assignment once. A succeeded bootstrap receipt/readback starts its complete
   implementation authority; there is no baseline-only phase or later GO.
6. Let the worker follow `references/worker.md` and
   `references/tracker-proof.md` autonomously. Monitor coarse progress through
   authoritative App reads and reconcile ambiguous App effects under the same
   operation key.
7. Apply `references/gates.md`. Root rereads authoritative tracker, App, Git,
   PR, CI, and review evidence without editing or judging criteria. Complete
   each assignment claim when its root-verified evidence becomes PR-ready, then
   complete the Goal and run only when the whole requested run is PR-ready.

If a worker observes compatible operational change, it adopts it and continues.
If a stable durable field changes, it records `assignment block` and stops
declaratively without asking. That post-bootstrap assignment retains only its
own Feature Spec claim; independent assignments continue.

## Reference Routing

- Always load `references/options.md`, `references/spec-backed-delivery.md`,
  `references/root-bootstrap.md`, and `references/app-orchestration.md` before
  startup mutation.
- Workers load `references/worker.md` and `references/tracker-proof.md`.
- Load `references/recovery-validation.md` for claim waits, compaction,
  ambiguous App effects, or blocked workers.
- Load `references/gates.md` for final verification and closeout.
- Load `references/run-state.md` for exact CLI shapes, errors, maintenance, or
  state recovery.
