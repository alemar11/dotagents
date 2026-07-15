---
name: codex-orchestrator
description: Explicitly coordinate Codex source graphs, workers, gates, ledgers, and authorized delivery closeout.
---

# Codex Orchestrator

## Purpose And Invocation

Use this Codex-dependent skill as the root control plane for an explicit
orchestration session across one or more repositories. Use it only when the
owner invokes `$codex-orchestrator` or asks to run Codex Orchestrator. Do not
auto-select it for ordinary implementation, planning, triage, GitHub, commit,
PR, or multi-repo requests.

The root always owns source routing, the active-root claim, its root Goal mode
or ledger fallback, worker lifecycle, permission and strategy decisions,
ledger state, source closeout, and final status. Every visible Codex thread the
root creates owns a separate assignment-scoped Goal or recorded runtime
fallback. Execution ownership depends on the resolved worker mode. When visible
Codex threads are not enabled, workers own only their assigned inspection,
implementation, validation, and report. When
`visible_app_task_permission=granted-by-authorized-user`, exactly one visible
thread owns each implementation-eligible Feature Spec through its complete
merge-ready PR lifecycle; the root becomes orchestration-only for that work.

## Non-Negotiable Invariants

- Load `references/options.md` during **CLAIM**. Resolve session options then;
  resolve authority and delivery options separately for each stable source or
  workstream ID after registration and before its dispatch or mutation. Use
  canonical snake_case fields and lower-kebab values. Preserve owner/source
  prose only as option-resolution evidence; downstream logic reads canonical
  values, never phrases or booleans.
- Resolve `references/ledger.md` before implementation, worker creation, or
  source mutation. Stop as `needs-owner` when another live root claims an
  overlapping repo realpath or source id.
- Workers never become roots: no ledger edits, visible App task or sibling/root
  worker management, takeover/handoff decisions, source mutation, branch/PR
  strategy decisions, merge decisions, or final source closeout. An assigned
  visible Feature Spec thread does own the already-decided implementation,
  integration, validation, publication, Codex-review request and polling,
  feedback disposition and fixes, CI, parent-closing-keyword preparation, and
  ready transition required for its selected delivery target. Any worker may
  create and manage internal background subagents within its assigned scope and
  action set; those subagents inherit the same authority ceiling and report
  through their parent.
- Every orchestrator-created visible Codex thread must establish or resume its
  own assignment-scoped Goal before starting work. The root supplies the exact
  objective and terminal delivery target, verifies thread-reported Goal
  evidence, and records a fallback only when the runtime Goal tool is absent.
  This is an automatic worker invariant, not a user option, and it does not
  apply to internal background subagents.
- The root resolves `worker_allowed_actions` per workstream. Actions are
  explicit, independent, and non-cumulative; allowed paths can narrow an action
  but never grant another one.
- Keep shared contracts, permission and strategy decisions, merge, ledger
  closeout, and final source status in the root. Outside mandatory visible
  Feature Spec thread mode, also keep integration and gate decisions in the
  root. Inside that mode, the assigned thread executes the complete decided
  delivery and gate sequence while the root only monitors and reconciles its
  evidence.
- Treat worker status as evidence, not lifecycle or source closeout. Read the
  latest worker state before steering or lifecycle changes.
- Preserve user-owned uncommitted changes. Preserve the caller checkout unless
  the scoped option row is
  `starting_checkout_branch_handling=branch-switch-authorized`.
- In the Codex App, every newly created dedicated worker, integration, or
  publication worktree must belong to a visible App task created for that
  worktree. If that surface is unavailable, require
  `unmanaged_git_worktree_fallback_permission=granted-by-authorized-user`
  before an unmanaged Git worktree fallback.
  Without visible consent, App root/background work stays in an existing
  owner-supplied checkout unless the owner grants one of those checkout paths.
  CLI-only sessions are exempt.
- Read-only discovery never grants GitHub, release, automation, or other
  external mutation authority.
- Treat the ledger `## Recovery Packet` as a compact derived projection, never
  as authority. On resume, use it only after its repo HEAD/worktree and source
  fingerprints match current state; otherwise invalidate it and run full
  reconciliation before mutation or dispatch.
