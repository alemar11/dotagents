---
name: codex-orchestrator
description: Execute execution-ready Feature Specs in visible Codex App tasks through one mandatory GitHub pull-request-ready implementation flow.
---

# Codex App Orchestrator

## Purpose And Invocation

Use this Codex-dependent skill only when the owner explicitly invokes
`$codex-orchestrator` or asks to run Codex Orchestrator in the App. It is the
single App-only orchestration surface.

The root owns execution-ready intake, the active-root claim, portfolio Goal or ledger
fallback, scheduling, permission decisions, ledger state, merge decisions,
source closeout, and final status. Implementation always runs in exactly one
visible App task per implementation-eligible Feature Spec. That task owns its
Spec through the fixed terminal target
`pull-request-ready-for-merge-but-not-merged`.

## Mandatory Runtime Surface Gate

This is the first runtime step. Before the permission gate, source intake,
claims, Goals, ledger work, or any mutation, inspect the capabilities
exposed by the current runtime.

- Continue only when the current runtime exposes the visible Codex App task
  creation and App-managed worktree binding surfaces required by this skill.
- Treat an interactive Codex CLI session, generic/background subagent tools,
  filesystem access, or the skill being locally discoverable as insufficient
  evidence of the App runtime.
- If the required App surfaces are absent or cannot be verified, abort
  immediately as unsupported in the current runtime. Do not ask for visible-task
  permission, create runtime artifacts, invoke or recommend another
  orchestrator, or begin source intake.

## Mandatory Permission Gate

Run this only after the runtime surface gate passes. Before source intake,
claiming a ledger, creating a Goal, or performing any mutation, resolve
`visible_app_task_permission` from the invoking instruction.

- If the instruction explicitly grants creation of visible Codex App tasks for
  this run, persist
  `granted-by-authorized-user` and continue.
- Generic delegation, subagent, background-worker, or task-creation authority
  does not grant visible App task creation; leave permission unresolved and ask
  the one required question.
- If permission is missing or `not-requested`, ask the user once whether to
  allow creation of exactly one visible App task per implementation-eligible
  Feature Spec for this run.
- If the user grants it, continue. If the user denies it, does not answer, or
  the runtime cannot ask, abort the run without implementation or runtime
  artifacts.

For an accepted execution-ready bundle, task spawning is mandatory after the
gate. It is not a strategy knob, and the grant is run-scoped rather than durable
project configuration. The grant does not make an incomplete source executable.

## Fixed Implementation Conclusion

The only successful App implementation conclusion is
`pull-request-ready-for-merge-but-not-merged`. This is a runtime invariant, not
a user option. A draft pull request is an intermediate state. Uncommitted
changes, local commits, pushes without a pull request, and draft-only delivery
are never successful App conclusions. Merge still requires separate explicit
authority.

After registration and before dispatch, run a GitHub PR preflight for every
affected repository. Require a GitHub repository target, authenticated access,
branch publication permission, pull-request creation/update capability, and
the review/CI surfaces required by the fixed conclusion. An incompatible source
delivery target aborts during intake as `unsupported-app-delivery-target`. A
failed capability preflight aborts as `pr-preflight-failed`; never downgrade the
target or continue with a partial delivery mode.

## Non-Negotiable Invariants

- Load `references/options.md` and `references/ledger.md` during CLAIM. Resolve
  only the non-merge fields needed
  for registration using canonical snake_case fields and lower-kebab values.
  Keep `pull_request_merge_permission` and
  `pull_request_merge_confirmation` unresolved during CLAIM, registration, and
  worker execution. Do not load `references/merge-authorization.md` on
  that path.
- Use `scripts/orchestrator-claim` as the sole active-root authority. Acquire
  the canonical repository/source claim before creating the ledger projection,
  portfolio Goal, task, worktree, or any other runtime artifact. A conflicting
  claim aborts as `needs-owner`; never emulate the claim with a read-then-write
  Markdown check.
- Accept only the execution-ready Feature Spec bundle defined in
  `references/spec-backed-delivery.md`. Rough intent, a standalone Feature Spec,
  ad-hoc implementation requests, draft source refs, missing generated issues,
  and incomplete or contradictory handoffs are not executable App inputs.
- Require `visible_app_task_permission=granted-by-authorized-user` before
  any orchestration work. Missing permission follows the mandatory permission
  gate; denied permission aborts. If the visible task surface cannot represent
  the assignment after a grant, abort as blocked. Never fall back to root or
  background implementation.
- Create exactly one visible task per Feature Spec, not per issue or repository.
  The task owns implementation, integration, validation, commits, publication,
  Codex review, fixes, CI, and merge-ready preparation already authorized by
  the root.
