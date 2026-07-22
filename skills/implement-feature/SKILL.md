---
name: implement-feature
description: Implement dependency-ready durable Feature Specs in visible ChatGPT desktop app tasks and deliver reviewed GitHub PRs or named local branches. Use only when explicitly invoked.
---

# Implement Feature

## Fixed Contract

Use this skill only after explicit `$implement-feature` invocation in the
ChatGPT desktop app in Codex mode. Consume complete execution-ready Feature Specs and their
issues unchanged. Never plan, repair planning artifacts, implement in root,
create raw worktrees, merge, enqueue, deploy, release, or perform post-merge
closure.

The root coordinates; each visible Codex worker task executes one Feature Spec
end to end in the ChatGPT-created worktree assigned to that task. A worker that remains within the durable
contract and continues producing coherent progress and evidence must not be
micromanaged. Root owns scheduling, one lifecycle Goal, canonical Feature Spec
claims, safely recorded task and Goal changes, coarse status, and read-only final
verification. The worker owns issue order, design, implementation and rewrites,
repairs, tests, validation, publication, reviews and fixes, tracker proof, and
its final delivery-ready evidence.

Ask exactly once at startup for `visible_app_task_permission` as defined in
`references/options.md`. That grant covers the selected workers, ChatGPT-created
worktrees, normal command approvals, validation, publication, review fixes,
tracker updates, and recovery. Never ask another authority, recovery,
validation, blocker, or continuation question during the run.

## Controller Flow

1. Load `references/feature-spec-contract.md` and
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
5. For each worker, follow `references/chatgpt-task-orchestration.md` and send the full
   assignment once. A verified bootstrap delivery starts its complete
   implementation authority; there is no baseline-only phase or later GO.
6. Let the worker follow `references/worker-execution.md` and
   `references/tracker-checklists.md` autonomously. Monitor coarse progress by
   reading the visible tasks. After an interruption, check whether each recorded
   task or Goal change already happened before deciding whether it is safe to
   repeat.
7. Apply `references/final-verification.md`. Root rereads authoritative tracker,
   ChatGPT task, Git, delivery-specific provider, CI, and review evidence without editing or
   judging criteria. Complete each assignment claim when its root-verified
   evidence reaches `pr-ready` or `local-branch-ready`, then complete the Goal
   and run only when the whole requested delivery vector is ready.

If a worker observes compatible operational change, it adopts it and continues.
If a stable durable field changes, it records `assignment block` and stops
declaratively without asking. That post-bootstrap assignment retains only its
own Feature Spec claim; independent assignments continue.

## Reference Routing

- Always load `references/options.md`, `references/feature-spec-contract.md`,
  `references/root-bootstrap.md`, and `references/chatgpt-task-orchestration.md` before
  startup mutation.
- Workers load `references/worker-execution.md` and `references/tracker-checklists.md`.
- Load `references/claim-waits-and-recovery.md` for claim waits, compaction,
  interrupted task, Goal, title, message, or archive changes, or blocked workers.
- Load `references/final-verification.md` for final verification and closeout.
- Load `references/run-state.md` for exact CLI shapes, errors, maintenance, or
  state recovery.
