---
node_id: convergence
kind: action
purpose: converge-source-issues-into-repository-owned-plan-members
entry_conditions:
  - analysis-evidence-is-available
  - material-question-batch-is-answered-or-empty
inputs:
  - normalized-source-issue-set
  - intent-analysis
  - boundary-analysis
  - critic-analysis
  - answered-question-batch
  - accepted-assumptions
  - repository-context-evidence
outputs:
  - plan-members
  - source-consolidation-decision
  - outcome-boundaries
  - repository-plan-links
  - plan-input-evidence
transitions:
  - to: plan
    when: every-plan-member-has-one-coherent-owned-outcome
  - to: blocked
    when: independent-boundaries-or-repository-ownership-cannot-be-resolved
stop_if:
  - plan-member-has-no-observable-outcome
  - caller-requested-split-has-no-independent-residual
  - multi-repository-linkage-is-ambiguous
side_effects:
  - none
terminal_states: []
---

# Convergence

Use the residual-outcome test to decide whether source issues belong to one
plan member or separate members. Consolidate sources that share one
independently deliverable outcome. Keep separate members when an exclusive
observable outcome, acceptance obligation, usable landing state, or
delivery reason remains.

For multiple repositories, produce one linked plan member per repository and
keep each member's context local. Cross-repository links describe the
relationship; they do not create an integration issue or an implementation
dependency graph.

Record every consolidation, separation, retained out-of-scope source, and
critic challenge that affected the boundary. Do not preserve an issue count
by inventing outcomes or acceptance criteria. Do not derive implementation
execution units, dependency IDs, waves, or path claims.
