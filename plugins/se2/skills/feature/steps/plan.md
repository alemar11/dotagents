---
node_id: plan
kind: action
purpose: compose-the-structured-textual-feature-plan
entry_conditions:
  - plan-members-and-convergence-evidence-are-resolved
inputs:
  - plan-members
  - source-consolidation-decision
  - outcome-boundaries
  - repository-context-evidence
  - answered-question-batch
  - accepted-assumptions
  - critic-analysis
  - risks
outputs:
  - feature-plan
  - feature-acceptance-criteria
  - feature-acceptance-high-water
  - implementation-handoff
  - plan-publication-content
transitions:
  - to: plan-validation
    when: textual-plan-draft-is-complete
  - to: blocked
    when: required-plan-content-is-missing
stop_if:
  - outcome-or-scope-is-still-ambiguous
  - acceptance-criteria-are-not-individually-provable
  - plan-attempts-to-prescribe-implementation-design
side_effects:
  - none
terminal_states: []
---

# Plan

Compose one narrative Feature Plan per repository-owned plan member using the
plan template. The plan is intentionally textual and explanatory, while its
headings, source references, acceptance IDs, assumptions, and question status
remain stable enough for Implement to interpret.

Include the problem statement, desired outcome, scope, non-goals, source
issues, repository context, acceptance criteria, constraints, assumptions,
risks, validation intent, critic findings, consolidation rationale, and the
handoff to Implement. Clearly distinguish confirmed evidence, accepted
assumptions, and unresolved questions.

Keep implementation considerations useful but generic. The plan may identify
affected surfaces, architectural constraints, likely validation areas, and
integration concerns. It must not prescribe code design, manufacture
execution units, or make runtime scheduling claims.

Feature criteria use ordinary list items with stable F-AC-NN identities. They
describe observable product outcomes and are not execution checkboxes.
