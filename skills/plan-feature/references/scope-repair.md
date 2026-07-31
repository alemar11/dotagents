# Scope Repair

Load this reference only when a separately invoked Plan Feature task receives
an exact `scope_repair_request` for a durable `existing-source` bundle.
`scope-repair` is a narrow internal branch of that route, not a selectable
option or a third `source_route`.

## Boundary

Scope repair authorizes the smallest complete monotonic expansion of
`allowed_paths` needed to satisfy an already accepted requirement, acceptance
criterion, or validation obligation. It does not authorize a new outcome,
repository, branch, dependency, acceptance criterion, safety policy, validation
policy, issue slice, or implementation approach.

Plan Feature owns the planning mutation. It remains unaware of Codex task IDs,
workers, worktrees, claims, queues, assignment generations, runtime collisions,
and implementation progress. Reject a request containing those runtime fields
instead of persisting them in a Feature Spec, issue, audit record, or result.

## Request Contract

Accept exactly:

```yaml
scope_repair_request:
  repair_id: <canonical-lowercase-uuid>
  source_spec_ref: <durable-hosted-ref>
  implementation_issue_ref: <durable-hosted-ref>
  requested_paths:
    - <portable-repo-relative-or-repo-qualified-path>
  reason: <why-current-scope-cannot-deliver-an-existing-obligation>
  contract_evidence_refs:
    - <existing-requirement-acceptance-or-validation-ref>
  evidence_refs:
    - <portable-repository-or-test-evidence-ref>
```

Require nonempty, duplicate-free `requested_paths`, `contract_evidence_refs`,
and `evidence_refs` lists. Reject absolute paths, parent traversal, ambiguous
repository ownership, proposed refs, unknown keys, runtime identities, and a
`repair_id` reused with different request content. The source and issue refs
must identify one issue in the complete current bundle.

The request is intake data. `references/options.md` continues to own the sole
selectable field `write_mode`.

## Validation

Reread the complete Feature Spec set and complete durable issue graph before
deciding or writing. Preserve current executor-owned checkbox markers and
mutable execution sections from that read.

For the named issue:

1. Prove every requested path is needed by at least one supplied existing
   contract evidence ref and its repository evidence. A reason without
   evidence is insufficient.
2. Apply the canonical allowed-path scope table in `spec-phase.md`. Authorize
   the smallest complete envelope, which may be a stable prefix broader than
   the literal requested file.
3. Require the previous Feature Spec paths to be a subset of the proposed
   Feature Spec paths and the previous issue paths to be a subset of the
   proposed issue paths.
4. Require every requested path to be contained by the proposed issue envelope
   and every implementation path in that issue envelope to be contained by the
   owning Feature Spec envelope.
5. Compare every other stable field directly and require exact equality.
   Preserve all current executor-owned content. Do not use a whole-body hash.
6. Rerun bundle completeness, acceptance coverage, issue-graph, verticality,
   overlap, dependency, and GitHub tracker validation. A temporary runtime collision
   does not create a planning dependency. If the overlap represents a real
   output dependency or unsafe independent ownership, return
   `full-replan-required`.
7. In a linked set, change only the owning member and its named issue. A path
   belonging to another repository/member is `full-replan-required`.

Classify the result:

| Current state | Result |
| --- | --- |
| Requested work is already contained by both Spec and issue | `no-op` |
| Spec contains the work but the issue does not | expand the issue only |
| Neither contains the work | expand the Spec, then the issue |
| Issue contains work outside the Spec | `blocked` as an inconsistent bundle |
| Another stable field or repository/member must change | `full-replan-required` |

## Mutation And Recovery

With `write_mode=propose`, write nothing. Return the complete proposed Spec and
issue changes, audit entry, mutation order, and `repair_outcome=proposed`.

With `write_mode=apply`, reread every target immediately before its mutation and
stop on drift. Apply in this fail-safe order:

1. widen the Feature Spec when required;
2. widen the named implementation issue;
3. append the audit record;
4. reread and validate the complete bundle.

A wider parent with a still-narrow child remains non-executable. Never reverse
the first two steps, because that would temporarily authorize an issue outside
its Feature Spec.

Append the audit as a canonical comment on the implementation issue. The record contains only
`repair_id`, source and issue refs, requested paths, previous and authorized
envelopes, reason, contract evidence, repository evidence, and completed
operations. It contains no runtime identity.

After a partial apply, return `repair_outcome=blocked`, the completed and missing
operations, and exact readback refs. A retry with the same `repair_id` rereads
the request, audit, Spec, and issue; it performs only an exact missing operation.
An already completed matching repair returns `no-op`. Conflicting reuse, foreign
edits, or an unrecognized partial sequence blocks without overwrite.

## Result Contract

Return exactly:

```yaml
scope_repair_result:
  repair_id: <same-request-id>
  repair_outcome: applied | proposed | no-op | blocked | full-replan-required
  source_spec_ref: <same-durable-ref>
  implementation_issue_ref: <same-durable-ref>
  previous_spec_allowed_paths: [...]
  authorized_spec_allowed_paths: [...]
  previous_issue_allowed_paths: [...]
  authorized_issue_allowed_paths: [...]
  changed_artifact_refs: [...]
  audit_ref: <durable-ref-or-null>
  readback_refs: [...]
  completed_operations: [...]
  missing_operations: [...]
  blocker: <null-or-specific-reason>
```

`applied` and `no-op` are resumable evidence only after the final complete-bundle
readback succeeds. The invoking runtime independently rereads authoritative
sources and decides scheduling; Plan Feature never declares a worker runnable.
