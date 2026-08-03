---
name: implement
description: "Discover or explicitly implement durable GitHub Feature Specs in the ChatGPT App through visible Codex tasks, validation, review, and PR-ready delivery. Use only for explicit discovery, start, or resume requests; do not use it to plan features or merge pull requests."
---

# Implement Feature Spec

## Normal Execution Path

For an explicit execution request, the invoking parent session first creates or
resumes one visible Implement root/controller task. The parent session does not
execute the controller flow itself. After the root is structurally verified,
the root presents and follows this six-stage path:

1. Select complete GitHub Feature Specs and their implementation issues.
2. Preflight the sources, repositories, saved Git projects, dependencies, and
   worker profiles; resolve the one startup authorization interaction.
3. Prepare the run and claim each available Spec/head-branch pair.
4. Create one visible managed-worktree worker per claimed Spec and deliver its
   assignment.
5. Let each worker implement, test, update the tracker, review, and publish its
   GitHub PR autonomously.
6. Verify current-head evidence and finish at `pr-ready-for-merge`; never merge.

The parent session remains open while the root is runnable. It relays only
coarse root milestones, blockers, and the root's final Markdown report. The
root's final report is authoritative; the parent must not synthesize a second
implementation result.

Keep `run-state` commands, protocol versions, operation IDs, replay generations,
and observation files internal unless an exception requires explaining them.
The detailed contracts remain in the directly routed references below.

## Exception Routing

- Discovery requests stop after GitHub-only Spec listing.
- A claim conflict uses the bounded wait path in
  `references/claim-waits-and-recovery.md`.
- An interrupted or ambiguous App action is reconciled before any replay through
  `references/codex-task-orchestration.md`.
- Durable-contract drift blocks the assignment; it does not trigger planning or
  an ad hoc repair.
- An out-of-envelope path uses the one bounded branch in
  `references/scope-repair-orchestration.md`.
- Final evidence mismatch returns evidence only to the worker, which owns repair.

For the out-of-envelope path branch, the worker stops before using the missing
path and reports the repository-relative path plus the evidence that it is
needed. Root then spawns one separate visible SE Feature task, when the
startup permission allows it, to update the GitHub Feature Spec's
`allowed_paths`. That planner task only changes the durable planning contract;
it never implements code, edits the worker, or replaces the worker task. After
the published contract is read back, root recomputes overlap and sends the
next contract generation to the same worker. A denied or unavailable planner
leaves the original assignment blocked; a second path miss requires a new
planning run.

## Runtime Dependency

Both discovery and execution use `$g:github-issues` for authoritative GitHub
reads. Before the first G handoff, load
[codex-dependency-preflight.md](../../references/codex-dependency-preflight.md).
If it blocks, stop before the GitHub query, ready gate, run-state mutation,
claim, task, or worktree creation that depends on G. Discovery-only remains
read-only, but it does not bypass this dependency gate.

## Request Routing

After explicit invocation, classify the request before loading startup
references:

- Use `discovery-only` when the user asks only whether Feature Specs exist,
  which Specs are available, or what could be implemented. Phrases such as
  "do we have any Spec?", "list available Specs", and "what can we implement?"
  remain discovery even when they contain the word "implement".
- Enter the execution flow only when the user explicitly directs the skill to
  start, implement, or resume one or more Feature Specs. That explicit
  `$se:implement` execution request authorizes creating the disclosed
  visible root and worker tasks plus the workers' ChatGPT-created worktrees.
  Do not ask for an additional root- or worker-task creation confirmation.

For `discovery-only`:

1. Load and pass the SE-to-G runtime dependency preflight, then query GitHub
   Issues for authoritative Feature Specs. Do not load or validate execution
   contracts, issue graphs, repository-to-project mappings, branches, worker
   profiles, runtime capabilities, run state, or startup authorization beyond
   that required G availability check.
2. Return the candidate Feature Spec references, links when available, and
   brief tracker summaries. Include child issue references only when the
   tracker exposes them without execution preflight.
3. State that this was discovery only: the G availability preflight was
   evaluated, but execution eligibility and the execution startup preflight
   were not.
4. Stop. Do not invoke `scripts/run-state`, create or modify run state, acquire
   claims, ask for startup authorization, create tasks or worktrees, or mutate
   repositories or trackers.

## Fixed Contract

Use this skill only after explicit `$se:implement` invocation in the
ChatGPT App in Codex mode. For execution, consume complete execution-ready
Feature Specs and their issues unchanged. The parent session only bootstraps
and monitors the root; the root is a control plane and never implements
repository code; workers own implementation. Never create raw worktrees,
merge, enqueue, deploy, release, or perform post-merge closure.

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

