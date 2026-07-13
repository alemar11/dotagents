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
`autonomous`, `ready-next`, the parent closeout watch, and recent notes. If
another non-stale active root claims overlapping repo realpaths or source ids,
stop as `needs-owner`. Report the claiming root, overlap, last progress read,
and options: resume the existing root, wait, hand off, or explicitly take over.

Staleness is recovery logic, not permission to race. Use `Last Progress Read`
plus active workstream `Next Check` values to decide whether a claim is stale.
For a stale overlap with no active workers and no actionable `autonomous` or
authorized `ready-next` items, no `root-monitoring` parent closeout watch, and
no unhanded `armed` parent closeout, preserve history: mark the prior claim
`released` or `takeover-recorded`, add a dated note naming the new owning
ledger/root, then continue only after the current ledger has a clear active-root
claim. Use explicit owner approval when freshness, worker output, source
mutation, or publication safety is unclear.

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
  `released` means closeout completed or a durable parent-closeout handoff
  transferred the remaining watch while the ledger stayed `paused`, and
  `takeover-recorded` means a new root explicitly recorded a takeover from a
  stale or owner-approved prior root.
- `active_root_takeover_policy`: `owner-approval` requires an explicit owner
  decision, while `stale-ledger-check` permits takeover only after the recorded
  stale-read note and takeover note are present.
- `merge_authority`: `none` by default or
  `explicit-owner-authorization` for the named PR or PR set.
- `merge_policy`: `owner-approval` by default or
  `automatic-after-gates` when the explicit merge instruction waives another
  checkpoint after gates pass.
- `parent_closeout_watch`: `not-applicable`, `root-monitoring`,
  `owner-handoff`, `automation-handoff`, or `complete`. Owner and automation
  handoffs release the root only with the durable packet defined below and keep
  the ledger `paused` until actual parent closure is reconciled.
- `github_workflow_skill`: the selected `$gitstack:*` workflow skill.
- `github_primary_transport`: `connector`; authenticated `gh` is fallback only.
- `github_fallback_reason`: `none`, `connector-unavailable`,
  `capability-unsupported`, or `transport-failure`.
- `recovery_packet_status`: `fresh`, `stale`, `invalid`, or `unavailable`;
  `fresh` requires current repo and source fingerprints to match the packet.
- `metric_status`: `exact-phase` for a root-scoped uncontaminated interval,
  `exact-interval` for an interleaved interval that must not be attributed to a
  phase, or `unavailable`. Never estimate.

Workstream state meanings are defined in `## Vocabulary`. Worker, publication,
and gate values are owned by `worker.md`, `prd-backed-delivery.md`, and
`gates.md`.
Option fields and values follow `options.md`: snake_case fields and lower-kebab
enum values. Treat older uppercase values, booleans, human labels, and
hyphenated assignment keys as read aliases only; rewrite them when touched.

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

## Option Resolution

### Session Rows

| row_id | scope_id | field | value | source | evidence |
| --- | --- | --- | --- | --- | --- |
| `session:<field>` | `session` | <Session Registry field from options.md> | <canonical value> | `default`, `owner-instruction`, `runtime-capability`, or `legacy-migration` | <instruction/tool ref or none> |
| `session:worker_limit` | `session` | `worker_limit` | <positive integer or `unbounded`> | `default` only for `unbounded`; otherwise `owner-instruction` or evidence-preserving `legacy-migration` | <matching bounded-delegation owner evidence or none> |
| `session:app_thread_limit` | `session` | `app_thread_limit` | <positive integer or `unspecified`> | `default` only for `unspecified`; otherwise `owner-instruction` or evidence-preserving `legacy-migration` | <matching App-thread-consent owner evidence or none> |

### Scoped Rows

| row_id | scope_id | field | value | source | evidence |
| --- | --- | --- | --- | --- | --- |
| `source:<Source ID>:source_mutation_authority` | `source:<Source ID>` | `source_mutation_authority` | <canonical value> | `default`, `owner-instruction`, `runtime-capability`, or `legacy-migration` | <instruction/source/tool ref or none> |
| `<scope_id>:<field>` | `workstream:<id>` | <Per-Workstream Registry field from options.md> | <canonical value> | `default`, `owner-instruction`, `source-contract`, `runtime-capability`, `runtime-derived`, or `legacy-migration` | <instruction/source/tool ref or none> |

