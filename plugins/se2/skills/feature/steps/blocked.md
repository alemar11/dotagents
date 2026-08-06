---
node_id: blocked
kind: terminal
purpose: report-the-smallest-planning-or-publication-blocker
entry_conditions:
  - a-required-feature-plan-contract-cannot-be-satisfied
transitions: []
stop_if: []
side_effects:
  - none
terminal_states:
  - blocked
---

# Blocked

Report the exact blocker, affected phase, retained plan and analysis
artifacts, worker provenance when relevant, unresolved question IDs, and the
smallest recovery input.

Use blocked for invalid scope or identity, missing required context, declined
material decisions, incomplete plan content, unverified publication, or
unrecoverable runtime and authority failures. Do not use it for ordinary
awaiting-user-input while a consolidated question batch is actively waiting
for an answer; that is a resumable plan wait state.
