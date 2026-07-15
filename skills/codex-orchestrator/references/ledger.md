# Ledger Reference

Use ledgers to persist portfolio scope, active workstreams, gate overrides, and
orchestration state between Codex sessions.

## Ledger Resolution And Validation

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

Classify an existing ledger from that file alone by parsing Markdown structure,
not by substring search. Ignore headings inside backtick or tilde fenced code,
including fences indented by up to three spaces, and normalize up to three
leading spaces on ATX headings before structural comparison. Current-format
ledgers use ATX headings only; any Setext underline syntax outside fences is
invalid. Keep current-format ledgers free of raw HTML:
outside fences, any HTML comment marker or line whose first non-space character
is `<` is also invalid instead of treating raw-block
contents as structure. Require the first non-blank line to be one non-empty
`# <name> Maintainer Ledger` heading and allow no other level-1 heading. Before
`## Scope`, require exactly one non-empty
`Last updated:` line, one non-empty `Owner:` line, and one `Status:` line whose
value is `active`, `paused`, `blocked`, `complete`, `released`, or `archived`.

Require every heading below exactly once, outside fenced code, with the shown
nesting and order. Allow no other level-2 or level-3 heading in the ledger:
`### Session Rows` and `### Scoped Rows` belong only to
`## Option Resolution`, while every workstream status heading belongs only to
`## Workstreams`. Within `## Recovery Packet`, also require exactly one
`Packet version: 1`, `Option resolution refs:`, and
`References to load next:` line. Text copied into `## Notes` never satisfies an
earlier marker; an unfenced level-2 or level-3 heading there is unexpected or
duplicate. A missing, duplicate, out-of-order, or wrongly nested marker—or a
missing or invalid header field—makes the ledger invalid.

```text
## Scope
## Option Resolution
### Session Rows
### Scoped Rows
## Discovery Sources
## Active Root
## Codex Review Wait Registry
## Feature Spec Task Registry
## Parent Closeout Watch
## Recovery Packet
Packet version: 1
Option resolution refs:
References to load next:
## Worker And Delivery References
## Gate Policy
## Workstreams
### active
### autonomous
### needs-owner
### ready-next
### blocked
### ignored-or-suppressed
### deferred
### completed
### released
## Wave Reports
## Runtime Metrics
## Notes
```

The three Recovery Packet markers above may have packet data between them, but
they must remain inside `## Recovery Packet` and in the displayed relative
order.

When the structure check fails, stop as `needs-owner` and report the resolved
ledger path plus missing, duplicate, out-of-order, or invalid markers. Do not
load `ledger-template.md`, reinterpret fields, or reconstruct the ledger.

If the resolved ledger file does not exist, load `ledger-template.md` and create
it before discovery. Fill known fields, use `tbd` for unknown owner or
repository metadata, set `Status: active`, and add a dated note summarizing the
owner request and initial task sources. Do not load the template for an existing
ledger that passes the marker check above.

## Ownership

- The orchestrator reads and writes the ledger.
- Worker tasks and subagents do not edit ledgers.
- Workers report status, proof, blockers, and next actions to the orchestrator.
- When `visible_app_task_permission=granted-by-authorized-user`, the ledger
  groups every implementation-eligible Feature Spec and all of its child
  workstreams under exactly one visible task. The root records and monitors
  that mapping but does not execute implementation, integration, validation,
  PR mutation, Codex-review request/polling, feedback or CI fixes, or mark-ready
  work for those Specs.
- Each orchestrator-created visible task owns its assignment-scoped Goal.
  The root records and monitors the reported Goal state but never creates,
  updates, or completes that Goal on the task's behalf.
- Preserve historical notes that explain owner decisions, suppressions, and
  release state.
- The orchestrator records worker lifecycle decisions: `integrated`,
  `retained-for-inspection`, `abandoned`, or `handoff-pending`.

## Controller State Reconciliation

Keep one authoritative owner for each current-state fact:

- `## Active Root` owns the root claim, root action, and run-wide serial
  caller-checkout branch-assignment registry;