- After the first full snapshot, carry evidence by path/ref, fingerprint,
  changed section, proof command/result, and failed-gate excerpt. Do not re-emit
  complete unchanged ledgers or diffs during ordinary controller iterations.
- Record exact phase-token deltas only from root-scoped counters over an
  uncontaminated phase interval. Label interleaved cumulative deltas as
  `exact-interval`, not phase usage; otherwise use `unavailable`. Usage metrics
  never weaken gates or block progress.

## Source Routing

Register every source before scheduling it. Record its stable id/ref, repo,
acceptance criteria, current state, mutation authority, dependencies, and
closeout target. The ledger is the runtime projection; the source remains the
acceptance and closure authority.

| Source shape | Route |
| --- | --- |
| Rough intent without durable Feature Spec and issues | Run `$plan-feature` `full-flow` before implementation scheduling. |
| Durable Feature Spec without generated issues | Run `$plan-feature` `issues-from-existing-spec` unless inspect-only. |
| Feature Spec-backed issue, linked partial Feature Spec, `source_spec_ref`, or `## Orchestrator Handoff` | Load `references/spec-backed-delivery.md`; reject retired vocabulary before registration. |
| Generated issue with valid handoff | Register directly; the handoff is its canonical dispatch projection. |
| Generated issue without valid handoff | Inspect or regenerate through `$plan-feature`; implement only with explicit ad-hoc authority. |
| PR, review, CI failure, bug, checklist, plan, TODO, implementation request, or other non-Feature-Spec issue | Register directly with `change_delivery_target=validated-changes-left-uncommitted`, `change_delivery_permission=not-required-for-uncommitted-changes`, `issue_update_permission=no-issue-changes`, and local acceptance plus validation closeout. |

For ad-hoc sources, missing publication metadata is not a blocker.
Commit, push, PR, issue mutation, merge, release, and deployment require
explicit permission. Authorized Feature Spec delivery defaults to
`change_delivery_target=pull-request-ready-for-merge-but-not-merged`, which
never authorizes merge.

`$plan-feature` owns Feature Spec and generated-issue publication before scheduling.
After registration, the root owns authorized issue lifecycle and closeout. For
`repository_layout=multi-repository-workspace`, expand linked repo-scoped partial
Feature Specs; no global Feature Spec is required. Register Markdown checklist
items by stable path and heading.

## Controller Loop

Run this deterministic loop:

1. **CLAIM** — resolve canonical options, resolve the ledger, canonicalize repo
   realpaths, acquire or verify the active-root claim, and establish Goal mode
   or its ledger fallback. Resolve `repository_layout` from project memory, safe
   repo evidence, or explicit owner input.
   On recovery, read and validate the compact recovery packet first; when fresh,
   load only its named active rows, gate rows, sources, and next action.
2. **REGISTER** — snapshot authorized sources by stable id and preserve their
   criteria, constraints, authority, dependencies, proof, and closeout target.
3. **ROUTE** — apply source routing, load only the selected references, choose
   companion skills, and classify workstreams with ledger vocabulary. Load
   `references/multi-repo-workspace.md` only for
   `repository_layout=multi-repository-workspace` or a registered source/handoff
   with `workspace_context=multi-repository-workspace`.
4. **DISPATCH** — select one bounded wave and load `references/worker.md` before
   any delegation. For every created or resumed visible thread, require its
   assignment-scoped Goal or unavailable-tool fallback before work starts. In
   mandatory visible Feature Spec thread mode, create or resume the single
   assigned thread for each eligible Feature Spec; never keep that Spec's
   implementation or review work in the root.
5. **INTEGRATE** — read current worker state, revalidate capabilities, accept or
   reject reported evidence, and record lifecycle decisions. In mandatory
   visible Feature Spec thread mode, the assigned thread integrates its own
   work; the root must not apply, copy, reimplement, validate, or repair it.
6. **GATE** — apply `references/gates.md`. Outside mandatory visible Feature
   Spec thread mode, run focused validation, `$autoreview` for non-trivial
   edits, and authorized publication/source mutations in the owning execution
   surface. Inside that mode, require the assigned thread to execute every
   implementation and PR gate through merge-ready while the root monitors its
   evidence and sends corrective messages when it drifts. Use
   status, diff stat/name lists, and focused hunks during iteration; read the
   complete relevant diff only for review/publication or a failing gate.
