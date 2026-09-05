---
node_id: plan
kind: action
purpose: converge-feature-boundaries-and-draft-the-plan-set
entry_conditions:
  - analysis-evidence-and-required-decisions-are-available
inputs:
  - plan_inputs
  - source_and_boundary_evidence
  - repository_context_evidence
  - answered_questions
  - accepted_assumptions
  - review_findings
outputs:
  - feature_plan_set_draft
  - feature_registry
  - feature_acceptance_criteria
  - macro_task_registries
  - macro_verification_paths
  - dependency_graphs
  - validation_seams
  - implementation_handoff
transitions:
  - to: review
    when: complete-plan-set-draft-is-available
  - to: blocked
    when: a-coherent-plan-contract-cannot-be-produced
stop_if:
  - artificial-container-or-integration-feature-is-required
  - technical-execution-units-or-worker-topology-would-enter-the-plan
side_effects:
  - none
terminal_states: []
---

# Plan

Use [plan.md](../templates/plan.md) to converge sources into the smallest set of
genuinely independent Feature outcomes and draft the complete textual Plan Set.
Do not preserve caller-proposed counts or splits when the outcome evidence
supports a different boundary.

For each Feature, define stable identity, repository, problem, observable
outcome, scope, non-goals, context, constraints, assumptions, risks, validation
intent, and unique observable, falsifiable `F-AC-NN` criteria. For each
criterion, identify the observation that would prove it false and ensure that
observation is false before new-behavior work. Record preservation of an
existing invariant separately from the new observable delta. Preserve monotonic
high-water marks and decision provenance during maintenance.

Create one closed Macro Task registry per Feature. Prefer coherent vertical
slices when the outcome supports them; otherwise use fewer macro outcomes and
explain the boundary. Every Macro must record an observable verification path,
or an explicit rationale that verification is integrated with another Macro
outcome. Every F-AC must be covered, no Macro may add scope, and each Macro
dependency must remain inside its parent Feature.

Build an acyclic hard-outcome Feature graph. Same-repository edges are stack
intent for Delivery Features; cross-repository edges are
scheduling-only. Keep preferred order as prose.

For existing-source work, revise the same identities and hosted projections,
increment the Plan Set revision, and change only the semantics justified by the
request and evidence. Preserve unaffected fields and executor-owned progress.

Record validation intent as observable evidence plus the highest practical
validation seam. Prefer an existing seam; propose a new seam only when the
evidence shows no suitable existing boundary. Do not prescribe commands, test
files, frameworks, or implementation steps. A material seam choice must already
be resolved or safely assumed before Plan.

When Review returns findings, apply coherent corrections to the whole plan
rather than patching wording mechanically. Return a complete draft for another
review only when the revision materially addresses the findings.
