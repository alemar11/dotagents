---
node_id: hosted-checks
kind: validation
purpose: verify-current-hosted-feature-state-before-mutation
entry_conditions:
  - g-dependency-is-available
inputs:
  - normalized-feature-publication
  - g-dependency-evidence
outputs:
  - current-feature-task-state
  - duplicate-and-collision-evidence
  - mutation-ready-publication
transitions:
  - to: mutate
    when: hosted-state-is-compatible-and-mutation-is-authorized
  - to: blocked
    when: duplicate-collision-or-hosted-contract-conflict-is-unresolved
stop_if:
  - hosted-state-is-ambiguous
side_effects:
  - read
  - hosted
terminal_states: []
---

# Hosted Checks

Read the current Feature set, Task state, relations, labels, issue types,
acceptance IDs, monotonic acceptance high-water marks, hosted acceptance
coverage, and collision evidence through the G-owned issue workflow. Reconcile
the frozen bundle against that state before mutation. Do not silently overwrite
a foreign, stale, duplicate, or contradictory hosted object.
