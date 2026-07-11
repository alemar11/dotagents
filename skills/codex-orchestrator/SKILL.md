---
name: codex-orchestrator
description: Coordinate Codex Goal mode, workers, portfolio ledgers, gates, autoreview, Git/GitHub companion skills, and authorized merge-ready closeout.
---

# Codex Orchestrator

## Purpose And Invocation

Use this Codex-dependent skill as the root control plane for explicit
orchestration sessions across one or more repositories. Use it only when the
owner invokes `$codex-orchestrator` or asks to run Codex Orchestrator; do not
auto-select it for ordinary implementation, planning, triage, GitHub, commit,
PR, or multi-repo requests.

The root owns source routing, the active-root claim, Goal mode or its ledger
fallback, worker lifecycle, integration, gates, ledger updates, publication,
source closeout, and the final status. Workers own only the scoped inspection,
implementation, validation, and report assigned by the root.

## Non-Negotiable Invariants

- Resolve the ledger with `references/ledger.md` before implementation,
  worker creation, or source mutation. Stop as `needs-owner` when another live
  root claims overlapping repo realpaths or source ids.
- A worker never becomes another root. Workers do not edit the ledger, create
  workers, subdelegate, choose takeover or handoff, mutate sources, invent
  branch or PR strategy, or decide closeout.
- Worker authorization is resolved only by the root orchestrator per workstream
  and session.
- Keep overlapping contracts, shared integration ownership, gate decisions,
  final publication decisions, and closeout in the root thread. The root may
  assign exact authorized integration or publication operations to a visible
  App worker that owns the managed worktree; the worker does not acquire those
  decisions or broader authority.
- Treat worker status as evidence, not a final lifecycle decision.
- Preserve user-owned dirty worktrees and the caller checkout unless the
  resolved source contract or owner explicitly authorizes a different action.
- In a Codex App session, creating or allocating a new dedicated worker,
  integration, or publication worktree requires a visible App worker thread
  targeted to that worktree. Do not implement through CLI subagents in the
  caller checkout and later relocate the result into an unmanaged worktree.
  This rule does not apply in CLI-only sessions. If App thread/worktree
  creation is unavailable, record the limitation and obtain explicit fallback
  authority before creating a raw Git worktree.
- Do not turn read-only discovery into GitHub, release, automation, or other
  external writes without the authority required by the source contract and
  matching companion skill.

## Source Routing

Register every task source before scheduling it. Record a stable source id/ref,
repo, acceptance criteria, current source state, mutation authority, and
closeout target. The ledger is the runtime projection; the source remains the
acceptance and closure authority unless the owner explicitly migrates it.

| Source shape | Route |
| --- | --- |
| Rough feature intent without a durable PRD and generated issues | Run `$plan-feature` full-flow before implementation scheduling. |
| Existing durable PRD without generated issues | Run `$plan-feature` in `issues-from-existing-prd` mode unless the request is inspect-only. |
| PRD-backed issue, linked partial PRD, `Source PRD`, or `## Orchestrator Handoff` | Load `references/prd-backed-delivery.md`; it owns graph expansion, delivery, publication, issue mutation, and PRD closeout. |
| Generated issue with a valid `## Orchestrator Handoff` | Register directly; use the handoff as the canonical issue-level dispatch projection. |
| Generated issue with no valid handoff | Inspect or regenerate through `$plan-feature`; implement only when the owner explicitly authorizes ad-hoc execution from the current body. |
| PR, review thread, CI failure, bug, local checklist, implementation plan, TODO, explicit implementation request, or legacy issue without a PRD delivery contract | Register directly. Default implementation to local code/docs edits plus validation; do not require delivery-mode, branch, PR, parallelization, or source-closeout metadata. Record runtime delivery as `local-only`, publication as `none`, issue mutation as `none`, and closeout as local acceptance criteria plus validation. |

For ad-hoc and legacy sources, missing publication metadata is not a blocker.
Commit, push, PR delivery, issue mutation, merge, release, and deployment remain
unavailable until the owner explicitly authorizes the action or delivery path.
When the owner authorizes `pull-request` delivery, default
`pr_closeout=merge-ready`; this includes ready-for-review transition and Codex
review but not merge. A contradictory or unsafe source contract is still a real
blocker; absence of a PRD contract is not.

`$plan-feature` owns PRD and generated-issue publication before implementation
scheduling. After the root registers a generated issue, the root owns its
authorized lifecycle mutations and closeout evidence. For workspace features,
expand linked repo-scoped partial PRDs and register the connected graph; no
global PRD is required. For Markdown plans or checklists, register each
actionable item with its nearest heading and stable path/anchor.