- `## Feature Spec Task Registry` owns visible-task identity, Feature Spec
  assignment, lifecycle state, task Goal projection, drift, and the canonical
  current cross-Spec dependency-edge projection;
- `## Workstreams` owns work state, delivery state, and the projection of its
  assigned task and review wait;
- `## Codex Review Wait Registry` owns review timing, stable observations, and
  wait transitions; and
- `## Recovery Packet`, active-worker lists, wave reports, and commentary are
  derived projections, never independent authorities.

Reconcile in one deterministic controller pass. Read the authoritative
sections into one in-memory snapshot, derive all dependent projections from
that snapshot, verify the invariants below, and apply the changed current-state
sections as one ledger patch. Append historical notes only after the current
projection agrees. Do not patch an active-worker list, workstream, wait row,
recovery field, or next action independently and leave the ledger split across
controller cycles.

For `serial-caller-checkout-branches`, append the Feature Spec, repository, and
target branch to `Serial caller-checkout branch assignments` before the root
switches the caller checkout. The `(feature_spec_ref, repository_ref)` row is
immutable except for `state`, and a `(repository_ref, target_branch)` pair may
belong to only one Feature Spec for the entire orchestration run. Retain
completed and blocked rows after their workstreams leave every active or queued
section; recovery and later dispatches must validate against the full registry.
Keep the row `assigned` throughout `branch-prepared` and `task-active`. Change
it to `completed` only in the same controller reconciliation that records a
verified `restored` lane, or to `blocked` with a blocked lane. Neither terminal
state may be prepared or dispatched again.

The stored `observation_fingerprint` hashes the stable GitStack review
observation together with the verified base ref and merge-base SHA. That hash
plus the review revision tuple
`(PR ref, request_head, request_base_ref, request_merge_base)` is the review
transition identity.
Persist the first observation, then update review rows, transition timestamps,
recovery fingerprints, notes, metrics, and owner commentary only when the
fingerprint, checker/wait state, request revision/object, terminal evidence, or
deadline tier changes. A changed base ref or merge base invalidates the prior
wait and result even when the head is unchanged; movement of a base tip that
leaves the merge base unchanged does not. Unchanged intermediate waiter
observations are no-ops:
do not rewrite the ledger, advance `Last Progress Read` or
`last_transition_at`, append a progress note, or emit progress commentary
merely because another poll occurred. When a complete bounded waiter exits by
timeout with the same fingerprint, the controller may perform one scheduling
write for the next `due_at`; update only Active Root plus its Recovery Packet
projection and do not present that scheduling write as work progress.
Elapsed time is derived from the persisted start/deadline timestamps only when
reporting and is never persisted as mutable controller state.
Released historical notes and bucket rows may retain their original head-only
review wording, but no active wait row, active workstream projection, or current
Recovery Packet may reuse that legacy evidence.

`Next Root Check` is structured as
`action=<value>; target=<value>; due_at=<value>` and must equal the Recovery
Packet `next_action`, `next_target`, and `next_due_at`. Use RFC 3339 timestamps,
`now`, a delimiter-safe event ref, or `none`; do not persist a mutable countdown.
Allowed actions are
`monitor-task`, `send-correction`, `dispatch-feature-spec`,
`reconcile-feature-spec`, `owner-action`, and `none`:

- `monitor-task` targets one active visible task with `drift=none` when it
  has a registry row; a created task whose Goal is pending must use this
  action until Goal establishment resolves;
- `send-correction` targets one active registry task with non-`none` drift;
- `dispatch-feature-spec` targets an eligible Feature Spec not yet active in
  the registry;
- `reconcile-feature-spec` targets an existing registry Feature Spec ref;
- `owner-action` targets a recorded owner-decision ref; and
- `none` requires `target=none` and `due_at=none`; every other action requires
  a non-`none` due value.

Root actions never contain implementation, review request, review polling,
feedback-fix, CI-fix, PR mutation, or mark-ready work in mandatory visible
Feature Spec task mode. A stale or unstructured root action makes the
current projection invalid; repair it before dispatch, recovery, or closeout.

