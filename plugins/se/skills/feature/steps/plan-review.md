---
node_id: plan-review
kind: validation
purpose: critically-review-and-reconcile-the-complete-plan-draft
entry_conditions:
  - textual-feature-plan-set-draft-is-complete
inputs:
  - planning-depth
  - clarification-route
  - clarification-route-evidence
  - feature-plan
  - feature-plan-set-registry
  - feature-acceptance-criteria
  - macro-task-registry
  - implementation-handoff
  - normalized-intent
  - normalized-source-issue-set
  - repository-context-evidence
  - answered-question-batch
  - accepted-assumptions
  - critic-analysis
  - plan-review-round
outputs:
  - planning-depth
  - clarification-route
  - clarification-route-evidence
  - plan-review-result
  - plan-review-findings
  - plan-review-evidence
  - plan-review-dispositions
  - plan-review-provenance
  - review-question-candidates
  - plan-review-round
transitions:
  - to: plan-validation
    when: critic-plan-review-is-clean
  - to: plan
    when: correctable-findings-require-one-bounded-draft-revision
  - to: clarification
    when: initial-review-exposes-a-material-user-decision-and-user-did-not-forbid-questions
  - to: blocked
    when: review-cannot-be-reconciled-or-would-require-a-second-follow-up-batch
stop_if:
  - complete-plan-or-source-evidence-is-missing
  - reviewer-cannot-separate-evidence-from-speculation
  - the-same-material-finding-persists-after-bounded-revision
  - post-clarification-review-discovers-another-material-user-decision
side_effects:
  - none
terminal_states: []
---

# Plan Review

Review every complete Feature Plan Set draft before Plan Validation. For a
substantial request, use the same independent critic assignment that performed
the first-pass problem critique when delegation is available. Give it the
finished draft, original intent and source set, repository evidence, resolved
questions, and accepted assumptions. It remains read-only and cannot edit the
plan, ask the user directly, or publish. When delegation is unavailable, the
planner performs the same adversarial review lens serially and records that the
review was not independently delegated.

Set `plan_review_provenance` to `delegated-critic` only after the critic
assignment was successfully dispatched and observed. Any unavailable, failed,
ambiguous, or unobserved delegation attempt selects `serial-fallback` before
the planner performs the critic lens. Never attribute a serial finding to a
delegated reviewer.

Review the plan as a product and planning contract, not as an implementation
design. Check:

- fidelity to the original problem, user answers, and repository evidence;
- outcome, scope, non-goals, ownership, and usable landing state;
- acceptance-criterion observability, completeness, and traceability;
- unsupported assumptions, contradictions, hidden product choices, and risks;
- genuine Feature boundaries and hard-outcome dependency semantics;
- complete Macro Task coverage without technical-layer decomposition;
- implementation-neutral handoff quality.

Return evidence-backed findings and separate them from speculation. The
planner owns every disposition and any revision; the reviewer never becomes
the plan reducer.

Set `plan_review_result` to:

- `clean` when no material finding remains;
- `revision-required` when the planner can correct evidence, traceability,
  wording, boundary, or coverage without a new user decision;
- `clarification-required` when correctness depends on a material product
  decision the user has not made;
- `blocked` when the reviewer cannot establish a trustworthy result or a
  bounded reconciliation fails.

For `revision-required`, return to Plan for one bounded correction and review
the revised draft again. If the same material finding persists, stop rather
than loop. For `clarification-required`, present one smallest-complete
review-generated follow-up batch through Clarification, then re-run
Convergence, Plan, and Plan Review with `plan_review_round:
post-clarification`. A second review-generated question batch is not allowed;
if another material decision appears, stop with the exact decision. If the
user previously selected `skip-user-directed`, do not ask a follow-up batch:
block instead of guessing.

When the review exposes a material decision after `skip-simple`, correct
`planning_depth` to `substantial` and `clarification_route` to `ask`. After
`skip-complete-brief`, invalidate that exception and select `ask`. Preserve the
review finding as the reason for the corrected route.

Plan Validation may start only from `plan_review_result: clean` with reviewer
provenance, findings, dispositions, and any bounded revision evidence retained.
