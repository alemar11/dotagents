---
node_id: preflight
kind: validation
purpose: verify-g-availability-before-feature-hosted-access
entry_conditions:
  - publication-operation-is-normalized
inputs:
  - normalized-feature-publication
  - target-repositories
outputs:
  - g-dependency-evidence
  - hosted-access-boundary
transitions:
  - to: hosted-checks
    when: required-g-workflows-are-available
  - to: blocked
    when: g-dependency-is-unavailable-or-unresolvable
stop_if:
  - provider-access-would-bypass-g
side_effects:
  - read
terminal_states: []
---

# Publication Preflight

Load and pass the shared G dependency preflight before the first hosted read or
write. Verify the exact G plugin identity and every G-owned workflow required
for Feature/Task issue publication. A passing gate does not grant mutation
authority and must not install, enable, refresh, or substitute a dependency.
