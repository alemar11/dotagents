---
name: codex-orchestrator
description: Coordinate Codex Goal mode, workers, portfolio ledgers, gates, autoreview, Git/GitHub companion skills, and authorized merge-ready closeout.
---

# Codex Orchestrator

## Overview

Use this Codex-dependent skill as the control plane for maintainer work across
one or more repositories. It coordinates named portfolio ledgers, read-only
standalone Git/GitHub companion skills, visible Codex App worker threads,
CLI/subagent worker threads, Codex Goal mode when available, ledger-driven
progress monitoring, gates, `$autoreview`, and owner-ready or authorized
merge-ready status reports.

This skill is not a worker. It delegates scoped work, monitors progress, keeps
the ledger current, and decides when a task is ready for owner review, commit,
PR, release, or another explicit decision. Keep the root orchestrator thread
lightweight: it owns routing, lifecycle, integration, gates, ledger updates,
and final publication/authorized merge-ready closeout, while delegated workers
own substantial repository inspection or implementation whenever delegation is
authorized and useful.

## Invocation Boundary

- Use only when the user explicitly invokes `$codex-orchestrator` or explicitly
  asks to run the Codex Orchestrator skill.
- Do not auto-select this skill for ordinary implementation, planning, triage,
  GitHub, commit, PR, or multi-repo requests.
- If a task appears to need orchestration but the user did not invoke this
  skill, handle the task with the normal local workflow or ask before switching
  to orchestration.
- Invoking `$codex-orchestrator` authorizes the root to use CLI subagents when
  useful unless the owner says `root only`, `no delegation`, `no subagents`, or
  equivalent. Visible Codex App worker threads still require explicit
  session-scoped consent.

## Root Ownership Contract

- The root orchestrator owns routing, ledger updates, worker lifecycle,
  integration choice, gate evaluation, Goal mode or ledger fallback state, and
  final closeout decisions.
- One active root orchestrator owns a project or portfolio source graph at a
  time. Before creating workers, starting root-owned implementation, or
  mutating source state, verify the active-root claim in the ledger and stop
  as `needs-owner` if another live root claims overlapping repo realpaths or
  source ids.
- Workers own one scoped repository or workstream plus focused validation and a
  clear final report.
- Worker-reported statuses such as `done`, `blocked`, `needs-owner`, or
  `ready-for-review` are inputs to the root thread, not final lifecycle
  decisions.
- A worker never becomes a second root: workers do not create active-root
  claims, edit ledgers, create workers, or decide takeover, handoff, source
  mutation, branch strategy, or closeout.
- If no inspectable worker surface is available, the owner disabled
  delegation, visible-thread consent is missing for visible App workers, or the
  work is too small or overlapping, keep the work in the root thread.

## Source Routing

Treat every task source as a source item before it becomes a workstream. Record
stable source id/ref, acceptance criteria, source status, closeout target, and
mutation authority. Examples include `github-issue:owner/repo#123`,
`github-pr-thread:owner/repo#45:<thread-id>`, `markdown:/path/plan.md#heading`,
`todo:/path/file.ext:88`, `ci:owner/repo/actions/runs/<id>`, and
`ledger:<portfolio>:<item-id>`. The ledger is the orchestration projection; the
source remains the acceptance and closure authority unless the owner explicitly
migrates it.

| Source shape | Orchestrator action |
| --- | --- |
| Rough feature or product intent without durable PRD plus generated issues | Route through `$plan-feature` full-flow before implementation scheduling. |
| Existing durable PRD without generated issues | Route through `$plan-feature` `issues-from-existing-prd` mode unless the owner only asked for inspect-only review. |
| PRD-backed issue, workspace partial PRD, or generated issue with `Source PRD` | Load `references/prd-backed-delivery.md` before scheduling. It owns partial-PRD graph expansion, draft PRD handling, delivery, publication, Codex PR review, authorized merge-ready closeout, and issue-mutation authority. |
| Durable generated issue with `## Orchestrator Handoff` | Register directly as a source item and use the handoff as the canonical issue-level dispatch contract. |
| Durable generated issue missing `## Orchestrator Handoff` | Register only for inspection or route through `$plan-feature` `issues-from-existing-prd` / issue regeneration before implementation scheduling, unless the owner explicitly authorizes ad hoc execution from the current issue body. |
| PR, CI failure, bug, local checklist, implementation plan, or explicit implementation request | Register directly as source items and decompose into workstreams. |

