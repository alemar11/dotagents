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

## Template

```md
# <Portfolio Name> Maintainer Ledger

Last updated: <YYYY-MM-DD HH:MM TZ>
Owner: <person or team>
Status: active|paused|blocked|released|archived

## Scope

Repositories:
- owner/app: <local path or URL>; role=<frontend|backend|library|docs|other>
- owner/backend: <local path or URL>; role=<api|service|worker|other>

Out of scope:
- <repos, branches, issues, or workflows intentionally ignored>

## Worker Policy

Default authorization: inspect|implement
Allowed worker count: <number>
Heartbeat: disabled|every 5 minutes|custom
No subdelegation: true
Workers edit ledger: false

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

| ID | Repo | Worker Thread | Objective | Status | Next Check |
| --- | --- | --- | --- | --- | --- |
| A-001 | owner/repo | <thread id or link> | <objective> | active | <time> |

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
