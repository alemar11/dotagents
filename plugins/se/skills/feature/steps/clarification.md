---
node_id: clarification
kind: decision
purpose: resolve-one-consolidated-batch-of-material-user-questions
entry_conditions:
  - analysis-produced-material-question-candidates
inputs:
  - question-candidates
  - analysis-provenance
  - affected-repositories
outputs:
  - answered-question-batch
  - accepted-assumptions
  - rejected-assumptions
transitions:
  - to: convergence
    when: one-complete-question-batch-has-been-answered
  - to: blocked
    when: a-required-decision-is-declined-or-remains-unresolved
stop_if:
  - user-answer-would-change-the-authorized-repository-set
  - evidence-remains-contradictory-after-the-batch
side_effects:
  - none
terminal_states: []
---

# Clarification

Present every material question discovered by the analysis in one consolidated
batch. Do not ask one question per worker or create a graph node for each
question. Each item must include a stable question ID, the requested decision,
why it matters, affected outcome or scope, available options, recommendation,
`question_blocking` value, and originating evidence.

The task may remain in awaiting-user-input while the batch is shown. This is a
wait state, not a terminal blocked result and not a reason to mark the run's
goal blocked. Resume the same planning task and preserve the original question
IDs when the user replies.

A question is blocking when it changes the product outcome, repository
ownership, plan boundary, scope, acceptance criteria, or an essential safety
constraint. Non-blocking questions become explicit assumptions and retain
their impact. Technical implementation choices are not Feature clarification
questions; Implement owns them.

After the complete user response is reconciled, carry accepted decisions and
assumptions to Convergence. If the user declines a required decision or
changes the authorized repository set, stop with the smallest recovery input.
