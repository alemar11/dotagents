# Implement Feature Ledger

## Resolution

Use one ledger per overlapping repository/source portfolio under
`~/.cache/dotagents/skills/implement-feature/ledgers/`, created only after
atomic claim acquisition. A missing ledger loads `ledger-template.md`; an
incompatible current ledger blocks without migration.

Archived ledgers live below `ledgers/archive/` as cold evidence and never
participate in active resolution or recovery. Load `cache-lifecycle.md` after
CLAIM and before terminal archival.

The ledger is evidence, not an option registry or concurrency primitive. It
records authorization/takeover, sources and fingerprints, claim/root-title/Goal
evidence, task title/profile/checkout state, gates and scheduling/recovery state,
and external handoffs.

## Authorization

Persist `visible_app_task_permission=granted-by-authorized-user` with its exact
run-scoped evidence. Add `stale_claim_takeover_permission` only when a takeover
question is actually resolved. Do not store fixed policy, derived state, bundle
data, or retired option rows as authorization.

## Root Task Display Title

After CLAIM and cache maintenance, REGISTER creates the ledger and complete
Feature Spec registry. `total_spec_count` counts its implementation-eligible
Feature Spec rows, excluding coordination-only parent/global artifacts; zero is
invalid. Use exactly `👨🏻‍💻 Feature Orchestrator` when
`total_spec_count=1` and `👨🏻‍💻 Multi-Feature Orchestrator` when
`total_spec_count>=2`.
Do not append a counter or progress suffix. This is derived UI evidence, never
an option, source field or fingerprint, claim key, task identity, scheduling
input, or branch component.

Persist `root_task_title` with `root_task_title_evidence_ref=pending`, call
`codex_app__set_thread_title` with only the title and omit `threadId`, then
observe the exact live title and persist its evidence. Finish this before the
`get_goal` adoption, any `create_goal` call, or dispatch. Mutation or observation failure must leave evidence
pending, retain the claim and ledger, and forbid Goal creation or dispatch. Recovery handles a
crash before mutation or after the title changed but before evidence persisted.

The root title is stable for the accepted run; worker lifecycle changes never
alter it. Each new invocation derives it from its accepted registry, allowing
singular, plural, or singular again. A denied, unsupported, or planning-required
pre-CLAIM run leaves the current title unchanged. Resume recomputes after the
complete freshness pass and repairs drift. Takeover uses the rebuilt candidate
registry for the new calling root and never copies a replaced root's title.

## Portfolio Goal

Ledger creation persists the objective, fingerprint, and
`portfolio_goal_state=pending` as registration intent. After exact root-title
observation, call `get_goal`; adopt a matching interrupted registration or call
`create_goal` with the recorded objective and without `token_budget` when none
exists, then atomically persist its evidence with
`portfolio_goal_state=active`. A different unfinished Goal is `needs-owner`.
Recovery may complete pending registration only after its full freshness pass;
an active row requires matching evidence and never recreates a missing Goal.

Call `update_goal` with `status=complete` only after every Feature Spec reaches
`pull-request-ready-for-merge-but-not-merged`. Persist the completion evidence
and `portfolio_goal_state=complete` before terminal claim release or archival.
If either operation fails, retain the claim and active ledger. Temporary
blockers and resumable handoffs leave the Goal active. Missing tooling or
fallback-only evidence never degrades to a ledger objective.

For interrupted terminal closeout, revalidate root-title evidence, all Goals,
and every gate. Recovery may finish an active terminal Goal with `update_goal`
or record matching completion evidence, then release and archive idempotently;
it never reopens implementation or recreates a Goal.

## Source Snapshots

Keep one row per authoritative Feature Spec and generated issue. Preserve the
authored ref separately from the canonical runtime id:

| authoritative_source_ref | canonical_source_id | planned_done_ref | source_state | artifact_kind | canonical_repository | content_fingerprint | acceptance_ref | observed_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

For verified GitHub `owner/repository#N`, preserve the shorthand in
`authoritative_source_ref` and use
`https://github.com/owner/repository/issues/N` as `canonical_source_id` for
claims, scheduling, task identity, and takeover. A local ref similarly preserves
its path beside `git:<git-common-dir>::ref:<source-ref>`.

