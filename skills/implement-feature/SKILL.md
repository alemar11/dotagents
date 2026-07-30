---
name: implement-feature
description: Discover or implement durable Feature Specs in the ChatGPT App, using collaborating visible Codex tasks for execution and delivering reviewed GitHub PRs or named local branches. Use only when explicitly invoked.
---

# Implement Feature Spec

## Request Routing

After explicit invocation, classify the request before loading startup
references:

- Use `discovery-only` when the user asks only whether Feature Specs exist,
  which Specs are available, or what could be implemented. Phrases such as
  "do we have any Spec?", "list available Specs", and "what can we implement?"
  remain discovery even when they contain the word "implement".
- Enter the execution flow only when the user explicitly directs the skill to
  start, implement, or resume one or more Feature Specs. That explicit
  `$implement-feature` execution request authorizes creating the disclosed
  visible worker tasks and their ChatGPT-created worktrees. Do not ask for an
  additional worker-task creation confirmation.

For `discovery-only`:

1. Resolve only the configured tracker backend needed to locate authoritative
   Feature Specs, then query that tracker. Do not load or validate execution
   contracts, issue graphs, repository-to-project mappings, branches, worker
   profiles, runtime capabilities, run state, or startup authorization.
2. Return the candidate Feature Spec references, links when available, and
   brief tracker summaries. Include child issue references only when the
   tracker exposes them without execution preflight.
3. State that this was discovery only and that execution eligibility and
   startup preflight were not evaluated.
4. Stop. Do not invoke `scripts/run-state`, create or modify run state, acquire
   claims, ask for startup authorization, create tasks or worktrees, or mutate
   repositories or trackers.

## Fixed Contract

Use this skill only after explicit `$implement-feature` invocation in the
ChatGPT App in Codex mode. For execution, consume complete execution-ready
Feature Specs and their issues unchanged. Never plan or implement in root,
create raw worktrees, merge, enqueue, deploy,
release, or perform post-merge closure.

`references/feature-spec-contract.md` owns the stable-source mutation table.
The root and workers may read stable fields, detect drift, and block. They may
resume the existing assignment only after an externally authored correction is
independently read back and restores the exact stable contract already accepted
by that run. The sole mutation exception is a separately owned monotonic
`allowed_paths` expansion executed through
`references/scope-repair-orchestration.md`. Any other changed stable contract
requires a new run and claim after the
existing owner is reconciled; root and workers must never create the change,
even when a user directly requests it inside the active run.

The root coordinates; each visible Codex worker task executes one Feature Spec
end to end in the ChatGPT-created worktree assigned to that task. A worker that remains within the durable
contract and continues producing coherent progress and evidence must not be
micromanaged. Root owns scheduling, canonical Feature Spec claims, safely
recorded task changes, coarse run status, and read-only final
verification. The worker owns issue order, design, implementation and rewrites,
repairs, tests, validation, publication, review-candidate preparation, finding
acceptance and fixes, tracker proof, and its final delivery-ready evidence. The
bootstrap's `review_owner=worker|root` owns AutoReview execution only; a
root-owned review never grants root implementation or repair authority.

The controller task may be bound to a local Codex multi-folder project. Codex
uses that project's primary folder for new-task working directory, default Git
operations, worktree and review actions, and automatic `AGENTS.md`, skills, and
`config.toml` discovery; secondary folders remain attached as file context. Those
defaults grant the root no implementation authority. When the controller
project is multi-folder, treat every attached folder as read-only coordination
context and never use that controller project as a worker target.

Current Codex task readback may omit `projectId` for a compatibility workspace
even though its `cwd` is the exact reported path of one saved local Git project.
In that case, resolve a controller-only project identity only through the
bounded exact-path fallback in `references/root-bootstrap.md`. The current
`list_projects` surface reports one project path but not the complete folder set,
so the fallback does not prove or require that the saved project is
single-folder. It may therefore identify either a one-folder project or a
multi-folder project's primary path, both of which are valid controller
contexts. It never makes that project eligible as a worker target or replaces
the independent worker-project preflight.

When the controller project is multi-folder, every worker still runs in the
separate saved Git project associated with its assigned repository. That worker
project's reported primary folder must be the exact repository root and its
independently resolved Git common directory must match the assignment's
canonical repository identity. A repository's presence as a primary or
secondary folder in the controller project does not satisfy this worker-project
requirement or create another repository identity, claim, or execution target.

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
visible Codex tasks, trackers, and repositories, and never create a
replacement controller while that run is unfinished. Do not add a heartbeat,
worker-to-root wake, persisted objective, or second lifecycle state. The root
title is UI evidence only and never durable state.

A recoverable pre-bootstrap worker or ChatGPT App failure must not
silently duplicate the attempted effect or release its claim. Reconcile the
recorded ChatGPT App operation before any continuation. Replay only
when that exact operation reports `replay_authorized=true`, always with the
same logical `operation_id` and a newly incremented `launch_count`; never begin
a replacement operation. Bootstrap replay preserves its derived `bootstrap_id`
and is deduplicated by the worker. A protected non-bootstrap operation may
replay only after authoritative failed readback proves the prior launch had no
effect. Controller follow-up messages are not replayable.

Resolve the startup authorization interaction defined in
`references/options.md` only after the worker-project preflight. When a required
repository has no separate saved Git project whose reported primary folder is
the exact repository root, that same interaction either authorizes creation of
only the listed projects plus the disclosed worker run, or stops before state.
The explicit execution request resolves
`visible_app_task_permission=granted` unless the user explicitly denies worker
creation. The startup interaction separately resolves missing-project creation
and, when at least one selected assignment is GitHub-backed,
`scope_repair_task_permission`. The worker grant
covers the selected workers, ChatGPT-created worktrees, normal command
approvals, validation, publication, review fixes, tracker updates, and recovery.
Never ask another authority, recovery, validation, blocker, or continuation
question during the run.

