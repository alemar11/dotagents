# Ledger Template

Load this reference only when creating a new Codex Orchestrator ledger. Never
use it to reinterpret or overwrite an existing invalid ledger.

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
tables below project that contract into a newly created ledger.

### Session Rows

| row_id | scope_id | field | value | source | evidence |
| --- | --- | --- | --- | --- | --- |
| `session:<field>` | `session` | <Session Registry field from options.md> | <canonical value> | `default`, `authorized-user-instruction`, `runtime-capability`, `runtime-derived`, or `project-layout-config` | <instruction/tool ref or none> |
| `session:repository_layout` | `session` | `repository_layout` | `single-repository`, `monorepo`, or `multi-repository-workspace` | `project-layout-config`, `runtime-derived`, or `authorized-user-instruction` | <project-layout path, repo evidence, or instruction ref> |

### Scoped Rows

| row_id | scope_id | field | value | source | evidence |
| --- | --- | --- | --- | --- | --- |
| `source:<Source ID>:tracked_work_item_update_permission` | `source:<Source ID>` | `tracked_work_item_update_permission` | <canonical value> | `default`, `authorized-user-instruction`, or `runtime-capability` | <instruction/source/tool ref or none> |
| `<scope_id>:<field>` | `workstream:<id>` | <Per-Workstream Registry field from options.md> | <canonical value> | `default`, `authorized-user-instruction`, `source-contract`, `runtime-capability`, or `runtime-derived` | <instruction/source/tool ref or none> |

Every applicable source row must be projected into its corresponding
discovery-source row, and every workstream row into its workstream ledger row.
Discovery sources carry only `tracked_work_item_update_permission`; full authority and
delivery options begin at workstream registration. Never reuse another scope's
authority or delivery value. Keep every `row_id` unique across both option
tables, restrict row IDs to `[A-Za-z0-9:_-]+` with no commas, and encode a
literal `|` in evidence data as `%7C`.

## Discovery Sources

| Source ID | Kind | Path/Query/URL | Last Checked | Cursor/Fingerprint | Item Key Rule | tracked_work_item_update_permission | Suppression Rule |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ds-001 | markdown, github-issue, github-pr, ci, todo, ledger | <path/query/url> | <time> | <etag/sha/cursor/checksum> | <stable id rule> | read-only, propose-updates-only, or apply-updates | <owner/date/reason/source fingerprint> |

`tracked_work_item_update_permission` uses the canonical option values.

## Active Root

Status: claimed|stale|released|takeover-recorded
Root ID: <task id, session id, or root descriptor>
Root surface: codex-app-task|cli|unknown
Goal mode: active|unavailable|not-applicable
Goal objective: <goal text or ledger fallback objective>
Goal fallback reason: <none or why /goal/runtime goal tool was unavailable>
Started: <YYYY-MM-DD HH:MM TZ>
Last Progress Read: <YYYY-MM-DD HH:MM TZ>
Next Root Check: action=<monitor-thread|send-correction|dispatch-feature-spec|reconcile-feature-spec|owner-action|none>; target=<visible-thread-id|feature-spec-ref|owner-decision-ref|none>; due_at=<RFC3339|now|event-ref|none>
existing_orchestrator_session_takeover_policy: ask-authorized-user-before-takeover|take-over-only-if-existing-ledger-is-stale
Scoped merge option refs: <exact workstream pull_request_merge_permission/pull_request_merge_confirmation row_ids or none>
parent_closeout_watch: not-applicable|root-monitoring|owner-handoff|automation-handoff|complete
Parent closeout watch evidence: <ledger section/fingerprint plus owner-visible handoff or automation id, or none>
Claimed repo realpaths:
- <absolute realpath or unknown>; source=<scope evidence>
Claimed source ids:
- <source id/ref>
Active workers:
- worker_id=<stable id>; actual_execution_location=<background-codex-subagent|visible-codex-app-task>; workstream_ids=<comma-separated ids>
- none
Nested internal subagents are reported under their parent worker evidence and
do not become separate root workstream assignments unless the root explicitly
registers them.
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

| wait_record | wait_profile_pr | request_head | request_object | wait_profile | wait_budget_minutes | wait_started_at | wait_deadline | wait_state | observation_fingerprint | last_transition_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <owner/repo#number@head-sha> | <owner/repo#number> | <head-sha> | <id/url> | <standard|extended> | <15|30> | <timestamp> | <timestamp> | <active|monitoring-required|terminal> | <sha256> | <timestamp> |