`$plan-feature` owns PRD and generated issue publication before implementation
scheduling. Once a generated issue is registered as an implementation
workstream, the root orchestrator owns lifecycle and closeout mutations for that
source item, including issue comments, label changes, direct closure when
authorized, real PR link recording, and integration proof.
For generated issues, treat `## Orchestrator Handoff` as the canonical
dispatch section. Copy only the runtime projection needed for scheduling into
the ledger. The issue body and linked PRD remain the durable planning source.

In workspace mode, there is no required global PRD. A GitHub issue or local
issue may point at one repo-scoped partial PRD whose links identify sibling
partial PRDs for the same feature. Treat that connected partial-PRD graph as the
durable feature scope, record every partial PRD/source item in the ledger, and
run independent repo work in parallel only when their dependencies and
integration gates allow it.

For Markdown plans or checklists, enumerate unchecked items with nearest heading
context and a stable path plus line or anchor. Preserve parent context, map each
actionable item to a ledger workstream, and close it by applying/proposing a
file update, moving residual scope to `deferred`, or recording the owner
decision that leaves it open.

## Target Repo Instructions

When orchestration setup needs durable agent instructions in a target
repository, update `AGENTS.md` only with explicit documentation/write authority
from the owner, source item, delivery contract, or project-memory setup.

- If `AGENTS.md` exists and has a Codex orchestration section, update that
  section minimally.
- If `AGENTS.md` exists and lacks a Codex orchestration section, append a short
  section covering one active root owner, parallel workers under that root, and
  takeover or handoff expectations.
- If `AGENTS.md` is missing, create it only when repo instruction files are
  explicitly authorized.
- Without write authority, include the proposed `AGENTS.md` change in the final
  report instead of applying it.

## Loop Semantics

Run orchestration as bounded waves, not as a one-pass checklist:

1. Resolve or initialize the ledger and verify the active-root claim.
2. Snapshot authorized task sources and reconcile them with existing ledger
   workstreams by stable source id.
3. Select the next root-owned and delegated wave.
4. Execute, monitor through the ledger, integrate, and gate the wave.
5. Update the ledger and any authorized source closeout targets.
6. Rescan due sources, then repeat only while there are `active` items,
   actionable `autonomous` candidates, due next checks, authorized `ready-next`
   actions, or newly surfaced source items.

Each wave must produce at least one ledger state transition, new proof, source
update, owner decision brief, or explicit no-progress/blocker record. Do not
loop silently on the same worker status or source snapshot.

## Goal Mode And Stop Contract

For implementation or publication orchestration, establish an explicit Codex
goal after resolving the active-root scope and before dispatching workers or
starting root-owned work. In a Codex surface with Goal mode, set it with
`/goal` or the equivalent runtime goal tool. Use a goal in this shape:

```text
Complete <portfolio/source scope> through validated closeout and, for
pull-request delivery, an authorized merge-ready PR state. Keep going until
completion or a real gate/blocker stops progress.
```

Real gates or blockers include missing owner decisions, missing credentials or
access, failed required gates, unsafe or contradictory source contracts,
unavailable required runtime tools, unresolved dependency proof, external CI or
Codex review waits that cannot be polled from the current runtime or have a
recorded timeout/blocker, missing merge-ready closeout authority, or explicit
owner stop conditions. They do not include ordinary multi-step work, newly
unblocked waves, review-triggered fixes, pollable CI or Codex review waits, or
authorized `ready-next` actions.

If Goal mode is unavailable, disabled, or not exposed in the current surface, do
not block only for that reason. Record the same objective and fallback reason in
the ledger's active-root section, then run the same stop contract from the
ledger. Do not use `/goal` to bypass gates, authorization boundaries, owner
decisions, or source closeout rules.

## Runtime Surfaces

Required surfaces depend on the resolved workstream:

- Codex App thread tools for visible App workers: project lookup before
  project-scoped creation, create/read/message/rename, archive, fork,
  handoff plus handoff-status reads, and optional list/pin.
- CLI/subagent worker tools for inspectable CLI workers: spawn, wait, send, and
  close through the current runtime's subagent or `/agent` equivalent.
- Codex App automation support only when the owner explicitly asks to schedule
  recurring or delayed ledger checks and the current runtime exposes automation
  tooling.
- `$autoreview`, standalone Git/GitHub companions, `$plan-feature`, and ledger
  storage at `~/.cache/dotagents/skills/codex-orchestrator/ledgers/`.

If a required Codex tool is not visible, search the tool registry by operation
name before treating it as unavailable. Record the actual callable tool name
when it differs from the logical name. If a tool or companion skill remains
unavailable, continue only with safe work and report the exact missing surface.

