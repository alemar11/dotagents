---
node_id: plan-validation
kind: validation
purpose: validate-feature-plan-set-and-local-macro-readiness-for-implement
entry_conditions:
  - critic-reviewed-feature-plan-set-is-clean
inputs:
  - planning-depth
  - clarification-route
  - clarification-route-evidence
  - feature-plan
  - feature-plan-set-registry
  - feature-acceptance-criteria
  - feature-acceptance-high-water
  - macro-task-registry
  - implementation-handoff
  - source-consolidation-decision
  - repository-context-evidence
  - answered-question-batch
  - accepted-assumptions
  - plan-review-result
  - plan-review-findings
  - plan-review-dispositions
  - plan-review-evidence
  - plan-review-round
  - plan-review-provenance
outputs:
  - plan-readiness
  - plan-validation-evidence
  - macro-task-validation-evidence
  - feature-dependency-validation-evidence
  - plan-blockers
transitions:
  - to: plan-publication
    when: plan-contract-is-complete
  - to: blocked
    when: plan-contract-is-invalid-or-incomplete
stop_if:
  - plan-review-result-is-not-clean
  - plan-review-evidence-or-dispositions-are-missing
  - plan-review-provenance-is-missing-or-contradicts-observed-delegation
  - material-question-remains-unanswered
  - planning-depth-is-missing-or-inconsistent-with-evidence
  - clarification-route-is-missing-or-invalid-for-planning-depth
  - question-free-route-lacks-required-evidence
  - repository-identity-or-outcome-is-missing
  - acceptance-id-is-missing-duplicate-or-high-water-inconsistent
  - feature-plan-set-registry-is-missing-incomplete-or-duplicated
  - feature-boundary-is-not-genuinely-distinct-or-creates-a-container
  - feature-dependency-is-missing-duplicated-cross-set-or-cyclic
  - macro-task-registry-is-missing-incomplete-or-duplicated
  - macro-task-dependency-is-missing-duplicated-cross-parent-or-cyclic
  - plan-hides-a-known-critic-conflict
side_effects:
  - none
terminal_states: []
---

# Plan Validation

Validate only the handoff contract between Feature planning and Implement.
Require a stable Plan Set identity/revision, genuinely distinct Feature
members, an observable outcome, explicit scope and non-goals, repository
identity, source mapping, context evidence, usable landing state, ownership,
delivery reason, stable Feature acceptance criteria, validation intent,
assumptions and risks, reconciled critic findings, complete clarification
evidence, a clean independent plan review, and a closed local Macro Task
registry for every Feature.

Require `plan_review_result: clean` for the exact draft being validated. Verify
reviewer provenance, every finding and planner disposition, closure of any
accepted revision, and the bounded handling of any review-generated
clarification. Reject stale review evidence, a hidden finding, an unresolved
disposition, delegated attribution without observed assignment evidence, or a
second follow-up question batch.

Validate the clarification gate before the plan content. `simple` requires
evidence for every narrow-request condition and `clarification_route:
skip-simple`. `substantial` requires `clarification_route: ask` plus a fully
answered batch unless either `skip-complete-brief` has traceable decision-brief
coverage and an independent critic no-question finding, or
`skip-user-directed` has the user's explicit direction and only safe,
non-blocking assumptions. Reject a route based only on confidence, familiarity,
repository evidence, or a plausible default. If material uncertainty remains,
the plan is not ready.

For the Feature Plan Set registry, require one stable lower-kebab `feature_id`
per Feature, one parent Feature identity per Feature, one repository identity,
one or more local Macro Tasks, and no artificial container. Require every
Feature-level `blocked_by` to name an existing Feature in the same set, with
no self-edge, duplicate, or cycle. Require evidence that each edge is a hard
outcome dependency rather than preferred order, and verify that repository
identity makes its Implement projection unambiguous: same-repository means
mandatory stack intent and cross-repository means scheduling-only.

For each local Macro Task registry, require stable unique lower-kebab IDs,
explicit matching `parent_feature_id`, one or more F-AC-NN references per
entry, coverage of every local F-AC-NN, no scope outside the parent Feature,
and no technical execution details. Require every Macro Task `blocked_by` to
name an existing Macro Task with the same `parent_feature_id`, with no
missing, duplicate, cross-parent, self, or cyclic reference. Mark both
relation levels as planning-owned rather than technical execution edges.
Macro-local relations are not Implement gates and may be internalized while
preserving every Macro Task outcome. Require every valid Feature and Macro
edge to have an unambiguous future hosted issue mapping: Feature edges map
parent issue to parent issue, including exact cross-repository identities, and
Macro edges map child issue to child issue under one parent Feature. This is
provider-projectability validation, not provider mutation; preview remains
local-only.

Confirm that the plan explains what must be true without pretending to decide
how code will be written. Reject missing or duplicate F-AC-NN identities,
decreasing feature acceptance high-water, hidden material questions,
unresolved repository ownership, unsupported assumptions, or a plan that
contains execution-graph or worker-readiness claims.

Do not validate technical implementation units, technical dependency edges,
current Git HEADs, worktree state, worker capacity, or PR readiness. Those are
Implement responsibilities.
