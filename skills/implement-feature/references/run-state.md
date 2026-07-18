# Implement Feature Run State

## Ownership And Resolution

Use one direct-child JSON state document per overlapping repository/source
portfolio under `~/.cache/dotagents/skills/implement-feature/ledgers/`. Create it
only after atomic claim acquisition. `scripts/ledger-cache` v3 is its sole
writer; the root and visible tasks never create, patch, or replace it directly.

`scripts/active-root-claim` remains the sole ownership authority. The state
records its root id, acquire-time fingerprint, repositories, sources, and claim
evidence, but never duplicates claim heartbeat state. Every state mutation
requires the same live root and raw 64-hex acquire fingerprint.

An active state path must be an absolute direct-child `.json` path. Active
Markdown, unsupported schemas, unknown fields, and invalid transitions block as
`unsupported-active-ledger`. Do not import, migrate, alias, dual-read, or
dual-write them. Archived state is cold evidence and never recovery input.

## Command Contract

Load `run-state-packets.md` immediately before creating a registration or event
packet. It is the sole field registry for strict command inputs.

Initialize once from a strict registration packet:

```text
scripts/ledger-cache --json ledger create --ledger '<absolute-active-json>' --root-id '<root-id>' --expected-claim-fingerprint '<claim-fingerprint>' --operation-id '<unique-operation-id>' --registration-file '<absolute-registration-json>'
```

The resulting state contains the accepted authorization evidence, complete
source snapshots, complete implementation-eligible Feature Spec registry,
resolved task profiles, portfolio Goal objective and fingerprint,
`portfolio_goal_state=pending`, and the derived pending root title. It is one
initial snapshot, not a stream of table writes. Missing or extra fields fail
closed.

Apply one or more material events atomically:

```text
scripts/ledger-cache --json ledger apply --ledger '<absolute-active-json>' --root-id '<root-id>' --expected-claim-fingerprint '<claim-fingerprint>' --expected-generation '<current-generation>' --operation-id '<unique-operation-id>' --events-file '<absolute-events-json>'
```

`expected_generation` is compare-and-swap authority. A stale generation changes
nothing and requires a fresh read. Replaying the same `operation_id` with the
same canonical payload is an idempotent success; reusing it with a different
payload is a conflict. The helper validates the complete batch, applies its
transition and invalidation rules, increments generation once, and atomically
replaces the file under the shared claim-store lock. No partial event batch is
visible.

Read only the projection needed by the next decision:

```text
scripts/ledger-cache --json ledger read --ledger '<absolute-active-json>' --projection 'status|dispatch|recovery|terminal'
```

`status` reports identity and current progress; `dispatch` reports the derived
ready set and capacity; `recovery` reports the freshness inputs and due actions;
`terminal` reports gate eligibility and final evidence. Reads never mutate or
refresh external truth.

## Event Registry

The event type registry is closed. Every event has strict type-specific fields
and an external evidence reference; unknown event types or fields are invalid.

| event type | material transition |
| --- | --- |
| `claim-rebound` | Bind a recovered takeover state to the validated candidate claim and embedded adoption evidence. |
| `root-title-observed` | Record exact live singular/plural root-title evidence after mutation or observation. |
| `portfolio-goal-activated` | Bind the matching root Goal and move `pending` to `active`. |
| `portfolio-goal-paused` | Bind the armed heartbeat and observed root Goal pause after the portfolio becomes quiescent. |
| `portfolio-goal-resumed` | Bind heartbeat consumption or manual wake evidence and restore the root Goal to `active`. |
| `portfolio-goal-completed` | Bind completion evidence after every terminal task and gate passes. |
| `task-observed` | Record a material task lifecycle, title, profile, Goal, managed-checkout, result, blocker, or terminal change. |
| `source-moved` | Atomically adopt one predeclared local active-to-done tracked move with unchanged body fingerprint. |
| `revision-observed` | Adopt one exact PR/head/base/merge-base tuple and invalidate stale revision-bound evidence. |
| `review-wait-started` | Record the root-issued revision key and one absolute 30-minute active-wait deadline. |
| `review-wait-invoked` | Record the worker's actual invocation time and remaining provider timeout. |
| `review-observed` | Record current-tuple request, provider, findings, disposition, and observation evidence. |
| `review-monitoring-scheduled` | Pause a still-waiting worker Goal and derive its next one-shot check at `observed_at+30m`. |
| `review-monitoring-resumed` | Resume one due worker Goal for exactly one provider check. |
| `gate-observed` | Record current evidence for one fixed validation, AutoReview, review, CI, integration, domain-closeout, tracker-closeout, publication, or mergeability gate. |
| `external-handoff-recorded` | Record the exact terminal merge/closeout handoff for a merge-ready task. |

Do not emit an event for an unchanged poll, wait timeout, repeated task text, or
claim heartbeat. Persist evidence digests and exact external references, not
large command output or prose summaries.

## Root Title And Portfolio Goal

`total_spec_count` counts implementation-eligible Feature Specs and excludes
coordination-only parent/global artifacts. Zero is invalid. Derive exactly
`👨🏻‍💻 Feature Orchestrator` for one Spec and
`👨🏻‍💻 Multi-Feature Orchestrator` for two or more, with no counter or suffix.
The title is stable for the accepted run and is UI evidence, never identity or
scheduling input.

After state creation, set and observe the calling task title before Goal
registration or dispatch, then apply `root-title-observed`. Call `get_goal`;
adopt a matching interrupted registration or call `create_goal` without
`token_budget`, then apply `portfolio-goal-activated`. A different unfinished
Goal is `needs-owner`; a missing active Goal is never recreated during recovery.

