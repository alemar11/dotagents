---
node_id: plan-validation
kind: validation
purpose: validate-feature-plan-readiness-for-implement
entry_conditions:
  - textual-feature-plan-draft-is-available
inputs:
  - feature-plan
  - feature-acceptance-criteria
  - feature-acceptance-high-water
  - implementation-handoff
  - source-consolidation-decision
  - repository-context-evidence
  - answered-question-batch
  - accepted-assumptions
outputs:
  - plan-readiness
  - plan-validation-evidence
  - plan-blockers
transitions:
  - to: plan-publication
    when: plan-contract-is-complete
  - to: blocked
    when: plan-contract-is-invalid-or-incomplete
stop_if:
  - material-question-remains-unanswered
  - repository-identity-or-outcome-is-missing
  - acceptance-id-is-missing-duplicate-or-high-water-inconsistent
  - plan-hides-a-known-critic-conflict
side_effects:
  - none
terminal_states: []
---

# Plan Validation

Validate only the handoff contract between Feature planning and Implement.
Require an observable outcome, explicit scope and non-goals, repository
identity, source mapping, context evidence, stable Feature acceptance
criteria, validation intent, assumptions and risks, reconciled critic
findings, and a complete status for the question batch.

Confirm that the plan explains what must be true without pretending to decide
how code will be written. Reject missing or duplicate F-AC-NN identities,
decreasing feature acceptance high-water, hidden material questions,
unresolved repository ownership, unsupported assumptions, or a plan that
contains execution-graph or worker-readiness claims.

Do not validate implementation units, dependency edges, current Git HEADs,
worktree state, worker capacity, or PR readiness. Those are Implement
responsibilities.