Every applicable source row must be projected into its corresponding
discovery-source row, and every workstream row into its workstream ledger row.
Discovery sources carry only `source_mutation_authority`; full authority and
delivery options begin at workstream registration. Never reuse another scope's
authority or delivery value. Keep every `row_id` unique across both option
tables, restrict row IDs to `[A-Za-z0-9:_-]+` with no commas, and encode a
literal `|` in evidence data as `%7C`.

## Discovery Sources

| Source ID | Kind | Path/Query/URL | Last Checked | Cursor/Fingerprint | Item Key Rule | source_mutation_authority | Suppression Rule |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ds-001 | markdown, github-issue, github-pr, ci, todo, ledger | <path/query/url> | <time> | <etag/sha/cursor/checksum> | <stable id rule> | none, propose, or write | <owner/date/reason/source fingerprint> |

`source_mutation_authority` uses the canonical option values.

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
active_root_takeover_policy: owner-approval|stale-ledger-check
Scoped merge option refs: <exact workstream merge_authority/merge_policy row_ids or none>
parent_closeout_watch: not-applicable|root-monitoring|owner-handoff|automation-handoff|complete
Parent closeout watch evidence: <ledger section/fingerprint plus owner-visible handoff or automation id, or none>
Claimed repo realpaths:
- <absolute realpath or unknown>; source=<scope evidence>
Claimed source ids:
- <source id/ref>
Active workers:
- worker_id=<stable id>; actual_workstream_surface=<cli-subagent|codex-app-thread>; workstream_ids=<comma-separated ids>
- none
Recovery packet content fingerprint: <sha256 from runtime-efficiency.md or none>
Takeover history:
- <date, previous root id, overlap, stale/owner approval evidence, worker disposition>

Refresh `Last Progress Read` during each wave or due ledger check. Release or
mark the active-root claim `released` during final closeout when there is no
active worker, authorized `ready-next` action, or root-owned closeout action
remaining. An unmerged `armed` parent closeout is a root-owned action unless a
durable `owner-handoff` or explicitly authorized `automation-handoff` transfers
the watch; that handoff releases the root with `ledger_status=paused`, never
`complete`.

## Codex Review Wait Registry

This is the sole authority for review wait timing. Keep exactly one row for
each active `<owner>/<repo>#<number>@<head-sha>` key; workstream wait fields are
derived projections that reference this row and never create independent
deadlines.

| wait_record | wait_profile_pr | request_head | request_object | wait_profile | wait_budget_minutes | wait_started_at | wait_deadline | wait_elapsed_seconds | wait_state |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <owner/repo#number@head-sha> | <owner/repo#number> | <head-sha> | <id/url> | <standard|extended> | <15|30> | <timestamp> | <timestamp> | <number> | <active|monitoring-required|terminal> |

When multiple workstreams map to the same PR and head, every one must carry
the same `wait_record` and an exact projection of that row. Update the registry
row first, then refresh all mapped projections. Retain the PR-level extended
profile across later heads as described by the review gate, while using a new
row and deadline for each new head.

## Parent Closeout Watch

Status: not-applicable|root-monitoring|owner-handoff|automation-handoff|complete
Parent PRD: <issue ref or none>
Closeout PR: <PR ref or pending>
Review policy: <required|skip|not-applicable>
Armed head: <closeout-qualified SHA or none>
Closeout base: <branch or none>
Current default branch: <branch or none>
PR-body evidence: <URL/fingerprint or none>
Merge state: open|merged|closed|unknown|not-applicable
Watch owner: <root id|owner|automation id|none>
Last checked: <time or none>
Next check: <time/event/owner action or none>
Handoff evidence: <persisted owner-visible packet or automation id/config, or none>
Mutation triggers: <head push, base retarget, default-branch change, PR-body edit, merge>
Mismatch action: <remove/replace parent closer, set policy-specific pending-review or pending-closeout, or deferred-to-default-branch, then rerun gates>
Merge control: <root-authorized-merger|owner-pre-merge-check|event-driven-automation|not-applicable>
Post-merge proof: <merged head/base/body plus parent issue closed state, or none>

