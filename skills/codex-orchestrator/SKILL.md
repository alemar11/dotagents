---
name: codex-orchestrator
description: Coordinate Codex workers, portfolio ledgers, gates, autoreview, Git/GitHub companion skills, and owner-ready closeout.
---

# Codex Orchestrator

## Overview

Use this Codex-dependent skill as the control plane for maintainer work across
one or more repositories. It coordinates named portfolio ledgers, read-only
standalone Git/GitHub companion skills, visible Codex App worker threads,
CLI/subagent worker threads, heartbeat monitoring, gates, `$autoreview`, and
owner-ready status reports.

This skill is not a worker. It delegates scoped work, monitors progress, keeps
the ledger current, and decides when a task is ready for owner review, commit,
PR, release, or another explicit decision. Keep the root orchestrator thread
lightweight: it owns routing, lifecycle, integration, gates, ledger updates,
and final publication, while delegated workers own substantial repository
inspection or implementation whenever delegation is authorized and useful.

## Root Ownership Contract

- The root orchestrator owns routing, ledger updates, worker lifecycle,
  integration choice, gate evaluation, and final closeout decisions.
- Workers own one scoped repository or workstream plus focused validation and a
  clear final report.
- Worker-reported statuses such as `done`, `blocked`, `needs-owner`, or
  `ready-for-review` are inputs to the root thread, not final lifecycle
  decisions.
- If no inspectable worker surface is available, delegation is not explicitly
  authorized, or the work is too small or overlapping, keep the work in the
  root thread.

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
| Generated issue with `Source PRD: draft-prd:<...>` | Register only for dry-run inspection or planning review. Do not dispatch, commit, push, open PRs, close issues, or mutate trackers until the source is a hosted PRD number, local PRD path, or explicit owner decision with separate publication and issue-mutation authority. |
| Durable generated issue, PR, CI failure, bug, local checklist, implementation plan, or explicit implementation request | Register directly as source items and decompose into workstreams. |

For Markdown plans or checklists, enumerate unchecked items with nearest heading
context and a stable path plus line or anchor. Preserve parent context, map each
actionable item to a ledger workstream, and close it by applying/proposing a
file update, moving residual scope to `deferred`, or recording the owner
decision that leaves it open.

## Loop Semantics

Run orchestration as bounded waves, not as a one-pass checklist:

1. Resolve or initialize the ledger.
2. Snapshot authorized task sources and reconcile them with existing ledger
   workstreams by stable source id.
3. Select the next root-owned and delegated wave.
4. Execute, monitor, integrate, and gate the wave.
5. Update the ledger and any authorized source closeout targets.
6. Rescan due sources, then repeat only while there are `active` items,
   actionable `autonomous` candidates, due next checks, authorized `ready-next`
   actions, or newly surfaced source items.

Each wave must produce at least one ledger state transition, new proof, source
update, owner decision brief, or explicit no-progress/blocker record. Do not
loop silently on the same worker status or source snapshot.

## Runtime Surfaces

Required surfaces depend on the resolved workstream:

- Codex App thread tools for visible App workers: create/read/message/rename,
  archive, handoff, fork, and optional list/pin. Logical operations map to
  `codex_app.create_thread`, `codex_app.read_thread`,
  `codex_app.send_message_to_thread`, `codex_app.set_thread_title`,
  `codex_app.set_thread_archived`, `codex_app.handoff_thread`,
  `codex_app.fork_thread`, and optionally `codex_app.list_threads` or
  `codex_app.set_thread_pinned`.
- CLI/subagent worker tools for inspectable CLI workers: spawn, wait, send, and
  close through `multi_agent_v1.spawn_agent`, `multi_agent_v1.wait_agent`,
  `multi_agent_v1.send_input`, `multi_agent_v1.close_agent`, or the CLI
  `/agent` equivalent.
- Codex heartbeat or automation support only when the owner selects periodic
  monitoring.
- `$autoreview`, standalone Git/GitHub companions, `$plan-feature`, and ledger
  storage at `~/.cache/dotagents/skills/codex-orchestrator/ledgers/`.

If a required Codex tool is not visible, search the tool registry by operation
name before treating it as unavailable. Record the actual callable tool name
when it differs from the logical name. If a tool or companion skill remains
unavailable, continue only with safe work and report the exact missing surface.

## Delegation Policy

Before creating workers, resolve and record the owner-authorized worker and
monitoring policy in the ledger. If a broad, worker-oriented, or parallelizable
request omits surface, limits, or monitoring, ask once:

> How should I run orchestration for this session: `cli-subagent`,
> `codex-app-thread`, `auto`, or `none`? What max active count should I use
> for each allowed worker surface? Should I monitor progress manually, or create
> a heartbeat? Default heartbeat is `every-5-minutes`, and you can change it.

While waiting, do only root-owned discovery or planning that does not create
workers, create visible App threads, mutate source state, or assume a quota.

Use `references/worker.md` for worker surfaces, caps, authorization modes,
prompt shape, lifecycle, resync, integration, artifacts, and closeout. Keep
these entrypoint rules in force:

- `auto` permits choosing among owner-authorized surfaces; it is not a quota.
- Visible Codex App threads require explicit owner intent for visible, new,
  separate, or background workers.
- CLI/subagent workers are valid for owner-authorized, inspectable bounded work
  when visible App threads were not requested.
- Split workers by independent ownership boundary: repository, package,
  service, path set, or tightly scoped workstream.
- Keep small, overlapping, shared-contract, dependency/config, migration,
  generated-snapshot, broad-test, conflict-resolution, and final integration
  work in the root thread.
