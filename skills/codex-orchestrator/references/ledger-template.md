# Codex App Ledger Template

## Scope

Objective: <exact objective>
Repositories: <canonical Git common directories>
Sources: <stable ids and refs>

## Authorization

| field | value | source_ref | evidence_fingerprint | resolved_at |
| --- | --- | --- | --- | --- |
| `visible_app_task_permission` | `granted-by-authorized-user` | <user instruction> | <sha256> | <RFC3339> |

Add `stale_claim_takeover_permission` only when explicitly resolved for an
exact verified-stale conflict set.

## Source Snapshots

| authoritative_source_ref | canonical_source_id | planned_done_ref | source_state | artifact_kind | canonical_repository | content_fingerprint | acceptance_ref | observed_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Active Root

Root id: <id>
Atomic claim ref: <absolute claim path>
Atomic claim fingerprint: <sha256>
Repository claims: <Git common directories>
Source claims: <ids>
Opened at: <RFC3339>
Heartbeat at: <RFC3339>
Takeover transaction: <none or transaction id and prepared-journal ref>
Takeover evidence: <none or permission plus full replaced-claim snapshots, prior ledger refs, and validated per-Spec task/Goal/managed-checkout or no-task mappings>

## Feature Spec Task Registry

| source_spec_ref | feature_spec_title | task_ref | goal_evidence_ref | managed_checkout_ref | affected_scope_ref | pull_request_refs | state | last_observed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Codex Review Wait Registry

| revision_key | request_ref | provider_state | observation_fingerprint | disposition | wait_started_at | wait_deadline | due_at | poll_owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Gate Evidence

| source_spec_ref | repository | gate | state | evidence_ref | observed_at |
| --- | --- | --- | --- | --- | --- |

## Wave Reports

For each wave record ordered ready candidates, merged-dependency and
path-disjointness proof, capacity, selected task refs, state changes,
validation, PR mergeability/repository rules, review/CI,
domain-knowledge closeout, and tracker-closeout
evidence, and next action.

## Recovery Packet

Source fingerprints: <refs>
Repository fingerprints: <refs>
Atomic claim fingerprint: <sha256>
Active task refs: <refs or none>
Managed checkout evidence: <refs>
Current PR tuples: <refs or none>
Domain closeout evidence: <none or captured gate evidence ref bound to delta fingerprint, destinations, docs diff, and implementation revision tuples>
Due checks: <refs or none>
Next action: <action and target>
Evidence index: <refs>

## External Handoffs

| handoff_kind | source_spec_ref | pull_request_tuples | tracker_closeout_ref | due_or_next_action | evidence_ref |
| --- | --- | --- | --- | --- | --- |

## Notes

<bounded runtime notes only>