7. **RECONCILE** — rescan due sources, replace stale projections, record the
   reconciliation result, and return to **REGISTER** while action remains.

Every wave must produce a ledger transition, proof, authorized source update,
owner decision brief, or explicit no-progress record. Never loop silently.
Update the recovery packet, delta evidence index, and exact phase metrics (or
one `unavailable` record) at the same boundary.
Load `references/recovery-validation.md` only when resuming from a packet. Load
`references/runtime-efficiency.md` before entering a second wave or recording
exact counters; a simple first wave need not load either reference.
Before final closeout, reconcile again and require no active worker,
`autonomous` candidate, authorized `ready-next` action, due check, or newly
surfaced source item.

## Goal And Persistence

After **CLAIM** and before edits or dispatch, establish this root objective for
implementation/publication:

```text
Complete <portfolio/source scope> through validated closeout and, when
authorized for `pull-request-ready-for-merge-but-not-merged`, that exact
delivery target. Continue until
completion or a real gate/blocker stops progress.
```

Use Goal mode when available. Otherwise record the objective and fallback
reason in the active-root ledger section. Goal mode never expands scope or
bypasses authority, gates, owner decisions, or source closeout.

The root Goal coordinates the portfolio; it never substitutes for a visible
thread's own Goal. Each orchestrator-created visible thread must use the
runtime Goal tool in its own context before implementation, with an objective
derived from its exact assignment and selected delivery target. The root sends
that instruction in the initial prompt and verifies the thread's reported Goal
state before advancing it beyond `created`. A resumed thread reuses its
matching active Goal; a replacement thread creates a new one. The thread marks
its Goal complete only after its assigned terminal target and gates are
actually satisfied. When the runtime exposes no Goal tool, the thread records
the same objective plus the unavailability reason as its fallback and may
continue. Internal background subagents do not require independent Goals.

Real blockers include missing owner decisions, credentials/access,
unsafe/contradictory contracts, failed required gates, unresolved dependency
proof, unavailable required tools, unpollable external checks, or missing
authority for required closeout. Multi-step work, newly unblocked waves,
fix/retest cycles, pollable checks, and authorized `ready-next` work are not
blockers.

## Workers And Runtime Surfaces

Resolve `visible_app_task_permission`, `unmanaged_git_worktree_fallback_permission`,
and `repository_layout` from `references/options.md`. Defaults are
`visible_app_task_permission=not-requested`, and
`unmanaged_git_worktree_fallback_permission=not-granted`. Visible user-owned App
tasks require `visible_app_task_permission=granted-by-authorized-user`. That
value selects mandatory visible Feature Spec thread mode: create exactly one
visible thread per implementation-eligible Feature Spec, title it with the
exact Feature Spec title, and keep all of that Spec's issue, repo, PR,
Codex-review, CI, and merge-readiness work in that thread. The root chooses only
when those threads start and whether they run serially or in parallel from
dependencies and live capacity. The root and every spawned Codex thread may
use internal background subagents within their assigned scope; no user
worker-count or topology option exists.

Load `references/worker.md` before delegation. It owns current tool mapping,
surface wording, permission, capability snapshots, worker actions, prompts,
execution reports, resync, integration, artifacts, and lifecycle. Do not copy
session worker choices into Feature Specs, issues, project memory, or handoffs.

When mandatory visible Feature Spec thread mode is selected, create the thread
and its managed worktree before implementation, title it, then require and
verify its thread-owned Goal or unavailable-tool fallback. If the visible
create/read/message surface cannot represent the assignment, stop or replace
the visible thread; never fall back to root-owned or background-only
implementation, integration, validation, review, or review polling for that
Feature Spec. Input
wording may supply option-resolution evidence, but the root must persist the
resolved fields before creating a visible worker. It must never carry the
wording itself as a worker permission, count, topology, or scheduling value.

At worker create, reuse, resume-equivalent, or fork—and before any network or
external mutation—record the capability snapshot required by `worker.md`. A
fork does not imply broader permissions. Search the current tool registry when
an operation is missing; record the actual fallback instead of claiming a
nonexistent resume, close, or scheduling action.

