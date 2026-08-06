---
node_id: maintenance
kind: action
purpose: rehydrate-and-revise-an-existing-feature-plan-set
entry_conditions:
  - existing-published-plan-and-explicit-maintenance-indication-are-available
inputs:
  - existing-feature-plan-set
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

Start from the existing published Feature Plan Set and the explicit external
indication. Rehydrate the current set, preserve its set identity/revision,
Feature identities, parent issue refs, Feature-level dependencies, acceptance
IDs, Macro Task identities, and child issue refs, and carry only the requested
semantic change into Analysis.

For an existing-source route, run the shared G dependency preflight before the
first hosted rehydration read. Rehydrate the authoritative Feature Plan Set,
every sibling Feature, each local Macro Task registry, child Task identities,
and both Feature-level and macro-local planning relations. Reject missing,
duplicate, cross-set, cross-parent, or cyclic relations. Do not rehydrate or
infer technical execution units, technical dependencies, or implementation
state. An unclear, contradictory, foreign, or missing target transitions to
blocked with the smallest recovery input.

Maintenance uses the same analysis, critic, question-batch, convergence, plan,
validation, and publication path as a new Plan Set. It does not create a
separate maintenance graph.
