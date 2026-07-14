# Ledger Template

Load this reference only when creating a new Codex Orchestrator ledger or when
the marker check in `ledger.md` classifies an existing ledger as legacy. Do not
load it for an existing ledger that passes that check.

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

`options.md` owns the six-column row schema and `%7C` evidence encoding. The
tables below project that contract into a newly created or migrated ledger.

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
Recovery packet content fingerprint: <sha256 from recovery-validation.md or none>
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
Parent Feature Spec: <issue ref or none>
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
`ledger_status=paused` and the parent Feature Spec under `needs-owner` or an active
monitor until post-merge proof shows the issue closed. Only then set this watch
to `complete` and parent closeout to `closed`.

## Recovery Packet

Packet version: 1
Status: fresh|stale|invalid|unavailable
Updated: <YYYY-MM-DD HH:MM TZ>
Projection fingerprint: <sha256 of ledger content before Notes, excluding this Recovery Packet, using recovery-validation.md canonical extraction>
Content fingerprint: <sha256 of packet derived fields, excluding status/timestamps/fingerprints, also recorded under Active Root>
Root: <root id>; claim=<status>; goal=<objective ref>; active_workers=<unique comma-separated worker ids or none>; parent_closeout_watch=<status/ref>
Current wave: <wave id/status>; current_workstreams=<ids>; next_action=<one bounded action or blocker>
Option resolution refs: session_rows=<unique comma-separated exact row_ids>; scoped_rows=<unique comma-separated exact current source/workstream row_ids or empty>; rows_fingerprint=<sha256 of exactly the referenced row union using recovery-validation.md>
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
fingerprints here; load `recovery-validation.md` before resume or recovery.

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
authority follow `spec-backed-delivery.md`. Gates follow `gates.md`. Keep only
the current session summary here; put full source contracts in Feature Specs, generated
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
| Delivery | delivery_mode=<local-only|pull-request|direct-commit>; delivery_source=<runtime-default|feature-level-inherited|issue-level-override|owner-instruction>; delivery_source_evidence=<scoped-option-row/source-ref|none>; branch_name=<exact branch|not-applicable>; current_pr_ref=<owner/repo#number|pending|not-applicable>; scope_transfer_ref=<issue:<NN>|not-applicable>; issue_mutation_transfer_ref=<issue:<NN>|not-applicable>; temporary_source_execution=<forbidden|owner-approved>; completion_proof_policy=<live-required|synthetic-accepted>; pr_shape=<single-pr|per-repo-pr|none>; closeout_mode=<feature-pr-closes-issue|repo-pr-closes-issue|direct-commit-closes-issue|local-done-move-after-proof|not-applicable>; integration_mode=<single-repo-pr|repo-pr|direct-commit|not-applicable>; publication_authority=<none|explicit-owner-authorization|spec-backed-pull-request|blocked>; pr_closeout=<merge-ready|draft-only|not-applicable>; codex_review_policy=<required|skip|not-applicable>; issue_mutation_authority=<none|pr-body-closeout-only|explicit-direct-mutation>; automation_authority=<none|explicit-owner-authorization>; automation_target=<source/workstream ref|none>; parent_spec_applicability=<required|deferred-vehicle|not-applicable>; parent_spec_applicability_reason=<whole-spec-final-pr|non-default-base|partial-pr|ad-hoc|local-tracker|no-parent|draft-only|other-reason>; parent_spec_closeout=<not-applicable|pending-review|pending-closeout|deferred-to-default-branch|armed|closed|blocked>; parent_spec_ref=<ref|none>; parent_closeout_vehicle=<pr-ref|pending|none>; parent_closeout_head=<sha|none>; parent_closeout_base=<branch|none>; default_branch=<branch|none>; pr_body_evidence=<url/fingerprint|none>; parent_closeout_watch=<not-applicable|root-monitoring|owner-handoff|automation-handoff|complete>; watch_evidence=<ref|none>; merge_authority=<none|explicit-owner-authorization>; merge_policy=<owner-approval|automatic-after-gates>; codex_review=<not-applicable|not-requested|requested|received|passed|skipped|blocked> |
| Codex review evidence | request_head=<sha|none>; request_object=<id/url|none>; checker_status=<not-requested|acknowledged|pending|clean|findings|stale|error>; wait_record=<pr-ref@head|none|not-applicable>; wait_profile_pr=<pr-ref|none|not-applicable>; wait_profile=<standard|extended|not-applicable>; wait_budget_minutes=<15|30|not-applicable>; wait_started_at=<timestamp|none|not-applicable>; wait_deadline=<timestamp|none|not-applicable>; wait_elapsed_seconds=<number|none|not-applicable>; wait_state=<not-started|active|monitoring-required|terminal|not-applicable>; result_head=<sha|none>; result_kind=<formal-review|provider-comment|clean-reaction|none>; result_object=<id/url|none>; provider=<verified identity|none>; terminal=<clean|findings|error|none>; disposition=<status/evidence> |
| GitHub routing | workflow_skill=<gitstack skill>; primary_transport=connector; operation=<operation>; fallback=<unused|gh>; fallback_reason=<none|connector-unavailable|capability-unsupported|transport-failure>; evidence=<failure/result>; authority_reused=<authority> |
| Integration | baseline=<commit/wave>; resync_state=<synced|needs-resync|replaced|root-owned>; publication_checkout=<checkout or not-applicable>; caller_checkout_policy=<policy> |
| Gates / proof | <required gates and current proof target> |

For every active row, `parent_spec_applicability=required` requires a parent ref
and one of `pending-review`, `pending-closeout`, `armed`, or `blocked`.
`parent_spec_applicability=deferred-vehicle` requires reason `non-default-base`,
state `deferred-to-default-branch`, and a linked later default-branch
`parent_closeout_vehicle` or `pending` vehicle-selection action in `ready-next`.
`parent_spec_closeout=armed` is valid only when `parent_closeout_head` equals the
current closeout-qualified SHA (reviewed for `required`, fully validated for
`skip`), `parent_closeout_base` equals the current `default_branch`,
and `pr_body_evidence` proves the parent closing keyword is present; none of
those proof fields may be `none`.
An unmerged `armed` row also requires `parent_closeout_watch=root-monitoring`,
`owner-handoff`, or `automation-handoff` with matching watch evidence.
`root-monitoring` additionally requires explicit merge authority and the root as
the designated merger; `merge_authority=none` requires `owner-handoff`, while
`automation-handoff` requires an explicitly authorized event-driven monitor.
`parent_spec_applicability=not-applicable` requires
`parent_spec_closeout=not-applicable` plus a concrete applicability reason.
Reconciliation must reject unsupported `armed` or unjustified
`not-applicable` claims before dispatch, mutation, recovery, or closeout.

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
  review policy/evidence, parent Feature Spec closeout state/closeout-qualified head/PR-body evidence when
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

Load `recovery-validation.md` before recovery. Load `runtime-efficiency.md`
before multi-wave delta transport or exact metric capture. One `unavailable`
row is sufficient when counters are absent.

## Notes

- <dated orchestration notes and durable context>
```
