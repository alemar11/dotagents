---
node_id: convergence
kind: action
purpose: converge-source-issues-into-a-feature-plan-set
entry_conditions:
  - analysis-evidence-is-available
  - material-question-batch-is-answered-or-empty
inputs:
  - normalized-source-issue-set
  - intent-analysis
  - boundary-analysis
  - feature-boundary-evidence
  - feature-dependency-evidence
  - macro-boundary-evidence
  - macro-dependency-evidence
  - critic-analysis
  - answered-question-batch
  - accepted-assumptions
  - repository-context-evidence
outputs:
  - feature-members
  - feature-plan-set-boundaries
  - feature-dependency-relations
  - source-consolidation-decision
  - outcome-boundaries
  - macro-task-boundaries
  - macro-dependency-relations
  - repository-plan-links
  - plan-input-evidence
transitions:
  - to: plan
    when: every-feature-member-has-one-coherent-owned-outcome-and-local-macro-boundary
  - to: blocked
    when: independent-boundaries-or-repository-ownership-cannot-be-resolved
stop_if:
  - feature-member-has-no-observable-outcome
  - caller-requested-split-has-no-independent-residual
  - feature-boundary-has-no-independent-landing-state-ownership-or-delivery-reason
  - macro-boundary-cannot-cover-the-feature-member
  - multi-repository-linkage-is-ambiguous
  - feature-dependency-is-missing-cross-set-or-cyclic
side_effects:
  - none
terminal_states: []
---

# Convergence

Use the residual-outcome test to decide whether source issues belong to one
Feature member or separate sibling Features. Consolidate sources that share
one independently deliverable outcome. Keep separate members only when an
exclusive observable outcome, acceptance obligation, usable landing state,
ownership boundary, or delivery reason remains. A shared integration
narrative never creates a container Feature.

For multiple repositories, produce one or more Feature members per repository
and keep each member's context local. Cross-repository Feature-level
dependencies may describe hard outcome sequencing, but they do not create an
integration issue or a stack because Git ancestry cannot cross repositories.

Record every consolidation, separation, retained out-of-scope source, and
critic challenge that affected the boundary. Do not preserve an issue count
by inventing outcomes or acceptance criteria. If a criterion spans distinct
Features, keep it in one Feature or decompose it into Feature-local criteria;
never create an integration Feature to hold the span.

Once each Feature member has one coherent outcome, decide whether it admits
clean vertical slices. When it does, define one Macro Task for each bounded
vertical view that maps to one or more Feature acceptance criteria and may
cross technical layers. When it does not, keep fewer coherent Macro Tasks and
record why a vertical split would be artificial. Do not create separate Macro
Tasks only for backend, frontend, tests, documentation, or other technical
layers.

Record Feature-level `blocked_by` relations only between Feature IDs in the
same Plan Set. Record Macro Task `blocked_by` relations only between Macro
Task IDs with the same `parent_feature_id`. Reject missing refs, duplicates,
self-edges, cross-parent edges, and cycles at the appropriate level. Require
every Feature-level edge to represent a hard outcome dependency and preserve
repository identity so Implement can project same-repository edges as stack
intent and cross-repository edges as scheduling-only. Macro-level edges remain
planning-only and may be internalized by Implement. Do not derive technical
execution units, allowed paths, execution waves, worker schedules, or
technical dependency IDs.
