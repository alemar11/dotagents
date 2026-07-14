# Ledger Reference

Use ledgers to persist portfolio scope, active workstreams, gate overrides, and
orchestration state between Codex sessions.

## Ledger Resolution And Current-Format Classification

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
ledgers use ATX headings only; any Setext underline syntax outside fences
classifies the ledger as legacy. Keep current-format ledgers free of raw HTML:
outside fences, any HTML comment marker or line whose first non-space character
is `<` also classifies the ledger as legacy instead of treating raw-block
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
duplicate and triggers migration. A missing, duplicate, out-of-order, or
wrongly nested marker—or a missing or invalid header field—classifies the
ledger as legacy.

```text
## Scope
## Option Resolution
### Session Rows
### Scoped Rows
## Discovery Sources
## Active Root
## Codex Review Wait Registry
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

When the structure check fails, load `ledger-template.md` to migrate the
ledger. Keep this lightweight marker set aligned with the template whenever the
required format changes.

If the resolved ledger file does not exist, load `ledger-template.md` and create
it before discovery. Fill known fields, use `tbd` for unknown owner or
repository metadata, set `Status: active`, and add a dated note summarizing the
owner request and initial task sources. Do not load the template for an existing
ledger that passes the marker check above.

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

## Creating Or Migrating A Ledger

Load `ledger-template.md` only when creating a ledger or when the marker check
in `## Ledger Resolution And Current-Format Classification` classifies an
existing ledger as legacy. Existing ledgers that pass that check do not load
the template.

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

- Every discovery source was rescanned or intentionally skipped with a reason,
  cursor, and fingerprint.
- The Goal objective, or its ledger fallback, is achieved. Record a concrete
  blocker instead of completion when it is not.
- The active-root claim is `released`, with no active worker, authorized
  `ready-next` action, `autonomous` candidate, due check, or root-owned
  closeout action.
- Required gates are selected and passed through `gates.md`. For
  `delivery_mode=pull-request` plus `pr_closeout=merge-ready`, project the
  conditional canonical review and parent-closeout result into the gate matrix
  and workstream row; do not duplicate its algorithm here.
- A parent PRD is not complete while closeout is `armed`,
  `deferred-to-default-branch`, or awaiting an owner/automation handoff.
  Completion requires `parent_prd_closeout=closed`,
  `parent_closeout_watch=complete`, and post-merge proof that GitHub closed the
  issue. Authorized `draft-only` and excluded workstreams record
  `not-applicable` with a reason.
- `active` contains only rows with a real next check or root-owned action;
  `autonomous` and `ready-next` are empty or reclassified with the missing
  authority, decision, blocker, or follow-up.
- PRD-backed authorized publication records its real PR URL and resolved
  terminal delivery state, or the exact blocker. Do not complete while an
  authorized commit, push, PR, review, disposition, or closeout action remains
  actionable.
- `needs-owner`, `blocked`, and `deferred` rows contain their decision brief or
  blocker, evidence, minimum next action, and owner-visible follow-up as
  applicable.
- `completed` records final proof, source closeout, integration, publication
  checkout, caller-checkout disposition, worker lifecycle, and the applicable
  review/parent-closeout projections.
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