`../../references/ready-gate.md` owns the execution-readiness boundary. Before
any startup authorization, run-state preparation, claim, worker, or worktree
mutation, the root must read the complete implementation issue graph and
verify the exact `ready-for-agent` label on every final implementation issue.
The parent Feature Spec is not a substitute for its child issue labels. A
missing label blocks that Spec before state and is routed back to Feature;
Implement never adds or repairs the label.

The root/controller coordinates; each visible Codex worker task executes one Feature Spec
end to end in the ChatGPT-created worktree assigned to that task. A worker that remains within the durable
contract and continues producing coherent progress and evidence must not be
micromanaged. Root owns scheduling, canonical Feature Spec claims, safely
recorded task changes, coarse run status, and read-only final
verification. The worker owns issue order, design, implementation and rewrites,
repairs, tests, validation, publication, review-candidate preparation, finding
acceptance and fixes, tracker proof, and its final delivery-ready evidence. The
worker always runs the native `codex review` command in its managed checkout,
passing its fixed model and resolved thinking value through the CLI's global
model and `model_reasoning_effort` overrides; root never runs review and only
verifies the worker's reported review evidence.

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
`visible_app_task_permission=granted` for the disclosed root and workers unless
the user explicitly denies task creation. The startup interaction separately
resolves missing-project creation and `scope_repair_task_permission`. The task
grant covers the root controller, selected workers, ChatGPT-created worktrees,
normal command approvals, validation, publication, review fixes, tracker
updates, and recovery.
Never ask another authority, recovery, validation, blocker, or continuation
question during the run.

## Parent-session bootstrap

This protocol runs only for an explicit `start`, `implement`, or `resume`
request. A `discovery-only` request remains GitHub-only and creates no root.

The session where `$se:implement` is invoked is the `parent session`. It is a
relay and monitor, not the Implement controller:

1. Build a complete handoff before creating a root. Include the request mode,
   objective, selected or requested Feature Specs, repository context, current
   state, accepted constraints, expected terminal report, validation
   expectations, unresolved risks, and the rule that the root must not invoke
   `$se:implement` or create another root. Include the parent task ID and host
   when the App exposes them, the exact project ID, and
   `environment.type=local`.
2. Resolve the current session's exact saved local project through
   `list_projects`, matching the current path and host. A missing, projectless,
   cross-host, or ambiguous match stops before root creation; do not substitute
   a new project or a worktree. The root and parent share this control-plane
   project, while implementation workers still use their independently
   verified repository-specific projects.
3. Before task mutation, inspect the live declarations for `create_thread`,
   `set_thread_title`, task readback/listing, and bounded task waits. Create
   exactly one root task for a new run with:

   ```text
   environment: { type: local }
   model: gpt-5.6-sol
   thinking: medium
   title: the canonical Implement Feature root title when known
   prompt: the complete handoff plus the root protocol
   ```

   When the final assignment count is not yet authoritative, use the stable
   provisional title `🤖 Implement Feature`; the root owns the existing single
   count-based `set-root-title` fallback after `run start`. Creation-time title
   support is always independently read back and is never identity evidence.
4. After creation, independently verify the real `threadId`, exact project,
   local environment, task state, and requested `gpt-5.6-sol` /
   `thinking: medium` settings when telemetry is exposed. A title warning is
   non-blocking; structural or settings drift stops before workers. A returned
   `clientThreadId`, timeout, or uncertain response is pending setup: reconcile
   the existing App task before any retry and never create a duplicate.
5. For a `resume` request, resolve the unfinished run's recorded
   `root_task_id`, read it back, and send the continuation only to that exact
   root. Never create a replacement root while the run is unfinished. If the
   root identity cannot be reconciled, stop and report the recovery blocker.
6. Keep the parent turn open and monitor the root with bounded waits, using
   direct root milestones when available and the root's final response as the
   authoritative report. Relay only preflight/run/worker/blocker milestones
   and the final Markdown report; do not relay routine worker collaboration or
   execute repository, Git, GitHub, or run-state work in the parent.
7. The parent never archives the root. A root that completes, blocks, or
   becomes recoverable remains the visible controller task for its run.

The parent-task identity and relay context are transient handoff data; the
existing run-state continues to persist only the real root task as
`root_task_id`. This keeps the first bootstrap change compatible with the
current run manifest and SQLite protocol.

