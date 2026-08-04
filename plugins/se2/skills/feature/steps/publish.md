---
node_id: publish
kind: action
purpose: normalize-the-authorized-feature-publication-operation
entry_conditions:
  - publish-mode-and-exact-authority-are-resolved
inputs:
  - frozen-feature-bundle
  - github-mutation-authority
  - publication-policy
outputs:
  - normalized-feature-publication
  - publication-order
transitions:
  - to: preflight
    when: publication-operation-is-normalized
stop_if:
  - target-repository-or-operation-is-ambiguous
side_effects:
  - transient
terminal_states: []
---

# Publish

Use the frozen bundle as the only publication input. Normalize one exact
Feature/Task issue operation at a time and preserve the explicit mutation
authority. Do not read or mutate hosted state from this node; `preflight` owns
the dependency gate and the first hosted access.