When multiple workstreams map to the same PR and head, every one must carry
the same `wait_record` and an exact projection of that row. Update the registry
row first, then refresh all mapped projections. Retain the PR-level extended
profile across later heads as described by the review gate, while using a new
row and deadline for each new head. `observation_fingerprint` is the stable
GitStack review observation fingerprint; update the row and
`last_transition_at` only when that fingerprint, the wait state, or a deadline
tier changes. Derive elapsed time from `wait_started_at` and the current clock
for reports only; it is not persisted controller state.

## Feature Spec Thread Registry

This derived registry is required when
`visible_app_task_permission=granted-by-authorized-user`. Keep exactly one row
per implementation-eligible Feature Spec selected for dispatch in the current
wave and exactly one active visible thread per row. Queued, dependency-blocked,
or capacity-deferred Specs enter the registry when their dispatch wave starts.
Multiple generated issues, repositories, worktrees, and PRs for the same Spec
remain in that row. The exact source title is also the required live thread
title. Every row also owns the current thread Goal projection. Keep
`thread_goal_mode=pending` only while `state=created`; do not start assigned
work until the thread reports `active` or an exact unavailable-tool fallback.
The thread, not the root, owns Goal updates and completion. A recovery packet
may preserve `created`/`pending`, but its next action must monitor that thread
and must not resume assigned work.

Ledger transport encodes title delimiters without changing the title itself:
encode `%` as `%25`, then `|` as `%7C`, `;` as `%3B`, and `=` as `%3D` in
`feature_spec_title` and `live_thread_title` cells or token values. Decode those
sequences in reverse order (`%3D`, `%3B`, `%7C`, then `%25`) before setting or
comparing the visible thread title. Bare delimiter characters are invalid in
the stored title fields.

| feature_spec_ref | feature_spec_title | visible_thread_id | live_thread_title | workstream_ids | repository_refs | pull_request_refs | lifecycle_owner | codex_review_poll_owner | state | last_read | drift | corrective_message_evidence | thread_state_evidence | thread_goal_mode | thread_goal_status | thread_goal_dispatch_objective_sha256 | thread_goal_reported_objective_sha256 | thread_goal_evidence | thread_goal_missing_tool |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <canonical ref> | <transport-encoded exact canonical title> | <thread id> | <transport-encoded exact canonical title> | <comma-separated ids> | <comma-separated repo refs> | <comma-separated PR refs or pending> | visible-feature-spec-thread | visible-feature-spec-thread | <created|implementing|validating|draft-pr|review-polling|fixing-review|ci|marking-ready|merge-ready|target-complete|blocked|needs-owner|replaced> | <time> | <none|description> | <message ref or none> | <current list/read-thread tool ref and fingerprint> | <pending|active|unavailable> | <pending|active|complete|blocked|not-applicable> | <root-computed 64-lowercase-hex> | <thread-reported 64-lowercase-hex or pending> | <goal tool, initial message, or current thread-read ref> | <runtime-goal-tool|not-applicable> |

Reject duplicate Feature Spec refs, one thread id mapped to multiple Feature
Specs, a live title that differs from the exact Feature Spec title, a
Feature-Spec-backed active workstream assigned outside its registry thread, or
a `current-orchestrator-session`/background-only implementation or review row.
A non-`created` row with a pending Goal, an active Goal mode with an
inapplicable status, an unavailable Goal mode without an exact fallback, or a
root-owned Goal update is also invalid.
Use `target-complete` when a selected non-merge-ready delivery target is fully
reached. An active Goal may be `complete` only with `merge-ready` or
`target-complete`, and a Goal may be `blocked` only with `blocked` or
`needs-owner` lifecycle state.
A replacement first records the prior thread lifecycle, leaves only one active
thread for the Spec, and updates this row without changing the Spec key.

## Parent Closeout Watch

