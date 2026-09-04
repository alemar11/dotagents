---
node_id: clarification
kind: action
purpose: refine-unready-planning-inputs-through-grilling
entry_conditions:
  - analysis-or-review-left-planning-not-ready-or-exposed-a-material-product-decision
inputs:
  - clarification_brief
  - clarification_context
outputs:
  - refined_clarification_handoff
  - answered_questions
  - accepted_assumptions
  - unresolved_material_decisions
transitions:
  - to: analysis
    when: refined-or-best-supported-input-is-available-and-material-decisions-are-resolved-or-safely-assumed
  - to: blocked
    when: grilling-is-blocked-or-a-required-decision-is-declined
stop_if:
  - planner-would-guess-a-material-product-decision
  - planner-would-author-a-consolidated-question-batch-instead-of-composing-grilling
  - repeated-review-clarification-shows-the-plan-is-not-converging
side_effects:
  - none
terminal_states: []
---

# Clarification

Compose the bundled `$se:grilling` contract in the same Feature planner flow.
Give Grilling the clarification brief and let it read applicable context, select
the highest-leverage ambiguity, and ask exactly one focused question per turn
with a concrete recommendation. Do not answer for the user, create another
controller, launch Study, split questions into a batch, or bypass the interview.

On a refined handoff, record answers, `delegated-choice` provenance, and safe
assumptions, then return to Analysis so the affected evidence and boundaries can
be reconciled. On `user-stopped`, use the best-supported handoff only when every
remaining material unknown is explicitly safe as an assumption; otherwise block.
Do not treat the wait as a blocked task and do not persist a workflow checkpoint.

Review may expose one previously hidden material decision. Return it through the
same Grilling composition, then rebuild the plan. If review repeatedly discovers
new material decisions or the user declines one required to define the Feature,
stop rather than guessing.