## Controller State Machine

Run this deterministic loop:

1. **CLAIM** — resolve the named ledger, canonicalize repo realpaths, acquire or
   verify the active-root claim, and establish Goal mode or its ledger fallback.
2. **REGISTER** — snapshot authorized sources and reconcile them by stable
   source id. Preserve acceptance criteria, mutation authority, owner
   constraints, dependencies, proof, and closeout target.
3. **ROUTE** — apply the source table, load only the references needed by the
   selected branches, choose companion skills, and classify workstreams with
   the ledger vocabulary.
4. **DISPATCH** — select one bounded wave. Keep shared work in the root; use
   `references/worker.md` before any delegation and record the execution report
   it defines.
5. **INTEGRATE** — monitor workers from current ledger state, read before
   steering or lifecycle changes, revalidate worker capabilities after create,
   resume, or fork, integrate accepted output, and record proof, blockers,
   artifacts, and next actions.
6. **GATE** — apply `references/gates.md`, run focused validation and
   `$autoreview` for non-trivial edits, perform only authorized publication and
   source mutations, and re-run affected gates after fixes.
7. **RECONCILE** — rescan every due source, replace stale current-state
   projections, update the ledger and authorized source state, and record a
   reconciliation result before returning to **REGISTER** while actionable work
   remains. Run the same reconciliation immediately before final closeout.

Each wave must create a ledger transition, new proof, an authorized source
update, an owner decision brief, or an explicit no-progress record. Never loop
silently on an unchanged worker or source snapshot.

Stop only when the objective is complete or a real gate blocks progress. Before
final closeout, there must be no active worker needing orchestration, actionable
`autonomous` candidate, authorized `ready-next` action, due check that can be
performed now, or newly surfaced source item.

## Goal And Persistence

For implementation or publication, establish the root goal after **CLAIM** and
before root-owned edits or worker dispatch:

```text
Complete <portfolio/source scope> through validated closeout and, when
authorized for pull-request delivery, merge-ready PR state. Continue until
completion or a real gate/blocker stops progress.
```

Use `/goal` or the current runtime goal tool when available. If Goal mode is
unavailable, record the same objective and the fallback reason in the ledger's
active-root section and enforce it from there. Goal mode never expands scope or
bypasses authorization, gates, owner decisions, or source closeout rules.

Real blockers include missing owner decisions, credentials or access, unsafe or
contradictory source contracts, failed required gates, unresolved dependency
proof, unavailable required tools, unpollable or timed-out external checks, and
missing authority for a required closeout action. Ordinary multi-step work,
newly unblocked waves, fix-and-retest cycles, pollable checks, and authorized
`ready-next` actions are not blockers.

## Workers And Runtime Surfaces

Invoking this skill authorizes internal CLI subagents when useful and allowed by
the active runtime policy, unless the owner says `root only`, `no delegation`,
`no subagents`, or sets a tighter limit. The root chooses the split; it may also
keep work local when delegation adds no value.

Visible user-owned Codex App worker threads require explicit session-scoped
consent and a bounded maximum before creation. In owner-facing wording,
`thread` means a visible App thread; do not silently substitute an internal
subagent. Ask only when runtime policy requires it, when visible App threads are
requested or useful, or when a requested worker surface needs an explicit
fallback decision.

In a Codex App session, the root's decision to use a new dedicated worker,
integration, or publication worktree makes a visible App thread required, not
an optional presentation choice. Owner wording such as `you can use Codex
threads if needed` supplies session consent; when it omits a maximum, cap the
surface at one concurrent visible worker. Create the App thread with a worktree
environment before implementation begins and keep implementation, validation,
commit, and publication execution in that managed surface when authorized by
the root. Integration ownership, publication decisions, gates, and closeout
remain in the root thread. In CLI-only sessions, CLI subagents and raw Git
worktrees remain valid.

Load `references/worker.md` before delegation. It owns worker surfaces, startup
consent wording, authorization modes, no-subdelegation, prompts, execution
reports, lifecycle, resync, integration, artifacts, and worker evidence. Do not
copy session worker choices into PRDs, issues, project memory, or handoff
sections. Automations remain explicit-only and runtime-tool-dependent.

If a required Codex tool is not visible, search the available tool registry by
operation before declaring it unavailable. Continue with safe root-owned work
when possible and record the exact missing surface or fallback.

At worker creation, resume, fork, and before any network, publication, or
external-mutation action, capture the capability snapshot required by
`references/worker.md`. A fork does not imply a broader permission profile. If
a worker loses a required capability, stop retrying that operation in the
worker and route it to a capable root surface when the existing authority and
gates permit it.

