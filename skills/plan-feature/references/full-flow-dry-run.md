# Full-Flow Dry-Run Fixture

Use this fixture to forward-test the planning pipeline without writing local
artifacts or mutating a hosted tracker.

## User Request

```text
Use $plan-feature to plan a feature named "account settings export". This is a
dry run: do not write files and do not mutate GitHub. Return draft publish
commands instead.
```

## Setup Snapshot

```text
tracker_backend: github
effective_target: draft-publish-commands
no_mutation_override: dry-run
feature_slug: account-settings-export
delivery_mode: pull-request
pr_closeout: merge-ready
source_prd_ref: draft-prd:account-settings-export
prd_body_fingerprint: sha256:7f4a9c21d003
capture_mode: defer-to-caller
domain_knowledge_delta:
  status: required
  decisions:
    - Account settings export is a user-owned portable archive.
  target_surfaces:
    - current-repository/CONTEXT.md
    - current-repository/project-memory/adr/ADR-account-settings-export.md
  evidence:
    - "Accepted planning decision: account settings export portability."
    - current-repository/src/account-settings/export.ts
  unresolved: []
```

## Expected Pipeline

1. `$plan-feature` reviews project memory and resolves the effective target.
2. `$grill-me-with-context` runs with `capture_mode: defer-to-caller`, resolves
   only blockers that affect the PRD or issue split, performs no documentation
   writes, and returns a structured `domain_knowledge_delta`.
3. The PRD phase returns the PRD body, a draft PRD publish command,
   `source_prd_ref=draft-prd:account-settings-export`, and
   `prd_body_fingerprint=sha256:7f4a9c21d003`. When the delta is required, the
   PRD body carries it under `## Domain Knowledge Handoff`.
4. The issue phase returns hardened issue bodies plus draft issue publish commands.
   Draft issue bodies may contain `Source PRD: draft-prd:account-settings-export`
   only because no hosted PRD number exists yet. A required knowledge delta is
   assigned to the last integration task, which depends on every terminal
   implementation issue and includes `## Domain Knowledge Closeout`. That task
   requires its later implementor to invoke `$project-memory domain-memory`,
   which runs Project Memory's internal domain-modeling workflow; Plan Feature
   does not run that capture during planning.
   For example, if `02 depends-on 01` while `03` is independent, the
   pre-closeout terminals are `02` and `03`; appended final task `04` depends
   directly on both. Hosted issue numbers are tracked separately and do not
   replace these generated dependency IDs.
5. `$codex-orchestrator` may inspect the resulting issue graph in dry-run mode
   but must not dispatch implementation workers, commit, push, create PRs, or
   close issues from the draft PRD ref.
6. Any `$codex-orchestrator` session settings remain runtime-only; they are not
   copied into the PRD, generated issue bodies, `## Orchestrator Handoff`, or
   draft publish commands.

## Expected Draft Publish Plan

- Publish the PRD first and capture the created issue number as `PRD_NUMBER`.
- Confirm the draft issue commands carry the same PRD body fingerprint as the
  draft PRD command.
- Replace every issue body line
  `Source PRD: draft-prd:account-settings-export` with
  `Source PRD: #$PRD_NUMBER` before creating hosted implementation issues.
- Attach each generated implementation issue to the PRD parent when the tracker
  supports parent/sub-issues.
- Publish the final integration and domain-knowledge closeout task last, after
  all terminal issue IDs are known, and preserve its dependency edges.
- Draft commands may include the intended future `ready-for-agent` labels, but
  the issues are not executable agent-ready output until `Source PRD` is replaced
  with the durable PRD issue number.
- Return exact commands without executing them.

## Failure Conditions

- A repo-local `.scratch/` PRD or issue file is created.
- `CONTEXT.md`, project domain docs, or ADRs are edited during the planning run.
- A GitHub issue is created, edited, labeled, typed, closed, or attached.
- An implementation worker receives `commit`, `push`, or `pr` authorization
  from project memory, plan-feature output, tracker defaults, or the draft PRD
  ref alone.
- Draft PRDs, generated issues, and draft publish commands include worker
  authorization fields or worker capability modes.
- Draft PRDs, generated issues, or draft publish commands include orchestration
  session values such as worker surfaces, worker counts, checkpoint approval,
  publication authority, or issue mutation authority.
- Generated issues use a prose `Source PRD` such as the PRD title when a stable
  draft ref is available.
- A required `domain_knowledge_delta` is omitted, captured during planning, or
  placed in a docs-only task instead of the last integration task.
- The final integration task permits direct edits to `CONTEXT.md`, domain docs,
  or ADRs without invoking `$project-memory domain-memory` and running its
  internal domain-modeling workflow.
