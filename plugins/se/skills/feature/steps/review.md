---
node_id: review
kind: validation
purpose: verify-semantic-quality-and-structural-plan-invariants
entry_conditions:
  - complete-feature-plan-set-draft-is-available
inputs:
  - feature_plan_set_draft
  - source_and_boundary_evidence
  - answered_questions
  - accepted_assumptions
  - prior_review_findings
outputs:
  - review_result
  - review_findings
  - planner_dispositions
  - material_question_batch
  - clarification_context
  - publication_ready_plan
transitions:
  - to: plan
    when: correctable-findings-exist-and-revision-is-making-progress
  - to: clarification
    when: review-exposes-a-new-material-product-decision
  - to: publish
    when: semantic-and-structural-review-is-clean
  - to: blocked
    when: findings-repeat-without-progress-or-required-evidence-is-unavailable
stop_if:
  - planner-would-self-certify-without-performing-a-separate-review-lens
  - clean-result-would-ignore-a-structural-invariant
side_effects:
  - read
terminal_states: []
---

# Review

Perform a distinct adversarial review of the complete draft. Use a read-only
helper when useful and available; otherwise review serially after setting aside
the drafting perspective. Delegation provenance is informative, not a gate.

Review the original intent, evidence, decisions, assumptions, and plan. Verify:

- stable Plan Set, Feature, F-AC, Macro, and revision identities;
- genuine sibling boundaries and absence of a container Feature;
- observable, non-duplicative F-ACs with monotonic high-water marks;
- complete F-AC coverage by closed, nontechnical Macro registries;
- no Macro scope expansion and only same-parent Macro edges;
- acyclic Feature and Macro graphs;
- correct repository mapping and stack-versus-scheduling semantics;
- complete source provenance, risk, validation, and implementation handoff;
- preservation of hosted identities, unaffected content, and executor-owned
  progress for existing-source revisions;
- complete preview or hosted projection mappings for every planned artifact.

Return correctable findings to Plan while each revision makes progress. Send a
newly exposed material decision to Clarification. A repeated unresolved finding
or no-progress revision blocks. When clean, pass the reviewed plan directly to
Publish; do not add a separate validation node or round-count protocol.
