---
node_id: mutate
kind: action
purpose: apply-the-authorized-feature-task-publication-through-g
entry_conditions:
  - hosted-state-is-compatible-and-mutation-is-authorized
inputs:
  - mutation-ready-publication
  - current-feature-task-state
outputs:
  - publication-receipts
  - partial-publication-state
  - maintenance-changelog-receipts
transitions:
  - to: reconcile-verify
    when: hosted-operation-returned-or-may-have-returned
stop_if:
  - mutation-authority-is-missing
side_effects:
  - hosted
terminal_states: []
---

# Mutate

Use only the G-owned GitHub issue workflow for the normalized operations. Re-read
the complete current state immediately before mutation, then create or update
repository-owned Features, link peer Features, create or attach Tasks, apply
authorized type metadata, reconcile local Task dependency relationships, and
publish the maintenance changelog comment when required. Verify operations one
at a time through the next reconciliation node.
