---
node_id: publish
kind: action
purpose: normalize-the-in-scope-feature-publication-operation
entry_conditions:
  - default-or-explicit-publish-and-exact-scope-is-resolved
inputs:
  - frozen-feature-bundle
  - github-mutation-scope
  - publication-policy
outputs:
  - normalized-feature-publication
  - publication-order
  - source-idea-close-operation
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

Use the frozen bundle as the only publication input. This is the default
terminal operation unless the invocation explicitly requests preview. Normalize
one exact Feature/Task issue operation at a time and preserve the implicit
mutation scope derived from the explicit request. When the new-source route
contains one exact hosted `idea-source`, normalize closing that source Idea as
the final publication operation after the Feature and every Task are published
and verified. Omit the close operation for preview, existing-source,
maintenance, local/non-hosted source evidence, or an ambiguous Idea identity.
Do not read or mutate hosted state from this node; `preflight` owns the
dependency gate and the first hosted access.
