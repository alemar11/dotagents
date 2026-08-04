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
  - source-idea-close-receipt
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
relationship, and maintenance changelog result. Require the hosted Feature body
to contain the exact current acceptance IDs, monotonic high-water marks, and
Feature-to-Task-and-Task-criterion coverage map. Distinguish verified created,
updated, reused, missing, and ambiguous operations. Retry only an operation
proven absent; preserve successful effects and block when hosted evidence cannot
establish a safe continuation.

When the published new-source bundle carried one exact hosted Idea, require an
independent readback proving that exact Idea is closed with reason `completed`
and that the retained Feature body still identifies it as tentative source
evidence. Do not require or perform Idea closure for preview, existing-source,
maintenance, or source evidence without an exact hosted Idea identity.
