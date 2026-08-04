---
node_id: reconcile-verify
kind: validation
purpose: reconcile-and-verify-every-feature-publication-result
entry_conditions:
  - hosted-operation-returned-or-may-have-returned
inputs:
  - publication-receipts
  - partial-publication-state
  - maintenance-changelog-receipts
outputs:
  - verified-publication-evidence
  - retained-identities
  - missing-or-blocked-operations
transitions:
  - to: complete
    when: every-selected-operation-has-authoritative-readback
  - to: blocked
    when: any-result-is-ambiguous-or-required-operation-is-missing
stop_if:
  - retry-would-replay-an-uncertain-operation
side_effects:
  - read
  - hosted
terminal_states: []
---

# Reconcile and Verify

Read back every Feature, Task, relation, metadata projection, dependency
relationship, and maintenance changelog result. Distinguish verified created,
updated, reused, missing, and ambiguous operations. Retry only an operation
proven absent; preserve successful effects and block when hosted evidence cannot
establish a safe continuation.
