---
node_id: plan-validation
kind: validation
purpose: validate-feature-plan-set-and-local-macro-readiness-for-implement
entry_conditions:
  - textual-feature-plan-set-draft-is-available
inputs:
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
  - material-question-remains-unanswered
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
assumptions and risks, reconciled critic findings, a complete question batch,
and a closed local Macro Task registry for every Feature.

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