`owner-handoff` requires this packet in the ledger and the same actionable
packet in the owner-visible final report. `automation-handoff` additionally
requires explicit owner authority and a real event-driven monitor id/config that
can catch head, base/default-branch, and body mutations before merge, block the
merge or disarm the closer on mismatch, and verify post-merge issue state; a
scheduled poll or suggested automation is not a handoff. `root-monitoring` is
valid only with explicit merge authority and the root recorded as the designated
merger. Otherwise require `owner-handoff` before reporting merge-ready. Keep
`ledger_status=paused` and the parent PRD under `needs-owner` or an active
monitor until post-merge proof shows the issue closed. Only then set this watch
to `complete` and parent closeout to `closed`.

## Recovery Packet

Packet version: 1
Status: fresh|stale|invalid|unavailable
Updated: <YYYY-MM-DD HH:MM TZ>
Projection fingerprint: <sha256 of ledger content before Notes, excluding this Recovery Packet, using runtime-efficiency.md canonical extraction>
Content fingerprint: <sha256 of packet derived fields, excluding status/timestamps/fingerprints, also recorded under Active Root>
Root: <root id>; claim=<status>; goal=<objective ref>; active_workers=<unique comma-separated worker ids or none>; parent_closeout_watch=<status/ref>
Current wave: <wave id/status>; current_workstreams=<ids>; next_action=<one bounded action or blocker>
Option resolution refs: session_rows=<unique comma-separated exact row_ids>; scoped_rows=<unique comma-separated exact current source/workstream row_ids or empty>; rows_fingerprint=<sha256 of exactly the referenced row union using runtime-efficiency.md>
Repo checkpoints:
- <repo realpath>; head=<sha>; worktree=<stable fingerprint of status --short>; branch=<name or detached>
Source checkpoints:
- <registered source item id from Workstreams>; fingerprint=<etag/sha/checksum/head>; state=<ledger state>
Workstream checkpoints:
- <workstream id>; source=<registered source item id>; state=<ledger state>; scope_transfer_ref=<issue:<NN>|not-applicable>; issue_mutation_transfer_ref=<issue:<NN>|not-applicable>; delivery_evidence_fingerprint=<sha256 or not-applicable>; issue_mutation_evidence_fingerprint=<sha256 or not-applicable>
Required gates:
- <source/workstream>; <gate>=<status>; evidence=<path/ref/hash or pending>
Proof index:
- <proof id>; <path/url/commit>; fingerprint=<sha/checksum>; result=<pass|fail|blocked>
Blockers:
- <source>; <blocker>; minimum_next_action=<action> or none
References to load next:
- `## Option Resolution`: <exact session and scoped row_ids above; required before dispatch or mutation>
- <ledger section/source/reference path and reason>

This packet is a disposable compact index, not authority. Keep refs and
fingerprints here; load `runtime-efficiency.md` before resume or recovery.

## Worker And Delivery References

authorization_resolution: per-workstream
worker_authorization: inspect|implement|commit|push|pr|review-ready|ci-rerun-fix|release
delegation_mode: auto|disabled|bounded
worker_surface: auto|root-thread|cli-subagent|codex-app-thread
worker_limit: <positive integer|unbounded>
app_thread_consent: not-requested|granted|denied
app_thread_limit: <positive integer|unspecified>
raw_worktree_fallback: forbidden|owner-approved
pr_shape: single-pr|per-repo-pr|none
branch_name: <exact branch|not-applicable>
scope_transfer_ref: <issue:<NN>|not-applicable>
issue_mutation_transfer_ref: <issue:<NN>|not-applicable>
closeout_mode: feature-pr-closes-issue|repo-pr-closes-issue|direct-commit-closes-issue|local-done-move-after-proof|not-applicable
integration_mode: single-repo-pr|repo-pr|direct-commit|not-applicable
subdelegation: forbidden
worker_ledger_mutation: forbidden
worker_lifecycle_owner: root
Visible worker title format: <Project>: <short current task>
Root capability snapshot: filesystem=<profile/evidence>; network=<available|restricted|unknown>; gh_auth=<available|unavailable|not-required>; codex_cli=<available|unavailable|not-required>; autoreview=<available|unavailable|reroute-to-root>; checked_at=<time/evidence>
GitHub workflow skill: <gitstack skill or none>
GitHub primary transport: connector
GitHub fallback: fallback_status=<unused|used>; transport=<none|gh>; reason=<none|connector-unavailable|capability-unsupported|transport-failure>; operation=<operation or none>; evidence=<failure or none>; authority_reused=<authority or none>; result=<result or none>

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
- merge-authorization