- Require every registered App workstream to resolve
  `change_delivery_target=pull-request-ready-for-merge-but-not-merged` and
  `change_delivery_permission=granted-for-selected-target`. Reject every other
  delivery tuple before dispatch instead of asking the user to choose a target.
- Every created or resumed task establishes its assignment-scoped Goal before
  work. Record an exact objective fallback only when that task runtime exposes
  no Goal tool. Internal background subagents do not need separate Goals.
- Use only App-managed worktrees. There is no checkout strategy, caller-branch
  rotation, unmanaged-worktree permission, raw worktree fallback, or CLI
  exemption. If the App cannot supply every required managed checkout, abort
  as blocked and record the exact failure reason.
- A multi-repository Feature Spec remains one task. The App-managed workspace
  must expose an isolated checkout for every affected child repository.
- Keep at most three nonterminal Feature Spec tasks. The root derives one, two,
  or three from dependency readiness, isolation, risk, and live capacity.
  Internal subagents remain inside the parent Spec slot.
- Workers never edit the ledger, manage sibling/root tasks, change authority,
  choose branch/PR strategy, merge, release, deploy, or close the source. They
  may use bounded internal subagents within their inherited scope and authority.
- The root resolves `worker_allowed_actions` per workstream and sends only that
  exact action set to the assigned visible task.
- Treat worker status as evidence. Read the latest task state before steering,
  replacement, lifecycle changes, or closeout.
- Preserve owner changes. Read-only discovery never grants mutation authority.
- Recovery packets are derived projections. Validate current source, checkout,
  task, Goal, and option evidence before resuming mutation.

## Execution-Ready Intake

After permission is granted, load `references/spec-backed-delivery.md` and run
one read-only intake. Accept only a durable Feature Spec plus its complete
generated implementation-issue graph and Orchestrator Handoffs. Validate stable
source refs, affected repositories, workstream ids, scope, acceptance,
dependencies, validation, delivery and issue authority, review requirements,
closeout, and durable-knowledge handoff before CLAIM.

Do not invoke another skill, create, repair, regenerate, or publish planning
artifacts, infer missing implementation detail, mutate a source or tracker,
acquire a claim, or create a ledger, Goal, or task during intake. An explicit
same-repository `upstream-merge-ready-head` dependency additionally loads
`references/stacked-feature-specs.md`; no other input shape selects another
route.

If any required planning or handoff evidence is missing, contradictory, stale,
or non-durable, abort this invocation with `planning-required`. Return the
source refs and exact missing or invalid fields, state that no runtime artifact
or mutation was created, and require planning to be completed separately. Do
not continue to CLAIM. If the bundle resolves a non-App delivery target, abort
with `unsupported-app-delivery-target`. A complete bundle finalizes the affected
repository set and continues to CLAIM.

Every accepted App implementation uses a pull request ready for merge but not
merged. Merge, release, deployment, source mutation, and target-repo instruction
changes each require their exact permission.

## Controller Loop

0. **SURFACE** — verify the current runtime exposes visible Codex App task
   creation and App-managed worktree binding; otherwise abort before asking
   permission or creating artifacts.
1. **PERMISSION** — run the mandatory permission gate and abort unless task
   creation is granted for this run.
2. **INTAKE** — validate the execution-ready bundle read-only and finalize the
   complete affected-repository set; abort as `planning-required` before CLAIM
   when any required evidence is missing or invalid.
3. **CLAIM** — canonicalize the finalized repositories, load the ledger,
   and call `scripts/orchestrator-claim --json claim acquire` to acquire the
   active-root claim atomically. Qualify every repository-local source ref,
   including `#42` and repo-relative Feature Spec paths, as
   `git:<git-common-dir>::ref:<source-ref>`; the helper rejects unqualified local
   refs. Preserve URI-shaped hosted or globally durable source ids unchanged so
   they still conflict across repositories. Only after ownership is established,
   create the ledger projection, resolve remaining non-merge options, and create
   the portfolio Goal or exact fallback.
4. **REGISTER** — snapshot the finalized sources, repositories, acceptance, dependency, authority, and
   closeout evidence.
5. **PR-PREFLIGHT** — verify the fixed target, GitHub remote/access,
   publication authority, PR capability, and required review/CI surfaces for
   every affected repository; abort as `pr-preflight-failed` on any failure.
6. **DISPATCH** — load `references/worker.md`, select up to three ready Specs,
   create one managed visible task per Spec, and verify each task Goal.
7. **MONITOR** — read current task state, reconcile evidence, and send precise
   corrections when a task drifts.
8. **GATE** — require the task to execute the fixed PR delivery and gate
   sequence. The root observes; it never takes implementation or review back.
9. **RECONCILE** — rescan sources and dependencies, update the ledger and
   recovery packet, and dispatch newly ready Specs.

Every wave yields a ledger transition, proof, source update, owner decision, or
explicit no-progress record. Continue until completion or a real authority,
access, dependency, tool, gate, or safety blocker stops progress.

