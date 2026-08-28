---
node_id: complete
kind: terminal
purpose: report-the-frozen-or-verified-feature-plan-set
entry_conditions:
  - preview-is-frozen-or-all-required-publication-results-are-reconciled
inputs:
  - final_plan_set
  - review_result
  - relationship_and_dependency_results
  - removed_dependency_results
  - publication_readback
  - publication_warnings
  - downstream_handoff_status
outputs:
  - feature_plan_report
transitions: []
stop_if:
  - required-semantic-projection-is-unverified
  - canonical-dependency-attempt-or-result-is-missing
  - requested-downstream-handoff-result-is-missing
side_effects:
  - none
terminal_states:
  - complete
---

# Complete

Use [plan-report.md](../templates/plan-report.md) to report the Plan Set identity
and revision, source and repository mapping, every Feature and parent issue,
F-ACs, Macro registries and child issues, dependency semantics and native
projection warnings, material questions and assumptions, review outcome,
preview or publication evidence, and the implementation-neutral handoff.

Distinguish verified semantic publication from optional metadata or native
projection warnings. Do not claim hosted publication for preview identities and
do not claim implementation readiness from code, branch, worker, or PR state.

The planner task remains available for a legitimate follow-up or revision; no
workflow checkpoint, goal, title status, or task-profile proof is required in
the report.