## Controller Flow

This flow runs in the newly created or explicitly resumed root task, never in
the parent session. The root first verifies the handoff, its own task identity,
the local control-plane project, and the explicit `gpt-5.6-sol` /
`thinking: medium` profile, then follows the existing controller flow.

This flow applies only after the user explicitly directs execution of one or
more Feature Specs. A discovery-only request never enters this flow.

1. Load `../../references/workflow-contract.md`,
   `../../references/ready-gate.md`, `references/feature-spec-contract.md`,
   and `references/root-bootstrap.md`. Validate current durable sources,
   dependencies, repository identities, allowed paths, acceptance, validation,
   GitHub PR delivery, and exact repository-to-worker-project mapping before state.
   Apply the ready-for-agent gate to every final implementation issue before
   resolving worker profiles, startup authorization, run state, or claims.
   Verify that the current root task readback still matches the parent handoff
   and explicitly reports `gpt-5.6-sol` with `thinking: medium` when those
   settings are exposed; settings drift stops before workers.
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
   `manifest_feature_set`. Keep those inputs unchanged until
   `run start` revalidates them. Resolve the one startup authorization
   interaction, including the bounded planner-task permission from
   `references/scope-repair-orchestration.md`, only after this read-only
   preflight.
   Before any task mutation, inspect the live Codex App declarations for every
   operation used by this flow and verify every argument that will be passed.
   Do not infer support from a previous runtime or from prompt text. Prefer
   `title` in every `create_thread` call when the inspected declaration
   exposes that field, then independently read back the created title. If
   creation does not yield the exact requested title, use the verified
   `set_thread_title` operation at most once after a real task ID exists and
   independently read it back again. If `create_thread.title` is absent, use
   that same fallback when available. Missing or unverifiable structural
   operations or arguments stop the run as `unsupported-runtime`; missing or
   unverifiable title support produces `title-unverified` telemetry and does
   not stop workers, bootstrap, or implementation unless the user explicitly
   requires an exact title.
   Missing saved projects either follow the explicitly authorized bounded setup
   path or stop before run state, claim, task, or worktree creation.
2. Prepare shared run state through read-only `capabilities` and `doctor`, then
   `state prepare`. Keep the exact schema, runtime pin, and fail-closed behavior
   internal; `references/run-state.md` owns those details.
3. Call `run start` with the manifest plus one repeated
   `--feature-spec-set-input <absolute-file>` per linked set; standalone Specs
   pass none. The CLI revalidates every complete body and requires exact
   validator-projection equality before SQLite access. Only then atomically
   claim each free `(repository_identity, source_spec_ref)` pair.
   Different Specs and head branches may run under different roots in the same
   repository. Keep a conflicting assignment in its bounded Spec wait without
   blocking claims already acquired by peer assignments.
4. When at least one assignment owns its claim, attempt the immutable root
   title once through the recorded App title operation when that operation is
   exposed; otherwise record `root-title-unverified` in the run report. Record
   any `root-title-unverified` or `root-title-drift` warning, then schedule every
   claimed Feature Spec allowed by path and
   dependency serialization, with no numeric worker cap. Dependency-related
   peers may start before their input HEADs stabilize so they can collaborate,
   but final proof must bind the exact prerequisite revisions. Never create a
   worker for an assignment whose Spec or head branch claim is waiting.
5. For each worker, follow `references/codex-task-orchestration.md` to create the
   visible task and deliver its full assignment. Operation IDs and replay
   generations are internal coordination facts. A verified, worker-accepted
   bootstrap starts complete implementation authority; the creation prompt
   grants none.
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
claim, delegate the portable repair to a separate SE Feature task when
   authorized and supported, recompute same-root overlap, then send the
   crash-safe next contract generation.
7. Apply `references/final-verification.md`. Root rereads authoritative GitHub,
   Codex task, Git, PR, CI, and native Codex review evidence without editing or
   judging criteria. Complete each assignment claim when its root-verified
   evidence reaches `pr-ready`, then finish the run only
   when the whole requested GitHub PR vector is ready.

If a worker observes compatible operational change, it adopts it and continues.
If a stable durable field changes, it records `assignment block` and stops
declaratively without asking. That post-bootstrap assignment retains only its
own Feature Spec claim; independent assignments continue.

## Reference Routing

- Always load `../../references/workflow-contract.md`,
  `../../references/ready-gate.md`, `references/options.md`,
  `references/feature-spec-contract.md`, `references/root-bootstrap.md`,
  `references/task-model-policy.md`, and
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