## Delegation Policy

When invoked to implement work, CLI subagents are an authorized orchestration
surface by default. The root may choose whether, when, and how many CLI
subagents to use for scoped inspection, implementation support, or review,
while staying inside the owner request, source graph, worker rules, and runtime
limits. If the owner says `root only`, `no delegation`, `no subagents`, or
equivalent, do not create CLI subagents. The owner may also limit CLI
subagents for the current session.

Visible Codex App worker threads are not authorized by default. Before creating
visible App worker threads, ask once for session-scoped consent with a bounded
maximum. CLI subagents are authorized by invoking `$codex-orchestrator` unless
the owner disables delegation.

Before delegation, load `references/worker.md`. It owns the exact startup
prompt, visible-thread wording, execution report, worker lifecycle, resync,
integration, artifacts, recurring PRD automation, and closeout details.

The entrypoint contract is:

- Worker authorization is resolved only by the root orchestrator per workstream
  and session.
- Visible-thread consent is current-session consent, not durable config or
  PRD/issue metadata.
- In owner worker-surface wording, `thread` means a visible Codex App thread.
  Do not silently downgrade requested App threads to CLI subagents.
- Do not copy session worker choices into PRDs, generated issue bodies, draft
  publish commands, project memory, or `## Orchestrator Handoff`.
- Automations are explicit-only and runtime-tool-dependent; unavailable
  automation tooling means draft instructions, not scheduled work.
- Split workers by independent ownership boundary, keep shared or overlapping
  integration work in the root, and build the non-blocking execution report from
  `references/worker.md` before dispatch.

## Delivery And Scheduling

For implementation or publication workstreams, resolve delivery mode from the
source item, linked `Source PRD`, or owner request, then record it in the
ledger. For generated issues, the PRD owns feature-level delivery details; the
issue body owns issue-level parallelization, dependencies, blocks, closeout,
and overrides.

Before scheduling or publishing PRD-backed work, load
`references/prd-backed-delivery.md`. That reference owns delivery authority,
publication authority, issue mutation authority, draft PRD handling,
PRD-backed publication, Codex PR review, issue-level scheduling values, ad hoc
publication limits, and closeout rules.

If dependency refs, `Source PRD`, closeout path, delivery mode, or
parallelization are missing, malformed, cyclical, contradictory, or unsafe, or
if a generated issue's `## Orchestrator Handoff` is missing or contradicts the
issue body, classify the workstream as `needs-owner` or `blocked` instead of
inventing semantics. Workers may not invent branch or PR strategy.

## Companion Skill Routing

Use the smallest standalone companion skill for each Git or GitHub workstream:

| Workstream | Companion skill |
| --- | --- |
| Read-only scans across multiple explicit repositories | `$github-portfolio-triage` |
| Current-repository issue, PR, label, milestone, or queue triage | `$github-triage` |
| GitHub issue creation, comments, labels, issue types, closure, or parent/sub-issue relationships | `$github-issues` |
| Evidence-first issue, PR, bug, root-cause, or fix-quality review | `$github-deep-review` |
| GitHub Actions runs, pending checks, or failing PR logs | `$github-ci` |
| PR review threads, Codex review requests, comment context, or selected replies | `$github-review-threads` |
| Release readiness, tags, GitHub Releases, notes, assets, or package availability | `$github-releases` |
| Local staging, commit authoring, and push-only flows | `$git-commit` |
| Full local checkout publish flow to branch plus draft PR | `$yeet` |

## Workflow

1. Resolve the portfolio ledger with `references/ledger.md`, canonicalize
   target repo realpaths when local paths are available, and verify or record
   the active-root claim before creating workers, starting implementation, or
   mutating source state. If another live root claims an overlapping repo or
   source id, stop as `needs-owner` and offer resume, wait, handoff, or
   explicit takeover. After the active-root scope is known, establish the Goal
   Mode And Stop Contract above or record its ledger fallback before worker
   dispatch or root-owned implementation.
2. Snapshot and register task sources: repos, source ids/refs, closeout targets,
   mutation authority, owner constraints, delivery or `Source PRD` inheritance,
   scheduling constraints, gate overrides, suppressed items, and, for generated
   issues, the `## Orchestrator Handoff` projection.
3. Route sources with the table above and pick the smallest companion skill.
   Broad discovery uses `$github-portfolio-triage`; focused GitHub work uses the
   specific current-repo companion. Decompose durable generated issues,
   checklists, and plans into workstreams before scanning for extra queue
   signals.
