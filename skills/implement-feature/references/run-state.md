# Implement Feature Run State

## Ownership And Hard Cut

Use one absolute direct-child `.json` state document per overlapping
repository/source portfolio under
`~/.cache/dotagents/skills/implement-feature/ledgers/`. Create it only after
atomic claim acquisition. `scripts/ledger-cache` v5 is the sole active-state
writer; roots and visible tasks never patch or replace it directly.

`scripts/active-root-claim` remains the sole ownership authority. Every
mutation requires the same live root and raw 64-hex acquire fingerprint. The
helper also requires a regular, non-symlinked state root and shared lock; a
missing lock or unsafe path fails closed.

Active state accepts only ledger schema `3.0.0` created from registration
schema `3.0.0`. Active Markdown, earlier JSON schemas, aliases, unknown fields,
invalid paths, and invalid transitions block as `unsupported-active-ledger`. Do not import, migrate,
rename, dual-read, dual-write, retire, or delete them. Frozen archive-v1 entries
remain byte-identical cold evidence that can only be read, verified, or pruned.

## Command Contract

Load `run-state-packets.md` immediately before writing a registration or event
packet. It is the sole strict field registry.

```text
scripts/ledger-cache --json ledger create --ledger '<absolute-active-json>' --root-id '<root-id>' --expected-claim-fingerprint '<claim-fingerprint>' --operation-id '<unique-operation-id>' --registration-file '<absolute-registration-json>'
scripts/ledger-cache --json ledger apply --ledger '<absolute-active-json>' --root-id '<root-id>' --expected-claim-fingerprint '<claim-fingerprint>' --expected-generation '<current-generation>' --operation-id '<unique-operation-id>' --events-file '<absolute-events-json>'
scripts/ledger-cache --json ledger read --ledger '<absolute-active-json>' --projection 'status|dispatch|recovery|terminal'
```

`expected_generation` is compare-and-swap authority. A stale generation
changes nothing and requires a fresh projection. Replaying the same
`operation_id` with the same canonical payload is an idempotent success; reuse
with another payload is a conflict. The root submits one atomic event batch;
the helper validates it, applies transitions and invalidations, increments generation once, and
atomically replaces the file under the shared lock. No partial batch is
visible. Reads never mutate or refresh external truth.

## Task And Delivery Model

Keep one task entity per implementation-eligible Feature Spec. It owns source
and visible-task identity/title, immutable profile, Goal, lifecycle,
dependencies, task gates, blocker, and next action; never a singular repository,
checkout, PR, or revision. Identity comes from refs, never display titles.

Each task owns nonempty `deliveries[]`, exactly one per affected Git repository.
A stable `delivery_key` owns repository, branch, paths, local tracker moves,
managed checkout/isolation, PR/revision, review, gates, and tracker dirt. Keys
are task-unique; no managed `(repository, checkout)` pair may serve two Specs.

Bind the task ref with the complete `managed-checkouts-observed` map, then use
`task-observed` for its title, profile, Goal, and lifecycle. Before work advances
beyond `created`, partial, unmanaged, or non-isolated checkout maps block.
Use `revision-observed` to establish one immutable delivery/PR tuple and derive
its `revision_key`. The tuple includes canonical GitHub `owner/repository` and
requires its exact `https://github.com/<owner/repository>/pull/<number>` URL.
Use `delivery-observed` only to bind the current full PR
lifecycle plus committed/published evidence to that exact key. The events are
distinct, not aliases.

At most three tasks are nonterminal. Ready sets, conflicts, capacity, review
deadlines, closeout readiness, and next actions are derived. Dependencies
require verified upstream merge. A task waiting for review remains nonterminal
and consumes a slot.

## Gate Scopes And Invalidation

Each gate name has exactly one scope; `gate-observed` carries the resulting
`delivery_key` and `binding_key`:

| scope | key | examples |
| --- | --- | --- |
| `task-static` | both keys null | dependency integration |
| `delivery-static` | delivery key; binding null | PR preflight |
| `delivery-revision` | delivery key; current revision key as binding | focused/full validation, AutoReview, publication, Codex review, CI, PR readiness, tracker closeout, mergeability |
| `task-revision-set` | delivery null; complete revision-set key as binding | scope acceptance, integration validation, domain closeout |

Static gates dispatch before a PR revision; requiring one would deadlock task
creation. A task revision set contains every delivery exactly once.

Changed revision, diff, PR identity, rule, or tracker delivery invalidates its
delivery gates and all task-set gates. Reuse AutoReview only for an unchanged
complete target. Unknown or pending evidence blocks.

## Closed Event Registry

Each event has the exact fields in `run-state-packets.md`, a bounded external
evidence reference, and no unknown fields.

| event | material transition |
| --- | --- |
| `root-title-observed` | Bind live root title. |
| `portfolio-goal-activated` | Bind active root Goal. |
| `task-observed` | Bind material task/Goal lifecycle. |
| `managed-checkouts-observed` | Bind complete delivery checkout map. |
| `revision-observed` | Establish exact delivery/PR revision tuple. |
| `delivery-observed` | Bind lifecycle/commit/publication to that revision. |
| `source-moved` | Adopt proven local move; dirty its delivery. |
| `review-wait-started` | Start immutable 45-minute wait. |
| `review-wait-invoked` | Bind actual invocation/timeout. |
| `review-observed` | Bind the single provider result/disposition and optional timeout warning. |
| `gate-observed` | Bind one typed gate. |
| `task-terminal-sealed` | Freeze current task terminal proof. |
| `task-goal-completed` | Bind worker Goal completion to seal. |
| `terminal-handoff-recorded` | Bind terminal seal, next action, and external authority. |
| `portfolio-terminal-verified` | Bind independent portfolio proof. |
| `portfolio-goal-completed` | Bind root Goal completion. |
| `post-terminal-drift-recorded` | Preserve Goals; mark drift/archive block. |