Portfolio overrides:
- <gate>: <stricter requirement or owner-approved exception>

Gate matrix:
| Source ID | Workstream ID | Gate | Required When | Status | Evidence | Waiver/Owner | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <source id> | <workstream id> | <gate> | <condition> | pass, fail, blocked, or not-applicable | <root-verifiable proof> | <owner/date or none> | <next action> |

## Workstreams

Every non-active bucket entry must preserve the source id/ref plus the relevant
proof or evidence, owner action or next action, and closeout or follow-up target
when those fields apply. Start every such entry with the parseable prefix
`- workstream_id=<stable-id>; source_id=<stable-id-or-ref>;`. Active entries use
their `#### <workstream-id>:` heading as the authoritative ID.

### active

Use one compact block per active workstream:

#### A-001: <Project>: <short task>

| Field | Value |
| --- | --- |
| Source | <source id/ref and closeout target> |
| Repo / surface | <repo>; <root|cli-subagent|codex-app-thread>; worker=<id or root> |
| Worker evidence | worker_surface=<auto|root-thread|cli-subagent|codex-app-thread>; actual_workstream_surface=<root-thread|cli-subagent|codex-app-thread>; authorization_state=<authorized-by-invocation|owner-consented|not-authorized>; status=<used|unavailable|attempt-failed|root-owned-fallback>; evidence=<tool/session/failure>; parallelism=<parallel|sequential|root-owned|simulated>; capability_snapshot=<filesystem/network/gh_auth/codex_cli/autoreview/checked_at evidence> |
| Wave / status | <wave>; active; last_read=<time>; next_check=<time/action> |
| Objective | <one concrete outcome> |
| Scheduling | parallelization=<independent|depends-on|blocks|root-integrated>; dependency_ids=<refs|none>; blocked_issue_ids=<refs|none>; dependency_reason=<reason|none>; dependency_proof=<evidence|pending|none> |
| Delivery | delivery_mode=<local-only|pull-request|direct-commit>; delivery_source=<runtime-default|feature-level-inherited|issue-level-override|owner-instruction>; delivery_source_evidence=<scoped-option-row/source-ref|none>; branch_name=<exact branch|not-applicable>; current_pr_ref=<owner/repo#number|pending|not-applicable>; scope_transfer_ref=<issue:<NN>|not-applicable>; issue_mutation_transfer_ref=<issue:<NN>|not-applicable>; temporary_source_execution=<forbidden|owner-approved>; completion_proof_policy=<live-required|synthetic-accepted>; pr_shape=<single-pr|per-repo-pr|none>; closeout_mode=<feature-pr-closes-issue|repo-pr-closes-issue|direct-commit-closes-issue|local-done-move-after-proof|not-applicable>; integration_mode=<single-repo-pr|repo-pr|direct-commit|not-applicable>; publication_authority=<none|explicit-owner-authorization|prd-backed-pull-request|blocked>; pr_closeout=<merge-ready|draft-only|not-applicable>; codex_review_policy=<required|skip|not-applicable>; issue_mutation_authority=<none|pr-body-closeout-only|explicit-direct-mutation>; automation_authority=<none|explicit-owner-authorization>; automation_target=<source/workstream ref|none>; parent_prd_applicability=<required|deferred-vehicle|not-applicable>; parent_prd_applicability_reason=<whole-prd-final-pr|non-default-base|partial-pr|ad-hoc|local-tracker|no-parent|draft-only|other-reason>; parent_prd_closeout=<not-applicable|pending-review|pending-closeout|deferred-to-default-branch|armed|closed|blocked>; parent_prd_ref=<ref|none>; parent_closeout_vehicle=<pr-ref|pending|none>; parent_closeout_head=<sha|none>; parent_closeout_base=<branch|none>; default_branch=<branch|none>; pr_body_evidence=<url/fingerprint|none>; parent_closeout_watch=<not-applicable|root-monitoring|owner-handoff|automation-handoff|complete>; watch_evidence=<ref|none>; merge_authority=<none|explicit-owner-authorization>; merge_policy=<owner-approval|automatic-after-gates>; codex_review=<not-applicable|not-requested|requested|received|passed|skipped|blocked> |
| Codex review evidence | request_head=<sha|none>; request_object=<id/url|none>; checker_status=<not-requested|acknowledged|pending|clean|findings|stale|error>; wait_record=<pr-ref@head|none|not-applicable>; wait_profile_pr=<pr-ref|none|not-applicable>; wait_profile=<standard|extended|not-applicable>; wait_budget_minutes=<15|30|not-applicable>; wait_started_at=<timestamp|none|not-applicable>; wait_deadline=<timestamp|none|not-applicable>; wait_elapsed_seconds=<number|none|not-applicable>; wait_state=<not-started|active|monitoring-required|terminal|not-applicable>; result_head=<sha|none>; result_kind=<formal-review|provider-comment|clean-reaction|none>; result_object=<id/url|none>; provider=<verified identity|none>; terminal=<clean|findings|error|none>; disposition=<status/evidence> |
| GitHub routing | workflow_skill=<gitstack skill>; primary_transport=connector; operation=<operation>; fallback=<unused|gh>; fallback_reason=<none|connector-unavailable|capability-unsupported|transport-failure>; evidence=<failure/result>; authority_reused=<authority> |
| Integration | baseline=<commit/wave>; resync_state=<synced|needs-resync|replaced|root-owned>; publication_checkout=<checkout or not-applicable>; caller_checkout_policy=<policy> |
| Gates / proof | <required gates and current proof target> |

