# Ledger Reference

Use ledgers to persist portfolio scope, active workstreams, gate overrides, and
orchestration state between Codex sessions.

## Resolution

1. An explicit user-provided ledger path wins.
2. A named portfolio uses:
   `~/.cache/dotagents/skills/codex-orchestrator/ledgers/<portfolio>.md`
3. If no portfolio is named, use:
   `~/.cache/dotagents/skills/codex-orchestrator/ledgers/default.md`

Create the parent directory if needed:

```bash
mkdir -p ~/.cache/dotagents/skills/codex-orchestrator/ledgers
```

Portfolio names should be lowercase, filesystem-safe slugs. If the user gives a
display name, derive a slug and record the display name in the ledger.

If the resolved ledger file does not exist, create it from the template before
discovery. Fill known fields, use `TBD` for unknown owner or repository
metadata, set `Status: active`, and add a dated note summarizing the owner
request and initial task sources.

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

## Discovery Sources

| Source ID | Kind | Path/Query/URL | Last Checked | Cursor/Fingerprint | Item Key Rule | Mutation Authority | Suppression Rule |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DS-001 | markdown, github-issue, github-pr, ci, todo, ledger | <path/query/url> | <time> | <etag/sha/cursor/checksum> | <stable id rule> | none, propose, or write | <owner/date/reason/source fingerprint> |

## Worker Policy

Default authorization: inspect|implement
Delegated worker surface: auto|codex-app-thread|cli-subagent|none
Max active delegated workers: <number>
Heartbeat: disabled|every 5 minutes|custom
No subdelegation: true
Workers edit ledger: false
Root owns worker lifecycle: true
Visible worker title format: <Project>: <short current task>

`Delegated worker surface` is the owner-authorized delegation policy. `auto`
means choose per workstream from available and owner-authorized delegated
surfaces: in Codex CLI this resolves to `cli-subagent`, while in Codex App it
may choose `codex-app-thread` or `cli-subagent`. `none` disables delegation.
`Max active delegated workers` is a cap, not a quota.

Each workstream records the actual surface used: `codex-app-thread`,
`cli-subagent`, or `no-delegation`. For root-owned work, record
`Surface=no-delegation`, `Worker ID=root`, and the reason delegation was skipped.

## Delivery Topology Policy

Default topology:
- **One Feature Branch** for a single git repo, including monorepos.
- **One PR Per Repo** for true multi-repo features.

Exceptions:
- **One PR Per Issue** only when the issue is isolated from shared contracts,
  migrations, lockfiles, generated files, broad validation, and other active
  issue work.
- **Direct Commit** only with explicit owner authorization.

Each implementation workstream records either the explicit topology or the
`Source PRD` it inherits from, plus issue-level parallelization, dependencies,
closeout target, branch or PR expectation, and integration proof target. Record
integration mode only when it is not obvious from the inherited topology or when
the issue declares an override. Workers may not choose a different branch or PR
strategy without a root-owned ledger update and authorization check.

## Gate Policy

Available gates:
- authorization
- closure
- follow-up
- live-proof
- autoreview
- ci
- owner-decision
- risk-follow-up
- release
- public-model-identifier
- cross-repo-integration
- credential-and-access

Portfolio overrides:
- <gate>: <stricter requirement or owner-approved exception>

Gate matrix:
| Source ID | Workstream ID | Gate | Required When | Status | Evidence | Waiver/Owner | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <source id> | <workstream id> | <gate> | <condition> | pass, fail, blocked, or not-applicable | <root-verifiable proof> | <owner/date or none> | <next action> |

## Workstreams

### Active

| ID | Source ID | Source Ref | Repo | Surface | Worker ID | Wave | Title | Objective | Delivery | Acceptance Criteria | Status | Last Read | Root Baseline | Resync State | Next Check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-001 | github-issue:owner/repo#123 | <url/path:line> | owner/repo | codex-app-thread | <thread id or root> | 1 | <Project>: <short task> | <objective> | <Source PRD or topology; parallelization; branch/PR expectation; closeout> | <source acceptance criteria> | active | <time> | <commit/ledger wave> | synced, needs-resync, replaced, or root-owned | <time/action> |

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

- <source id/ref, delivery topology, branch/PR/proof, validation, source closeout target and
  whether it was updated/closed>
- <worker id/title, integration method, worker lifecycle decision, generated
  ignored artifacts removed/retained/left in helper worktree>

### Released

- <repo/version/tag/date/proof>

## Wave Checkpoints