Status: not-applicable|root-monitoring|owner-handoff|automation-handoff|complete
Parent Feature Spec: <issue ref or none>
Closeout PR: <PR ref or pending>
Review policy: <required-on-current-pull-request-head|explicitly-skipped-by-authorized-user|not-needed-for-selected-delivery-target>
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
Feature Spec threads: <feature-spec-ref>=<visible-thread-id>, or none
Current wave: <wave id/status>; current_workstreams=<ids>; next_action=<monitor-thread|send-correction|dispatch-feature-spec|reconcile-feature-spec|owner-action|none>; next_target=<visible-thread-id|feature-spec-ref|owner-decision-ref|none>; next_due_at=<RFC3339|now|event-ref|none>
Option resolution refs: session_rows=<unique comma-separated exact row_ids>; scoped_rows=<unique comma-separated exact current source/workstream row_ids or empty>; rows_fingerprint=<sha256 of exactly the referenced row union using recovery-validation.md>
Repo checkpoints:
- <repo realpath>; head=<sha>; worktree=<stable fingerprint of status --short>; branch=<name or detached>
Source checkpoints:
- <registered source item id from Workstreams>; fingerprint=<etag/sha/checksum/head>; state=<ledger state>
Workstream checkpoints:
- <workstream id>; source=<registered source item id>; state=<ledger state>; feature_spec_ref=<canonical ref|not-applicable>; feature_spec_title=<transport-encoded exact title|not-applicable>; delivery_permission_source_issue_ref=<issue:<NN>|not-applicable>; issue_update_permission_source_issue_ref=<issue:<NN>|not-applicable>; delivery_evidence_fingerprint=<sha256 or not-applicable>; issue_mutation_evidence_fingerprint=<sha256 or not-applicable>
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
worker_allowed_actions: <explicit action list from worker.md>
visible_app_task_permission: not-requested|granted-by-authorized-user|denied-by-authorized-user
feature_spec_thread_assignment: required|not-applicable
unmanaged_git_worktree_fallback_permission: not-granted|granted-by-authorized-user
repository_layout: single-repository|monorepo|multi-repository-workspace
workstream_repository_layout: single-repository|monorepo|multi-repository-workspace
pull_request_count_strategy: one-pull-request-total|one-pull-request-per-repository|no-pull-request
target_branch_name: <exact branch|not-applicable>
delivery_permission_source_issue_ref: <issue:<NN>|not-applicable>
issue_update_permission_source_issue_ref: <issue:<NN>|not-applicable>
issue_completion_method: feature-pull-request-closing-keyword|repository-pull-request-closing-keyword|final-commit-closing-keyword|move-local-issue-to-done-after-proof|no-issue-completion
internal_subdelegation: allowed-within-assigned-scope
worker_ledger_mutation: forbidden
visible_worker_lifecycle_owner: root
internal_subagent_lifecycle_owner: parent-thread
Visible Feature Spec thread title format: <exact canonical Feature Spec title>
Root capability snapshot: filesystem=<profile/evidence>; network=<available|restricted|unknown>; gh_auth=<available|unavailable|not-required>; codex_cli=<available|unavailable|not-required>; autoreview=<available|unavailable|reroute-to-root>; checked_at=<time/evidence>
GitHub workflow skill: <gitstack skill or none>
GitHub primary transport: connector
GitHub fallback: fallback_status=<unused|used>; transport=<none|gh>; reason=<none|connector-unavailable|capability-unsupported|transport-failure>; operation=<operation or none>; evidence=<failure or none>; authority_reused=<authority or none>; result=<result or none>