The controller has a hard `spec_task_cap=3`; this is not a user option. Before
each dispatch, count unique nonterminal Feature Spec refs across every current
worker surface, compute the remaining slots, and select no more than that many
eligible Specs. In `serial-caller-checkout-branches`, use a cap of one. Record
`active_spec_task_count`, `eligible_spec_count`,
`selected_spec_task_count`, and every capacity- or dependency-deferred Spec
with its reason in the wave report. A blocked or owner-waiting task releases a
slot only after its worker is actually handed off or released and its registry
row moves to a released terminal state such as `replaced`; changing only the
workstream bucket does not free capacity.

Cross-Spec dependency rows project authored Feature Spec edges and never infer
permission to stack. `upstream-merged` uses depth one and dispatches only after
merge proof. `upstream-merge-ready-head` uses depth two and is valid only for
one identical `owner/repo`; freeze its upstream PR, branch, head, base ref, and
merge base before downstream dispatch. Keep at most one unresolved early edge
per downstream Spec, and never let a Spec be both the downstream and upstream
of unresolved early edges at once. The downstream remains nonterminal through
`awaiting-upstream-merge` and `resyncing`; only current post-merge
reconciliation can change the edge to `satisfied`. Bind every mutable row to a
fresh source/PR/task projection fingerprint during recovery; a released
`satisfied` row may retain immutable completion evidence. These edge rows are
distinct from intra-Spec implementation-issue `dependency_ids`.

Reject a controller snapshot when any of these invariants fails:

- more than three unique nonterminal Feature Spec executions are live across
  root, background, and visible-task surfaces; count `blocked` and
  `needs-owner` while their worker remains live, but not released
  `merge-ready`, `target-complete`, or `replaced` tasks;
- in mandatory visible Feature Spec task mode, Active Root visible workers
  are not exactly the active registry task assignments, or Recovery Packet
  `active_workers` is not the complete Active Root worker set;
- `implementation_checkout_strategy=serial-caller-checkout-branches` has more
  than one active Feature Spec task, an active task outside the caller checkout,
  a repository/target-branch pair reused by a different Feature Spec, a missing original-branch
  baseline, or a `dispatch-feature-spec` action before the prior task reached
  its complete target and the original branch was restored;
- a registry task, active workstream task assignment, or recovery task
  mapping disagrees about Feature Spec identity or lifecycle owner;
- a visible task advances beyond `created` while its Goal is pending, a
  pending Goal has a non-monitor next action, its
  Goal state lacks root-readable evidence, or its Goal fallback does not name
  the unavailable runtime surface and exact objective;
- a dependency edge is duplicated, cyclic, self-referential, cross-repository
  for `upstream-merge-ready-head`, deeper than two, has more than one unresolved
  early edge for the same downstream Spec, or lacks the state-specific frozen
  upstream and downstream evidence defined by the ledger template;
- a terminal wait row coexists with an active/pending workstream review
  projection, or a non-terminal wait row coexists with terminal evidence;
- workstreams sharing a PR revision disagree with the single wait row, head,
  base ref, merge base, observation fingerprint, deadline, or transition
  timestamp;
- a complete Goal lacks `merge-ready` or `target-complete` lifecycle state, a
  blocked Goal lacks `blocked` or `needs-owner`, or live task Goal evidence
  differs from the authoritative dispatch objective/state;
- a root owns implementation or review for a mandatory visible-task Feature
  Spec; or
- Active Root and Recovery Packet next action/target projections differ or
  violate the action predicates above.

## Active Root Claims

Before creating workers, starting root-owned implementation outside mandatory
Feature Spec task mode, or mutating source
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
- `tracked_work_item_update_permission`: `read-only` means do not mutate the
  source item, `propose-updates-only` means draft the update without applying
  it, and `apply-updates` means apply authorized source updates.
- `resync_state`: `synced` means worker state matches accepted integrated work,
  `needs-resync` means worker state must be reconciled, `replaced` means a new
  worker took over or, outside mandatory mode, a root flow took over, and
  `root-owned` means root owns integration or
  follow-up outside mandatory Feature Spec task mode. `root-owned` is invalid
  for implementation or review of a Feature Spec whose visible-task mode is
  active.