For every active row, `parent_prd_applicability=required` requires a parent ref
and one of `pending-review`, `pending-closeout`, `armed`, or `blocked`.
`parent_prd_applicability=deferred-vehicle` requires reason `non-default-base`,
state `deferred-to-default-branch`, and a linked later default-branch
`parent_closeout_vehicle` or `pending` vehicle-selection action in `ready-next`.
`parent_prd_closeout=armed` is valid only when `parent_closeout_head` equals the
current closeout-qualified SHA (reviewed for `required`, fully validated for
`skip`), `parent_closeout_base` equals the current `default_branch`,
and `pr_body_evidence` proves the parent closing keyword is present; none of
those proof fields may be `none`.
An unmerged `armed` row also requires `parent_closeout_watch=root-monitoring`,
`owner-handoff`, or `automation-handoff` with matching watch evidence.
`root-monitoring` additionally requires explicit merge authority and the root as
the designated merger; `merge_authority=none` requires `owner-handoff`, while
`automation-handoff` requires an explicitly authorized event-driven monitor.
`parent_prd_applicability=not-applicable` requires
`parent_prd_closeout=not-applicable` plus a concrete applicability reason.
Reconciliation must reject unsupported `armed` or unjustified
`not-applicable` claims before dispatch, mutation, recovery, or closeout.

When reading legacy ledger rows, migrate
`prd-backed-merge-ready-pr` to
`publication_authority=prd-backed-pull-request` plus
`pr_closeout=merge-ready`. Migrate `prd-backed-branch-plus-draft-pr` to
`publication_authority=prd-backed-pull-request`, resolve `pr_closeout` from the
canonical option record, and default it to `merge-ready`. Rewrite the legacy
value whenever the row is touched.

### autonomous

- workstream_id=<id>; source_id=<id/ref>; <candidate item, repo, evidence it is safe to delegate, next
  action, closeout target>

### needs-owner

- workstream_id=<id>; source_id=<id/ref>; <decision, context/evidence, options, recommendation, minimum
  owner action, closeout impact>

### ready-next

- workstream_id=<id>; source_id=<id/ref>; <owner-ready task, proof, authorized next action, closeout
  target>

### blocked

- workstream_id=<id>; source_id=<id/ref>; <blocker, evidence, minimum next action, owner-actionable or
  external>

### ignored-or-suppressed

- workstream_id=<id>; source_id=<id/ref>; <source fingerprint, item, reason, date, owner>

### deferred

- workstream_id=<id>; source_id=<id/ref>; <follow-up issue/ticket or proposed issue body, residual scope,
  blocker, owner/action needed, closeout impact>

### completed

- workstream_id=<id>; source_id=<id/ref>; <runtime delivery, branch/PR/proof, ready-for-review state, Codex
  review policy/evidence, parent-PRD closeout state/closeout-qualified head/PR-body evidence when
  applicable, closeout-watch/post-merge proof when applicable, validation,
  source closeout target and whether it was
  updated/closed, publication checkout, caller checkout disposition>
  - <worker id/title, integration method, publication checkout, caller checkout
  disposition, worker lifecycle decision, generated ignored artifacts
  removed/retained/left in helper worktree>