## Delivery, Gates, And Closeout

For Feature Spec-backed sources, load `references/spec-backed-delivery.md`
before scheduling or delivery. It owns the selected delivery target, delivery
permission, issue updates, review requirement, and merge permission. For ad hoc
sources, local acceptance plus validation completes
`validated-changes-left-uncommitted`; any later commit, push, or PR requires a
new exact delivery target and permission row.

Load `references/gates.md` before owner-ready, issue-closed, merge-ready,
release-ready, or final status. It owns gate selection and conditionally routes
`pull-request-ready-for-merge-but-not-merged` through the canonical current-head
Codex review and parent Feature Spec closeout algorithm. Its review default is
`codex_review_requirement=required-on-current-pull-request-head`; an exact
scoped authorized-user instruction may select
`explicitly-skipped-by-authorized-user`, which bypasses only the review request
and wait. `validated-draft-pull-request-published` never enters that route.
In mandatory visible Feature Spec thread mode, the assigned thread owns the
pre-merge parent-closeout mutation and proof required for its PR to become
merge-ready. The root owns the ledger watch, any authorized merge, post-merge
verification, and final source closeout. `armed` is not actual closure, and
neither the parent Feature Spec nor the ledger completes before merge and
verified issue closure.

Merge is root-owned and unavailable by default. Set
`pull_request_merge_permission=granted-for-named-pull-request` only for an
explicit instruction to merge or land the named PR or PR set. Use
`pull_request_merge_confirmation=merge-automatically-after-checks` only when
the same instruction waives another checkpoint; otherwise use
`ask-authorized-user-after-checks`.

Target-repo `AGENTS.md` changes, source comments/labels/direct closure, merge,
release, and deployment each require matching authority.

## Companion Routing

| Workstream | GitStack skill |
| --- | --- |
| Multi-repo read-only queue | `$gitstack:github-portfolio-triage` |
| Current-repo issue/PR queue | `$gitstack:github-triage` |
| Issue creation/lifecycle | `$gitstack:github-issues` |
| Evidence-first deep review | `$gitstack:github-deep-review` |
| GitHub Actions | `$gitstack:github-ci` |
| PR review threads/Codex review | `$gitstack:github-review-threads` |
| Releases | `$gitstack:github-releases` |
| Local commit/optional push | `$gitstack:git-commit` |
| Branch publication/draft PR | `$gitstack:yeet` |

Use the smallest matching workflow. Within GitStack, use the official GitHub
connector first and authenticated `gh` only for connector gaps or transport
failure. Never fall back for missing authority, failed gates, unsafe contracts,
actionable findings, or correctable input. Record the workflow skill, primary
operation/evidence, fallback reason/operation, reused authority, and result.

## Final Report

Return a compact ledger-derived status: reconciled sources, worker evidence,
edits/validation, publication/source mutations, active-root decision, gates and
proof, blockers/owner decisions, fallbacks, next safe action, recovery-packet
freshness, canonical option snapshot/resolution evidence, and phase-token
evidence (`exact-phase`, `exact-interval`, or `unavailable`). Reference full
artifacts by path/ref and fingerprint instead of repeating them. Use
`references/worker.md` and `references/ledger.md` for exact fields.

## References

- `references/options.md`: canonical option fields, values, defaults,
  cross-field validation, and the strict input boundary.
- `references/ledger.md`: ledger resolution, claims, state, wave records, and
  closeout hygiene.
- `references/worker.md`: worker surfaces, tools, authorization, lifecycle,
  integration, and reports.
- `references/multi-repo-workspace.md`: parent/child repo ownership,
  child-worktree layout, derived serial/parallel dispatch, and cross-repo
  integration/closeout for `repository_layout=multi-repository-workspace` or
  `workspace_context=multi-repository-workspace`.
- `references/spec-backed-delivery.md`: Feature Spec graph, authorities, publication,
  issue mutation, review, and closeout.
- `references/gates.md`: authorization, proof, review, integration, release,
  and closeout gates.
- `references/recovery-validation.md`: conditional Recovery Packet freshness
  validation before resumed mutation or dispatch.
- `references/runtime-efficiency.md`: conditional multi-wave delta-evidence
  transport and exact phase-token metrics.
