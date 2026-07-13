---
name: codex-orchestrator
description: Explicitly coordinate Codex source graphs, workers, gates, ledgers, and authorized merge-ready closeout.
---

# Codex Orchestrator

## Purpose And Invocation

Use this Codex-dependent skill as the root control plane for an explicit
orchestration session across one or more repositories. Use it only when the
owner invokes `$codex-orchestrator` or asks to run Codex Orchestrator. Do not
auto-select it for ordinary implementation, planning, triage, GitHub, commit,
PR, or multi-repo requests.

The root owns source routing, the active-root claim, Goal mode or ledger
fallback, worker lifecycle, integration, gates, publication decisions, source
closeout, and final status. Workers own only their assigned inspection,
implementation, validation, and report.

## Non-Negotiable Invariants

- Resolve `references/ledger.md` before implementation, worker creation, or
  source mutation. Stop as `needs-owner` when another live root claims an
  overlapping repo realpath or source id.
- Workers never become roots: no ledger edits, subdelegation, worker/thread
  management, takeover/handoff decisions, source mutation, branch/PR strategy,
  merge, or closeout decisions.
- The root resolves worker authorization per workstream. Capability modes are
  explicit and non-cumulative; allowed paths or surfaces can narrow a mode but
  never grant another one.
- Keep shared contracts, integration, gate decisions, publication decisions,
  and closeout in the root. A worker may execute exact authorized publication
  operations without acquiring those decisions.
- Treat worker status as evidence, not lifecycle or source closeout. Read the
  latest worker state before steering or lifecycle changes.
- Preserve user-owned dirty worktrees and the caller checkout unless the source
  contract or owner explicitly authorizes another action.
- In the Codex App, every newly created dedicated worker, integration, or
  publication worktree must belong to a visible App task created for that
  worktree. If that surface is unavailable, obtain explicit authority before a
  raw Git worktree fallback. CLI-only sessions are exempt.
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
| Rough intent without durable PRD and issues | Run `$plan-feature` `full-flow` before implementation scheduling. |
| Durable PRD without generated issues | Run `$plan-feature` `issues-from-existing-prd` unless inspect-only. |
| PRD-backed issue, linked partial PRD, `Source PRD`, or `## Orchestrator Handoff` | Load `references/prd-backed-delivery.md`. |
| Generated issue with valid handoff | Register directly; the handoff is its canonical dispatch projection. |
| Generated issue without valid handoff | Inspect or regenerate through `$plan-feature`; implement only with explicit ad-hoc authority. |
| PR, review, CI failure, bug, checklist, plan, TODO, implementation request, or legacy issue | Register directly with `local-only` delivery, publication/issue mutation `none`, and local acceptance plus validation closeout. |

For ad-hoc and legacy sources, missing publication metadata is not a blocker.
Commit, push, PR, issue mutation, merge, release, and deployment require
explicit authority. Authorized pull-request delivery defaults to
`pr_closeout=merge-ready` but never authorizes merge.

`$plan-feature` owns PRD and generated-issue publication before scheduling.
After registration, the root owns authorized issue lifecycle and closeout. For
workspace features, expand linked repo-scoped partial PRDs; no global PRD is
required. Register Markdown checklist items by stable path and heading.

## Controller Loop

Run this deterministic loop:

1. **CLAIM** — resolve the ledger, canonicalize repo realpaths, acquire or
   verify the active-root claim, and establish Goal mode or its ledger fallback.
   On recovery, read and validate the compact recovery packet first; when fresh,
   load only its named active rows, gate rows, sources, and next action.
2. **REGISTER** — snapshot authorized sources by stable id and preserve their
   criteria, constraints, authority, dependencies, proof, and closeout target.
3. **ROUTE** — apply source routing, load only the selected references, choose
   companion skills, and classify workstreams with ledger vocabulary.
4. **DISPATCH** — select one bounded wave; keep shared work in the root and load
   `references/worker.md` before any delegation.
5. **INTEGRATE** — read current worker state, revalidate capabilities, accept or
   reject output, rerun root-owned proof, and record lifecycle decisions.
6. **GATE** — apply `references/gates.md`, focused validation, `$autoreview` for
   non-trivial edits, and only authorized publication/source mutations. Use
   status, diff stat/name lists, and focused hunks during iteration; read the
   complete relevant diff only for review/publication or a failing gate.
7. **RECONCILE** — rescan due sources, replace stale projections, record the
   reconciliation result, and return to **REGISTER** while action remains.

Every wave must produce a ledger transition, proof, authorized source update,
owner decision brief, or explicit no-progress record. Never loop silently.
Update the recovery packet, delta evidence index, and exact phase metrics (or
one `unavailable` record) at the same boundary.
Load `references/runtime-efficiency.md` before resuming from a packet, entering
a second wave, or recording exact counters; a simple first wave need not load it.
Before final closeout, reconcile again and require no active worker,
`autonomous` candidate, authorized `ready-next` action, due check, or newly
surfaced source item.