- `active_root_status`: `claimed` means this root currently owns the portfolio
  source graph, `stale` means the claim missed the recorded ledger check window,
  `released` means closeout completed or a durable parent-closeout handoff
  transferred the remaining watch while the ledger stayed `paused`, and
  `takeover-recorded` means a new root explicitly recorded a takeover from a
  stale prior root or after authorized-user approval.
- `existing_orchestrator_session_takeover_policy`:
  `ask-authorized-user-before-takeover` requires an explicit decision, while
  `take-over-only-if-existing-ledger-is-stale` permits takeover only after the recorded
  stale-read note and takeover note are present.
- `pull_request_merge_permission`: `not-granted` by default or
  `granted-for-named-pull-request` for the named PR or PR set.
- `pull_request_merge_confirmation`: `ask-authorized-user-after-checks` by
  default or `merge-automatically-after-checks` when the explicit merge instruction waives another
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
and gate values are owned by `worker.md`, `spec-backed-delivery.md`, and
`gates.md`.
Option fields and values follow `options.md`: snake_case fields and lower-kebab
enum values. Unknown or retired option fields and values are invalid runtime
input and are never reinterpreted.

## Creating A Ledger

Load `ledger-template.md` only when the resolved ledger does not exist. When the
marker check in `## Ledger Resolution And Validation` rejects an existing
ledger, stop; do not load the new-ledger template. Existing ledgers that pass
the check continue without loading the template.

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
| `autonomous` | Candidate safe to delegate under current session authorization and execution-report boundaries. Move to `active` when assigned or reclassify when delegation is no longer useful or safe. Ledger cannot be `complete` while actionable items remain. |
| `needs-owner` | Waiting on owner decision, credentials, scope approval, risk acceptance, mutation authorization, or another non-Codex decision. Record decision brief, options, recommendation, and minimum owner action. |
| `ready-next` | Work still needing an authorized delivery, review, closeout, merge, or release action. Execute in the owning surface when authorized; otherwise record the missing permission or blocker. In mandatory visible Feature Spec task mode, implementation and review actions stay assigned to that Spec's task and never become root actions. `pull-request-ready-for-merge-but-not-merged` keeps required review actions actionable while the PR is draft, then mark-ready and parent closeout actionable after the current-revision review policy and remaining gates pass. An explicit review skip makes request/wait actions `not-applicable`, not blocked. `validated-draft-pull-request-published` makes all later PR lifecycle actions `not-applicable`. |
| `blocked` | Cannot progress with current access, state, dependency, or proof. Record blocker, evidence, minimum next action, and whether it is owner-actionable or external. |
| `ignored-or-suppressed` | Known item intentionally excluded. Record source id, source fingerprint, owner, date, and reason; rediscover only if owner direction or source fingerprint changes. |
| `completed` | Required gates passed and the exact `change_delivery_target` is proven. For `validated-changes-left-uncommitted`, acceptance plus validation are sufficient and commit/push/PR fields are not applicable. A default-branch GitHub whole Feature Spec closeout PR may report merge-ready with `parent_spec_closeout=armed`, proof, and an active or handed-off watch, but the parent source and portfolio ledger remain incomplete until merge and verified issue closure. A non-default-base PR workstream may reach its own target with `deferred-to-default-branch` only while the later closeout vehicle remains actionable. The draft-PR target records later lifecycle actions as not applicable. Otherwise record delivery proof, source closeout, publication checkout, caller-checkout disposition, lifecycle decision, and artifact disposition. Pending required delivery, closeout, or proof remains non-terminal. |
| `deferred` | Residual work intentionally outside current closeout. Link the follow-up or proposed body; use only for real residual scope, blocked live proof, or owner-visible follow-up work. |
| `released` | Release gate passed and actual product/package/version release, deploy, or tag proof is recorded. Ordinary implementation remains `completed` unless a release happened. |

## Closeout Hygiene

Before marking a ledger `complete`, verify:

- Every discovery source was rescanned or intentionally skipped with a reason,
  cursor, and fingerprint.
