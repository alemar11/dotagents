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
discovery. Fill known fields, use `tbd` for unknown owner or repository
metadata, set `Status: active`, and add a dated note summarizing the owner
request and initial task sources.

## Ownership

- The orchestrator reads and writes the ledger.
- Worker threads do not edit ledgers.
- Workers report status, proof, blockers, and next actions to the orchestrator.
- Preserve historical notes that explain owner decisions, suppressions, and
  release state.
- The orchestrator records worker lifecycle decisions: `integrated`,
  `retained-for-inspection`, `abandoned`, or `handoff-pending`.

## Structured Ledger Values

Use these ledger-owned values:

- `ledger_status`: `active`, `paused`, `blocked`, `complete`, `released`, or
  `archived`; this describes the portfolio ledger as a whole.
- `source_mutation_authority`: `none` means do not mutate the source item,
  `propose` means draft the update without applying it, and `write` means apply
  authorized source updates.
- `resync_state`: `synced` means worker state matches root-integrated work,
  `needs-resync` means worker state must be reconciled, `replaced` means a new
  worker or root flow took over, and `root-owned` means root owns integration or
  follow-up.

Workstream state meanings are defined in `## Vocabulary`. Worker, publication,
and gate values are owned by `worker.md`, `prd-backed-delivery.md`, and
`gates.md`.
Lower-kebab-case values are canonical. Treat older uppercase kebab-case values
as legacy aliases when reading existing artifacts. When updating an artifact
that contains legacy aliases, rewrite touched structured values to
lower-kebab-case.

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
| ds-001 | markdown, github-issue, github-pr, ci, todo, ledger | <path/query/url> | <time> | <etag/sha/cursor/checksum> | <stable id rule> | none, propose, or write | <owner/date/reason/source fingerprint> |

`Mutation Authority` uses the `source_mutation_authority` option values.

## Worker Policy

Default worker authorization: inspect, implement
Assignable authorization modes: inspect|implement|commit|push|pr|ci-rerun-fix|merge-close|release
Delegated worker surface: auto|codex-app-thread|cli-subagent|none
Max active delegated workers: <number>
Heartbeat: disabled|manual|every-5-minutes|custom
No subdelegation: true
Workers edit ledger: false
Root owns worker lifecycle: true
Visible worker title format: <Project>: <short current task>

`Delegated worker surface` is the owner-authorized delegation policy. `auto`
means choose per workstream from available and owner-authorized delegated
surfaces: in Codex CLI this resolves to `cli-subagent`, while in Codex App it
may choose `codex-app-thread` or `cli-subagent`. `none` disables delegation.
`Max active delegated workers` is a cap, not a quota.

Worker authorization modes are capability flags, not a cumulative ladder. List
each allowed action explicitly for each workstream. A
`default_worker_authorization` value from project memory is only a starting
policy default; current owner/session authorization and gates may only narrow
or explicitly extend it.

Each workstream records the actual surface used: `codex-app-thread`,
`cli-subagent`, or `no-delegation`. For root-owned work, record
`Surface=no-delegation`, `Worker ID=root`, and the reason delegation was skipped.

## Delivery Mode Policy

Default delivery mode:
- `one-feature-branch` for a single git repo, including monorepos.
- `one-pr-per-repo` for true multi-repo features.

Exceptions:
- `one-pr-per-issue` only when the issue is isolated from shared contracts,
  migrations, lockfiles, generated files, broad validation, and other active
  issue work.
- `direct-commit` only with explicit owner authorization.

Each implementation workstream records the effective `Delivery mode` label and
whether it is feature-level inherited metadata from `Source PRD` or an
issue-level override. It also records issue-level parallelization,
dependencies, blocks, closeout target, branch or PR expectation, current wave,
and integration proof target. For PRD-backed workflows, also record delivery
authority, publication authority, and issue mutation authority separately, as
defined in `prd-backed-delivery.md`. Record integration mode only when it is
not obvious from the inherited delivery mode or when the issue declares an
override. Workers may not choose a different branch or PR strategy without a
root-owned ledger update and authorization check.

Issue-level parallelization controls startability:

- `independent`: may enter an active wave when authorization, ownership
  boundaries, and gates allow it.
- `depends-on <issue>`: do not assign until the named dependency has
  root-verifiable completion proof.
- `blocks <issue>`: may start when otherwise eligible; keep dependent items
  unassigned until this one completes.
- `root-integrated`: keep implementation in the root thread and record
  `Surface=no-delegation` unless the worker is read-only or proof-only.

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
- publication-safety

Portfolio overrides:
- <gate>: <stricter requirement or owner-approved exception>

Gate matrix:
| Source ID | Workstream ID | Gate | Required When | Status | Evidence | Waiver/Owner | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <source id> | <workstream id> | <gate> | <condition> | pass, fail, blocked, or not-applicable | <root-verifiable proof> | <owner/date or none> | <next action> |

## Workstreams

### active

