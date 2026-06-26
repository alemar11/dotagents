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

## Active Root Claims

Before creating workers, starting root-owned implementation, or mutating source
state, the root orchestrator verifies that no live root already claims the same
portfolio, repo realpath, or source id. The ledger is the source of truth for
this advisory claim; do not introduce a separate filesystem lock as the
authoritative state.

Use canonical local repo realpaths when available. Portfolio names can alias the
same checkout, so a new root should check the target ledger and any known
ledgers under `~/.cache/dotagents/skills/codex-orchestrator/ledgers/` for
overlapping active-root claims before dispatch.

If another non-stale active root claims overlapping repo realpaths or source
ids, stop as `needs-owner`. Report the claiming root, overlap, last heartbeat,
and options: resume the existing root, wait, hand off, or explicitly take over.
If the prior root is stale, record the takeover before dispatching new workers
or mutating sources.

Staleness is recovery logic, not permission to race. Use explicit owner
approval when heartbeat freshness is unclear, when workers may still contain
unintegrated output, or when source mutation or publication could be duplicated.
Default heartbeat policy is `every-5-minutes` when monitoring is active; a
takeover should require at least two missed heartbeats plus a grace window or
explicit owner approval.

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
- `active_root_status`: `claimed` means this root currently owns the portfolio
  source graph, `stale` means the claim missed the recorded heartbeat policy,
  `released` means closeout completed, and `takeover-recorded` means a new root
  explicitly recorded a takeover from a stale or owner-approved prior root.
- `active_root_takeover_policy`: `owner-approval` requires an explicit owner
  decision, while `stale-heartbeat` permits takeover only after the recorded
  heartbeat threshold and takeover note are present.

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

## Active Root

Status: claimed|stale|released|takeover-recorded
Root ID: <thread id, session id, or root descriptor>
Root surface: codex-app-thread|cli|unknown
Started: <YYYY-MM-DD HH:MM TZ>
Last heartbeat: <YYYY-MM-DD HH:MM TZ>
Heartbeat policy: disabled|manual|every-5-minutes|custom
Takeover policy: owner-approval|stale-heartbeat
Claimed repo realpaths:
- <absolute realpath or unknown>; source=<scope evidence>
Claimed source ids:
- <source id/ref>
Active workers:
- <worker id/title or none>
Takeover history:
- <date, previous root id, overlap, stale/owner approval evidence, worker disposition>

Refresh `Last heartbeat` during each wave or heartbeat check. Release or mark
the active-root claim `released` during final closeout when there is no active
worker, authorized `ready-next` action, or root-owned closeout action remaining.

## Worker Policy

Authorization resolution: per-workstream
Assignable authorization modes: inspect|implement|commit|push|pr|ci-rerun-fix|merge-close|release
Delegated worker surface: auto|codex-app-thread|cli-subagent|none
Max active delegated workers: <number>
Max active CLI/subagents: <number or none>
Max active Codex App threads: <number or none>
Session-wide delegated worker cap: <number or none>
Heartbeat: disabled|manual|every-5-minutes|custom
No subdelegation: true
Workers edit ledger: false
Root owns worker lifecycle: true
Visible worker title format: <Project>: <short current task>

Worker policy values follow `worker.md`. Caps are not quotas. Preserve separate
CLI/App/session caps, list each authorization mode explicitly, and record
`Surface=no-delegation`, `Worker ID=root`, and the reason when root owns work.
Authorization modes are not project-memory defaults; the root resolves them for
each workstream from owner request, source item, linked `Source PRD`,
publication authority, issue mutation authority, selected worker surface,
dependencies, dirty-worktree state, and gates. Ignore legacy
project-memory worker-authorization setup values as stale, non-authoritative
state.

## Delivery Mode Policy

Default delivery mode:
- `one-feature-branch` for a single git repo, including monorepos.
- `one-pr-per-repo` for true multi-repo features.

Exceptions:
- `one-pr-per-issue` only when the issue is isolated from shared contracts,
  migrations, lockfiles, generated files, broad validation, and other active
  issue work.
- `direct-commit` only with explicit owner authorization.

Each implementation workstream records effective delivery mode, inheritance or
override source, issue-level parallelization, dependencies, blocks, closeout,
branch/PR expectation, publication checkout, caller checkout policy, current
wave, integration proof target, and, for PRD-backed workflows, separate
delivery, publication, and issue-mutation authority. Workers may not choose a
different branch or PR strategy without a root-owned ledger update and
authorization check.

Startability is issue-level: `independent` may start when gates allow,
`depends-on <issue>` waits for root-verifiable dependency proof,
`blocks <issue>` starts when otherwise eligible while dependents wait, and
`root-integrated` stays in root except for read-only or proof-only workers.

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

Every non-active bucket entry must preserve the source id/ref plus the relevant
proof or evidence, owner action or next action, and closeout or follow-up target
when those fields apply.

### active

