---
node_id: feature
kind: action
purpose: create-review-or-reconcile-the-feature-definition-and-feature-issue
entry_conditions:
  - bounded-intent-or-rehydrated-feature-bundle-is-available
inputs:
  - normalized-intent
  - resolved-intent
  - feature-boundary-analysis
  - resolved-feature-boundary
  - accepted-assumptions
  - source_route
  - entry_route
  - rehydrated-bundle
  - maintenance-evidence
  - affected-repositories
  - repository-context
  - documentation-update-candidates
outputs:
  - feature-boundary-decision
  - feature-definition
  - feature-issue
  - feature-issue-ref
  - feature-set
  - acceptance-criteria
  - feature-acceptance-high-water
  - linked-feature-references
  - feature-type-projection
  - documentation-update-plan
  - maintenance-feature-delta
transitions:
  - to: tasks
    when: feature-definition-and-feature-identity-are-stable
  - to: blocked
    when: feature-definition-or-feature-relationship-is-conflicted
stop_if:
  - feature-boundary-analysis-is-missing-or-unresolved
  - acceptance-criteria-are-not-individually-provable
  - acceptance-criterion-id-is-missing-duplicate-or-reused
  - feature-acceptance-high-water-is-missing-or-decreases
  - feature-target-is-ambiguous
  - repository-scope-is-missing
side_effects:
  - none
terminal_states: []
---

# Feature

Create, review, or reconcile one repository-owned Feature definition and its
Feature issue for each affected repository. The Feature definition is the
canonical contract: outcome, non-goals, requirements, repository/path scope,
context evidence, acceptance criteria, safety constraints, documentation
updates, and validation policy. There is no separate Spec entity.

Before freezing a new Feature identity, verify the Intake boundary analysis.
Retain the smallest coherent boundary whose outcome is independently valuable
and separately deliverable. Fold every candidate without an exclusive
observable residual into this Feature and preserve its distinct work as Task
scope. Record the candidates, residual-outcome evidence, final consolidation,
and any independently deliverable candidate intentionally left for a separate
Feature run. Block rather than publishing overlapping Feature identities.

For a new Feature, render templates/feature.md. For an existing Feature,
preserve its identity and stable content, compare it with the explicit
maintenance indication when present, and calculate only justified updates.
Require unique, individually provable acceptance criteria with stable IDs and a
failure policy for constrained validation before Tasks are derived. Render each
criterion as `- [F-AC-NN] <criterion>`, starting at `F-AC-01`. Keep IDs unique
within the Feature, retain them across non-semantic wording clarification and
reordering, and never reuse a retired ID. A semantic replacement receives the
next ID above the durable `feature_acceptance_high_water`, then advances that
monotonic high-water mark. Bracketed IDs are contract identity, not Markdown
checkboxes or execution state; do not render `[ ]` or `[x]` markers. The
uppercase ID spelling is an explicit external rendered-contract syntax
exception to the repository's normal lower-kebab assigned-value rule.

In a multi-repository feature, create or retain exactly one Feature per
repository and link those Features with globally qualified issue references or
URLs. Do not create an integration Feature or issue. The GitHub type `Feature`
is publication metadata; the definition and Feature relation carry the
semantics.

Carry only documentation updates justified by the repository instruction
hierarchy or accepted requirements. Keep them owned by the Feature or a Task.
On duplicate, stale, foreign, or conflicting state, block instead of silently
overwriting it.
