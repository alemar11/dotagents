---
name: maintainer-orchestrator
description: Use when coordinating Codex worker threads across one or more repositories, portfolio triage, gates, ledgers, autoreview, GitStack workflows, or owner-ready maintainer closeout.
---

# Maintainer Orchestrator

## Overview

Use this Codex-dependent skill as the control plane for maintainer work across
one or more repositories. It coordinates named portfolio ledgers, read-only
GitStack portfolio triage, Codex worker threads, heartbeat monitoring, gates,
`$autoreview`, and owner-ready status reports.

This skill is not a worker. It delegates scoped work, monitors progress, keeps
the ledger current, and decides when a task is ready for owner review, commit,
PR, release, or another explicit decision.

## Runtime Requirements

- Codex thread tools for worker creation, inspection, messaging, handoff, title
  updates, pin/archive state, or equivalent thread management.
- Codex heartbeat or automation support when the user asks for periodic worker
  monitoring.
- The reusable `$autoreview` skill for closeout review after non-trivial code
  edits and after review-triggered fixes.
- The GitStack plugin for `github-portfolio-triage`, current-repo triage, CI,
  reviews, releases, commit, and publish workflows.
- Local ledger storage at
  `~/.cache/dotagents/skills/maintainer-orchestrator/ledgers/`.

If a required Codex tool or companion skill is unavailable, continue only with
the parts that can be done safely and report the exact missing surface.

## Workflow

1. Resolve the portfolio ledger with `references/ledger.md`.
2. Identify the repository set, current goals, suppressed items, owner
   constraints, and portfolio-specific gate overrides.
3. Run GitStack `github-portfolio-triage` for broad or multi-repo queue scans.
   Use current-repo GitStack skills only when the task is focused on one repo.
4. Classify work as `Active`, `Autonomous`, `Needs owner`, `Ready next`,
   `Blocked`, `Ignored`, or `Released` in the ledger.
5. Before delegation, read `references/worker.md` and create one Codex worker
   thread per repository or tightly scoped workstream.
6. Give each worker an explicit authorization mode, scope, gates, expected
   proof, and final report shape. Workers must not spawn sub-workers or edit
   the ledger.
7. Use heartbeat monitoring only when periodic follow-up is requested. Capture
   status, blockers, and next actions in the ledger.
8. Before marking owner-ready, merge-ready, release-ready, or final, apply
   `references/gates.md`.
9. For non-trivial code edits, require focused tests and `$autoreview`; rerun
   both after any review-triggered code change.
10. Stop when the ledger shows no active worker requiring orchestration and all
    surfaced work is either owner-ready, blocked with a decision brief,
    released, or intentionally deferred.

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
  authorization and the matching GitStack skill.
- The orchestrator owns ledger updates. Worker threads report facts and
  recommendations; they do not edit portfolio ledgers directly.