| ID | Source ID | Source Ref | Repo | Surface | Worker ID | Wave | Title | Objective | Delivery | Acceptance Criteria | Status | Last Read | Root Baseline | Resync State | Next Check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-001 | github-issue:owner/repo#123 | <url/path:line> | owner/repo | codex-app-thread | <thread id or root> | 1 | <Project>: <short task> | <objective> | <Source PRD; delivery mode; delivery authority; publication authority; issue mutation authority; parallelization; dependencies; blocks; branch/PR expectation; closeout> | <source acceptance criteria> | active | <time> | <commit/ledger wave> | synced, needs-resync, replaced, or root-owned | <time/action> |

### autonomous

- <candidate item, repo, URL, reason it is safe to delegate>

### needs-owner

- <decision, URL/context, options, recommendation>

### ready-next

- <owner-ready task, proof, required next action>

### blocked

- <blocker, owner/action needed, evidence>

### ignored-or-suppressed

- <item, reason, date, owner>

### deferred

- <follow-up issue/ticket or proposed issue body, residual scope, blocker,
  source item, owner/action needed>

### completed

- <source id/ref, delivery mode, branch/PR/proof, validation, source closeout target and
  whether it was updated/closed>
- <worker id/title, integration method, worker lifecycle decision, generated
  ignored artifacts removed/retained/left in helper worktree>

### released

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

- `active`: work that currently needs orchestration, worker monitoring,
  integration, owner input, or a scheduled next check. Remove a worker row from
  `active` once its output is integrated, abandoned, retained only for
  inspection, or handed off with the remaining action recorded elsewhere. A
  completed row may remain in `active` only while a root-owned closeout action
  is still pending, and the `Next Check` must name that action.
- `autonomous`: candidate work safe to delegate under the current worker policy.
  Move it to `active` when assigned, or reclassify it when delegation is no
  longer useful or authorized. A ledger cannot be `complete` while actionable
  `autonomous` work remains.
- `needs-owner`: progress waits on owner decision, credentials, scope approval,
  risk acceptance, mutation authorization, or another non-Codex decision. Record
  the decision brief, options, recommendation, and minimum owner action.
- `ready-next`: owner-ready work that still needs an explicit next action such
  as review, commit, push, PR, merge, close, or release. Execute it before
  stopping when current authorization permits; otherwise reclassify it as
  `needs-owner`, `blocked`, or `deferred` with the missing decision or access.
  For PRD-backed workflows with branch plus draft PR delivery authority,
  commit, push, and draft PR creation are current-authorized actions after
  gates pass unless the owner restricted publication.
- `blocked`: work cannot progress with current access, state, dependency, or
  proof. Record blocker, evidence, minimum next action, and whether the blocker
  is owner-actionable or external.
- `ignored-or-suppressed`: known item intentionally excluded from this loop.
  Record source id, source fingerprint, owner, date, and reason. Do not
  rediscover it unless owner direction changes or the source fingerprint changes.
- `completed`: implemented work whose required gates passed and whose delivery
  contract is satisfied. Record commits, PRs, validation, root-verifiable proof,
  source closeout state, integration method, worker lifecycle decision, and any
  generated ignored artifacts that were removed or intentionally retained.
  If publication, closeout, or proof is blocked outside current authorization,
  keep the source in `needs-owner`, `blocked`, or `deferred` instead.
- `deferred`: known residual work that is intentionally not part of the current
  closeout. Link the follow-up issue/ticket when one exists, or record the
  proposed follow-up when mutation is not authorized. Do not mirror completed
  source items here; use `deferred` only for real residual scope, blocked live
  proof, or owner-visible follow-up work.
- `released`: use only for actual product/package/version releases, deploys, or
  tags. Do not put ordinary issue-closing commits here unless a release really
  happened.

## Closeout Hygiene

Before marking a ledger `complete`, verify:

- All discovery sources were rescanned or intentionally skipped with a recorded
  reason, cursor, and fingerprint.
- `active` contains no worker that is merely done; every active row needs a real
  next check or root-owned closeout action.
- `autonomous` is empty, or every item was reclassified as non-actionable under
  the current authorization.
- `ready-next` is empty, or every remaining action was reclassified as
  `needs-owner`, `blocked`, or `deferred` with the missing authorization,
  decision, or follow-up.
- PRD-backed work with authorized branch plus draft PR delivery either records
  the published draft PR URL or records the exact blocker that prevents
  publication; do not mark it complete while authorized commit, push, or draft
  PR creation remains in `ready-next`.
- `needs-owner` and `blocked` entries are explicitly non-Codex-actionable and
  include decision briefs, blockers, evidence, and minimum next actions.
- `deferred` contains only residual work with a linked or proposed
  owner-visible follow-up.
- `completed` records the final proof, source closeout state, integration
  method, publication state, and worker lifecycle decision for each completed
  worker-backed item.
- Generated ignored artifacts and helper worktrees are either removed, retained
  for inspection with a reason, left only inside a helper worktree with an
  explicit lifecycle decision, or explicitly handed off.
- `ignored-or-suppressed` items have source id, source fingerprint, reason,
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
  `needs-owner`, `blocked`, or `deferred`;
- newly surfaced source items are added to `autonomous`, `active`,
  `needs-owner`, `blocked`, `deferred`, or `ignored-or-suppressed` before
  stopping.