- The Goal objective, or its ledger fallback, is achieved. Record a concrete
  blocker instead of completion when it is not.
- The active-root claim is `released`, with no active worker, authorized
  `ready-next` action, `autonomous` candidate, due check, or root-owned
  closeout action.
- Required gates are selected and passed through `gates.md`. For
  `change_delivery_target=pull-request-ready-for-merge-but-not-merged`, project the
  conditional canonical review and parent-closeout result into the gate matrix
  and workstream row; do not duplicate its algorithm here.
- A parent Feature Spec is not complete while closeout is `armed`,
  `deferred-to-default-branch`, or awaiting an owner/automation handoff.
  Completion requires `parent_spec_closeout=closed`,
  `parent_closeout_watch=complete`, and post-merge proof that GitHub closed the
  issue. The draft-PR target and excluded workstreams record
  `not-applicable` with a reason.
- `active` contains only rows with a real next check, assigned-task action, or root-owned action outside mandatory Feature Spec implementation/review;
  `autonomous` and `ready-next` are empty or reclassified with the missing
  authority, decision, blocker, or follow-up.
- Feature Spec-backed delivery records its real branch or PR proof and resolved
  terminal target, or the exact blocker. Do not complete while an
  authorized commit, push, PR, review, disposition, or closeout action remains
  actionable.
- `needs-owner`, `blocked`, and `deferred` rows contain their decision brief or
  blocker, evidence, minimum next action, and owner-visible follow-up as
  applicable.
- `completed` records final proof, source closeout, integration, publication
  checkout, caller-checkout disposition, worker lifecycle, and the applicable
  review/parent-closeout projections.
- Serial caller-checkout completion additionally proves that implementation
  occurred only on the Spec's dedicated target branch and that the original
  branch, HEAD, and clean status were restored before the next dispatch or
  portfolio closeout.
- Generated ignored artifacts and helper worktrees are removed, retained with
  a reason, isolated in a helper worktree, or explicitly handed off.
- The Recovery Packet reflects the final current-state projection or is
  explicitly `unavailable`; a stale packet cannot support closeout.
- Runtime metrics contain exact root-scoped phase deltas, labeled interval
  deltas, or one `unavailable` row; metrics never replace closeout proof.
- Suppressed items retain source id, fingerprint, reason, owner, and date and
  are rediscovered only after that fingerprint or owner direction changes.

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
active-worker lists, and current next actions in the same deterministic patch.
When the authoritative source or controller state changed, append one dated
note and record this compact result. If the snapshot is unchanged, perform no
ledger write and emit no synthetic progress row:

| Checked At | Sources Re-read | Current Projection Updated | Stale Values Removed | Remaining Actionable | Result |
| --- | --- | --- | --- | --- | --- |
| <time> | <source ids/URLs> | <sections/rows> | <values or none> | <count and refs> | pass|blocked |

After recording a real transition, refresh the recovery packet from the
reconciled projection and record only its changed sections and new fingerprint
in normal progress output. Poll attempts, elapsed wall time, and repeated
unchanged observations are not transitions.

Before setting the ledger `complete`, run the reconciliation after the last
source mutation and verify these invariants:

- no closed source is described as open or pending in a current-state field;
- no merged PR is described as draft, open, or merely ready for merge;
- no archived, integrated, abandoned, or handed-off worker remains active;
- every fallback records its GitStack workflow, primary connector attempt,
  authenticated `gh` fallback, and authority reuse;
- merge proof exists only when explicit merge authority exists;
- every default-branch whole Feature Spec closeout vehicle is merged with
  `parent_spec_closeout=closed`, `parent_closeout_watch=complete`, matching armed
  head/base/body history, and post-merge proof that the parent issue closed; no
  `armed` unmerged PR or `deferred-to-default-branch` vehicle remains
  outstanding;
  every draft-PR or otherwise excluded workstream records
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
final report, `ledger_status=paused`, and the Feature Spec retained under `needs-owner`
or the named active monitor. Otherwise keep the root `claimed` and the watch
`root-monitoring` until the merge and actual parent closure are verified.
