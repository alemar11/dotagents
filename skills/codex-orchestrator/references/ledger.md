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
portfolio, repo realpath, or source id. The ledger is an advisory coordination
record, not a filesystem or database lock. Treat it as the owner-visible record
for root claims, but do not use it to justify racing duplicate publication or
source mutation.

Use canonical local repo realpaths when available. Portfolio names can alias the
same checkout, so a new root should check the target ledger and any known
ledgers under `~/.cache/dotagents/skills/codex-orchestrator/ledgers/` for
overlapping active-root claims before dispatch.

Classify each overlapping active-root claim as live, stale, released, or
non-overlapping by reading only the active-root claim, active workers,
`autonomous`, `ready-next`, and recent notes. If another non-stale active root
claims overlapping repo realpaths or source ids, stop as `needs-owner`. Report
the claiming root, overlap, last progress read, and options: resume the
existing root, wait, hand off, or explicitly take over.

Staleness is recovery logic, not permission to race. Use `Last Progress Read`
plus active workstream `Next Check` values to decide whether a claim is stale.
For a stale overlap with no active workers and no actionable `autonomous` or
authorized `ready-next` items, preserve history: mark the prior claim
`released` or `takeover-recorded`, add a dated note naming the new owning
ledger/root, then continue only after the current ledger has a clear
active-root claim. Use explicit owner approval when freshness, worker output,
source mutation, or publication safety is unclear.

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
  source graph, `stale` means the claim missed the recorded ledger check window,
  `released` means closeout completed, and `takeover-recorded` means a new root
  explicitly recorded a takeover from a stale or owner-approved prior root.
- `active_root_takeover_policy`: `owner-approval` requires an explicit owner
  decision, while `stale-ledger-check` permits takeover only after the recorded
  stale-read note and takeover note are present.

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
Goal mode: active|unavailable|not-applicable
Goal objective: <goal text or ledger fallback objective>
Goal fallback reason: <none or why /goal/runtime goal tool was unavailable>
Started: <YYYY-MM-DD HH:MM TZ>
Last Progress Read: <YYYY-MM-DD HH:MM TZ>
Next Root Check: <YYYY-MM-DD HH:MM TZ or none>
Takeover policy: owner-approval|stale-ledger-check
Claimed repo realpaths:
- <absolute realpath or unknown>; source=<scope evidence>
Claimed source ids:
- <source id/ref>
Active workers:
- <worker id/title or none>
Takeover history:
- <date, previous root id, overlap, stale/owner approval evidence, worker disposition>

Refresh `Last Progress Read` during each wave or due ledger check. Release or
mark the active-root claim `released` during final closeout when there is no
active worker, authorized `ready-next` action, or root-owned closeout action
remaining.

## Worker And Delivery References

Authorization resolution: per-workstream
Assignable authorization modes: inspect|implement|commit|push|pr|review-ready|ci-rerun-fix|merge-close|release
Session CLI subagents consented: authorized-by-invocation|disabled|limited; max=<n|unbounded>
Session Codex App threads consented: true|false; max=<n|unspecified>
No subdelegation: true
Workers edit ledger: false
Root owns worker lifecycle: true
Visible worker title format: <Project>: <short current task>

Worker fields follow `worker.md`. Delivery, publication, and issue-mutation
authority follow `prd-backed-delivery.md`. Gates follow `gates.md`. Keep only
the current session summary here; put full source contracts in PRDs, generated
issues, owner requests, or the linked references.

## Gate Policy

Available gates:
- authorization
- closure
- follow-up
- live-proof
- autoreview
- ci
- codex-pr-review
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

Use one compact block per active workstream:

#### A-001: <Project>: <short task>

| Field | Value |
| --- | --- |
| Source | <source id/ref and closeout target> |
| Repo / surface | <repo>; <root|cli-subagent|codex-app-thread>; worker=<id or root> |
| Worker evidence | requested=<none|cli-subagent|codex-app-thread>; authorized_or_consented=<true|false>; actual=<root-thread|cli-subagent|codex-app-thread>; status=<used|unavailable|attempt-failed|root-owned-fallback>; evidence=<tool/session/failure>; parallelism=<parallel|sequential|root-owned|simulated> |
| Wave / status | <wave>; active; last-read=<time>; next-check=<time/action> |
| Objective | <one concrete outcome> |
| Scheduling | <independent|depends-on|blocks|root-integrated plus proof/dependency refs> |
| Delivery | <local-only|pull-request|direct-commit>; publication=<none|explicit-owner-authorization|prd-backed-branch-plus-draft-pr|prd-backed-merge-ready-pr|blocked>; issue-mutation=<none|pr-body-closeout-only|explicit-direct-mutation>; codex-review=<not-applicable|not-requested|requested|received|passed|blocked> |
| Integration | baseline=<commit/wave>; resync=<synced|needs-resync|replaced|root-owned>; publication checkout=<checkout or not-applicable>; caller checkout=<policy> |
| Gates / proof | <required gates and current proof target> |

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

- <source id/ref, runtime delivery, branch/PR/proof, ready-for-review state, Codex
  review proof, validation, source closeout target and whether it was
  updated/closed, publication checkout, caller checkout disposition>
- <worker id/title, integration method, publication checkout, caller checkout
  disposition, worker lifecycle decision, generated ignored artifacts
  removed/retained/left in helper worktree>

### released

- <source id/ref, repo/version/tag/date, release gate proof, release action or
  deploy proof>

## Wave Reports