## Delivery, Gates, And Closeout

For PRD-backed sources, load `references/prd-backed-delivery.md` before
scheduling or publication and follow its separate delivery, publication, and
issue-mutation authorities. Do not infer missing PRD semantics or let workers
invent branch, PR, or closeout behavior.

For ad-hoc and legacy sources, use the `local-only` default in **Source
Routing**. Local completion requires acceptance criteria plus appropriate
validation; it does not require a commit, PR, or tracker mutation. If the owner
later authorizes publication, record the new authority and route it through the
matching companion skill before acting.

Apply `references/gates.md` before owner-ready, issue-closed, merge-ready,
release-ready, or final status. For `pull-request`, default
`pr_closeout=merge-ready`; opening the PR as draft is only the initial state.
Do not declare merge-ready until the PR is out of draft,
GitStack review-status preflight has reused or requested exactly one review for
the current head, a verified terminal Codex result covers that head, actionable
feedback is resolved or explicitly dispositioned, fixes are validated and
published, and the publication checkout is clean. A terminal current-head
result may be a formal review or verified provider-authored result comment; its
GitHub object type alone never justifies another `@codex review` request. Use
`pr_closeout=draft-only` only for an explicit current-user instruction about
the PR lifecycle or a structured PRD `PR closeout: draft-only` value. Draft-only completes after
validation and draft publication, marks downstream ready/review/merge-ready
gates `not-applicable`, and resumes at ready-for-review if the user removes the
restriction. `Draft PR`, `open a draft PR`, and `do not merge automatically`
do not select draft-only. Neither does Plan Feature's separate `draft-only
output` no-mutation instruction.

Update target-repo `AGENTS.md` only with explicit documentation/write authority
from the owner or source contract; otherwise report the proposed change. Source
comments, labels, direct closure, merge, release, and deployment likewise
require their own authority.

Merge is root-owned and unavailable by default. Record
`merge_authority=explicit-owner-authorization` only when the owner explicitly
directs the orchestrator to merge or land the named PR or PR set. Record
`merge_policy=automatic-after-gates` only when that instruction also authorizes
the root to proceed after gates without another owner checkpoint; otherwise use
`merge_policy=owner-approval`. Wording such as finish, complete, deliver, or
make merge-ready does not authorize merge.

## Companion Routing

Use the smallest matching GitStack bundled skill:

| Workstream | Skill |
| --- | --- |
| Multi-repo read-only queue scan | `$gitstack:github-portfolio-triage` |
| Current-repo issue/PR queue triage | `$gitstack:github-triage` |
| Issue creation or lifecycle mutation | `$gitstack:github-issues` |
| Evidence-first issue, PR, bug, or fix-quality review | `$gitstack:github-deep-review` |
| GitHub Actions checks and logs | `$gitstack:github-ci` |
| PR review threads, Codex review requests, or replies | `$gitstack:github-review-threads` |
| Release readiness, tags, notes, assets, or packages | `$gitstack:github-releases` |
| Local commit and optional push without PR publication | `$gitstack:git-commit` |
| Branch publication plus draft PR creation/update | `$gitstack:yeet` |

Portfolio triage is read-only. Follow-up mutations require the matching skill
and the authority described above.

GitStack companion skills are the primary Git/GitHub route. Within GitStack,
prefer the official GitHub connector for supported remote operations and use
authenticated `gh` only for connector gaps or transport/authentication
failures. Do not fall back for missing owner authority, failed gates, unsafe or
contradictory source contracts, actionable review findings, or correctable
command input. Never run primary and fallback mutations in parallel. The
fallback inherits the exact existing scope and
mutation authority; it cannot broaden either. Record the primary skill,
attempted operation, failure category and evidence, fallback operation,
authority check, and result in the ledger.

## Final Report

Return a compact status report derived from the current ledger: reconciled
sources, worker usage/evidence, local edits and validation, publication/source
mutations, active-root decision, gates and proof, blockers or owner decisions,
fallbacks, and the next safe action. Use `references/worker.md` and
`references/ledger.md` for exact report and closeout fields.

## References

- `references/ledger.md`: ledger resolution, active-root claims, state
  vocabulary, wave records, and closeout hygiene.
- `references/worker.md`: worker surfaces, prompts, authorization modes,
  no-subdelegation, lifecycle, integration, and reports.
- `references/prd-backed-delivery.md`: PRD graph expansion, delivery,
  publication, issue mutation, Codex PR review, and closeout.
- `references/gates.md`: owner-ready, merge, release, CI, autoreview, and
  cross-repo integration gates.
