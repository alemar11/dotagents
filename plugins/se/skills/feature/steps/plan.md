---
node_id: plan
kind: action
purpose: compose-the-feature-plan-set-and-local-macro-task-registries
entry_conditions:
  - feature-members-and-convergence-evidence-are-resolved
inputs:
  - feature-members
  - feature-plan-set-boundaries
  - feature-dependency-relations
  - source-consolidation-decision
  - outcome-boundaries
  - macro-task-boundaries
  - macro-dependency-relations
  - repository-context-evidence
  - answered-question-batch
  - accepted-assumptions
  - critic-analysis
  - risks
outputs:
  - feature-plan
  - feature-plan-set-registry
  - feature-acceptance-criteria
  - feature-acceptance-high-water
  - macro-task-registry
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
  - macro-task-registry-cannot-cover-the-feature-outcome
  - plan-attempts-to-prescribe-implementation-design
side_effects:
  - none
terminal_states: []
---

# Plan

Compose one Feature Plan Set using the plan template. The set contains one
narrative Feature member per genuinely distinct outcome, including when
multiple members target the same repository. The plan is intentionally
textual and explanatory, while its set identity, Feature IDs, source
references, acceptance IDs, assumptions, and question status remain stable
enough for Implement to interpret.

Include the set identity, Feature identity, problem statement, desired
outcome, scope, non-goals, source issues, repository context, usable landing
state, ownership, delivery reason, acceptance criteria, Feature-level
`blocked_by` relations, the complete local Macro Task registry, local macro
`blocked_by` relations, constraints, assumptions, risks, validation intent,
critic findings, consolidation rationale, and the handoff to Implement.
Clearly distinguish confirmed evidence, accepted assumptions, and unresolved
questions.

Write each Feature member's description from the confirmed evidence: explain
who or what is affected, what outcome is desired, what is in and out of scope,
and how success will be observed. If evidence is incomplete, record the
assumption or question instead of inventing product detail.

Keep implementation considerations useful but generic. The plan may identify
affected surfaces, architectural constraints, likely validation areas, and
integration concerns. Macro Tasks are planning projections of the Feature
outcome, not technical execution units. The plan must not prescribe code
design, allowed paths, worker assignments, or runtime scheduling claims.

Use vertical Macro Tasks when the Feature outcome admits clean, coherent
slices. If it does not, keep fewer coherent Macro Tasks and explain the
boundary; do not force a backend/frontend/test split. Feature criteria use
ordinary list items with stable F-AC-NN identities. They
describe observable product outcomes and are not execution checkboxes. Every
F-AC-NN belongs to exactly one Feature member and every Feature's criteria are
covered by at least one local Macro Task. Every Macro Task carries its
`parent_feature_id` explicitly.