A local generated issue records `planned_done_ref` and begins
`source_state=active`. After substantive acceptance, integration, and required
captured domain closeout, permit one tracked active-to-done move. Atomically replace both
refs with their done-path forms, set `source_state=done`, and record Gate
Evidence. Its body fingerprint stays identical; canonical body metadata cannot
change, and only that move permits a missing old path. Both paths, neither path,
a different destination, or a changed body is drift. The root fingerprints
complete current artifacts at intake and reconciliation; changes block dispatch
or recovery until revalidated.

## Active Root Claim

This section projects `scripts/active-root-claim`, which serializes overlaps in
`~/.cache/dotagents/skills/implement-feature/claims/`. Acquire before any ledger,
Goal, task, checkout, or mutation; persist its ref, fingerprint, canonical
Git-common-directory repositories, source ids, opened time, and heartbeat.

An overlap is `needs-owner`. Before takeover, read every stale snapshot, root
scope, ledger, task ref, and current App state without mutation. Before asking
or stopping tasks, helper status must prove each heartbeat passed the fixed
five-minute stale threshold. Resolve
`stale_claim_takeover_permission=granted-by-authorized-user` first. Then require
verified non-mutating and resumable state or proven task absence, one
stop-evidence ref per root, and candidate coverage of every replaced repository
and source. Pass
`--takeover-permission granted-by-authorized-user` and
one `--expected-task-termination <root-id>=<evidence-ref>` per root; a stale
heartbeat alone is insufficient. Heartbeat and release use the acquire-time
fingerprint.

For each replaced root, pass one absolute JSON file through
`--expected-task-adoption <root-id>=<path>`. The helper validates and embeds the
file before deleting any claim. Its exact shape is:

```json
{
  "root_id": "<replaced-root-id>",
  "claim_fingerprint": "<sha256>",
  "task_termination_evidence": "<same evidence ref passed separately>",
  "specs": [
    {
      "source_spec_ref": "<exact claimed source>",
      "task_state": "recorded",
      "task_ref": "<exact visible App task ref>",
      "task_model": "<exact canonical model>",
      "task_thinking": "<medium, high, or xhigh>",
      "thinking_reason": "<evidence-backed policy decision>",
      "goal_evidence_ref": "<exact Goal evidence ref>",
      "managed_checkouts": [
        {
          "repository": "<canonical Git common directory>",
          "checkout": "<absolute App-managed checkout>",
          "target_branch_name": "<valid branch>",
          "git_top_level": "<absolute top level>",
          "baseline_revision": "<full revision>",
          "isolation_evidence_ref": "<evidence ref>"
        }
      ],
      "evidence_ref": "<stopped-and-resumable evidence ref>"
    }
  ]
}
```

Use one `specs` entry for every claimed source exactly once. For a Spec with no
created task, use `task_state: "no-task"`, `task_ref: "none"`,
the exact already-resolved `task_model`, `task_thinking`, and `thinking_reason`,
`goal_evidence_ref: "none"`, an empty `managed_checkouts` list, and an explicit
absence `evidence_ref`. A root may mix recorded and no-task entries. The helper
loads `task-model-policy.md`, validates every per-Spec task profile, and requires
every recorded task ref and managed `(repository, checkout)` pair to have one
owner across the complete takeover candidate. It verifies each recorded
checkout against the replaced repository identity, requires its current branch
to equal `target_branch_name`, proves `baseline_revision` resolves as a commit,
and requires the JSON termination evidence to match the separate CLI evidence.

Before any replaced claim is deleted, the helper atomically persists
`<candidate-root>.takeover` with the complete candidate, full replaced claims,
and adoption mappings. The journal itself owns the union scope until
finalization. Every mutating helper command first replays valid pending
transactions. For explicit recovery, read its transaction id through
`claim status`, then run `claim recover-takeover`; replay is idempotent before,
among, or after claim deletions and after candidate creation. A live replaced
claim that differs from the prepared snapshot blocks replay and remains intact.
`claim status --root-id <replaced-root>` returns the prepared transaction plus
its candidate recovery root, including after that replaced claim was deleted.
The helper accepts only schema-5 claims and schema-1 takeover journals whose
candidate and snapshots are schema 5. Unsupported state blocks every mutation
without migration, retirement, or deletion. Release after terminal proof or an
explicit durable handoff. Pass `--release-reason terminal` only after
terminal proof and `--release-reason durable-handoff` for resumable handoffs;
the helper persists the exact release receipt before deleting claim ownership.