### released

- workstream_id=<id>; source_id=<id/ref>; <repo/version/tag/date, release gate proof, release action or
  deploy proof>

## Wave Reports

Record the canonical startup option snapshot before dispatch:
`delegation_mode`, `worker_surface`, `worker_limit`, `app_thread_consent`,
`app_thread_limit`, `raw_worktree_fallback`, and
`active_root_takeover_policy`, with their option-resolution evidence. In a
Codex App session, also record the App
thread id/title for every newly created worker, integration, or publication
worktree. Record each non-blocking execution report with its source items,
canonical worker surface, orchestrator-chosen split for the current wave,
authorization modes, delivery path, stop conditions, and any owner-authorized
option changes.

The execution report is not an approval prompt. Continue later waves while they
stay inside the recorded source items, canonical option snapshot, authorization
modes, delivery path, and stop conditions. If a required option is unresolved
or a wave would exceed its recorded limit, planned work may remain in the
ledger, but dispatch must not start until the canonical option row is valid.

Do not record a newly created raw Git worktree as the publication checkout in a
Codex App session unless App thread/worktree creation was reported as missing,
failed, or unsuitable and the session row is
`raw_worktree_fallback=owner-approved`. Keep the managed-worktree failure as
runtime evidence only. This restriction does not apply in CLI-only sessions.

| Wave | Started | Finished | Sources Scanned | Items Processed | Execution Report | Remaining Actionable | Blockers | Ledger Mutations | Source Mutations | Next Scan/Check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | <time> | <time> | <source ids> | <count> | <reported; startup baseline; worker split; authorization modes; delivery path; stop conditions; edits> | <count> | <summary> | <status changes> | <file/github updates or proposed updates> | <time/action> |

Record worker evidence every time the requested or available worker surface and
actual worker surface differ. Include `worker_surface`,
`actual_workstream_surface`, the relevant canonical authorization or consent
field, tool or session id when one exists, fallback reason, and whether
execution was parallel, sequential, root-owned, or simulated.

## Runtime Metrics

| Phase / Wave | Start Counter | End Counter | Input Delta | Cached Input Delta | Output Delta | Total Delta | Status / Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <phase/wave or interval> | <exact or n/a> | <exact or n/a> | <exact or n/a> | <exact or n/a> | <exact or n/a> | <exact or n/a> | exact-phase; <scoped counter> or exact-interval/unavailable |

Load `runtime-efficiency.md` before multi-wave delta transport, recovery, or
exact metric capture. One `unavailable` row is sufficient when counters are absent.

## Notes

- <dated orchestration notes and durable context>
```

## Multi-Portfolio Use

Use one ledger per portfolio. For example:

- `~/.cache/dotagents/skills/codex-orchestrator/ledgers/default.md`
- `~/.cache/dotagents/skills/codex-orchestrator/ledgers/mobile-stack.md`
- `~/.cache/dotagents/skills/codex-orchestrator/ledgers/app-backend.md`

Do not mix unrelated portfolios in one ledger. A combined operating view is
one explicitly scoped portfolio with its own stable slug and repo/source set.

If separate portfolios claim the same repo realpath or source id, treat that as
an overlap unless their recorded path/source boundaries prove non-overlap or a
canonical handoff/takeover record transfers ownership. Record intentional split
roots in the active-root claim and in `## Notes`.

## Vocabulary