Do not emit events for unchanged polls, wait timeouts, repeated task text, or
claim heartbeats. Persist digests and exact refs, not command output, review
transcripts, or prose summaries. Do not persist Wave Reports, Recovery Packets,
no-progress rows, or hand-authored projections.

## Root Title And Portfolio Goal

`total_spec_count` includes only implementation-eligible Feature Specs and
excludes coordination-only parent/global artifacts. Derive
exactly `👨🏻‍💻 Feature Orchestrator` for one or
`👨🏻‍💻 Multi-Feature Orchestrator` for more than one, with no counter or suffix.
The title is stable for the accepted run, is UI evidence, and is never identity
or scheduling input. After registration, set and observe the calling task title before Goal registration
or dispatch, then apply `root-title-observed`. Call `get_goal`; adopt a matching
interrupted registration or call `create_goal` without `token_budget`, then
apply `portfolio-goal-activated`. A different unfinished Goal is `needs-owner`;
a missing active Goal is never recreated during recovery.

Root and worker Goals remain active during review waits and all nonterminal
closeout work. They transition to complete only through staged terminal
closeout.

## Review Timing

Keep one review per delivery revision. `review-wait-started` derives immutable
`wait_deadline=wait_started_at+45m`. Before GitStack, persist
`review-wait-invoked` with a nonfuture timestamp and
`provider_timeout=max(0,floor(wait_deadline-wait_invoked_at))`; zero is an immediate check.
That event is single-launch authority. Never default, restart, or extend.

Bind exactly one result to the current request and revision. Valid pairs are
`clean/accepted`, `findings/fix-required`, `failed/blocked`, and
`waiting/timeout-accepted`. The pending pair is valid only at or after the
deadline and requires a persistent PR `warning_ref`; every other pair requires
that field to be null. The warning must be a canonical GitHub issue-comment URL
on the review entity's exact PR URL, have a post-deadline timestamp, and match
the request/revision-specific warning fingerprint in
`codex-review-closeout.md`. A timeout-accepted review passes the review gate without
claiming a clean verdict, is surfaced in projections and the final report, and
does not waive any other gate. Retain the claim and keep Goals active. Never
schedule another check, pause a Goal, arm an App heartbeat, relaunch the waiter,
or create a nonterminal handoff. Projections include a byte-bounded detailed
prefix of warnings only for current delivery revisions plus an omitted-count
summary when needed; the ledger retains the complete evidence. Superseded
warnings remain inert history. The later merge
workflow re-checks late Codex findings.

## Local Source Move

`source-moved` requires a predeclared local active-to-done ref, unchanged body,
and current task-set substantive/integration/domain proof. GitHub, premature,
alternate, and untracked moves are invalid.

It dirties the delivery and invalidates revision/task-set gates. Commit/push,
establish a newer `revision-observed`, then apply `delivery-observed`; only
current committed/published proof clears dirt. Rerun gates. A move is not
terminal.

## Staged Terminal Closeout

Closeout has one irreversible order:

1. Require every applicable current static, delivery-revision, and
   task-revision-set gate; apply `task-terminal-sealed` for the exact complete
   delivery revision set.
2. Call the worker Goal through `update_goal` with `status=complete`, read it
   back, then apply `task-goal-completed`. Do not derive completion from task
   prose.
3. Apply `terminal-handoff-recorded` with the unchanged seal fingerprint,
   `pull-request-ready` kind, external authority, and next merge action.
4. After every task passes those stages, independently reverify current
   external truth and apply `portfolio-terminal-verified`.
5. Call the root Goal through `update_goal` with `status=complete`, read it back,
   then apply `portfolio-goal-completed`.
6. Reverify archive eligibility, release the claim as terminal, and archive
   through `cache-lifecycle.md`.

The terminal projection exposes each stage without requiring a later one.
`terminal-handoff-recorded` is terminal-only, never monitoring/dependency wait.

From seal onward, changed terminal truth permits only
`post-terminal-drift-recorded`; it blocks terminal handoff, verification, and
archive. Never reopen a Goal. Record an externally completed Goal without
advancing closeout; correction needs owner action and a separately authorized
fresh run.

## Takeover And Recovery

`active-root-claim` owns takeover and its prepared journal. Existing candidate
state validates normally. Missing state initializes only from the current
claim's complete adoption mappings after source, task/no-task, Goal, profile,
and delivery-checkout verification. Creation binds the candidate claim; do not
infer identity or replace a mapped task. A same-root resumed run keeps its exact
claim and fingerprint; verify them before mutation. If an authorized
takeover replaced that claim, the old root stops. Revalidate surfaces, sources,
titles, Goals, full checkouts, revisions, reviews, and gates. `recovery` is
guidance, not external truth.

## Bounds And Projections

`run-state-packets.md` bounds all input, state growth, and output. Canonical
paths reject absolute/backslash/empty/parent traversal.

`status` reports bounded identity and progress, `dispatch` reports only the
derived ready set and capacity, `recovery` reports freshness inputs, and
`terminal` reports staged closeout, review-timeout warnings, and archive
readiness. Callers compare the immutable review deadline with their observed
clock; a projection never persists or invents an `overdue` fact.

## Hard Cut

There is no compatibility path or migration for active Markdown or any active
JSON schema before `3.0.0`.
Frozen archive-v1 entries remain readable evidence only. The deterministic
Markdown audit report is rendered only during archival. Terminal archival uses
the `ledger archive` command in `cache-lifecycle.md`; active state exposes only
deterministic projections from JSON.
