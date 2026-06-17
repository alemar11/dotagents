---
name: codex-orchestrator
description: Use when coordinating visible Codex App worker threads, CLI/subagent worker threads, portfolio triage, gates, ledgers, root-owned worker lifecycle, autoreview, standalone Git/GitHub companion skills, or owner-ready Codex closeout.
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

## Workstream Sources

A workstream is the orchestration unit. It may come from a user-provided plan,
GitHub issue, PR review, CI failure, release checklist, local TODO, audit
result, ledger item, or ad hoc owner request. GitHub issues and PRs are trigger
sources, not the only planning model.

## Runtime Requirements

- Codex App thread tools when visible App workers are requested and available:
  `codex_app.create_thread`, `codex_app.read_thread`,
  `codex_app.send_message_to_thread`, `codex_app.set_thread_title`,
  `codex_app.set_thread_archived`, `codex_app.handoff_thread`,
  `codex_app.fork_thread`, and optionally `codex_app.list_threads` or
  `codex_app.set_thread_pinned`.
- CLI/subagent worker tools when that is the active inspectable surface:
  `multi_agent_v1.spawn_agent`, `multi_agent_v1.wait_agent`,
  `multi_agent_v1.send_input`, `multi_agent_v1.close_agent`, or the CLI
  `/agent` equivalent.
- Codex heartbeat or automation support when the user asks for periodic worker
  monitoring.
- The reusable `$autoreview` skill for closeout review after non-trivial code
  edits and after review-triggered fixes.
- Standalone Git/GitHub companion skills as needed: `$github`,
  `$github-portfolio-triage`, `$github-triage`, `$github-ci`,
  `$github-reviews`, `$github-releases`, `$git-commit`, and `$yeet`.
- Local ledger storage at
  `~/.cache/dotagents/skills/codex-orchestrator/ledgers/`.

If a required Codex tool or companion skill is unavailable, continue only with
the parts that can be done safely and report the exact missing surface.

## Worker Surface Selection

Ask for or infer owner authorization before delegation. If the owner requests
workers, parallelism, background work, heartbeat monitoring, or broad
orchestration, delegation is authorized for the scoped workstreams. If the
request is a small single-thread task or worker visibility is ambiguous, keep
the work in the root thread unless parallel work materially improves progress.

Visible Codex App thread creation requires explicit owner intent for visible,
new, separate, or background threads. Do not create user-owned App threads
merely because a subtask exists.

Choose the worker surface deliberately:

- In Codex App, prefer visible Codex App worker threads for substantial
  delegated work only when the owner explicitly asks for visible, new,
  separate, or background worker threads, or otherwise explicitly indicates
  they expect to see, inspect, rename, hand off, archive, or continue workers
  from the sidebar.
- In Codex CLI, prefer CLI/subagent workers for bounded parallel work because
  they are inspectable through `/agent`.
- If only one surface is exposed, use that surface only when it can satisfy the
  authorization, scope, and inspection requirements. Otherwise do not delegate.

Record the chosen surface, worker id, title or nickname, repository, scope, and
authorization mode in the ledger. Do not call a hidden subagent a visible
thread.

## Delegation Fast Rules

- Use visible Codex App threads only when the owner explicitly asked for
  visible, new, separate, or background workers.
- Use CLI/subagent workers for inspectable bounded parallel work when visible
  App threads were not requested.
- Keep small single-thread tasks, overlapping file work, and last-mile
  integration in the root thread unless there is a strong reason to delegate.
- Before sending overlapping new scope into an existing worker, resync or
  replace that worker instead of assuming its checkout is still current.

## Companion Skill Routing

Use the smallest standalone companion skill for each Git or GitHub workstream:

