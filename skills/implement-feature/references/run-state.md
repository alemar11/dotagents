# Implement Feature Run State

## Ownership And Hard Cut

Use one absolute direct-child `.json` state document per overlapping
repository/source portfolio under
`~/.cache/dotagents/skills/implement-feature/ledgers/`. Create it only after
atomic claim acquisition. `scripts/ledger-cache` v8 is the sole active-state
writer; roots and visible tasks never patch or replace it directly.

`scripts/active-root-claim` remains the sole ownership authority. Every
mutation requires the same live root and raw 64-hex acquire fingerprint. The
helper also requires a regular, non-symlinked state root and shared lock; a
missing lock or unsafe path fails closed. Filesystem `EACCES`, `EPERM`, and
`EROFS` report `claim-store-unavailable`; they are not corruption evidence.

Active state accepts only ledger schema `5.0.0` created from registration
schema `4.0.0`. Active Markdown, earlier JSON schemas, aliases, unknown fields,
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

Keep one task per implementation-eligible Feature Spec. It owns source/task
identity, title, profile, Goal, lifecycle, dependencies, gates, blocker, and
next action; identity comes from refs, never display titles. Its nonempty
`deliveries[]` has one stable task-unique `delivery_key` per affected Git
repository, owning repository/GitHub identity, branch/default base, CI and
preflight state, paths, tracker moves, checkout, PR/revision, compact AutoReview
chain, review, and gates.
No managed `(repository, checkout)` pair may serve two Specs.

Bind the complete isolated checkout map with `managed-checkouts-observed`
before work passes `created`; bind task/Goal lifecycle with `task-observed`.
`revision-observed` establishes the immutable delivery/PR tuple and
`revision_key`; `delivery-observed` binds lifecycle plus committed/published
truth to it. The events are distinct, not aliases.

Registration seeds the passed preflight. Before seal,
`delivery-preflight-observed` may replace it with another definitive
`configured|not-configured` result; unknown inspection blocks and preserves the
last valid state. At most three tasks are nonterminal. Scheduling, review
deadlines, closeout, and next actions are derived; dependencies require merge,
and a review wait consumes a slot.

## Gate Scopes And Invalidation

Each `gate-observed` has one scope from `run-state-packets.md`:
`task-static` dependency integration uses null keys; `delivery-revision` uses
the delivery key plus its delivery evidence binding; `task-revision-set` uses
the complete set key with no delivery. The delivery evidence key binds its
revision key and preflight key. The task set contains every delivery evidence
key once. CI is inapplicable only for `not-configured`.

A changed revision, preflight/CI state, diff, PR identity, rule, or tracker
delivery invalidates affected delivery and task-set gates. AutoReview is
reusable only for an unchanged complete target; unknown or pending truth blocks.

## Closed Event Registry

`run-state-packets.md` is the sole closed event-name and field registry. Events
represent only its material transitions and carry bounded evidence refs; unknown
fields fail. Emit nothing for unchanged polls, wait timeouts, repeated task
text, or claim heartbeats. Persist digests/refs rather than outputs or
transcripts; never persist Wave Reports, Recovery Packets, no-progress rows, or
hand-authored projections.

## Root Title And Portfolio Goal

Derive each `objective` from its current bundle; require exact
`CI when configured`. Never reuse Goal/ledger text/fingerprint; helper rejects
unconditional-CI registration and active state.

`total_spec_count` includes only implementation-eligible Feature Specs and
excludes coordination-only parent/global artifacts. Derive
exactly `👨🏻‍💻 Feature Orchestrator` for one or
`👨🏻‍💻 Multi-Feature Orchestrator` for more than one, with no counter or suffix.
The title is stable for the accepted run, is UI evidence, and is never identity
or scheduling input. After registration, set and observe the calling task title before Goal registration
or dispatch, then apply `root-title-observed`. Call `get_goal`; adopt a matching
interrupted registration or call `create_goal` without `token_budget`, then
apply `portfolio-goal-activated`. A different unfinished Goal is `needs-owner`;
a missing active Goal is never recreated during recovery. The entry gate returns
`new-root-required` for a blocked root Goal; never adopt or replace it.

## Review Timing

Keep one review per delivery revision. `review-wait-started` fixes
`wait_deadline=wait_started_at+45m`; before GitStack,
`review-wait-invoked` records a nonfuture timestamp and
`provider_timeout=max(0,floor(wait_deadline-wait_invoked_at))`. It is
single-launch authority: never default, restart, or extend.

`review-observed` binds exactly one current request/revision result:
`clean/accepted`, `findings/fix-required`, `failed/blocked`, or
`waiting/timeout-accepted`. Only the last is valid after the deadline and needs
the exact PR warning URL, time, and fingerprint from
`codex-review-closeout.md`; all other warning fields are null. It passes only
the review gate and is never clean. Keep claim and Goals active; never schedule,
pause, relaunch, or create a nonterminal handoff. Projections bound current
warnings and count omissions; superseded warnings are inert. The merge workflow
re-checks late findings.

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
JSON schema before `4.0.0`.
Frozen archive-v1 entries remain readable evidence only. The deterministic
Markdown audit report is rendered only during archival. Terminal archival uses
the `ledger archive` command in `cache-lifecycle.md`; active state exposes only
deterministic projections from JSON.
