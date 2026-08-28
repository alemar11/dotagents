---
node_id: blocked
kind: terminal
purpose: report-the-real-planning-or-publication-blocker
entry_conditions:
  - no-responsible-workflow-edge-remains
inputs:
  - current_plan_evidence
  - unresolved_decisions
  - publication_evidence
  - retained_hosted_identities
outputs:
  - blocker_report
  - smallest_recovery_input
transitions: []
stop_if:
  - another-safe-graph-edge-remains
side_effects:
  - none
terminal_states:
  - blocked
---

# Blocked

Report the exact invalid or inaccessible source, unresolved material decision,
inconsistent Plan Set, missing publication authority or dependency, or
unreconciled required write. Preserve any verified hosted identities and state
the smallest input needed to continue safely.

Do not block because the planner cannot self-observe its task identity, model,
reasoning effort, title, application project metadata, or an execution-target
bootstrap. Those are not Feature correctness properties. Do not convert an
ordinary clarification wait or an optional metadata/native-dependency warning
into a terminal blocker.
