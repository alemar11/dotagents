---
node_id: analysis
kind: action
purpose: gather-evidence-and-identify-material-decisions
entry_conditions:
  - intake-resolved-sources-repositories-and-scope
inputs:
  - normalized_source_set
  - affected_repositories
  - repository_and_source_evidence
  - existing_plan_evidence
  - bounded_plan_scope
  - answered_questions
  - accepted_assumptions
outputs:
  - problem_and_user_analysis
  - source_and_boundary_evidence
  - repository_context_evidence
  - constraints_assumptions_and_risks
  - material_question_batch
  - clarification_context
  - plan_inputs
transitions:
  - to: clarification
    when: one-or-more-material-product-decisions-remain
  - to: plan
    when: evidence-and-decisions-are-sufficient
  - to: blocked
    when: required-planning-evidence-cannot-be-established
stop_if:
  - evidence-and-speculation-cannot-be-distinguished
  - repository-ownership-or-feature-boundary-remains-unknowable
side_effects:
  - read
terminal_states: []
---

# Analysis

Study the user or product problem, affected actors, observable outcome,
repository context, source relationships, constraints, assumptions, risks, and
validation intent. Separate evidence from inference. Optional read-only helpers
may study independent repositories or challenge assumptions, but the planner
reduces their results and serial work is always valid.

Identify only material product decisions: outcome, scope, behavior,
compatibility, migration, data, safety, rollout, ownership, or hard Feature
dependencies. A complete brief, an explicitly delegated choice, or a safe
assumption does not require a question. Technical code design, implementation
decomposition, allowed paths, worker topology, and validation commands that can
be derived from repository evidence belong to the later implementation
workflow. Feature records only outcome-level validation intent.

When questions remain, produce one smallest-complete batch with the decision,
why it matters, options, recommendation, and evidence. Otherwise pass the
bounded evidence directly to Plan.

On re-entry after Clarification, incorporate the answers and rerun only the
analysis they affect. Do not restart task creation, repository discovery, or
unrelated evidence gathering.