Root and worker Goal pause/resume is owned by the conditional workflow in
`review-monitoring.md`; load it only after a deadline remains pending or when
recovering that typed schedule. The root pauses only for a quiescent portfolio
and resumes before any due worker.

Only after every Spec reaches
`pull-request-ready-for-merge-but-not-merged`, every task Goal is complete, and
the terminal projection passes may the root call `update_goal` with
`status=complete` and apply `portfolio-goal-completed`. Interrupted closeout may finish these exact
idempotent transitions after full revalidation; it never reopens implementation.

## Sources, Tasks, And Scheduling

Preserve each authored source ref separately from its canonical runtime id and
content fingerprint. Use the canonical GitHub issue URL or qualified local id
for claim, task, and scheduling identity. A local generated issue begins at its
active ref with its predeclared done ref. Only `source-moved` may adopt that done
ref, and only after substantive, integration, and required domain-closeout
evidence with an unchanged body fingerprint.

Keep one typed task entity per implementation-eligible Feature Spec. It owns the
exact task ref and title, model/thinking profile, assignment Goal evidence,
managed checkout map, lifecycle, affected scope, current PR identities,
material results, blocker, and next action. A Spec has at most one task and the
portfolio at most three nonterminal tasks. Identity comes from source and task
refs, never display titles.

Ready sets, path-conflict decisions, available capacity, due checks, and next
actions are deterministic projections. A dependency is ready only when its
upstream implementation is externally verified merged and current gate evidence
records that fact; an upstream `merge-ready` task is still unfinished. Dispatch
also requires current passed `pr-preflight` and `dependency-integration` gates.
Workers paused in `review-monitoring` remain nonterminal, retain their scope,
and count against the three-task limit. Do not persist Wave Reports, scheduling
summaries, no-progress rows, or a hand-authored Recovery Packet.

## Monitoring And Reconciliation

After dispatch, take one full task snapshot. Wait with the current cursor until
the earliest material task event, attention request, claim-heartbeat deadline,
or hard workflow deadline. An unchanged timeout performs only the required
claim heartbeat. Thereafter consume compact deltas and apply only material
events. Use another full task read only for anomaly or blocker diagnosis and
independent terminal verification.

Each reconciliation reads the smallest projection, refreshes the external facts
needed for the next decision, and submits one atomic event batch. On a CAS
conflict, discard the derived batch, read the new generation, and recompute. The
worker owns the bounded GitStack waiter; the root does not poll that provider in
parallel.

## Revision, Review, And Gate Invalidation

`revision-observed` binds the exact repository, PR number and URL, head SHA,
base ref, and merge-base SHA. A head, base, merge-base, material diff, or
repository-rule change invalidates older revision-bound validation, AutoReview,
Codex review, CI, tracker-closeout, and mergeability evidence. Clean AutoReview
evidence may be reused only when its complete target remains unchanged.

Keep exactly one review entity per exact PR/head/base/merge-base revision key.
The root applies `review-wait-started` with `wait_started_at` and absolute
`wait_deadline=wait_started_at+30m`. The worker immediately computes
`provider_timeout=floor(wait_deadline-now)`, launches GitStack in the same local
step, and reports `wait_invoked_at` and the actual timeout through
`review-wait-invoked`. If the result is nonpositive, check once. Never default,
restart, segment, or extend the deadline.

At deadline check once. If still pending, load `review-monitoring.md`; later
checks are due one-shots and never another waiter. The original wait timestamps
never change.

Actionable findings remain represented until their fix and proof exist. A new
revision receives a distinct review request and deadline. Terminal state
requires the current exact PR identity, `OPEN`, non-draft, conflict-free
mergeability, required base freshness, approvals, merge-queue eligibility,
successful applicable CI, prepared tracker closeout, and every other fixed gate.
Unknown or pending evidence blocks; never enqueue or merge.

## Takeover And Recovery

Takeover authority and journals remain owned by `active-root-claim`. Cross-check
each available prior JSON state through its recorded `ledger_ref`. A prepared
takeover journal may initialize a missing candidate state only when no candidate
state was ever created and the current claim, complete embedded mappings, task
Goals, titles, profiles, and managed checkouts all revalidate. Then record
`claim-rebound`. Never rebuild from task titles or import prior Markdown.

On resume, revalidate runtime surfaces, claim ownership, source fingerprints,
repositories, root and task titles, Goals, managed checkouts, current revisions,
review waits, and fixed gates against external truth. Use the `recovery`
projection to locate due work, but treat it as derived. Apply only material
corrections after the complete freshness pass.

## Handoff, Release, And Archive

`external-handoff-recorded` is terminal-only. A resumable review handoff uses
the typed schedule, paused Goal evidence, and heartbeat in
`review-monitoring.md`, then releases the claim while retaining active JSON.

For terminal closeout, require the `terminal` projection to pass, complete all
Goals, apply `portfolio-goal-completed`, independently verify current external
evidence, and use the complete checksum-bound release/archive sequence in
`cache-lifecycle.md` through `ledger archive`. The deterministic Markdown audit report is rendered only
during archival; it is never active state.

## Hard Cut

There is no compatibility path for active Markdown, templates, mutable tables,
manual patches, free-form notes, Wave Reports, Recovery Packets, retired fields,
or earlier active schemas. A blocked old run can start fresh only after its owner
releases the claim. Frozen archive-v1 entries remain readable evidence under the
separate archive contract; that does not make them active-compatible.