## Goal And Persistence

After **CLAIM** and before edits or dispatch, establish this root objective for
implementation/publication:

```text
Complete <portfolio/source scope> through validated closeout and, when
authorized for pull-request delivery, merge-ready PR state. Continue until
completion or a real gate/blocker stops progress.
```

Use Goal mode when available. Otherwise record the objective and fallback
reason in the active-root ledger section. Goal mode never expands scope or
bypasses authority, gates, owner decisions, or source closeout.

Real blockers include missing owner decisions, credentials/access,
unsafe/contradictory contracts, failed required gates, unresolved dependency
proof, unavailable required tools, unpollable external checks, or missing
authority for required closeout. Multi-step work, newly unblocked waves,
fix/retest cycles, pollable checks, and authorized `ready-next` work are not
blockers.

## Workers And Runtime Surfaces

Invoking this skill authorizes internal Codex subagents (`cli-subagent` in the
ledger) when useful unless the owner disables or limits delegation. Visible
user-owned App tasks require explicit session consent and a bounded maximum;
`thread` in owner-facing wording means that visible App surface.

Load `references/worker.md` before delegation. It owns current tool mapping,
surface wording, consent, capability snapshots, authorization modes, prompts,
execution reports, resync, integration, artifacts, and lifecycle. Do not copy
session worker choices into PRDs, issues, project memory, or handoffs.

When the App root chooses a new dedicated worktree, create the visible App task
with that worktree before implementation and keep the work in its managed
surface. Owner wording such as `you can use Codex threads if needed` consents to
one concurrent visible worker unless a higher bound is stated.

At worker create, reuse, resume-equivalent, or fork—and before any network or
external mutation—record the capability snapshot required by `worker.md`. A
fork does not imply broader permissions. Search the current tool registry when
an operation is missing; record the actual fallback instead of claiming a
nonexistent resume, close, or scheduling action.

## Delivery, Gates, And Closeout

For PRD-backed sources, load `references/prd-backed-delivery.md` before
scheduling or publication. It owns separate delivery, publication, PR
closeout, issue mutation, and merge authorities. For ad-hoc/legacy sources,
local acceptance plus validation completes `local-only` work; publication is a
later explicit authority change.

Load `references/gates.md` before owner-ready, issue-closed, merge-ready,
release-ready, or final status. Pull-request delivery defaults to
`merge-ready`: validate, leave draft, transition ready, reuse or request exactly
one Codex review per current head, receive a verified terminal result, resolve
or disposition findings, publish fixes, verify current CI, and leave the
publication checkout clean. For a GitHub-backed `merge-ready` final feature or
integration PR that completes the whole PRD and targets the current default
branch, add the parent PRD closing keyword only after the current-head Codex
review gate passes, revalidate that reviewed head around the root-owned PR-body
update, and require parent closeout `armed` before reporting merge-ready. A
non-default-base PR may report merge-ready with a linked later default-branch
closeout vehicle still active; the whole PRD and ledger may not complete until
that vehicle is armed. Because an armed PR remains mutable until merge, keep a
root closeout watch only when the root has explicit merge authority and is the
designated merger; otherwise require a durable owner pre-merge or explicitly
authorized event-driven-automation handoff before reporting merge-ready. Do not
mark the parent PRD or ledger complete until merge and actual issue closure are
verified. Record `not-applicable` for
an explicitly `draft-only` workstream and other excluded workstreams. This arms
closure when the PR merges; it does not authorize direct issue closure or merge.
Use `draft-only` only from an explicit current-user PR lifecycle
instruction or structured PRD value; initial draft wording, `do not merge`, and
Plan Feature `draft-output` do not select it.

Merge is root-owned and unavailable by default. Set
`merge_authority=explicit-owner-authorization` only for an explicit instruction
to merge/land the named PR or PR set. Use `automatic-after-gates` only when the
same instruction waives another checkpoint; otherwise use `owner-approval`.

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
freshness, and phase-token evidence (`exact-phase`, `exact-interval`, or
`unavailable`). Reference full artifacts by path/ref and fingerprint instead of
repeating them. Use
`references/worker.md` and `references/ledger.md` for exact fields.

## References

- `references/ledger.md`: ledger resolution, claims, state, wave records, and
  closeout hygiene.
- `references/worker.md`: worker surfaces, tools, authorization, lifecycle,
  integration, and reports.
- `references/prd-backed-delivery.md`: PRD graph, authorities, publication,
  issue mutation, review, and closeout.
- `references/gates.md`: authorization, proof, review, integration, release,
  and closeout gates.
- `references/runtime-efficiency.md`: conditional recovery validation,
  delta-evidence transport, and exact phase-token metrics.