## Atomic Claim Helper

Normal App runtime uses the shipped `scripts/orchestrator-claim` artifact. Run
`--json doctor` without creating state, then acquire with the root id,
every canonical repository realpath, every source id, and the absolute ledger
ref. Persist its returned claim fingerprint in the
ledger projection. Use `claim heartbeat` while active and `claim release` only
after terminal evidence or an explicit durable handoff is recorded. Both
commands require the fingerprint returned by acquire so a reused root id cannot
act as the prior owner.

Takeover is never a retry alias. A terminal owner releases its own claim with
the acquire-epoch fingerprint. Use `claim takeover` only after validating stale
heartbeat evidence, resolving
`existing_orchestrator_session_takeover_policy=takeover-authorized`, and naming
the exact conflicting root ids plus evidence. Pass the canonical takeover
policy and reason plus every expected claim's current fingerprint and heartbeat.
The helper atomically verifies that the current conflicts and snapshots equal
those expected before replacing them and enforces its fixed five-minute
heartbeat threshold. There is no opaque terminal-evidence takeover path.

## Goal And Persistence

The root Goal coordinates the portfolio. Each task Goal contains the exact
Feature Spec assignment and the fixed PR-ready terminal target. A resumed task reuses a
matching active Goal; a replacement creates a new Goal. A task marks its Goal
complete only after the terminal target and gates pass.

The canonical ledger lives under
`~/.cache/dotagents/skills/codex-orchestrator/ledgers/`. All App runs use the
same active-root claim namespace so overlapping runs stop safely.

## Visible App Task

Load `references/worker.md` before creating, resuming, reading, or steering a
task. Title the task with the exact Feature Spec title and bind it to the
App-managed worktree target. Record the task id, title, managed checkout map,
Goal evidence, capability snapshot, internal subagent topology, lifecycle
state, validation, PRs, review, CI, and delivery evidence.

If a task fails or becomes stale, read it, record failure evidence, and resume
or replace it with one task for the same Spec. Never keep two active tasks for
one Spec and never transfer its implementation or review work to the root.

## Delivery And Closeout

Load `references/gates.md` before merge-ready or final status. A successful App
run requires every affected repository PR to be non-draft, current-revision
review-complete, CI-clean, free of unresolved actionable feedback, and ready to
merge. The Feature Spec task owns pre-merge PR and parent-closeout preparation;
the root owns any separately authorized merge, post-merge verification, and
final source closeout.

Use the smallest matching GitStack workflow for issues, CI, review threads,
commits, pull requests, releases, or portfolio inspection. `$autoreview`
remains a required non-trivial edit gate unless the canonical closeout contract
selects another exact owner.

Only after every affected PR reaches the fixed PR-ready conclusion, and only
when the owner separately requests merge, may the root resolve
`pull_request_merge_permission` and `pull_request_merge_confirmation`. This is
a post-conclusion root authorization step, not intake, CLAIM, registration, or
worker authority. Load `references/merge-authorization.md` only for that
step.

## Final Report

For a pre-claim abort, return the intake outcome, source refs, exact missing or
invalid evidence, and explicit proof that no claim, ledger, Goal, task, tracker
write, source mutation, or runtime artifact was created. Do not fabricate
ledger-derived status.

Return ledger-derived source status, task and Goal evidence, managed checkout
map, edits and validation, pull-request refs and ready state, current review/CI
proof, blockers, recovery freshness, and next safe action. Success requires the
fixed PR-ready conclusion for every affected repository. Reference full
artifacts by path/ref and fingerprint instead of repeating them.

## References

- `references/options.md`: App orchestration option registry.
- `references/merge-authorization.md`: separately loaded post-conclusion merge
  authority.
- `references/ledger.md`: ledger, claims, task registry, and state.
- `references/worker.md`: visible App Feature Spec task contract.
- `references/multi-repo-workspace.md`: managed multi-repo App execution.
- `references/spec-backed-delivery.md`: execution-ready bundle, delivery,
  and authority contract.
- `references/stacked-feature-specs.md`: two-Spec stack.
- `references/gates.md`: proof and closeout gates.
- `references/codex-review-closeout.md`: PR review closeout.
- `references/recovery-validation.md`: App recovery validation.
- `references/runtime-efficiency.md`: multi-wave delta evidence and metrics.

## Claim Helper Maintenance

`scripts/orchestrator-claim` is the only supported atomic-claim artifact. It is
a standard-library Python script with `__version__` as its semver source of
truth and no maintenance project. Change it in place, then re-run `--help`,
`--version`, `--json doctor`, the competing-root fixture, and the focused App
contract tests. Use major versions for breaking command or JSON contracts,
minor versions for backward-compatible commands, and patches for fixes.
