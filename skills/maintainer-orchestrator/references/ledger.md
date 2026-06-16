# Ledger Reference

Use ledgers to persist portfolio scope, active workstreams, gate overrides, and
orchestration state between Codex sessions.

## Resolution

1. An explicit user-provided ledger path wins.
2. A named portfolio uses:
   `~/.cache/dotagents/skills/maintainer-orchestrator/ledgers/<portfolio>.md`
3. If no portfolio is named, use:
   `~/.cache/dotagents/skills/maintainer-orchestrator/ledgers/default.md`

Create the parent directory if needed:

```bash
mkdir -p ~/.cache/dotagents/skills/maintainer-orchestrator/ledgers
```

Portfolio names should be lowercase, filesystem-safe slugs. If the user gives a
display name, derive a slug and record the display name in the ledger.

## Ownership

- The orchestrator reads and writes the ledger.
- Worker threads do not edit ledgers.
- Workers report status, proof, blockers, and next actions to the orchestrator.
- Preserve historical notes that explain owner decisions, suppressions, and
  release state.
- The orchestrator records worker lifecycle decisions: integrated,
  retained-for-inspection, abandoned, or handoff-pending.

## Template

```md
# <Portfolio Name> Maintainer Ledger

Last updated: <YYYY-MM-DD HH:MM TZ>
Owner: <person or team>
Status: active|paused|blocked|complete|released|archived

## Scope

Repositories:
- owner/app: <local path or URL>; role=<frontend|backend|library|docs|other>
- owner/backend: <local path or URL>; role=<api|service|worker|other>

Out of scope:
- <repos, branches, issues, or workflows intentionally ignored>

## Worker Policy

Default authorization: inspect|implement
Worker surface: codex-app-thread|cli-subagent|no-delegation
Allowed worker count: <number>
Heartbeat: disabled|every 5 minutes|custom
No subdelegation: true
Workers edit ledger: false
Root owns worker lifecycle: true
Visible worker title format: <Project>: <short current task>

## Gate Policy

Required gates:
- authorization
- live-proof
- autoreview
- ci
- owner-decision
- release
- public-model-identifier
- cross-repo-integration

Portfolio overrides:
- <gate>: <stricter requirement or owner-approved exception>

## Workstreams

### Active

| ID | Repo | Surface | Worker ID | Title | Objective | Status | Next Check |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A-001 | owner/repo | codex-app-thread | <thread id or link> | <Project>: <short task> | <objective> | active | <time> |

### Autonomous

- <candidate item, repo, URL, reason it is safe to delegate>

### Needs Owner

- <decision, URL/context, options, recommendation>

### Ready Next

- <owner-ready task, proof, required next action>

### Blocked

- <blocker, owner/action needed, evidence>

### Ignored Or Suppressed

- <item, reason, date, owner>

### Deferred

- <follow-up issue/ticket or proposed issue body, residual scope, blocker,
  source item, owner/action needed>

### Completed

- <issue/PR/work item, commit/PR/proof, validation, whether the source issue
  was closed>
- <worker id/title, integration method, worker lifecycle decision, generated
  ignored artifacts removed/retained/left in disposable worktree>

### Released

- <repo/version/tag/date/proof>

## Notes

- <dated orchestration notes and durable context>
```

## Multi-Portfolio Use

Use one ledger per portfolio. For example:

- `~/.cache/dotagents/skills/maintainer-orchestrator/ledgers/default.md`
- `~/.cache/dotagents/skills/maintainer-orchestrator/ledgers/mobile-stack.md`
- `~/.cache/dotagents/skills/maintainer-orchestrator/ledgers/app-backend.md`

Do not mix unrelated portfolios in one ledger unless the user explicitly wants a
single combined operating view.

## Vocabulary

- `Active`: work that currently needs orchestration, worker monitoring,
  integration, owner input, or a scheduled next check. Remove a worker row from
  `Active` once its output is integrated, abandoned, retained only for
  inspection, or handed off with the remaining action recorded elsewhere. A
  completed row may remain in `Active` only while a root-owned closeout action
  is still pending, and the `Next Check` must name that action.
- `Ready Next`: owner-ready work that still needs an explicit next action such
  as review, commit, push, PR, merge, close, or release.
- `Completed`: implemented work whose required gates passed. Record commits,
  PRs, validation, proof, source issue closure, integration method, worker
  lifecycle decision, and any generated ignored artifacts that were removed or
  intentionally retained.
- `Deferred`: known residual work that is intentionally not part of the current
  closeout. Link the follow-up issue/ticket when one exists, or record the
  proposed follow-up when mutation is not authorized. Do not mirror completed
  source items here; use `Deferred` only for real residual scope, blocked live
  proof, or owner-visible follow-up work.
- `Released`: use only for actual product/package/version releases, deploys, or
  tags. Do not put ordinary issue-closing commits here unless a release really
  happened.

## Closeout Hygiene

Before marking a ledger `complete`, verify:

- `Active` contains no worker that is merely done; every active row needs a real
  next check or root-owned closeout action.
- `Deferred` contains only residual work with a linked or proposed
  owner-visible follow-up.
- `Completed` records the final proof, issue/PR closure state, integration
  method, and worker lifecycle decision for each completed worker-backed item.
- Generated ignored artifacts and helper worktrees are either removed, retained
  for inspection with a reason, left only inside disposable worker state, or
  explicitly handed off.