## Controller Flow

This flow applies only after the user explicitly directs execution of one or
more Feature Specs. A discovery-only request never enters this flow.

1. Load `references/feature-spec-contract.md` and
   `references/root-bootstrap.md`. Validate current durable sources,
   dependencies, repository identities, allowed paths, acceptance, validation,
   delivery type, and exact repository-to-worker-project mapping before state.
   Resolve each worker's fixed model and adaptive thinking level through
   `references/task-model-policy.md`, verify destination-host support, and
   disclose every resolved profile before startup authorization.
   Resolve the current controller task's direct local saved Codex-project
   binding or its bounded exact-path compatibility identity as controller
   identity only; a later UI-primary change does not alter it. The resolved
   project may be multi-folder, need not be affected, and grants no
   implementation authority. Require every affected repository to map
   independently to its own exact repo-specific saved Git project. For each
   multi-repository set, run read-only
   `scripts/run-state --json feature-spec-set validate --input <absolute-file>`
   over ephemeral complete member-body snapshots and retain its exact
   `manifest_feature_set`, including each validated local member's decoded
   `repository_relative_spec_path`. Keep those inputs unchanged until
   `run start` revalidates them. Resolve the one startup authorization
   interaction, including the bounded planner-task permission from
   `references/scope-repair-orchestration.md`, only after this read-only
   preflight.
   Missing saved projects either follow the explicitly authorized bounded setup
   path or stop before run state, claim, task, or worktree creation.
2. Run read-only `scripts/run-state --json capabilities` and
   `scripts/run-state --json doctor`, then
   `scripts/run-state --json state prepare`. CLI `4.2.0` implements runtime
   contract `5.0.0` over the permanently unversioned per-user SQLite DB at
   `~/.cache/dotagents/skills/implement-feature/run-state.sqlite3`; database
   schema integer `4` is separate from those SemVer identities. Every run pins
   its exact runtime contract, CLI, and shipped artifact SHA-256. A database
   schema-1 state with active owners cannot prove those pins and therefore
   stops fail-closed; a drained schema-1 state is atomically dropped and
   recreated as schema 4 without carrying rows forward. Schemas 2 and 3 record exact
   owner pins: pass every distinct required executable with repeated
   `state prepare --retained-runtime` flags and keep the root open for bounded
   drain sweeps. Never start a worker or another run during a fenced cutover.
   Unknown, newer, corrupt, unversioned, or same-version-invalid state stops
   before claims. SQLite transactions and `target_schema_version` fence
   concurrent CLI work; no filesystem lock is used.
3. Call `run start` with the manifest plus one repeated
   `--feature-spec-set-input <absolute-file>` per linked set; standalone Specs
   pass none. The CLI revalidates every complete body and requires exact
   validator-projection equality before SQLite access. Only then atomically
   claim each free `(repository_identity, source_spec_ref)` pair.
   Different Specs and head branches may run under different roots in the same
   repository. Keep a conflicting assignment in its bounded Spec wait without
   blocking claims already acquired by peer assignments.
4. When at least one assignment owns its claim, set and verify the immutable
   root title once, then schedule every claimed Feature Spec allowed by path and
   dependency serialization, with no numeric worker cap. Dependency-related
   peers may start before their input HEADs stabilize so they can collaborate,
   but final proof must bind the exact prerequisite revisions. Never create a
   worker for an assignment whose Spec or head branch claim is waiting.
5. For each worker, follow `references/codex-task-orchestration.md` and send
   the full assignment under the generated `bootstrap_id`, including canonical
   `review_owner=worker|root`. Persist the initial owner atomically on
   `send-bootstrap begin --review-owner`; allow at most one worker-to-root
   reroute through the reconciled `set-review-owner` operation after the early
   AutoReview doctor path. A verified,
   worker-accepted bootstrap starts its complete implementation authority;
   duplicate delivery of that same logical bootstrap has one effect. There is
   no baseline-only phase or later GO.
6. Let the worker follow `references/worker-execution.md` and
   `references/tracker-checklists.md` autonomously. Monitor coarse progress by
   reading the visible tasks. After an interruption, check whether each recorded
   task change already happened before trusting its typed
   `replay_authorized` result. Never infer no effect from an immediate tool
   error.
   Multi-repository workers communicate directly using the exact peer task and
   checkout identities supplied by root. Each worker operates only in its own
   worktree and exposes its own component to the peer that owns combined proof,
   with exact pre/post HEAD evidence. Never create a dedicated integration
   worker or grant cross-worktree access.
   If a worker reports a required path outside the durable envelope, follow
   `references/scope-repair-orchestration.md`: retain the original worker and
   claim, delegate the portable repair to a separate Plan Feature task when
   authorized and supported, recompute same-root overlap, then send the
   crash-safe next contract generation.
7. Apply `references/final-verification.md`. Root rereads authoritative tracker,
Codex task, Git, delivery-specific provider, CI, and AutoReview-owned review evidence without editing or
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
  `references/root-bootstrap.md`, `references/task-model-policy.md`, and
  `references/codex-task-orchestration.md` before startup mutation.
- Load `references/scope-repair-orchestration.md` when startup authorization is
  resolved or a worker reports an out-of-envelope path.
- Workers load `references/worker-execution.md` and `references/tracker-checklists.md`.
- Load `references/claim-waits-and-recovery.md` for claim waits, compaction,
  interrupted root or worker tasks, title, message, or archive changes, or
  blocked workers.
- Load `references/final-verification.md` for final verification and closeout.
- Load `references/run-state.md` for exact CLI shapes, errors, maintenance, or
  state recovery.
