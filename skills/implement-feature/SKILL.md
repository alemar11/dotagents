---
name: implement-feature
description: Implement durable Feature Specs in collaborating visible ChatGPT desktop app tasks and deliver reviewed GitHub PRs or named local branches. Use only when explicitly invoked.
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
micromanaged. Root owns scheduling, canonical Feature Spec claims, safely
recorded task changes, coarse run status, and read-only final
verification. The worker owns issue order, design, implementation and rewrites,
repairs, tests, validation, publication, reviews and fixes, tracker proof, and
its final delivery-ready evidence.

A root task that owns an unfinished run remains the sole controller for that
run. During executable work, root keeps its current turn open and monitors
workers with bounded task waits until the run is delivery-ready,
preimplementation-aborted, owner-abandoned, or declaratively blocked with no
runnable work.
Never return a final response while runnable work remains.
`blocked` is terminal only for the current response: the run intentionally
remains unfinished with its claims retained, so only the same root may resume
after authoritative recovery or contract change.
An unexpected task interruption does not make the run terminal: manually
resume the exact root task and run, reconstruct current state from SQLite,
visible ChatGPT tasks, trackers, and repositories, and never create a
replacement controller while that run is unfinished. Do not add a heartbeat,
worker-to-root wake, persisted objective, or second lifecycle state. The root
title is UI evidence only and never durable state.

A recoverable pre-bootstrap worker or ChatGPT desktop app failure must not abort the assignment
or release its claim. Reconcile the failed ChatGPT desktop app operation, keep the assignment
planned, and retry from the same root with a new recorded operation.

Resolve the startup authorization interaction defined in
`references/options.md` only after the saved-project preflight. When a required
repository is not a saved Git project, that same interaction either authorizes
creation of only the listed projects plus the disclosed worker run, or stops
before state. Otherwise it resolves only `visible_app_task_permission`. The
worker grant covers the selected workers, ChatGPT-created worktrees, normal
command approvals, validation, publication, review fixes, tracker updates, and
recovery. Never ask another authority, recovery, validation, blocker, or
continuation question during the run.

## Controller Flow

1. Load `references/feature-spec-contract.md` and
   `references/root-bootstrap.md`. Validate current durable sources,
   dependencies, repository identities, allowed paths, acceptance, validation,
   delivery type, and exact saved Git-project mapping before state. Resolve the
   one startup authorization interaction only after this read-only preflight.
   Missing saved projects either follow the explicitly authorized bounded setup
   path or stop before run state, claim, task, or worktree creation.
2. Run read-only `scripts/run-state --json doctor`, then
   `scripts/run-state --json state prepare`. It uses the permanently
   unversioned per-user SQLite DB at
   `~/.cache/dotagents/skills/implement-feature/run-state.sqlite3`, with schema
   version `1` stored only in its singleton `runtime_metadata` row. If a
   recognized older schema has active
   owners, keep the root open and repeat bounded doctor/prepare sweeps until
   they drain through the exact old runtime passed to `state prepare
   --retained-runtime`; if that executable is unavailable, stop fail-closed.
   Never start a worker or another run during that wait. Preparation then
   drops and recreates the complete schema inside one exclusive SQLite
   transaction without migrating state.
   Unknown, newer, corrupt, unversioned, or same-version-invalid state stops
   before claims. SQLite transactions and `target_schema_version` fence
   concurrent CLI work; no filesystem lock is used.
3. Atomically claim each free `(repository_identity, source_spec_ref)` pair.
   Different Specs and head branches may run under different roots in the same
   repository. Keep a conflicting assignment in its bounded Spec wait without
   blocking claims already acquired by sibling assignments.
4. When at least one assignment owns its claim, set and verify the immutable
   root title once, then schedule up to three path-disjoint Feature Specs; serialize
   overlap inside this root. Dependency-related peers may start before their
   input HEADs stabilize so they can collaborate, but final proof must bind the
   exact prerequisite revisions. Never create a worker for an
   assignment whose Spec or head branch claim is waiting.
5. For each worker, follow `references/chatgpt-task-orchestration.md` and send the full
   assignment once. A verified bootstrap delivery starts its complete
   implementation authority; there is no baseline-only phase or later GO.
6. Let the worker follow `references/worker-execution.md` and
   `references/tracker-checklists.md` autonomously. Monitor coarse progress by
   reading the visible tasks. After an interruption, check whether each recorded
   task change already happened before deciding whether it is safe to
   repeat.
   Multi-repository workers communicate directly using the exact peer task and
   checkout identities supplied by root. Each worker operates only in its own
   worktree and exposes its own component to the peer that owns combined proof,
   with exact pre/post HEAD evidence. Never create a dedicated integration
   worker or grant cross-worktree access.
7. Apply `references/final-verification.md`. Root rereads authoritative tracker,
ChatGPT task, Git, delivery-specific provider, CI, and AutoReview-owned review evidence without editing or
   judging criteria. For local-branch delivery, use `scripts/verify-ready` for
   the deterministic Git and tracker snapshot instead of composing shell
   probes. Complete each assignment claim when its root-verified
   evidence reaches `pr-ready` or `local-branch-ready`, then finish the run only
   when the whole requested delivery vector is ready.

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
  interrupted root or worker tasks, title, message, or archive changes, or
  blocked workers.
- Load `references/final-verification.md` for final verification and closeout.
- Load `references/run-state.md` for exact CLI shapes, errors, maintenance, or
  state recovery.