| ID | Source ID | Source Ref | Repo | Surface | Worker ID | Wave | Title | Objective | Delivery | Acceptance Criteria | Status | Last Read | Root Baseline | Resync State | Next Check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-001 | github-issue:owner/repo#123 | <url/path:line> | owner/repo | codex-app-thread | <thread id or root> | 1 | <Project>: <short task> | <objective> | <Source PRD; delivery mode; delivery authority; publication authority; issue mutation authority; parallelization; dependencies; blocks; branch/PR expectation; publication checkout; caller checkout policy; closeout> | <source acceptance criteria> | active | <time> | <commit/ledger wave> | synced, needs-resync, replaced, or root-owned | <time/action> |

### autonomous

- <source id/ref, candidate item, repo, evidence it is safe to delegate, next
  action, closeout target>

### needs-owner

- <source id/ref, decision, context/evidence, options, recommendation, minimum
  owner action, closeout impact>

### ready-next

- <source id/ref, owner-ready task, proof, authorized next action, closeout
  target>

### blocked

- <source id/ref, blocker, evidence, minimum next action, owner-actionable or
  external>

### ignored-or-suppressed

- <source id/ref, source fingerprint, item, reason, date, owner>

### deferred

- <source id/ref, follow-up issue/ticket or proposed issue body, residual scope,
  blocker, owner/action needed, closeout impact>

### completed

- <source id/ref, delivery mode, branch/PR/proof, validation, source closeout target and
  whether it was updated/closed, publication checkout, caller checkout disposition>
- <worker id/title, integration method, publication checkout, caller checkout
  disposition, worker lifecycle decision, generated ignored artifacts
  removed/retained/left in helper worktree>

### released

- <source id/ref, repo/version/tag/date, release gate proof, release action or
  deploy proof>

## Wave Checkpoints

Record the owner checkpoint approval before dispatch. Include the approval
timestamp, approver wording, approval scope (`current-wave` or
`bounded-multi-wave`), selected worker surface, resolved surface when `auto` is
used, worker cap, stop conditions, and any owner edits to split, surface, cap,
authorization, or delivery path. If a bounded multi-wave checkpoint is approved,
record its boundaries and continue later waves only while they stay inside the
approved source items, surface, cap, authorization, delivery path, and stop
conditions. If approval is pending, planned work may remain in the ledger, but
implementation workers and root-owned implementation must not start.

| Wave | Started | Finished | Sources Scanned | Items Processed | Owner Checkpoint | Remaining Actionable | Blockers | Ledger Mutations | Source Mutations | Next Scan/Check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | <time> | <time> | <source ids> | <count> | <approval time, wording, scope, surface/cap, stop conditions, edits, or pending> | <count> | <summary> | <status changes> | <file/github updates or proposed updates> | <time/action> |

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

If separate portfolios claim the same repo realpath or source id, treat that as
an overlap unless the owner explicitly recorded non-overlapping boundaries or a
handoff/takeover decision. Record intentional split roots in the active-root
claim and in `## Notes`.

## Vocabulary

| State | Meaning and required record |
| --- | --- |
| `active` | Codex-actionable orchestration, worker monitoring, root integration, or scheduled root check. Owner waiting belongs in `needs-owner`; missing access/state/dependency/proof belongs in `blocked`. Remove worker rows once integrated, abandoned, retained, or handed off unless a root closeout action remains named in `Next Check`. |
| `autonomous` | Candidate safe to delegate under current policy. Move to `active` when assigned or reclassify when delegation is no longer useful or authorized. Ledger cannot be `complete` while actionable items remain. |
| `needs-owner` | Waiting on owner decision, credentials, scope approval, risk acceptance, mutation authorization, or another non-Codex decision. Record decision brief, options, recommendation, and minimum owner action. |
| `ready-next` | Owner-ready work still needing review, commit, push, PR, merge, close, or release. Execute when authorized; otherwise reclassify with the missing decision/access. PRD-backed commit, push, and draft PR creation are authorized after gates when branch plus draft PR delivery exists and publication was not restricted. |
| `blocked` | Cannot progress with current access, state, dependency, or proof. Record blocker, evidence, minimum next action, and whether it is owner-actionable or external. |
| `ignored-or-suppressed` | Known item intentionally excluded. Record source id, source fingerprint, owner, date, and reason; rediscover only if owner direction or source fingerprint changes. |
| `completed` | Required gates passed and delivery contract is satisfied. Record commits/PRs, validation, proof, source closeout, integration method, publication checkout, caller checkout disposition, lifecycle decision, and generated ignored artifact disposition. Blocked publication, closeout, or proof remains `needs-owner`, `blocked`, or `deferred`. |
| `deferred` | Residual work intentionally outside current closeout. Link the follow-up or proposed body; use only for real residual scope, blocked live proof, or owner-visible follow-up work. |
| `released` | Release gate passed and actual product/package/version release, deploy, or tag proof is recorded. Ordinary implementation remains `completed` unless a release happened. |

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
  method, publication state, publication checkout, caller checkout disposition,
  and worker lifecycle decision for each completed worker-backed item.
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