- Before sending overlapping new scope to an existing worker, resync or replace
  the worker.

## Delivery And Scheduling

For implementation or publication workstreams, resolve delivery mode from the
source item, linked `Source PRD`, or owner request, then record it in the
ledger. For generated issues, the PRD owns feature-level delivery details; the
issue body owns issue-level parallelization, dependencies, blocks, closeout,
and overrides.

Before scheduling or publishing PRD-backed work, load
`references/prd-backed-delivery.md`. That reference owns delivery authority,
publication authority, issue mutation authority, draft PRD handling,
PRD-backed publication, ad hoc publication limits, and closeout rules.

Use issue-level scheduling fields as the wave graph:

| Field | Start rule |
| --- | --- |
| `independent` | May start when authorization, ownership boundaries, and gates allow it. |
| `depends-on <issue>` | Queue-ready is not start-ready; wait for root-verifiable dependency proof. |
| `blocks <issue>` | May start when otherwise eligible; dependent work remains unassigned. |
| `root-integrated` | Keep implementation in root; workers may inspect or prove only if integration stays root-owned. |

If dependency refs, `Source PRD`, closeout path, delivery mode, or
parallelization are missing, malformed, cyclical, contradictory, or unsafe,
classify the workstream as `needs-owner` or `blocked` instead of inventing
semantics. Workers may not invent branch or PR strategy.

## Companion Skill Routing

Use the smallest standalone companion skill for each Git or GitHub workstream:

| Workstream | Companion skill |
| --- | --- |
| Read-only scans across multiple explicit repositories | `$github-portfolio-triage` |
| Current-repository issue, PR, label, milestone, or queue triage | `$github-triage` |
| GitHub issue creation, comments, labels, issue types, closure, or parent/sub-issue relationships | `$github-issues` |
| Evidence-first issue, PR, bug, root-cause, or fix-quality review | `$github-deep-review` |
| GitHub Actions runs, pending checks, or failing PR logs | `$github-ci` |
| PR review threads, comment context, or selected replies | `$github-review-threads` |
| Release readiness, tags, GitHub Releases, notes, assets, or package availability | `$github-releases` |
| Local staging, commit authoring, and push-only flows | `$git-commit` |
| Full local checkout publish flow to branch plus draft PR | `$yeet` |

## Workflow

1. Resolve the portfolio ledger with `references/ledger.md`.
2. Snapshot and register task sources: repos, source ids/refs, closeout targets,
   mutation authority, owner constraints, delivery or `Source PRD` inheritance,
   scheduling constraints, gate overrides, and suppressed items.
3. Route sources with the table above and pick the smallest companion skill.
   Broad discovery uses `$github-portfolio-triage`; focused GitHub work uses the
   specific current-repo companion. Decompose durable generated issues,
   checklists, and plans into workstreams before scanning for extra queue
   signals.
4. Classify every workstream with the `references/ledger.md` vocabulary. Each
   item needs source id, acceptance criteria, scheduling constraints,
   dependencies, selected gates, proof target, and closeout target.
5. Resolve the worker and monitoring policy, then read `references/worker.md`
   before delegation. Create at most one worker per independent ownership
   boundary in the current wave, name visible App threads immediately, and give
   each worker explicit scope, authorization modes, delivery/publication
   authority, dependency state, gates, proof, branch/integration expectations,
   and final report shape.
6. Monitor using the recorded policy. Read a worker before steering, renaming,
   archiving, interrupting, replacing, closing, reusing, or integrating it.
   Record status, blockers, validation, risks, resync state, integration method,
   artifacts, lifecycle decision, and next action in the ledger.
7. Keep root ownership over orchestration, integration, gates, publication, and
   source closeout. Apply `references/gates.md` before owner-ready, issue-closed,
   merge-ready, release-ready, or final status. For non-trivial edits, require
   focused tests and `$autoreview`; rerun both after review-triggered changes.
8. Mutate source state only when authorized. Use `$github-issues` for GitHub
   issue lifecycle work, `$github-review-threads` for PR replies,
   `$git-commit` for commit/push-only delivery, and `$yeet` when draft PR
   creation or update is part of the resolved path. If partial source closeout
   cannot be applied, keep the proposed update owner-ready rather than calling
   the source complete.
9. Before stopping, execute every authorized `ready-next` action. If anything
   actionable remains, return to source reconciliation and start the next
   bounded wave. Final ledger state must have no `active` worker requiring
   orchestration, no delegable `autonomous` item, no authorized `ready-next`
   action, and no newly surfaced source item.

## Final Report

Before handing control back to the owner, return a compact owner-facing report:

- overall status: `completed`, `needs-owner`, `blocked`, `deferred`,
  `released`, or mixed with the blocking reason;
- source items reconciled, with source ids/refs and closeout state;
- workers used, integration method per worker, and any worker output left
  unintegrated;
- commits, branches, PRs, issue updates, releases, or draft mutation commands
  produced under current authorization;
- gates and proof: tests, CI, autoreview, live proof, cross-repo proof, or why
  a proof path was unavailable;
- remaining owner decisions, blocked access, deferred follow-ups, and the next
  safe action.

## References

- `references/ledger.md`: named-ledger resolution, ledger template, portfolio
  overrides, and write ownership.
- `references/worker.md`: worker prompt template, authorization modes, no
  subdelegation rule, and final report format.
- `references/prd-backed-delivery.md`: PRD/generated-issue delivery contracts,
  publication authority, and closeout rules.
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
