---
node_id: clarification
kind: decision
purpose: resolve-material-unknowns-without-expanding-scope
entry_conditions:
  - intake-reports-material-unknowns
inputs:
  - normalized-intent
  - feature-boundary-analysis
  - planning-blockers
outputs:
  - resolved-intent
  - resolved-feature-boundary
  - accepted-assumptions
transitions:
  - to: feature
    when: every-material-blocker-is-resolved
  - to: blocked
    when: a-required-decision-remains-unresolved
stop_if:
  - clarification-would-create-a-second-feature
  - caller-requires-overlapping-feature-identities
  - evidence-is-contradictory
side_effects:
  - none
terminal_states: []
---

# Clarification

Resolve only the smallest material unknown that prevents a coherent Feature
definition. Keep accepted assumptions explicit and separate from confirmed
evidence.

When candidate Feature boundaries lack independent residual outcomes, resolve
whether to consolidate them into one Feature with multiple vertical Tasks or
to provide the missing observable outcome and separate-delivery reason. Never
preserve a requested Feature count by inventing acceptance criteria, path
boundaries, or release semantics.

Do not broaden the feature, invent repository facts, or silently convert an
unresolved question into a requirement. Continue to Feature only when the
remaining intent is internally consistent.