| State | Meaning and required record |
| --- | --- |
| `active` | Codex-actionable orchestration, worker monitoring, root integration, or scheduled root check. Owner waiting belongs in `needs-owner`; missing access/state/dependency/proof belongs in `blocked`. Remove worker rows once integrated, abandoned, retained, or handed off unless a root closeout action remains named in `Next Check`. |
| `autonomous` | Candidate safe to delegate under current session authorization and execution-report boundaries. Move to `active` when assigned or reclassify when delegation is no longer useful or authorized. Ledger cannot be `complete` while actionable items remain. |
| `needs-owner` | Waiting on owner decision, credentials, scope approval, risk acceptance, mutation authorization, or another non-Codex decision. Record decision brief, options, recommendation, and minimum owner action. |
| `ready-next` | Owner-ready work still needing review, commit, push, PR, policy-required Codex PR review, root-owned parent-PRD PR-body closeout, merge, close, or release. Execute when authorized; otherwise reclassify with the missing decision/access. PRD-backed `pull-request` publication authorizes initial draft PR creation and defaults `pr_closeout=merge-ready` plus `codex_review_policy=required`, so ready-for-review transition, the resolved review policy, and applicable parent-PRD closeout remain actionable after local gates. An owner-scoped `codex_review_policy=skip` makes review request/wait actions `not-applicable`, not blocked. `pr_closeout=draft-only` is valid only from its canonical option-resolution row and makes those downstream actions `not-applicable` rather than blocked. |
| `blocked` | Cannot progress with current access, state, dependency, or proof. Record blocker, evidence, minimum next action, and whether it is owner-actionable or external. |
| `ignored-or-suppressed` | Known item intentionally excluded. Record source id, source fingerprint, owner, date, and reason; rediscover only if owner direction or source fingerprint changes. |
| `completed` | Required gates passed and the resolved delivery contract is satisfied. For ad-hoc `local-only` work, acceptance criteria plus validation are sufficient and publication fields are `none` or `not-applicable`. A default-branch GitHub whole-PRD closeout PR may report merge-ready with `parent_prd_closeout=armed`, proof, and an active or handed-off watch, but the parent PRD source and portfolio ledger are not complete until the PR merges and the issue is verified closed. A non-default-base PR workstream may complete at merge-ready with `deferred-to-default-branch` only when the linked later vehicle remains `active` or `ready-next`; this never completes the parent PRD or ledger. Authorized `draft-only` and other excluded workstreams record `not-applicable` with a reason. Otherwise record commits/PRs, validation, proof, source closeout, integration method, publication checkout, caller checkout disposition, lifecycle decision, and generated ignored artifact disposition. Blocked or pending required publication, closeout, or proof remains `active`, `ready-next`, `needs-owner`, `blocked`, or `deferred`. |
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
- Do not mark the ledger `complete` while a parent PRD is only `armed`, while a
  deferred default-branch vehicle remains, or while an owner/automation handoff
  is waiting for merge. `root-monitoring` keeps the root claimed;
  `owner-handoff` or `automation-handoff` may release the root only with the
  durable watch packet and `ledger_status=paused`. Ledger completion requires
  watch `complete`, parent closeout `closed`, and post-merge proof that GitHub
  closed the parent issue.
- `active` contains no worker that is merely done; every active row needs a real
  next check or root-owned closeout action.
- `autonomous` is empty, or every item was reclassified as non-actionable under
  the current authorization.
- `ready-next` is empty, or every remaining action was reclassified as
  `needs-owner`, `blocked`, or `deferred` with the missing authorization,
  decision, or follow-up.
- PRD-backed work with authorized pull-request delivery either records
  the published PR URL or records the exact blocker that prevents publication;
  do not mark it complete while authorized commit, push, or draft PR creation
  remains in `ready-next`. When `pr_closeout=merge-ready`, also record non-draft
  state and the resolved review policy. For `codex_review_policy=required`,
  record Codex review proof and discussion disposition, and do not mark it
  complete while current-head review preflight, a permitted request,
  existing-request wait, review-triggered fix, fresh-result wait, or PR-thread
  disposition remains in `ready-next`. For `codex_review_policy=skip`, record
  scoped owner evidence, keep review request/wait actions `not-applicable`, and
  resolve any already-known actionable feedback. For a default-branch GitHub whole-PRD
  closeout vehicle, merge-ready reporting requires `parent_prd_closeout=armed`,
  the parent ref, a `parent_closeout_head` equal to the current
  closeout-qualified SHA, a
  `parent_closeout_base` equal to the current `default_branch`, PR-body evidence,
  current live-body fingerprint matching that evidence, and a valid closeout
  watch. With no merge authority the watch must be `owner-handoff`; use
  `root-monitoring` only when the root has explicit merge authority and is the
  designated merger, and use `automation-handoff` only for an explicitly
  authorized event-driven monitor. Parent-source and ledger completion
  additionally require the PR merged, parent closeout `closed`, watch
  `complete`, and post-merge issue-closure proof.
  A non-default-base PR workstream may report merge-ready with
  `deferred-to-default-branch` only when its linked later closeout vehicle stays
  `active` or `ready-next`. Authorized `draft-only` workstreams and other
  excluded workstreams must record `not-applicable` with a reason. Never keep a
  duplicate review request in `ready-next` when a terminal result or active
  request exists for that head.
