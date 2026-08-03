# Contract Repair

This plugin-level contract is the common portable boundary between Feature and
Implement. It defines planning evidence and outcomes only. It contains no
runtime task, run, assignment, worktree, claim, generation, host, or operation
identity.

## Authorization And Ownership

An explicit `$se:implement` invocation authorizes every Contract Repair task
needed by that run. Do not ask for additional permission. Implement's root owns
only suspension, durable run-state, task lifecycle, monitoring, reconciliation,
and worker continuation. It never edits a Feature Spec, issue, repository, or
implementation, including through another transport skill.

Every contract mutation is performed by one separate task that explicitly
invokes `$se:feature`. Feature owns semantic repair, complete-bundle
validation, publication, and audit. The canonical task title is
`🧭 Contract Repair · <Feature Spec title>`; it is display metadata, not
identity, and the task is not a worker or part of the worker count.

## Portable Request

Accept exactly one `contract_repair_request` with:

```yaml
contract_repair_request:
  repair_id: <canonical-lowercase-uuid>
  source_spec_ref: <durable-hosted-ref>
  originating_issue_refs: [<durable-hosted-ref>, ...]
  known_issue_refs: [<durable-hosted-ref>, ...]
  conflicting_clauses: [<portable-clause-ref-and-description>, ...]
  reason: <evidence-backed-contract-conflict>
  contract_evidence_refs: [<portable-ref>, ...]
  repository_evidence_refs: [<portable-ref>, ...]
  test_evidence_refs: [<portable-ref>, ...]
  runtime_evidence_refs: [<portable-ref>, ...]
```

All keys are exact. Lists are duplicate-free; originating issues, conflicting
clauses, reason, and contract evidence are nonempty, and at least one
repository, test, or runtime evidence ref is present. `known_issue_refs` may be
empty. The packet may describe an `allowed_paths` conflict, invalid acceptance
or validation, missing or incorrect dependencies, issue-graph defects, or any
other stable semantic contradiction. It never proposes replacement bodies,
patches, or exact tracker mutations.

Reject unknown keys, proposed source refs, nonportable evidence, ambiguous
repository ownership, conflicting reuse of a repair ID, and every runtime or
control-plane identity. Runtime observations may be cited only through a
portable evidence ref whose content contains no runtime identity.

## Portable Result And Audit

Feature returns exactly:

```yaml
contract_repair_result:
  repair_id: <same-request-id>
  repair_outcome: applied | proposed | no-op | blocked
  source_spec_ref: <same-durable-ref>
  changed_artifact_refs: [<durable-or-proposed-ref>, ...]
  created_artifact_refs: [<durable-or-proposed-ref>, ...]
  superseded_artifact_refs: [<durable-or-proposed-ref>, ...]
  audit_ref: <durable-or-proposed-ref-or-null>
  readback_refs: [<durable-ref>, ...]
  completed_operations: [<semantic-operation>, ...]
  missing_operations: [<semantic-operation>, ...]
  blocker: <null-or-specific-reason>
```

The audit records the request facts, before/after artifact refs, preservation of
executor-owned checkbox/progress/evidence sections, operation order, complete
and missing operations, and authoritative readback. It contains no runtime
identity. `applied` and `no-op` require no missing operation, no blocker, and a
fresh readback of the complete Spec set and issue graph. `proposed` has no
durable completed operation. `blocked` identifies the blocker and any exact
partial-publication remainder.

## Readback, Recovery, And Replay

Feature rereads the complete bundle before deciding, immediately before every
mutation, and after publication. Publication is fail-safe: parent contracts
precede dependent issue changes; relationships and metadata follow their
artifacts; audit is appended only after the intended graph exists. A partial
result records completed and missing operations and returns `blocked`.

A retry with the same repair ID first rereads source, full graph, audit, and
result. It performs only a proven missing operation from the identical request.
Matching completion returns `no-op`; conflicting reuse, foreign drift, or an
unknown partial sequence blocks. Implement independently rereads the complete
authoritative bundle before any worker revision and reconciles task state before
retrying an uncertain creation. It never blindly creates a duplicate.
