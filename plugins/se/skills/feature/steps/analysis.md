---
node_id: analysis
kind: action
purpose: run-grounded-and-independent-parallel-problem-analysis
entry_conditions:
  - normalized-source-issue-set-and-repository-identities-are-available
inputs:
  - normalized-intent
  - normalized-source-issue-set
  - affected-repositories
  - repository-identities
outputs:
  - repository-context-evidence
  - intent-analysis
  - boundary-analysis
  - feature-boundary-evidence
  - feature-dependency-evidence
  - macro-boundary-evidence
  - macro-dependency-evidence
  - question-candidates
  - critic-analysis
  - assumptions
  - risks
  - analysis-provenance
transitions:
  - to: clarification
    when: material-question-batch-remains
  - to: convergence
    when: evidence-is-sufficient-and-no-blocking-question-remains
  - to: blocked
    when: required-context-or-analysis-cannot-be-established
stop_if:
  - repository-context-cannot-be-read
  - analysis-workers-return-unreconciled-authority-conflict
  - source-set-cannot-be-grounded
side_effects:
  - none
terminal_states: []
---

# Analysis

For every affected repository, read the applicable AGENTS.md hierarchy and the
documents and code it requires for safe planning. Record the sources and facts
used; do not invent a context-document taxonomy.

When delegation is available, the planner may dispatch bounded read-only
analysts with distinct responsibilities. Otherwise run the same assignments
serially. Every assignment receives the same immutable intent and source set,
returns evidence or proposals, and remains unable to publish, edit the plan,
or ask the user directly.

Run these analytical lenses when useful:

- intent and source normalization;
- repository context and affected-surface analysis;
- multi-issue boundary and residual-outcome analysis;
- acceptance, validation, risk, and documentation analysis;
- independent critic analysis.

The critic analyst receives the original problem and repository snapshot
without the planner draft or context-derived requirements during its first
pass. It challenges assumptions, unnecessary constraints, missing outcomes,
and possible conflicts with repository instructions. It remains read-only and
must separate evidence from speculation. A critic does not override AGENTS.md;
it produces a conflict or question for the parent planner to reconcile.

The planner aggregates all worker results once, preserves provenance, removes
duplicate questions, and separates:

- confirmed evidence;
- accepted assumptions;
- competing interpretations;
- material questions for the user;
- non-blocking risks and follow-up suggestions.

Identify candidate Feature boundaries and evidence for whether each outcome
has a separate usable landing state, ownership, acceptance obligation, or
delivery reason. Record candidate Feature-level `blocked_by` relations and
their evidence for later Plan Set composition only when one outcome is a hard
prerequisite, not merely preferred order. Preserve both repository identities:
Implement projects a same-repository relation as mandatory stack intent and a
cross-repository relation as scheduling-only. Identify candidate Macro Task
areas and evidence-backed local macro `blocked_by` relationships. Keep both
levels vertical at the product/capability level and do not split by technical
layer. Do not create Feature containers or cross-Feature Macro Task edges.
Do not derive technical execution units, allowed paths, execution waves,
worker schedules, or technical dependency IDs in this node. Those belong to
Implement.
