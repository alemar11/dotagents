---
node_id: mutate
kind: action
purpose: apply-the-in-scope-feature-task-publication-through-g
entry_conditions:
  - hosted-state-is-compatible-and-mutation-is-in-scope
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
  - target-or-operation-is-out-of-scope
side_effects:
  - hosted
terminal_states: []
---

# Mutate

Use only the G-owned GitHub issue workflow for the normalized operations. Load
the shared
[hosted-content-safety.md](../../../references/hosted-content-safety.md), re-read
the complete current state, and apply its gate to the exact final title/body or
comment immediately before each mutation. Then create or update
repository-owned Features, link peer Features, create or attach Tasks, apply
authorized type metadata, reconcile local Task dependency relationships, and
publish the maintenance changelog comment when required. After Task identities
are resolved, create or update the Feature body with the complete acceptance
criteria, monotonic Feature and Task high-water marks, and authoritative
Feature-to-Task-and-Task-criterion coverage map. Verify operations one at a time
through the next reconciliation node.
