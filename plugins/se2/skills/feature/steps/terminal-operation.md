---
node_id: terminal-operation
kind: decision
purpose: resolve-the-final-feature-bundle-operation
entry_conditions:
  - feature-and-task-bundle-is-valid
inputs:
  - calculated-feature-bundle
  - run-mode-request
  - github-mutation-authority
outputs:
  - frozen-feature-bundle
  - run_mode
  - operation-authority
transitions:
  - to: preview
    when: preview-mode-is-explicitly-requested
  - to: publish
    when: publish-mode-is-explicit-or-default-and-exact-authority-is-resolved
  - to: blocked
    when: publish-selected-and-required-publication-authority-is-unresolved
stop_if:
  - bundle-is-incomplete
side_effects:
  - none
terminal_states: []
---

# Terminal Operation

Freeze the complete Feature-and-Task bundle before choosing the final operation.
Resolve `run_mode` exactly once: an omitted mode means `publish`, while
`preview` is valid only when explicitly requested. Preview is local and
non-durable; publish is the hosted operation and still requires exact mutation
authority. Do not inspect hosted state or load the G dependency gate from this
node; those belong to the selected publish path or an earlier hosted
rehydration boundary.