Worker fields follow `worker.md`. Delivery and issue-update permissions follow
`spec-backed-delivery.md`. Gates follow `gates.md`. Keep only
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
| Feature Spec thread | feature_spec_ref=<canonical ref|not-applicable>; feature_spec_title=<transport-encoded exact canonical title|not-applicable>; feature_spec_thread_assignment=<required|not-applicable>; visible_thread_id=<id|not-applicable>; lifecycle_owner=<visible-feature-spec-thread|bounded-worker|root>; codex_review_poll_owner=<visible-feature-spec-thread|assigned-worker|not-applicable>; root_implementation_fallback=<forbidden|not-applicable>; thread_goal_mode=<pending|active|unavailable|not-applicable>; thread_goal_status=<pending|active|complete|blocked|not-applicable>; thread_goal_dispatch_objective_sha256=<root-computed 64-lowercase-hex|not-applicable>; thread_goal_reported_objective_sha256=<thread-reported 64-lowercase-hex|pending|not-applicable>; thread_goal_evidence=<tool/thread ref|not-applicable>; thread_goal_missing_tool=<runtime-goal-tool|not-applicable> |
| Repo / execution location | <repo>; <current-orchestrator-session|background-codex-subagent|visible-codex-app-task>; worker=<id or root> |
| Worker evidence | visible_app_task_permission=<not-requested|granted-by-authorized-user|denied-by-authorized-user>; actual_execution_location=<current-orchestrator-session|background-codex-subagent|visible-codex-app-task>; authorization_state=<authorized-by-invocation|authorized-user-consented|not-authorized>; status=<used|unavailable|attempt-failed|root-owned-fallback>; evidence=<tool/session/failure>; nested_subagents=<ids/scopes/outcomes/topology|none>; parallelism=<parallel|sequential|root-owned|simulated>; capability_snapshot=<filesystem/network/gh_auth/codex_cli/autoreview/checked_at evidence> |
| Wave / status | <wave>; active; last_read=<time>; next_check=<time/action> |
| Objective | <one concrete outcome> |
| Scheduling | parallelization=<independent|depends-on|blocks|root-integrated>; dependency_ids=<refs|none>; blocked_issue_ids=<refs|none>; dependency_reason=<reason|none>; dependency_proof=<evidence|pending|none> |
| Delivery | change_delivery_target=<validated-changes-left-uncommitted|local-commit-created-without-pushing|changes-pushed-to-target-branch-without-pull-request|validated-draft-pull-request-published|pull-request-ready-for-merge-but-not-merged>; delivery_decision_origin=<safe-default-for-ad-hoc-work|inherited-from-feature-spec|overridden-by-implementation-issue|specified-by-authorized-user>; delivery_decision_origin_evidence=<scoped-option-row/source-ref|none>; target_branch_name=<exact branch|not-applicable>; target_pull_request_ref=<owner/repo#number|pending|not-applicable>; delivery_permission_source_issue_ref=<issue:<NN>|not-applicable>; issue_update_permission_source_issue_ref=<issue:<NN>|not-applicable>; temporary_source_execution_permission=<not-granted|granted-by-authorized-user>; completion_evidence_policy=<require-live-system-evidence|allow-simulated-evidence-by-authorized-user-exception>; pull_request_count_strategy=<one-pull-request-total|one-pull-request-per-repository|no-pull-request>; issue_completion_method=<feature-pull-request-closing-keyword|repository-pull-request-closing-keyword|final-commit-closing-keyword|move-local-issue-to-done-after-proof|no-issue-completion>; change_delivery_permission=<not-required-for-uncommitted-changes|not-granted|granted-for-selected-target>; delivery_gate_status=<ready|blocked|not-applicable>; delivery_allowed_actions=<canonical action list>; codex_review_requirement=<required-on-current-pull-request-head|explicitly-skipped-by-authorized-user|not-needed-for-selected-delivery-target>; issue_update_permission=<no-issue-changes|pull-request-closing-keyword-only|direct-issue-updates-explicitly-authorized>; scheduled_automation_change_permission=<not-granted|granted-by-authorized-user>; automation_target=<source/workstream ref|none>; parent_spec_applicability=<required|deferred-vehicle|not-applicable>; parent_spec_applicability_reason=<whole-spec-final-pr|non-default-base|partial-pr|ad-hoc|local-tracker|no-parent|draft-pull-request-target|other-reason>; parent_spec_closeout=<not-applicable|pending-review|pending-closeout|deferred-to-default-branch|armed|closed|blocked>; parent_spec_ref=<ref|none>; parent_closeout_vehicle=<pr-ref|pending|none>; parent_closeout_head=<sha|none>; parent_closeout_base=<branch|none>; default_branch=<branch|none>; pr_body_evidence=<url/fingerprint|none>; parent_closeout_watch=<not-applicable|root-monitoring|owner-handoff|automation-handoff|complete>; watch_evidence=<ref|none>; pull_request_merge_permission=<not-granted|granted-for-named-pull-request>; pull_request_merge_confirmation=<ask-authorized-user-after-checks|merge-automatically-after-checks>; codex_review=<not-applicable|not-requested|requested|received|passed|skipped|blocked> |
| Codex review evidence | request_head=<sha|none>; request_object=<id/url|none>; checker_status=<not-requested|acknowledged|pending|clean|findings|stale|error>; wait_record=<pr-ref@head|none|not-applicable>; wait_profile_pr=<pr-ref|none|not-applicable>; wait_profile=<standard|extended|not-applicable>; wait_budget_minutes=<15|30|not-applicable>; wait_started_at=<timestamp|none|not-applicable>; wait_deadline=<timestamp|none|not-applicable>; wait_state=<not-started|active|monitoring-required|terminal|not-applicable>; observation_fingerprint=<sha256|none|not-applicable>; last_transition_at=<timestamp|none|not-applicable>; result_head=<sha|none>; result_kind=<formal-review|provider-comment|clean-reaction|none>; result_object=<id/url|none>; provider=<verified identity|none>; terminal=<clean|findings|error|none>; disposition=<status/evidence> |
| GitHub routing | workflow_skill=<gitstack skill>; primary_transport=connector; operation=<operation>; fallback=<unused|gh>; fallback_reason=<none|connector-unavailable|capability-unsupported|transport-failure>; evidence=<failure/result>; authority_reused=<authority> |
| Integration | baseline=<commit/wave>; resync_state=<synced|needs-resync|replaced|root-owned>; result_checkout_path=<checkout or not-applicable>; starting_checkout_branch_handling=<policy> |
| Gates / proof | <required gates and current proof target> |