| Wave | Started | Finished | Sources Scanned | Items Processed | Remaining Actionable | Blockers | Ledger Mutations | Source Mutations | Next Scan/Check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | <time> | <time> | <source ids> | <count> | <count> | <summary> | <status changes> | <file/github updates or proposed updates> | <time/action> |

## Notes

- <dated orchestration notes and durable context>
```

## Multi-Portfolio Use

Use one ledger per portfolio. For example:

- `~/.cache/dotagents/skills/codex-orchestrator/ledgers/default.md`
- `~/.cache/dotagents/skills/codex-orchestrator/ledgers/mobile-stack.md`
- `~/.cache/dotagents/skills/codex-orchestrator/ledgers/app-backend.md`

Do not mix unrelated portfolios in one ledger unless the user explicitly wants a
single combined operating view.

## Vocabulary

- `Active`: work that currently needs orchestration, worker monitoring,
  integration, owner input, or a scheduled next check. Remove a worker row from
  `Active` once its output is integrated, abandoned, retained only for
  inspection, or handed off with the remaining action recorded elsewhere. A
  completed row may remain in `Active` only while a root-owned closeout action
  is still pending, and the `Next Check` must name that action.
- `Autonomous`: candidate work safe to delegate under the current worker policy.
  Move it to `Active` when assigned, or reclassify it when delegation is no
  longer useful or authorized. A ledger cannot be `complete` while actionable
  `Autonomous` work remains.
- `Needs Owner`: progress waits on owner decision, credentials, scope approval,
  risk acceptance, mutation authorization, or another non-Codex decision. Record
  the decision brief, options, recommendation, and minimum owner action.
- `Ready Next`: owner-ready work that still needs an explicit next action such
  as review, commit, push, PR, merge, close, or release. Execute it before
  stopping when current authorization permits; otherwise reclassify it as
  `Needs Owner`, `Blocked`, or `Deferred` with the missing decision or access.
- `Blocked`: work cannot progress with current access, state, dependency, or
  proof. Record blocker, evidence, minimum next action, and whether the blocker
  is owner-actionable or external.
- `Ignored Or Suppressed`: known item intentionally excluded from this loop.
  Record source id, source fingerprint, owner, date, and reason. Do not
  rediscover it unless owner direction changes or the source fingerprint changes.
- `Completed`: implemented work whose required gates passed. Record commits,
  PRs, validation, root-verifiable proof, source closeout state, integration
  method, worker lifecycle decision, and any generated ignored artifacts that
  were removed or intentionally retained.
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

- All discovery sources were rescanned or intentionally skipped with a recorded
  reason, cursor, and fingerprint.
- `Active` contains no worker that is merely done; every active row needs a real
  next check or root-owned closeout action.
- `Autonomous` is empty, or every item was reclassified as non-actionable under
  the current authorization.
- `Ready Next` is empty, or every remaining action was reclassified as `Needs
  Owner`, `Blocked`, or `Deferred` with the missing authorization, decision, or
  follow-up.
- `Needs Owner` and `Blocked` entries are explicitly non-Codex-actionable and
  include decision briefs, blockers, evidence, and minimum next actions.
- `Deferred` contains only residual work with a linked or proposed
  owner-visible follow-up.
- `Completed` records the final proof, source closeout state, integration
  method, and worker lifecycle decision for each completed worker-backed item.
- Generated ignored artifacts and helper worktrees are either removed, retained
  for inspection with a reason, left only inside a helper worktree with an
  explicit lifecycle decision, or explicitly handed off.
- `Ignored Or Suppressed` items have source id, source fingerprint, reason,
  owner, and date, and they are not rediscovered unless that fingerprint or
  owner direction changes.

## Source Reconciliation

At the end of each wave and before final closeout, compare the current source
snapshot against the ledger:

- every open GitHub issue, PR thread, CI failure, Markdown checkbox, local TODO,
  release checklist item, and ledger-only item in scope has a stable source id;
- every source id is mapped to exactly one current ledger status or an explicit
  suppression entry;
- completed source items have root-verifiable proof and a source closeout
  update, such as issue closure, PR reply, resolved thread, green CI URL,
  Markdown checkbox diff, TODO removal/update, commit SHA, release URL,
  screenshot, API response, or timestamped command output;
- partial completions have a linked/proposed follow-up or remain open under
  `Needs Owner`, `Blocked`, or `Deferred`;
- newly surfaced source items are added to `Autonomous`, `Active`, `Needs
  Owner`, `Blocked`, `Deferred`, or `Ignored Or Suppressed` before stopping.