After takeover, create or verify the new registry from the candidate claim's
embedded adoption mappings, even when recovery begins before the new ledger was
written. Cross-check an available prior ledger through its embedded
`ledger_ref`. A schema-5 no-task mapping preserves the profile resolved before
CLAIM so a later wave creates its first task with that exact profile rather than
recomputing it. Resume the same task and never allocate a second task for that
Spec. Missing or contradictory embedded evidence and an unadoptable task block
the taken-over root.

## Feature Spec Task Registry

Keep one row per implementation-eligible Feature Spec:

| source_spec_ref | feature_spec_title | task_title | task_ref | task_model | task_thinking | thinking_reason | goal_evidence_ref | managed_checkout_ref | affected_scope_ref | pull_request_refs | state | last_observed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

A Spec has at most one live task. At most three rows are nonterminal. The task
registry's `source_spec_ref` is the canonical claim/task source id and points
back to the Source Snapshots row that preserves the authoritative authored ref.
The task row points to fixed worker actions; only affected repositories and
allowed paths vary. `task_model`, `task_thinking`, and `thinking_reason` are the
exact resolved evidence from `task-model-policy.md`, not another option
registry. `task_title` is the root-resolved `<emoji> <exact authored Feature
Spec title>` UI value and never supplies identity; `source_spec_ref` and
`task_ref` remain authoritative. Every creation, steering, and resume call must
preserve the recorded profile and title.

A no-task row may hold its selected `task_title` before creation. Missing
`task_title` alone does not make an otherwise current pre-title ledger
incompatible. For a recorded task, read its live title, select and apply the
canonical title on that same task when needed, then record the observed value
before further execution. For a no-task row, resolve it at DISPATCH. This
backfill is permitted only for derived UI evidence and never repairs identity,
scope, profile, Goal, checkout, or gate state.

## Scheduling

Each wave records the ordered ready candidate refs, verified merged dependencies,
path-disjointness proof, available capacity, selected task refs, state changes,
validation, PR/review/CI, domain-knowledge closeout, and tracker-closeout
evidence, and next action. The root
sorts by canonical claim/task source id and greedily selects up to capacity; it never
persists user-selected parallelism.

## Codex Review Wait Registry

Keep one row per exact PR/head/base/merge-base tuple with its fixed 30-minute
deadline, request evidence, provider state, disposition, due time, and poll
owner.

## Gate Evidence

Keep validation, PR, current-head mergeability and repository-rule satisfaction,
review, CI, integration, domain-knowledge closeout, and tracker-closeout
evidence by Spec and repository. Do not duplicate bundle
fields into option tables. For `gate=domain-knowledge-closeout`, use
`state=captured` only and make `evidence_ref` resolve to the exact
`knowledge_delta` fingerprint, `capture_outcome=captured`, every verified named
destination, complete documentation-diff fingerprint, and the relevant
implementation revision tuples. A later material code, evidence, target, or
documentation change invalidates that row and requires the Project Memory
closeout to run again before terminal `merge-ready`.

For `gate=pr-mergeability`, bind lifecycle `OPEN`, `isDraft=false`, conflict-free
mergeability, required base-update state, required approvals, merge-queue
eligibility, and the observation time to the exact PR/head/base/merge-base tuple.
Unknown or pending state never passes.

## Recovery Packet

The packet is a compact derived projection containing source and repository
fingerprints, claim fingerprint, root-title evidence, active task refs,
managed-checkout evidence, recorded task titles and profiles, current PR tuples, current domain-closeout
evidence ref when required, due review/CI checks, next action, and evidence refs. On
resume, validate every item before mutation. Any mismatch triggers full source
and ledger reconciliation.

## External Handoffs And Closeout

Record monitoring handoffs after an exhausted review deadline and merge/closeout
handoffs after PR-ready proof. Include exact PR tuples, checks, tracker closeout
vehicle, due or next action, and evidence. Before final status require no active
task, due in-run check, newly ready Spec, or unresolved authorized work. Release
the claim only after terminal evidence or the durable handoff is persisted.

After terminal release only, archive the active ledger with
`scripts/ledger-cache` using the receipt's exact evidence ref; keep
resumable-handoff ledgers active.

## Hard Cut

Reject ledgers containing retired delivery permissions, review skips, worker
action options, parallelization, checkout strategies, adapter or lifecycle-owner
fields, stacked states, PR-count strategies, completion methods, closeout enums,
or source-provided option fingerprints. Do not migrate them in place.