For every active row, `parent_spec_applicability=required` requires a parent ref
and one of `pending-review`, `pending-closeout`, `armed`, or `blocked`.
`parent_spec_applicability=deferred-vehicle` requires reason `non-default-base`,
state `deferred-to-default-branch`, and a linked later default-branch
`parent_closeout_vehicle` or `pending` vehicle-selection action in `ready-next`.
`parent_spec_closeout=armed` is valid only when `parent_closeout_head` equals the
current closeout-qualified SHA (reviewed for the required path, fully validated
for the explicit-skip path), `parent_closeout_base` equals the current `default_branch`,
and `pr_body_evidence` proves the parent closing keyword is present; none of
those proof fields may be `none`.
An unmerged `armed` row also requires `parent_closeout_watch=root-monitoring`,
`owner-handoff`, or `automation-handoff` with matching watch evidence.
`root-monitoring` additionally requires explicit merge authority and the root as
the designated merger; `pull_request_merge_permission=not-granted` requires `owner-handoff`, while
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
  disposition, Feature Spec thread ref/id/exact title and review-poll ownership
  when applicable, worker lifecycle decision, generated ignored artifacts
  removed/retained/left in helper worktree>

### released

- workstream_id=<id>; source_id=<id/ref>; <repo/version/tag/date, release gate proof, release action or
  deploy proof>

## Wave Reports

Record the canonical startup option snapshot before dispatch:
`visible_app_task_permission`, `unmanaged_git_worktree_fallback_permission`, and
`existing_orchestrator_session_takeover_policy`, with their option-resolution evidence. In a
Codex App session, also record the App
task id/title for every newly created worker, integration, or publication
worktree. Record each non-blocking execution report with its source items,
actual worker surfaces, orchestrator-chosen split for the current wave,
worker action lists, delivery target, stop conditions, and any owner-authorized
option changes.

When visible task permission is granted, each wave report must also map every
implementation-eligible Feature Spec ref and exact title to its one visible
thread id, list all child workstream and repository/PR refs under that mapping,
name `visible-feature-spec-thread` as lifecycle and review-poll owner, and prove
the root did no implementation or review work. Include each thread's Goal
mode/status/evidence and prove no work began while its Goal was pending. Thread
count is derived from the Feature Spec set; do not record a user cap.

The execution report is not an approval prompt. Continue later waves while they
stay inside the recorded source items, canonical option snapshot, worker
actions, delivery target, and stop conditions. If a required option is unresolved
or live runtime capacity cannot safely represent the planned wave, work may
remain in the ledger, but dispatch must not start until the option row or
runtime evidence is valid.

Do not record a newly created raw Git worktree as the publication checkout in a
Codex App session unless App task/worktree creation was reported as missing,
failed, or unsuitable and the session row is
`unmanaged_git_worktree_fallback_permission=granted-by-authorized-user`. Keep the managed-worktree failure as
runtime evidence only. This restriction does not apply in CLI-only sessions.

| Wave | Started | Finished | Sources Scanned | Items Processed | Execution Report | Remaining Actionable | Blockers | Ledger Mutations | Source Mutations | Next Scan/Check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | <time> | <time> | <source ids> | <count> | <reported; startup baseline; worker split; action lists; delivery target; stop conditions; edits> | <count> | <summary> | <status changes> | <file/github updates or proposed updates> | <time/action> |

Record worker evidence every time delegation is used or attempted. Include
`visible_app_task_permission`, `actual_execution_location`, authorization state,
tool or session id when one exists, nested subagent topology, fallback reason,
and whether execution was parallel, sequential, root-owned, or simulated.
`root-owned-fallback` is invalid for Feature Spec implementation or review when
visible task permission is granted.

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