- When `pr_closeout=draft-only`, require validated draft publication and the
  canonical option-resolution evidence, record downstream
  ready/review/merge-ready gates and parent PRD
  closeout as `not-applicable` with reason `draft-only`, and allow completion at
  that requested state. A later owner instruction changes the canonical row to
  `pr_closeout=merge-ready`; resume at ready-for-review only after that update.
- For merge-ready closeout, verify the publication checkout is clean, accepted
  fixes are committed and pushed to the PR branch, and current CI belongs to the
  pushed head. With `codex_review_policy=required`, require GitStack or
  authenticated supplemental evidence to prove a terminal Codex result for that
  head, disposition unresolved review threads, and record request/result ids for
  reuse. With `codex_review_policy=skip`, require scoped owner evidence, no
  request/wait action, and disposition only already-known actionable feedback.
  For an applicable parent PRD, also verify the armed closeout head equals the
  current closeout-qualified head, the closeout PR still targets the current default branch,
  and the recorded PR-body evidence still contains the parent closing keyword.
  If any check fails, keep the ledger active,
  `ready-next`, or blocked instead of `complete`.
- `needs-owner` and `blocked` entries are explicitly non-Codex-actionable and
  include decision briefs, blockers, evidence, and minimum next actions.
- `deferred` contains only residual work with a linked or proposed
  owner-visible follow-up.
- `completed` records the final proof, source closeout state, integration
  method, publication state, ready-for-review state, review policy and evidence,
  applicable parent-PRD closeout state/head/PR-body evidence, closeout-watch and
  post-merge proof, publication checkout, caller checkout disposition, and
  worker lifecycle decision for each completed worker-backed item.
- Generated ignored artifacts and helper worktrees are either removed, retained
  for inspection with a reason, left only inside a helper worktree with an
  explicit lifecycle decision, or explicitly handed off.
- The recovery packet reflects the last source mutation and final current-state
  projection, or is explicitly `unavailable`; stale packets cannot support
  closeout.
- Runtime metrics contain root-scoped uncontaminated phase deltas,
  explicitly labeled interval deltas, or one `unavailable` row. Missing metrics
  never override otherwise valid closeout proof.
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

Reconciliation updates the current projection instead of appending a new claim
that contradicts stale current fields. Preserve historical `## Notes`, but
replace outdated source snapshots, gate rows, workstream delivery values,
active-worker lists, and current next actions. For every reconciliation, append
one dated note and record this compact result:

| Checked At | Sources Re-read | Current Projection Updated | Stale Values Removed | Remaining Actionable | Result |
| --- | --- | --- | --- | --- | --- |
| <time> | <source ids/URLs> | <sections/rows> | <values or none> | <count and refs> | pass|blocked |

After recording the result, refresh the recovery packet from the reconciled
projection and record only its changed sections and new fingerprint in normal
progress output.

Before setting the ledger `complete`, run the reconciliation after the last
source mutation and verify these invariants:

- no closed source is described as open or pending in a current-state field;
- no merged PR is described as draft, open, or merge-ready-only;
- no archived, integrated, abandoned, or handed-off worker remains active;
- every fallback records its GitStack workflow, primary connector attempt,
  authenticated `gh` fallback, and authority reuse;
- merge proof exists only when explicit merge authority exists;
- every default-branch whole-PRD closeout vehicle is merged with
  `parent_prd_closeout=closed`, `parent_closeout_watch=complete`, matching armed
  head/base/body history, and post-merge proof that the parent issue closed; no
  `armed` unmerged PR or `deferred-to-default-branch` vehicle remains
  outstanding;
  every authorized `draft-only` or otherwise excluded workstream records
  `not-applicable` with a reason;
- the current gate matrix, workstream rows, bucket membership, wave report,
  root status, and final note agree.

If any invariant fails, keep the ledger active or blocked and repair the
current projection before final status. Historical notes are evidence, not a
substitute for current-state reconciliation.

Releasing the active root before parent closure is a distinct handoff, not
ledger completion. It requires a fresh reconciliation, a complete
`owner-handoff` or explicitly authorized `automation-handoff` packet under
`## Parent Closeout Watch`, the same actionable packet in the owner-visible
final report, `ledger_status=paused`, and the PRD retained under `needs-owner`
or the named active monitor. Otherwise keep the root `claimed` and the watch
`root-monitoring` until the merge and actual parent closure are verified.
