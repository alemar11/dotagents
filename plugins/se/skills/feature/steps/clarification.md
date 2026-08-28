---
node_id: clarification
kind: decision
purpose: resolve-material-product-decisions
entry_conditions:
  - analysis-or-review-produced-a-material-question-batch
inputs:
  - material_question_batch
  - clarification_context
outputs:
  - answered_questions
  - accepted_assumptions
  - unresolved_material_decisions
transitions:
  - to: analysis
    when: required-answers-or-safe-assumptions-are-available
  - to: blocked
    when: a-required-decision-is-declined-or-cannot-be-obtained
stop_if:
  - planner-would-guess-a-material-product-decision
  - repeated-review-clarification-shows-the-plan-is-not-converging
side_effects:
  - none
terminal_states: []
---

# Clarification

Present one concise consolidated question batch and wait nonterminally for the
user. Keep recommendations clear and avoid one-question-per-turn churn.

Record answers and safe user-approved assumptions, then return to Analysis so
the affected evidence and boundaries can be reconciled. Do not treat the wait
as a blocked task and do not persist a workflow checkpoint.

Review may expose one previously hidden material decision. Ask it as the
smallest follow-up batch, then rebuild the plan. If review repeatedly discovers
new material decisions or the user declines one required to define the Feature,
stop rather than guessing.
