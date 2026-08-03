---
node_id: blocked
kind: terminal
purpose: report-why-the-graph-cannot-continue
entry_conditions:
  - required-contract-cannot-be-satisfied
inputs:
  - blockers
  - partial-artifacts
outputs:
  - terminal-report
transitions: []
stop_if: []
side_effects:
  - none
terminal_states:
  - blocked
---

# Blocked

Return the exact blocker, the node where it was observed, the evidence
available, the partial artifacts retained, and the smallest recovery input
required to resume the graph.