Record the startup delegation baseline before dispatch. Include that CLI
subagents are authorized by invoking `$codex-orchestrator` unless the owner
disabled delegation, visible Codex App worker thread consent when that surface
is available, and any visible-thread max concurrent worker limit. Record each
non-blocking execution report with its source items, selected worker surface,
orchestrator-chosen split for the current wave, authorization modes, delivery
path, stop conditions, and any owner edits to surface, authorization, or
delivery path.

The execution report is not an approval prompt. Continue later waves while they
stay inside the recorded source items, CLI subagent default, visible-thread
session consent, authorization modes, delivery path, and stop conditions. If
visible-thread consent is missing, delegation was disabled, or a wave would
exceed consented visible-thread limits, planned work may remain in the ledger,
but unauthorized visible workers or disabled delegation must not start until
the owner gives the missing consent.

| Wave | Started | Finished | Sources Scanned | Items Processed | Execution Report | Remaining Actionable | Blockers | Ledger Mutations | Source Mutations | Next Scan/Check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | <time> | <time> | <source ids> | <count> | <reported; startup baseline; worker split; authorization modes; delivery path; stop conditions; edits> | <count> | <summary> | <status changes> | <file/github updates or proposed updates> | <time/action> |

Record worker evidence every time the requested or available worker surface and
actual worker surface differ. Include the requested surface, owner consent when
required, actual surface, tool or session id when one exists, fallback reason,
and whether execution was parallel, sequential, root-owned, or simulated.

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
| `autonomous` | Candidate safe to delegate under current session authorization and execution-report boundaries. Move to `active` when assigned or reclassify when delegation is no longer useful or authorized. Ledger cannot be `complete` while actionable items remain. |
| `needs-owner` | Waiting on owner decision, credentials, scope approval, risk acceptance, mutation authorization, or another non-Codex decision. Record decision brief, options, recommendation, and minimum owner action. |
| `ready-next` | Owner-ready work still needing review, commit, push, PR, Codex PR review, merge, close, or release. Execute when authorized; otherwise reclassify with the missing decision/access. PRD-backed commit, push, and draft PR creation are authorized after gates when branch plus draft PR delivery exists and publication was not restricted. Ready-for-review transition and Codex review request require merge-ready closeout authority, such as `publication_authority=prd-backed-merge-ready-pr` or `publication_authority=explicit-owner-authorization` with those actions named. |
| `blocked` | Cannot progress with current access, state, dependency, or proof. Record blocker, evidence, minimum next action, and whether it is owner-actionable or external. |
| `ignored-or-suppressed` | Known item intentionally excluded. Record source id, source fingerprint, owner, date, and reason; rediscover only if owner direction or source fingerprint changes. |
| `completed` | Required gates passed and the resolved delivery contract is satisfied. For ad-hoc `local-only` work, acceptance criteria plus validation are sufficient and publication fields are `none` or `not-applicable`. Otherwise record commits/PRs, validation, proof, source closeout, integration method, publication checkout, caller checkout disposition, lifecycle decision, and generated ignored artifact disposition. Blocked required publication, closeout, or proof remains `needs-owner`, `blocked`, or `deferred`. |
| `deferred` | Residual work intentionally outside current closeout. Link the follow-up or proposed body; use only for real residual scope, blocked live proof, or owner-visible follow-up work. |
| `released` | Release gate passed and actual product/package/version release, deploy, or tag proof is recorded. Ordinary implementation remains `completed` unless a release happened. |

## Closeout Hygiene

Before marking a ledger `complete`, verify:

- All discovery sources were rescanned or intentionally skipped with a recorded
  reason, cursor, and fingerprint.
- The Goal mode objective is achieved, or Goal mode was unavailable and the
  equivalent ledger fallback objective is achieved. If the objective is blocked,
  record the concrete gate or blocker instead of marking the ledger complete.
- The current active-root claim is `released`. If orchestration still has a
  concrete active worker, root-owned next check, or authorized next action, do
  not mark the ledger `complete`; keep the ledger active, paused, or blocked
  and say so in the final report.
- `active` contains no worker that is merely done; every active row needs a real
  next check or root-owned closeout action.
- `autonomous` is empty, or every item was reclassified as non-actionable under
  the current authorization.
- `ready-next` is empty, or every remaining action was reclassified as
  `needs-owner`, `blocked`, or `deferred` with the missing authorization,
  decision, or follow-up.
- PRD-backed work with authorized branch plus draft PR delivery either records
  the published PR URL or records the exact blocker that prevents publication;
  do not mark it complete while authorized commit, push, or draft PR creation
  remains in `ready-next`. When merge-ready closeout authority exists, also
  record non-draft state, Codex review proof, and discussion disposition, and do
  not mark it complete while ready-for-review transition, Codex review request,
  completed-review wait, review-triggered fix, post-fix validation, fresh-review
  wait, or PR-thread disposition remains in `ready-next`.
- For merge-ready closeout, verify the publication checkout is clean, accepted
  review fixes are committed and pushed to the PR branch, current CI belongs to
  the pushed head, the latest Codex review covers that same head, and unresolved
  review threads are either fixed, explicitly dispositioned, or recorded as a
  blocker. If any check fails, keep the ledger active, `ready-next`, or blocked
  instead of `complete`.
- `needs-owner` and `blocked` entries are explicitly non-Codex-actionable and
  include decision briefs, blockers, evidence, and minimum next actions.
- `deferred` contains only residual work with a linked or proposed
  owner-visible follow-up.
- `completed` records the final proof, source closeout state, integration
  method, publication state, ready-for-review state, Codex review proof,
  publication checkout, caller checkout disposition, and worker lifecycle
  decision for each completed worker-backed item.
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