| Workstream | Companion skill |
| --- | --- |
| GitHub setup, authentication, ambiguous GitHub work, or PR lifecycle after a branch is pushed | `$github` |
| Read-only scans across multiple explicit repositories | `$github-portfolio-triage` |
| Current-repository issue, PR, label, milestone, or queue triage | `$github-triage` |
| GitHub Actions runs, pending checks, or failing PR logs | `$github-ci` |
| PR review threads, comment context, or selected replies | `$github-reviews` |
| Release readiness, tags, GitHub Releases, notes, assets, or package availability | `$github-releases` |
| Local staging, commit authoring, and push-only flows | `$git-commit` |
| Full local checkout publish flow to branch plus draft PR | `$yeet` |

## Workflow

1. Resolve the portfolio ledger with `references/ledger.md`.
2. Identify the repository set, current goals, suppressed items, owner
   constraints, and portfolio-specific gate overrides.
3. Select Git/GitHub companion skills from the routing table. If discovery is
   needed, use `$github-portfolio-triage` for broad or multi-repo queue scans;
   use focused current-repo companions such as `$github-triage`, `$github-ci`,
   or `$github-reviews` only when the task is focused on one repo or PR. If the
   user provided a plan, decompose that plan into workstreams before scanning
   for additional queue signals. For broad maintainer discovery, include open
   issues, open PRs, failing or pending CI, latest release or package state when
   relevant, unreleased changelog/TODO signals, and owner-suppressed items.
4. Classify work with the vocabulary in `references/ledger.md`: `Active`,
   `Autonomous`, `Needs owner`, `Ready next`, `Blocked`, `Deferred`,
   `Completed`, `Ignored`, or `Released`.
5. Before delegation, read `references/worker.md` and create one Codex worker
   per repository or tightly scoped workstream using the selected worker
   surface. Use visible Codex App threads in App-oriented workflows only when
   explicit owner intent for visible/new/separate/background workers is present;
   otherwise use CLI/subagent workers when authorized and inspectable, or stay
   in the root thread.
6. Give each worker an explicit authorization mode, scope, gates, expected
   proof, and final report shape. Workers must not spawn sub-workers, create
   threads, manage other chats, or edit the ledger.
7. For visible Codex App workers, immediately rename each worker thread to
   `<Project>: <short current task>` and update the title when the material
   assignment changes. Keep titles short enough to scan in the sidebar.
8. Keep the root thread focused on orchestration. Delegate heavy repo-local
   implementation to workers when delegation is authorized; perform root-side
   integration only when it is cross-cutting, blocked on worker outputs, or
   necessary to satisfy final gates.
9. Use heartbeat monitoring only when periodic follow-up is requested. Before
   steering, renaming, archiving, interrupting, replacing, or closing a worker,
   read the worker's latest state. Capture status, blockers, validation, risks,
   and next actions in the ledger.
10. Before reusing a worker for a new wave, changing overlapping scope, or
    integrating worker output, apply the lifecycle guidance in
    `references/worker.md`: resync against root-integrated work, choose a
    root-owned integration method, record generated ignored artifacts, and make
    an explicit worker closeout decision.
11. Before marking owner-ready, issue-closed, merge-ready, release-ready, or
    final, apply `references/gates.md`. Treat blocked live proof, deferred
    acceptance criteria, and worker-reported risks as gate inputs, not as notes
    to bury after closure.
12. For non-trivial code edits, require focused tests and `$autoreview`; rerun
   both after any review-triggered code change.
13. Before closing a GitHub issue or PR thread that is only partially satisfied,
    create or link an owner-visible follow-up issue for the deferred work when
    GitHub mutation is authorized. If mutation is not authorized, keep the item
    owner-ready with the proposed follow-up body and do not call it complete.
14. Stop when the ledger shows no active worker requiring orchestration and all
    surfaced work is either completed with gates satisfied, owner-ready, blocked
    with a decision brief, released, or intentionally deferred with a linked or
    proposed follow-up. Completed workers should be moved out of active tracking
    or explicitly marked as awaiting a root-owned closeout action.

## References

- `references/ledger.md`: named-ledger resolution, ledger template, portfolio
  overrides, and write ownership.
- `references/worker.md`: worker prompt template, authorization modes, no
  subdelegation rule, and final report format.
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
