---
node_id: complete
kind: terminal
purpose: report-the-complete-feature-plan-set-and-macro-projections
entry_conditions:
  - preview-is-frozen-or-publication-is-verified
inputs:
  - feature-plan
  - feature-plan-set-registry
  - feature-plan-set-projection
  - feature-members
  - source-consolidation-decision
  - feature-acceptance-criteria
  - feature-acceptance-high-water
  - macro-task-registry
  - macro-task-projection
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

Return the complete Feature Plan Set report. Include the set identity and
revision, every Feature member and repository, source issue, consolidation
and separation decision, outcome, scope, non-goals, context source, usable
landing state, ownership, delivery reason, Feature-level dependencies, local
acceptance criteria, the complete local Macro Task registry and macro
dependency relations, assumptions, risks, critic findings, answered question
batch, validation intent, and Implement handoff.

Include the selected preview or publish operation and its evidence. For
published sets, include every parent Feature identity, every child Macro
Task identity, the final set registry, the verified Feature/Macro boundaries,
and the authoritative read-after-write results. Include exact source-Idea
lifecycle evidence when a hosted Idea was promoted.

This node performs no publication, recovery, technical execution-unit
creation, implementation planning, or worker scheduling. It reports the
complete Feature Plan Set and its sibling Feature/Macro projections that are
ready for se:implement.
