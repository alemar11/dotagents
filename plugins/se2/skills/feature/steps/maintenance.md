---
node_id: maintenance
kind: action
purpose: rehydrate-and-revise-an-existing-feature-plan
entry_conditions:
  - existing-published-plan-and-explicit-maintenance-indication-are-available
inputs:
  - existing-feature-plan
  - source-issues
  - external-indication
  - repository-identities
outputs:
  - rehydrated-plan
  - maintenance-evidence
  - entry_route
  - source_route
transitions:
  - to: analysis
    when: plan-identity-and-maintenance-indication-are-reconciled
  - to: blocked
    when: target-or-indication-is-ambiguous
stop_if:
  - maintenance-would-silently-change-plan-identity
  - hosted-rehydration-cannot-be-authoritatively-read
side_effects:
  - none
terminal_states: []
---

# Maintenance

Start from the existing published Feature Plan and the explicit external
indication. Rehydrate the current plan, preserve its stable identity and
acceptance IDs, and carry only the requested semantic change into Analysis.

For an existing-source route, run the shared G dependency preflight before the
first hosted rehydration read. Do not rehydrate or infer execution units,
dependencies, or implementation state. An unclear, contradictory, foreign, or missing target
transitions to blocked with the smallest recovery input.

Maintenance uses the same analysis, critic, question-batch, convergence, plan,
validation, and publication path as a new plan. It does not create a separate
maintenance graph.
