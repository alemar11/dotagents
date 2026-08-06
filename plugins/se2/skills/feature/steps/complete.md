---
node_id: complete
kind: terminal
purpose: report-the-complete-feature-plan-and-publication-evidence
entry_conditions:
  - preview-is-frozen-or-publication-is-verified
inputs:
  - feature-plan
  - plan-members
  - source-consolidation-decision
  - feature-acceptance-criteria
  - feature-acceptance-high-water
  - implementation-handoff
  - question-batch
  - plan-validation-evidence
  - publication-evidence
  - source-idea-lifecycle-evidence
transitions: []
stop_if: []
side_effects:
  - none
terminal_states:
  - complete
---

# Complete

Return the complete Feature Plan report. Include every repository-owned plan
member, source issue, consolidation and separation decision, outcome, scope,
non-goals, context source, acceptance criteria, assumptions, risks, critic
findings, answered question batch, validation intent, and Implement handoff.

Include the selected preview or publish operation and its evidence. For
published plans, include each Feature issue identity and the authoritative
read-after-write result. Include exact source-Idea lifecycle evidence when a
hosted Idea was promoted.

This node performs no publication, recovery, execution-unit creation, implementation
planning, or worker scheduling. It reports a plan that is ready for
se2:implement.
