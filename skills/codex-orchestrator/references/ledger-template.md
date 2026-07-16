# Codex App Ledger Template

## Scope

Objective: <exact objective>
Repositories: <canonical realpaths>
Sources: <stable ids/refs>

## Option Resolution

authorization_resolution: per-workstream

| scope_id | field | value | source | source_ref | fingerprint | resolved_at |
| --- | --- | --- | --- | --- | --- | --- |

## Discovery Sources

| source_id | source_ref | repository | fingerprint | acceptance_ref | closeout_target |
| --- | --- | --- | --- | --- | --- |

## Active Root

Root id: <id>
Atomic claim ref: <absolute claim path>
Atomic claim fingerprint: <sha256>
Goal mode: active|unavailable
Goal evidence: <ref>
Repository claims: <realpaths>
Source claims: <ids>
Opened at: <RFC3339>
Heartbeat at: <RFC3339>
Takeover evidence: <none or ref>

## Codex Review Wait Registry

| revision_key | request_ref | provider_state | observation_fingerprint | result_disposition | wait_profile | wait_started_at | wait_deadline | due_at | poll_owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Feature Spec Task Registry

| feature_spec_ref | feature_spec_title | task_ref | task_evidence_ref | workstream_ids | repository_refs | pull_request_refs | lifecycle_owner | state | last_observed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Worker evidence:

- feature_spec_ref=<ref>; task_ref=<visible task id>;
  managed_checkouts=<repository checkout refs>;
  parallelism=<parallel|sequential>; fallback_reason=<none or evidence>.

## Parent Closeout Handoff

| source_spec_ref | closeout_vehicle | state | evidence | external_next_action |
| --- | --- | --- | --- | --- |

## Recovery Packet

Option fingerprint: <hash>
Repository fingerprints: <refs>
Active task refs: <refs or none>
Due gates/checks: <refs or none>
Next action: <action and target>
Evidence index: <refs>

## Gate Policy

| scope_id | gate | requirement | state | evidence |
| --- | --- | --- | --- | --- |

## Workstreams

### active

### needs-owner

### ready-next

### blocked

### deferred

### completed

### released

Each workstream row records source/spec, repositories/paths, dependencies,
allowed actions, delivery and issue permissions, task ref, evidence, gates,
lifecycle state, and next action.

## Wave Reports

Record selected Specs, dependency proof, slots, task refs, changes, validation,
delivery, reconciliation, and recovery update.

## Runtime Metrics

Record exact phase counters only when measured over an uncontaminated interval;
otherwise use `unavailable`.

## Notes

<bounded durable runtime notes>
