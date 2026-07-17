# Codex App Orchestration Ledger

## Resolution

Use one ledger per overlapping repository/source portfolio under
`~/.cache/dotagents/skills/implement-feature/ledgers/`. Create it only after
atomic claim acquisition. A missing ledger loads `ledger-template.md`; an
incompatible current ledger blocks rather than being migrated.

The ledger is evidence, not a second option registry or concurrency primitive.
Record only:

- run authorization and exceptional takeover evidence;
- authoritative source refs, derived canonical claim/task source ids, and
  root-computed fingerprints;
- active-root claim ownership;
- visible task, Goal, managed-checkout, and resolved task-profile state;
- PR revision, mergeability/repository rules, review, CI, validation,
  domain-knowledge closeout, and
  tracker-closeout proof;
- deterministic scheduling waves and recovery state;
- external monitoring, merge, and closeout handoffs.

## Authorization

Persist `visible_app_task_permission=granted-by-authorized-user` with its exact
run-scoped evidence. Add `stale_claim_takeover_permission` only when a takeover
question is actually resolved. Do not store fixed policy, derived state, bundle
data, or retired option rows as authorization.

## Source Snapshots

Keep one row per authoritative Feature Spec and generated issue. Preserve the
authored ref separately from the canonical runtime id:

| authoritative_source_ref | canonical_source_id | planned_done_ref | source_state | artifact_kind | canonical_repository | content_fingerprint | acceptance_ref | observed_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

For a verified GitHub `owner/repository#N` Feature Spec, store that shorthand in
`authoritative_source_ref` and
`https://github.com/owner/repository/issues/N` in `canonical_source_id`. Use the
canonical id for claims, scheduling, task identity, and takeover. For a local
ref, store the authored path separately from its
`git:<git-common-dir>::ref:<source-ref>` canonical id.

For a local generated issue, record its exact predeclared destination in
`planned_done_ref` and start with `source_state=active`. After substantive
acceptance, integration, and any required captured domain-knowledge closeout,
permit exactly one
active-path-to-planned-done-path transition. The task performs the tracked move;
then atomically replace the row's authoritative ref and git-qualified canonical
id with the done-path forms and set `source_state=done`, while recording move
evidence in Gate Evidence. The body fingerprint must remain identical; no
current canonical closeout metadata mutation is allowed. The missing old path is
therefore expected only for this exact transition. Both paths existing, neither
path existing, another destination, or any body change is source drift.

The root computes fingerprints from complete current artifacts during intake
and reconciliation. A changed fingerprint invalidates dispatch or recovery
until the bundle is revalidated.

## Active Root Claim

The Markdown section is a projection. Use `scripts/orchestrator-claim`, which
serializes overlap checks under one filesystem lock in
`~/.cache/dotagents/skills/implement-feature/claims/`. Acquire before ledger,
Goal, task, managed checkout, or mutation. Persist the returned claim ref,
fingerprint, canonical Git-common-directory repositories, source ids, opened
time, and heartbeat.

An overlapping claim blocks as `needs-owner`. Before takeover, read the exact
stale snapshots, complete root scopes, ledgers, recorded task refs, and current
App state without mutation. Resolve
`stale_claim_takeover_permission=granted-by-authorized-user` before interrupting
or terminating a task. After the grant, require verified non-mutating and
resumable state or proven task absence, one task-stop evidence ref per root, and
full candidate coverage of every replaced repository and source. Pass
`--takeover-permission granted-by-authorized-user`; a stale heartbeat alone is
insufficient. Every heartbeat and release uses the acquire-time fingerprint.

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
A schema-1 journal carrying a schema-4 candidate remains replayable after this
hard cut. Because its adoption evidence has no canonical task profile, recovery
finalizes it only as a schema-4 legacy ownership claim; it never invents model
settings or resumes the task as current.

The helper reports schema-3 and schema-4 claims as legacy and permits only exact-owner
`retire-legacy` with the stored fingerprint plus terminal or durable-handoff
evidence; it never migrates them. Release after terminal proof or an explicit
durable handoff.

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

| source_spec_ref | feature_spec_title | task_ref | task_model | task_thinking | thinking_reason | goal_evidence_ref | managed_checkout_ref | affected_scope_ref | pull_request_refs | state | last_observed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

A Spec has at most one live task. At most three rows are nonterminal. The task
registry's `source_spec_ref` is the canonical claim/task source id and points
back to the Source Snapshots row that preserves the authoritative authored ref.
The task row points to fixed worker actions; only affected repositories and
allowed paths vary. `task_model`, `task_thinking`, and `thinking_reason` are the
exact resolved evidence from `task-model-policy.md`, not another option
registry. Every creation, steering, and resume call must preserve them.

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
fingerprints, claim fingerprint, active task refs, managed-checkout evidence,
recorded task profiles, current PR tuples, current domain-closeout evidence ref
when required, due review/CI checks, next action, and evidence refs. On
resume, validate every item before mutation. Any mismatch triggers full source
and ledger reconciliation.

## External Handoffs And Closeout

Record monitoring handoffs after an exhausted review deadline and merge/closeout
handoffs after PR-ready proof. Include exact PR tuples, checks, tracker closeout
vehicle, due or next action, and evidence. Before final status require no active
task, due in-run check, newly ready Spec, or unresolved authorized work. Release
the claim only after terminal evidence or the durable handoff is persisted.

## Hard Cut

Reject ledgers containing retired delivery permissions, review skips, worker
action options, parallelization, checkout strategies, adapter or lifecycle-owner
fields, stacked states, PR-count strategies, completion methods, closeout enums,
or source-provided option fingerprints. Do not migrate them in place.