4. Classify every workstream with the `references/ledger.md` vocabulary. Each
   item needs source id, acceptance criteria, scheduling constraints,
   dependencies, selected gates, proof target, and closeout target.
5. Resolve session worker settings from the owner request and this skill's
   delegation policy, then read `references/worker.md` before delegation.
   Prepare the implementation plan and first wave, build the execution report,
   and keep it visible before dispatching the source batch. Create workers
   according to the orchestrator's chosen split for the current wave, name
   visible App threads immediately, and give each
   worker explicit scope, per-workstream authorization modes,
   delivery/publication authority, dependency state, gates, proof,
   branch/integration expectations, and final report shape. Continue into newly
   unblocked waves while the recorded boundaries, CLI subagent default or
   disabled-delegation choice, and visible-thread consent limits still hold.
   Stop for owner input only when the run needs visible worker-thread consent or
   higher visible-thread limits, a changed delivery/authorization boundary, risk
   acceptance, credentials, or another explicit stop condition.
6. Monitor from the ledger state. Read the ledger before each owner-facing
   progress update and report the current wave, active workstreams, blockers,
   proof changes, and next scan/check from the ledger. Read a worker before
   steering, renaming, archiving, interrupting, replacing, closing, reusing, or
   integrating it. Record status, blockers, validation, risks, resync state,
   integration method, artifacts, lifecycle decision, and next action in the
   ledger.
7. Keep root ownership over orchestration, integration, gates, publication, and
   source closeout. Apply `references/gates.md` before owner-ready, issue-closed,
   merge-ready, release-ready, or final status. For non-trivial edits, require
   focused tests and `$autoreview`; rerun both after review-triggered changes.
   For `pull-request` delivery with merge-ready closeout authority, the root may
   not declare merge-ready until the PR is out of draft, a Codex GitHub review
   was requested with `@codex review`, a completed Codex GitHub review exists
   for the latest PR state, and actionable feedback has been resolved or
   explicitly dispositioned under the `codex-pr-review` gate. If only draft PR
   publication is authorized, record the draft PR state and stop short of
   merge-ready.
8. Mutate source state and target-repo `AGENTS.md` only when authorized. For
   target-repo instructions, apply the `Target Repo Instructions` rules above.
   For source items published by
   `$plan-feature`, treat the published PRD and generated issues as planning
   inputs; after workstream registration, lifecycle comments, labels, direct
   closure, real PR links, Codex PR review evidence, and integration proof are
   orchestrator closeout work.
   Use `$github-issues` for GitHub issue lifecycle work,
   `$github-review-threads` for PR replies, Codex review requests, and
   PR-discussion updates, `$git-commit` for commit/push-only delivery, and
   `$yeet` when draft PR creation or update is part of the resolved path. If
   partial source closeout cannot be applied, keep the
   proposed update owner-ready rather than calling the source complete.
9. Before stopping, execute every authorized `ready-next` action. If anything
   actionable remains, return to source reconciliation and start the next
   bounded wave. Final ledger state must have no `active` worker requiring
   orchestration, no delegable `autonomous` item, no authorized `ready-next`
   action, and no newly surfaced source item.

## Final Report

Before handing control back to the owner, return a compact owner-facing report
that covers status, reconciled source items, worker usage and evidence,
delivery/publication mutations, active-root decisions, gates and proof,
remaining owner decisions, fallback reason for any planned worker surface that
was unavailable or intentionally unused, and the next safe action. Use
`references/worker.md` and `references/ledger.md` for the detailed worker
evidence, execution-mode, lifecycle, and ledger closeout fields.

## References

- `references/ledger.md`: named-ledger resolution, active-root claims, ledger
  template, portfolio overrides, and write ownership.
- `references/worker.md`: worker prompt template, authorization modes, no
  subdelegation rule, and final report format.
- `references/prd-backed-delivery.md`: PRD/generated-issue delivery contracts,
  publication authority, Codex PR review, authorized merge-ready closeout, and
  closeout rules.
- `references/gates.md`: universal gate catalog for owner-ready, merge, release,
  CI, autoreview, and cross-repo integration decisions.

## Boundaries

- V1 does not include 1Password, specialized release executors, ledger-parsing
  scripts, or mandatory live GitHub write tests.
- Portfolio triage is read-only. Follow-up mutations require explicit user
  authorization and the matching standalone Git/GitHub skill.
- Do not depend on repo-local plugin bundles, plugin cache artifacts, or
  removed shared helper runtimes for GitHub work.
- The orchestrator owns ledger updates. Worker threads report facts and
  recommendations; they do not edit portfolio ledgers directly.
